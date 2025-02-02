from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import os
import uuid
import json
from typing import Optional
from .services.ai_service import AIService
from .auth.keycloak_auth import get_current_user, User

app = FastAPI()
ai_service = AIService()

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/models")
async def get_models(current_user: User = Depends(get_current_user)):
    """获取可用的AI模型列表"""
    return await ai_service.model_manager.get_models()

async def stream_response(generator):
    """生成SSE响应"""
    try:
        async for chunk in generator:
            if chunk:
                # 确保chunk是字符串
                if not isinstance(chunk, str):
                    chunk = str(chunk)
                # 发送SSE格式的数据
                yield f"data: {json.dumps({'content': chunk})}\n\n"
        # 发送结束标记
        yield "data: [DONE]\n\n"
    except Exception as e:
        # 发送错误信息
        yield f"data: {json.dumps({'error': str(e)})}\n\n"
        yield "data: [DONE]\n\n"

@app.post("/api/search/stream")
async def search_stream(
    query: str,
    model: str,
    model_name: str,
    document_id: Optional[str] = None,
    use_rag: bool = True,
    current_user: User = Depends(get_current_user)
):
    """执行流式搜索查询"""
    try:
        generator = ai_service.process_query_stream(
            query=query,
            model_provider=model,
            model_name=model_name,
            document_id=document_id,
            use_rag=use_rag
        )
        return StreamingResponse(
            stream_response(generator),
            media_type="text/event-stream"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/process-document")
async def process_document(
    file: UploadFile = File(...),
    model: str = None,
    model_name: str = None,
    current_user: User = Depends(get_current_user)
):
    """处理上传的文档"""
    try:
        # 创建文档存储目录
        os.makedirs("documents", exist_ok=True)
        
        # 生成唯一的文档ID和文件名
        document_id = str(uuid.uuid4())
        file_extension = os.path.splitext(file.filename)[1]
        file_path = f"documents/{document_id}{file_extension}"
        
        # 保存文件
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # 处理文档
        result = ai_service.process_document(file_path, document_id)
        
        # 如果指定了模型，使用AI分析文档
        analysis = ""
        if model and model_name:
            async def get_analysis():
                async for chunk in ai_service.process_query_stream(
                    query="请总结这篇文档的主要内容",
                    model_provider=model,
                    model_name=model_name,
                    document_id=document_id,
                    use_rag=True
                ):
                    analysis += chunk
                return analysis

            analysis = await get_analysis()
        
        return {
            "document_id": document_id,
            "message": result,
            "analysis": analysis
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/documents/{document_id}")
async def delete_document(
    document_id: str,
    current_user: User = Depends(get_current_user)
):
    """删除文档"""
    try:
        # 删除文档文件
        for ext in ['.pdf', '.docx', '.txt']:
            file_path = f"documents/{document_id}{ext}"
            if os.path.exists(file_path):
                os.remove(file_path)
        
        # 删除向量存储中的文档数据
        ai_service.delete_document(document_id)
        
        return {"message": "文档删除成功"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/history")
async def get_history(
    skip: int = 0,
    limit: int = 10,
    current_user: User = Depends(get_current_user)
):
    return await get_user_history(current_user.get("sub"), skip, limit)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
