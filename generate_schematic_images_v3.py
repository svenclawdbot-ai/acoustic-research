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
                                    facecolor=color, edgecolor='black', linewidth=lw, zorder=3)
    ax.add_patch(rect)
    weight = 'bold' if bold else 'normal'
    ax.text(x, y, label, ha='center', va='center', fontsize=fontsize,
            color=text_color, fontweight=weight, wrap=True, linespacing=0.9, zorder=4)

def draw_wire(ax, x1, y1, x2, y2, color='#1a5276', lw=1.2, zorder=2):
    ax.plot([x1, x2], [y1, y2], color=color, linewidth=lw, solid_capstyle='round', zorder=zorder)

def draw_l_wire(ax, x1, y1, x2, y2, color='#1a5276', lw=1.2, zorder=2):
    ax.plot([x1, x2], [y1, y1], color=color, linewidth=lw, solid_capstyle='round', zorder=zorder)
    ax.plot([x2, x2], [y1, y2], color=color, linewidth=lw, solid_capstyle='round', zorder=zorder)

def draw_label(ax, x, y, text, color='#1a5276', fontsize=7, ha='center', zorder=5):
    ax.text(x, y, text, ha=ha, va='center', fontsize=fontsize, color=color, fontweight='bold', zorder=zorder)

def draw_pin_label(ax, x, y, text, side='left', color='black', fontsize=5, zorder=5):
    offset = 3 if side == 'left' else -3
    ha = 'right' if side == 'left' else 'left'
    ax.text(x + offset, y, text, ha=ha, va='center', fontsize=fontsize, color=color, zorder=zorder)

def draw_junction(ax, x, y, color='#1a5276', size=2.5, zorder=6):
    circ = patches.Circle((x, y), size, facecolor=color, edgecolor='none', zorder=zorder)
    ax.add_patch(circ)

# ============================================================
# SHEET 2: ANALOG FRONTEND — FIXED
# ============================================================
fig, ax = plt.subplots(1, 1, figsize=(20, 16))
ax.set_xlim(0, 290)
ax.set_ylim(0, 170)
ax.set_aspect('equal')
ax.axis('off')
ax.set_title('TurboQuant V5 — ANALOG FRONTEND Sheet', fontsize=14, fontweight='bold', pad=10)
ax.text(145, 167, 'T/R Bridge → DG408 MUX → OPA1641 LNA  |  8 channels, 2 LNAs (RX0 + RX1)',
        ha='center', fontsize=9, style='italic', color='#555')

# --- TOP: Power rails (well above all components) ---
draw_wire(ax, 20, 160, 280, 160, color='#2980b9', lw=2.5)
draw_label(ax, 285, 160, '+5V', color='#2980b9', ha='left', fontsize=9)
draw_wire(ax, 20, 155, 280, 155, color='#c0392b', lw=2.5)
draw_label(ax, 285, 155, '+12V', color='#c0392b', ha='left', fontsize=9)
draw_wire(ax, 20, 150, 280, 150, color='#7f8c8d', lw=2)
draw_label(ax, 285, 150, 'GND', color='#7f8c8d', ha='left', fontsize=9)

# --- LEFT: Hierarchical inputs ---
input_x = 12
input_items = [
    (input_x, 140, 'MUX_A', '#2c3e50'),
    (input_x, 135, 'MUX_B', '#2c3e50'),
    (input_x, 130, 'MUX_C', '#2c3e50'),
    (input_x, 125, 'MUX_EN', '#2c3e50'),
    (input_x, 115, 'TX_BUS', '#e67e22'),
]
for x, y, label, color in input_items:
    draw_label(ax, x, y, label, color=color, ha='left', fontsize=8)
    draw_wire(ax, x+8, y, 28, y, color=color, lw=1.2)

