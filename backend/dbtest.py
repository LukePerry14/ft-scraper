import turso
import os
import dotenv

dotenv.load_dotenv()

db = turso.connect(os.getenv("STORAGE_PATH"))
cur = db.cursor()

# db.execute("DROP TABLE articles")

# db.execute("""
#   CREATE TABLE IF NOT EXISTS articles (
#     articleID TEXT PRIMARY KEY,
#     title TEXT,
#     content TEXT,
#     summary TEXT,
#     author TEXT,
#     publishDate DATE,
#     articleEmbedding F32_BLOB(1024)
#   )
# """)

db.execute("BEGIN")

db.execute("INSERT INTO articles (articleID) VALUES (?)", ("test",))
res = db.execute("SELECT * FROM articles")
print(res)
print(res.fetchall()[0][0])

db.rollback()