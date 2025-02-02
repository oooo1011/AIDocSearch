import motor.motor_asyncio
import os
from datetime import datetime
from bson import ObjectId

client = motor.motor_asyncio.AsyncIOMotorClient(os.getenv("MONGODB_URL"))
db = client.aidocsearch

async def add_user(user_data: dict):
    user_data["created_at"] = datetime.utcnow()
    user = await db.users.insert_one(user_data)
    return str(user.inserted_id)

async def get_user(email: str):
    return await db.users.find_one({"email": email})

async def save_search_result(search_data: dict):
    search_data["created_at"] = datetime.utcnow()
    result = await db.search_results.insert_one(search_data)
    return str(result.inserted_id)

async def save_document_analysis(analysis_data: dict):
    analysis_data["created_at"] = datetime.utcnow()
    result = await db.document_analyses.insert_one(analysis_data)
    return str(result.inserted_id)

async def get_user_history(user_id: str, skip: int = 0, limit: int = 10):
    searches = await db.search_results.find(
        {"user_id": user_id}
    ).sort("created_at", -1).skip(skip).limit(limit).to_list(length=limit)
    
    analyses = await db.document_analyses.find(
        {"user_id": user_id}
    ).sort("created_at", -1).skip(skip).limit(limit).to_list(length=limit)
    
    return {"searches": searches, "analyses": analyses}
