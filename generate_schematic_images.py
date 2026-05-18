import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import os

# Create output directory
os.makedirs('/home/james/.openclaw/canvas/turboquant_v5_schematics', exist_ok=True)

# Style settings
plt.rcParams['font.size'] = 7
plt.rcParams['font.family'] = 'monospace'

def draw_box(ax, x, y, w, h, label, color='#e0e0e0', text_color='black', fontsize=7, bold=False):
    """Draw a component box."""
    rect = patches.FancyBboxPatch((x-w/2, y-h/2), w, h,
                                    boxstyle="round,pad=0.02,rounding_size=0.5",
                                    facecolor=color, edgecolor='black', linewidth=1)
    ax.add_patch(rect)
    weight = 'bold' if bold else 'normal'
    ax.text(x, y, label, ha='center', va='center', fontsize=fontsize,
            color=text_color, fontweight=weight, wrap=True)

def draw_pin(ax, x, y, label, side='left', color='black'):
    """Draw a pin label near a component."""
    offset = 2.5 if side == 'left' else -2.5
    ha = 'right' if side == 'left' else 'left'
    ax.text(x + offset, y, label, ha=ha, va='center', fontsize=5, color=color)

def draw_wire(ax, x1, y1, x2, y2, color='#1a5276', lw=1.5):
    """Draw a wire between two points."""
    ax.plot([x1, x2], [y1, y2], color=color, linewidth=lw, solid_capstyle='round')

def draw_bus(ax, x1, y1, x2, y2, color='#1a5276', lw=2.5):
    """Draw a thick bus wire."""
    ax.plot([x1, x2], [y1, y2], color=color, linewidth=lw, solid_capstyle='round')

def draw_label(ax, x, y, text, color='#1a5276', fontsize=7, ha='center', rotation=0):
    ax.text(x, y, text, ha=ha, va='center', fontsize=fontsize, color=color,
            rotation=rotation, fontweight='bold')

# ============================================================
# SHEET 1: ROOT / OVERVIEW
# ============================================================
fig, ax = plt.subplots(1, 1, figsize=(14, 10))
ax.set_xlim(0, 360)
ax.set_ylim(0, 180)
ax.set_aspect('equal')
ax.axis('off')
ax.set_title('TurboQuant V5 — ROOT SHEET (Overview)', fontsize=14, fontweight='bold', pad=10)

# Sheet boxes
draw_box(ax, 50, 55, 55, 45, 'POWER\nSUPPLIES', '#c8e6c9', bold=True, fontsize=9)
draw_box(ax, 135, 55, 70, 55, 'DIGITAL\nCONTROL\n(74HCT595 →\nBSS138 → GATE)', '#bbdefb', bold=True, fontsize=9)
draw_box(ax, 140, 130, 160, 65, 'ANALOG FRONTEND\n(T/R Bridge → DG408 → OPA1641)', '#ffcdd2', bold=True, fontsize=9)
draw_box(ax, 280, 130, 105, 65, 'TX SWITCH\n(TC4427 → IRF830)', '#ffe0b2', bold=True, fontsize=9)

# Connectors
draw_box(ax, 25, 130, 15, 15, 'J1\nE1\nGPIO', '#f5f5f5', fontsize=6)
draw_box(ax, 25, 160, 15, 10, 'J2\nTX_IN', '#f5f5f5', fontsize=6)
draw_box(ax, 240, 175, 15, 10, 'J11\nRX0', '#f5f5f5', fontsize=6)
draw_box(ax, 290, 175, 15, 10, 'J12\nRX1', '#f5f5f5', fontsize=6)

# Power distribution
for x in [50, 135, 140, 280]:
    draw_wire(ax, 50, 75, x, 75, color='#c0392b', lw=2)
draw_wire(ax, 50, 75, 50, 55, color='#c0392b', lw=2)
draw_label(ax, 30, 75, '+12V', color='#c0392b')

for x in [50, 135, 140]:
    draw_wire(ax, 50, 65, x, 65, color='#2980b9', lw=2)
