from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from app.schemas.evidence import FieldEvidence

class PersonalInfo(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    linkedin: Optional[str] = None
    github: Optional[str] = None

class Experience(BaseModel):
    job_title: Optional[str] = None
    company: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    is_current: Optional[bool] = None
    description: list[str] = Field(default_factory=list)

class Education(BaseModel):
    degree: Optional[str] = None
    institution: Optional[str] = None
    graduation_year: Optional[int] = None
    field_of_study: Optional[str] = None

class Certification(BaseModel):
    name: Optional[str] = None
    issuer: Optional[str] = None
    date: Optional[str] = None

class Project(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    technologies: list[str] = Field(default_factory=list)

class ParsedResume(BaseModel):
    personal_info: PersonalInfo = Field(default_factory=PersonalInfo)
    professional_summary: Optional[str] = None
    skills: list[str] = Field(default_factory=list)
    experience: list[Experience] = Field(default_factory=list)
    education: list[Education] = Field(default_factory=list)
    certifications: list[Certification] = Field(default_factory=list)
    projects: list[Project] = Field(default_factory=list)
    languages: list[str] = Field(default_factory=list)
    raw_text: Optional[str] = None
    evidence: Optional[dict[str, FieldEvidence]] = None
    confidence_score: Optional[float] = None
    low_confidence_fields: list[str] = Field(default_factory=list)

class ParseResponse(BaseModel):
    id: str
    filename: str
    parsed_resume: ParsedResume
    created_at: datetime = Field(default_factory=datetime.now)

