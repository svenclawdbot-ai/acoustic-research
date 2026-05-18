import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import os

os.makedirs('/home/james/.openclaw/canvas/turboquant_v5_schematics', exist_ok=True)

plt.rcParams['font.size'] = 7
plt.rcParams['font.family'] = 'monospace'

def draw_box(ax, x, y, w, h, label, color='#e0e0e0', text_color='black', fontsize=7, bold=False, lw=1):
    rect = patches.FancyBboxPatch((x-w/2, y-h/2), w, h,
                                    boxstyle="round,pad=0.02,rounding_size=0.3",
                                    facecolor=color, edgecolor='black', linewidth=lw)
    ax.add_patch(rect)
    weight = 'bold' if bold else 'normal'
    ax.text(x, y, label, ha='center', va='center', fontsize=fontsize,
            color=text_color, fontweight=weight, wrap=True,
            linespacing=0.9)

def draw_pin(ax, x, y, label, side='left', color='black', fontsize=6):
    offset = 2.8 if side == 'left' else -2.8
    ha = 'right' if side == 'left' else 'left'
    ax.text(x + offset, y, label, ha=ha, va='center', fontsize=fontsize, color=color)

def draw_wire(ax, x1, y1, x2, y2, color='#1a5276', lw=1.2):
    ax.plot([x1, x2], [y1, y2], color=color, linewidth=lw, solid_capstyle='round')

def draw_l_wire(ax, x1, y1, x2, y2, color='#1a5276', lw=1.2):
    """L-shaped wire (horizontal then vertical or vice versa)."""
    mid_x = x2
    ax.plot([x1, mid_x], [y1, y1], color=color, linewidth=lw, solid_capstyle='round')
    ax.plot([mid_x, x2], [y1, y2], color=color, linewidth=lw, solid_capstyle='round')

def draw_bus(ax, x1, y1, x2, y2, color='#1a5276', lw=2.5):
    """Draw a thick bus wire."""
    ax.plot([x1, x2], [y1, y2], color=color, linewidth=lw, solid_capstyle='round')

def draw_label(ax, x, y, text, color='#1a5276', fontsize=7, ha='center', rotation=0):
    ax.text(x, y, text, ha=ha, va='center', fontsize=fontsize, color=color,
            rotation=rotation, fontweight='bold')

# ============================================================
# SHEET 1: ROOT / OVERVIEW
# ============================================================
fig, ax = plt.subplots(1, 1, figsize=(16, 11))
ax.set_xlim(0, 340)
ax.set_ylim(0, 170)
ax.set_aspect('equal')
ax.axis('off')
ax.set_title('TurboQuant V5 — ROOT SHEET (Overview)', fontsize=14, fontweight='bold', pad=10)

# Sheet boxes with more spacing
draw_box(ax, 55, 55, 60, 50, 'POWER\nSUPPLIES', '#c8e6c9', bold=True, fontsize=10)
draw_box(ax, 150, 55, 75, 60, 'DIGITAL\nCONTROL', '#bbdefb', bold=True, fontsize=10)
draw_box(ax, 150, 130, 130, 65, 'ANALOG\nFRONTEND', '#ffcdd2', bold=True, fontsize=10)
draw_box(ax, 295, 130, 75, 65, 'TX\nSWITCH', '#ffe0b2', bold=True, fontsize=10)

# External connectors
draw_box(ax, 20, 130, 18, 18, 'J1\nE1\nGPIO', '#f5f5f5', fontsize=7)
draw_box(ax, 20, 160, 18, 10, 'J2\nTX_IN', '#f5f5f5', fontsize=7)
draw_box(ax, 260, 168, 18, 10, 'J11\nRX0', '#f5f5f5', fontsize=7)
draw_box(ax, 320, 168, 18, 10, 'J12\nRX1', '#f5f5f5', fontsize=7)

# Power rails (vertical distribution)
# +12V rail
draw_wire(ax, 20, 95, 55, 95, color='#c0392b', lw=2.5)
draw_wire(ax, 55, 95, 55, 80, color='#c0392b', lw=2.5)
draw_wire(ax, 55, 95, 295, 95, color='#c0392b', lw=2.5)
draw_wire(ax, 295, 95, 295, 130, color='#c0392b', lw=2.5)
draw_wire(ax, 150, 95, 150, 55, color='#c0392b', lw=2.5)
draw_label(ax, 15, 95, '+12V', color='#c0392b', ha='left')

