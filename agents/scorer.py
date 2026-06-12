from datetime import datetime
from langchain_core.prompts import ChatPromptTemplate
from agents.state import EmployabilityScoring, ScoreBreakdown, CareerCounselingState, AgentLogEntry
from agents.llm_helper import get_structured_output

def calculate_base_scores(state: CareerCounselingState) -> ScoreBreakdown:
    """
    Deterministically computes base score values from user profile and skill gap details
    to ensure math is consistent, transparent, and accurate.
    """
    user_profile = state.get("user_profile")
    skill_gap = state.get("skill_gap_report")
    career_recs = state.get("career_recommendations")
    
    # 1. Experience Score (Weight 25%): 15 pts per year of experience, base of 30, capped at 100.
    total_exp = user_profile.total_experience_years
    experience_score = min(100, int(total_exp * 12 + 30))
    
    # 2. Skill Relevance Score (Weight 25%): Ratio of matching skills vs total skills
    num_matching = len(skill_gap.matching_skills)
    num_missing = len(skill_gap.missing_skills)
    total_skills = num_matching + num_missing
    if total_skills > 0:
        skill_relevance_score = int((num_matching / total_skills) * 60 + 40)
    else:
        skill_relevance_score = 50
    skill_relevance_score = min(100, skill_relevance_score)
        
    # 3. Market Demand Score (Weight 20%): Derived from target role demand
    demand_str = "High"
    if career_recs and career_recs.recommended_paths:
        demand_str = career_recs.recommended_paths[0].demand_index_2026
        
    if demand_str == "High":
        market_demand_score = 95
    elif demand_str == "Medium":
        market_demand_score = 75
    else:
        market_demand_score = 50
        
    # 4. Time Availability Score (Weight 15%): Study hours commitment
    hours = user_profile.time_commitment_hours_per_day
    if hours >= 4:
        time_availability_score = 95
    elif hours >= 2:
        time_availability_score = 75
    else:
        time_availability_score = 50
        
    # 5. Gap Mitigation Score (Weight 15%): Gap duration decay with upskilling buffer
    gap_years = user_profile.gap_duration_years
    decay = gap_years * 8
    # If notes indicate upskilling/projects or she has positive notes, reduce decay
    mitigation_bonus = 0
    notes_lower = (user_profile.additional_notes or "").lower()
    if "course" in notes_lower or "study" in notes_lower or "learned" in notes_lower or "project" in notes_lower:
        mitigation_bonus = 15
        
    gap_mitigation_score = max(30, min(100, int(100 - decay + mitigation_bonus)))
    
    return ScoreBreakdown(
        experience_score=experience_score,
        skill_relevance_score=skill_relevance_score,
        market_demand_score=market_demand_score,
        time_availability_score=time_availability_score,
        gap_mitigation_score=gap_mitigation_score
    )

