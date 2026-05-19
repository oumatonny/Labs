"""
Certificate generator for the Phishing Awareness Lab.
Produces a landscape A4 PDF with a custom multi-layer design.

Palette:
  #013140  DARK  — primary background
  #026281  MID   — surfaces / header band
  #CC9F66  GOLD  — accents, borders, headings
  #FFFFFF  WHITE — body text
"""
import io
import hashlib
from datetime import datetime

from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.pdfgen import canvas as rl_canvas


# ── Colour helpers ────────────────────────────────────────────────────────────

DARK  = colors.HexColor("#013140")
MID   = colors.HexColor("#026281")
GOLD  = colors.HexColor("#CC9F66")
WHITE = colors.HexColor("#FFFFFF")


def _rgba(r, g, b, a):
    return colors.Color(r, g, b, alpha=a)


GOLD_20  = _rgba(0.800, 0.624, 0.400, 0.20)
GOLD_35  = _rgba(0.800, 0.624, 0.400, 0.35)
GOLD_50  = _rgba(0.800, 0.624, 0.400, 0.50)
MID_25   = _rgba(0.010, 0.384, 0.506, 0.25)
MID_50   = _rgba(0.010, 0.384, 0.506, 0.50)
WHITE_30 = _rgba(1, 1, 1, 0.30)
WHITE_55 = _rgba(1, 1, 1, 0.55)
WHITE_75 = _rgba(1, 1, 1, 0.75)


# ── Drawing primitives ────────────────────────────────────────────────────────

def _diamond(c, cx, cy, half, color=None):
    """Filled diamond centred at (cx, cy)."""
    if color:
        c.setFillColor(color)
    path = c.beginPath()
    path.moveTo(cx,        cy + half)
    path.lineTo(cx + half, cy)
    path.lineTo(cx,        cy - half)
    path.lineTo(cx - half, cy)
    path.close()
    c.drawPath(path, fill=1, stroke=0)


def _corner_bracket(c, x, y, size, dx, dy):
    """L-shaped corner bracket.  dx / dy = ±1 for direction."""
    c.line(x, y, x + dx * size, y)
    c.line(x, y, x, y + dy * size)


def _divider(c, cx, y, half_width):
    """Decorative line with a diamond centre and two flanking dots."""
    c.setStrokeColor(GOLD_35)
    c.setLineWidth(0.7)
    c.line(cx - half_width, y, cx - 18, y)
    c.line(cx + 18, y, cx + half_width, y)
    _diamond(c, cx, y, 8, GOLD)
    _diamond(c, cx - 44, y, 3, GOLD_50)
    _diamond(c, cx + 44, y, 3, GOLD_50)


def _shield(c, cx, cy, w, h, fill_col, stroke_col, line_w=1.5):
    """Heraldic shield shape centred horizontally at cx, vertically at cy."""
    hw = w / 2
    path = c.beginPath()
    path.moveTo(cx - hw, cy + h * 0.50)
    path.lineTo(cx + hw, cy + h * 0.50)
    path.lineTo(cx + hw, cy - h * 0.05)
    path.curveTo(cx + hw,      cy - h * 0.52,
                 cx + hw * 0.3, cy - h * 0.62,
                 cx,            cy - h * 0.52)
    path.curveTo(cx - hw * 0.3, cy - h * 0.62,
                 cx - hw,      cy - h * 0.52,
                 cx - hw,      cy - h * 0.05)
    path.lineTo(cx - hw, cy + h * 0.50)
    path.close()
    c.setFillColor(fill_col)
    c.setStrokeColor(stroke_col)
    c.setLineWidth(line_w)
    c.drawPath(path, fill=1, stroke=1)


def _gradient_background(c, W, H):
    """Simulate a subtle radial gradient via layered rectangles."""
    c.setFillColor(DARK)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    # Horizontal bands getting slightly lighter in the middle
    bands = 14
    for i in range(bands):
        t = abs(i - bands / 2) / (bands / 2)         # 0 at centre, 1 at edges
        alpha = 0.00 + (1 - t) * 0.07
        c.setFillColor(_rgba(0.010, 0.384, 0.506, alpha))
        c.rect(0, H * i / bands, W, H / bands + 1, fill=1, stroke=0)


def _corner_glows(c, W, H):
    """Soft golden glow at each corner."""
    for ox, oy, r_base in [(0, 0, 190), (W, 0, 160), (0, H, 170), (W, H, 200)]:
        for frac, alpha in [(1.0, 0.04), (0.65, 0.06), (0.35, 0.05)]:
            c.setFillColor(_rgba(0.800, 0.624, 0.400, alpha))
            c.circle(ox, oy, r_base * frac, fill=1, stroke=0)


def _watermark(c, W, H):
    """Very faint diagonal 'CERTIFIED' watermark in the background."""
    c.saveState()
    c.translate(W / 2, H / 2)
    c.rotate(24)
    c.setFillColor(_rgba(0.800, 0.624, 0.400, 0.032))
    c.setFont("Helvetica-Bold", 100)
    c.drawCentredString(0, 0, "CERTIFIED")
    c.restoreState()