# +5V rail
draw_wire(ax, 55, 85, 150, 85, color='#2980b9', lw=2)
draw_wire(ax, 55, 85, 55, 55, color='#2980b9', lw=2)
draw_wire(ax, 150, 85, 150, 55, color='#2980b9', lw=2)
draw_label(ax, 15, 85, '+5V', color='#2980b9', ha='left')

# GND rail
draw_wire(ax, 20, 75, 55, 75, color='#7f8c8d', lw=1.5)
draw_wire(ax, 55, 75, 295, 75, color='#7f8c8d', lw=1.5)
draw_wire(ax, 55, 75, 55, 55, color='#7f8c8d', lw=1.5)
draw_wire(ax, 150, 75, 150, 55, color='#7f8c8d', lw=1.5)
draw_wire(ax, 295, 75, 295, 130, color='#7f8c8d', lw=1.5)
draw_label(ax, 15, 75, 'GND', color='#7f8c8d', ha='left')

# E1 → Digital control (SPI)
draw_wire(ax, 29, 130, 29, 105, color='#27ae60', lw=1.5)
draw_wire(ax, 29, 105, 110, 105, color='#27ae60', lw=1.5)
draw_wire(ax, 110, 105, 110, 55, color='#27ae60', lw=1.5)
draw_label(ax, 15, 105, 'SPI\nControl', color='#27ae60', ha='left', fontsize=7)

# Digital → Analog (MUX + GATE control)
draw_wire(ax, 187, 85, 187, 100, color='#2c3e50', lw=2)
draw_wire(ax, 187, 100, 150, 100, color='#2c3e50', lw=2)
draw_wire(ax, 150, 100, 150, 97, color='#2c3e50', lw=2)
draw_label(ax, 195, 92, 'MUX_A..EN\nGATE0..7', color='#2c3e50', fontsize=7, ha='left')

# TX_BUS connection
draw_wire(ax, 215, 130, 215, 150, color='#e67e22', lw=2.5)
draw_wire(ax, 215, 150, 295, 150, color='#e67e22', lw=2.5)
draw_wire(ax, 295, 150, 295, 130, color='#e67e22', lw=2.5)
draw_wire(ax, 29, 160, 29, 150, color='#e67e22', lw=2.5)
draw_wire(ax, 29, 150, 150, 150, color='#e67e22', lw=2.5)
draw_label(ax, 80, 153, 'TX_BUS (±100V)', color='#e67e22', fontsize=8)

# RX outputs
draw_wire(ax, 260, 168, 245, 168, color='#8e44ad', lw=1.5)
draw_wire(ax, 245, 168, 245, 145, color='#8e44ad', lw=1.5)
draw_wire(ax, 245, 145, 215, 145, color='#8e44ad', lw=1.5)
draw_label(ax, 270, 171, 'RX0_OUT', color='#8e44ad', fontsize=7)

draw_wire(ax, 320, 168, 335, 168, color='#8e44ad', lw=1.5)
draw_wire(ax, 335, 168, 335, 140, color='#8e44ad', lw=1.5)
draw_wire(ax, 335, 140, 295, 140, color='#8e44ad', lw=1.5)
draw_label(ax, 330, 171, 'RX1_OUT', color='#8e44ad', fontsize=7)

plt.tight_layout()
plt.savefig('/home/james/.openclaw/canvas/turboquant_v5_schematics/01_root_overview.png',
            dpi=200, bbox_inches='tight', facecolor='white')
plt.close()

# ============================================================
# SHEET 2: ANALOG FRONTEND
# ============================================================
fig, ax = plt.subplots(1, 1, figsize=(18, 14))
ax.set_xlim(0, 260)
ax.set_ylim(0, 150)
ax.set_aspect('equal')
ax.axis('off')
ax.set_title('TurboQuant V5 — ANALOG FRONTEND Sheet', fontsize=14, fontweight='bold', pad=10)

ax.text(130, 147, 'T/R Bridge → DG408 MUX → OPA1641 LNA  |  8 channels, 2 LNAs (RX0 + RX1)',
        ha='center', fontsize=9, style='italic', color='#555')

