from fastapi import FastAPI, Request

from typing import Union
from pydantic import BaseModel

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from fastapi import Depends
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Float

from http.client import HTTPException

app = FastAPI()

@app.get("/")
def hello_world():
    return {"massage": "Hello World"}

@app.get("/sum/{x}")
def sumX(x):
    sum = x
    return {"massage": sum}

@app.get("/query/{x}")
def qeury(x: int, q : Union[str, None] = None):
    return {"massage": x,
            "Query": q}

@app.post("/items")
async def create_item(request: Request):
    body = await request.json()
    return {"massage": body}

# Pydantic Model
# 1. Base
class Item(BaseModel):
    name: str
    price: float

# 2. Request
class ItemCreate(Item):
    pass

# 3. Response
class ItemResponse(Item):
    id: int
    class Config:
        from_attributes = True

@app.post("/items2")
def create_item2(item: Item):
    return {"massage": item}

@app.put("/items/{item_id}")
def update_item(item_id: int, item: Item):
    return {"item_id": item_id, "item": item}

@app.delete("/items/{item_id}")
def delete_item(item_id: int):
    return {"item_id": item_id, "message": "Item deleted"}

# step 1: Create Database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
    )
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# step 2: Create a database model (ORM Class)
class ItemModel(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    price = Column(Float)

# step 3: Create the database tables
Base.metadata.create_all(bind=engine)

#step 4: Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/postDB", response_model = ItemResponse)
def create_postDB(item: ItemCreate, db: Session = Depends(get_db)):
    db_item = ItemModel(**item.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@app.get("/getDB/{item_id}", response_model = ItemResponse)
def read_item(item_id: int, db: Session = Depends(get_db)):
    db_item = db.query(ItemModel).filter(ItemModel.id == item_id).first()
    return db_item

@app.get("/getDB", response_model=list[ItemResponse])
def read_items(db: Session = Depends(get_db)):
    db_items = db.query(ItemModel).all()
    return db_items

@app.put("/updateDB/{item_id}", response_model = ItemResponse)
def update_item(item_id: int, item: ItemCreate, db: Session = Depends(get_db)):
    db_item = db.query(ItemModel).filter(ItemModel.id == item_id).first()
    if db_item is None:
        return HTTPException(status_code=404, detail="Item not found")
    for key, value in item.model_dump().items():
        setattr(db_item, key, value)
    db.commit()
    db.refresh(db_item)
    return db_item

@app.delete("/deleteDB/{item_id}")
async def delete_item(item_id: int, db: Session = Depends(get_db)):
    db_item = db.query(ItemModel).filter(ItemModel.id == item_id).first()
    if db_item is None:
        return HTTPException(status_code=404, detail="Item not found")
    db.delete(db_item)
    db.commit()
    return {"message": "Item deleted"}