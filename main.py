from fastapi import FastAPI, Query
import random
import math
app = FastAPI()


@app.get("/about")
def about():
    return {
        "Name" : "Danil", 
        "Surname" : "Pesterev",
        "Group number" : "T-323901-NT",
        "Email" : "zhiraff2004@gmail.com"
    }
    
@app.get("/rnd")
def random_number():
    return{"random_number" : random.randint(1,10)}


@app.get("/t_square")
def calc(
    a: int = Query(gt=0,description="Сторона А"),
    b: int = Query(gt=0,description="Сторона B"),
    c: int = Query(gt=0,description="Сторона C"),
):
    if not (a+b > c and a+c > b and b+c > a ):
        return{
            "mesage" : "Треугольник с такими сторонами не существует"
        }
    if (a >= 0 or b >= 0 or c >= 0):
        return{
            "mesage" : "Треугольник с такими сторонами не существует"
        }
    P = a+b+c
    half_P = P/2
    S = math.sqrt(half_P * (half_P-a) * (half_P-b) * (half_P-c))
    
    return{
        "Периметр" : P,
        "Площадь" : S,
        "Message" : "Расчёт выполнен"
    }
    