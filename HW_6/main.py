import datetime
from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import sessionmaker
from sqlalchemy.future import select
from pydantic import BaseModel
from typing import List
from random import randint

# Параметры подключения к SQLite
DATABASE_URL = "sqlite:///./test.db"  # База данных сохранится как файл test.db в текущей папке
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
Base = declarative_base()  # Базовый класс для всех моделей
metadata = MetaData()

# Создаём сессию
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Определение моделей для таблиц
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    surname = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    price = Column(Float)

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    prod_id = Column(Integer, ForeignKey("products.id"))
    status = Column(String)
    date = Column(DateTime)

# Pydantic-схемы
class UserCreate(BaseModel):
    name: str
    surname: str
    email: str
    password: str

class ProductCreate(BaseModel):
    title: str
    description: str
    price: float

class OrderCreate(BaseModel):
    user_id: int
    prod_id: int
    status: str
    date: datetime.datetime

class UserRead(BaseModel):
    id: int
    name: str
    surname: str
    email: str

    class Config:
        orm_mode = True

class ProductRead(BaseModel):
    id: int
    title: str
    description: str
    price: float

    class Config:
        orm_mode = True

class OrderRead(BaseModel):
    id: int
    user_id: int
    prod_id: int
    status: str
    date: datetime.datetime

    class Config:
        orm_mode = True

# Создаём приложение
app = FastAPI()

# Создаём таблицы при запуске
@app.on_event("startup")
async def startup():
    Base.metadata.create_all(bind=engine)

@app.get("/")
def root():
    return {"message": "SQLite FastAPI Example"}

# CRUD для пользователей
@app.post("/users/", response_model=UserRead)
def create_user(user: UserCreate):
    db = SessionLocal()
    db_user = User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    db.close()
    return db_user

@app.get("/users/", response_model=List[UserRead])
def read_users():
    db = SessionLocal()
    users = db.execute(select(User)).scalars().all()
    db.close()
    return users

# CRUD для продуктов
@app.post("/products/", response_model=ProductRead)
def create_product(product: ProductCreate):
    db = SessionLocal()
    db_product = Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    db.close()
    return db_product

@app.get("/products/", response_model=List[ProductRead])
def read_products():
    db = SessionLocal()
    products = db.execute(select(Product)).scalars().all()
    db.close()
    return products

# CRUD для заказов
@app.post("/orders/", response_model=OrderRead)
def create_order(order: OrderCreate):
    db = SessionLocal()
    db_order = Order(**order.dict())
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    db.close()
    return db_order

@app.get("/orders/", response_model=List[OrderRead])
def read_orders():
    db = SessionLocal()
    orders = db.execute(select(Order)).scalars().all()
    db.close()
    return orders

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

