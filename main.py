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

        # DHA_Wellsの先頭2件をログに出力
        docs = list(db["DHA_Wells"].find({}, {"_id": 0}).limit(2))
        print("📘 DHA_Wells サンプル:", docs)

    except Exception as e:
        print("❌ Atlas接続エラー:")
        traceback.print_exc()




