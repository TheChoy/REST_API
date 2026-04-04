from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"massage": "Hello World"}

@app.get("/{x}")
async def root(x):
    sum = x
    return {"massage": sum}