import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import re
import streamlit as st
from utils.accounts import login_or_register, get_account
from utils.certificate_generator import generate_certificate

# ── helpers ───────────────────────────────────────────────────────────────────

def _valid_email(e: str) -> bool:
    return bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", e.strip()))


def _load_profile_from_account(acc: dict):
    """Populate st.session_state.user_profile from an account dict."""
    st.session_state.user_profile = {
        "name":       acc.get("name", ""),
        "email":      acc.get("email", ""),
        "role":       acc.get("role", ""),
        "platform":   acc.get("platform", ""),
        "tech_level": acc.get("tech_level", ""),
        "user_id":    acc.get("user_id", ""),
    }


def _has_complete_profile(acc: dict) -> bool:
    return bool(acc.get("role") and acc.get("platform") and acc.get("tech_level"))


# ─────────────────────────────────────────────────────────────────────────────
# NOT LOGGED IN  →  Login / Register screen
# ─────────────────────────────────────────────────────────────────────────────
if not st.session_state.get("logged_in"):

    # ── Branding ──────────────────────────────────────────────────────────────
    st.markdown("""
<div style="text-align:center;padding:20px 0 8px;">
  <div style="font-size:3em;">🛡️</div>
  <h1 style="color:#CC9F66;margin:0;">Phishing Awareness Lab</h1>
  <p style="color:rgba(255,255,255,0.6);margin-top:4px;">
    Interactive cybersecurity training by <strong>Newslight Kenya</strong>
  </p>
</div>
""", unsafe_allow_html=True)

    st.divider()

    col_info, col_gap, col_form = st.columns([5, 1, 4])

    # ── Left — what is this? ──────────────────────────────────────────────────
    with col_info:
        st.markdown("""
### What you will learn
✅ Identify phishing emails, DMs, and SMS messages
✅ Recognise red flags on any platform
✅ Know exactly what to do when you spot a scam
✅ Earn a **PDF certificate** after passing

### Who is at risk?
Phishing attacks target everyone, but especially:
- 🎥 Content creators  (fake sponsorships)
- 🏦 Business owners  (invoice fraud)
- 📱 Social-media users  (fake verification badges)
- 👴 Senior citizens  (tech-support scams)

### How it works
| Step | Activity | Time |
|------|----------|------|
| 1 | Short survey | ~1 min |
| 2 | 10 flashcards | ~5 min |
| 3 | 5-scenario lab | ~10 min |
| 4 | Certificate | instant |
""")

    # ── Right — login form ────────────────────────────────────────────────────
    with col_form:
        st.markdown("""
<div style="background:#026281;border:1.5px solid rgba(204,159,102,0.4);border-radius:14px;padding:28px 24px;">
""", unsafe_allow_html=True)

        st.markdown("### 🔐 Login / Register")
        st.caption("New users are registered automatically. Returning users are logged straight in.")

        with st.form("login_form"):
            name_in  = st.text_input("Full Name",      placeholder="e.g. Jane Mwangi")
            email_in = st.text_input("Email Address",  placeholder="e.g. jane@example.com")
            submitted = st.form_submit_button("Continue →", type="primary")

        if submitted:
            name_in  = name_in.strip()
            email_in = email_in.strip()
            err = ""
            if not name_in:
                err = "Please enter your name."
            elif not email_in or not _valid_email(email_in):
                err = "Please enter a valid email address."

            if err:
                st.error(err)
            else:
                acc, is_new = login_or_register(name_in, email_in)
                st.session_state.logged_in  = True
                st.session_state.email      = acc["email"]
                st.session_state.account    = acc
                _load_profile_from_account(acc)

                if is_new or not _has_complete_profile(acc):
                    st.success(f"Welcome, **{acc['name']}**! Let's set up your profile.")
                    st.switch_page("pages/01_survey.py")
                else:
                    st.success(f"Welcome back, **{acc['name']}**!")
                    st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

    st.stop()


# ─────────────────────────────────────────────────────────────────────────────
# LOGGED IN  →  Dashboard
# ─────────────────────────────────────────────────────────────────────────────

# Refresh account from disk (catches results saved in other pages)
_acc = get_account(st.session_state.email) or st.session_state.account or {}
st.session_state.account = _acc
_load_profile_from_account(_acc)

prof     = st.session_state.user_profile
attempts = _acc.get("attempts", [])
best     = _acc.get("best_score")

# ── Welcome header ────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="background:linear-gradient(135deg,#013140,#026281);border:1.5px solid rgba(204,159,102,0.35);border-radius:14px;padding:24px 28px;margin-bottom:8px;">
  <div style="font-size:1.6em;font-weight:700;color:#FFFFFF;">
    👋 Welcome back, {prof.get('name','Participant')}!
  </div>
  <div style="color:rgba(255,255,255,0.55);font-size:0.9em;margin-top:4px;">
    📧 {st.session_state.email}
    &nbsp;·&nbsp;
    🎭 {prof.get('role','—')}
    &nbsp;·&nbsp;
    📱 {prof.get('platform','—')}
    &nbsp;·&nbsp;
    Last login: {_acc.get('last_login','—')}
  </div>