# --- LEFT: Hierarchical input labels ---
input_x = 12
input_items = [
    (input_x, 138, '+5V', '#2980b9'),
    (input_x, 133, '+12V', '#c0392b'),
    (input_x, 128, 'GND', '#7f8c8d'),
    (input_x, 118, 'MUX_A', '#2c3e50'),
    (input_x, 113, 'MUX_B', '#2c3e50'),
    (input_x, 108, 'MUX_C', '#2c3e50'),
    (input_x, 103, 'MUX_EN', '#2c3e50'),
    (input_x, 93, 'TX_BUS', '#e67e22'),
]
for x, y, label, color in input_items:
    draw_label(ax, x, y, label, color=color, ha='left', fontsize=8)
    draw_wire(ax, x+8, y, 28, y, color=color, lw=1.2)

# --- T/R BRIDGE: 8 channels ---
for ch in range(8):
    y = 140 - ch * 8.5
    x = 45
    # Channel label
    ax.text(32, y, f'CH{ch}', ha='right', va='center', fontsize=6, color='#555', fontweight='bold')
    
    # Bias network (left of bridge)
    draw_box(ax, 38, y+1, 8, 3, f'Z{ch}\n5.1V', '#e3f2fd', fontsize=4)
    draw_box(ax, 38, y-1.5, 8, 3, f'R{ch}a\n1k', '#e8f5e9', fontsize=4)
    draw_box(ax, 38, y-4, 8, 3, f'R{ch}b\n100k', '#e8f5e9', fontsize=4)
    
    # 4-diode bridge
    bridge_w = 18
    bridge_h = 6
    rect = patches.FancyBboxPatch((x-bridge_w/2, y-bridge_h/2), bridge_w, bridge_h,
                                    boxstyle="round,pad=0.02,rounding_size=0.3",
                                    facecolor='#fff3e0', edgecolor='#e65100', linewidth=0.8)
    ax.add_patch(rect)
    # Diode symbols inside
    for d in range(4):
        dx = x - 6 + d * 4
        tiny = patches.Rectangle((dx-1.2, y-2), 2.4, 4,
                                  facecolor='#ffcc80', edgecolor='#e65100', linewidth=0.5)
        ax.add_patch(tiny)
        ax.text(dx, y, 'D', ha='center', va='center', fontsize=3, color='#bf360c')
    ax.text(x, y-4.5, f'D{ch*4+1}-D{ch*4+4}\nMUR120', ha='center', va='top', fontsize=4, color='#555')
    
    # TX_BUS feed into bridge
    draw_l_wire(ax, 28, 93, 36, y, color='#e67e22', lw=1)
    draw_wire(ax, 36, y, x-9, y, color='#e67e22', lw=1)
    
    # Bridge output (right side)
    draw_wire(ax, x+9, y, 72, y, color='#555', lw=1)

# --- DG408 MUXes ---
# U1: CH0-3 → RX0
mux1_x = 95
mux1_y = 125
draw_box(ax, mux1_x, mux1_y, 22, 42, 'U1\nDG408\nMUX 0-3', '#ffccbc', bold=True, fontsize=9)

# U1 pins (left side)
u1_pin_y = [mux1_y+18, mux1_y+12, mux1_y+6, mux1_y+0]
for n in range(4):
    py = u1_pin_y[n]
    ch_y = 140 - n * 8.5
    # Wire from CH to MUX input
    draw_l_wire(ax, 72, ch_y, 84, py, color='#555', lw=1)
    draw_wire(ax, 84, py, mux1_x-11, py, color='#555', lw=1)
    draw_pin(ax, mux1_x-11, py, f'S{n+1}', side='left', fontsize=5)

# U1 pins (right side)
for label, py in [('EN', mux1_y+18), ('A', mux1_y+12), ('B', mux1_y+6), ('C', mux1_y+0),
                  ('X', mux1_y-6), ('V-', mux1_y-12), ('V+', mux1_y-18)]:
    draw_pin(ax, mux1_x+11, py, label, side='right', fontsize=5)

# U1 control wiring
for label, py, src_y in [('MUX_A', mux1_y+12, 118), ('MUX_B', mux1_y+6, 113), 
                         ('MUX_C', mux1_y+0, 108), ('MUX_EN', mux1_y-6, 103)]:
    draw_wire(ax, 28, src_y, 80, src_y, color='#2c3e50', lw=1.2)
    draw_wire(ax, 80, src_y, 80, py, color='#2c3e50', lw=1.2)
    draw_wire(ax, 80, py, mux1_x+11, py, color='#2c3e50', lw=1.2)

