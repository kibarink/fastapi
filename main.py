from fastapi import FastAPI
from pymongo import MongoClient
import os

app = FastAPI()

# Atlas 接続
client = MongoClient(os.getenv("MONGO_URI"), tls=True)
db = client[os.getenv("MONGO_DB")]

@app.get("/")
def root():
    return {"message": "FastAPI Render Server is running"}

@app.get("/ping")
def ping():
    try:
        db.command("ping")
        return {"status": "ok", "message": "Connected to Atlas"}
    except Exception as e:
        return {"status": "error", "detail": str(e)}

import asyncio

@app.on_event("startup")
async def startup_event():
    import traceback
    try:
        db.command("ping")
        print("✅ Atlas接続OK（Render起動時）")
    except Exception as e:
        print("❌ Atlas接続エラー:")
        traceback.print_exc()

from fastapi.responses import JSONResponse

@app.get("/find")
def find_documents(limit: int = 5):
    try:
        docs = list(db["DHA_Wells"].find({}, {"_id": 0}).limit(limit))
        return JSONResponse(content={"count": len(docs), "documents": docs})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})



