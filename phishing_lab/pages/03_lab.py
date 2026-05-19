import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from utils.scenario_generator import get_scenarios_for_session
from utils.scorer import update_score_in_csv

# ─────────────────────────────────────────────────────────────────────────────
# Simulator renderers — each returns HTML string
# ─────────────────────────────────────────────────────────────────────────────

def _email_simulator(s: dict) -> str:
    content = s.get("message_content", "")
    sender_name = s.get("sender_name", "Unknown Sender")
    sender_addr = s.get("sender_address", "unknown@example.com")
    # Split out headers vs body
    lines = content.split("\n")
    subject = "Important Notice"
    body_lines = []
    in_body = False
    for ln in lines:
        if ln.lower().startswith("subject:"):
            subject = ln[8:].strip()
        elif ln.lower().startswith("from:"):
            pass
        else:
            in_body = True
            body_lines.append(ln)
    body = "<br>".join(l for l in body_lines if l.strip() or in_body)

    return f"""
<div style="background:#013140;border-radius:12px;overflow:hidden;max-width:580px;margin:auto;box-shadow:0 6px 28px rgba(1,49,64,0.6);border:1px solid rgba(204,159,102,0.25);">
  <div style="background:#026281;padding:10px 18px;display:flex;align-items:center;gap:10px;border-bottom:1px solid rgba(204,159,102,0.2);">
    <span style="color:#CC9F66;font-weight:700;font-size:0.95em;letter-spacing:1px;">📧 EMAIL — INBOX</span>
    <span style="color:rgba(255,255,255,0.45);font-size:0.8em;margin-left:auto;">Unread</span>
  </div>
  <div style="padding:20px 24px;">
    <table style="width:100%;border-collapse:collapse;margin-bottom:14px;font-size:0.9em;">
      <tr><td style="color:rgba(255,255,255,0.55);width:70px;padding:4px 0;vertical-align:top;">From:</td>
          <td style="color:#FFFFFF;padding:4px 0;"><strong>{sender_name}</strong> <span style="color:#ef4444;">&lt;{sender_addr}&gt;</span></td></tr>
      <tr><td style="color:rgba(255,255,255,0.55);padding:4px 0;">To:</td>
          <td style="color:#FFFFFF;padding:4px 0;">you@email.com</td></tr>
      <tr><td style="color:rgba(255,255,255,0.55);padding:4px 0;">Subject:</td>
          <td style="color:#CC9F66;font-weight:600;padding:4px 0;">{subject}</td></tr>
    </table>
    <hr style="border-color:rgba(204,159,102,0.2);margin:12px 0;">
    <div style="color:#FFFFFF;line-height:1.75;font-size:0.95em;">{body}</div>
    <div style="margin-top:16px;padding:8px 12px;background:rgba(239,68,68,0.12);border-left:3px solid #ef4444;border-radius:4px;color:#fca5a5;font-size:0.8em;">
      ⚠️ Links in this simulation are disabled. Clicking would be dangerous in real life.
    </div>
  </div>
</div>"""