# --- T/R BRIDGE: 8 channels ---
for ch in range(8):
    y = 138 - ch * 9
    x = 45
    ax.text(32, y, f'CH{ch}', ha='right', va='center', fontsize=6, color='#555', fontweight='bold')
    
    draw_box(ax, 38, y+1.5, 7, 3, f'Z{ch}', '#e3f2fd', fontsize=4)
    draw_box(ax, 38, y-1.5, 7, 3, f'R{ch}a', '#e8f5e9', fontsize=4)
    
    bridge_w = 16
    bridge_h = 5.5
    rect = patches.FancyBboxPatch((x-bridge_w/2, y-bridge_h/2), bridge_w, bridge_h,
                                    boxstyle="round,pad=0.02,rounding_size=0.3",
                                    facecolor='#fff3e0', edgecolor='#e65100', linewidth=0.8, zorder=3)
    ax.add_patch(rect)
    for d in range(4):
        dx = x - 5 + d * 3.3
        tiny = patches.Rectangle((dx-1, y-1.8), 2, 3.6,
                                  facecolor='#ffcc80', edgecolor='#e65100', linewidth=0.5, zorder=3)
        ax.add_patch(tiny)
    ax.text(x, y-3.8, f'D{ch*4+1}-{ch*4+4}', ha='center', va='top', fontsize=4, color='#555')
    
    draw_l_wire(ax, 28, 115, 36, y, color='#e67e22', lw=1)
    draw_wire(ax, 36, y, x-8, y, color='#e67e22', lw=1)
    draw_wire(ax, x+8, y, 68, y, color='#555', lw=1)

# --- DG408 MUXes (moved right) ---
mux1_x = 105
mux1_y = 125
draw_box(ax, mux1_x, mux1_y, 20, 42, 'U1\nDG408\nMUX 0-3', '#ffccbc', bold=True, fontsize=9)

for n in range(4):
    py = mux1_y + 15 - n * 10
    ch_y = 138 - n * 9
    draw_l_wire(ax, 68, ch_y, 88, py, color='#555', lw=1)
    draw_wire(ax, 88, py, mux1_x-10, py, color='#555', lw=1)
    draw_pin_label(ax, mux1_x-10, py, f'S{n+1}', side='left', fontsize=5)

ctrl_pins = [('EN', mux1_y+18), ('A', mux1_y+10), ('B', mux1_y+2), ('C', mux1_y-6), ('X', mux1_y-14)]
for label, py in ctrl_pins:
    draw_pin_label(ax, mux1_x+10, py, label, side='right', fontsize=5)

ctrl_x_stagger = [78, 80, 82, 84]
for n, (label, src_y, dst_y) in enumerate([
    ('MUX_A', 140, mux1_y+10), ('MUX_B', 135, mux1_y+2),
    ('MUX_C', 130, mux1_y-6), ('MUX_EN', 125, mux1_y-14)
]):
    cx = ctrl_x_stagger[n]
    draw_wire(ax, 28, src_y, cx, src_y, color='#2c3e50', lw=1.2)
    draw_wire(ax, cx, src_y, cx, dst_y, color='#2c3e50', lw=1.2)
    draw_wire(ax, cx, dst_y, mux1_x+10, dst_y, color='#2c3e50', lw=1.2)

draw_wire(ax, mux1_x+10, mux1_y-14, 138, mux1_y-14, color='#8e44ad', lw=1.5)

# U1 power (outside left edge)
draw_wire(ax, mux1_x-12, mux1_y+10, mux1_x-12, 160, color='#2980b9', lw=1)
draw_wire(ax, mux1_x-12, mux1_y-10, mux1_x-12, 150, color='#7f8c8d', lw=1)

mux2_x = 105
mux2_y = 55
draw_box(ax, mux2_x, mux2_y, 20, 42, 'U2\nDG408\nMUX 4-7', '#ffccbc', bold=True, fontsize=9)

for n in range(4, 8):
    pin_idx = n - 4
    py = mux2_y + 15 - pin_idx * 10
    ch_y = 138 - n * 9
    draw_l_wire(ax, 68, ch_y, 88, py, color='#555', lw=1)
    draw_wire(ax, 88, py, mux2_x-10, py, color='#555', lw=1)
    draw_pin_label(ax, mux2_x-10, py, f'S{n+1}', side='left', fontsize=5)

