import streamlit as st
import os

st.set_page_config(
    page_title="Phishing Awareness Lab",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Session state defaults ────────────────────────────────────────────────────
_DEFAULTS = {
    "user_profile": {},
    "lab_score": None,
    "completed_lab": False,
    "dark_mode": True,
    "text_size": "Medium",
    "high_contrast": False,
    "flashcards_learned": set(),
    "lab_scenarios": None,
    "lab_current": 0,
    "lab_state": "init",
    "lab_answers": [],
    "lab_feedback_data": None,
    "survey_completed": False,
    "lab_csv_saved": False,
    "admin_authenticated": False,
    "certificate_downloaded": False,
}
for _k, _v in _DEFAULTS.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v

# ── Inject base CSS ───────────────────────────────────────────────────────────
_css = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "styles.css")
if os.path.exists(_css):
    with open(_css, encoding="utf-8") as _f:
        st.markdown(f"<style>{_f.read()}</style>", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🛡️ Phishing Lab")
    st.divider()
    st.markdown("### ⚙️ Accessibility")

    # Widgets use session_state keys directly for two-way binding
    st.toggle("🌙 Dark Mode", key="dark_mode")
    st.select_slider(
        "📝 Text Size",
        options=["Small", "Medium", "Large"],
        key="text_size",
    )
    st.toggle("⚡ High Contrast", key="high_contrast")

    # Compute and inject dynamic theme CSS
    _fs = {"Small": "14px", "Medium": "16px", "Large": "20px"}[st.session_state.text_size]
    if st.session_state.high_contrast:
        _bg, _fg, _accent, _surface = "#000000", "#FFFF00", "#FFFF00", "#111111"
    elif st.session_state.dark_mode:
        _bg, _fg, _accent, _surface = "#013140", "#FFFFFF", "#CC9F66", "#026281"
    else:
        # Light mode: invert — white bg, dark-teal text, gold accent
        _bg, _fg, _accent, _surface = "#FFFFFF", "#013140", "#026281", "#f0f7fa"

    st.markdown(
        f"""<style>
        html, body, [class*="css"] {{ font-size: {_fs} !important; }}
        .stApp {{ background-color: {_bg} !important; }}
        h1, h2, h3, h4 {{ color: {_accent} !important; }}
        p, span, li {{ color: {_fg}; }}
        [data-testid="stMetric"] {{ background: {_surface} !important; }}
        </style>""",
        unsafe_allow_html=True,
    )

    st.divider()
    # Live progress snapshot
    _prof = st.session_state.user_profile
    if _prof.get("name"):
        st.markdown(f"**👤 {_prof['name']}**")
        st.markdown(f"🎭 {_prof.get('role', '—')}")
        if st.session_state.survey_completed:
            st.success("✅ Survey done", icon=None)
        _n = len(st.session_state.flashcards_learned)
        st.progress(_n / 10, text=f"🃏 {_n}/10 cards")
        if st.session_state.completed_lab and st.session_state.lab_score is not None:
            _s = st.session_state.lab_score
            _clr = "🟢" if _s >= 80 else "🔴"
            st.markdown(f"{_clr} Lab score: **{_s}/100**")

# ── Multi-page navigation ─────────────────────────────────────────────────────
pg = st.navigation([
    st.Page("pages/00_home.py",      title="Home",         icon="🏠"),
    st.Page("pages/01_survey.py",    title="Survey",       icon="📋"),
    st.Page("pages/02_flashcards.py",title="Flashcards",   icon="🃏"),
    st.Page("pages/03_lab.py",       title="Phishing Lab", icon="🔬"),
    st.Page("pages/04_results.py",   title="Results",      icon="🏆"),
])
pg.run()
