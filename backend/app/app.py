from typing import List

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Article(BaseModel):
    title: str
    url: str
    topics: List[str]

@app.post('/article')
async def get_article(article):
    pass

@app.get('/articles')
def test():
    pass