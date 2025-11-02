"""
Pydantic schemas for website analysis and automation recommendations
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, HttpUrl
from enum import Enum

class BusinessType(str, Enum):
    ECOMMERCE = "ecommerce"
    SERVICE = "service"
    BLOG = "blog"
    SAAS = "saas"
    PORTFOLIO = "portfolio"
    CORPORATE = "corporate"
    NONPROFIT = "nonprofit"
    OTHER = "other"

class AutomationCategory(str, Enum):
    AGENT = "agent"
    BOOKING = "booking"
    MARKETING = "marketing"
    LEAD_GENERATION = "lead_generation"
    SOCIAL_MEDIA = "social_media"
    ANALYTICS = "analytics"
    AUTOMATION = "automation"

class Priority(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class FormInfo(BaseModel):
    action: Optional[str] = None
    method: str = "GET"
    inputs: List[str] = Field(default_factory=list)
    has_email: bool = False
    has_phone: bool = False
    purpose: Optional[str] = None  # contact, newsletter, checkout, etc

class CTAInfo(BaseModel):
    text: str
    url: Optional[str] = None
    type: str  # button, link, form_submit

class WebsiteExtraction(BaseModel):
    url: str
    title: Optional[str] = None
    description: Optional[str] = None
    h1_tags: List[str] = Field(default_factory=list)
    h2_tags: List[str] = Field(default_factory=list)
    nav_links: List[Dict[str, str]] = Field(default_factory=list)
    forms: List[FormInfo] = Field(default_factory=list)
    ctas: List[CTAInfo] = Field(default_factory=list)
    content_text: str = ""  # Main content
    keywords: List[str] = Field(default_factory=list)
    business_type: BusinessType = BusinessType.OTHER
    has_blog: bool = False
    has_shop: bool = False
    has_booking: bool = False
    social_links: Dict[str, str] = Field(default_factory=dict)
    structured_data: List[Dict[str, Any]] = Field(default_factory=list)

class WorkflowConfig(BaseModel):
    """Basic workflow configuration hints"""
    trigger_type: str  # webhook, schedule, manual
    actions: List[str] = Field(default_factory=list)
    estimated_setup_time: str = "5-10 minutes"

class AutomationRecommendation(BaseModel):
    key: str  # Unique identifier like 'ai-chatbot', 'lead-capture'
    title: str
    description: str
    rationale: str  # Why this automation is recommended
    expected_impact: str  # What results to expect
    category: AutomationCategory
    priority: Priority
    workflow_config: Optional[WorkflowConfig] = None
    estimated_value: Optional[str] = None  # e.g., "20% increase in conversions"

class WebsiteAnalysis(BaseModel):
    url: str
    business_type: BusinessType
    summary: str  # Overall analysis
    strengths: List[str] = Field(default_factory=list)
    opportunities: List[str] = Field(default_factory=list)
    recommendations: List[AutomationRecommendation] = Field(default_factory=list)
    confidence_score: float = Field(ge=0.0, le=1.0, default=0.8)
