from pydantic import BaseModel, Field, ConfigDict
from typing import List, Literal, Optional, Union


# ============================================================
# 请求模型
# ============================================================

DiagramType = Literal["flowchart", "er"]


class DiagramGenerateRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    type: DiagramType
    description: str = Field(..., min_length=1, description="用户对图表的自然语言描述")


class DiagramRegenerateRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    type: DiagramType
    description: str = Field(..., min_length=1, description="用户对图表的自然语言描述")


# ============================================================
# 流程图输出模型（AI 返回格式）
# ============================================================

class FlowchartNode(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    id: str = Field(..., description="节点唯一标识")
    type: Literal["start_end", "process", "decision", "input_output", "connector"] = Field(
        ..., description="节点类型"
    )
    text: str = Field(..., description="节点显示文本")


class FlowchartEdge(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    from_: str = Field(..., alias="from", description="起始节点 ID")
    to: str = Field(..., alias="to", description="目标节点 ID")
    label: Optional[str] = Field("", description="连线标签（如 是/否）")


class FlowchartRaw(BaseModel):
    diagram_type: str
    title: str = ""
    nodes: List[FlowchartNode] = Field(default_factory=list)
    edges: List[FlowchartEdge] = Field(default_factory=list)


# ============================================================
# 内部统一数据模型
# ============================================================

class FlowchartData(BaseModel):
    nodes: List[dict] = Field(default_factory=list)
    edges: List[dict] = Field(default_factory=list)


# ============================================================
# ER 图输出模型（AI 返回格式）
# ============================================================

class ERAttribute(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    id: str = ""
    name: str = Field(..., description="属性名称")
    primary_key: bool = Field(default=False, description="是否为主键")


class EREntity(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    id: str = Field(..., description="实体唯一标识")
    name: str = Field(..., description="实体名称")
    attributes: List[ERAttribute] = Field(default_factory=list, description="属性列表")


class ERRelationship(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    id: str = Field(..., description="关系唯一标识")
    name: str = Field(..., description="关系名称")
    from_: str = Field(..., alias="from", description="起始实体 ID")
    to: str = Field(..., alias="to", description="目标实体 ID")
    cardinality: dict = Field(default_factory=lambda: {"from": "N", "to": "M"})
    attributes: List[ERAttribute] = Field(default_factory=list)


class ERDiagramRaw(BaseModel):
    diagram_type: str
    title: str = ""
    entities: List[EREntity] = Field(default_factory=list)
    relationships: List[ERRelationship] = Field(default_factory=list)


class ERDiagramData(BaseModel):
    entities: List[dict] = Field(default_factory=list)
    relationships: List[dict] = Field(default_factory=list)


# ============================================================
# 统一响应模型
# ============================================================

class DiagramResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    type: DiagramType
    data: Union[FlowchartData, ERDiagramData]


# ============================================================
# OpenAI/通义 JSON Schema
# ============================================================

FLOWCHART_JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "diagram_type": {"type": "string", "const": "flowchart"},
        "title": {"type": "string", "description": "流程图标题"},
        "nodes": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "string", "description": "节点唯一标识，如 node_1"},
                    "type": {
                        "type": "string",
                        "enum": ["start_end", "process", "decision", "input_output", "connector"],
                        "description": "节点类型"
                    },
                    "text": {"type": "string", "description": "节点显示的文本"}
                },
                "required": ["id", "type", "text"],
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
    "required": ["diagram_type", "nodes", "edges"],
    "additionalProperties": False
}

ER_DIAGRAM_JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "diagram_type": {"type": "string", "const": "er_diagram"},
        "title": {"type": "string", "description": "ER 图标题"},
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
                                "id": {"type": "string", "description": "属性唯一标识"},
                                "name": {"type": "string", "description": "属性名称"},
                                "primary_key": {"type": "boolean", "description": "是否为主键"}
                            },
                            "required": ["name", "primary_key"],
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
                    "from": {"type": "string", "description": "起始实体 ID"},
                    "to": {"type": "string", "description": "目标实体 ID"},
                    "cardinality": {
                        "type": "object",
                        "properties": {
                            "from": {"type": "string", "enum": ["1", "N", "M"], "description": "起始端基数"},
                            "to": {"type": "string", "enum": ["1", "N", "M"], "description": "目标端基数"}
                        },
                        "required": ["from", "to"],
                        "additionalProperties": False
                    },
                    "attributes": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "string"},
                                "name": {"type": "string"},
                                "primary_key": {"type": "boolean"}
                            },
                            "additionalProperties": False
                        },
                        "description": "关系自身的属性"
                    }
                },
                "required": ["id", "name", "from", "to", "cardinality"],
                "additionalProperties": False
            },
            "description": "实体之间的关系"
        }
    },
    "required": ["diagram_type", "entities", "relationships"],
    "additionalProperties": False
}
