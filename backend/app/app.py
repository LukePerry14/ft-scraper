from typing import List
import requests
from fastapi import FastAPI
from pydantic import BaseModel
import dotenv
import os
import turso
from fastapi.responses import HTMLResponse


dotenv.load_dotenv()

con = turso.connect(os.getenv("STORAGE_PATH"))
cur = con.cursor()

app = FastAPI()


class Article(BaseModel):
    title: str
    url: str
    topics: List[str]

@app.get("/", response_class=HTMLResponse)
async def home():
    # Get homepage and articles from scraper API
    resp = await requests.post(f"http://localhost:{os.getenv("SCRAPER_PORT")}/articles")
    resp.raise_for_status()

    data = resp.json()
    
    contentPaths = data["articles"].keys()

    # Query db for contentPaths
    placeholders = ",".join("?" * len(contentPaths))
    res = cur.execute(f"SELECT * from articles WHERE articleID in ({placeholders})", contentPaths)
    existing = res.fetchall()

    # Create DB records for unstored articles 
    if len(existing) < len(contentPaths):
        new_articles = [rec for rec in existing if existing[0] not in contentPaths]

        for article in new_articles:
            cur.execute("INSERT INTO articles (articleID) VALUES (?)", article)

        con.commit()


    # For every record with a 
    placeholders = ",".join("?" * len(contentPaths))
    res = cur.execute(f"SELECT articleID from articles WHERE articleID in ({placeholders}) AND summary IS NONE", contentPaths)
    to_queue = res.fetchall()

    # resp = requests.post(
    #     url=f"http://localhost:{os.getenv("LLM_PORT")}/add_to_queue",
    #     data=
    #     )
    resp.raise_for_status()

    return data["pageHTML"]
    

@app.post('/{contentPath}', response_class=HTMLResponse)
async def get_article(article):
    pass

@app.get('/articles')
def test():
    pass