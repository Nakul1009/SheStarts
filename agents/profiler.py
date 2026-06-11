from datetime import datetime
from langchain_core.prompts import ChatPromptTemplate
from agents.state import UserProfile, CareerCounselingState, AgentLogEntry
from agents.llm_helper import get_structured_output

def profiler_agent(state: CareerCounselingState) -> CareerCounselingState:
    """
    Profiler Agent: Extracts and consolidates form inputs and resume text into a structured UserProfile.
    """
    print("--- PROFILER AGENT STARTING ---")
    
    # Retrieve input data
    form_inputs = state.get("form_inputs", {})
    resume_text = state.get("resume_text", "")
    
    # Create prompt template
    system_prompt = (
        "You are an empathetic, expert Profiler Agent for SheStarts Career Guide. Your goal is to construct "
        "a highly detailed, professional, and accurate candidate profile for a woman returning to the workforce. "
        "Combine the raw form answers with the parsed resume text (if any) to create a clean profile. "
        "Do not leave details out. Ensure any prior experience is parsed into structured work history. "
        "Format instructions:\n{format_instructions}"
    )
    
    user_prompt = (
        "Here are the form inputs provided by the candidate:\n"
        "{form_inputs}\n\n"
        "Here is the parsed resume text (which may contain older job histories):\n"
        "{resume_text}\n\n"
        "Synthesize this into a structured UserProfile. Make sure to aggregate total experience years "
        "and list all current skills accurately."
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("user", user_prompt)
    ])
    
    # We pass 'format_instructions' in prompt_vars since it is required for fallback JSON parsing
    prompt_vars = {
        "form_inputs": str(form_inputs),
        "resume_text": resume_text or "No resume uploaded.",
        "format_instructions": ""  # Filled by helper if needed
    }
    
    # Invoke structured LLM
    try:
        user_profile = get_structured_output(
            state=state,
            pydantic_model=UserProfile,
            prompt_template=prompt,
            prompt_vars=prompt_vars
        )
    except Exception as e:
        # Emergency fallback logic in case LLM fails completely
        print(f"Profiler agent failed: {e}")
        # Create a basic profile from inputs
        
    
    # Update logs
    log_entry: AgentLogEntry = {
        "agent_name": "Profiler Agent",
        "action": "Parsed form and resume text into a structured profile.",
        "output_preview": f"Name: {user_profile.name}, Gap: {user_profile.gap_duration_years} years, Total Exp: {user_profile.total_experience_years} years, Skills: {', '.join(user_profile.current_skills[:5])}...",
        "timestamp": datetime.now().isoformat()
    }
    
    # Update state
    new_state = state.copy()
    new_state["user_profile"] = user_profile
    if "agent_logs" not in new_state or not new_state["agent_logs"]:
        new_state["agent_logs"] = []
    new_state["agent_logs"].append(log_entry)
    
    print("--- PROFILER AGENT COMPLETE ---")
    return new_state