draw_label(ax, 30, 65, '+5V', color='#2980b9')

for x in [50, 135, 140, 280]:
    draw_wire(ax, 50, 55, x, 55, color='#7f8c8d', lw=1.5)
draw_label(ax, 30, 55, 'GND', color='#7f8c8d')

# Digital → Analog control
draw_bus(ax, 170, 85, 170, 100, color='#2c3e50', lw=2)
draw_label(ax, 160, 92, 'MUX_A..EN\nGATE0..7', color='#2c3e50', fontsize=6)

# TX_BUS
draw_bus(ax, 220, 130, 220, 160, color='#e67e22', lw=2.5)
draw_label(ax, 210, 145, 'TX_BUS\n(±100V)', color='#e67e22', fontsize=7)

# RX paths
draw_wire(ax, 240, 170, 220, 170, color='#8e44ad', lw=1.5)
draw_wire(ax, 290, 170, 310, 170, color='#8e44ad', lw=1.5)
draw_label(ax, 255, 173, 'RX0_OUT', color='#8e44ad', fontsize=6)
draw_label(ax, 300, 173, 'RX1_OUT', color='#8e44ad', fontsize=6)

# E1 → Digital
draw_wire(ax, 32, 130, 32, 85, color='#27ae60', lw=1.5)
draw_wire(ax, 32, 85, 100, 85, color='#27ae60', lw=1.5)
draw_label(ax, 22, 105, 'SPI\nSER/SRCLK/\nRCLK/OE', color='#27ae60', fontsize=5)

plt.tight_layout()
plt.savefig('/home/james/.openclaw/canvas/turboquant_v5_schematics/01_root_overview.png',
            dpi=200, bbox_inches='tight', facecolor='white')
plt.close()

# ============================================================
# SHEET 2: ANALOG FRONTEND
# ============================================================
fig, ax = plt.subplots(1, 1, figsize=(16, 12))
ax.set_xlim(0, 220)
ax.set_ylim(0, 120)
ax.set_aspect('equal')
ax.axis('off')
ax.set_title('TurboQuant V5 — ANALOG FRONTEND Sheet', fontsize=14, fontweight='bold', pad=10)

# Title annotation
ax.text(110, 118, 'T/R Bridge → DG408 MUX → OPA1641 LNA (×2 channels)',
        ha='center', fontsize=9, style='italic', color='#555')

# --- LEFT: Hierarchical inputs ---
inputs = [
    (15, 108, '+5V', '#2980b9'),
    (15, 103, '+12V', '#c0392b'),
    (15, 98, 'GND', '#7f8c8d'),
    (15, 90, 'MUX_A', '#2c3e50'),
    (15, 85, 'MUX_B', '#2c3e50'),
    (15, 80, 'MUX_C', '#2c3e50'),
    (15, 75, 'MUX_EN', '#2c3e50'),
    (15, 65, 'TX_BUS', '#e67e22'),
]
for x, y, label, color in inputs:
    draw_label(ax, x, y, label, color=color, ha='left', fontsize=7)
    draw_wire(ax, x+10, y, 40, y, color=color, lw=1)

# --- RIGHT: Outputs ---
draw_label(ax, 205, 95, 'RX0_OUT', color='#8e44ad', ha='right')
draw_wire(ax, 190, 95, 205, 95, color='#8e44ad', lw=1.5)
draw_label(ax, 205, 50, 'RX1_OUT', color='#8e44ad', ha='right')
draw_wire(ax, 190, 50, 205, 50, color='#8e44ad', lw=1.5)

# Right side CH0-CH7
for n in range(8):
    y = 110 - n * 7.5
    draw_label(ax, 205, y, f'CH{n}', color='#555', ha='right', fontsize=6)

