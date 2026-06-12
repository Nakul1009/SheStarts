from datetime import datetime
from langchain_core.prompts import ChatPromptTemplate
from agents.state import RoadmapPlan, CareerCounselingState, AgentLogEntry
from agents.llm_helper import get_structured_output

def roadmap_agent(state: CareerCounselingState) -> CareerCounselingState:
    """
    Roadmap Agent: Generates a 30/60/90-day study plan targeting the identified skill gaps.
    """
    print("--- ROADMAP AGENT STARTING ---")
    
    user_profile = state.get("user_profile")
    skill_gap = state.get("skill_gap_report")
    
    if not user_profile or not skill_gap:
        raise ValueError("User Profile or Skill Gap Report are missing in Roadmap Agent!")
    
    target_role = skill_gap.target_role
    
    system_prompt = (
        "You are an encouraging, highly organized Roadmap Agent for SheStarts. Your goal is to design a personalized "
        "30/60/90-day upskilling plan for '{target_role}'.\n"
        "Ensure each phase has clear topics, actionable course links (like Coursera, Google Professional Certificates, "
        "YouTube tutorials, and Internshala projects), and a tangible project-based milestone.\n"
        "Tailor the depth of the roadmap to the candidate's available study commitment: {study_hours} hours per day.\n\n"
        "Format instructions:\n{format_instructions}"
    )
    
    user_prompt = (
        "Candidate Information:\n"
        "- Target Role: {target_role}\n"
        "- Available Study Time: {study_hours} hours/day\n"
        "- Core Skill Gaps to Address:\n{missing_skills_list}\n\n"
        "Generate a structured, empathetic 30/60/90-day Roadmap. Give specific recommendations for "
        "certification courses and practical projects they can build to showcase on their portfolio."
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("user", user_prompt)
    ])
    
    missing_skills_list = "\n".join([
        f"- {ms.skill_name} ({ms.importance_level}): {ms.description}"
        for ms in skill_gap.missing_skills
    ]) or "No critical gaps identified."
    
    prompt_vars = {
        "target_role": target_role,
        "study_hours": str(user_profile.time_commitment_hours_per_day),
        "missing_skills_list": missing_skills_list,
        "format_instructions": ""  # Filled by helper if needed
    }
    
    try:
        roadmap_plan = get_structured_output(
            state=state,
            pydantic_model=RoadmapPlan,
            prompt_template=prompt,
            prompt_vars=prompt_vars
        )
    except Exception as e:
        print(f"Roadmap Agent failed: {e}. Falling back to default plan.")
        # Fallback
        
        
    log_entry: AgentLogEntry = {
        "agent_name": "Roadmap Agent",
        "action": f"Designed a 30/60/90-day learning roadmap targeting {target_role}.",
        "output_preview": f"30-day Topic: {roadmap_plan.phase_30_days[0].topic if roadmap_plan.phase_30_days else 'None'} | 90-day Milestone: {roadmap_plan.phase_90_days[0].goal_milestone if roadmap_plan.phase_90_days else 'None'}",
        "timestamp": datetime.now().isoformat()
    }
    
    new_state = state.copy()
    new_state["roadmap_plan"] = roadmap_plan
    new_state["agent_logs"].append(log_entry)
    
    print("--- ROADMAP AGENT COMPLETE ---")
    return new_state
