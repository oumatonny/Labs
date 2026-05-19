import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import pandas as pd
from datetime import datetime
from utils.certificate_generator import generate_certificate
from utils.scorer    import load_all_progress, mark_certificate_downloaded
from utils.accounts  import get_account, mark_cert_downloaded, all_accounts, save_attempt

# ── Auth guard ────────────────────────────────────────────────────────────────
st.title("🏆 Results & Certificate")
st.divider()

if not st.session_state.get("logged_in"):
    st.warning("⚠️ Please login first.")
    if st.button("Go to Login →", type="primary"):
        st.switch_page("pages/00_home.py")
    st.stop()

# ── Load latest account data ──────────────────────────────────────────────────
_acc = get_account(st.session_state.email) or st.session_state.get("account") or {}
st.session_state.account = _acc
prof     = st.session_state.user_profile
attempts = list(_acc.get("attempts", []))   # copy so we can extend safely
best     = _acc.get("best_score")

# ── Session-state fallback ─────────────────────────────────────────────────────
# If accounts.json has no record (save failed, or pre-login session) but the lab
# was completed this session, synthesise a display-only attempt from session state.
_session_score = st.session_state.get("lab_score")
_session_done  = (
    st.session_state.get("completed_lab") and
    _session_score is not None and
    st.session_state.get("lab_answers")
)

if not attempts and _session_done:
    _synth = {
        "attempt_id":             1,
        "date":                   datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "score":                  _session_score,
        "passed":                 _session_score >= 80,
        "answers":                st.session_state.lab_answers,
        "certificate_downloaded": False,
        "_session_only":          True,   # marker — not persisted yet
    }
    attempts = [_synth]
    best     = _session_score

    # Try one more time to persist it now
    if st.session_state.get("email"):
        try:
            _aid = save_attempt(
                st.session_state.email,
                _session_score,
                _session_score >= 80,
                st.session_state.lab_answers,
            )
            if _aid:
                st.session_state.current_attempt_id = _aid
                # Reload from disk so subsequent rerenders are correct
                _acc = get_account(st.session_state.email) or {}
                st.session_state.account = _acc
                attempts = list(_acc.get("attempts", []))
                best     = _acc.get("best_score")
        except Exception:
            pass

# ── No attempts and nothing in session ────────────────────────────────────────
if not attempts:
    st.warning("⚠️ You haven't completed the **Phishing Lab** yet.")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🃏 Go to Flashcards", width="stretch"):
            st.switch_page("pages/02_flashcards.py")
    with c2:
        if st.button("🔬 Go to Lab", type="primary", width="stretch"):
            st.switch_page("pages/03_lab.py")
    st.stop()

# ─────────────────────────────────────────────────────────────────────────────
# Summary stats
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(f"### Results for **{prof.get('name', 'Participant')}**")
st.caption(f"📧 {st.session_state.email}  ·  🎭 {prof.get('role','—')}  ·  📱 {prof.get('platform','—')}")

passed_list = [a for a in attempts if a.get("passed")]
m1, m2, m3, m4 = st.columns(4)
m1.metric("Total Attempts",  len(attempts))
m2.metric("Best Score",      f"{best}/100" if best is not None else "—")
m3.metric("Times Passed",    len(passed_list))
m4.metric("Pass Rate",       f"{int(len(passed_list)/len(attempts)*100)}%" if attempts else "—")

st.divider()

# ─────────────────────────────────────────────────────────────────────────────
# Current session result (highlighted at top if fresh)
# ─────────────────────────────────────────────────────────────────────────────
_cur_id = st.session_state.get("current_attempt_id")
if _cur_id and st.session_state.get("completed_lab"):
    cur = next((a for a in attempts if a["attempt_id"] == _cur_id), None)
    if cur:
        score  = cur["score"]
        passed = cur["passed"]
        st.markdown("### 🎯 Latest Result")
        st.progress(score / 100, text=f"**{score}/100**")

        if passed:
            if passed:
                st.balloons()
            st.success(f"🎉 **Congratulations!** You scored **{score}/100** and passed the lab.")
        else:
            st.error(f"📚 You scored **{score}/100**. Score 80+ to pass. Review flashcards and try again!")
            c1, c2 = st.columns(2)
            with c1:
                if st.button("🃏 Review Flashcards", width="stretch"):
                    st.switch_page("pages/02_flashcards.py")
            with c2:
                if st.button("🔄 Retake Lab", type="primary", width="stretch"):
                    st.session_state.lab_state     = "init"
                    st.session_state.lab_scenarios  = None
                    st.session_state.lab_current   = 0
                    st.session_state.lab_score     = 0
                    st.session_state.lab_answers   = []
                    st.session_state.lab_feedback_data = None
                    st.session_state.lab_csv_saved = False
                    st.switch_page("pages/03_lab.py")

        # Answer breakdown for current attempt
        with st.expander("📊 Detailed Answer Breakdown", expanded=True):
            answers = cur.get("answers", [])
            if answers:
                rows = [{
                    "Scenario":       i + 1,
                    "Platform":       a.get("platform", "—").title(),
                    "Your Action":    a.get("chosen", "—"),
                    "Correct Action": a.get("correct_action", "—"),
                    "Points":         a.get("points", 0),
                    "Result":         "✅ Correct" if a.get("is_correct") else "❌ Wrong",
                } for i, a in enumerate(answers)]
                st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

        st.divider()

