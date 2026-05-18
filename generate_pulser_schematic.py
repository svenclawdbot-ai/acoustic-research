import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, Rectangle, Circle, FancyArrowPatch, Wedge, Polygon
import numpy as np

fig, ax = plt.subplots(1, 1, figsize=(14, 10))
ax.set_xlim(0, 14)
ax.set_ylim(0, 10)
ax.set_aspect('equal')
ax.axis('off')

# Color scheme
c_power = '#f39c12'    # orange - power
c_hv = '#e74c3c'       # red - high voltage
c_logic = '#3498db'    # blue - logic/control
c_output = '#2ecc71'   # green - output
c_ground = '#7f8c8d'   # grey - ground
c_text = '#2c3e50'     # dark - text

# Title
ax.text(7, 9.6, 'External 400V Pulser Module — TurboQuant NDE', 
        ha='center', va='center', fontsize=16, fontweight='bold', color=c_text)
ax.text(7, 9.2, 'UC3843 Flyback + IRF830 Pulse Transformer', 
        ha='center', va='center', fontsize=11, color='#7f8c8d')

# ─────────────────────────────────────────────────────────────────
# POWER INPUT SECTION (Top Left)
# ─────────────────────────────────────────────────────────────────
# Battery
bat = FancyBboxPatch((0.3, 7.8), 1.8, 1.0, boxstyle="round,pad=0.05",
                      facecolor=c_power, edgecolor='black', linewidth=1.5, alpha=0.85)
ax.add_patch(bat)
ax.text(1.2, 8.5, '7.4V LiPo\n2S 2000mAh', ha='center', va='center', 
        fontsize=8, fontweight='bold', color='white')

# Fuse
fuse = Rectangle((2.3, 8.2), 0.6, 0.2, facecolor='white', edgecolor='black', linewidth=1.5)
ax.add_patch(fuse)
ax.text(2.6, 8.45, 'FUSE\n3A', ha='center', va='center', fontsize=6, fontweight='bold')

# BMS
bms = FancyBboxPatch((3.2, 7.9), 0.8, 0.8, boxstyle="round,pad=0.02",
                      facecolor='#e67e22', edgecolor='black', linewidth=1)
ax.add_patch(bms)
ax.text(3.6, 8.3, 'BMS\n2S', ha='center', va='center', fontsize=7, color='white', fontweight='bold')

# Pre-boost (12V)
boost12 = FancyBboxPatch((4.4, 7.8), 1.2, 1.0, boxstyle="round,pad=0.05",
                          facecolor=c_power, edgecolor='black', linewidth=1.5, alpha=0.7)
ax.add_patch(boost12)
ax.text(5.0, 8.5, 'MT3608\n7.4V→12V', ha='center', va='center', 
        fontsize=8, fontweight='bold', color='white')

# 12V rail
ax.plot([6.0, 9.5], [8.3, 8.3], color=c_power, linewidth=3, alpha=0.8)
ax.text(7.8, 8.55, '+12V RAIL', ha='center', va='bottom', 
        fontsize=9, fontweight='bold', color=c_power)

# 5V LDO
ldo5 = FancyBboxPatch((6.5, 7.0), 1.0, 0.6, boxstyle="round,pad=0.02",
                       facecolor='#f1c40f', edgecolor='black', linewidth=1)
ax.add_patch(ldo5)
ax.text(7.0, 7.3, 'LM7805\n5V', ha='center', va='center', fontsize=7, fontweight='bold')

ax.plot([5.0, 7.0], [8.3, 8.3], color=c_power, linewidth=2)
ax.plot([7.0, 7.0], [8.3, 7.6], color=c_power, linewidth=2)

# ─────────────────────────────────────────────────────────────────
# FLYBACK HV SUPPLY (Top Middle)
# ─────────────────────────────────────────────────────────────────
# UC3843
uc = FancyBboxPatch((8.0, 7.8), 1.2, 1.0, boxstyle="round,pad=0.05",
                     facecolor=c_logic, edgecolor='black', linewidth=1.5, alpha=0.85)
ax.add_patch(uc)
ax.text(8.6, 8.5, 'UC3843\nFlyback\nCtrl', ha='center', va='center', 
        fontsize=8, fontweight='bold', color='white')

ax.plot([7.0, 8.6], [8.3, 8.3], color=c_power, linewidth=2)  # 12V to UC3843