for n, (label, src_y, dst_y) in enumerate([
    ('MUX_A', 140, mux2_y+10), ('MUX_B', 135, mux2_y+2),
    ('MUX_C', 130, mux2_y-6), ('MUX_EN', 125, mux2_y-14)
]):
    cx = ctrl_x_stagger[n]
    draw_wire(ax, cx, src_y, cx, dst_y, color='#2c3e50', lw=1.2)
    draw_wire(ax, cx, dst_y, mux2_x+10, dst_y, color='#2c3e50', lw=1.2)

draw_wire(ax, mux2_x+10, mux2_y-14, 138, mux2_y-14, color='#8e44ad', lw=1.5)

# U2 power (outside left edge)
draw_wire(ax, mux2_x-12, mux2_y+10, mux2_x-12, 160, color='#2980b9', lw=1)
draw_wire(ax, mux2_x-12, mux2_y-10, mux2_x-12, 150, color='#7f8c8d', lw=1)

# --- OPA1641 LNAs (moved right, power outside) ---
lna1_x = 165
lna1_y = 108
draw_box(ax, lna1_x, lna1_y, 20, 30, 'U3\nOPA1641\nLNA RX0\nGain=10', '#c8e6c9', bold=True, fontsize=8)

draw_wire(ax, 138, mux1_y-14, 145, mux1_y-14, color='#8e44ad', lw=1.2)
draw_box(ax, 145, lna1_y, 6, 5, 'C3\n100p', '#e3f2fd', fontsize=4)
draw_wire(ax, 148, lna1_y, lna1_x-10, lna1_y, color='#8e44ad', lw=1.2)
draw_pin_label(ax, lna1_x-10, lna1_y, '+', side='left', fontsize=6)

draw_box(ax, lna1_x+16, lna1_y+8, 8, 5, 'R6\n10k', '#e8f5e9', fontsize=5)
draw_box(ax, lna1_x+5, lna1_y-10, 8, 5, 'R5\n1k', '#e8f5e9', fontsize=5)
draw_wire(ax, lna1_x+10, lna1_y+8, lna1_x+12, lna1_y+8, color='#555', lw=0.8)
draw_wire(ax, lna1_x+12, lna1_y+8, lna1_x+12, lna1_y, color='#555', lw=0.8)
draw_wire(ax, lna1_x+12, lna1_y, lna1_x+10, lna1_y, color='#555', lw=0.8)
draw_wire(ax, lna1_x+5, lna1_y-7, lna1_x+5, lna1_y, color='#555', lw=0.8)
draw_wire(ax, lna1_x+5, lna1_y-7, lna1_x-10, lna1_y-7, color='#555', lw=0.8)
draw_pin_label(ax, lna1_x-10, lna1_y-7, '-', side='left', fontsize=6)

draw_wire(ax, lna1_x+10, lna1_y, 190, lna1_y, color='#8e44ad', lw=1.5)
draw_label(ax, 210, lna1_y, 'RX0_OUT →', color='#8e44ad', ha='left', fontsize=8)

# U3 power (outside left edge, x=150)
draw_wire(ax, 150, lna1_y+15, 150, 160, color='#2980b9', lw=1)
draw_wire(ax, 150, lna1_y-15, 150, 150, color='#7f8c8d', lw=1)

lna2_x = 165
lna2_y = 40
draw_box(ax, lna2_x, lna2_y, 20, 30, 'U4\nOPA1641\nLNA RX1\nGain=10', '#c8e6c9', bold=True, fontsize=8)

draw_wire(ax, 138, mux2_y-14, 145, mux2_y-14, color='#8e44ad', lw=1.2)
draw_box(ax, 145, lna2_y, 6, 5, 'C6\n100p', '#e3f2fd', fontsize=4)
draw_wire(ax, 148, lna2_y, lna2_x-10, lna2_y, color='#8e44ad', lw=1.2)
draw_pin_label(ax, lna2_x-10, lna2_y, '+', side='left', fontsize=6)

