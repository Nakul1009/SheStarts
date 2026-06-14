import streamlit as st
import os
import sys
from dotenv import load_dotenv
from agents.graph import build_counseling_graph
from agents.resume_parser import extract_resume_text

# Ensure the project root is in python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

load_dotenv()

st.set_page_config(
    page_title="She-Starts",
    page_icon="🌸",
    layout="wide"
)
if "page" not in st.session_state:
    st.session_state.page = "home"
# ---------- CUSTOM CSS ----------
st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Poppins', sans-serif;
}

.main {
    background: linear-gradient(
        135deg,
        #FFF7FB 0%,
        #F8F4FF 50%,
        #FFFFFF 100%
    );
}

.hero {
    padding: 5rem 2rem;
    border-radius: 25px;

    background: rgba(255,255,255,0.8);
    backdrop-filter: blur(10px);

    text-align: center;

    box-shadow:
        0 8px 32px rgba(124,58,237,0.08);
}

.hero-title {
    font-size: 4rem;
    font-weight: 700;
    color: #4C1D95;
    margin-bottom: 0.5rem;
}

.hero-subtitle {
    font-size: 1.3rem;
    color: #6B7280;
    max-width: 850px;
    margin: auto;
    line-height: 1.8;
}

.highlight {
    color: #EC4899;
}

.badge {
    display: inline-block;
    padding: 8px 18px;
    border-radius: 999px;

    background: #F3E8FF;
    color: #7C3AED;

    font-size: 14px;
    font-weight: 600;

    margin-bottom: 20px;
}

.form-header {
    font-size: 2.2rem;
    font-weight: 700;
    color: #4C1D95;
    margin-bottom: 0.5rem;
    text-align: center;
}

.form-subtitle {
    font-size: 1.1rem;
    color: #6B7280;
    max-width: 750px;
    margin: 0 auto 2rem auto;
    text-align: center;
    line-height: 1.6;
}

.form-card {
    background: white;
    padding: 2.5rem;
    border-radius: 20px;
    box-shadow: 0 10px 25px rgba(124,58,237,0.05);
    border: 1px solid #F3E8FF;
    max-width: 800px;
    margin: 0 auto;
}

</style>
""", unsafe_allow_html=True)

# ---------- HERO SECTION ----------

st.markdown("""
<div class="hero">

<div class="badge">
✨ For Women Who Want A Career Restart
</div>

<div class="hero-title">
🌸She<span class="highlight">Starts</span>
</div>

<div class="hero-subtitle">
For women who want to get back to work after a career break.
</div>