# Flyback transformer
xfmr = FancyBboxPatch((9.8, 7.8), 1.4, 1.2, boxstyle="round,pad=0.05",
                       facecolor='#9b59b6', edgecolor='black', linewidth=2, alpha=0.8)
ax.add_patch(xfmr)
ax.text(10.5, 8.6, 'Flyback\nXfmr\n1:30', ha='center', va='center', 
        fontsize=8, fontweight='bold', color='white')

# IRF840 (switching)
irf840 = FancyBboxPatch((9.8, 6.2), 1.0, 0.8, boxstyle="round,pad=0.02",
                         facecolor=c_hv, edgecolor='black', linewidth=1.5, alpha=0.85)
ax.add_patch(irf840)
ax.text(10.3, 6.7, 'IRF840\n500V', ha='center', va='center', 
        fontsize=8, fontweight='bold', color='white')

# Flyback connections
ax.plot([9.2, 9.8], [8.3, 8.3], color=c_logic, linewidth=2)  # UC3843 to xfmr
ax.plot([10.5, 10.3], [7.8, 7.0], color='black', linewidth=1.5)  # xfmr to IRF840 drain
ax.plot([10.3, 10.3], [6.2, 5.5], color='black', linewidth=1.5)  # IRF840 source to GND
ax.plot([11.5, 11.5], [8.4, 8.4], color=c_hv, linewidth=2)  # HV output from xfmr

# MUR460 output diode
diode = FancyBboxPatch((11.3, 7.9), 0.6, 0.4, boxstyle="round,pad=0.02",
                        facecolor='#e67e22', edgecolor='black', linewidth=1)
ax.add_patch(diode)
ax.text(11.6, 8.15, 'MUR460', ha='center', va='center', fontsize=6, fontweight='bold')

# HV capacitor + rail
hv_cap = FancyBboxPatch((12.2, 7.8), 1.0, 1.0, boxstyle="round,pad=0.05",
                         facecolor=c_hv, edgecolor='black', linewidth=2, alpha=0.6)
ax.add_patch(hv_cap)
ax.text(12.7, 8.5, '10µF\n450V', ha='center', va='center', 
        fontsize=9, fontweight='bold', color='white')

ax.plot([11.9, 12.2], [8.3, 8.3], color=c_hv, linewidth=3)  # HV rail
ax.text(12.05, 8.55, '+HV', ha='center', va='bottom', fontsize=8, fontweight='bold', color=c_hv)

# Bleeder resistor
ax.plot([12.7, 12.7], [7.8, 7.3], color=c_hv, linewidth=1.5)
bleed = Rectangle((12.5, 7.0), 0.4, 0.3, facecolor='white', edgecolor='black', linewidth=1)
ax.add_patch(bleed)
ax.text(12.7, 6.85, '100kΩ', ha='center', va='top', fontsize=7)
ax.plot([12.7, 12.7], [7.0, 6.5], color=c_ground, linewidth=1.5)
ax.text(12.7, 6.4, 'GND', ha='center', va='top', fontsize=7, color=c_ground)

# HV indicator LED
ax.plot([11.8, 11.8], [7.7, 7.3], color=c_hv, linewidth=1)
led = Circle((11.8, 7.1), 0.15, facecolor='red', edgecolor='black', linewidth=1)
ax.add_patch(led)
ax.text(11.8, 6.85, 'HV ON', ha='center', va='top', fontsize=6, color=c_hv, fontweight='bold')

# ─────────────────────────────────────────────────────────────────
# TRIGGER / CONTROL SECTION (Middle Left)
# ─────────────────────────────────────────────────────────────────
# Trigger input
ax.text(0.8, 5.8, 'TRIGGER', ha='center', va='center', 
        fontsize=9, fontweight='bold', color=c_text)
trigger_box = FancyBboxPatch((0.2, 5.2), 1.2, 0.8, boxstyle="round,pad=0.02",
                              facecolor=c_logic, edgecolor='black', linewidth=1)
ax.add_patch(trigger_box)
ax.text(0.8, 5.6, 'BNC\nfrom RP', ha='center', va='center', fontsize=7, color='white')

# TC4427
tc = FancyBboxPatch((2.0, 5.0), 1.2, 1.0, boxstyle="round,pad=0.05",
                     facecolor=c_logic, edgecolor='black', linewidth=1.5, alpha=0.85)