draw_box(ax, lna2_x+16, lna2_y+8, 8, 5, 'R32\n10k', '#e8f5e9', fontsize=5)
draw_box(ax, lna2_x+5, lna2_y-10, 8, 5, 'R31\n1k', '#e8f5e9', fontsize=5)
draw_wire(ax, lna2_x+10, lna2_y+8, lna2_x+12, lna2_y+8, color='#555', lw=0.8)
draw_wire(ax, lna2_x+12, lna2_y+8, lna2_x+12, lna2_y, color='#555', lw=0.8)
draw_wire(ax, lna2_x+12, lna2_y, lna2_x+10, lna2_y, color='#555', lw=0.8)
draw_wire(ax, lna2_x+5, lna2_y-7, lna2_x+5, lna2_y, color='#555', lw=0.8)
draw_wire(ax, lna2_x+5, lna2_y-7, lna2_x-10, lna2_y-7, color='#555', lw=0.8)
draw_pin_label(ax, lna2_x-10, lna2_y-7, '-', side='left', fontsize=6)

draw_wire(ax, lna2_x+10, lna2_y, 190, lna2_y, color='#8e44ad', lw=1.5)
draw_label(ax, 210, lna2_y, 'RX1_OUT →', color='#8e44ad', ha='left', fontsize=8)

# U4 power (outside left edge)
draw_wire(ax, 150, lna2_y+15, 150, 160, color='#2980b9', lw=1)
draw_wire(ax, 150, lna2_y-15, 150, 150, color='#7f8c8d', lw=1)

for n in range(8):
    y = 138 - n * 9
    ax.text(270, y, f'CH{n}', ha='left', va='center', fontsize=6, color='#777')

plt.tight_layout()
plt.savefig('/home/james/.openclaw/canvas/turboquant_v5_schematics/02_analog_frontend.png',
            dpi=200, bbox_inches='tight', facecolor='white')
plt.close()

# ============================================================
# SHEET 3: DIGITAL CONTROL — FIXED
# ============================================================
fig, ax = plt.subplots(1, 1, figsize=(18, 14))
ax.set_xlim(0, 240)
ax.set_ylim(0, 140)
ax.set_aspect('equal')
ax.axis('off')
ax.set_title('TurboQuant V5 — DIGITAL CONTROL Sheet', fontsize=14, fontweight='bold', pad=10)
ax.text(120, 137, 'RP E1 GPIO → 74HCT595 → BSS138 Gate Drivers → GATE0..7',
        ha='center', fontsize=9, style='italic', color='#555')

# Top/bottom rails
draw_wire(ax, 20, 130, 220, 130, color='#2980b9', lw=2.5)
draw_label(ax, 225, 130, '+5V', color='#2980b9', ha='left', fontsize=9)
draw_wire(ax, 20, 14, 220, 14, color='#7f8c8d', lw=2)
draw_label(ax, 225, 14, 'GND', color='#7f8c8d', ha='left', fontsize=9)

# Left inputs
input_x = 15
for x, y, label, color in [
    (input_x, 120, 'SER', '#27ae60'),
    (input_x, 115, 'SRCLK', '#27ae60'),
    (input_x, 110, 'RCLK', '#27ae60'),
    (input_x, 105, '~OE', '#27ae60'),
    (input_x, 100, 'SRCLR', '#27ae60'),
]:
    draw_label(ax, x, y, label, color=color, ha='left', fontsize=8)
    draw_wire(ax, x+8, y, 35, y, color=color, lw=1.2)

# J3
draw_box(ax, 50, 108, 16, 28, 'J3\nRP_E1\nGPIO', '#f5f5f5', fontsize=7)

# U5
draw_box(ax, 95, 108, 24, 40, 'U5\n74HCT595\n8-bit Shift\nRegister', '#bbdefb', bold=True, fontsize=9)

# SPI inputs (staggered)
for n, (label, src_y, dst_y) in enumerate([
    ('SER', 120, 118), ('SRCLK', 115, 113), ('RCLK', 110, 108),
    ('~OE', 105, 95), ('SRCLR', 100, 123)
]):
    entry_x = 75 + n * 2
    draw_wire(ax, 35, src_y, entry_x, src_y, color='#27ae60', lw=1.5)
    draw_wire(ax, entry_x, src_y, entry_x, dst_y, color='#27ae60', lw=1.5)
    draw_wire(ax, entry_x, dst_y, 83, dst_y, color='#27ae60', lw=1.5)

