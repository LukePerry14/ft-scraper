import dotenv
import os
import turso
from pathlib import Path
dotenv.load_dotenv()

sPath = os.getenv("STORAGE_PATH")

Path(sPath).parent.mkdir(parents=True, exist_ok=True)

con = turso.connect(sPath)
cur = con.cursor()

cur.execute("""
  CREATE TABLE IF NOT EXISTS articles (
    articleID TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    content TEXT,
    summary TEXT,
    author TEXT,
    publishDate DATE,
    articleEmbedding F32_BLOB(1024)
  )
""")

cur.execute("""
  CREATE TABLE IF NOT EXISTS topics (
    topicID INTEGER PRIMARY KEY AUTOINCREMENT,
    topicName TEXT NOT NULL
  )
""")

cur.execute("""
  CREATE TABLE IF NOT EXISTS article_topics (
    articleID TEXT,
    topicID INTEGER,
    PRIMARY KEY (articleID, topicID),
    FOREIGN KEY (articleID) REFERENCES articles(articleID),
    FOREIGN KEY (topicID) REFERENCES topics(topicID)
  )
""")

con.commit()