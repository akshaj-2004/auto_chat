from fastapi import FastAPI
from typing import Union

app = FastAPI()

@app.get('/')
def home():
    return {"message": "hi there"}

@app.get('/item/{itemid}')
def read_inp(itemid: int, q: Union[str, None] = None):
    return {"itemid": itemid, "q": q}