# --- T/R BRIDGE (8 channels, 4 diodes each) ---
for ch in range(8):
    y = 110 - ch * 7.5
    # T/R bridge box
    draw_box(ax, 55, y, 20, 5, f'TR{ch}', '#fff3e0', fontsize=5)
    # 4 diodes inside (mini)
    for d in range(4):
        dx = 48 + d * 3.5
        tiny = patches.Rectangle((dx-0.8, y-1.5), 1.6, 3,
                                  facecolor='#ffcc80', edgecolor='#e65100', linewidth=0.5)
        ax.add_patch(tiny)
    # Bias network
    draw_box(ax, 40, y, 8, 3, f'Z{ch}\n5V1', '#e3f2fd', fontsize=4)
    draw_box(ax, 32, y, 6, 3, '1k', '#e8f5e9', fontsize=4)
    draw_box(ax, 32, y-3, 6, 3, '100k', '#e8f5e9', fontsize=4)
    # TX_BUS feed
    draw_wire(ax, 40, y, 55, y, color='#e67e22', lw=1)
    # CH output
    draw_wire(ax, 65, y, 80, y, color='#555', lw=1)
    draw_wire(ax, 80, y, 80, y, color='#555', lw=1)

# --- DG408 MUXes ---
# U1: channels 0-3 → RX0
draw_box(ax, 110, 95, 25, 35, 'U1\nDG408\n(CH0-3)', '#ffccbc', bold=True, fontsize=8)
for n in range(4):
    y = 108 - n * 7.5
    draw_wire(ax, 80, y, 97, y, color='#555', lw=1)
    draw_wire(ax, 97, y, 97, 108 - n*8.75, color='#555', lw=1)
    draw_wire(ax, 97, 108 - n*8.75, 97, 108 - n*8.75, color='#555', lw=1)
# U1 pins
for pin_y, pin_name in [(108, 'S1'), (100, 'S2'), (92, 'S3'), (84, 'S4'),
                         (108, 'V+'), (84, 'GND'), (97, 'EN'), (92, 'A'), (88, 'B'), (84, 'C')]:
    pass  # simplified

# U2: channels 4-7 → RX1
draw_box(ax, 110, 50, 25, 35, 'U2\nDG408\n(CH4-7)', '#ffccbc', bold=True, fontsize=8)
for n in range(4, 8):
    y = 110 - n * 7.5
    draw_wire(ax, 80, y, 97, y, color='#555', lw=1)
    draw_wire(ax, 97, y, 97, 62 - (n-4)*8.75, color='#555', lw=1)

# MUX control lines
for n, (label, y) in enumerate([('MUX_A', 90), ('MUX_B', 85), ('MUX_C', 80), ('MUX_EN', 75)]):
    draw_wire(ax, 40, y, 110, y, color='#2c3e50', lw=1.5)

# MUX outputs to LNA
draw_wire(ax, 123, 95, 140, 95, color='#8e44ad', lw=1.5)
draw_wire(ax, 123, 50, 140, 50, color='#8e44ad', lw=1.5)

# --- OPA1641 LNAs ---
# U3: RX0 LNA
draw_box(ax, 155, 95, 20, 25, 'U3\nOPA1641\nGain=10', '#c8e6c9', bold=True, fontsize=8)
draw_wire(ax, 140, 95, 145, 95, color='#8e44ad', lw=1.5)
draw_wire(ax, 165, 95, 175, 95, color='#8e44ad', lw=1.5)
# Feedback network
draw_box(ax, 175, 90, 8, 4, 'R6\n10k', '#e8f5e9', fontsize=5)
draw_box(ax, 160, 85, 8, 4, 'R5\n1k', '#e8f5e9', fontsize=5)
draw_wire(ax, 175, 92, 160, 92, color='#555', lw=0.8)
draw_wire(ax, 160, 87, 145, 87, color='#555', lw=0.8)
# Power
draw_wire(ax, 155, 110, 155, 108, color='#2980b9', lw=1)
draw_wire(ax, 155, 80, 155, 82, color='#7f8c8d', lw=1)

