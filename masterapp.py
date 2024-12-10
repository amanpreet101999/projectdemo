from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.sql import func
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext

# Initialize FastAPI app
app = FastAPI()

# Database Setup
DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Models
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    created_at = Column(DateTime, default=func.now())

class Category(Base):
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    created_at = Column(DateTime, default=func.now())

class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    price = Column(Float)
    category_id = Column(Integer, ForeignKey('categories.id'))
    image_url = Column(String)
    created_at = Column(DateTime, default=func.now())

class Order(Base):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    total_price = Column(Float)
    status = Column(String)
    created_at = Column(DateTime, default=func.now())

class Favorite(Base):
    __tablename__ = 'favorites'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    product_id = Column(Integer, ForeignKey('products.id'))
    created_at = Column(DateTime, default=func.now())

# Pydantic Models
class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class CategoryCreate(BaseModel):
    name: str

class ProductCreate(BaseModel):
    name: str
    description: str
    price: float
    category_id: int
    image_url: str

class OrderCreate(BaseModel):
    user_id: int
    total_price: float
    status: str

class FavoriteCreate(BaseModel):
    user_id: int
    product_id: int

# Password Encryption
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Dependency: get_db
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create all tables
Base.metadata.create_all(bind=engine)

# Authentication
@app.post("/auth/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    hashed_password = pwd_context.hash(user.password)
    db_user = User(username=user.username, email=user.email, password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.post("/auth/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not pwd_context.verify(form_data.password, user.password):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    # Generate a token here (not implemented)
    return {"access_token": "fake_token", "token_type": "bearer"}

# Category endpoints
@app.get("/categories")
def get_categories(db: Session = Depends(get_db)):
    return db.query(Category).all()

@app.get("/categories/{id}")
def get_category(id: int, db: Session = Depends(get_db)):
    return db.query(Category).filter(Category.id == id).first()

@app.post("/categories")
def create_category(category: CategoryCreate, db: Session = Depends(get_db)):
    db_category = Category(name=category.name)
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

@app.put("/categories/{id}")
def update_category(id: int, category: CategoryCreate, db: Session = Depends(get_db)):
    db_category = db.query(Category).filter(Category.id == id).first()
    db_category.name = category.name
    db.commit()
    db.refresh(db_category)
    return db_category

@app.delete("/categories/{id}")
def delete_category(id: int, db: Session = Depends(get_db)):
    db_category = db.query(Category).filter(Category.id == id).first()
    db.delete(db_category)
    db.commit()
    return {"message": "Category deleted"}

# Product endpoints
@app.get("/products")
def get_products(db: Session = Depends(get_db)):
    return db.query(Product).all()

@app.get("/products/{id}")
def get_product(id: int, db: Session = Depends(get_db)):
    return db.query(Product).filter(Product.id == id).first()

@app.get("/products/category/{category_id}")
def get_products_by_category(category_id: int, db: Session = Depends(get_db)):
    return db.query(Product).filter(Product.category_id == category_id).all()

@app.post("/products")
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    db_product = Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

@app.put("/products/{id}")
def update_product(id: int, product: ProductCreate, db: Session = Depends(get_db)):
    db_product = db.query(Product).filter(Product.id == id).first()
    for key, value in product.dict().items():
        setattr(db_product, key, value)
    db.commit()
    db.refresh(db_product)
    return db_product

@app.delete("/products/{id}")
def delete_product(id: int, db: Session = Depends(get_db)):
    db_product = db.query(Product).filter(Product.id == id).first()
    db.delete(db_product)
    db.commit()
    return {"message": "Product deleted"}

# Order endpoints
@app.get("/orders")
def get_orders(db: Session = Depends(get_db)):
    return db.query(Order).all()

@app.get("/orders/{id}")
def get_order(id: int, db: Session = Depends(get_db)):
    return db.query(Order).filter(Order.id == id).first()

@app.post("/orders")
def create_order(order: OrderCreate, db: Session = Depends(get_db)):
    db_order = Order(**order.dict())
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order

@app.put("/orders/{id}/status")
def update_order_status(id: int, status: str, db: Session = Depends(get_db)):
    db_order = db.query(Order).filter(Order.id == id).first()
    db_order.status = status
    db.commit()
    db.refresh(db_order)
    return db_order

@app.delete("/orders/{id}")
def delete_order(id: int, db: Session = Depends(get_db)):
    db_order = db.query(Order).filter(Order.id == id).first()
    db.delete(db_order)
    db.commit()
    return {"message": "Order deleted"}

# Favorite endpoints
@app.get("/favorites")
def get_favorites(db: Session = Depends(get_db)):
    return db.query(Favorite).all()

@app.post("/favorites")
def add_to_favorites(favorite: FavoriteCreate, db: Session = Depends(get_db)):
    db_favorite = Favorite(**favorite.dict())
    db.add(db_favorite)
    db.commit()
    db.refresh(db_favorite)
    return db_favorite

@app.delete("/favorites/{product_id}")
def remove_from_favorites(product_id: int, db: Session = Depends(get_db)):
    db_favorite = db.query(Favorite).filter(Favorite.product_id == product_id).first()
    db.delete(db_favorite)
    db.commit()
    return {"message": "Product removed from favorites"}
