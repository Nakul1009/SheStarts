from datetime import datetime
from langchain_core.prompts import ChatPromptTemplate
from agents.state import SkillGapReport, CareerCounselingState, AgentLogEntry
from agents.llm_helper import get_structured_output
from agents.recommender import retrieve_counseling_context

def skill_gap_agent(state: CareerCounselingState) -> CareerCounselingState:
    """
    Skill Gap Agent: Compares user's current skills against target role requirements.
    Grounded in RAG data about in-demand skills and transition pathways.
    """
    print("--- SKILL GAP AGENT STARTING ---")
    
    user_profile = state.get("user_profile")
    career_recs = state.get("career_recommendations")
    
    if not user_profile or not career_recs or not career_recs.recommended_paths:
        raise ValueError("User Profile or Career Recommendations are missing in Skill Gap Agent!")
    
    # Analyze the top recommended career path
    target_role = career_recs.recommended_paths[0].title
    
    # Retrieve RAG context regarding this role
    rag_context = retrieve_counseling_context(f"Skills required for {target_role}", state)
    
    system_prompt = (
        "You are an expert Skill Gap Agent for SheStarts. Your task is to compare the candidate's current skills "
        "with the skills required for the target role: '{target_role}'.\n"
        "Identify:\n"
        "1. Matching skills (transferable skills they already have).\n"
        "2. Missing skills (technical or soft skills they need to learn, with importance level and a short explanation).\n\n"
        "Ground your skill requirements in the following market data:\n"
        "{rag_context}\n\n"
        "Format instructions:\n{format_instructions}"
    )
    
    user_prompt = (
        "Candidate Details:\n"
        "- Previous Experience Summary: {experience_summary}\n"
        "- Current Skills: {current_skills}\n"
        "- Target Role: {target_role}\n\n"
        "Provide a comprehensive, empathetic Skill Gap Report. Remind them of the value of their transferable skills "
        "and list exactly what they need to bridge next."
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("user", user_prompt)
    ])
    
    experience_summary = ", ".join([exp.role for exp in user_profile.previous_experience]) or "Career starter / pivoting"
    
    prompt_vars = {
        "target_role": target_role,
        "rag_context": rag_context,
        "experience_summary": experience_summary,
        "current_skills": ", ".join(user_profile.current_skills),
        "format_instructions": ""  # Filled by helper if needed
    }
    
    try:
        skill_gap_report = get_structured_output(
            state=state,
            pydantic_model=SkillGapReport,
            prompt_template=prompt,
            prompt_vars=prompt_vars
        )
    except Exception as e:
        print(f"Skill Gap Agent failed: {e}. Falling back to default report.")
        from agents.state import MissingSkill
        skill_gap_report = SkillGapReport(
            target_role=target_role,
            matching_skills=user_profile.current_skills or ["Communication", "Problem Solving"],
            missing_skills=[
                MissingSkill(
                    skill_name="Domain Specific Tools",
                    importance_level="Critical",
                    description=f"Core technical skills and platforms required to succeed as a {target_role}."
                ),
                MissingSkill(
                    skill_name="Practical Projects",
                    importance_level="Important",
                    description="Hands-on portfolio projects showcasing real-world experience."
                ),
                MissingSkill(
                    skill_name="Collaborative Tools",
                    importance_level="Nice-to-have",
                    description="Familiarity with team productivity tools like Git, Jira, or Slack."
                )
            ]
        )
        
        
    log_entry: AgentLogEntry = {
        "agent_name": "Skill Gap Agent",
        "action": f"Analyzed skill gaps for target role: {target_role}.",
        "output_preview": f"Matching: {', '.join(skill_gap_report.matching_skills[:3])} | Missing: {', '.join([ms.skill_name for ms in skill_gap_report.missing_skills[:3]])}",
        "timestamp": datetime.now().isoformat()
    }
    
    new_state = state.copy()
    new_state["skill_gap_report"] = skill_gap_report
    new_state["agent_logs"].append(log_entry)
    
    print("--- SKILL GAP AGENT COMPLETE ---")
    return new_state
