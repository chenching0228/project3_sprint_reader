from typing import List, Optional, Dict, Any
from pydantic import BaseModel


class ModuleMetadataResponse(BaseModel):
    module_id: str
    source_document: str
    source: str
    domains: List[str]
    warning_text: str


class FlashcardPageResponse(BaseModel):
    page_id: str
    sequence_number: int
    title: str
    domain_tag: str
    page_content_json: Dict[str, Any]


class FlashcardListResponse(BaseModel):
    module_id: str
    pages: List[FlashcardPageResponse]


class StartSessionRequest(BaseModel):
    agent_id: str
    module_id: str


class StartSessionResponse(BaseModel):
    sprint_id: str
    module_id: str
    remaining_time: int
    tab_switch_count: int
    is_paused: bool
    completion_status: str


class PauseResumeRequest(BaseModel):
    remaining_time: int


class ProgressUpdateRequest(BaseModel):
    remaining_time: int


class CompleteSessionRequest(BaseModel):
    completion_status: str
    remaining_time: int


class SessionStateResponse(BaseModel):
    sprint_id: str
    is_paused: bool
    tab_switch_count: int
    remaining_time: Optional[int] = None


class CompleteSessionResponse(BaseModel):
    sprint_id: str
    session_id: str
    completion_status: str
    redirect_url: str