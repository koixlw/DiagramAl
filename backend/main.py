import os
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from openai import AsyncOpenAI
from dotenv import load_dotenv

from schemas import (
    DiagramGenerateRequest,
    DiagramRegenerateRequest,
    DiagramResponse,
    FlowchartData,
    ERDiagramData,
    FLOWCHART_JSON_SCHEMA,
    ER_DIAGRAM_JSON_SCHEMA,
)
from prompt_engine import get_system_prompt

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

API_KEY = os.getenv("OPENAI_API_KEY", "")
BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("DiagramAI backend started")
    yield
    logger.info("DiagramAI backend stopped")


app = FastAPI(title="DiagramAI", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_openai_client() -> AsyncOpenAI:
    if not API_KEY:
        raise HTTPException(status_code=500, detail="未配置 OPENAI_API_KEY")
    return AsyncOpenAI(api_key=API_KEY, base_url=BASE_URL)


@app.get("/api/health")
async def health():
    return {"status": "ok", "model": MODEL}


@app.post("/api/generate")
async def generate(req: DiagramGenerateRequest):
    client = get_openai_client()
    system_prompt = get_system_prompt(req.type)

    json_schema = FLOWCHART_JSON_SCHEMA if req.type == "flowchart" else ER_DIAGRAM_JSON_SCHEMA

    try:
        response = await client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": req.description},
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "diagram_output",
                    "schema": json_schema,
                    "strict": True,
                },
            },
        )
    except Exception as e:
        logger.error(f"OpenAI API error: {e}")
        raise HTTPException(status_code=500, detail=f"AI 调用失败: {str(e)}")

    try:
        import json
        data = json.loads(response.choices[0].message.content)
    except Exception as e:
        logger.error(f"JSON parse error: {e}")
        raise HTTPException(status_code=500, detail="AI 返回格式解析失败")

    if req.type == "flowchart":
        flowchart_data = FlowchartData(**data)
        return DiagramResponse(type=req.type, data=flowchart_data)
    else:
        er_data = ERDiagramData(**data)
        return DiagramResponse(type=req.type, data=er_data)


@app.post("/api/regenerate")
async def regenerate(req: DiagramRegenerateRequest):
    """重新生成：在原始描述基础上加入"换一种表达方式"的提示"""
    client = get_openai_client()
    system_prompt = get_system_prompt(req.type)

    json_schema = FLOWCHART_JSON_SCHEMA if req.type == "flowchart" else ER_DIAGRAM_JSON_SCHEMA

    try:
        response = await client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"请换一种结构重新生成以下内容，但保持核心逻辑不变：\n\n{req.description}"},
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "diagram_output",
                    "schema": json_schema,
                    "strict": True,
                },
            },
        )
    except Exception as e:
        logger.error(f"OpenAI API error: {e}")
        raise HTTPException(status_code=500, detail=f"AI 调用失败: {str(e)}")

    try:
        import json
        data = json.loads(response.choices[0].message.content)
    except Exception as e:
        logger.error(f"JSON parse error: {e}")
        raise HTTPException(status_code=500, detail="AI 返回格式解析失败")

    if req.type == "flowchart":
        flowchart_data = FlowchartData(**data)
        return DiagramResponse(type=req.type, data=flowchart_data)
    else:
        er_data = ERDiagramData(**data)
        return DiagramResponse(type=req.type, data=er_data)
