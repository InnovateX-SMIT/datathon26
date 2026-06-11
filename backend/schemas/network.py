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

class CentralityScore(BaseModel):
    id: str
    type: str
    label: str
    score: float

class CentralityResponse(BaseModel):
    degree: List[CentralityScore]
    betweenness: List[CentralityScore]
    closeness: List[CentralityScore]

class ClusterMember(BaseModel):
    id: str
    type: str
    label: str

class ClusterResponse(BaseModel):
    cluster_id: str
    members: List[ClusterMember]
    size: int
    criminal_count: int
    crime_count: int
    location_count: int

class AssociationPartner(BaseModel):
    id: str
    type: str
    label: str
    metadata: Dict[str, Any]

class AssociationSharedCrime(BaseModel):
    id: str
    type: str
    label: str
    metadata: Dict[str, Any]

class AssociationResponse(BaseModel):
    criminal_a: AssociationPartner
    criminal_b: AssociationPartner
    shared_crimes: List[AssociationSharedCrime]
    frequency: int
    strength: float

class LocationIntelInfo(BaseModel):
    id: str
    district: str
    state: str
    degree: int
    crime_count: int
    criminal_count: int

class LocationIntelPartner(BaseModel):
    id: str
    type: str
    label: str

class LocationLinkInfo(BaseModel):
    location_a: LocationIntelPartner
    location_b: LocationIntelPartner
    connecting_criminals: List[LocationIntelPartner]
    strength: int

class LocationNetworkResponse(BaseModel):
    most_active: List[LocationIntelInfo]
    most_connected: List[LocationIntelInfo]
    location_links: List[LocationLinkInfo]

class LinkAnalysisNode(BaseModel):
    id: str
    type: str
    label: str

class LinkAnalysisEdge(BaseModel):
    source: str
    target: str
    relationship: str

class LinkAnalysisResponse(BaseModel):
    path_found: bool
    nodes: List[LinkAnalysisNode]
    edges: List[LinkAnalysisEdge]
    path_length: int