# ── Main generator ────────────────────────────────────────────────────────────

def generate_certificate(user_name: str, score: int, date: str = None) -> bytes:
    """
    Return PDF bytes for a phishing-awareness completion certificate.
    Suitable for use with st.download_button(data=..., mime='application/pdf').
    """
    if not date:
        date = datetime.now().strftime("%B %d, %Y")
    user_name = (user_name or "Participant").strip()
    cert_id = "NL-" + hashlib.md5(
        f"{user_name}{score}{date}".encode()
    ).hexdigest()[:8].upper()

    buf = io.BytesIO()
    W, H = landscape(A4)      # 841.89 × 595.28 pts
    cx = W / 2

    c = rl_canvas.Canvas(buf, pagesize=landscape(A4))

    # ── Layer 0: background ───────────────────────────────────────────────────
    _gradient_background(c, W, H)
    _corner_glows(c, W, H)
    _watermark(c, W, H)

    # ── Layer 1: outer gold frame + inner teal frame ──────────────────────────
    c.setStrokeColor(GOLD)
    c.setLineWidth(6.5)
    c.rect(12, 12, W - 24, H - 24, fill=0, stroke=1)

    c.setStrokeColor(MID)
    c.setLineWidth(1.2)
    c.rect(22, 22, W - 44, H - 44, fill=0, stroke=1)

    # ── Layer 2: corner bracket ornaments ─────────────────────────────────────
    c.setStrokeColor(GOLD)
    c.setLineWidth(2.2)
    c.setFillColor(GOLD)
    for (bx, by, dx, dy) in [(36, 36, 1, 1), (W-36, 36, -1, 1),
                              (36, H-36, 1, -1), (W-36, H-36, -1, -1)]:
        _corner_bracket(c, bx, by, 30, dx, dy)
        _diamond(c, bx, by, 4.5)

    # ── Layer 3: header band ──────────────────────────────────────────────────
    HDR_H   = 88
    HDR_BOT = H - 22 - HDR_H          # bottom y of header band

    c.setFillColor(MID)
    c.rect(22, HDR_BOT, W - 44, HDR_H, fill=1, stroke=0)

    # Left accent strip inside header
    c.setFillColor(MID_50)
    c.rect(22, HDR_BOT, 7, HDR_H, fill=1, stroke=0)

    # Gold line above header (top of band)
    c.setStrokeColor(GOLD)
    c.setLineWidth(2.5)
    c.line(22, H - 22, W - 22, H - 22)
    # Gold line below header
    c.setLineWidth(1.5)
    c.line(22, HDR_BOT, W - 22, HDR_BOT)

    # Small gold squares at band corners for depth
    sq = 5
    for (sx, sy) in [(22, HDR_BOT), (W-22-sq, HDR_BOT),
                     (22, H-22-sq), (W-22-sq, H-22-sq)]:
        c.setFillColor(GOLD)
        c.rect(sx, sy, sq, sq, fill=1, stroke=0)

    # ── Layer 4: shield logo in header ────────────────────────────────────────
    sh_cx = 70
    sh_cy = HDR_BOT + HDR_H / 2
    _shield(c, sh_cx, sh_cy, 46, 54, DARK, GOLD, 1.8)
    # Inner shield outline
    _shield(c, sh_cx, sh_cy, 32, 38,
            _rgba(0, 0, 0, 0), GOLD_35, 0.8)
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(GOLD)
    c.drawCentredString(sh_cx, sh_cy - 5, "NL")

    # ── Header text ───────────────────────────────────────────────────────────
    c.setFont("Helvetica-Bold", 29)
    c.setFillColor(WHITE)
    c.drawCentredString(cx, HDR_BOT + HDR_H - 34, "CERTIFICATE OF COMPLETION")

    c.setFont("Helvetica", 12.5)
    c.setFillColor(GOLD)
    c.drawCentredString(cx, HDR_BOT + 16,
                        "Phishing Awareness Training Program  ·  Newslight Kenya")

    # ── Decorative divider — top ──────────────────────────────────────────────
    DIV_TOP = HDR_BOT - 22
    _divider(c, cx, DIV_TOP, cx - 55)

    # ── "This certifies that" ─────────────────────────────────────────────────
    Y_CERT = DIV_TOP - 34
    c.setFont("Helvetica-Oblique", 12.5)
    c.setFillColor(WHITE_55)
    c.drawCentredString(cx, Y_CERT, "This certifies that")

    # ── Recipient name ────────────────────────────────────────────────────────
    Y_NAME = Y_CERT - 46
    c.setFont("Helvetica-Bold", 40)
    c.setFillColor(WHITE)
    c.drawCentredString(cx, Y_NAME, user_name)

    # Double underline beneath name
    nw = c.stringWidth(user_name, "Helvetica-Bold", 40)
    ul0 = cx - nw / 2 - 18
    ul1 = cx + nw / 2 + 18
    c.setStrokeColor(GOLD)
    c.setLineWidth(1.8)
    c.line(ul0, Y_NAME - 10, ul1, Y_NAME - 10)
    c.setStrokeColor(GOLD_20)
    c.setLineWidth(0.6)
    c.line(ul0 + 10, Y_NAME - 16, ul1 - 10, Y_NAME - 16)

    # ── Body text ─────────────────────────────────────────────────────────────
    Y_BODY = Y_NAME - 50
    c.setFont("Helvetica", 13)
    c.setFillColor(WHITE_75)
    c.drawCentredString(cx, Y_BODY,
                        "has successfully completed the Phishing Awareness Lab")
    c.drawCentredString(cx, Y_BODY - 20,
                        "and demonstrated knowledge of cybersecurity best practices")

    # ── Score + Status badges ─────────────────────────────────────────────────
    Y_BADGES = Y_BODY - 64
    BADGE_W, BADGE_H, BADGE_R = 132, 38, 7
    GAP = 16
    b1_x = cx - BADGE_W - GAP / 2
    b2_x = cx + GAP / 2

    for bx, label in [(b1_x, f"Score:  {score} / 100"), (b2_x, "Status:  PASSED")]:
        # Filled tinted bg
        c.setFillColor(MID_25)
        c.roundRect(bx, Y_BADGES, BADGE_W, BADGE_H, BADGE_R, fill=1, stroke=0)
        # Gold border
        c.setStrokeColor(GOLD)
        c.setLineWidth(1.3)
        c.roundRect(bx, Y_BADGES, BADGE_W, BADGE_H, BADGE_R, fill=0, stroke=1)
        # Top highlight line
        c.setStrokeColor(GOLD_50)
        c.setLineWidth(0.5)
        c.roundRect(bx + 2, Y_BADGES + 2, BADGE_W - 4, BADGE_H - 4,
                    BADGE_R - 1, fill=0, stroke=1)
        # Label
        c.setFont("Helvetica-Bold", 12.5)
        c.setFillColor(GOLD)
        c.drawCentredString(bx + BADGE_W / 2, Y_BADGES + 13, label)

    # ── Date ──────────────────────────────────────────────────────────────────
    Y_DATE = Y_BADGES - 28
    c.setFont("Helvetica", 10.5)
    c.setFillColor(WHITE_30)
    c.drawCentredString(cx, Y_DATE, f"Date of Completion:  {date}")

    # ── Decorative divider — bottom ───────────────────────────────────────────
    DIV_BOT = 115
    _divider(c, cx, DIV_BOT, cx - 55)

    # ── Footer — left: org + signature ────────────────────────────────────────
    c.setFont("Helvetica-Bold", 13)
    c.setFillColor(GOLD)
    c.drawString(48, 94, "Newslight Kenya")

    c.setFont("Helvetica", 10)
    c.setFillColor(WHITE_55)
    c.drawString(48, 78, "Cybersecurity Awareness Initiative")

    c.setStrokeColor(GOLD_35)
    c.setLineWidth(0.8)
    c.line(48, 68, 240, 68)

    c.setFont("Helvetica-Oblique", 9)
    c.setFillColor(WHITE_30)
    c.drawString(48, 54, "Authorised by Newslight Kenya")

    # ── Footer — centre: certificate ID ───────────────────────────────────────
    c.setFont("Helvetica", 8.5)
    c.setFillColor(WHITE_30)
    c.drawCentredString(cx, 84, f"Certificate ID:  {cert_id}")
    c.drawCentredString(cx, 68, "Verify at  newslight.co.ke/verify")

    # Tiny dot separators
    c.setFillColor(GOLD_35)
    _diamond(c, cx - 80, 76, 2)
    _diamond(c, cx + 80, 76, 2)

    # ── Footer — right: certified shield stamp ─────────────────────────────────
    ST_CX = W - 88
    ST_CY = 76
    # Outer shield
    _shield(c, ST_CX, ST_CY, 82, 94, MID, GOLD, 2.0)
    # Inner shield (outline only)
    _shield(c, ST_CX, ST_CY, 64, 74,
            _rgba(0, 0, 0, 0), GOLD_35, 0.8)
    # Shield text
    c.setFont("Helvetica-Bold", 8)
    c.setFillColor(WHITE)
    c.drawCentredString(ST_CX, ST_CY + 26, "PHISHING")
    c.drawCentredString(ST_CX, ST_CY + 14, "AWARENESS")
    c.setFont("Helvetica-Bold", 10.5)
    c.setFillColor(GOLD)
    c.drawCentredString(ST_CX, ST_CY + 1, "CERTIFIED")
    c.setFont("Helvetica", 8)
    c.setFillColor(WHITE_55)
    c.drawCentredString(ST_CX, ST_CY - 13, str(datetime.now().year))
    # Star above shield text
    c.setFillColor(GOLD)
    _diamond(c, ST_CX, ST_CY + 38, 4)

    c.save()
    buf.seek(0)
    return buf.getvalue()