# U4: RX1 LNA
draw_box(ax, 155, 50, 20, 25, 'U4\nOPA1641\nGain=10', '#c8e6c9', bold=True, fontsize=8)
draw_wire(ax, 140, 50, 145, 50, color='#8e44ad', lw=1.5)
draw_wire(ax, 165, 50, 175, 50, color='#8e44ad', lw=1.5)
# Feedback
draw_box(ax, 175, 45, 8, 4, 'R32\n10k', '#e8f5e9', fontsize=5)
draw_box(ax, 160, 40, 8, 4, 'R31\n1k', '#e8f5e9', fontsize=5)
# Power
draw_wire(ax, 155, 65, 155, 62, color='#2980b9', lw=1)
draw_wire(ax, 155, 35, 155, 37, color='#7f8c8d', lw=1)

# Power rails (horizontal)
draw_bus(ax, 20, 108, 200, 108, color='#2980b9', lw=2)
draw_bus(ax, 20, 103, 200, 103, color='#c0392b', lw=2)
draw_bus(ax, 20, 98, 200, 98, color='#7f8c8d', lw=2)

# TX_BUS rail
for ch in range(8):
    y = 110 - ch * 7.5
    draw_wire(ax, 15, 65, 48, 65, color='#e67e22', lw=2)
    draw_wire(ax, 48, 65, 48, y, color='#e67e22', lw=1)

plt.tight_layout()
plt.savefig('/home/james/.openclaw/canvas/turboquant_v5_schematics/02_analog_frontend.png',
            dpi=200, bbox_inches='tight', facecolor='white')
plt.close()

# ============================================================
# SHEET 3: DIGITAL CONTROL
# ============================================================
fig, ax = plt.subplots(1, 1, figsize=(14, 10))
ax.set_xlim(0, 200)
ax.set_ylim(0, 100)
ax.set_aspect('equal')
ax.axis('off')
ax.set_title('TurboQuant V5 — DIGITAL CONTROL Sheet', fontsize=14, fontweight='bold', pad=10)

# Inputs from root
ax.text(10, 95, 'FROM ROOT:', ha='left', fontsize=8, fontweight='bold', color='#555')
inputs = [
    (10, 85, '+5V', '#2980b9'),
    (10, 80, 'GND', '#7f8c8d'),
    (10, 70, 'SER', '#27ae60'),
    (10, 65, 'SRCLK', '#27ae60'),
    (10, 60, 'RCLK', '#27ae60'),
    (10, 55, '~OE', '#27ae60'),
    (10, 50, 'SRCLR', '#27ae60'),
]
for x, y, label, color in inputs:
    draw_label(ax, x, y, label, color=color, ha='left', fontsize=7)
    draw_wire(ax, x+10, y, 35, y, color=color, lw=1)

# J3 E1 connector
draw_box(ax, 45, 62, 18, 35, 'J3\nRP_E1\nGPIO', '#f5f5f5', fontsize=7)

# 74HCT595 shift register
draw_box(ax, 100, 62, 25, 35, 'U5\n74HCT595\n8-bit SR', '#bbdefb', bold=True, fontsize=8)

# SPI lines
for y in [70, 65, 60, 55, 50]:
    draw_wire(ax, 53, y, 87, y, color='#27ae60', lw=1.5)

# U5 outputs → BSS138 gates
for n in range(8):
    qy = 78 - n * 4.5
    gate_y = 78 - n * 4.5
    # Output from 74HCT595
    draw_wire(ax, 113, qy, 140, qy, color='#2c3e50', lw=1)
    # Gate resistor
    draw_box(ax, 145, qy, 6, 3, 'R', '#e8f5e9', fontsize=5)
    # BSS138
    draw_box(ax, 155, qy, 12, 6, f'Q{n+1}\nBSS138', '#fff9c4', fontsize=5)
    # Source to GND
    draw_wire(ax, 155, qy-3, 155, 20, color='#7f8c8d', lw=0.8)
    # Drain to GATE output
    draw_wire(ax, 161, qy, 180, qy, color='#e67e22', lw=1.5)
    # GATE label
    draw_label(ax, 190, qy, f'GATE{n}', color='#e67e22', ha='left', fontsize=6)

