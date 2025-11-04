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

from fastapi.responses import Response

# === カラー設定 ===
COLOR_MAP = {
    "Reservoir": "#FFD700",  # 黄色
    "Seal": "#8B4513",       # 茶色
    "Trap": "#228B22",       # 緑
    "Charge": "#A52A2A"      # 薄えんじ
}

RESULT_RING = {
    "Oil": "#FF0000",
    "Oil_Show": "#FFA07A",
    "Gas": "#0000FF",
    "Gas_Show": "#87CEFA",
    "Dry": "#808080"
}

@app.get("/icon/{well_name}")
def generate_icon(well_name: str):
    well = db["DHA_Wells"].find_one({"WELL_NAME": well_name}, {"_id": 0})
    if not well:
        return {"error": "Well not found"}

    res, trap, seal, charge = well["Reservoir"], well["Trap"], well["Seal"], well["Charge"]
    result = well.get("Result", "Dry")
    ring_color = RESULT_RING.get(result, "#CCCCCC")

    # === SVG生成 ===
    svg = f'''
    <svg xmlns="http://www.w3.org/2000/svg" width="256" height="256">
        <rect width="256" height="256" fill="white"/>
        <path d="M128,0 A128,128 0 0,1 256,128 L128,128 Z" fill="{COLOR_MAP['Reservoir'] if res>0 else '#E0E0E0'}"/>
        <path d="M256,128 A128,128 0 0,1 128,256 L128,128 Z" fill="{COLOR_MAP['Trap'] if trap>0 else '#E0E0E0'}"/>
        <path d="M128,256 A128,128 0 0,1 0,128 L128,128 Z" fill="{COLOR_MAP['Seal'] if seal>0 else '#E0E0E0'}"/>
        <path d="M0,128 A128,128 0 0,1 128,0 L128,128 Z" fill="{COLOR_MAP['Charge'] if charge>0 else '#E0E0E0'}"/>
        <circle cx="128" cy="128" r="120" fill="none" stroke="{ring_color}" stroke-width="16"/>
    </svg>
    '''
    return Response(content=svg, media_type="image/svg+xml")