# U1 output → RX0 LNA
draw_wire(ax, mux1_x+11, mux1_y-6, 125, mux1_y-6, color='#8e44ad', lw=1.5)

# U2: CH4-7 → RX1
mux2_x = 95
mux2_y = 55
draw_box(ax, mux2_x, mux2_y, 22, 42, 'U2\nDG408\nMUX 4-7', '#ffccbc', bold=True, fontsize=9)

# U2 pins (left side)
u2_pin_y = [mux2_y+18, mux2_y+12, mux2_y+6, mux2_y+0]
for n in range(4, 8):
    py = u2_pin_y[n-4]
    ch_y = 140 - n * 8.5
    draw_l_wire(ax, 72, ch_y, 84, py, color='#555', lw=1)
    draw_wire(ax, 84, py, mux2_x-11, py, color='#555', lw=1)
    draw_pin(ax, mux2_x-11, py, f'S{n+1}', side='left', fontsize=5)

# U2 control wiring (shared with U1)
for label, py, src_y in [('MUX_A', mux2_y+12, 118), ('MUX_B', mux2_y+6, 113), 
                         ('MUX_C', mux2_y+0, 108), ('MUX_EN', mux2_y-6, 103)]:
    draw_wire(ax, 80, src_y, 80, py, color='#2c3e50', lw=1.2)
    draw_wire(ax, 80, py, mux2_x+11, py, color='#2c3e50', lw=1.2)

# U2 output → RX1 LNA
draw_wire(ax, mux2_x+11, mux2_y-6, 125, mux2_y-6, color='#8e44ad', lw=1.5)

# --- OPA1641 LNAs ---
# U3: RX0 LNA
lna1_x = 155
lna1_y = 115
draw_box(ax, lna1_x, lna1_y, 22, 30, 'U3\nOPA1641\nLNA RX0\nGain = 10', '#c8e6c9', bold=True, fontsize=8)

# Input coupling cap
draw_box(ax, 130, lna1_y, 8, 5, 'C3\n100p', '#e3f2fd', fontsize=5)
draw_wire(ax, 125, lna1_y, 130, lna1_y, color='#8e44ad', lw=1.2)
draw_wire(ax, 134, lna1_y, lna1_x-11, lna1_y, color='#8e44ad', lw=1.2)
draw_pin(ax, lna1_x-11, lna1_y, '+', side='left', fontsize=6)

# Feedback network
draw_box(ax, lna1_x+18, lna1_y+8, 8, 5, 'R6\n10k', '#e8f5e9', fontsize=5)
draw_box(ax, lna1_x+5, lna1_y-10, 8, 5, 'R5\n1k', '#e8f5e9', fontsize=5)
draw_wire(ax, lna1_x+11, lna1_y+8, lna1_x+14, lna1_y+8, color='#555', lw=0.8)
draw_wire(ax, lna1_x+14, lna1_y+8, lna1_x+14, lna1_y, color='#555', lw=0.8)
draw_wire(ax, lna1_x+14, lna1_y, lna1_x+11, lna1_y, color='#555', lw=0.8)
draw_wire(ax, lna1_x+5, lna1_y-7, lna1_x+5, lna1_y, color='#555', lw=0.8)
draw_wire(ax, lna1_x+5, lna1_y-7, lna1_x-11, lna1_y-7, color='#555', lw=0.8)
draw_pin(ax, lna1_x-11, lna1_y-7, '-', side='left', fontsize=6)

# Output
draw_wire(ax, lna1_x+11, lna1_y, 180, lna1_y, color='#8e44ad', lw=1.5)
draw_label(ax, 195, lna1_y, 'RX0_OUT →', color='#8e44ad', ha='left', fontsize=8)

# Power U3
for pin_name, py, rail_y in [('V+', lna1_y+12, 138), ('V-', lna1_y-12, 128)]:
    draw_wire(ax, lna1_x, py, lna1_x, rail_y, color='#2980b9' if 'V+' in pin_name else '#7f8c8d', lw=1)

# U4: RX1 LNA
lna2_x = 155
lna2_y = 50
draw_box(ax, lna2_x, lna2_y, 22, 30, 'U4\nOPA1641\nLNA RX1\nGain = 10', '#c8e6c9', bold=True, fontsize=8)

