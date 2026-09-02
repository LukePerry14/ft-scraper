import asyncio
from contextlib import asynccontextmanager
import json
from typing import List, Optional
import os
from pathlib import Path
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from . import model_manager
from .summarise import summarise_article
from . import priority_queue

# Make sure never less than 1
IDLE_CHECK_INTERVAL_SECONDS = 30

manager = model_manager.ModelManager()

queue = priority_queue.PriorityQueue()

summarised = set()

async def _summary_worker():
    while True:
        if len(queue) > 0:
            articleQObj = queue.dequeue()
            model, tokenizer = await asyncio.to_thread(manager.get_model)
            try:
                print(f"Summarising {articleQObj}")
                JSONOut = await asyncio.to_thread(summarise_article, model=model, tokenizer=tokenizer, filePath=articleQObj[0], contentPath=articleQObj[1])
                print(f"JSONOut: {JSONOut}")
                summarised.add(articleQObj[1])
            except Exception as e:
                print(f"Article Summary failed: {e}")
                print(f"Requeing {articleQObj}")
                queue.enqueue(articleQObj)
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
    filePath: Optional[str]
    contentPaths: List[str]

class BumpupRequest(BaseModel):
    contentPath: str

class SummarisedQueryRequest(BaseModel):
    filePath: Optional[str]
    contentPaths: List[str]


@app.get("/status")
def status():
    return {"modelLoaded": manager.is_loaded()}


@app.get("/articles/processed")
def processed(req: SummarisedQueryRequest):
    retObj = {}

    for path in req.contentPaths:
        retObj[path] = path in summarised

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



@app.post("/bumpup")
def bumpup(req: BumpupRequest):
    try:
        queue.bumpup(qItem=req.contentPath)
    except priority_queue.MissingItemError:
        raise HTTPException(status_code=404, detail="Requested Item not in Summary Queue")


# standard synchronous endpoint rather than async endpoint to ensure blocking.
# @app.post("/summarise")
# def summarise(req: SummariseRequest):
#     model, tokenizer = manager.get_model()

#     try:
#         return summarise_article(model, tokenizer, req.filePath, req.contentPath)
#     except FileNotFoundError:
#         raise HTTPException(status_code=404, detail=f"File not found: {req.filePath}")
#     except KeyError:
#         raise HTTPException(status_code=404, detail=f"Article not found for contentPath: {req.contentPath}")
#     except IOError:
#         raise HTTPException(status_code=404, detail=f"File Access Error")
