import os
import json
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from anthropic import AsyncAnthropic
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

API_KEY = os.getenv("ANTHROPIC_AUTH_TOKEN", "")
BASE_URL = os.getenv("ANTHROPIC_BASE_URL", "https://api.anthropic.com")
MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514")


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


def get_client() -> AsyncAnthropic:
    if not API_KEY:
        raise HTTPException(status_code=500, detail="未配置 ANTHROPIC_AUTH_TOKEN")
    return AsyncAnthropic(api_key=API_KEY, base_url=BASE_URL)


@app.get("/api/health")
async def health():
    return {"status": "ok", "model": MODEL}


def _extract_json(text: str) -> dict:
    """从 AI 回复中提取 JSON（兼容 ```json 代码块包裹）"""
    text = text.strip()
    if text.startswith("```"):
        # 去掉 ```json ... ``` 包裹
        lines = text.split("\n")
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines)
    return json.loads(text)


async def _call_ai(system_prompt: str, user_content: str, json_schema: dict) -> dict:
    client = get_client()
    try:
        response = await client.messages.create(
            model=MODEL,
            max_tokens=4096,
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_content},
            ],
            tools=[
                {
                    "name": "output_diagram",
                    "description": "输出结构化图表数据",
                    "input_schema": json_schema,
                }
            ],
            tool_choice={"type": "tool", "name": "output_diagram"},
        )
    except Exception as e:
        logger.error(f"Anthropic API error: {e}")
        raise HTTPException(status_code=500, detail=f"AI 调用失败: {str(e)}")

    # 从 tool_use 中提取 JSON
    for block in response.content:
        if block.type == "tool_use" and block.name == "output_diagram":
            return block.input

    raise HTTPException(status_code=500, detail="AI 未返回有效的结构化数据")


@app.post("/api/generate")
async def generate(req: DiagramGenerateRequest):
    system_prompt = get_system_prompt(req.type)
    json_schema = FLOWCHART_JSON_SCHEMA if req.type == "flowchart" else ER_DIAGRAM_JSON_SCHEMA

    data = await _call_ai(system_prompt, req.description, json_schema)

    if req.type == "flowchart":
        flowchart_data = FlowchartData(**data)
        return DiagramResponse(type=req.type, data=flowchart_data)
    else:
        er_data = ERDiagramData(**data)
        return DiagramResponse(type=req.type, data=er_data)


@app.post("/api/regenerate")
async def regenerate(req: DiagramRegenerateRequest):
    system_prompt = get_system_prompt(req.type)
    json_schema = FLOWCHART_JSON_SCHEMA if req.type == "flowchart" else ER_DIAGRAM_JSON_SCHEMA

    user_content = f"请换一种结构重新生成以下内容，但保持核心逻辑不变：\n\n{req.description}"
    data = await _call_ai(system_prompt, user_content, json_schema)

    if req.type == "flowchart":
        flowchart_data = FlowchartData(**data)
        return DiagramResponse(type=req.type, data=flowchart_data)
    else:
        er_data = ERDiagramData(**data)
        return DiagramResponse(type=req.type, data=er_data)