# Power rails
draw_bus(ax, 10, 85, 180, 85, color='#2980b9', lw=2)
draw_bus(ax, 10, 20, 180, 20, color='#7f8c8d', lw=2)

# VCC/GND for 74HCT595
draw_wire(ax, 100, 79, 100, 85, color='#2980b9', lw=1)
draw_wire(ax, 100, 45, 100, 20, color='#7f8c8d', lw=1)

plt.tight_layout()
plt.savefig('/home/james/.openclaw/canvas/turboquant_v5_schematics/03_digital_control.png',
            dpi=200, bbox_inches='tight', facecolor='white')
plt.close()

# ============================================================
# SHEET 4: TX SWITCH
# ============================================================
fig, ax = plt.subplots(1, 1, figsize=(14, 10))
ax.set_xlim(0, 220)
ax.set_ylim(0, 100)
ax.set_aspect('equal')
ax.axis('off')
ax.set_title('TurboQuant V5 — TX SWITCH Sheet', fontsize=14, fontweight='bold', pad=10)

# Inputs
ax.text(10, 95, 'FROM ROOT:', ha='left', fontsize=8, fontweight='bold', color='#555')
inputs = [
    (10, 85, '+12V', '#c0392b'),
    (10, 80, 'GND', '#7f8c8d'),
]
for x, y, label, color in inputs:
    draw_label(ax, x, y, label, color=color, ha='left', fontsize=7)
    draw_wire(ax, x+10, y, 35, y, color=color, lw=1)

# GATE0-7 inputs
for n in range(8):
    y = 75 - n * 5
    draw_label(ax, 10, y, f'GATE{n}', color='#e67e22', ha='left', fontsize=6)
    draw_wire(ax, 20, y, 35, y, color='#e67e22', lw=1)

# TC4427 gate drivers (4 chips, 2 channels each)
for drv in range(4):
    x = 55 + drv * 15
    y = 62
    draw_box(ax, x, y, 12, 30, f'U{drv+1}\nTC4427\n2-ch', '#ffe0b2', fontsize=6)
    # Decoupling cap
    draw_box(ax, x+8, y+18, 4, 4, '100n', '#e3f2fd', fontsize=4)
    # VCC/GND
    draw_wire(ax, x, y+15, x-10, y+15, color='#c0392b', lw=1)
    draw_wire(ax, x, y-15, x-10, y-15, color='#7f8c8d', lw=1)

