import asyncio
from contextlib import asynccontextmanager
import json
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from . import model_manager
from .summarise import summarise_article
from . import priority_queue
import turso
import os
import dotenv
dotenv.load_dotenv()


# Make sure never less than 1
IDLE_CHECK_INTERVAL_SECONDS = 30

manager = model_manager.ModelManager()
queue = priority_queue.PriorityQueue()
summarised = set()

# Connect to Turso DB
con = turso.connect(os.getenv("STORAGE_PATH"))


async def _summary_worker():
    while True:
        if len(queue) > 0:
            contentPath = queue.dequeue()
            model, tokenizer = await asyncio.to_thread(manager.get_model)
            try:
                print(f"Summarising {contentPath}")
                JSONOut = await asyncio.to_thread(summarise_article, model=model, tokenizer=tokenizer, contentPath=contentPath)
                print(f"JSONOut: {JSONOut}")
                summarised.add(contentPath)
            except Exception as e:
                print(f"Article Summary failed: {e}")
                print(f"Requeing {contentPath}")
                queue.enqueue(contentPath)
        else:
            await asyncio.sleep(IDLE_CHECK_INTERVAL_SECONDS//2)


async def _idle_checker():
    while True:
        await asyncio.sleep(IDLE_CHECK_INTERVAL_SECONDS)
        manager.unload_if_idle()


@asynccontextmanager
async def lifespan(app: FastAPI):
    idle_checker_task = asyncio.create_task(_idle_checker())
    summary_worker_task = asyncio.create_task(_summary_worker())
    yield
    idle_checker_task.cancel()
    summary_worker_task.cancel()


app = FastAPI(lifespan=lifespan)


class EnqueueRequest(BaseModel):
    contentPaths: List[str]

class BumpupRequest(BaseModel):
    contentPath: str


@app.get("/status")
def status():
    return {"modelLoaded": manager.is_loaded()}


@app.get("/articles/{contentPath: path}")
def processed(contentPath: str):
    retObj = {"contentPath": contentPath}
    retObj["summarised"] = contentPath in summarised

    return retObj


@app.post("/add_to_queue")
def add_to_queue(req: EnqueueRequest):

    try:
        with open(req.filePath, 'r', encoding='utf-8') as f:
            dataJSON = json.load(f)

        if len(req.contentPaths) == 0:
            to_queue = [(req.filePath, x) for x in dataJSON["articles"].keys()]
            queue.enqueue(to_queue)

        else:
            assert all(x in dataJSON["articles"] for x in req.contentPaths), "Unknown ContentPaths in Request"
            to_queue = [(req.filePath, x) for x in req.contentPaths]
            queue.enqueue(to_queue)

        return {
            "Queued" : to_queue
        }

    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"File not found: {req.filePath}")
    except IOError:
        raise HTTPException(status_code=404, detail=f"File Access Error")



@app.post("/bumpup/{contentPath: path}")
def bumpup(contentPath: str):
    try:
        queue.bumpup(qItem=contentPath)
    except priority_queue.MissingItemError:
        raise HTTPException(status_code=404, detail="Requested Item not in Summary Queue")


