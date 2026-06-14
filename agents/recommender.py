import os
from datetime import datetime
from langchain_core.prompts import ChatPromptTemplate
from agents.state import CareerRecommendations, CareerCounselingState, AgentLogEntry
from agents.llm_helper import get_structured_output
from langchain_nvidia_ai_endpoints import NVIDIAEmbeddings
from langchain_chroma import Chroma


def retrieve_counseling_context(query: str, state: CareerCounselingState) -> str:
    """
    Attempts to retrieve context from Chroma DB. If Chroma fails,
    performs a keyword search over RELAUNCH_DATA.
    """
    context = ""
    api_key = state.get("nvidia_api_key") or os.getenv("NVIDIA_API_KEY")
    try:
        persist_dir = "./rag/chroma_db"
        embeddings = NVIDIAEmbeddings(
                model="nvidia/nv-embedqa-e5-v5",
                nvidia_api_key=api_key
            )
        
        # Check if the DB already exists or if we should populate it
        db_exists = os.path.exists(persist_dir) and len(os.listdir(persist_dir)) > 0
        
        db = Chroma(
            persist_directory=persist_dir,
            embedding_function=embeddings
        )
        results = db.similarity_search(query, k=3)
        context = "\n\n".join([doc.page_content for doc in results])
        print(f"Retrieved {len(results)} relevant records from Chroma Vector DB.")
    except Exception as e:
        print(f"Chroma DB retrieval failed: {e}. Using direct data fallback.")
        try:
            from rag.data import DATA
            # Simple keyword matching fallback
            keywords = query.lower().split()
            matched_docs = []
            for item in DATA:
                match_count = sum(1 for kw in keywords if kw in item["title"].lower() or kw in item["content"].lower())
                if match_count > 0:
                    matched_docs.append((match_count, item))
            # Sort by match count descending
            matched_docs.sort(key=lambda x: x[0], reverse=True)
            context = "\n\n".join([f"Title: {item['title']}\nContent: {item['content']}" for _, item in matched_docs[:3]])
        except Exception as fallback_err:
            print(f"Fallback direct data search also failed: {fallback_err}")
               
    return context

def recommender_agent(state: CareerCounselingState) -> CareerCounselingState:
    """
    Recommender Agent: Recommends 3-5 career paths grounded in RAG returnship data.
    """
    print("--- RECOMMENDER AGENT STARTING ---")
    
    user_profile = state.get("user_profile")
    if not user_profile:
        raise ValueError("User Profile is empty in Recommender Agent!")
    
    # Query vector DB using previous experience and desired roles/notes
    query_str = f"{user_profile.education} {', '.join(user_profile.current_skills)} {user_profile.additional_notes}"
    rag_context = retrieve_counseling_context(query_str, state)
    
    system_prompt = (
        "You are an strategic Recommender Agent for SheStarts. Your goal is to suggest "
        "3 to 5 realistic, high-potential career paths for a woman restarting her career after a break. "
        "Prioritize roles that are remote-friendly, have returnship programs active, or have a lower "
        "barrier to entry for career changers.\n\n"
        "Ground your recommendations in the following retrieved market data:\n"
        "{rag_context}\n\n"
        "Format instructions:\n{format_instructions}"
    )
    
    user_prompt = (
        "Here is the candidate's profile:\n"
        "- Education: {education}\n"
        "- Previous Experience: {experience}\n"
        "- Total Experience: {total_exp} years\n"
        "- Career Break: {gap_duration} years (Reason: {gap_reason})\n"
        "- Skills: {skills}\n"
        "- Remote Preference: {remote_pref}\n"
        "- Daily Commitment: {study_hours} hours/day available for study\n"
        "- Additional Goals/Notes: {notes}\n\n"
        "Recommend 3 to 5 specific career paths suitable for her. Explain your reasoning in an empathetic, "
        "empowering tone, showing how her prior experience or current skills translate to these target roles."
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("user", user_prompt)
    ])
    
    experience_str = "\n".join([
        f"- {exp.role} at {exp.company} ({exp.years} yrs): {exp.description}"
        for exp in user_profile.previous_experience
    ]) or "No prior experience listed."
    
    prompt_vars = {
        "rag_context": rag_context,
        "education": user_profile.education,
        "experience": experience_str,
        "total_exp": str(user_profile.total_experience_years),
        "gap_duration": str(user_profile.gap_duration_years),
        "gap_reason": user_profile.gap_reason,
        "skills": ", ".join(user_profile.current_skills),
        "remote_pref": user_profile.remote_preference,
        "study_hours": str(user_profile.time_commitment_hours_per_day),
        "notes": user_profile.additional_notes or "None",
        "format_instructions": ""  # Filled by helper if needed
    }
    
    try:
        recommendations = get_structured_output(
            state=state,
            pydantic_model=CareerRecommendations,
            prompt_template=prompt,
            prompt_vars=prompt_vars
        )
    except Exception as e:
        print(f"Recommender agent failed: {e}. Falling back to default recommendations.")
        from agents.state import CareerPath
        recommendations = CareerRecommendations(
            recommended_paths=[
                CareerPath(
                    title="Data Analyst",
                    suitability_reasoning="A great, analytical role with high remote flexibility, leveraging your previous transferable skills.",
                    remote_suitability_score=8,
                    entry_barrier="Medium",
                    target_companies=["Capgemini", "Amazon", "Tata SCIP"],
                    demand_index_2026="High"
                ),
                CareerPath(
                    title="AI Prompt Engineer",
                    suitability_reasoning="A fast-growing, low-code entry point that matches technical curiosity and adaptability.",
                    remote_suitability_score=9,
                    entry_barrier="Low",
                    target_companies=["Goldman Sachs", "IBM"],
                    demand_index_2026="High"
                ),
                CareerPath(
                    title="Digital Marketing Specialist",
                    suitability_reasoning="A creative, data-driven path that is highly remote-friendly and suitable for returnees.",
                    remote_suitability_score=9,
                    entry_barrier="Low",
                    target_companies=["Amazon", "Tata SCIP"],
                    demand_index_2026="Medium"
                )
            ]
        )
       
    log_entry: AgentLogEntry = {
        "agent_name": "Recommender Agent",
        "action": "Generated 3-5 returnee-friendly career path recommendations.",
        "output_preview": f"Paths Suggested: {', '.join([path.title for path in recommendations.recommended_paths])}",
        "timestamp": datetime.now().isoformat()
    }
    
    new_state = state.copy()
    new_state["career_recommendations"] = recommendations
    new_state["agent_logs"].append(log_entry)
    
    print("--- RECOMMENDER AGENT COMPLETE ---")
    return new_state