# U5 outputs → gate drivers (clear routing)
output_pins = [
    ('QA', 123, 0), ('QB', 118, 1), ('QC', 113, 2), ('QD', 108, 3),
    ('QE', 103, 4), ('QF', 98, 5), ('QG', 93, 6), ('QH', 88, 7)
]
for label, py, ch in output_pins:
    draw_pin_label(ax, 83, py, label, side='left', fontsize=5)
    gate_y = 120 - ch * 7
    # Horizontal from U5, then vertical down, then horizontal to resistor
    mid_x = 125
    draw_wire(ax, 83, py, mid_x, py, color='#2c3e50', lw=1)
    draw_wire(ax, mid_x, py, mid_x, gate_y, color='#2c3e50', lw=1)
    draw_wire(ax, mid_x, gate_y, 132, gate_y, color='#2c3e50', lw=1)

# U5 power (clear, no overlap with QH')
draw_wire(ax, 95, 128, 95, 130, color='#2980b9', lw=1.2)  # VCC
draw_wire(ax, 95, 68, 95, 14, color='#7f8c8d', lw=1.2)    # GND pin

# Gate drivers
for n in range(8):
    gate_y = 120 - n * 7
    draw_box(ax, 140, gate_y, 7, 4, f'R{n+3}\n100', '#e8f5e9', fontsize=4)
    draw_wire(ax, 132, gate_y, 136, gate_y, color='#2c3e50', lw=1)
    draw_box(ax, 158, gate_y, 14, 6, f'Q{n+1}\nBSS138', '#fff9c4', fontsize=5)
    draw_wire(ax, 144, gate_y, 151, gate_y, color='#2c3e50', lw=1)
    # Source → GND (well below)
    draw_wire(ax, 158, gate_y-3, 158, 22, color='#7f8c8d', lw=0.8)
    # Drain → output
    draw_wire(ax, 165, gate_y, 185, gate_y, color='#e67e22', lw=1.5)
    draw_label(ax, 205, gate_y, f'GATE{n}', color='#e67e22', ha='left', fontsize=7)

# Source bus (left of FETs, clear)
for n in range(8):
    gate_y = 120 - n * 7
    draw_wire(ax, 152, gate_y-3, 152, 22, color='#7f8c8d', lw=0.5)
draw_wire(ax, 152, 22, 220, 22, color='#7f8c8d', lw=1)
draw_wire(ax, 152, 22, 152, 14, color='#7f8c8d', lw=1)
draw_junction(ax, 152, 22, color='#7f8c8d', size=2)

plt.tight_layout()
plt.savefig('/home/james/.openclaw/canvas/turboquant_v5_schematics/03_digital_control.png',
            dpi=200, bbox_inches='tight', facecolor='white')
plt.close()

# ============================================================
# SHEET 4: TX SWITCH — FIXED (no overlap)
# ============================================================
fig, ax = plt.subplots(1, 1, figsize=(20, 14))
ax.set_xlim(0, 280)
ax.set_ylim(0, 140)
ax.set_aspect('equal')
ax.axis('off')
ax.set_title('TurboQuant V5 — TX SWITCH Sheet', fontsize=14, fontweight='bold', pad=10)
ax.text(140, 137, 'GATE0..7 → TC4427 Drivers → IRF830 MOSFETs → TX_BUS (±100V)',
        ha='center', fontsize=9, style='italic', color='#555')

# Top/bottom rails
draw_wire(ax, 20, 130, 260, 130, color='#c0392b', lw=2.5)
draw_label(ax, 265, 130, '+12V', color='#c0392b', ha='left', fontsize=9)
draw_wire(ax, 20, 18, 260, 18, color='#7f8c8d', lw=2)
draw_label(ax, 265, 18, 'GND', color='#7f8c8d', ha='left', fontsize=9)

# GATE inputs
for n in range(8):
    y = 120 - n * 7
    draw_label(ax, 15, y, f'GATE{n}', color='#e67e22', ha='left', fontsize=7)
    draw_wire(ax, 25, y, 38, y, color='#e67e22', lw=1.2)