def _tiktok_simulator(s: dict) -> str:
    sender = s.get("sender_name", "TikTok User")
    content = s.get("message_content", "").replace("\n", "<br>")
    initial = sender[0].upper() if sender else "?"
    return f"""
<div style="background:#010101;border-radius:16px;overflow:hidden;max-width:380px;margin:auto;box-shadow:0 6px 24px rgba(0,0,0,0.5);">
  <div style="background:#111;padding:14px 16px;display:flex;align-items:center;gap:12px;border-bottom:1px solid #222;">
    <div style="background:#fe2c55;border-radius:50%;width:36px;height:36px;display:flex;align-items:center;justify-content:center;color:white;font-weight:700;flex-shrink:0;">{initial}</div>
    <div>
      <div style="color:white;font-weight:600;font-size:0.9em;">{sender}</div>
      <div style="color:#888;font-size:0.75em;">Direct Message</div>
    </div>
    <div style="margin-left:auto;color:#fe2c55;font-size:1.1em;">🎵</div>
  </div>
  <div style="padding:18px 16px;min-height:100px;">
    <div style="display:flex;align-items:flex-start;gap:10px;">
      <div style="background:#fe2c55;border-radius:50%;width:28px;height:28px;display:flex;align-items:center;justify-content:center;color:white;font-size:0.75em;flex-shrink:0;">{initial}</div>
      <div style="background:#1f1f1f;border-radius:4px 16px 16px 16px;padding:10px 14px;color:#f5f5f5;font-size:0.9em;line-height:1.55;max-width:280px;">{content}</div>
    </div>
    <div style="color:#555;font-size:0.75em;margin-top:6px;margin-left:38px;">just now</div>
  </div>
  <div style="padding:8px 16px;background:#0a0a0a;border-top:1px solid #1a1a1a;">
    <div style="background:#1a1a1a;border-radius:20px;padding:8px 14px;color:#555;font-size:0.85em;">Message…</div>
  </div>
</div>"""


def _instagram_simulator(s: dict) -> str:
    sender = s.get("sender_name", "Instagram Support")
    content = s.get("message_content", "").replace("\n", "<br>")
    initial = sender[0].upper() if sender else "?"
    return f"""
<div style="background:#fafafa;border-radius:16px;overflow:hidden;max-width:380px;margin:auto;box-shadow:0 6px 24px rgba(0,0,0,0.35);">
  <div style="background:linear-gradient(135deg,#833ab4,#fd1d1d,#fcb045);padding:14px 16px;display:flex;align-items:center;gap:12px;">
    <div style="background:rgba(255,255,255,0.25);border-radius:50%;width:36px;height:36px;display:flex;align-items:center;justify-content:center;color:white;font-weight:700;">{initial}</div>
    <div>
      <div style="color:white;font-weight:700;font-size:0.9em;">{sender} ✓</div>
      <div style="color:rgba(255,255,255,0.75);font-size:0.75em;">Instagram Direct</div>
    </div>
  </div>
  <div style="padding:18px 16px;background:white;min-height:90px;">
    <div style="background:#efefef;border-radius:4px 16px 16px 16px;padding:12px 14px;color:#262626;font-size:0.9em;line-height:1.55;max-width:280px;display:inline-block;">{content}</div>
    <div style="color:#8e8e8e;font-size:0.75em;margin-top:6px;">1 minute ago</div>
  </div>
  <div style="padding:8px 14px;background:white;border-top:1px solid #dbdbdb;">
    <div style="border:1px solid #dbdbdb;border-radius:20px;padding:8px 14px;color:#8e8e8e;font-size:0.85em;">Message…</div>
  </div>
</div>"""


def _whatsapp_simulator(s: dict) -> str:
    sender = s.get("sender_address", "+254700000000")
    sender_name = s.get("sender_name", sender)
    content = s.get("message_content", "").replace("\n", "<br>")
    return f"""
<div style="background:#111b21;border-radius:16px;overflow:hidden;max-width:380px;margin:auto;box-shadow:0 6px 24px rgba(0,0,0,0.4);">
  <div style="background:#202c33;padding:12px 16px;display:flex;align-items:center;gap:12px;border-bottom:1px solid #2a3942;">
    <div style="background:#00a884;border-radius:50%;width:38px;height:38px;display:flex;align-items:center;justify-content:center;color:white;font-size:1.2em;flex-shrink:0;">💬</div>
    <div>
      <div style="color:#e9edef;font-weight:600;font-size:0.9em;">{sender_name}</div>
      <div style="color:#8696a0;font-size:0.75em;">{sender}</div>
    </div>
  </div>
  <div style="padding:16px;min-height:100px;background:linear-gradient(rgba(17,27,33,0.97),rgba(17,27,33,0.97));">
    <div style="background:#005c4b;border-radius:8px 0 8px 8px;padding:10px 14px;color:#e9edef;max-width:290px;margin-left:auto;font-size:0.9em;line-height:1.55;">
      {content}
      <div style="text-align:right;color:#8696a0;font-size:0.7em;margin-top:4px;">12:34 ✓✓</div>
    </div>
  </div>
  <div style="padding:8px 14px;background:#202c33;border-top:1px solid #2a3942;">
    <div style="background:#2a3942;border-radius:20px;padding:8px 14px;color:#8696a0;font-size:0.85em;">Type a message</div>
  </div>
</div>"""


