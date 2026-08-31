import os
import json
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

# API 配置 — 兼容 OpenAI 格式的 Qwen/GLM 代理
API_KEY = os.getenv("API_KEY", os.getenv("ANTHROPIC_AUTH_TOKEN", ""))
BASE_URL = os.getenv("BASE_URL", os.getenv("ANTHROPIC_BASE_URL", "https://api.openai.com/v1"))
MODEL = os.getenv("MODEL", os.getenv("ANTHROPIC_MODEL", "qwen-plus"))


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


def get_client() -> AsyncOpenAI:
    if not API_KEY:
        raise HTTPException(status_code=500, detail="未配置 API_KEY")
    return AsyncOpenAI(api_key=API_KEY, base_url=BASE_URL)


@app.get("/api/health")
async def health():
    return {"status": "ok", "model": MODEL}


def _extract_json(text: str) -> dict:
    """从 AI 回复中提取 JSON（兼容 ```json 代码块包裹）"""
    text = text.strip()
    if text.startswith("```"):
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
        response = await client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content},
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
        logger.error(f"AI API error: {e}")
        raise HTTPException(status_code=500, detail=f"AI 调用失败: {str(e)}")

    try:
        return _extract_json(response.choices[0].message.content)
    except Exception as e:
        logger.error(f"JSON parse error: {e}, raw: {response.choices[0].message.content[:200]}")
        raise HTTPException(status_code=500, detail="AI 返回格式解析失败")


@app.post("/api/generate")
async def generate(req: DiagramGenerateRequest):
    system_prompt = get_system_prompt(req.type)
    json_schema = FLOWCHART_JSON_SCHEMA if req.type == "flowchart" else ER_DIAGRAM_JSON_SCHEMA

    data = await _call_ai(system_prompt, req.description, json_schema)

    if req.type == "flowchart":
        # 兼容旧 schema 的字段映射
        nodes = [{"id": n["id"], "type": n["type"], "label": n["text"]} for n in data.get("nodes", [])]
        edges = [{"from": e["from"], "to": e["to"], "label": e.get("label", "")} for e in data.get("edges", [])]
        flowchart_data = FlowchartData(nodes=nodes, edges=edges)
        return DiagramResponse(type=req.type, data=flowchart_data)
    else:
        # ER 图字段映射
        entities = []
        for e in data.get("entities", []):
            entities.append({
                "id": e["id"],
                "name": e["name"],
                "attributes": [
                    {"name": a["name"], "is_primary_key": a.get("primary_key", False)}
                    for a in e.get("attributes", [])
                ]
            })
        relationships = []
        for r in data.get("relationships", []):
            relationships.append({
                "id": r["id"],
                "name": r["name"],
                "from_entity": r["from"],
                "to_entity": r["to"],
                "from_cardinality": r.get("cardinality", {}).get("from", "N"),
                "to_cardinality": r.get("cardinality", {}).get("to", "M"),
                "attributes": []
            })
        er_data = ERDiagramData(entities=entities, relationships=relationships)
        return DiagramResponse(type=req.type, data=er_data)


@app.post("/api/regenerate")
async def regenerate(req: DiagramRegenerateRequest):
    system_prompt = get_system_prompt(req.type)
    json_schema = FLOWCHART_JSON_SCHEMA if req.type == "flowchart" else ER_DIAGRAM_JSON_SCHEMA

    user_content = f"请换一种结构重新生成以下内容，但保持核心逻辑不变：\n\n{req.description}"
    data = await _call_ai(system_prompt, user_content, json_schema)

    if req.type == "flowchart":
        nodes = [{"id": n["id"], "type": n["type"], "label": n["text"]} for n in data.get("nodes", [])]
        edges = [{"from": e["from"], "to": e["to"], "label": e.get("label", "")} for e in data.get("edges", [])]
        flowchart_data = FlowchartData(nodes=nodes, edges=edges)
        return DiagramResponse(type=req.type, data=flowchart_data)
    else:
        entities = []
        for e in data.get("entities", []):
            entities.append({
                "id": e["id"],
                "name": e["name"],
                "attributes": [
                    {"name": a["name"], "is_primary_key": a.get("primary_key", False)}
                    for a in e.get("attributes", [])
                ]
            })
        relationships = []
        for r in data.get("relationships", []):
            relationships.append({
                "id": r["id"],
                "name": r["name"],
                "from_entity": r["from"],
                "to_entity": r["to"],
                "from_cardinality": r.get("cardinality", {}).get("from", "N"),
                "to_cardinality": r.get("cardinality", {}).get("to", "M"),
                "attributes": []
            })
        er_data = ERDiagramData(entities=entities, relationships=relationships)
        return DiagramResponse(type=req.type, data=er_data)
