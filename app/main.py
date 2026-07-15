from typing import Union
from fastapi import FastAPI
app = FastAPI()

from fastapi.responses import FileResponse

@app.get("/")
def index():
    return FileResponse('app/index.html')

@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

@app.get("/health")
def health_check():
    return {"status": "ok"}

from pydantic import BaseModel
class Model(BaseModel):
    name: str
    phone: int

@app.post("/send")
def 작명(data : Model):
    print(data)
    return {"message": "전송완료"}