</div>
""", unsafe_allow_html=True)

# ── Stats row ─────────────────────────────────────────────────────────────────
m1, m2, m3, m4 = st.columns(4)
passed_count = sum(1 for a in attempts if a.get("passed"))
m1.metric("Total Attempts",  len(attempts))
m2.metric("Best Score",      f"{best}/100" if best is not None else "—")
m3.metric("Times Passed",    passed_count)
m4.metric("Pass Rate",       f"{int(passed_count/len(attempts)*100)}%" if attempts else "—")

st.divider()

# ── Quick actions ─────────────────────────────────────────────────────────────
st.markdown("### 🚀 Quick Actions")
qa1, qa2, qa3, qa4 = st.columns(4)
with qa1:
    if st.button("📋 Update Profile", width="stretch"):
        st.switch_page("pages/01_survey.py")
with qa2:
    if st.button("🃏 Flashcards", width="stretch"):
        st.switch_page("pages/02_flashcards.py")
with qa3:
    if st.button("🔬 Start New Lab", type="primary", width="stretch"):
        # Reset lab state for a fresh attempt
        st.session_state.lab_state    = "init"
        st.session_state.lab_scenarios = None
        st.session_state.lab_current  = 0
        st.session_state.lab_score    = 0
        st.session_state.lab_answers  = []
        st.session_state.lab_feedback_data = None
        st.session_state.lab_csv_saved = False
        st.session_state.completed_lab = False
        st.switch_page("pages/03_lab.py")
with qa4:
    if st.button("🏆 View Results", width="stretch"):
        st.switch_page("pages/04_results.py")

st.divider()

# ── Attempt history ────────────────────────────────────────────────────────────
st.markdown("### 📜 Your Attempt History")

if not attempts:
    st.info("No attempts yet. Start the lab to record your first result.")
else:
    for att in reversed(attempts):          # most recent first
        att_id   = att["attempt_id"]
        score    = att["score"]
        passed   = att["passed"]
        att_date = att["date"]
        cert_dl  = att.get("certificate_downloaded", False)

        border  = "#22c55e" if passed else "#ef4444"
        bg      = "rgba(34,197,94,0.08)" if passed else "rgba(239,68,68,0.08)"
        status  = "✅ PASSED" if passed else "❌ FAILED"

        with st.container():
            st.markdown(f"""
<div style="background:{bg};border:1px solid {border};border-radius:10px;padding:14px 18px;margin-bottom:8px;">
  <div style="display:flex;justify-content:space-between;align-items:center;">
    <div>
      <span style="color:#CC9F66;font-weight:700;font-size:1em;">Attempt #{att_id}</span>
      <span style="color:rgba(255,255,255,0.5);font-size:0.85em;margin-left:12px;">{att_date}</span>
    </div>
    <div>
      <span style="font-weight:700;font-size:1.1em;color:#FFFFFF;">{score}/100</span>
      <span style="margin-left:10px;font-size:0.9em;">{status}</span>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

            # Per-answer mini table inside expander
            with st.expander(f"  Show answers — Attempt #{att_id}"):
                answers = att.get("answers", [])
                if answers:
                    import pandas as pd
                    rows = [{
                        "Scenario":       i + 1,
                        "Platform":       a.get("platform", "—").title(),
                        "Your Action":    a.get("chosen", "—"),
                        "Correct Action": a.get("correct_action", "—"),
                        "Points":         a.get("points", 0),
                        "Result":         "✅" if a.get("is_correct") else "❌",
                    } for i, a in enumerate(answers)]
                    st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch")
                else:
                    st.caption("No answer breakdown available for this attempt.")

            # Certificate download (only for passed attempts)
            if passed:
                try:
                    from utils.accounts import mark_cert_downloaded
                    pdf = generate_certificate(
                        user_name=prof.get("name", "Participant"),
                        score=score,
                        date=att_date[:10],
                    )
                    safe = prof.get("name", "participant").replace(" ", "_")
                    dl = st.download_button(
                        label=f"📄 Download Certificate — Attempt #{att_id}" + (" ✓" if cert_dl else ""),
                        data=pdf,
                        file_name=f"certificate_{safe}_attempt{att_id}.pdf",
                        mime="application/pdf",
                        key=f"dl_cert_{att_id}",
                    )
                    if dl:
                        mark_cert_downloaded(st.session_state.email, att_id)
                except Exception as e:
                    st.warning(f"Certificate unavailable: {e}")

        st.markdown("")