# Input coupling cap
draw_box(ax, 130, lna2_y, 8, 5, 'C6\n100p', '#e3f2fd', fontsize=5)
draw_wire(ax, 125, lna2_y, 130, lna2_y, color='#8e44ad', lw=1.2)
draw_wire(ax, 134, lna2_y, lna2_x-11, lna2_y, color='#8e44ad', lw=1.2)
draw_pin(ax, lna2_x-11, lna2_y, '+', side='left', fontsize=6)

# Feedback
draw_box(ax, lna2_x+18, lna2_y+8, 8, 5, 'R32\n10k', '#e8f5e9', fontsize=5)
draw_box(ax, lna2_x+5, lna2_y-10, 8, 5, 'R31\n1k', '#e8f5e9', fontsize=5)
draw_wire(ax, lna2_x+11, lna2_y+8, lna2_x+14, lna2_y+8, color='#555', lw=0.8)
draw_wire(ax, lna2_x+14, lna2_y+8, lna2_x+14, lna2_y, color='#555', lw=0.8)
draw_wire(ax, lna2_x+14, lna2_y, lna2_x+11, lna2_y, color='#555', lw=0.8)
draw_wire(ax, lna2_x+5, lna2_y-7, lna2_x+5, lna2_y, color='#555', lw=0.8)
draw_wire(ax, lna2_x+5, lna2_y-7, lna2_x-11, lna2_y-7, color='#555', lw=0.8)
draw_pin(ax, lna2_x-11, lna2_y-7, '-', side='left', fontsize=6)

# Output
draw_wire(ax, lna2_x+11, lna2_y, 180, lna2_y, color='#8e44ad', lw=1.5)
draw_label(ax, 195, lna2_y, 'RX1_OUT →', color='#8e44ad', ha='left', fontsize=8)

# Power U4
for pin_name, py, rail_y in [('V+', lna2_y+12, 138), ('V-', lna2_y-12, 128)]:
    draw_wire(ax, lna2_x, py, lna2_x, rail_y, color='#2980b9' if 'V+' in pin_name else '#7f8c8d', lw=1)

# --- Power rails (horizontal at top) ---
draw_bus(ax, 20, 138, 240, 138, color='#2980b9', lw=2.5)
draw_label(ax, 245, 138, '+5V', color='#2980b9', ha='left', fontsize=9)

draw_bus(ax, 20, 133, 240, 133, color='#c0392b', lw=2.5)
draw_label(ax, 245, 133, '+12V', color='#c0392b', ha='left', fontsize=9)

draw_bus(ax, 20, 128, 240, 128, color='#7f8c8d', lw=2)
draw_label(ax, 245, 128, 'GND', color='#7f8c8d', ha='left', fontsize=9)

# --- Right side CH labels ---
for n in range(8):
    y = 140 - n * 8.5
    ax.text(250, y, f'CH{n}', ha='left', va='center', fontsize=6, color='#777')

plt.tight_layout()
plt.savefig('/home/james/.openclaw/canvas/turboquant_v5_schematics/02_analog_frontend.png',
            dpi=200, bbox_inches='tight', facecolor='white')
plt.close()

# ============================================================
# SHEET 3: DIGITAL CONTROL
# ============================================================
fig, ax = plt.subplots(1, 1, figsize=(16, 12))
ax.set_xlim(0, 220)
ax.set_ylim(0, 120)
ax.set_aspect('equal')
ax.axis('off')
ax.set_title('TurboQuant V5 — DIGITAL CONTROL Sheet', fontsize=14, fontweight='bold', pad=10)

ax.text(110, 117, 'RP E1 GPIO → 74HCT595 Shift Register → BSS138 Gate Drivers → GATE0..7',
        ha='center', fontsize=9, style='italic', color='#555')

# --- LEFT: Hierarchical inputs ---
input_x = 15
input_items = [
    (input_x, 108, '+5V', '#2980b9'),
    (input_x, 103, 'GND', '#7f8c8d'),
    (input_x, 93, 'SER', '#27ae60'),
    (input_x, 88, 'SRCLK', '#27ae60'),
    (input_x, 83, 'RCLK', '#27ae60'),
    (input_x, 78, '~OE', '#27ae60'),
    (input_x, 73, 'SRCLR', '#27ae60'),
]
for x, y, label, color in input_items:
    draw_label(ax, x, y, label, color=color, ha='left', fontsize=8)
    draw_wire(ax, x+8, y, 30, y, color=color, lw=1.2)