def scorer_agent(state: CareerCounselingState) -> CareerCounselingState:
    """
    Employability Scorer Agent: Calculates a weighted employability index and writes explanations.
    """
    print("--- SCORER AGENT STARTING ---")
    
    user_profile = state.get("user_profile")
    skill_gap = state.get("skill_gap_report")
    
    if not user_profile or not skill_gap:
        raise ValueError("User Profile or Skill Gap details are missing in Scorer Agent!")
    
    # Calculate programmatic base scores
    breakdown = calculate_base_scores(state)
    
    # Calculate overall weighted score
    # Weights: Exp (25%), Skills (25%), Demand (20%), Time (15%), Gap (15%)
    overall = int(
        (breakdown.experience_score * 0.25) +
        (breakdown.skill_relevance_score * 0.25) +
        (breakdown.market_demand_score * 0.20) +
        (breakdown.time_availability_score * 0.15) +
        (breakdown.gap_mitigation_score * 0.15)
    )
    
    system_prompt = (
        "You are an empathetic, insightful Employability Scorer Agent for SheStarts. Your goal is to write "
        "constructive, encouraging explanations for the candidate's employability factors and give "
        "overall positive feedback. Do not change the scores provided. Explain how they can leverage their strengths "
        "and bridge any gaps. Keep the tone warm, empowering, and focused on growth.\n\n"
        "Format instructions:\n{format_instructions}"
    )
    
    user_prompt = (
        "Candidate Profile:\n"
        "- Name: {name}\n"
        "- Education: {education}\n"
        "- Career Gap: {gap_duration} years (Reason: {gap_reason})\n"
        "- Daily Upskilling Commitment: {study_hours} hours/day\n"
        "- Target Role: {target_role}\n\n"
        "Pre-Calculated Scores (DO NOT ALTER THE NUMBERS):\n"
        "- Experience Score: {exp_score}/100\n"
        "- Skill Relevance Score: {skill_score}/100\n"
        "- Market Demand Score: {demand_score}/100\n"
        "- Time Availability Score: {time_score}/100\n"
        "- Gap Mitigation Score: {gap_score}/100\n"
        "- Overall Weighted Score: {overall_score}/100\n\n"
        "Create a response containing:\n"
        "1. Detailed text explanations for each of the five factors, highlighting their positive aspects.\n"
        "2. An overall feedback statement that reinforces self-worth and charts an active upskilling path."
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("user", user_prompt)
    ])
    
    prompt_vars = {
        "name": user_profile.name,
        "education": user_profile.education,
        "gap_duration": str(user_profile.gap_duration_years),
        "gap_reason": user_profile.gap_reason,
        "study_hours": str(user_profile.time_commitment_hours_per_day),
        "target_role": skill_gap.target_role,
        "exp_score": str(breakdown.experience_score),
        "skill_score": str(breakdown.skill_relevance_score),
        "demand_score": str(breakdown.market_demand_score),
        "time_score": str(breakdown.time_availability_score),
        "gap_score": str(breakdown.gap_mitigation_score),
        "overall_score": str(overall),
        "format_instructions": ""  # Filled by helper if needed
    }
    
    try:
        scoring_output = get_structured_output(
            state=state,
            pydantic_model=EmployabilityScoring,
            prompt_template=prompt,
            prompt_vars=prompt_vars
        )
        # Enforce the mathematical overall score just in case LLM outputs something slightly different
        scoring_output.overall_score = overall
        scoring_output.factor_breakdown = breakdown
    except Exception as e:
        print(f"Scorer Agent LLM call failed: {e}. Falling back to default explanations.")
        # Fallback explanation
        scoring_output = EmployabilityScoring(
            overall_score=overall,
            factor_breakdown=breakdown,
            explanations={
                "experience_score": "Your previous work experience provides a strong foundation of core transferable skills.",
                "skill_relevance_score": "You possess several matching skills. Learning a few domain-specific tools will quickly fill the gaps.",
                "market_demand_score": "The market demand for this target role is high, offering numerous returnship opportunities.",
                "time_availability_score": "Your daily study commitment is sufficient to complete your upskilling within 3 months.",
                "gap_mitigation_score": "Though your career break is a factor, your dedication to upskilling effectively mitigates the gap."
            },
            overall_feedback="You have a robust foundation! With structured upskilling, your career restart is highly achievable."
        )
        
    log_entry: AgentLogEntry = {
        "agent_name": "Employability Scorer",
        "action": "Calculated weighted employability scoring and generated factor-based explanations.",
        "output_preview": f"Overall Score: {scoring_output.overall_score}/100 | Key Strength: {scoring_output.overall_feedback[:60]}...",
        "timestamp": datetime.now().isoformat()
    }
    
    new_state = state.copy()
    new_state["employability_scoring"] = scoring_output
    new_state["agent_logs"].append(log_entry)
    
    print("--- SCORER AGENT COMPLETE ---")
    return new_state
