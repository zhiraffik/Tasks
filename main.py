from fastapi import FastAPI, HTTPException, UploadFile, File, Form, status
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field, HttpUrl, validator, confloat, conint  # Исправлено pydamtic → pydantic
from typing import List, Optional
from datetime import datetime, date
import os
import uuid
from pathlib import Path

app = FastAPI(title="KinoMonster", version="1.0.0")

# Настройки
UPLOAD_DIR = "posters"
ALLOWED_IMAGE_TYPES = ["image/jpeg", "image/png"]
MAX_IMAGE_SIZE = 2 * 1024 * 1024  # 2MB


os.makedirs(UPLOAD_DIR, exist_ok=True)

# Модели данных
class Genre(BaseModel):
    id: int
    name: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = Field(None, max_length=500)

class MovieCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    year: int(ge=1888, le=datetime.now().year) 
    genres: List[int]
    duration: int(gt=0)  
    rating: Optional[float(ge=0, le=10)] = None
    description: Optional[str] = Field(None, max_length=1000)
    poster_url: Optional[HttpUrl] = None

    @validator('genres')
    def validate_genres(cls, v):
        if not v:
            raise ValueError('Должен быть указан хотя бы один жанр')
        return v  

class Movie(MovieCreate):
    id: int
    date_added: datetime
    poster_filename: Optional[str] = None

# "База данных"
genres_db = [
    Genre(id=1, name="Боевик", description="Фильмы с динамичными сценами борьбы и погонями"),
    Genre(id=2, name="Драма", description="Фильмы с глубоким эмоциональным содержанием"),
    Genre(id=3, name="Комедия", description="Юмористические фильмы")
]

movies_db = [
    Movie(
        id=1,
        title="Крепкий орешек",
        year=1988,
        genres=[1],
        duration=132,
        rating=8.2,
        description="Полицейский пытается спасти людей, захваченных террористами в небоскребе.",
        date_added=datetime(2023, 1, 15),
        poster_url="https://example.com/poster1.jpg"
    ),
    Movie(
        id=2,
        title="Форрест Гамп",
        year=1994,
        genres=[2],
        duration=142,
        rating=8.8,
        description="История жизни человека с низким IQ, который стал свидетелем ключевых событий американской истории.",
        date_added=datetime(2023, 2, 20),
        poster_url="https://example.com/poster2.jpg"
    )
]


def get_movie_by_id(movie_id: int) -> Optional[Movie]:
    for movie in movies_db:
        if movie.id == movie_id:
            return movie
    return None

def get_genre_by_id(genre_id: int) -> Optional[Genre]:
    for genre in genres_db:
        if genre.id == genre_id:
            return genre
    return None

def validate_genres(genre_ids: List[int]):
    for genre_id in genre_ids:
        if not get_genre_by_id(genre_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Жанр с ID {genre_id} не найден"
            )

def save_poster(file: UploadFile) -> str:
    # Генерируем уникальное имя файла
    file_ext = file.filename.split(".")[-1]
    filename = f"{uuid.uuid4()}.{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, filename)
    
    # Сохраняем файл
    with open(file_path, "wb") as buffer:
        buffer.write(file.file.read())
    
    return filename


@app.get("/movies", response_model=List[Movie])
async def get_movies():
    """Получить список всех фильмов"""
    return movies_db

@app.get("/movies/{movie_id}", response_model=Movie)
async def get_movie(movie_id: int):
    """Получить информацию о конкретном фильме"""
    movie = get_movie_by_id(movie_id)
    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Фильм не найден"
        )
    return movie

@app.post("/movies", response_model=Movie, status_code=status.HTTP_201_CREATED)
async def create_movie(movie: MovieCreate):
    """Добавить новый фильм"""
    validate_genres(movie.genres)
    
    new_id = max(movie.id for movie in movies_db) + 1 if movies_db else 1
    new_movie = Movie(
        id=new_id,
        date_added=datetime.now(),
        poster_filename=None,
        **movie.dict()
    )
    movies_db.append(new_movie)
    return new_movie

@app.put("/movies/{movie_id}", response_model=Movie)
async def update_movie(movie_id: int, movie: MovieCreate):
    """Обновить информацию о фильме"""
    validate_genres(movie.genres)
    
    existing_movie = get_movie_by_id(movie_id)
    if not existing_movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Фильм не найден"
        )
    
    
    for field, value in movie.dict().items():
        setattr(existing_movie, field, value)
    
    return existing_movie

@app.put("/movies/{movie_id}/image", response_model=Movie)
async def update_movie_poster(
    movie_id: int,
    file: UploadFile = File(..., description="Постер фильма (JPEG или PNG, до 2MB)")
):
    """Обновить постер фильма"""
    
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Недопустимый тип файла. Разрешены только JPEG и PNG"
        )
    
   
    file.file.seek(0, 2)  
    file_size = file.file.tell()
    file.file.seek(0)  
    
    if file_size > MAX_IMAGE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Файл слишком большой. Максимальный размер: {MAX_IMAGE_SIZE//(1024*1024)}MB"
        )
    
 
    movie = get_movie_by_id(movie_id)
    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Фильм не найден"
        )
    
   
    filename = save_poster(file)
    
    
    if movie.poster_filename:
        old_path = os.path.join(UPLOAD_DIR, movie.poster_filename)
        if os.path.exists(old_path):
            os.remove(old_path)
    
    # Обновляем информацию о фильме
    movie.poster_filename = filename
    movie.poster_url = None  
    
    return movie

@app.get("/movies/{movie_id}/poster")
async def get_movie_poster(movie_id: int):
    """Получить постер фильма"""
    movie = get_movie_by_id(movie_id)
    if not movie or not movie.poster_filename:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Постер не найден"
        )
    
    file_path = os.path.join(UPLOAD_DIR, movie.poster_filename)
    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Файл постера не найден на сервере"
        )
    
    return FileResponse(file_path)

@app.delete("/movies/{movie_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_movie(movie_id: int):
    """Удалить фильм"""
    global movies_db
    
    movie = get_movie_by_id(movie_id)
    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Фильм не найден"
        )
    
    
    if movie.poster_filename:
        file_path = os.path.join(UPLOAD_DIR, movie.poster_filename)
        if os.path.exists(file_path):
            os.remove(file_path)
    
    # Удаляем фильм из базы
    movies_db = [m for m in movies_db if m.id != movie_id]

@app.get("/genres", response_model=List[Genre])
async def get_genres():
    """Получить список всех жанров"""
    return genres_db

@app.post("/genres", response_model=Genre, status_code=status.HTTP_201_CREATED)
async def create_genre(genre: Genre):
    """Добавить новый жанр"""
    new_id = max(g.id for g in genres_db) + 1 if genres_db else 1
    genre.id = new_id
    genres_db.append(genre)
    return genre