# --- J3 E1 Connector ---
draw_box(ax, 45, 82, 18, 32, 'J3\nRP_E1\nGPIO\nHeader', '#f5f5f5', fontsize=7)
# Pin labels on connector
for n, (label, y) in enumerate([('SER', 93), ('SRCLK', 88), ('RCLK', 83), ('~OE', 78), ('SRCLR', 73)]):
    draw_wire(ax, 54, y, 54, y, color='#27ae60', lw=1)

# --- 74HCT595 Shift Register ---
draw_box(ax, 95, 82, 25, 40, 'U5\n74HCT595\n8-bit Shift\nRegister', '#bbdefb', bold=True, fontsize=9)

# SPI inputs to 74HCT595
for label, src_y, dst_y in [('SER', 93, 95), ('SRCLK', 88, 90), ('RCLK', 83, 85), 
                             ('~OE', 78, 70), ('SRCLR', 73, 98)]:
    draw_wire(ax, 30, src_y, 82, src_y, color='#27ae60', lw=1.5)
    draw_wire(ax, 82, src_y, 82, dst_y, color='#27ae60', lw=1.5)
    draw_wire(ax, 82, dst_y, 83, dst_y, color='#27ae60', lw=1.5)

# 74HCT595 outputs (left side: QA-QH)
output_pins = [
    ('QA', 100, 0), ('QB', 95, 1), ('QC', 90, 2), ('QD', 85, 3),
    ('QE', 80, 4), ('QF', 75, 5), ('QG', 70, 6), ('QH', 65, 7)
]
for label, py, ch in output_pins:
    draw_pin(ax, 83, py, label, side='left', fontsize=5)
    gate_y = 100 - ch * 6.5
    # Route from 74HCT595 to BSS138
    draw_l_wire(ax, 83, py, 135, gate_y, color='#2c3e50', lw=1)

# 74HCT595 power
draw_wire(ax, 95, 102, 95, 108, color='#2980b9', lw=1.2)
draw_wire(ax, 95, 62, 95, 55, color='#7f8c8d', lw=1.2)

# --- BSS138 Gate Drivers (8) ---
for n in range(8):
    gate_y = 100 - n * 6.5
    # Gate resistor
    draw_box(ax, 145, gate_y, 7, 4, f'R{n+3}\n100Ω', '#e8f5e9', fontsize=4)
    # BSS138
    draw_box(ax, 162, gate_y, 14, 7, f'Q{n+1}\nBSS138', '#fff9c4', fontsize=5)
    # Source → GND
    draw_wire(ax, 162, gate_y-3.5, 162, 15, color='#7f8c8d', lw=0.8)
    # Drain → output
    draw_wire(ax, 169, gate_y, 185, gate_y, color='#e67e22', lw=1.5)
    # GATE label
    draw_label(ax, 200, gate_y, f'GATE{n}', color='#e67e22', ha='left', fontsize=7)

# --- Power rails ---
draw_bus(ax, 15, 108, 180, 108, color='#2980b9', lw=2.5)
draw_bus(ax, 15, 15, 180, 15, color='#7f8c8d', lw=2)

plt.tight_layout()
plt.savefig('/home/james/.openclaw/canvas/turboquant_v5_schematics/03_digital_control.png',
            dpi=200, bbox_inches='tight', facecolor='white')
plt.close()

# ============================================================
# SHEET 4: TX SWITCH
# ============================================================
fig, ax = plt.subplots(1, 1, figsize=(18, 12))
ax.set_xlim(0, 260)
ax.set_ylim(0, 120)
ax.set_aspect('equal')
ax.axis('off')
ax.set_title('TurboQuant V5 — TX SWITCH Sheet', fontsize=14, fontweight='bold', pad=10)

ax.text(130, 117, 'GATE0..7 → TC4427 Gate Drivers → IRF830 MOSFETs → TX_BUS (±100V)',
        ha='center', fontsize=9, style='italic', color='#555')

# --- LEFT: Inputs ---
input_x = 15
inputs = [
    (input_x, 108, '+12V', '#c0392b'),
    (input_x, 103, 'GND', '#7f8c8d'),
]
for x, y, label, color in inputs:
    draw_label(ax, x, y, label, color=color, ha='left', fontsize=8)
    draw_wire(ax, x+8, y, 35, y, color=color, lw=1.2)

# GATE0-7 inputs
for n in range(8):
    y = 95 - n * 6.5
    draw_label(ax, input_x, y, f'GATE{n}', color='#e67e22', ha='left', fontsize=7)
    draw_wire(ax, input_x+8, y, 35, y, color='#e67e22', lw=1.2)

