from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

# Enums
class CampaignStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class ProcessType(str, Enum):
    SEQUENTIAL = "sequential"
    HIERARCHICAL = "hierarchical"

# Schémas de base
class AgentBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    role: str = Field(..., min_length=1, max_length=200)
    goal: str = Field(..., min_length=1)
    backstory: Optional[str] = None
    enabled_tools: List[str] = Field(default_factory=list)
    max_iter: int = Field(default=3, ge=1, le=10)
    verbose: bool = True
    memory: bool = False
    allow_delegation: bool = False

class AgentCreate(AgentBase):
    pass

class AgentUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    role: Optional[str] = Field(None, min_length=1, max_length=200)
    goal: Optional[str] = Field(None, min_length=1)
    backstory: Optional[str] = None
    enabled_tools: Optional[List[str]] = None
    max_iter: Optional[int] = Field(None, ge=1, le=10)
    verbose: Optional[bool] = None
    memory: Optional[bool] = None
    allow_delegation: Optional[bool] = None

class AgentResponse(AgentBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Schémas pour les crews
class CrewBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    process_type: ProcessType = ProcessType.SEQUENTIAL

class CrewCreate(CrewBase):
    selected_agents: List[str] = Field(..., min_items=1)

class CrewUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    process_type: Optional[ProcessType] = None
    selected_agents: Optional[List[str]] = Field(None, min_items=1)

class CrewAgentResponse(BaseModel):
    id: int
    name: str
    role: str
    order: int
    
    class Config:
        from_attributes = True

class CrewResponse(CrewBase):
    id: int
    created_at: datetime
    updated_at: datetime
    agents: List[CrewAgentResponse] = []
    
    class Config:
        from_attributes = True

# Schémas pour les campagnes
class CampaignBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    problem_statement: str = Field(..., min_length=1)
    company_context: Optional[str] = None

class CampaignCreate(CampaignBase):
    crew_id: int

class CampaignUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    problem_statement: Optional[str] = Field(None, min_length=1)
    company_context: Optional[str] = None
    status: Optional[CampaignStatus] = None

class CampaignFileResponse(BaseModel):
    id: int
    filename: str
    file_path: str
    file_type: str
    file_size: Optional[int]
    created_at: datetime
    
    class Config:
        from_attributes = True

class AgentOutputResponse(BaseModel):
    id: int
    agent_name: str
    output_content: str
    output_type: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class CampaignResponse(CampaignBase):
    id: int
    crew_id: int
    status: CampaignStatus
    result: Optional[str]
    created_at: datetime
    completed_at: Optional[datetime]
    files: List[CampaignFileResponse] = []
    agent_outputs: List[AgentOutputResponse] = []
    
    class Config:
        from_attributes = True

# Schémas pour l'exécution des campagnes
class CampaignExecutionRequest(BaseModel):
    problem_statement: str = Field(..., min_length=1)
    company_context: Optional[str] = None
    crew_id: int
    openai_api_key: str = Field(..., min_length=1)
    serper_api_key: Optional[str] = None
    openai_model: str = Field(default="gpt-4o-mini")

class CampaignExecutionResponse(BaseModel):
    campaign_id: int
    status: CampaignStatus
    message: str
    result: Optional[str] = None

# Schémas pour les fichiers
class FileUploadResponse(BaseModel):
    filename: str
    file_path: str
    file_size: int
    message: str

class FileListResponse(BaseModel):
    files: List[CampaignFileResponse]
    total_count: int

# Schémas pour les réponses d'API
class APIResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None

class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    size: int
    pages: int

# Schémas pour les statistiques
class DashboardStats(BaseModel):
    total_agents: int
    total_crews: int
    total_campaigns: int
    completed_campaigns: int
    pending_campaigns: int
    failed_campaigns: int
    total_files: int

# Schémas pour la configuration
class APIConfig(BaseModel):
    openai_api_key: Optional[str] = None
    serper_api_key: Optional[str] = None
    openai_model: str = "gpt-4o-mini"
    database_url: Optional[str] = None

# Schémas pour les outils disponibles
class ToolInfo(BaseModel):
    name: str
    description: str
    enabled: bool

class ToolsResponse(BaseModel):
    tools: Dict[str, ToolInfo]