def _website_simulator(s: dict) -> str:
    sender_name = s.get("sender_name", "Account Portal")
    fake_domain = f"login-{sender_name.lower().replace(' ', '-')}.xyz"
    return f"""
<div style="background:#013140;border-radius:12px;overflow:hidden;max-width:440px;margin:auto;box-shadow:0 6px 28px rgba(1,49,64,0.6);border:1px solid rgba(204,159,102,0.25);">
  <div style="background:#026281;padding:8px 14px;display:flex;align-items:center;gap:8px;">
    <div style="display:flex;gap:5px;">
      <div style="background:#ff5f57;border-radius:50%;width:11px;height:11px;"></div>
      <div style="background:#febc2e;border-radius:50%;width:11px;height:11px;"></div>
      <div style="background:#28c840;border-radius:50%;width:11px;height:11px;"></div>
    </div>
    <div style="background:rgba(1,49,64,0.7);border-radius:4px;padding:4px 10px;color:#ef4444;font-size:0.78em;flex:1;margin-left:6px;font-family:monospace;border:1px solid rgba(239,68,68,0.3);">
      🔴 http://{fake_domain}/signin
    </div>
  </div>
  <div style="padding:30px 28px;background:#f5f0eb;text-align:center;">
    <div style="font-size:2.2em;margin-bottom:6px;">⚠️</div>
    <div style="font-size:1.25em;font-weight:700;color:#013140;margin-bottom:4px;">{sender_name}</div>
    <div style="color:#026281;font-size:0.85em;margin-bottom:20px;">Sign in to continue</div>
    <input disabled placeholder="Username or Email" style="width:100%;padding:10px 12px;margin-bottom:10px;border:1px solid #CC9F66;border-radius:6px;box-sizing:border-box;background:#fff;font-size:0.9em;color:#013140;">
    <input type="password" disabled placeholder="Password" style="width:100%;padding:10px 12px;margin-bottom:16px;border:1px solid #CC9F66;border-radius:6px;box-sizing:border-box;background:#fff;font-size:0.9em;color:#013140;">
    <div style="background:#026281;color:#FFFFFF;padding:10px;border-radius:6px;font-weight:600;opacity:0.55;">Sign In</div>
    <div style="margin-top:14px;padding:8px 10px;background:rgba(204,159,102,0.15);border:1px solid rgba(204,159,102,0.4);border-radius:6px;color:#013140;font-size:0.8em;">
      ⚠️ This is a simulation. The login above is disabled — no data is collected.
    </div>
  </div>
</div>"""