# --- TC4427 Gate Drivers (4 chips) ---
for drv in range(4):
    x = 55 + drv * 22
    y = 70
    draw_box(ax, x, y, 18, 38, f'U{drv+1}\nTC4427\nDual Driver', '#ffe0b2', fontsize=7)
    
    # Decoupling cap
    draw_box(ax, x+6, y+18, 7, 5, '100nF', '#e3f2fd', fontsize=4)
    
    # VCC/GND pins
    draw_wire(ax, x, y+15, x-8, y+15, color='#c0392b', lw=1)
    draw_wire(ax, x, y-19, x-8, y-19, color='#7f8c8d', lw=1)
    
    # Input A (top channel)
    ch_a = drv * 2
    y_a = 95 - ch_a * 6.5
    draw_wire(ax, 35, y_a, x-8, y_a, color='#e67e22', lw=1)
    draw_wire(ax, x-8, y_a, x-8, y+12, color='#e67e22', lw=1)
    draw_wire(ax, x-8, y+12, x-9, y+12, color='#e67e22', lw=1)
    draw_pin(ax, x-9, y+12, 'A_in', side='left', fontsize=5)
    
    # Input B (bottom channel)
    ch_b = drv * 2 + 1
    y_b = 95 - ch_b * 6.5
    draw_wire(ax, 35, y_b, x-8, y_b, color='#e67e22', lw=1)
    draw_wire(ax, x-8, y_b, x-8, y+5, color='#e67e22', lw=1)
    draw_wire(ax, x-8, y+5, x-9, y+5, color='#e67e22', lw=1)
    draw_pin(ax, x-9, y+5, 'B_in', side='left', fontsize=5)
    
    # Output A
    out_a_y = y + 12
    ch_a_y = 95 - ch_a * 6.5
    draw_wire(ax, x+9, out_a_y, 125, ch_a_y, color='#e67e22', lw=1.5)
    
    # Output B
    out_b_y = y + 5
    ch_b_y = 95 - ch_b * 6.5
    draw_wire(ax, x+9, out_b_y, 125, ch_b_y, color='#e67e22', lw=1.5)

# --- IRF830 MOSFETs (8) ---
for n in range(8):
    y = 95 - n * 6.5
    x = 135
    draw_box(ax, x, y, 16, 6, f'Q{n+1}\nIRF830', '#ffccbc', fontsize=5)
    
    # Gate input
    draw_wire(ax, 125, y, x-8, y, color='#e67e22', lw=1.5)
    
    # Source → GND
    draw_wire(ax, x, y-3, x, 15, color='#7f8c8d', lw=0.8)
    
    # Drain → TX_BUS
    draw_wire(ax, x+8, y, 160, y, color='#c0392b', lw=2)

# --- TX_BUS ---
draw_bus(ax, 160, 55, 250, 55, color='#c0392b', lw=3)
draw_label(ax, 205, 62, 'TX_BUS  (±100V pulse to Analog Frontend)', color='#c0392b', fontsize=9)

# TX_OUT label
draw_label(ax, 250, 55, '→ TX_BUS', color='#c0392b', ha='left', fontsize=8)

# --- Power rails ---
draw_bus(ax, 15, 108, 140, 108, color='#c0392b', lw=2.5)
draw_bus(ax, 15, 15, 140, 15, color='#7f8c8d', lw=2)

plt.tight_layout()
plt.savefig('/home/james/.openclaw/canvas/turboquant_v5_schematics/04_tx_switch.png',
            dpi=200, bbox_inches='tight', facecolor='white')
plt.close()

# ============================================================
# SHEET 5: POWER SUPPLIES
# ============================================================
fig, ax = plt.subplots(1, 1, figsize=(14, 10))
ax.set_xlim(0, 180)
ax.set_ylim(0, 100)
ax.set_aspect('equal')
ax.axis('off')
ax.set_title('TurboQuant V5 — POWER SUPPLIES Sheet', fontsize=14, fontweight='bold', pad=10)

ax.text(90, 97, '12V IN → LM7805 (+5V) → AMS1117-3.3 (+3.3V)  |  Protected input with polyfuse + Schottky',
        ha='center', fontsize=9, style='italic', color='#555')

