import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from utils.accounts import update_profile
from utils.scorer   import save_survey_to_csv

# ── Auth guard ────────────────────────────────────────────────────────────────
if not st.session_state.get("logged_in"):
    st.warning("⚠️ Please login first.")
    if st.button("Go to Login →", type="primary"):
        st.switch_page("pages/00_home.py")
    st.stop()

# ── Step counter ──────────────────────────────────────────────────────────────
if "survey_step" not in st.session_state:
    st.session_state.survey_step = 1

prof = st.session_state.user_profile
TOTAL = 3

st.title("📋 User Profile Survey")
st.markdown(f"Hi **{prof.get('name', 'there')}** — tell us a bit about yourself so we can personalise your training.")
st.divider()

step = st.session_state.survey_step
st.progress(step / TOTAL, text=f"Step {step} of {TOTAL}")
st.markdown("")

# ─────────────────────────────────────────────────────────────────────────────
# STEP 1 — Role
# ─────────────────────────────────────────────────────────────────────────────
if step == 1:
    st.markdown("### 💼 What is your primary role?")
    st.caption("Scams are tailored to your profession — this shapes the scenarios you will face.")

    ROLES = ["Content Creator", "Teacher", "Doctor", "Business Owner", "Student", "Senior Citizen"]
    # Pre-fill from existing profile if available
    default_role = prof.get("role", ROLES[0])
    role_idx = ROLES.index(default_role) if default_role in ROLES else 0
    role = st.selectbox("Select your role", ROLES, index=role_idx, key="s_role")

    role_descriptions = {
        "Content Creator": "🎥 Targets: fake sponsorships, demonetization threats, verification badge scams",
        "Teacher":         "📚 Targets: fake school portal logins, grant notifications, payroll phishing",
        "Doctor":          "🏥 Targets: patient data requests, medical supply scams, licensing alerts",
        "Business Owner":  "💼 Targets: invoice fraud, fake supplier deals, tax authority impersonation",
        "Student":         "🎓 Targets: scholarship scams, fake university portals, job offer fraud",
        "Senior Citizen":  "👴 Targets: bank freeze scams, lottery wins, tech-support fraud",
    }
    st.info(role_descriptions.get(role, ""))

    st.markdown("")
    if st.button("Next →", type="primary"):
        st.session_state.user_profile["role"] = role
        st.session_state.survey_step = 2
        st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
# STEP 2 — Platform
# ─────────────────────────────────────────────────────────────────────────────
elif step == 2:
    st.markdown("### 📱 What is your primary digital platform?")
    st.caption("Your main platform determines which attack types appear most in your lab.")

    PLATFORMS = ["Email", "TikTok", "Instagram", "WhatsApp", "SMS", "Facebook"]
    default_plat = prof.get("platform", PLATFORMS[0])
    plat_idx = PLATFORMS.index(default_plat) if default_plat in PLATFORMS else 0
    platform = st.selectbox("Primary platform", PLATFORMS, index=plat_idx, key="s_platform")

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
            st.session_state.survey_step = 1
            st.rerun()
    with c2:
        if st.button("Next →", type="primary"):
            st.session_state.user_profile["platform"] = platform
            st.session_state.survey_step = 3
            st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
# STEP 3 — Tech comfort
# ─────────────────────────────────────────────────────────────────────────────
elif step == 3:
    st.markdown("### 💻 What is your tech comfort level?")
    st.caption("This adjusts the complexity of scenarios and the depth of explanations.")

    LEVELS = ["Beginner", "Intermediate", "Advanced"]
    default_tech = prof.get("tech_level", "Intermediate")
    tech_idx = LEVELS.index(default_tech) if default_tech in LEVELS else 1
    tech = st.radio("Tech Comfort Level", LEVELS, index=tech_idx, key="s_tech")

    tech_desc = {
        "Beginner":     "New to tech. Use basic apps for calls, messages, and photos.",
        "Intermediate": "Comfortable with most apps. Occasionally use advanced features.",
        "Advanced":     "Power user. Familiar with settings, privacy tools, and security.",
    }
    st.markdown(f"**{tech}:** {tech_desc[tech]}")

    st.markdown("")
    c1, c2 = st.columns([1, 3])
    with c1:
        if st.button("← Back"):
            st.session_state.survey_step = 2
            st.rerun()
    with c2:
        if st.button("✅ Save & Continue", type="primary"):
            st.session_state.user_profile["tech_level"] = tech

            # Persist to accounts.json and legacy CSV
            try:
                update_profile(
                    st.session_state.email,
                    st.session_state.user_profile["role"],
                    st.session_state.user_profile["platform"],
                    tech,
                )
            except Exception:
                pass
            try:
                save_survey_to_csv(st.session_state.user_profile)
            except Exception:
                pass

            st.session_state.survey_completed = True
            st.session_state.survey_step = 1   # reset for next visit
            st.success("Profile saved! Taking you to Flashcards…")
            st.switch_page("pages/02_flashcards.py")

# ── Sidebar: answers so far ───────────────────────────────────────────────────
with st.sidebar:
    st.markdown("---")
    st.markdown("**Profile so far**")
    _p = st.session_state.user_profile
    st.markdown(f"👤 **{_p.get('name', '—')}**")
    st.caption(f"📧 {st.session_state.email}")
    if _p.get("role"):
        st.markdown(f"💼 {_p['role']}")
    if _p.get("platform"):
        st.markdown(f"📱 {_p['platform']}")
