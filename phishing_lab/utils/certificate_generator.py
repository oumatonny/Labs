import io
from datetime import datetime
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.pdfgen import canvas as rl_canvas


def generate_certificate(user_name: str, score: int, date: str = None) -> bytes:
    """
    Generate a PDF certificate of completion.
    Returns raw PDF bytes suitable for st.download_button.
    """
    if not date:
        date = datetime.now().strftime("%B %d, %Y")
    if not user_name:
        user_name = "Participant"

    buf = io.BytesIO()
    page_w, page_h = landscape(A4)  # 841.89 x 595.28 pts
    c = rl_canvas.Canvas(buf, pagesize=landscape(A4))

    # Palette
    DARK   = colors.HexColor("#013140")
    MID    = colors.HexColor("#026281")
    WHITE  = colors.HexColor("#FFFFFF")
    GOLD   = colors.HexColor("#CC9F66")
    GOLD_D = colors.HexColor("#a07840")   # darker gold for subtle accents
    WHITE_D = colors.Color(1, 1, 1, alpha=0.55)

    # ── Background ──────────────────────────────────────────────────────────
    c.setFillColor(DARK)
    c.rect(0, 0, page_w, page_h, fill=1, stroke=0)

    # Subtle gradient effect — lighter teal band in centre
    c.setFillColor(MID)
    c.rect(0, page_h * 0.25, page_w, page_h * 0.5, fill=1, stroke=0)
    # Re-draw dark over it to make the teal very subtle
    c.setFillColor(colors.Color(0.004, 0.192, 0.251, alpha=0.82))
    c.rect(0, page_h * 0.25, page_w, page_h * 0.5, fill=1, stroke=0)

    # ── Outer border (gold) ──────────────────────────────────────────────────
    c.setStrokeColor(GOLD)
    c.setLineWidth(7)
    c.rect(18, 18, page_w - 36, page_h - 36, fill=0, stroke=1)

    # ── Inner border (mid-teal) ──────────────────────────────────────────────
    c.setStrokeColor(MID)
    c.setLineWidth(1.5)
    c.rect(30, 30, page_w - 60, page_h - 60, fill=0, stroke=1)

    # ── Header band ─────────────────────────────────────────────────────────
    c.setFillColor(MID)
    c.rect(30, page_h - 108, page_w - 60, 78, fill=1, stroke=0)
    # Gold accent line below header
    c.setStrokeColor(GOLD)
    c.setLineWidth(2)
    c.line(30, page_h - 108, page_w - 30, page_h - 108)

    # ── Org initials badge in header ─────────────────────────────────────────
    c.setFont("Helvetica-Bold", 28)
    c.setFillColor(GOLD)
    c.drawString(52, page_h - 88, "[NL]")

    # ── Main title ───────────────────────────────────────────────────────────
    c.setFont("Helvetica-Bold", 32)
    c.setFillColor(WHITE)
    c.drawCentredString(page_w / 2, page_h - 82, "CERTIFICATE OF COMPLETION")

    # ── Subtitle ─────────────────────────────────────────────────────────────
    c.setFont("Helvetica", 15)
    c.setFillColor(GOLD)
    c.drawCentredString(page_w / 2, page_h - 102, "Phishing Awareness Training Program")

    # ── Divider line ─────────────────────────────────────────────────────────
    c.setStrokeColor(GOLD)
    c.setLineWidth(1.5)
    c.line(80, page_h - 128, page_w - 80, page_h - 128)

    # ── "This certifies that" ────────────────────────────────────────────────
    c.setFont("Helvetica-Oblique", 15)
    c.setFillColor(colors.Color(1, 1, 1, alpha=0.6))
    c.drawCentredString(page_w / 2, page_h - 162, "This certifies that")

    # ── Recipient name ────────────────────────────────────────────────────────
    c.setFont("Helvetica-Bold", 38)
    c.setFillColor(WHITE)
    c.drawCentredString(page_w / 2, page_h - 218, user_name)

    # Name underline (gold)
    name_w = c.stringWidth(user_name, "Helvetica-Bold", 38)
    c.setStrokeColor(GOLD)
    c.setLineWidth(2)
    c.line(page_w / 2 - name_w / 2 - 12, page_h - 230,
           page_w / 2 + name_w / 2 + 12, page_h - 230)

    # ── Body text ────────────────────────────────────────────────────────────
    c.setFont("Helvetica", 14)
    c.setFillColor(colors.Color(1, 1, 1, alpha=0.78))
    c.drawCentredString(page_w / 2, page_h - 262,
                        "has successfully completed the Phishing Awareness Lab")
    c.drawCentredString(page_w / 2, page_h - 282,
                        "and demonstrated knowledge of cybersecurity best practices.")

    # ── Score badge ──────────────────────────────────────────────────────────
    badge_x, badge_y, badge_w, badge_h = page_w / 2 - 85, page_h - 345, 170, 44
    c.setFillColor(colors.Color(0.004, 0.192, 0.251, alpha=0.7))
    c.roundRect(badge_x, badge_y, badge_w, badge_h, 8, fill=1, stroke=0)
    c.setStrokeColor(GOLD)
    c.setLineWidth(1.8)
    c.roundRect(badge_x, badge_y, badge_w, badge_h, 8, fill=0, stroke=1)
    c.setFont("Helvetica-Bold", 18)
    c.setFillColor(GOLD)
    c.drawCentredString(page_w / 2, badge_y + 14, f"Score: {score}/100")

    # ── Date ─────────────────────────────────────────────────────────────────
    c.setFont("Helvetica", 12)
    c.setFillColor(colors.Color(1, 1, 1, alpha=0.45))
    c.drawCentredString(page_w / 2, page_h - 378, f"Date of Completion: {date}")

    # ── Footer divider ────────────────────────────────────────────────────────
    c.setStrokeColor(GOLD)
    c.setLineWidth(1.5)
    c.line(80, 92, page_w - 80, 92)

    # ── Organisation ─────────────────────────────────────────────────────────
    c.setFont("Helvetica-Bold", 14)
    c.setFillColor(GOLD)
    c.drawCentredString(page_w / 2, 70, "Newslight Kenya")
    c.setFont("Helvetica", 11)
    c.setFillColor(colors.Color(1, 1, 1, alpha=0.45))
    c.drawCentredString(page_w / 2, 54, "Cybersecurity Awareness Initiative")

    # ── Stamp circle (right side) ─────────────────────────────────────────────
    stamp_cx, stamp_cy = page_w - 112, 150
    c.setFillColor(MID)
    c.circle(stamp_cx, stamp_cy, 62, fill=1, stroke=0)
    c.setStrokeColor(GOLD)
    c.setLineWidth(2.5)
    c.circle(stamp_cx, stamp_cy, 62, fill=0, stroke=1)
    c.setStrokeColor(colors.Color(0.8, 0.62, 0.4, alpha=0.4))
    c.setLineWidth(1)
    c.circle(stamp_cx, stamp_cy, 54, fill=0, stroke=1)
    c.setFillColor(WHITE)
    c.setFont("Helvetica-Bold", 9)
    c.drawCentredString(stamp_cx, stamp_cy + 22, "PHISHING")
    c.drawCentredString(stamp_cx, stamp_cy + 10, "AWARENESS")
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(GOLD)
    c.drawCentredString(stamp_cx, stamp_cy - 4, "CERTIFIED")
    c.setFont("Helvetica", 8)
    c.setFillColor(colors.Color(1, 1, 1, alpha=0.5))
    c.drawCentredString(stamp_cx, stamp_cy - 18, str(datetime.now().year))

    c.save()
    buf.seek(0)
    return buf.getvalue()
