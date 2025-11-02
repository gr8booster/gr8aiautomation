"""
MongoDB Pydantic models for GR8 AI Automation
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

class AutomationStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    DRAFT = "draft"

class ExecutionState(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class Website(BaseModel):
    id: str
    owner_id: str = "anonymous"  # No auth initially
    url: str
    title: Optional[str] = None
    business_type: str = "other"
    fetched_at: datetime
    analysis_summary: str = ""
    content_digest: str = ""

class AutomationTemplate(BaseModel):
    id: str
    key: str
    name: str
    description: str
    category: str
    workflow_json: Dict[str, Any] = Field(default_factory=dict)
    version: int = 1

class ActiveAutomation(BaseModel):
    id: str
    owner_id: str = "anonymous"
    website_id: str
    template_id: str
    name: str
    status: AutomationStatus
    config: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime

class Workflow(BaseModel):
    id: str
    owner_id: str = "anonymous"
    website_id: str
    name: str
    nodes: List[Dict[str, Any]] = Field(default_factory=list)
    edges: List[Dict[str, Any]] = Field(default_factory=list)
    variables: Dict[str, Any] = Field(default_factory=dict)
    version: int = 1

class Execution(BaseModel):
    id: str
    workflow_id: str
    triggered_by: str = "manual"
    state: ExecutionState
    started_at: datetime
    finished_at: Optional[datetime] = None
    logs: List[str] = Field(default_factory=list)
    metrics: Dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = None

class AnalysisRequest(BaseModel):
    url: str

class AnalysisResponse(BaseModel):
    analysis_id: str
    url: str
    summary: str
    business_type: str
    strengths: List[str]
    opportunities: List[str]
    recommendations: List[Dict[str, Any]]
    confidence_score: float

class AutomationActivateRequest(BaseModel):
    website_id: str
    recommendation_key: str
    config: Optional[Dict[str, Any]] = None
