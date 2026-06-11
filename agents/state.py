from typing import TypedDict, List, Dict, Any, Optional
from pydantic import BaseModel, Field

# ==========================================
# 1. Pydantic Models for Agent Outputs
# ==========================================

class WorkExperience(BaseModel):
    role: str = Field(description="Title of the role held, e.g., HR Specialist, Software Engineer.")
    company: str = Field(description="Name of the company or organization.")
    years: float = Field(description="Number of years in this role.")
    description: str = Field(description="Brief summary of duties and technologies used.")

class UserProfile(BaseModel):
    name: str = Field(default="Valued Candidate", description="Full name of the candidate.")
    education: str = Field(description="Highest degree obtained and major field of study.")
    previous_experience: List[WorkExperience] = Field(default_factory=list, description="List of previous jobs.")
    total_experience_years: float = Field(default=0.0, description="Sum of years across prior roles.")
    gap_duration_years: float = Field(description="Number of years of career break/gap.")
    gap_reason: str = Field(description="Brief reason for the career break, e.g., Childcare, Health, Caregiving, Relocation.")
    current_skills: List[str] = Field(default_factory=list, description="List of core competencies and software skills.")
    time_commitment_hours_per_day: float = Field(description="Available study hours per day for upskilling.")
    remote_preference: str = Field(description="Preferred work style: Remote, Hybrid, or In-Office.")
    additional_notes: Optional[str] = Field(default="", description="Any other goals, worries, or considerations.")

class CareerPath(BaseModel):
    title: str = Field(description="Name of the suggested career role.")
    suitability_reasoning: str = Field(description="Empathetic, clear justification of why this role matches her background and preferences.")
    remote_suitability_score: int = Field(description="Score from 1 to 10 indicating how remote-friendly this role is.")
    entry_barrier: str = Field(description="Entry barrier classification: Low, Medium, High.")
    target_companies: List[str] = Field(description="Companies offering returnship or hiring for this role.")
    demand_index_2026: str = Field(description="Expected market demand in 2026: High, Medium, Low.")

class CareerRecommendations(BaseModel):
    recommended_paths: List[CareerPath] = Field(description="List of 3 to 5 realistic, returnee-friendly career paths.")

class MissingSkill(BaseModel):
    skill_name: str = Field(description="Name of the missing or outdated skill.")
    importance_level: str = Field(description="Importance level: Critical, Important, Nice-to-have.")
    description: str = Field(description="Why this skill is needed for the recommended path.")

class SkillGapReport(BaseModel):
    target_role: str = Field(description="The primary target role analyzed.")
    matching_skills: List[str] = Field(description="Skills the candidate already possesses that are relevant to the role.")
    missing_skills: List[MissingSkill] = Field(description="Skills the candidate needs to learn or refresh.")

class ResourceLink(BaseModel):
    name: str = Field(description="Name of the course, certificate, or learning resource.")
    platform: str = Field(description="Platform host, e.g., Coursera, Google Certificates, YouTube, Internshala.")
    url: str = Field(description="Mock or real link to the course.")

class RoadmapStep(BaseModel):
    topic: str = Field(description="Subject or skill to learn.")
    description: str = Field(description="What needs to be achieved in this step.")
    resources: List[ResourceLink] = Field(description="Suggested courses or websites.")
    goal_milestone: str = Field(description="Tangible project or milestone to complete by the end of this step.")

class RoadmapPlan(BaseModel):
    target_role: str = Field(description="The role this learning roadmap targets.")
    phase_30_days: List[RoadmapStep] = Field(description="Action plan for the first 30 days.")
    phase_60_days: List[RoadmapStep] = Field(description="Action plan for days 31-60.")
    phase_90_days: List[RoadmapStep] = Field(description="Action plan for days 61-90.")

class ScoreBreakdown(BaseModel):
    experience_score: int = Field(description="Score (0-100) for previous work experience value.")
    skill_relevance_score: int = Field(description="Score (0-100) for existing transferable skills.")
    market_demand_score: int = Field(description="Score (0-100) for market opportunities in target roles.")
    time_availability_score: int = Field(description="Score (0-100) for daily study availability.")
    gap_mitigation_score: int = Field(description="Score (0-100) based on gap duration (mitigated by upskilling/experience).")

class EmployabilityScoring(BaseModel):
    overall_score: int = Field(description="Final weighted employability score (0-100).")
    factor_breakdown: ScoreBreakdown = Field(description="Breakdown of the 5 key factors.")
    explanations: Dict[str, str] = Field(description="Detailed text explanations for each of the 5 scoring categories.")
    overall_feedback: str = Field(description="Empathetic, encouraging evaluation of the candidate's strengths and how to bridge gaps.")

# ==========================================
# 2. LangGraph State Definition
# ==========================================

class AgentLogEntry(TypedDict):
    agent_name: str
    action: str
    output_preview: str
    timestamp: str

class CareerCounselingState(TypedDict):
    # Inputs
    form_inputs: Dict[str, Any]
    resume_text: str
    
    # Intermediate & Final outputs from Agents
    user_profile: Optional[UserProfile]
    career_recommendations: Optional[CareerRecommendations]
    skill_gap_report: Optional[SkillGapReport]
    roadmap_plan: Optional[RoadmapPlan]
    employability_scoring: Optional[EmployabilityScoring]
    
    # Combined outputs and logs
    synthesized_response: Optional[str]
    agent_logs: List[AgentLogEntry]
    
    # Routing controls
    next_node: str
