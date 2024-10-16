import os
from fastapi import FastAPI, Query
from fastapi.responses import StreamingResponse
from lightrag import LightRAG, QueryParam
import dotenv
from typing import AsyncGenerator
import uvicorn
import asyncio

dotenv.load_dotenv()
app = FastAPI()

# Initialize LightRAG
rag = LightRAG(working_dir="./documents/dickens")

@app.get("/search")
async def search(query: str = Query(...), mode: str = Query("local")):
    async def stream_generator() -> AsyncGenerator[str, None]:
        async for chunk in rag.query_stream(query, param=QueryParam(mode=mode)):
            yield chunk

    return StreamingResponse(stream_generator(), media_type="text/plain")

@app.post("/document")
async def change_working_dir(working_dir: str = Query(...)):
    global rag
    
    # Ensure the working directory path starts with ./
    if not working_dir.startswith("./"):
        working_dir = f"./{working_dir}"
    
    # Check if the folder exists, if not, create it
    if not os.path.exists(working_dir):
        os.makedirs(working_dir)
    
    rag = LightRAG(working_dir=working_dir)
    return {"message": "Working directory changed", "working_dir": working_dir}

@app.get("/document")
async def get_working_dir():
    return {"working_dir": rag.working_dir}

if __name__ == "__main__":
    uvicorn.run("test:app", host="0.0.0.0", port=8000, reload=True)

# # test only
# rag = LightRAG(working_dir="./dickens")
# async def local_search_test(query: str = Query(...)):
#     async for chunk in rag.query_stream(query, param=QueryParam(mode="hybrid")):
#         print(chunk)
        
# # local_search_test("What is the name of the main character in the book?")
# asyncio.run(local_search_test("What is the name of the main character in the book?"))