def _phone_simulator(s: dict) -> str:
    sender = s.get("sender_name", "Unknown Caller")
    sender_addr = s.get("sender_address", "+Unknown")
    content = s.get("message_content", "Caller: 'Hello, this is your bank. We need to verify your account.'")
    # Format as transcript lines
    lines = content.split("\n")
    bubbles = ""
    for ln in lines:
        if not ln.strip():
            continue
        if ln.lower().startswith("you:") or ln.lower().startswith("me:"):
            bubbles += f'<div style="text-align:right;margin:6px 0;"><div style="display:inline-block;background:rgba(204,159,102,0.2);border:1px solid rgba(204,159,102,0.4);color:#FFFFFF;padding:8px 13px;border-radius:12px 3px 12px 12px;font-size:0.88em;max-width:280px;text-align:left;">{ln}</div></div>'
        else:
            bubbles += f'<div style="margin:6px 0;"><div style="display:inline-block;background:#026281;color:#FFFFFF;padding:8px 13px;border-radius:3px 12px 12px 12px;font-size:0.88em;max-width:280px;">{ln}</div></div>'

    return f"""
<div style="background:#013140;border-radius:16px;overflow:hidden;max-width:400px;margin:auto;box-shadow:0 6px 28px rgba(1,49,64,0.6);border:1px solid rgba(204,159,102,0.25);">
  <div style="background:#026281;padding:16px;text-align:center;border-bottom:1px solid rgba(204,159,102,0.2);">
    <div style="font-size:2em;margin-bottom:4px;">📞</div>
    <div style="color:#CC9F66;font-size:0.75em;font-weight:700;letter-spacing:2px;">INCOMING CALL</div>
    <div style="color:#FFFFFF;font-size:1.1em;font-weight:700;margin-top:4px;">{sender}</div>
    <div style="color:rgba(255,255,255,0.5);font-size:0.8em;">{sender_addr}</div>
  </div>
  <div style="padding:16px;">
    <div style="color:#CC9F66;font-size:0.72em;font-weight:700;letter-spacing:2px;margin-bottom:12px;">CALL TRANSCRIPT</div>
    {bubbles}
  </div>
</div>"""


# ─────────────────────────────────────────────────────────────────────────────
# Action button definitions per platform
# ─────────────────────────────────────────────────────────────────────────────
PLATFORM_ACTIONS = {
    # email: verify by navigating directly to the official site (never via the link in the email)
    "email":     [("🚨 Report Phishing",              "report"),
                  ("🗑️ Delete",                       "ignore"),
                  ("🔍 Verify through Official App",  "verify_elsewhere"),
                  ("⚠️ Click Link",                   "click_link")],
    # tiktok: verify by opening TikTok app → Settings → Account
    "tiktok":    [("🚨 Report",                       "report"),
                  ("🚫 Block",                         "ignore"),
                  ("🔍 Verify through Official App",  "verify_elsewhere"),
                  ("⚠️ Click Link",                   "click_link")],
    # instagram: verify by opening Instagram → Settings → Account → Emails from Instagram
    "instagram": [("🚨 Report Spam",                  "report"),
                  ("👁️ Ignore",                       "ignore"),
                  ("🔍 Verify through Official App",  "verify_elsewhere"),
                  ("⚠️ Click Link",                   "click_link")],
    # whatsapp: verify by opening the official service app directly (e.g. MySafaricom for M-PESA)
    "whatsapp":  [("🚨 Report Spam",                  "report"),
                  ("🚫 Block Number",                 "ignore"),
                  ("🔍 Verify through Official App",  "verify_elsewhere"),
                  ("⚠️ Click Link",                   "click_link")],
    # sms: verify by dialing the official USSD code or opening the official app
    "sms":       [("🚨 Report Spam",                  "report"),
                  ("🚫 Block Number",                 "ignore"),
                  ("🔍 Verify through Official App",  "verify_elsewhere"),
                  ("⚠️ Click Link",                   "click_link")],
    # website: no "verify" option — either close the tab or enter credentials
    "website":   [("⚠️ Enter Credentials",            "click_link"),
                  ("✅ Close Tab",                    "click_none"),
                  ("🚨 Report",                       "report")],
    # phone: ask targeted questions to expose the scammer, or hang up
    "phone":     [("✅ Hang Up",                      "ignore"),
                  ("⚠️ Provide Info",                 "click_link"),
                  ("🔍 Verify through Official App",  "verify_elsewhere")],
}

CORRECT_ACTION_LABELS = {
    "report":           "🚨 Report Phishing / Report Spam",
    "ignore":           "🗑️ Delete / Block / Ignore / Hang Up",
    "verify_elsewhere": "🔍 Verify through the Official App / Website directly",
    "click_none":       "✅ Close Tab — never enter credentials on suspicious pages",
    "mark_safe":        "(This message is NOT safe)",
}