</div>
""", unsafe_allow_html=True)

st.write("")
st.write("")

col1, col2, col3 = st.columns([1,1,1])


if st.button("Start Your Journey",  use_container_width=True):
    st.session_state.page = "form"
    st.rerun()

# --------------------------------------------------
# FORM PAGE
# --------------------------------------------------

elif st.session_state.page == "form":

    st.markdown("""
    <div class="form-header">
        Career Restart Profile
    </div>

    <div class="form-subtitle">
        Tell us about your background, experience, and goals.
        We'll use this information to generate a personalized
        career restart roadmap.
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="form-card">', unsafe_allow_html=True)

    with st.form("career_restart_form"):

        resume = st.file_uploader(
            "Resume",
            type=["pdf", "docx"]
        )

        name = st.text_input(
            "Full Name",
            placeholder="Enter your full name"
        )

        education = st.selectbox(
            "Highest Education",
            [
                "Bachelor's Degree",
                "Master's Degree",
                "PhD",
                "Diploma",
                "Higher Secondary",
                "Other"
            ]
        )

        experience = st.slider(
            "Years of Professional Experience",
            min_value=0,
            max_value=30,
            value=3
        )

        career_gap = st.slider(
            "Career Break Duration (Years)",
            min_value=0,
            max_value=20,
            value=1
        )

        skills = st.text_area(
            "Key Skills",
            placeholder="Python, SQL, Marketing, Project Management, HR..."
        )

        commitment = st.slider(
            "Weekly Upskilling Commitment (Hours)",
            min_value=1,
            max_value=40,
            value=10
        )

        work_style = st.multiselect(
            "Preferred Work Style",
            [
                "Remote",
                "Hybrid",
                "Office",
                "Part-Time",
                "Freelance",
                "Flexible Hours"
            ]
        )

        goal = st.text_area(
            "Career Restart Goal",
            placeholder="Describe the role, industry, or career path you want to pursue..."
        )

        submitted = st.form_submit_button(
            "Generate My Career Roadmap"
        )

        if submitted:
            if not name.strip():
                st.error("Please enter your name.")
            else:
                with st.spinner("🚀 Activating SheStarts Multi-Agent Counseling Team..."):
                    # 1. Parse Resume Text
                    resume_text = ""
                    if resume is not None:
                        file_bytes = resume.read()
                        resume_text = extract_resume_text(resume.name, file_bytes)
                    
                    # 2. Build form inputs
                    form_inputs = {
                        "name": name,
                        "education": education,
                        "experience": experience,
                        "career_gap": career_gap,
                        "skills": skills,
                        "commitment": commitment,
                        "work_style": work_style,
                        "goal": goal
                    }
                    
                    # 3. Create counseling graph initial state
                    initial_state = {
                        "form_inputs": form_inputs,
                        "resume_text": resume_text,
                        "user_profile": None,
                        "career_recommendations": None,
                        "skill_gap_report": None,
                        "roadmap_plan": None,
                        "employability_scoring": None,
                        "synthesized_response": None,
                        "agent_logs": [],
                        "next_node": ""
                    }
                    
                    try:
                        # 4. Invoke graph
                        counseling_graph = build_counseling_graph()
                        result = counseling_graph.invoke(initial_state)
                        
                        # 5. Save results to session state and navigate
                        st.session_state.result = result
                        st.session_state.page = "dashboard"
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error running multi-agent counseling system: {e}")

    st.markdown("</div>", unsafe_allow_html=True)

    st.write("")

    if st.button("← Back"):
        st.session_state.page = "home"
        st.rerun()

