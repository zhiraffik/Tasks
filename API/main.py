from fastapi import FastAPI, Query, Path, HTTPException
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from uuid import uuid4

app = FastAPI()

# Модель для хранения товаров
class Item(BaseModel):
    id: str
    name: str = Field(..., min_length=2, max_length=100)
    price: float = Field(..., gt=0)
    description: Optional[str] = Field(None, max_length=500)

# Модель для создания товара (без id)
class ItemCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, example="Laptop")
    price: float = Field(..., gt=0, example=999.99)
    description: Optional[str] = Field(None, max_length=500, example="A powerful laptop for work and gaming.")

    # Пример для документации
    class Config:
        schema_extra = {
            "example": {
                "name": "Laptop",
                "price": 999.99,
                "description": "A powerful laptop for work and gaming."
            }
        }

# "База данных" товаров
items_db = []

# Эндпоинт 1: Получение списка товаров с фильтрацией
@app.get("/items/", response_model=List[Item])
def get_items(
    name: Optional[str] = Query(
        None,
        min_length=2,
        description="Фильтрация по названию товара (минимум 2 символа)",
        example="phone"
    ),
    min_price: Optional[float] = Query(
        None,
        gt=0,
        description="Минимальная цена (должен быть положительным числом)",
        example=100
    ),
    max_price: Optional[float] = Query(
        None,
        gt=0,
        description="Максимальная цена (должна быть больше min_price)",
        example=1000
    ),
    limit: int = Query(
        10,
        gt=0,
        le=100,
        description="Количество возвращаемых товаров (по умолчанию 10, максимум 100)",
        example=5
    )
):
    """
    Получение списка товаров с возможностью фильтрации по названию и цене.
    
    Параметры:
    - name: фильтр по названию (минимум 2 символа)
    - min_price: минимальная цена (положительное число)
    - max_price: максимальная цена (должна быть больше min_price)
    - limit: количество товаров в ответе (по умолчанию 10, максимум 100)
    """
    filtered_items = items_db
    
    if name:
        filtered_items = [item for item in filtered_items if name.lower() in item.name.lower()]
    
    if min_price is not None:
        filtered_items = [item for item in filtered_items if item.price >= min_price]
    
    if max_price is not None:
        if min_price is not None and max_price <= min_price:
            raise HTTPException(
                status_code=400,
                detail="max_price должен быть больше min_price"
            )
        filtered_items = [item for item in filtered_items if item.price <= max_price]
    
    return filtered_items[:limit]

# Эндпоинт 2: Получение информации о товаре по ID
@app.get("/items/{item_id}", response_model=Item)
def get_item(
    item_id: str = Path(
        ...,
        description="Идентификатор товара",
        example="42"
    )
):
    """
    Получение информации о конкретном товаре по его идентификатору.
    
    Параметры:
    - item_id: идентификатор товара
    
    Возвращает 404 если товар не найден.
    """
    for item in items_db:
        if item.id == item_id:
            return item
    
    raise HTTPException(
        status_code=404,
        detail="Товар не найден"
    )

# Эндпоинт 3: Создание нового товара
@app.post("/items/", response_model=Item, status_code=201)
def create_item(item: ItemCreate):
    """
    Создание нового товара.
    
    Параметры тела запроса:
    - name: название товара (2-100 символов)
    - price: цена товара (должна быть больше 0)
    - description: описание товара (до 500 символов, опционально)
    """
    new_item = Item(
        id=str(uuid4()),
        name=item.name,
        price=item.price,
        description=item.description
    )
    items_db.append(new_item)
    return new_item


if not items_db:
    items_db.extend([
        Item(id="1", name="Smartphone", price=599.99, description="Latest smartphone model"),
        Item(id="2", name="Laptop", price=999.99, description="Powerful laptop for work"),
        Item(id="3", name="Headphones", price=149.99, description="Noise-cancelling headphones"),
        Item(id="4", name="Tablet", price=299.99, description="Portable tablet device"),
        Item(id="5", name="Smartwatch", price=199.99, description="Fitness tracking smartwatch"),
        Item(id="6", name="Camera", price=499.99, description="Professional digital camera"),
        Item(id="7", name="Speaker", price=79.99, description="Bluetooth portable speaker"),
        Item(id="8", name="Monitor", price=249.99, description="27-inch computer monitor"),
        Item(id="9", name="Keyboard", price=89.99, description="Mechanical gaming keyboard"),
        Item(id="10", name="Mouse", price=49.99, description="Wireless computer mouse")
    ])