# GATE lines from left to TC4427 inputs
for n in range(8):
    y = 75 - n * 5
    drv_x = 42 + (n // 2) * 15
    draw_wire(ax, 35, y, drv_x, y, color='#e67e22', lw=1)

# TC4427 outputs → IRF830 gates
for n in range(8):
    y = 75 - n * 5
    drv_x = 55 + (n // 2) * 15
    # Output A or B
    out_x = drv_x + 6 if (n % 2 == 0) else drv_x + 6
    draw_wire(ax, drv_x+6, y, 95, y, color='#e67e22', lw=1.5)

# IRF830 MOSFETs (8)
for n in range(8):
    y = 75 - n * 5
    draw_box(ax, 105, y, 15, 6, f'Q{n+1}\nIRF830', '#ffccbc', fontsize=5)
    # Gate connection
    draw_wire(ax, 95, y, 97, y, color='#e67e22', lw=1.5)
    # Source to GND
    draw_wire(ax, 105, y-3, 105, 15, color='#7f8c8d', lw=0.8)
    # Drain to TX_BUS
    draw_wire(ax, 113, y, 130, y, color='#c0392b', lw=2)

# TX_BUS (thick)
draw_bus(ax, 130, 50, 200, 50, color='#c0392b', lw=3)
draw_label(ax, 165, 55, 'TX_BUS (±100V pulse)', color='#c0392b', fontsize=8)

# TX_OUT connector
draw_box(ax, 200, 50, 12, 10, 'TX_OUT', '#f5f5f5', fontsize=6)

# Power rails
draw_bus(ax, 10, 85, 120, 85, color='#c0392b', lw=2)
draw_bus(ax, 10, 15, 120, 15, color='#7f8c8d', lw=2)

plt.tight_layout()
plt.savefig('/home/james/.openclaw/canvas/turboquant_v5_schematics/04_tx_switch.png',
            dpi=200, bbox_inches='tight', facecolor='white')
plt.close()

# ============================================================
# SHEET 5: POWER SUPPLIES
# ============================================================
fig, ax = plt.subplots(1, 1, figsize=(12, 8))
ax.set_xlim(0, 160)
ax.set_ylim(0, 80)
ax.set_aspect('equal')
ax.axis('off')
ax.set_title('TurboQuant V5 — POWER SUPPLIES Sheet', fontsize=14, fontweight='bold', pad=10)

# 12V input
draw_box(ax, 20, 65, 20, 10, 'J1\n12V IN', '#f5f5f5', fontsize=7)
draw_box(ax, 45, 65, 12, 8, 'F1\nPolyfuse\n1A', '#fff3e0', fontsize=6)
draw_box(ax, 65, 65, 12, 8, 'D1\nSchottky\nSS34', '#fff3e0', fontsize=6)

# LM7805
draw_box(ax, 90, 65, 20, 15, 'U1\nLM7805\nTO-220', '#c8e6c9', bold=True, fontsize=8)
# Input cap
draw_box(ax, 75, 55, 8, 5, 'C1\n100n', '#e3f2fd', fontsize=5)
draw_box(ax, 105, 55, 8, 5, 'C2\n10µ', '#e3f2fd', fontsize=5)

# AMS1117-3.3
draw_box(ax, 90, 35, 20, 15, 'U2\nAMS1117\nSOT-223', '#c8e6c9', bold=True, fontsize=8)
draw_box(ax, 75, 25, 8, 5, 'C3\n100n', '#e3f2fd', fontsize=5)
draw_box(ax, 105, 25, 8, 5, 'C4\n10µ', '#e3f2fd', fontsize=5)

# Wiring
draw_wire(ax, 30, 65, 30, 65, color='#c0392b', lw=2)
draw_wire(ax, 30, 65, 39, 65, color='#c0392b', lw=2)
draw_wire(ax, 51, 65, 59, 65, color='#c0392b', lw=2)
draw_wire(ax, 71, 65, 80, 65, color='#c0392b', lw=2)

# 5V output
draw_wire(ax, 100, 57, 100, 50, color='#2980b9', lw=2)
draw_label(ax, 115, 50, '+5V OUT', color='#2980b9', fontsize=7)

# 5V → 3.3V input
draw_wire(ax, 100, 50, 100, 42, color='#2980b9', lw=2)

# 3.3V output
draw_wire(ax, 100, 27, 100, 20, color='#2980b9', lw=2)
draw_label(ax, 115, 20, '+3.3V OUT', color='#2980b9', fontsize=7)

# GND rail
draw_bus(ax, 20, 15, 120, 15, color='#7f8c8d', lw=2)
draw_label(ax, 130, 15, 'GND', color='#7f8c8d', fontsize=7)

# GND connections
draw_wire(ax, 90, 57, 90, 15, color='#7f8c8d', lw=1)
draw_wire(ax, 90, 27, 90, 15, color='#7f8c8d', lw=1)

plt.tight_layout()
plt.savefig('/home/james/.openclaw/canvas/turboquant_v5_schematics/05_power_supplies.png',
            dpi=200, bbox_inches='tight', facecolor='white')
plt.close()

print("Schematic reference images generated successfully!")
print("Location: /home/james/.openclaw/canvas/turboquant_v5_schematics/")
print("\nFiles:")
for i in range(1, 6):
    fname = f'{i:02d}_*.png'
    print(f"  {fname}")
