import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import pandas as pd
from datetime import datetime
from utils.certificate_generator import generate_certificate
from utils.scorer import load_all_progress, mark_certificate_downloaded

# ─────────────────────────────────────────────────────────────────────────────
# Guards
# ─────────────────────────────────────────────────────────────────────────────
st.title("🏆 Results & Certificate")
st.divider()

prof = st.session_state.user_profile
if not prof.get("name"):
    st.warning("⚠️ Please complete the **Survey** first.")
    if st.button("Go to Survey →", type="primary"):
        st.switch_page("pages/01_survey.py")
    st.stop()

if not st.session_state.completed_lab or st.session_state.lab_score is None:
    st.warning("⚠️ Please complete the **Phishing Lab** first to see your results.")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Go to Flashcards →"):
            st.switch_page("pages/02_flashcards.py")
    with c2:
        if st.button("Go to Lab →", type="primary"):
            st.switch_page("pages/03_lab.py")
    st.stop()

# ─────────────────────────────────────────────────────────────────────────────
# Score section
# ─────────────────────────────────────────────────────────────────────────────
score = st.session_state.lab_score or 0
passed = score >= 80
pct = score  # already out of 100

# Summary row
m1, m2, m3, m4 = st.columns(4)
m1.metric("Your Score",      f"{score}/100")
m2.metric("Percentage",      f"{pct}%")
m3.metric("Status",          "PASSED ✅" if passed else "FAILED ❌")
m4.metric("Pass Threshold",  "80%")

st.markdown("")
st.progress(score / 100, text=f"**{score}/100**")
st.markdown("")

if passed:
    st.success(f"""
### 🎉 Congratulations, {prof.get('name', 'Participant')}!

You passed the Phishing Awareness Lab with a score of **{score}/100** ({pct}%).
You have demonstrated strong cybersecurity awareness. Download your certificate below.
""")
else:
    st.error(f"""
### 📚 Keep Practising!

You scored **{score}/100** ({pct}%). The passing threshold is **80%**.
Review the flashcards and retake the lab — you can do it!
""")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🃏 Review Flashcards", use_container_width=True):
            st.switch_page("pages/02_flashcards.py")
    with c2:
        if st.button("🔄 Retake Lab", type="primary", use_container_width=True):
            st.session_state.lab_state = "init"
            st.session_state.lab_scenarios = None
            st.session_state.lab_current = 0
            st.session_state.lab_score = 0
            st.session_state.lab_answers = []
            st.session_state.lab_feedback_data = None
            st.session_state.lab_csv_saved = False
            st.switch_page("pages/03_lab.py")

st.divider()

# ─────────────────────────────────────────────────────────────────────────────
# Answer breakdown
# ─────────────────────────────────────────────────────────────────────────────
with st.expander("📊 Detailed Answer Breakdown", expanded=True):
    answers = st.session_state.lab_answers or []
    if answers:
        rows = []
        for i, ans in enumerate(answers):
            rows.append({
                "Scenario": i + 1,
                "Platform": ans.get("platform", "—").title(),
                "Your Action": ans.get("chosen", "—"),
                "Correct Action": ans.get("correct_action", "—"),
                "Points": ans.get("points", 0),
                "Result": "✅ Correct" if ans.get("is_correct") else "❌ Wrong",
            })
        df_ans = pd.DataFrame(rows)
        st.dataframe(df_ans, use_container_width=True, hide_index=True)
    else:
        st.info("No answer data available.")

st.divider()

# ─────────────────────────────────────────────────────────────────────────────
# Certificate
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("## 📜 Your Certificate")

