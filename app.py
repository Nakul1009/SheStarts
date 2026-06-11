import streamlit as st

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

            st.success("Profile submitted successfully.")

            st.write("### Summary")

            st.write(f"**Name:** {name}")
            st.write(f"**Education:** {education}")
            st.write(f"**Experience:** {experience} years")
            st.write(f"**Career Gap:** {career_gap} years")
            st.write(f"**Skills:** {skills}")
            st.write(f"**Learning Commitment:** {commitment} hrs/week")
            st.write(f"**Work Style:** {', '.join(work_style)}")
            st.write(f"**Goal:** {goal}")

    st.markdown("</div>", unsafe_allow_html=True)

    st.write("")

    if st.button("← Back"):
        st.session_state.page = "home"
        st.rerun()