from pydantic import BaseModel, Field
from typing import List, Literal, Optional
from enum import Enum


# ============================================================
# 请求模型
# ============================================================

class DiagramType(str, Enum):
    FLOWCHART = "flowchart"
    ER = "er"


class DiagramGenerateRequest(BaseModel):
    type: DiagramType
    description: str = Field(..., min_length=1, description="用户对图表的自然语言描述")


class DiagramRegenerateRequest(BaseModel):
    type: DiagramType
    description: str = Field(..., min_length=1, description="用户对图表的自然语言描述")


# ============================================================
# 流程图输出模型
# ============================================================

class FlowchartNode(BaseModel):
    id: str = Field(..., description="节点唯一标识")
    type: Literal["start", "end", "process", "decision", "io", "connector"] = Field(
        ..., description="节点类型"
    )
    label: str = Field(..., description="节点显示文本")


class FlowchartEdge(BaseModel):
    from_node: str = Field(..., alias="from", description="起始节点 ID")
    to_node: str = Field(..., alias="to", description="目标节点 ID")
    label: Optional[str] = Field(None, description="连线标签（如 是/否）")


class FlowchartData(BaseModel):
    nodes: List[FlowchartNode] = Field(default_factory=list)
    edges: List[FlowchartEdge] = Field(default_factory=list)


# ============================================================
# ER 图输出模型
# ============================================================

class ERAttribute(BaseModel):
    name: str = Field(..., description="属性名称")
    is_primary_key: bool = Field(default=False, description="是否为主键")


class EREntity(BaseModel):
    id: str = Field(..., description="实体唯一标识")
    name: str = Field(..., description="实体名称")
    attributes: List[ERAttribute] = Field(default_factory=list, description="属性列表")


class ERRelationship(BaseModel):
    id: str = Field(..., description="关系唯一标识")
    name: str = Field(..., description="关系名称")
    from_entity: str = Field(..., description="起始实体 ID")
    to_entity: str = Field(..., description="目标实体 ID")
    from_cardinality: str = Field(..., description="起始端基数，如 1/N/M")
    to_cardinality: str = Field(..., description="目标端基数，如 1/N/M")
    attributes: List[ERAttribute] = Field(default_factory=list, description="关系自身的属性")


class ERDiagramData(BaseModel):
    entities: List[EREntity] = Field(default_factory=list)
    relationships: List[ERRelationship] = Field(default_factory=list)


# ============================================================
# 统一响应模型
# ============================================================

class DiagramResponse(BaseModel):
    type: DiagramType
    data: FlowchartData | ERDiagramData


# ============================================================
# OpenAI Structured Outputs JSON Schema
# 用于强制 AI 输出标准格式
# ============================================================

FLOWCHART_JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "nodes": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "string", "description": "节点唯一标识，如 node_1"},
                    "type": {
                        "type": "string",
                        "enum": ["start", "end", "process", "decision", "io", "connector"],
                        "description": "节点类型"
                    },
                    "label": {"type": "string", "description": "节点显示的文本"}
                },
                "required": ["id", "type", "label"],
                "additionalProperties": False
            },
            "description": "流程图中的所有节点"
        },
        "edges": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "from": {"type": "string", "description": "起始节点 ID"},
                    "to": {"type": "string", "description": "目标节点 ID"},
                    "label": {"type": "string", "description": "连线标签，判断节点分支填 是/否"}
                },
                "required": ["from", "to"],
                "additionalProperties": False
            },
            "description": "节点之间的连线"
        }
    },
    "required": ["nodes", "edges"],
    "additionalProperties": False
}

ER_DIAGRAM_JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "entities": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "string", "description": "实体唯一标识，如 entity_1"},
                    "name": {"type": "string", "description": "实体名称"},
                    "attributes": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string", "description": "属性名称"},
                                "is_primary_key": {"type": "boolean", "description": "是否为主键"}
                            },
                            "required": ["name", "is_primary_key"],
                            "additionalProperties": False
                        },
                        "description": "实体的属性列表"
                    }
                },
                "required": ["id", "name", "attributes"],
                "additionalProperties": False
            },
            "description": "所有实体"
        },
        "relationships": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "string", "description": "关系唯一标识，如 rel_1"},
                    "name": {"type": "string", "description": "关系名称"},
                    "from_entity": {"type": "string", "description": "起始实体 ID"},
                    "to_entity": {"type": "string", "description": "目标实体 ID"},
                    "from_cardinality": {
                        "type": "string",
                        "description": "起始端基数，1、N 或 M"
                    },
                    "to_cardinality": {
                        "type": "string",
                        "description": "目标端基数，1、N 或 M"
                    },
                    "attributes": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string", "description": "关系属性名称"},
                                "is_primary_key": {"type": "boolean", "description": "是否为主键"}
                            },
                            "required": ["name", "is_primary_key"],
                            "additionalProperties": False
                        },
                        "description": "关系自身的属性"
                    }
                },
                "required": ["id", "name", "from_entity", "to_entity", "from_cardinality", "to_cardinality"],
                "additionalProperties": False
            },
            "description": "实体之间的关系"
        }
    },
    "required": ["entities", "relationships"],
    "additionalProperties": False
}
