from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class MOAttributes(BaseModel):
    entry_method: Optional[str] = Field(None, description="Extracted entry or infiltration method")
    weapon_tool: Optional[str] = Field(None, description="Extracted weapon, tool, instrument or digital vector")
    target_type: Optional[str] = Field(None, description="Extracted target or victim classification")
    time_pattern: Optional[str] = Field(None, description="Extracted temporal/operating time pattern")
    approach_method: Optional[str] = Field(None, description="Extracted modus/approach technique")
    escape_method: Optional[str] = Field(None, description="Extracted getaway, laundering or evasion method")
    location_type: Optional[str] = Field(None, description="Extracted location/environmental context")

class AssociatedSuspect(BaseModel):
    accused_id: int
    name: str
    person_id: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None

class SimilarCaseMatch(BaseModel):
    case_id: int
    crime_no: Optional[str] = None
    case_no: Optional[str] = None
    crime_type: str
    district: str
    police_station: str
    registered_date: Optional[str] = None
    similarity_score: float = Field(..., ge=0.0, le=1.0, description="Mathematical cosine similarity score between 0.0 and 1.0")
    similarity_percentage: int = Field(..., ge=0, le=100, description="Similarity score expressed as percentage")
    is_cross_jurisdiction: bool = Field(False, description="True if case occurred in a different district/station")
    matching_attributes: List[str] = Field(default_factory=list, description="Overlapping behavioral attributes and tags")
    associated_suspects: List[AssociatedSuspect] = Field(default_factory=list, description="Suspects linked to this similar case")

class MOProfileResponse(BaseModel):
    case_id: int
    crime_no: Optional[str] = None
    case_no: Optional[str] = None
    crime_type: str
    district: Optional[str] = None
    police_station: Optional[str] = None
    registered_date: Optional[str] = None
    raw_narrative: Optional[str] = None
    is_sufficient: bool = Field(True, description="False if text is missing or insufficient for MO extraction")
    mo_summary: str
    attributes: MOAttributes
    behavioral_tags: List[str] = Field(default_factory=list)
    associated_suspects: List[AssociatedSuspect] = Field(default_factory=list)
    similar_cases: List[SimilarCaseMatch] = Field(default_factory=list)
    interpretation_disclaimer: str = Field(
        default="Investigative Intelligence: Behavioral similarity indicates matching crime patterns and potential investigative leads, not definitive attribution."
    )

class OffenderCaseSummary(BaseModel):
    case_id: int
    crime_no: Optional[str] = None
    crime_type: str
    registered_date: Optional[str] = None
    district: Optional[str] = None
    police_station: Optional[str] = None
    mo_summary: str
    behavioral_tags: List[str] = Field(default_factory=list)

class OffenderBehavioralProfileResponse(BaseModel):
    accused_id: int
    name: str
    person_id: Optional[str] = None
    total_associated_cases: int
    has_sufficient_history: bool
    recurring_mo_signatures: List[str] = Field(default_factory=list)
    primary_crime_types: List[str] = Field(default_factory=list)
    primary_districts: List[str] = Field(default_factory=list)
    associated_cases: List[OffenderCaseSummary] = Field(default_factory=list)
    interpretation_disclaimer: str = Field(
        default="Offender Behavioral Profile reflects documented case associations. Behavioral patterns represent historical patterns for investigative context."
    )

class CrossJurisdictionLink(BaseModel):
    source_case_id: int
    source_crime_no: Optional[str] = None
    source_district: str
    target_case_id: int
    target_crime_no: Optional[str] = None
    target_district: str
    crime_type: str
    similarity_score: float
    similarity_percentage: int
    matching_attributes: List[str]

class CrossJurisdictionSummary(BaseModel):
    total_cross_jurisdiction_patterns: int
    jurisdiction_pairs: List[Dict[str, Any]]
    sample_links: List[CrossJurisdictionLink]