def _render_simulator(scenario: dict):
    platform = scenario.get("platform", "email").lower()
    if platform == "email":
        html = _email_simulator(scenario)
    elif platform == "tiktok":
        html = _tiktok_simulator(scenario)
    elif platform == "instagram":
        html = _instagram_simulator(scenario)
    elif platform in ("whatsapp", "sms"):
        html = _whatsapp_simulator(scenario)
    elif platform == "website":
        html = _website_simulator(scenario)
    elif platform == "phone":
        html = _phone_simulator(scenario)
    else:
        html = _email_simulator(scenario)
    st.markdown(html, unsafe_allow_html=True)


def _render_action_buttons(scenario: dict, current_idx: int):
    """Render platform-appropriate action buttons. Returns the chosen action or None."""
    platform = scenario.get("platform", "email").lower()
    actions = PLATFORM_ACTIONS.get(platform, PLATFORM_ACTIONS["email"])

    st.markdown("### 🤔 What should you do?")
    cols = st.columns(len(actions))
    for i, (col, (label, action_id)) in enumerate(zip(cols, actions)):
        with col:
            btn_type = "primary" if "⚠️" in label else "secondary"
            if st.button(label, key=f"act_{current_idx}_{i}",
                         use_container_width=True, type=btn_type):
                return action_id
    return None


# ─────────────────────────────────────────────────────────────────────────────
# PAGE
# ─────────────────────────────────────────────────────────────────────────────
st.title("🔬 Phishing Lab")
st.markdown("Face 5 realistic phishing scenarios. Choose the correct action for each. **20 points per correct answer — 100 max.**")
st.divider()

# Guard: require survey
if not st.session_state.user_profile.get("name"):
    st.warning("⚠️ Please complete the **Survey** first so we can personalise your scenarios.")
    if st.button("Go to Survey →", type="primary"):
        st.switch_page("pages/01_survey.py")
    st.stop()

state = st.session_state.lab_state

# ─────────────────────────────────────────────────────────────────────────────
# STATE: init — show start screen
# ─────────────────────────────────────────────────────────────────────────────
if state == "init":
    prof = st.session_state.user_profile
    st.markdown(f"""
### Welcome to the Lab, **{prof.get('name', 'Participant')}**!

You will face **5 phishing scenarios** tailored to:
- **Your role:** {prof.get('role', '—')}
- **Your platform:** {prof.get('platform', '—')}
- **Your tech level:** {prof.get('tech_level', '—')}

Each scenario is a realistic simulation of an actual phishing attack.
Read carefully and choose the best action. You cannot go back once you confirm.
""")
    col_a, col_b, col_c = st.columns([2, 1, 2])
    with col_b:
        if st.button("🚀 Start Lab", type="primary", use_container_width=True):
            st.session_state.lab_state = "loading"
            st.session_state.lab_current = 0
            st.session_state.lab_score = 0
            st.session_state.lab_answers = []
            st.session_state.lab_feedback_data = None
            st.session_state.lab_csv_saved = False
            st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
# STATE: loading — generate scenarios
# ─────────────────────────────────────────────────────────────────────────────
elif state == "loading":
    with st.spinner("🤖 Generating personalised phishing scenarios… (this may take up to 30 s)"):
        try:
            scenarios = get_scenarios_for_session(
                st.session_state.user_profile, use_api=True
            )
        except Exception:
            from utils.scenario_generator import _load_fallback
            scenarios = _load_fallback()
    if not scenarios:
        st.error("Could not load scenarios. Please refresh and try again.")
        st.stop()
    st.session_state.lab_scenarios = scenarios
    st.session_state.lab_state = "in_progress"
    st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