ax.add_patch(tc)
ax.text(2.6, 5.7, 'TC4427\nGate\nDriver', ha='center', va='center', 
        fontsize=8, fontweight='bold', color='white')

ax.plot([1.4, 2.0], [5.6, 5.6], color=c_logic, linewidth=2)

# Arduino Nano (optional control)
arduino = FancyBboxPatch((0.2, 3.5), 1.6, 1.2, boxstyle="round,pad=0.05",
                          facecolor='#16a085', edgecolor='black', linewidth=1.5, alpha=0.85)
ax.add_patch(arduino)
ax.text(1.0, 4.3, 'Arduino\nNano', ha='center', va='center', 
        fontsize=8, fontweight='bold', color='white')
ax.text(1.0, 3.8, '(optional)', ha='center', va='center', fontsize=7, color='#ecf0f1')

ax.plot([1.8, 2.0], [4.0, 5.0], color='#16a085', linewidth=1.5, linestyle='--')
ax.text(1.7, 4.5, 'D9', ha='center', va='center', fontsize=7, color='#16a085')

# 5V rail to Arduino
ax.plot([1.0, 1.0], [4.7, 7.3], color=c_power, linewidth=1.5, linestyle='--', alpha=0.5)

# ─────────────────────────────────────────────────────────────────
# PULSE OUTPUT SECTION (Center)
# ─────────────────────────────────────────────────────────────────
# IRF830 (output stage)
irf830 = FancyBboxPatch((4.5, 5.0), 1.0, 0.8, boxstyle="round,pad=0.02",
                         facecolor=c_hv, edgecolor='black', linewidth=1.5, alpha=0.85)
ax.add_patch(irf830)
ax.text(5.0, 5.5, 'IRF830\n500V', ha='center', va='center', 
        fontsize=8, fontweight='bold', color='white')

ax.plot([3.2, 4.5], [5.6, 5.6], color=c_logic, linewidth=2)  # TC4427 to IRF830 gate

# Gate protection
ax.plot([4.5, 4.3], [5.6, 5.9], color='black', linewidth=1)
ax.text(4.1, 6.0, '12V\nZener', ha='center', va='bottom', fontsize=6)

# Pulse transformer
pulse_xfmr = FancyBboxPatch((6.0, 4.8), 1.4, 1.4, boxstyle="round,pad=0.05",
                             facecolor='#9b59b6', edgecolor='black', linewidth=2, alpha=0.8)
ax.add_patch(pulse_xfmr)
ax.text(6.7, 5.7, 'Pulse\nXfmr\n1:1', ha='center', va='center', 
        fontsize=8, fontweight='bold', color='white')

ax.plot([5.5, 6.0], [5.4, 5.4], color='black', linewidth=2)  # IRF830 drain to xfmr

# Damping cap
ax.plot([6.7, 6.7], [6.2, 6.8], color='black', linewidth=1)
cap_damp = Rectangle((6.5, 6.8), 0.4, 0.3, facecolor=c_hv, edgecolor='black', linewidth=1)
ax.add_patch(cap_damp)
ax.text(6.7, 7.15, '10µF', ha='center', va='bottom', fontsize=6, color=c_hv)
ax.plot([6.7, 6.7], [7.1, 7.8], color=c_hv, linewidth=2)  # to HV rail

# HV feed to pulse transformer
ax.plot([10.0, 7.4], [8.3, 8.3], color=c_hv, linewidth=2)
ax.plot([7.4, 7.4], [8.3, 6.2], color=c_hv, linewidth=2)
ax.plot([7.4, 7.4], [6.2, 5.9], color=c_hv, linewidth=1.5)
ax.text(7.6, 6.0, '+HV', ha='left', va='center', fontsize=7, color=c_hv, fontweight='bold')

# Output diode (MUR460)
out_diode = FancyBboxPatch((7.8, 4.9), 0.6, 0.4, boxstyle="round,pad=0.02",
                            facecolor='#e67e22', edgecolor='black', linewidth=1)
ax.add_patch(out_diode)
ax.text(8.1, 5.15, 'MUR460', ha='center', va='center', fontsize=6, fontweight='bold')

# BNC output
bnc = FancyBboxPatch((9.0, 4.8), 1.0, 0.8, boxstyle="round,pad=0.05",
                      facecolor=c_output, edgecolor='black', linewidth=2, alpha=0.85)
