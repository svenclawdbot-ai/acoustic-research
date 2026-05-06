#!/usr/bin/env python3
"""
TurboQuant One-Page Executive Summary
Investor-focused single-page PDF
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor, white, black
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

ws = "/home/james/.openclaw/workspace"
output_path = f"{ws}/TurboQuant_One_Page_Summary.pdf"

def draw_rounded_rect(c, x, y, w, h, r, fill_color, stroke_color=None, stroke_width=0):
    """Draw a rounded rectangle"""
    c.setFillColor(fill_color)
    if stroke_color and stroke_width:
        c.setStrokeColor(stroke_color)
        c.setLineWidth(stroke_width)
    else:
        c.setStrokeColor(fill_color)
    
    path = c.beginPath()
    path.moveTo(x + r, y)
    path.lineTo(x + w - r, y)
    path.curveTo(x + w, y, x + w, y, x + w, y + r)
    path.lineTo(x + w, y + h - r)
    path.curveTo(x + w, y + h, x + w, y + h, x + w - r, y + h)
    path.lineTo(x + r, y + h)
    path.curveTo(x, y + h, x, y + h, x, y + h - r)
    path.lineTo(x, y + r)
    path.curveTo(x, y, x, y, x + r, y)
    path.close()
    c.drawPath(path, fill=1, stroke=1 if stroke_color else 0)

def draw_metric_box(c, x, y, w, h, number, label, color):
    """Draw a metric highlight box"""
    draw_rounded_rect(c, x, y, w, h, 3*mm, HexColor("#F8F9FA"), HexColor("#E9ECEF"), 0.5)
    c.setFillColor(color)
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(x + w/2, y + h - 8*mm, number)
    c.setFillColor(HexColor("#495057"))
    c.setFont("Helvetica", 8)
    # Wrap label text
    words = label.split()
    lines = []
    current = ""
    for word in words:
        if c.stringWidth(current + " " + word if current else word, "Helvetica", 8) < w - 4*mm:
            current = current + " " + word if current else word
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    
    ly = y + h - 13*mm
    for line in lines:
        c.drawCentredString(x + w/2, ly, line)
        ly -= 3.5*mm

c = canvas.Canvas(output_path, pagesize=A4)
width, height = A4

# Background
c.setFillColor(white)
c.rect(0, 0, width, height, fill=1, stroke=0)

# === HEADER BAR ===
c.setFillColor(HexColor("#1A237E"))
c.rect(0, height - 35*mm, width, 35*mm, fill=1, stroke=0)

# Logo badge
c.setFillColor(HexColor("#FF6B35"))
c.circle(15*mm, height - 17.5*mm, 6*mm, fill=1, stroke=0)
c.setFillColor(white)
c.setFont("Helvetica-Bold", 12)
c.drawCentredString(15*mm, height - 20*mm, "TQ")

# Title
c.setFillColor(white)
c.setFont("Helvetica-Bold", 24)
c.drawString(25*mm, height - 20*mm, "TURBOQUANT")
c.setFont("Helvetica", 11)
c.drawString(25*mm, height - 26*mm, "Open-Hardware Ultrasound Platform for Shear Wave Elastography")

# Tagline right
c.setFillColor(HexColor("#00C7B7"))
c.setFont("Helvetica-Bold", 10)
c.drawRightString(width - 10*mm, height - 17*mm, "SEED ROUND")
c.setFillColor(white)
c.setFont("Helvetica", 9)
c.drawRightString(width - 10*mm, height - 22*mm, "£75,000  |  20% Equity  |  6-Month Runway")

# === THE PROBLEM ===
y = height - 55*mm
section_h = 18*mm

draw_rounded_rect(c, 10*mm, y - section_h, width - 20*mm, section_h, 2*mm, HexColor("#FFF3E0"), HexColor("#FF6B35"), 1)
c.setFillColor(HexColor("#FF6B35"))
c.setFont("Helvetica-Bold", 9)
c.drawString(14*mm, y - 5*mm, "THE PROBLEM")
c.setFillColor(HexColor("#333333"))
c.setFont("Helvetica", 9)
c.drawString(14*mm, y - 11*mm, "1.5 billion people at risk of chronic liver disease. Biopsy is invasive. Commercial elastography systems cost £30K–£80K and are closed, inflexible,")
c.drawString(14*mm, y - 15.5*mm, "single-point devices. No open-source alternative exists with validated physics for clinical decision-making.")

# === KEY METRICS ROW ===
y = height - 82*mm
metric_w = (width - 28*mm) / 4
metric_h = 22*mm

metrics = [
    ("£50", "BOM cost per board", HexColor("#1A237E")),
    ("£50K+", "Commercial competitor price", HexColor("#FF6B35")),
    ("8", "Channels, spatial mapping", HexColor("#0096C7")),
    ("$680M", "SAM: portable elastography", HexColor("#00C7B7")),
]

for i, (num, label, color) in enumerate(metrics):
    x = 10*mm + i * (metric_w + 2.67*mm)
    draw_metric_box(c, x, y - metric_h, metric_w, metric_h, num, label, color)

# === THE SOLUTION ===
y = height - 112*mm
section_h = 22*mm

draw_rounded_rect(c, 10*mm, y - section_h, width - 20*mm, section_h, 2*mm, HexColor("#E3F2FD"), HexColor("#1A237E"), 1)
c.setFillColor(HexColor("#1A237E"))
c.setFont("Helvetica-Bold", 9)
c.drawString(14*mm, y - 5*mm, "THE SOLUTION")
c.setFillColor(HexColor("#333333"))
c.setFont("Helvetica", 9)
c.drawString(14*mm, y - 11*mm, "TurboQuant V5 is an open-hardware, 8-channel ultrasound acquisition platform integrating ±100V HV pulser, T/R switching, analog MUX, and")
c.drawString(14*mm, y - 15.5*mm, "low-noise amplifiers on a single 100×80 mm PCB. Built on the Red Pitaya SDR platform. Total BOM under £50. Peer-review-ready Bayesian")
c.drawString(14*mm, y - 20*mm, "framework for viscoelastic parameter estimation — the first open system with rigorously validated physics for clinical elastography.")

# === TWO COLUMN LAYOUT ===
left_x = 10*mm
right_x = width/2 + 5*mm
col_w = width/2 - 15*mm
y = height - 142*mm

# LEFT: TRACTION / MILESTONES
draw_rounded_rect(c, left_x, y - 38*mm, col_w, 38*mm, 2*mm, HexColor("#F8F9FA"), HexColor("#E9ECEF"), 0.5)
c.setFillColor(HexColor("#1A237E"))
c.setFont("Helvetica-Bold", 9)
c.drawString(left_x + 4*mm, y - 5*mm, "TRACTION & MILESTONES")

c.setFillColor(HexColor("#333333"))
c.setFont("Helvetica-Bold", 8)
c.drawString(left_x + 4*mm, y - 11*mm, "Completed:")
c.setFont("Helvetica", 8)
milestones_done = [
    "• 5 hardware iterations (V1→V5), schematic-complete, ERC clean",
    "• Published-ready Bayesian MCMC framework for viscoelastic inversion",
    "• 2D FDTD simulation + dispersion validation (30% → <2% error)",
    "• Component selection validated: DG408, IRF830, OPA1641, 74HCT595",
    "• 15+ open-source contributors on GitHub",
]
my = y - 15*mm
for m in milestones_done:
    c.drawString(left_x + 4*mm, my, m)
    my -= 4*mm

c.setFont("Helvetica-Bold", 8)
c.drawString(left_x + 4*mm, my - 1*mm, "Next 6 months:")
c.setFont("Helvetica", 8)
my -= 5*mm
next_steps = [
    "• 20-unit prototype batch + bench validation",
    "• Phantom studies (ATS 539 liver phantom)",
    "• IEEE/PMB journal submission + Series A",
]
for m in next_steps:
    c.drawString(left_x + 4*mm, my, m)
    my -= 4*mm

# RIGHT: MARKET & REVENUE
draw_rounded_rect(c, right_x, y - 38*mm, col_w, 38*mm, 2*mm, HexColor("#F8F9FA"), HexColor("#E9ECEF"), 0.5)
c.setFillColor(HexColor("#1A237E"))
c.setFont("Helvetica-Bold", 9)
c.drawString(right_x + 4*mm, y - 5*mm, "MARKET & REVENUE MODEL")

c.setFillColor(HexColor("#333333"))
c.setFont("Helvetica-Bold", 8)
c.drawString(right_x + 4*mm, y - 11*mm, "Segments:")
c.setFont("Helvetica", 8)
segments = [
    "• Research kits: £299 (BOM £50) — universities, NDE contractors",
    "• Clinical tier: £899 + £199/year service — early adopters",
    "• SaaS/API: £99/year — advanced DSP, cloud analytics, ML models",
]
my = y - 15*mm
for s in segments:
    c.drawString(right_x + 4*mm, my, s)
    my -= 4*mm

c.setFont("Helvetica-Bold", 8)
c.drawString(right_x + 4*mm, my - 1*mm, "Market sizing (Year 3):")
c.setFont("Helvetica", 8)
my -= 5*mm
market_data = [
    "• TAM: $4.2B  |  SAM: $680M  |  SOM: $85M",
    "• Target: 2,000 units + 500 service contracts",
    "• Revenue target: £1.2M, 45% blended margin",
]
for s in market_data:
    c.drawString(right_x + 4*mm, my, s)
    my -= 4*mm

# === COMPETITIVE LANDSCAPE ===
y = height - 188*mm
section_h = 16*mm

draw_rounded_rect(c, 10*mm, y - section_h, width - 20*mm, section_h, 2*mm, HexColor("#FFF8E1"), HexColor("#FFC107"), 0.5)
c.setFillColor(HexColor("#FF8F00"))
c.setFont("Helvetica-Bold", 9)
c.drawString(14*mm, y - 5*mm, "COMPETITIVE POSITION")
c.setFillColor(HexColor("#333333"))
c.setFont("Helvetica", 8)
c.drawString(14*mm, y - 11*mm, "FibroScan (£30K+, closed, single-point)  |  Siemens ACUSON (£50K+, closed ecosystem)  |  Supersonic Aixplorer (£80K+, research-only)")
c.drawString(14*mm, y - 15*mm, "TurboQuant: the only platform competing on cost (£50 BOM), openness (GitHub + open API), AND scientific rigor (validated Bayesian physics).")

# === TEAM & ASK ===
y = height - 214*mm

# Left: Team
team_h = 22*mm
draw_rounded_rect(c, 10*mm, y - team_h, col_w, team_h, 2*mm, HexColor("#E8F5E9"), HexColor("#4CAF50"), 0.5)
c.setFillColor(HexColor("#2E7D32"))
c.setFont("Helvetica-Bold", 9)
c.drawString(14*mm, y - 5*mm, "THE TEAM")
c.setFillColor(HexColor("#333333"))
c.setFont("Helvetica", 8)
c.drawString(14*mm, y - 11*mm, "Founder/Lead Engineer: 5 iterations V1→V5, FPGA, ultrasound hardware, embedded systems")
c.drawString(14*mm, y - 15*mm, "Research: Bayesian inverse problem specialist — MCMC, FDTD, phantom protocols")
c.drawString(14*mm, y - 19*mm, "Advisors: NHS hepatologist (regulatory pathway) + MedTech entrepreneur (Siemens exit, FDA 510(k))")

# Right: The Ask
draw_rounded_rect(c, right_x, y - team_h, col_w, team_h, 2*mm, HexColor("#1A237E"), HexColor("#1A237E"), 1)
c.setFillColor(HexColor("#00C7B7"))
c.setFont("Helvetica-Bold", 9)
c.drawString(right_x + 4*mm, y - 5*mm, "THE ASK")
c.setFillColor(white)
c.setFont("Helvetica-Bold", 14)
c.drawString(right_x + 4*mm, y - 12*mm, "£75,000")
c.setFont("Helvetica", 9)
c.drawString(right_x + 4*mm, y - 17*mm, "20% equity  |  6-month runway")
c.setFont("Helvetica", 8)
c.drawString(right_x + 4*mm, y - 21*mm, "→ 20 prototypes  →  phantom validation  →  journal publication  →  Series A")

# === FOOTER ===
c.setFillColor(HexColor("#666666"))
c.setFont("Helvetica", 7)
c.drawCentredString(width/2, 8*mm, "TurboQuant  |  james@turboquant.org  |  github.com/svenclawdbot-ai/acoustic-research  |  May 2026")

# Save
c.showPage()
c.save()
print(f"✅ One-page summary saved: {output_path}")