# ─────────────────────────────────────────────────────────────────────────────
# All attempts with per-attempt certificate download
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("### 📜 All Attempts")

for att in reversed(attempts):
    att_id   = att["attempt_id"]
    score    = att["score"]
    passed   = att["passed"]
    att_date = att["date"]
    cert_dl  = att.get("certificate_downloaded", False)

    border = "#22c55e" if passed else "#ef4444"
    bg     = "rgba(34,197,94,0.07)" if passed else "rgba(239,68,68,0.07)"
    badge  = "✅ PASSED" if passed else "❌ FAILED"

    st.markdown(f"""
<div style="background:{bg};border:1px solid {border};border-radius:10px;padding:14px 20px;margin-bottom:6px;">
  <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;">
    <div>
      <span style="color:#CC9F66;font-weight:700;">Attempt #{att_id}</span>
      <span style="color:rgba(255,255,255,0.45);font-size:0.85em;margin-left:12px;">{att_date}</span>
    </div>
    <div style="font-size:1.05em;">
      <strong style="color:#FFFFFF;">{score}/100</strong>
      <span style="margin-left:10px;">{badge}</span>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

    col_exp, col_cert = st.columns([3, 2])

    with col_exp:
        with st.expander(f"Show answer breakdown — Attempt #{att_id}"):
            _ans = att.get("answers", [])
            if _ans:
                rows = [{
                    "#":             i + 1,
                    "Platform":      a.get("platform", "—").title(),
                    "Your Action":   a.get("chosen", "—"),
                    "Correct":       a.get("correct_action", "—"),
                    "Pts":           a.get("points", 0),
                    "Result":        "✅" if a.get("is_correct") else "❌",
                } for i, a in enumerate(_ans)]
                st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch")
            else:
                st.caption("No detailed breakdown available.")

    with col_cert:
        if passed:
            try:
                pdf = generate_certificate(
                    user_name=prof.get("name", "Participant"),
                    score=score,
                    date=att_date[:10],
                )
                safe = prof.get("name", "participant").replace(" ", "_")
                label = (f"📄 Download Certificate #{att_id}" +
                         (" ✓ downloaded" if cert_dl else ""))
                dl_clicked = st.download_button(
                    label=label,
                    data=pdf,
                    file_name=f"certificate_{safe}_attempt{att_id}.pdf",
                    mime="application/pdf",
                    type="primary",
                    key=f"res_dl_{att_id}",
                    width="stretch",
                )
                if dl_clicked:
                    mark_cert_downloaded(st.session_state.email, att_id)
                    try:
                        mark_certificate_downloaded(prof.get("user_id", ""))
                    except Exception:
                        pass
            except Exception as ex:
                st.warning(f"Certificate error: {ex}")
        else:
            st.info("Score 80+ to unlock certificate.", icon="🔒")

    st.markdown("")

st.divider()

# ─────────────────────────────────────────────────────────────────────────────
# Admin panel
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("## 🔐 Organisation Admin Panel")

if not st.session_state.get("admin_authenticated"):
    with st.form("admin_login"):
        pwd    = st.text_input("Admin Password", type="password")
        submit = st.form_submit_button("Login")
    if submit:
        if pwd == "admin123":
            st.session_state.admin_authenticated = True
            st.rerun()
        else:
            st.error("Incorrect password.")
else:
    st.success("✅ Admin access granted.")
    if st.button("🔓 Logout Admin", key="admin_logout"):
        st.session_state.admin_authenticated = False
        st.rerun()

    st.markdown("### 📈 Organisation Statistics")
    try:
        accs = all_accounts()
        if not accs:
            st.info("No accounts registered yet.")
        else:
            total     = len(accs)
            completed = [a for a in accs if a.get("attempts")]
            all_atts  = [att for a in accs for att in a.get("attempts", [])]
            passed_a  = [att for att in all_atts if att.get("passed")]
            avg_score = (sum(att["score"] for att in all_atts) / len(all_atts)) if all_atts else 0
            pass_rate = (len(passed_a) / len(all_atts) * 100) if all_atts else 0

            s1, s2, s3, s4 = st.columns(4)
            s1.metric("Registered Users",   total)
            s2.metric("Completed Lab",       len(completed))
            s3.metric("Avg Score",           f"{avg_score:.1f}/100")
            s4.metric("Overall Pass Rate",   f"{pass_rate:.1f}%")

            st.markdown("### 👥 All Accounts")
            rows = []
            for a in accs:
                best_a = a.get("best_score")
                rows.append({
                    "Name":          a.get("name", ""),
                    "Email":         a.get("email", ""),
                    "Role":          a.get("role", "—"),
                    "Platform":      a.get("platform", "—"),
                    "Attempts":      len(a.get("attempts", [])),
                    "Best Score":    f"{best_a}/100" if best_a is not None else "—",
                    "Last Login":    a.get("last_login", "—"),
                })
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

            # Legacy CSV download
            try:
                df_csv = load_all_progress()
                st.download_button(
                    "📊 Download Legacy CSV",
                    df_csv.to_csv(index=False).encode(),
                    "phishing_lab_results.csv",
                    "text/csv",
                )
            except Exception:
                pass

            # Accounts JSON download
            import json
            from utils.accounts import _load as _load_acc
            st.download_button(
                "📦 Download accounts.json",
                json.dumps(_load_acc(), indent=2, ensure_ascii=False).encode(),
                "accounts.json",
                "application/json",
            )
    except Exception as e:
        st.error(f"Could not load data: {e}")