# STATE: in_progress — show current scenario
# ─────────────────────────────────────────────────────────────────────────────
elif state == "in_progress":
    scenarios = st.session_state.lab_scenarios or []
    if not scenarios:
        st.session_state.lab_state = "loading"
        st.rerun()

    idx = st.session_state.lab_current
    if idx >= len(scenarios):
        st.session_state.lab_state = "completed"
        st.rerun()

    scenario = scenarios[idx]
    score_so_far = st.session_state.lab_score or 0
    platform = scenario.get("platform", "email").title()

    # Progress header
    sc1, sc2, sc3 = st.columns([3, 1, 1])
    with sc1:
        st.progress((idx) / 5, text=f"Scenario **{idx + 1} / 5**")
    with sc2:
        st.metric("Score", f"{score_so_far}/100")
    with sc3:
        st.metric("Platform", platform)

    st.markdown("")

    # Simulator
    _render_simulator(scenario)
    st.markdown("")

    # Action buttons
    chosen = _render_action_buttons(scenario, idx)
    if chosen is not None:
        correct = scenario.get("correct_action", "report")
        is_correct = (chosen == correct)
        points = 20 if is_correct else 0
        st.session_state.lab_score = score_so_far + points
        st.session_state.lab_answers.append({
            "scenario_idx": idx,
            "platform": scenario.get("platform"),
            "chosen": chosen,
            "is_correct": is_correct,
            "correct_action": correct,
            "points": points,
        })
        st.session_state.lab_feedback_data = {
            "chosen": chosen,
            "correct": correct,
            "points": points,
            "is_correct": is_correct,
            "is_link_click": chosen == "click_link",
            "explanation": scenario.get("explanation", ""),
            "red_flags": scenario.get("red_flags", []),
            "platform": scenario.get("platform", "email"),
        }
        st.session_state.lab_state = "feedback"
        st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
# STATE: feedback — show result of choice
# ─────────────────────────────────────────────────────────────────────────────
elif state == "feedback":
    fd = st.session_state.lab_feedback_data or {}
    idx = st.session_state.lab_current
    score_now = st.session_state.lab_score or 0

    # Danger banner for link clicks
    if fd.get("is_link_click"):
        st.markdown("""
<div style="background:rgba(239,68,68,0.13);border:2px solid #ef4444;border-radius:12px;padding:18px 22px;margin-bottom:16px;">
  <div style="font-size:1.1em;font-weight:700;color:#fca5a5;letter-spacing:0.5px;">⚠️ DANGER — Link Clicked!</div>
  <div style="color:#FFFFFF;margin-top:8px;line-height:1.6;">In a real phishing attack, clicking this link could install malware, steal your login credentials, or give attackers full access to your accounts and finances.</div>
</div>""", unsafe_allow_html=True)

    # Correct / wrong
    chosen_action = fd.get("chosen", "")

    if fd.get("is_correct"):
        # Special praise for choosing verify_elsewhere correctly
        if chosen_action == "verify_elsewhere":
            st.success(f"✅ **Excellent!** Verifying through the official app is the safest move. +{fd['points']} points — score: **{score_now}/100**")
        else:
            st.success(f"✅ **Correct!** +{fd['points']} points — your score is now **{score_now}/100**")
    else:
        correct_label = CORRECT_ACTION_LABELS.get(fd.get("correct", ""), fd.get("correct", ""))
        # Explain why verify_elsewhere is sometimes better than just deleting
        if fd.get("correct") == "verify_elsewhere":
            st.error(f"❌ **Not quite.** Simply deleting or reporting is good, but the best action here is: **{correct_label}** — go to the official app or website independently to check if the alert is real.")
        else:
            st.error(f"❌ **Incorrect.** The right action was: **{correct_label}**")

    # Explanation
    st.info(f"**📖 Explanation:** {fd.get('explanation', '')}")

    # Verify-elsewhere tip: show platform-specific official verification guidance
    if chosen_action == "verify_elsewhere" or fd.get("correct") == "verify_elsewhere":
        platform = fd.get("platform", "")
        VERIFY_TIPS = {
            "email":     "Open your browser and **type the official website URL yourself** (e.g. youtube.com, kra.go.ke). Never follow links from suspicious emails.",
            "whatsapp":  "Dial the official USSD code (e.g. **\\*234#** for M-PESA) or open the **MySafaricom / official bank app** directly.",
            "sms":       "Dial the official USSD code or open the **official app** on your phone. Never tap links in SMS messages from unknown senders.",
            "tiktok":    "Open the **TikTok app** → Profile → Settings → Account. All real notifications appear inside the app.",
            "instagram": "Open **Instagram** → Profile → Settings → Security → Emails from Instagram to see genuine communications.",
            "phone":     "Hang up and **call the official number** printed on your bank card or the company's official website — never the number the caller gives you.",
        }
        tip = VERIFY_TIPS.get(platform, "Always go directly to the official website or app — **never follow links sent to you unsolicited**.")
        st.markdown(f"""
<div style="background:rgba(2,98,129,0.2);border:1px solid rgba(204,159,102,0.4);border-radius:10px;padding:14px 18px;margin-top:10px;">
  <div style="color:#CC9F66;font-weight:700;font-size:0.85em;letter-spacing:1px;margin-bottom:6px;">🔍 HOW TO VERIFY SAFELY</div>
  <div style="color:#FFFFFF;font-size:0.92em;line-height:1.6;">{tip}</div>
</div>""", unsafe_allow_html=True)

    # Red flags
    flags = fd.get("red_flags", [])
    if flags:
        st.markdown("**🚩 Red Flags in this message:**")
        flag_html = " ".join(
            f'<span style="display:inline-block;background:rgba(204,159,102,0.12);border:1px solid rgba(204,159,102,0.45);color:#CC9F66;border-radius:20px;padding:5px 14px;margin:3px;font-size:0.85em;">🚩 {f}</span>'
            for f in flags
        )
        st.markdown(flag_html, unsafe_allow_html=True)

    st.markdown("")
    is_last = (idx >= 4)
    next_label = "🏆 See My Results →" if is_last else f"Next Scenario ({idx + 2}/5) →"

    if st.button(next_label, type="primary", use_container_width=True):
        if is_last:
            st.session_state.lab_state = "completed"
        else:
            st.session_state.lab_current += 1
            st.session_state.lab_state = "in_progress"
        st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