# TC4427 drivers (4 chips, well spaced)
for drv in range(4):
    x = 55 + drv * 28
    y = 95
    draw_box(ax, x, y, 20, 38, f'U{drv+1}\nTC4427', '#ffe0b2', fontsize=7)
    
    # Decoupling cap (above, not overlapping)
    draw_box(ax, x+2, y+24, 8, 5, '100n', '#e3f2fd', fontsize=4)
    draw_wire(ax, x+6, y+21, x+6, y+24, color='#c0392b', lw=0.8)
    
    # VCC → +12V
    draw_wire(ax, x, y+15, x, 130, color='#c0392b', lw=1)
    # GND → GND rail
    draw_wire(ax, x, y-19, x, 18, color='#7f8c8d', lw=1)
    
    # Input A
    ch_a = drv * 2
    y_a = 120 - ch_a * 7
    in_a_y = y + 12
    draw_l_wire(ax, 38, y_a, x-12, in_a_y, color='#e67e22', lw=1)
    draw_pin_label(ax, x-12, in_a_y, 'A_in', side='left', fontsize=5)
    
    # Input B
    ch_b = drv * 2 + 1
    y_b = 120 - ch_b * 7
    in_b_y = y + 5
    draw_l_wire(ax, 38, y_b, x-12, in_b_y, color='#e67e22', lw=1)
    draw_pin_label(ax, x-12, in_b_y, 'B_in', side='left', fontsize=5)
    
    # Output A → via elbow to MOSFET area (no diagonal crossings)
    out_a_y = y + 12
    draw_wire(ax, x+10, out_a_y, x+20, out_a_y, color='#e67e22', lw=1.5)
    draw_wire(ax, x+20, out_a_y, x+20, y_a, color='#e67e22', lw=1.5)
    draw_wire(ax, x+20, y_a, 160, y_a, color='#e67e22', lw=1.5)
    
    # Output B
    out_b_y = y + 5
    draw_wire(ax, x+10, out_b_y, x+24, out_b_y, color='#e67e22', lw=1.5)
    draw_wire(ax, x+24, out_b_y, x+24, y_b, color='#e67e22', lw=1.5)
    draw_wire(ax, x+24, y_b, 160, y_b, color='#e67e22', lw=1.5)

# IRF830 MOSFETs (moved right, clear of drivers)
for n in range(8):
    y = 120 - n * 7
    x = 175  # well to right of drivers (drivers end at ~55+3*28+10=149)
    draw_box(ax, x, y, 16, 5.5, f'Q{n+1}\nIRF830', '#ffccbc', fontsize=5)
    
    # Gate input
    draw_wire(ax, 160, y, x-8, y, color='#e67e22', lw=1.5)
    
    # Source → GND
    draw_wire(ax, x, y-2.8, x, 25, color='#7f8c8d', lw=0.8)
    
    # Drain → TX_BUS
    draw_wire(ax, x+8, y, 205, y, color='#c0392b', lw=2)

# Source bus
draw_wire(ax, 175, 25, 220, 25, color='#7f8c8d', lw=1)
draw_wire(ax, 220, 25, 220, 18, color='#7f8c8d', lw=1)
draw_junction(ax, 220, 25, color='#7f8c8d', size=2)

# TX_BUS
draw_wire(ax, 205, 55, 260, 55, color='#c0392b', lw=3)
draw_label(ax, 210, 62, 'TX_BUS (±100V pulse to Analog Frontend)', color='#c0392b', fontsize=9)
draw_label(ax, 260, 55, '→', color='#c0392b', ha='left', fontsize=8)

plt.tight_layout()
plt.savefig('/home/james/.openclaw/canvas/turboquant_v5_schematics/04_tx_switch.png',
            dpi=200, bbox_inches='tight', facecolor='white')
plt.close()

# ============================================================
# SHEET 5: POWER SUPPLIES (unchanged, was fine)
# ============================================================
fig, ax = plt.subplots(1, 1, figsize=(14, 10))
ax.set_xlim(0, 180)
ax.set_ylim(0, 100)
ax.set_aspect('equal')
ax.axis('off')
ax.set_title('TurboQuant V5 — POWER SUPPLIES Sheet', fontsize=14, fontweight='bold', pad=10)
ax.text(90, 97, '12V IN → LM7805 (+5V) → AMS1117-3.3 (+3.3V)',
        ha='center', fontsize=9, style='italic', color='#555')

