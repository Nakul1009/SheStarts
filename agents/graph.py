from langgraph.graph import StateGraph, END
from agents.state import CareerCounselingState
from agents.profiler import profiler_agent
from agents.recommender import recommender_agent
from agents.skill_gap import skill_gap_agent
from agents.roadmap import roadmap_agent
from agents.scorer import scorer_agent
from agents.synthesizer import synthesizer_agent

def supervisor_router(state: CareerCounselingState) -> str:
    """
    Supervisor router node: Dynamically decides the next node in the pipeline
    based on what data has been generated so far.
    """
    print("--- SUPERVISOR ROUTING DECISION ---")
    
    # 1. Parse Profile
    if not state.get("user_profile"):
        print("Routing to: profiler")
        return "profiler"
        
    # 2. Generate Recommendations
    if not state.get("career_recommendations"):
        print("Routing to: recommender")
        return "recommender"
        
    # 3. Analyze Skill Gaps
    if not state.get("skill_gap_report"):
        print("Routing to: skill_gap")
        return "skill_gap"
        
    # 4. Generate Study Roadmap
    if not state.get("roadmap_plan"):
        print("Routing to: roadmap")
        return "roadmap"
        
    # 5. Calculate Employability Score
    if not state.get("employability_scoring"):
        print("Routing to: scorer")
        return "scorer"
        
    # 6. Synthesize final report
    if not state.get("synthesized_response"):
        print("Routing to: synthesizer")
        return "synthesizer"
        
    # 7. Complete
    print("Orchestration complete. Routing to: END")
    return END

def build_counseling_graph():
    """
    Assembles the StateGraph connecting the supervisor router to all agent nodes.
    """
    # Initialize state graph
    workflow = StateGraph(CareerCounselingState)
    
    # Add nodes
    workflow.add_node("profiler", profiler_agent)
    workflow.add_node("recommender", recommender_agent)
    workflow.add_node("skill_gap", skill_gap_agent)
    workflow.add_node("roadmap", roadmap_agent)
    workflow.add_node("scorer", scorer_agent)
    workflow.add_node("synthesizer", synthesizer_agent)
    
    
    def supervisor_node(state: CareerCounselingState) -> dict:
        return {"next_node": supervisor_router(state)}

    workflow.add_node("supervisor", supervisor_node)
    workflow.set_entry_point("supervisor")
    
    # Define conditional edges from the supervisor node
    workflow.add_conditional_edges(
        "supervisor",
        lambda state: state.get("next_node", "profiler"),
        {
            "profiler": "profiler",
            "recommender": "recommender",
            "skill_gap": "skill_gap",
            "roadmap": "roadmap",
            "scorer": "scorer",
            "synthesizer": "synthesizer",
            END: END
        }
    )
    
    # Every agent node returns control to the supervisor
    workflow.add_edge("profiler", "supervisor")
    workflow.add_edge("recommender", "supervisor")
    workflow.add_edge("skill_gap", "supervisor")
    workflow.add_edge("roadmap", "supervisor")
    workflow.add_edge("scorer", "supervisor")
    workflow.add_edge("synthesizer", "supervisor")
    
    # Compile
    return workflow.compile()