# --------------------------------------------------
# DASHBOARD PAGE
# --------------------------------------------------
elif st.session_state.page == "dashboard":
    result = st.session_state.get("result", {})
    user_profile = result.get("user_profile")
    career_recs = result.get("career_recommendations")
    skill_gap = result.get("skill_gap_report")
    roadmap = result.get("roadmap_plan")
    scoring = result.get("employability_scoring")
    synthesized_response = result.get("synthesized_response")
    agent_logs = result.get("agent_logs", [])

    # Back button and page title
    col_back, col_title = st.columns([1.5, 8.5])
    with col_back:
        if st.button("← Edit Profile", use_container_width=True):
            st.session_state.page = "form"
            st.rerun()
            
    with col_title:
        st.markdown("<h2 style='margin-top:0; color:#4C1D95;'>🌸 Your SheStarts Career Restart Dashboard</h2>", unsafe_allow_html=True)
        
    st.write("---")
    
    # Render overall score banner if scoring exists
    if scoring:
        score = scoring.overall_score
        feedback = scoring.overall_feedback
        
        # Color based on score range
        if score >= 80:
            score_color = "#10B981"  # green
            score_text = "Strong Readiness"
        elif score >= 60:
            score_color = "#F59E0B"  # yellow/orange
            score_text = "Moderate Readiness"
        else:
            score_color = "#EF4444"  # red
            score_text = "Needs Upskilling"
            
        # Banner HTML
        st.markdown(f"""
        <div style="background-color: #FDF2F8; border-left: 8px solid {score_color}; padding: 1.5rem; border-radius: 12px; margin-bottom: 2rem; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.02);">
            <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 15px;">
                <div style="flex: 1; min-width: 300px;">
                    <h3 style="margin: 0 0 5px 0; color: #4C1D95;">Employability Restart Index</h3>
                    <p style="margin: 0; color: #4B5563; font-size: 0.95rem; line-height: 1.6;">{feedback}</p>
                </div>
                <div style="text-align: center; padding: 10px 20px; background: white; border-radius: 10px; border: 1px solid #F3E8FF; box-shadow: 0 2px 4px rgba(0,0,0,0.02); min-width: 150px;">
                    <span style="font-size: 2.5rem; font-weight: 700; color: {score_color};">{score}</span><span style="font-size: 1.2rem; color: #9CA3AF;">/100</span>
                    <div style="font-size: 0.8rem; font-weight: 600; color: #6B7280; text-transform: uppercase; margin-top: 2px;">{score_text}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Factor breakdown grid
        st.markdown("<h4 style='color: #4C1D95; margin-top: 0; margin-bottom: 1rem;'>📊 Scoring Factors</h4>", unsafe_allow_html=True)
        breakdown = scoring.factor_breakdown
        explanations = scoring.explanations
        
        f_cols = st.columns(5)
        factors = [
            ("💼 Experience", breakdown.experience_score, explanations.get("experience_score", "")),
            ("🎯 Skill Relevance", breakdown.skill_relevance_score, explanations.get("skill_relevance_score", "")),
            ("📈 Market Demand", breakdown.market_demand_score, explanations.get("market_demand_score", "")),
            ("⏱️ Study Time", breakdown.time_availability_score, explanations.get("time_availability_score", "")),
            ("🛡️ Gap Mitigation", breakdown.gap_mitigation_score, explanations.get("gap_mitigation_score", ""))
        ]
        
        for idx, (label, val, expl) in enumerate(factors):
            with f_cols[idx]:
                st.markdown(f"""
                <div style="background-color: white; padding: 1.2rem; border-radius: 10px; border: 1px solid #ECE9F1; height: 100%; box-shadow: 0 2px 4px rgba(0,0,0,0.01); display: flex; flex-direction: column;">
                    <div style="font-size: 0.85rem; font-weight: 600; color: #6B7280; margin-bottom: 6px;">{label}</div>
                    <div style="font-size: 1.8rem; font-weight: 700; color: #4C1D95; margin-bottom: 8px;">{val}<span style="font-size: 0.9rem; font-weight: normal; color: #9CA3AF;">/100</span></div>
                    <div style="font-size: 0.75rem; color: #4B5563; line-height: 1.4; border-top: 1px solid #F3F1F6; padding-top: 8px; flex: 1;">{expl}</div>
                </div>
                """, unsafe_allow_html=True)

    st.write("")
    st.write("")

    # Dashboard Tabs
    tab_report, tab_recs, tab_skills, tab_roadmap, tab_logs = st.tabs([
        "🌸 Counseling Report",
        "📈 Career Recommendations",
        "🎯 Skill Gaps & Focus Area",
        "🗺️ Upskilling Roadmap",
        "🕵️ Agent Logs"
    ])
    
    with tab_report:
        if synthesized_response:
            st.markdown(f"""
            <div style="background-color: white; padding: 2rem; border-radius: 12px; border: 1px solid #E5E7EB; box-shadow: 0 4px 6px rgba(0,0,0,0.02); line-height: 1.8; color: #1F2937;">
                {synthesized_response}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("Synthesized response is missing.")
            
    with tab_recs:
        st.markdown("<h3 style='color: #4C1D95; margin-top:0;'>Recommended Career Paths</h3>", unsafe_allow_html=True)
        st.markdown("<p style='color: #6B7280;'>These returnee-friendly career recommendations are tailored specifically to your background and career restart goals.</p>", unsafe_allow_html=True)
        
        if career_recs and career_recs.recommended_paths:
            for idx, path in enumerate(career_recs.recommended_paths):
                barrier_color = "#10B981" if path.entry_barrier == "Low" else ("#F59E0B" if path.entry_barrier == "Medium" else "#EF4444")
                
                st.markdown(f"""
                <div style="background-color: white; padding: 1.5rem; border-radius: 12px; border: 1px solid #E5E7EB; margin-bottom: 1.5rem; box-shadow: 0 2px 4px rgba(0,0,0,0.01);">
                    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px; flex-wrap: wrap;">
                        <h4 style="margin: 0; color: #4C1D95; font-size: 1.3rem;">{idx+1}. {path.title}</h4>
                        <div style="display: flex; gap: 8px; align-items: center; flex-wrap: wrap; margin-top: 5px;">
                            <span style="background: #F3E8FF; color: #7C3AED; font-size: 0.75rem; font-weight: 600; padding: 4px 10px; border-radius: 99px;">💻 Remote Friendly: {path.remote_suitability_score}/10</span>
                            <span style="background: #ECFDF5; color: {barrier_color}; font-size: 0.75rem; font-weight: 600; padding: 4px 10px; border-radius: 99px; border: 1px solid {barrier_color}20;">Barrier: {path.entry_barrier}</span>
                            <span style="background: #EFF6FF; color: #2563EB; font-size: 0.75rem; font-weight: 600; padding: 4px 10px; border-radius: 99px;">Demand 2026: {path.demand_index_2026}</span>
                        </div>
                    </div>
                    <p style="color: #4B5563; font-size: 0.95rem; line-height: 1.6; margin-bottom: 15px;">{path.suitability_reasoning}</p>
                    <div style="border-top: 1px dashed #E5E7EB; padding-top: 12px;">
                        <span style="font-size: 0.85rem; font-weight: 600; color: #6B7280;">Hiring Companies / Returnships:</span>
                        <div style="display: flex; gap: 8px; flex-wrap: wrap; margin-top: 6px;">
                            {' '.join([f'<span style="background: #F3F4F6; color: #374151; font-size: 0.75rem; font-weight: 500; padding: 3px 8px; border-radius: 4px;">{comp}</span>' for comp in path.target_companies])}
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No recommendations found.")
            
    with tab_skills:
        st.markdown("<h3 style='color: #4C1D95; margin-top:0;'>Skill Gap Analysis</h3>", unsafe_allow_html=True)
        if skill_gap:
            st.markdown(f"<p style='color: #6B7280;'>Analysis targeting your primary career path: <strong>{skill_gap.target_role}</strong>.</p>", unsafe_allow_html=True)
            
            col_match, col_missing = st.columns(2)
            
            with col_match:
                skills_badges = " ".join([f'<span style="background: white; color: #047857; font-size: 0.8rem; font-weight: 600; padding: 6px 12px; border-radius: 99px; border: 1px solid #A7F3D0; box-shadow: 0 1px 2px rgba(0,0,0,0.02); margin-bottom: 8px; display: inline-block;">{skill}</span>' for skill in skill_gap.matching_skills])
                st.markdown(f"""
                <div style="background-color: #ECFDF5; border-radius: 12px; border: 1px solid #A7F3D0; padding: 1.5rem; height: 100%;">
                    <h4 style="margin-top: 0; color: #065F46; font-size: 1.1rem; display: flex; align-items: center; gap: 6px;">✅ Your Transferable & Matching Skills</h4>
                    <p style="color: #065F46; font-size: 0.85rem; opacity: 0.9; margin-bottom: 1.2rem;">These skills are highly relevant to your target role and give you a strong head start.</p>
                    <div style="display: flex; gap: 8px; flex-wrap: wrap;">
                        {skills_badges}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
            with col_missing:
                st.markdown("""
                <div style="background-color: #FFFBEB; border-radius: 12px; border: 1px solid #FDE68A; padding: 1.5rem; height: 100%;">
                    <h4 style="margin-top: 0; color: #92400E; font-size: 1.1rem; display: flex; align-items: center; gap: 6px;">⚠️ Skills to Bridge (Gaps)</h4>
                    <p style="color: #92400E; font-size: 0.85rem; opacity: 0.9; margin-bottom: 1.2rem;">Focus on building these technical or soft skills to qualify for returnships and jobs.</p>
                    <div style="display: flex; flex-direction: column; gap: 10px;">
                """, unsafe_allow_html=True)
                
                for idx, ms in enumerate(skill_gap.missing_skills):
                    imp_bg = "#FEF2F2" if ms.importance_level == "Critical" else ("#FFFBEB" if ms.importance_level == "Important" else "#F9FAFB")
                    imp_text = "#EF4444" if ms.importance_level == "Critical" else ("#D97706" if ms.importance_level == "Important" else "#4B5563")
                    
                    st.markdown(f"""
                    <div style="background: white; border-radius: 8px; border: 1px solid #FDE68A; padding: 10px 14px; box-shadow: 0 1px 2px rgba(0,0,0,0.01);">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                            <span style="font-weight: 600; color: #92400E; font-size: 0.9rem;">{idx+1}. {ms.skill_name}</span>
                            <span style="background: {imp_bg}; color: {imp_text}; font-size: 0.7rem; font-weight: 700; padding: 2px 8px; border-radius: 99px; border: 1px solid {imp_text}30;">{ms.importance_level}</span>
                        </div>
                        <p style="margin: 0; color: #4B5563; font-size: 0.8rem; line-height: 1.4;">{ms.description}</p>
                    </div>
                    """, unsafe_allow_html=True)
                st.markdown("</div></div>", unsafe_allow_html=True)
        else:
            st.info("No skill gaps analysis available.")
            
    with tab_roadmap:
        if roadmap:
            st.markdown(f"<h3 style='color: #4C1D95; margin-top:0;'>Upskilling Roadmap: {roadmap.target_role}</h3>", unsafe_allow_html=True)
            st.markdown("<p style='color: #6B7280;'>This 30/60/90-day interactive path targets your specific skill gaps and outlines courses, platforms, and hands-on milestones.</p>", unsafe_allow_html=True)
            
            phases = [
                ("🌸 Phase 1: First 30 Days (Foundations)", roadmap.phase_30_days),
                ("🚀 Phase 2: 31-60 Days (Build Portfolio)", roadmap.phase_60_days),
                ("💼 Phase 3: 61-90 Days (Job Readiness)", roadmap.phase_90_days)
            ]
            
            for title, steps in phases:
                st.markdown(f"""
                <div style="background-color: #F9FAFB; padding: 12px 18px; border-radius: 8px; border-left: 5px solid #7C3AED; margin-top: 1.5rem; margin-bottom: 1rem;">
                    <strong style="font-size: 1.1rem; color: #4C1D95;">{title}</strong>
                </div>
                """, unsafe_allow_html=True)
                
                if steps:
                    for step_idx, step in enumerate(steps):
                        links_html = ""
                        if step.resources:
                            links_html = '<div style="display: flex; gap: 8px; flex-wrap: wrap; margin-top: 6px;">'
                            for res in step.resources:
                                links_html += f'<a href="{res.url}" target="_blank" style="background: #F3E8FF; color: #7C3AED; font-size: 0.75rem; font-weight: 600; padding: 3px 8px; border-radius: 4px; text-decoration: none; border: 1px solid #7C3AED30;">🔗 {res.name} ({res.platform})</a>'
                            links_html += '</div>'
                        
                        st.markdown(f"""<div style="background: white; border-radius: 12px; border: 1px solid #E5E7EB; padding: 1.2rem; margin-bottom: 1rem; box-shadow: 0 2px 4px rgba(0,0,0,0.02);">
<h5 style="margin-top: 0; color: #4C1D95; font-size: 1.1rem; margin-bottom: 6px; font-weight: 600;">{step.topic}</h5>
<p style="color: #4B5563; font-size: 0.9rem; line-height: 1.5; margin-bottom: 12px;">{step.description}</p>
<div style="background: #FDF2F8; border: 1px solid #FBCFE8; border-radius: 8px; padding: 10px 14px; margin-bottom: 12px;">
<span style="font-size: 0.75rem; font-weight: 700; color: #EC4899; text-transform: uppercase; display: block; margin-bottom: 4px;">🎯 Goal / Project Milestone:</span>
<p style="margin: 0; color: #9D174D; font-size: 0.875rem; font-weight: 500; line-height: 1.4;">{step.goal_milestone}</p>
</div>
<div style="font-size: 0.825rem; color: #6B7280; font-weight: 600; margin-bottom: 6px;">Suggested Learning Resources:</div>
{links_html}
</div>""", unsafe_allow_html=True)
                else:
                    st.write("No steps specified for this phase.")
        else:
            st.info("No roadmap available.")
            
    with tab_logs:
        st.markdown("<h3 style='color: #4C1D95; margin-top:0;'>Agent Collaboration Activity Log</h3>", unsafe_allow_html=True)
        st.markdown("<p style='color: #6B7280;'>SheStarts operates on a multi-agent network orchestrated by a supervisor. Below is the background log of agent activations:</p>", unsafe_allow_html=True)
        
        if agent_logs:
            for log in agent_logs:
                with st.expander(f"🤖 {log.get('agent_name')} - {log.get('action')}"):
                    st.markdown(f"**Timestamp:** `{log.get('timestamp')}`")
                    st.markdown("**Output Preview:**")
                    st.code(log.get('output_preview'))
        else:
            st.write("No agent logs recorded.")