from pydantic import BaseModel
from typing import Dict, Any, List

class NetworkNode(BaseModel):
    id: str
    type: str
    label: str
    metadata: Dict[str, Any]

class NetworkEdge(BaseModel):
    source: str
    target: str
    relationship: str

class NetworkGraphResponse(BaseModel):
    nodes: List[NetworkNode]
    edges: List[NetworkEdge]
    total_nodes: int
    total_edges: int

    model_config = {
        "from_attributes": True
    }
