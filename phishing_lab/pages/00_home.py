import streamlit as st

st.title("🛡️ Phishing Awareness Lab")
st.markdown("### Your interactive cybersecurity training — learn to spot scams before they spot you.")

st.divider()

# ── Hero section ──────────────────────────────────────────────────────────────
col_left, col_right = st.columns([3, 2], gap="large")

with col_left:
    st.markdown("""
## What is Phishing?

**Phishing** is a cyberattack where criminals impersonate trusted organisations,
platforms, or people to trick you into revealing passwords, banking details, or
personal data.

Attackers use **email, SMS, WhatsApp, Instagram DMs, TikTok messages, and fake
phone calls** to target people every single day.

### Why it matters to *you*
- 📧 **3.4 billion** phishing emails are sent every day globally
- 💸 Phishing causes **$1.8 billion** in annual losses
- 📱 Social-media & SMS phishing (smishing) is growing rapidly
- 🎯 **Content creators, teachers, business owners, and students** are prime targets
""")

with col_right:
    st.info("""
### 📚 What You Will Learn

✅ How to identify phishing attempts
✅ Red flags in emails, DMs, and SMS
✅ What to do if you click a phishing link
✅ Safe habits to protect yourself & others
✅ Platform-specific scam tactics
""")
    st.warning("""
**⏱ Estimated time:** 15–20 minutes
**📜 Completion:** PDF certificate
**🎯 Pass score:** 80 / 100
""")

st.divider()

# ── Stats row ─────────────────────────────────────────────────────────────────
st.markdown("## 📊 The Scale of the Threat")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Daily Phishing Emails", "3.4 B+",  delta="Growing", delta_color="inverse")
c2.metric("New Phishing Sites / Day", "1.5 M+", delta="Growing", delta_color="inverse")
c3.metric("Employees Fooled",        "1 in 3", delta=None)
c4.metric("Avg. Recovery Time",      "Months", delta=None)

st.divider()

# ── Journey map ──────────────────────────────────────────────────────────────
st.markdown("## 🗺️ Your Learning Journey")

steps = [
    ("1️⃣", "Survey", "Tell us about yourself so we can personalise your training"),
    ("2️⃣", "Flashcards", "Learn 10 key phishing concepts with interactive cards"),
    ("3️⃣", "Phishing Lab", "Face 5 real-world simulated phishing attacks"),
    ("4️⃣", "Score", "See how well you did and read detailed explanations"),
    ("5️⃣", "Certificate", "Download your Phishing Awareness Certificate as PDF"),
]

cols = st.columns(5)
for col, (num, title, desc) in zip(cols, steps):
    with col:
        st.markdown(f"### {num}")
        st.markdown(f"**{title}**")
        st.caption(desc)

st.divider()

# ── Common attack types ───────────────────────────────────────────────────────
st.markdown("## 🎭 Attack Types You Will Encounter")
a1, a2, a3 = st.columns(3)
with a1:
    st.error("📧 **Email Phishing**\nFake emails impersonating YouTube, KRA, or your bank with urgent threats.")
with a2:
    st.error("📱 **Smishing / Vishing**\nFraudulent SMS (smishing) and phone calls (vishing) requesting urgent action.")
with a3:
    st.error("📸 **Social Media Scams**\nFake DMs on Instagram, TikTok, and WhatsApp offering deals or threatening your account.")

st.divider()

# ── CTA ───────────────────────────────────────────────────────────────────────
st.markdown("## Ready to start?")

_prof = st.session_state.user_profile
if _prof.get("name"):
    st.success(f"Welcome back, **{_prof['name']}**! Pick up where you left off.")
    bc1, bc2, bc3 = st.columns(3)
    with bc1:
        if st.button("📋 Go to Survey", use_container_width=True):
            st.switch_page("pages/01_survey.py")
    with bc2:
        if st.button("🃏 Go to Flashcards", use_container_width=True):
            st.switch_page("pages/02_flashcards.py")
    with bc3:
        if st.button("🔬 Go to Lab", type="primary", use_container_width=True):
            st.switch_page("pages/03_lab.py")
else:
    if st.button("🚀 Start Training Now →", type="primary", use_container_width=True):
        st.switch_page("pages/01_survey.py")
