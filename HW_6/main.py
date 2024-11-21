import datetime
from typing import List, AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.future import select
from sqlalchemy.orm import sessionmaker
from passlib.context import CryptContext

# Параметры подключения к SQLite
DATABASE_URL = "sqlite:///./test.db"  # База данных сохранится как файл test.db в текущей папке
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
Base = declarative_base()  # Базовый класс для всех моделей
metadata = MetaData()

# Создаём сессию
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Настройка bcrypt для хэширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

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

# Lifespan для инициализации приложения
@asynccontextmanager
async def lifespan() -> AsyncGenerator[None, None]:
    print("Приложение запускается: создаём таблицы")
    Base.metadata.create_all(bind=engine)  # Создание таблиц
    yield
    print("Приложение завершает работу")

# Создаём приложение
application = FastAPI(lifespan=lifespan)

# Маршруты
@application.get("/")
def root():
    return {"message": "SQLite FastAPI Example"}

# CRUD для пользователей
@application.post("/users/", response_model=UserRead)
def create_user(user: UserCreate):
    with SessionLocal() as db:
        # Проверка, существует ли пользователь с таким email
        existing_user = db.execute(select(User).where(User.email == user.email)).scalar_one_or_none()
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        # Создание нового пользователя
        hashed_password = hash_password(user.password)
        db_user = User(name=user.name, surname=user.surname, email=user.email, password=hashed_password)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

@application.get("/users/", response_model=List[UserRead])
def read_users():
    with SessionLocal() as db:
        users = db.execute(select(User)).scalars().all()
        return users

# CRUD для продуктов
@application.post("/products/", response_model=ProductRead)
def create_product(product: ProductCreate):
    with SessionLocal() as db:
        db_product = Product(**product.model_dump())
        db.add(db_product)
        db.commit()
        db.refresh(db_product)
        return db_product

@application.get("/products/", response_model=List[ProductRead])
def read_products():
    with SessionLocal() as db:
        products = db.execute(select(Product)).scalars().all()
        return products

# CRUD для заказов
@application.post("/orders/", response_model=OrderRead)
def create_order(order: OrderCreate):
    with SessionLocal() as db:
        db_order = Order(**order.model_dump())
        db.add(db_order)
        db.commit()
        db.refresh(db_order)
        return db_order

@application.get("/orders/", response_model=List[OrderRead])
def read_orders():
    with SessionLocal() as db:
        orders = db.execute(select(Order)).scalars().all()
        return orders

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:application", host="127.0.0.1", port=8000, reload=True)
