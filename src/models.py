"""Pydantic data models for the SiteSense Zero-Rework RFI Agent."""
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class HazardLevel(str, Enum):
    CRITICAL_STOP_WORK = "CRITICAL_STOP_WORK"  # Immediate structural/life safety hazard
    CAUTION_VERIFY = "CAUTION_VERIFY"          # Requires supervisor sign-off or depth restrictions
    SAFE_PROCEED = "SAFE_PROCEED"              # Clear according to all past RFIs and blueprints


class Discipline(str, Enum):
    STRUCTURAL = "Structural"
    ELECTRICAL = "Electrical"
    MEP = "Mechanical & Plumbing"
    FIRE_PROTECTION = "Fire Protection"
    ARCHITECTURAL = "Architectural"


class RFIDocument(BaseModel):
    id: str = Field(..., description="Unique RFI Identifier, e.g., RFI-104")
    title: str = Field(..., description="Short descriptive title of change")
    date_issued: str = Field(..., description="ISO Date or relative date string")
    discipline: Discipline = Field(..., description="Engineering discipline")
    level: str = Field(..., description="Floor level, e.g., Level 3")
    grid_location: str = Field(..., description="Structural grid location, e.g., Grid B-4")
    issue_description: str = Field(..., description="The original problem or query submitted")
    approved_resolution: str = Field(..., description="Architect/Engineer signed off change")
    hazard_level: HazardLevel = Field(default=HazardLevel.SAFE_PROCEED)
    critical_directives: List[str] = Field(default_factory=list, description="Strict instructions/restrictions")
    tags: List[str] = Field(default_factory=list)
    rework_cost_risk: float = Field(0.0, description="Estimated dollar rework/damage if ignored")

    def to_hindsight_content(self) -> str:
        """Format the RFI into rich narrative text for Hindsight memory retention."""
        directives_str = "\n".join(f"- {d}" for d in self.critical_directives) if self.critical_directives else "None"
        return (
            f"OFFICIAL CONSTRUCTION RFI RECORD: [{self.id}] - {self.title}\n"
            f"Date Approved: {self.date_issued} | Discipline: {self.discipline.value}\n"
            f"Location: {self.level}, {self.grid_location}\n"
            f"Issue: {self.issue_description}\n"
            f"Approved Engineering Resolution: {self.approved_resolution}\n"
            f"Safety Hazard Rating: {self.hazard_level.value}\n"
            f"Estimated Rework Cost if Severed: ${self.rework_cost_risk:,.2f}\n"
            f"Critical Field Directives:\n{directives_str}"
        )


class WorkerQueryRequest(BaseModel):
    question: str = Field(..., description="Worker's prompt or spoken question from site")
    worker_role: Optional[str] = Field("Site Subcontractor", description="Role of the worker")
    level: Optional[str] = Field(None, description="Current level/floor, e.g., Level 3")
    grid_location: Optional[str] = Field(None, description="Grid coordinate, e.g., Grid B-4")
    action_type: Optional[str] = Field(None, description="Action planned: Core Drilling, Wall Anchor, Pipe Penetration")


class RecalledMemoryItem(BaseModel):
    id: Optional[str] = None
    rfi_id: Optional[str] = None
    text: str
    relevance_score: Optional[float] = None
    timestamp: Optional[str] = None
    tags: List[str] = Field(default_factory=list)


class WorkerQueryResponse(BaseModel):
    status: HazardLevel
    verdict: str
    summary_message: str
    hazard_details: str
    recalled_rfis: List[Dict[str, Any]] = Field(default_factory=list)
    critical_directives: List[str] = Field(default_factory=list)
    recommended_alternative: str
    rework_cost_prevented: float = 0.0
    hindsight_memory_hits: int = 0
    stateless_contrast: Optional[str] = None


class ComparisonItem(BaseModel):
    scenario_title: str
    worker_question: str
    location: str
    stateless_behavior: Dict[str, Any]
    hindsight_behavior: Dict[str, Any]
    rework_cost_prevented: float
    safety_danger_prevented: str
