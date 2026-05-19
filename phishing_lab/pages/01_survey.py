import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import uuid
from utils.scorer import save_survey_to_csv

# ── Page guard: init step counter ────────────────────────────────────────────
if "survey_step" not in st.session_state:
    st.session_state.survey_step = 1

st.title("📋 User Profile Survey")
st.markdown("Help us personalise your phishing training. This takes about **1 minute**.")
st.divider()

step = st.session_state.survey_step
TOTAL = 4

# ── Step progress bar ─────────────────────────────────────────────────────────
st.progress(step / TOTAL, text=f"Step {step} of {TOTAL}")
st.markdown("")

# ─────────────────────────────────────────────────────────────────────────────
# STEP 1 — Name
# ─────────────────────────────────────────────────────────────────────────────
if step == 1:
    st.markdown("### 👤 What is your name?")
    st.caption("Your name will appear on your completion certificate.")
    name = st.text_input("Full Name", placeholder="e.g. Jane Mwangi", key="s_name")

    st.markdown("")
    if st.button("Next →", type="primary", disabled=not name.strip(), width='content'):
        if "user_profile" not in st.session_state:
            st.session_state.user_profile = {}
        st.session_state.user_profile["name"] = name.strip()
        st.session_state.user_profile["user_id"] = str(uuid.uuid4())[:8]
        st.session_state.survey_step = 2
        st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
# STEP 2 — Role
# ─────────────────────────────────────────────────────────────────────────────
elif step == 2:
    st.markdown("### 💼 What is your primary role?")
    st.caption("We use this to generate phishing scenarios that match real attacks targeting your profession.")

    ROLES = ["Content Creator", "Teacher", "Doctor", "Business Owner", "Student", "Senior Citizen"]
    role = st.selectbox("Select your role", ROLES, key="s_role")

    role_descriptions = {
        "Content Creator": "🎥 Targets: fake sponsorships, demonetization threats, account verification scams",
        "Teacher": "📚 Targets: fake school portal logins, grant notifications, payroll phishing",
        "Doctor": "🏥 Targets: patient data requests, medical supply scams, fake licensing alerts",
        "Business Owner": "💼 Targets: invoice fraud, fake supplier deals, tax authority impersonation",
        "Student": "🎓 Targets: scholarship scams, fake university portals, job offer fraud",
        "Senior Citizen": "👴 Targets: bank account freeze scams, lottery wins, tech support fraud",
    }
    st.info(role_descriptions.get(role, ""))

    st.markdown("")
    c1, c2 = st.columns([1, 3])
    with c1:
        if st.button("← Back"):
            st.session_state.survey_step = 1
            st.rerun()
    with c2:
        if st.button("Next →", type="primary"):
            st.session_state.user_profile["role"] = role
            st.session_state.survey_step = 3
            st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
# STEP 3 — Platform
# ─────────────────────────────────────────────────────────────────────────────
elif step == 3:
    st.markdown("### 📱 What is your primary digital platform?")
    st.caption("Scams are highly platform-specific — this shapes the simulated attack types you will face.")

    PLATFORMS = ["Email", "TikTok", "Instagram", "WhatsApp", "SMS", "Facebook"]
    platform = st.selectbox("Primary platform", PLATFORMS, key="s_platform")

    platform_info = {
        "Email":     "📧 Most common phishing vector — fake receipts, account warnings, job offers",
        "TikTok":    "🎵 Fake brand deals, copyright strikes, verification badge scams",
        "Instagram": "📸 Account impersonation, fake verification, collaboration fraud",
        "WhatsApp":  "💬 M-PESA scams, family emergency fraud, fake customer service",
        "SMS":       "📲 Bank alerts, KRA refunds, parcel delivery scams",
        "Facebook":  "👍 Marketplace scams, fake prize giveaways, page verification fraud",
    }
    st.info(platform_info.get(platform, ""))

    st.markdown("")
    c1, c2 = st.columns([1, 3])
    with c1:
        if st.button("← Back"):
            st.session_state.survey_step = 2
            st.rerun()
    with c2:
        if st.button("Next →", type="primary"):
            st.session_state.user_profile["platform"] = platform
            st.session_state.survey_step = 4
            st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
# STEP 4 — Tech comfort
# ─────────────────────────────────────────────────────────────────────────────
elif step == 4:
    st.markdown("### 💻 What is your tech comfort level?")
    st.caption("This determines the difficulty and detail of explanations in your training.")

    tech = st.radio(
        "Tech Comfort Level",
        ["Beginner", "Intermediate", "Advanced"],
        key="s_tech",
    )

    tech_desc = {
        "Beginner":     "New to technology. Use basic functions like calls, messages, and simple apps.",
        "Intermediate": "Comfortable with most apps. Occasionally explore settings and advanced features.",
        "Advanced":     "Power user. Familiar with settings, privacy tools, and security best practices.",
    }
    st.markdown(f"**{tech}:** {tech_desc[tech]}")

    st.markdown("")
    c1, c2 = st.columns([1, 3])
    with c1:
        if st.button("← Back"):
            st.session_state.survey_step = 3
            st.rerun()
    with c2:
        if st.button("✅ Complete Survey", type="primary"):
            st.session_state.user_profile["tech_level"] = tech
            # Persist to CSV
            try:
                save_survey_to_csv(st.session_state.user_profile)
            except Exception as e:
                pass  # Non-fatal — don't block the user
            st.session_state.survey_completed = True
            st.session_state.survey_step = 1  # reset for future visits
            st.success("Profile saved! Taking you to the Flashcards…")
            st.switch_page("pages/02_flashcards.py")

# ─────────────────────────────────────────────────────────────────────────────
# Sidebar summary of answers so far
# ─────────────────────────────────────────────────────────────────────────────
if step > 1:
    prof = st.session_state.user_profile
    with st.sidebar:
        st.markdown("---")
        st.markdown("**Your answers so far**")
        if prof.get("name"):
            st.markdown(f"👤 {prof['name']}")
        if prof.get("role"):
            st.markdown(f"💼 {prof['role']}")
        if prof.get("platform"):
            st.markdown(f"📱 {prof['platform']}")