if passed:
    # Certificate preview
    st.markdown(f"""
<div style="background:linear-gradient(150deg,#013140,#026281);border:3px solid #CC9F66;border-radius:16px;padding:44px 40px;text-align:center;max-width:600px;margin:auto;box-shadow:0 10px 40px rgba(1,49,64,0.6);">
  <div style="color:#CC9F66;font-size:0.8em;font-weight:700;letter-spacing:4px;margin-bottom:6px;">CERTIFICATE OF COMPLETION</div>
  <div style="color:rgba(255,255,255,0.7);font-size:0.95em;margin-bottom:24px;">Phishing Awareness Training Program</div>
  <div style="color:rgba(255,255,255,0.55);font-size:0.9em;margin-bottom:10px;">This certifies that</div>
  <div style="color:#FFFFFF;font-size:2em;font-weight:700;margin:10px 0 4px;">{prof.get('name','Participant')}</div>
  <div style="border-bottom:2px solid #CC9F66;width:55%;margin:0 auto 22px;"></div>
  <div style="color:rgba(255,255,255,0.8);font-size:0.95em;line-height:1.7;margin-bottom:20px;">
    has successfully completed the Phishing Awareness Lab<br>and demonstrated knowledge of cybersecurity best practices.
  </div>
  <div style="display:inline-block;background:rgba(204,159,102,0.15);border:2px solid #CC9F66;border-radius:8px;padding:10px 28px;color:#CC9F66;font-weight:700;font-size:1.15em;margin-bottom:16px;">Score: {score}/100</div>
  <div style="color:rgba(255,255,255,0.45);font-size:0.85em;margin-bottom:16px;">{datetime.now().strftime("%B %d, %Y")}</div>
  <div style="color:#CC9F66;font-weight:700;font-size:1em;">Newslight Kenya</div>
  <div style="color:rgba(255,255,255,0.4);font-size:0.8em;">Cybersecurity Awareness Initiative</div>
</div>
""", unsafe_allow_html=True)

    st.markdown("")

    # Generate and offer PDF download
    try:
        pdf_bytes = generate_certificate(
            user_name=prof.get("name", "Participant"),
            score=score,
            date=datetime.now().strftime("%B %d, %Y"),
        )
        safe_name = prof.get("name", "participant").replace(" ", "_")
        clicked = st.download_button(
            label="📄 Download PDF Certificate",
            data=pdf_bytes,
            file_name=f"phishing_certificate_{safe_name}.pdf",
            mime="application/pdf",
            type="primary",
            use_container_width=True,
        )
        if clicked:
            try:
                mark_certificate_downloaded(prof.get("user_id", ""))
                st.session_state.certificate_downloaded = True
            except Exception:
                pass
    except Exception as e:
        st.error(f"Certificate generation failed: {e}")
        st.info("Please ensure reportlab is installed: `pip install reportlab`")

else:
    st.info("🔒 Complete the lab with a score of **80 or higher** to unlock your certificate.")

st.divider()

# ─────────────────────────────────────────────────────────────────────────────
# Admin panel (password-protected)
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("## 🔐 Organisation Admin Panel")

if not st.session_state.get("admin_authenticated"):
    with st.form("admin_login"):
        pwd = st.text_input("Admin Password", type="password", placeholder="Enter admin password")
        submit = st.form_submit_button("Login")
    if submit:
        if pwd == "admin123":
            st.session_state.admin_authenticated = True
            st.rerun()
        else:
            st.error("Incorrect password.")
else:
    st.success("✅ Admin access granted.")
    if st.button("🔓 Logout", key="admin_logout"):
        st.session_state.admin_authenticated = False
        st.rerun()

    st.markdown("### 📈 Organisation Statistics")
    try:
        df = load_all_progress()
        if df.empty:
            st.info("No participant data yet.")
        else:
            # Compute stats
            total = len(df)
            df_scored = df[df["lab_score"].notna() & (df["lab_score"] != "")]
            n_completed = len(df_scored)

            if n_completed > 0:
                df_scored = df_scored.copy()
                df_scored["lab_score"] = pd.to_numeric(df_scored["lab_score"], errors="coerce")
                avg_score = df_scored["lab_score"].mean()
                passed_mask = df_scored["lab_score"] >= 80
                pass_rate = (passed_mask.sum() / n_completed) * 100
            else:
                avg_score = 0.0
                pass_rate = 0.0

            a1, a2, a3, a4 = st.columns(4)
            a1.metric("Total Registered",  total)
            a2.metric("Completed Lab",     n_completed)
            a3.metric("Average Score",     f"{avg_score:.1f}/100" if n_completed else "—")
            a4.metric("Pass Rate",         f"{pass_rate:.1f}%" if n_completed else "—")

            st.markdown("")
            st.markdown("### 📋 Participant Records")
            st.dataframe(df, use_container_width=True, hide_index=True)

            # CSV download
            csv_data = df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📊 Download Full CSV",
                data=csv_data,
                file_name="phishing_lab_results.csv",
                mime="text/csv",
                use_container_width=True,
            )
    except Exception as e:
        st.error(f"Could not load data: {e}")