# STATE: completed
# ─────────────────────────────────────────────────────────────────────────────
elif state == "completed":
    final_score = st.session_state.lab_score or 0
    passed = final_score >= 80

    if passed:
        st.balloons()

    st.markdown(f"""
## 🎯 Lab Complete!

You scored **{final_score} / 100** ({final_score}%)
""")

    if passed:
        st.success("🎉 **Congratulations!** You passed the Phishing Awareness Lab. Download your certificate on the Results page.")
    else:
        st.error("📚 You didn't quite make the 80% threshold. Review the flashcards and try again!")

    # Answers summary
    with st.expander("📋 Review Your Answers"):
        answers = st.session_state.lab_answers or []
        for i, ans in enumerate(answers):
            icon = "✅" if ans.get("is_correct") else "❌"
            st.markdown(f"{icon} **Scenario {i+1}** ({ans.get('platform','').title()}) — You chose: `{ans['chosen']}` | Correct action: `{ans.get('correct_action','—')}` | Points: **{ans['points']}**")

    # Save to CSV once
    if not st.session_state.lab_csv_saved:
        try:
            prof = st.session_state.user_profile
            update_score_in_csv(prof.get("user_id", ""), final_score, passed)
            st.session_state.lab_csv_saved = True
            st.session_state.completed_lab = True
            st.session_state.lab_score = final_score
        except Exception:
            pass

    st.markdown("")
    rc1, rc2 = st.columns(2)
    with rc1:
        if st.button("🔄 Retake Lab", use_container_width=True):
            st.session_state.lab_state = "init"
            st.session_state.lab_scenarios = None
            st.session_state.lab_current = 0
            st.session_state.lab_score = 0
            st.session_state.lab_answers = []
            st.session_state.lab_feedback_data = None
            st.session_state.lab_csv_saved = False
            st.rerun()
    with rc2:
        if st.button("🏆 View Full Results →", type="primary", use_container_width=True):
            st.switch_page("pages/04_results.py")