# --- Input section ---
draw_box(ax, 25, 75, 22, 12, 'J1\n12V DC\nInput', '#f5f5f5', fontsize=7)
draw_box(ax, 58, 75, 14, 10, 'F1\nPolyfuse\n1A', '#fff3e0', fontsize=6)
draw_box(ax, 82, 75, 14, 10, 'D1\nSS34\nSchottky', '#fff3e0', fontsize=6)

# Input wiring
draw_wire(ax, 36, 75, 36, 75, color='#c0392b', lw=2.5)
draw_wire(ax, 36, 75, 51, 75, color='#c0392b', lw=2.5)
draw_wire(ax, 65, 75, 75, 75, color='#c0392b', lw=2.5)
draw_wire(ax, 89, 75, 96, 75, color='#c0392b', lw=2.5)

# --- LM7805 ---
draw_box(ax, 115, 75, 22, 20, 'U1\nLM7805\nTO-220', '#c8e6c9', bold=True, fontsize=9)

# Input cap
draw_box(ax, 100, 62, 10, 6, 'C1\n100nF', '#e3f2fd', fontsize=5)
draw_wire(ax, 96, 75, 96, 62, color='#c0392b', lw=1)
draw_wire(ax, 96, 62, 100, 62, color='#c0392b', lw=1)

# Output cap
draw_box(ax, 128, 62, 10, 6, 'C2\n10µF', '#e3f2fd', fontsize=5)
draw_wire(ax, 126, 75, 126, 62, color='#c0392b', lw=1)
draw_wire(ax, 126, 62, 128, 62, color='#c0392b', lw=1)

# 5V output rail
draw_wire(ax, 126, 65, 126, 55, color='#2980b9', lw=2.5)
draw_wire(ax, 126, 55, 160, 55, color='#2980b9', lw=2.5)
draw_label(ax, 165, 55, '+5V OUT', color='#2980b9', ha='left', fontsize=9)

# --- AMS1117-3.3 ---
draw_box(ax, 115, 35, 22, 18, 'U2\nAMS1117\nSOT-223', '#c8e6c9', bold=True, fontsize=9)

# 5V → 3.3V input
draw_wire(ax, 126, 55, 126, 44, color='#2980b9', lw=2)
draw_wire(ax, 126, 44, 115, 44, color='#2980b9', lw=2)

# Input cap
draw_box(ax, 100, 28, 10, 6, 'C3\n100nF', '#e3f2fd', fontsize=5)
draw_wire(ax, 96, 35, 96, 28, color='#2980b9', lw=1)
draw_wire(ax, 96, 28, 100, 28, color='#2980b9', lw=1)

# Output cap
draw_box(ax, 128, 28, 10, 6, 'C4\n10µF', '#e3f2fd', fontsize=5)
draw_wire(ax, 126, 35, 126, 28, color='#2980b9', lw=1)
draw_wire(ax, 126, 28, 128, 28, color='#2980b9', lw=1)

# 3.3V output rail
draw_wire(ax, 126, 26, 126, 20, color='#2980b9', lw=2)
draw_wire(ax, 126, 20, 160, 20, color='#2980b9', lw=2)
draw_label(ax, 165, 20, '+3.3V OUT', color='#2980b9', ha='left', fontsize=9)

# --- GND distribution ---
draw_bus(ax, 20, 10, 150, 10, color='#7f8c8d', lw=2.5)
draw_label(ax, 155, 10, 'GND', color='#7f8c8d', ha='left', fontsize=9)

# GND connections
draw_wire(ax, 115, 65, 115, 55, color='#7f8c8d', lw=1)
draw_wire(ax, 115, 55, 115, 10, color='#7f8c8d', lw=1)
draw_wire(ax, 115, 26, 115, 10, color='#7f8c8d', lw=1)

# 12V passthrough (to TX switch)
draw_wire(ax, 96, 75, 96, 90, color='#c0392b', lw=2)
draw_wire(ax, 96, 90, 160, 90, color='#c0392b', lw=2)
draw_label(ax, 165, 90, '+12V passthrough', color='#c0392b', ha='left', fontsize=8)

plt.tight_layout()
plt.savefig('/home/james/.openclaw/canvas/turboquant_v5_schematics/05_power_supplies.png',
            dpi=200, bbox_inches='tight', facecolor='white')
plt.close()

print("Regenerated schematic reference images with improved spacing.")
print("Location: /home/james/.openclaw/canvas/turboquant_v5_schematics/")
