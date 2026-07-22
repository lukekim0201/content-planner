from fastapi import FastAPI
from app.controller import items, users

app = FastAPI()

app.include_router(items.router)
app.include_router(users.router)

from fastapi.responses import FileResponse

@app.get("/")
def index():
    return FileResponse('app/index.html')

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