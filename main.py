from fastapi import FastAPI, Request

from typing import Union
from pydantic import BaseModel

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

class Item(BaseModel):
    name: str
    price: float

@app.post("/items2")
def create_item2(item: Item):
    return {"massage": item}

@app.put("/items/{item_id}")
def update_item(item_id: int, item: Item):
    return {"item_id": item_id, "item": item}

@app.delete("/items/{item_id}")
def delete_item(item_id: int):
    return {"item_id": item_id, "message": "Item deleted"}