ax.add_patch(bnc)
ax.text(9.5, 5.3, 'BNC\nOUTPUT', ha='center', va='center', 
        fontsize=9, fontweight='bold', color='white')

ax.plot([8.4, 9.0], [5.2, 5.2], color='black', linewidth=2)

# Coax to V5
ax.plot([10.0, 11.5], [5.2, 5.2], color=c_output, linewidth=3, alpha=0.7)
ax.text(10.75, 5.45, '→ V5 TX_IN', ha='center', va='bottom', 
        fontsize=9, fontweight='bold', color=c_output)

# TVS protection
tvs = FancyBboxPatch((8.5, 4.3), 0.5, 0.3, boxstyle="round,pad=0.02",
                      facecolor='#f1c40f', edgecolor='black', linewidth=1)
ax.add_patch(tvs)
ax.text(8.75, 4.45, 'TVS\n400V', ha='center', va='center', fontsize=6, fontweight='bold')

# ─────────────────────────────────────────────────────────────────
# GROUND PLANE
# ─────────────────────────────────────────────────────────────────
# GND rail
ax.plot([0.5, 13.5], [1.5, 1.5], color=c_ground, linewidth=3, alpha=0.6)
ax.text(7, 1.2, 'GND RAIL', ha='center', va='top', fontsize=10, fontweight='bold', color=c_ground)

# Ground connections
for gx in [1.2, 3.6, 5.0, 7.0, 8.6, 10.3, 10.5, 12.7]:
    ax.plot([gx, gx], [1.5, 2.0], color=c_ground, linewidth=1.5)
    ax.plot([gx-0.1, gx+0.1], [2.0, 2.0], color=c_ground, linewidth=1.5)
    ax.plot([gx-0.2, gx+0.2], [2.1, 2.1], color=c_ground, linewidth=1.5)

# ─────────────────────────────────────────────────────────────────
# SAFETY BOX
# ─────────────────────────────────────────────────────────────────
safety = FancyBboxPatch((0.2, 0.2), 4.0, 1.0, boxstyle="round,pad=0.05",
                         facecolor='#fdf2e9', edgecolor='#e74c3c', linewidth=2, linestyle='--')
ax.add_patch(safety)
ax.text(2.2, 0.9, 'SAFETY', ha='center', va='center', 
        fontsize=9, fontweight='bold', color='#e74c3c')
ax.text(2.2, 0.5, 'Bleeder: 100kΩ 2W | LED: HV indicator | Fuse: 3A | Interlock: lid switch',
        ha='center', va='center', fontsize=7, color=c_text)

# ─────────────────────────────────────────────────────────────────
# LEGEND / ANNOTATIONS
# ─────────────────────────────────────────────────────────────────
legend_items = [
    (c_power, 'Power / 12V'),
    (c_hv, 'High Voltage (100–400V)'),
    (c_logic, 'Logic / Control'),
    (c_output, 'Output / BNC'),
    ('#9b59b6', 'Transformer'),
    ('#e67e22', 'Diode'),
]

for i, (color, label) in enumerate(legend_items):
    x = 5.0 + i * 1.5
    ax.plot([x, x+0.3], [0.5, 0.5], color=color, linewidth=4)
    ax.text(x+0.4, 0.5, label, ha='left', va='center', fontsize=7)

# ─────────────────────────────────────────────────────────────────
# PERFORMANCE BOX
# ─────────────────────────────────────────────────────────────────
perf = FancyBboxPatch((10.5, 0.2), 3.3, 1.0, boxstyle="round,pad=0.05",
                        facecolor='#e8f6f3', edgecolor='#1abc9c', linewidth=2)
ax.add_patch(perf)
ax.text(12.15, 0.9, 'PERFORMANCE', ha='center', va='center', 
        fontsize=9, fontweight='bold', color='#16a085')
ax.text(12.15, 0.5, 'Output: 50–400V | Pulse: 50ns–10µs | PRF: 1–1kHz | Cost: ~£40',
        ha='center', va='center', fontsize=7, color=c_text)

plt.tight_layout()
plt.savefig('pulser_400v_schematic.png', dpi=150, bbox_inches='tight', facecolor='white')
print("✓ Saved: pulser_400v_schematic.png")