draw_box(ax, 25, 75, 22, 12, 'J1\n12V DC\nInput', '#f5f5f5', fontsize=7)
draw_box(ax, 58, 75, 14, 10, 'F1\nPolyfuse\n1A', '#fff3e0', fontsize=6)
draw_box(ax, 82, 75, 14, 10, 'D1\nSS34\nSchottky', '#fff3e0', fontsize=6)

draw_wire(ax, 36, 75, 51, 75, color='#c0392b', lw=2.5)
draw_wire(ax, 65, 75, 75, 75, color='#c0392b', lw=2.5)
draw_wire(ax, 89, 75, 96, 75, color='#c0392b', lw=2.5)

draw_box(ax, 115, 75, 22, 20, 'U1\nLM7805\nTO-220', '#c8e6c9', bold=True, fontsize=9)

draw_box(ax, 100, 62, 10, 6, 'C1\n100n', '#e3f2fd', fontsize=5)
draw_wire(ax, 96, 75, 96, 62, color='#c0392b', lw=1)
draw_wire(ax, 96, 62, 100, 62, color='#c0392b', lw=1)

draw_box(ax, 128, 62, 10, 6, 'C2\n10µ', '#e3f2fd', fontsize=5)
draw_wire(ax, 126, 75, 126, 62, color='#c0392b', lw=1)
draw_wire(ax, 126, 62, 128, 62, color='#c0392b', lw=1)

draw_wire(ax, 126, 65, 126, 55, color='#2980b9', lw=2.5)
draw_wire(ax, 126, 55, 160, 55, color='#2980b9', lw=2.5)
draw_label(ax, 165, 55, '+5V OUT', color='#2980b9', ha='left', fontsize=9)

draw_box(ax, 115, 35, 22, 18, 'U2\nAMS1117\nSOT-223', '#c8e6c9', bold=True, fontsize=9)

draw_wire(ax, 126, 55, 126, 44, color='#2980b9', lw=2)
draw_wire(ax, 126, 44, 115, 44, color='#2980b9', lw=2)

draw_box(ax, 100, 28, 10, 6, 'C3\n100n', '#e3f2fd', fontsize=5)
draw_wire(ax, 96, 35, 96, 28, color='#2980b9', lw=1)
draw_wire(ax, 96, 28, 100, 28, color='#2980b9', lw=1)

draw_box(ax, 128, 28, 10, 6, 'C4\n10µ', '#e3f2fd', fontsize=5)
draw_wire(ax, 126, 35, 126, 28, color='#2980b9', lw=1)
draw_wire(ax, 126, 28, 128, 28, color='#2980b9', lw=1)

draw_wire(ax, 126, 26, 126, 20, color='#2980b9', lw=2)
draw_wire(ax, 126, 20, 160, 20, color='#2980b9', lw=2)
draw_label(ax, 165, 20, '+3.3V OUT', color='#2980b9', ha='left', fontsize=9)

draw_wire(ax, 20, 12, 150, 12, color='#7f8c8d', lw=2.5)
draw_label(ax, 155, 12, 'GND', color='#7f8c8d', ha='left', fontsize=9)

draw_wire(ax, 115, 65, 115, 55, color='#7f8c8d', lw=1)
draw_wire(ax, 115, 55, 115, 12, color='#7f8c8d', lw=1)
draw_wire(ax, 115, 26, 115, 12, color='#7f8c8d', lw=1)

draw_wire(ax, 96, 75, 96, 88, color='#c0392b', lw=2)
draw_wire(ax, 96, 88, 160, 88, color='#c0392b', lw=2)
draw_label(ax, 165, 88, '+12V passthrough', color='#c0392b', ha='left', fontsize=8)

plt.tight_layout()
plt.savefig('/home/james/.openclaw/canvas/turboquant_v5_schematics/05_power_supplies.png',
            dpi=200, bbox_inches='tight', facecolor='white')
plt.close()

print("Clean v3 schematic images generated successfully!")
