import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, Circle, Rectangle, FancyArrowPatch
import numpy as np

# Use non-interactive backend
import matplotlib
matplotlib.use('Agg')

fig, ax = plt.subplots(1, 1, figsize=(16, 12))
ax.set_xlim(0, 16)
ax.set_ylim(0, 12)
ax.set_aspect('equal')
ax.axis('off')
ax.set_title('Hybrid Soil Spectrometer — Wiring Diagram\nSTM32 Nucleo-H743 + ESP32-S3 + AD9833 + OPA1641 + RFM95W', 
             fontsize=14, fontweight='bold', pad=20)

# Color scheme
c_nucleo = '#1f77b4'    # blue
c_esp32 = '#ff7f0e'     # orange
c_ad9833 = '#2ca02c'    # green
c_opa = '#d62728'       # red
c_lora = '#9467bd'      # purple
c_electrode = '#8c564b' # brown
c_power = '#bcbd22'     # yellow-green
c_signal = '#e377c2'    # pink

# =============================================================================
# MODULE BOXES
# =============================================================================

def draw_module(ax, x, y, w, h, color, label, pins_left=None, pins_right=None, pins_top=None, pins_bottom=None):
    """Draw a module box with pins."""
    rect = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.05", 
                          facecolor=color, edgecolor='black', linewidth=2, alpha=0.85)
    ax.add_patch(rect)
    ax.text(x + w/2, y + h/2, label, ha='center', va='center', 
            fontsize=10, fontweight='bold', color='white',
            bbox=dict(boxstyle='round', facecolor=color, alpha=0.9, edgecolor='none'))
    
    # Draw pins
    pin_h = 0.15
    for i, pin in enumerate(pins_left or []):
        py = y + h - 0.3 - i * 0.25
        ax.plot([x-0.2, x], [py, py], 'k-', lw=1.5)
        ax.text(x-0.25, py, pin, ha='right', va='center', fontsize=7, family='monospace')
    
    for i, pin in enumerate(pins_right or []):
        py = y + h - 0.3 - i * 0.25
        ax.plot([x+w, x+w+0.2], [py, py], 'k-', lw=1.5)
        ax.text(x+w+0.25, py, pin, ha='left', va='center', fontsize=7, family='monospace')
    
    for i, pin in enumerate(pins_top or []):
        px = x + 0.3 + i * 0.4
        ax.plot([px, px], [y+h, y+h+0.2], 'k-', lw=1.5)
        ax.text(px, y+h+0.35, pin, ha='center', va='bottom', fontsize=7, family='monospace', rotation=45)
    
    for i, pin in enumerate(pins_bottom or []):
        px = x + 0.3 + i * 0.4
        ax.plot([px, px], [y, y-0.2], 'k-', lw=1.5)
        ax.text(px, y-0.35, pin, ha='center', va='top', fontsize=7, family='monospace', rotation=45)

# NUCLEO-H743 (left side)
draw_module(ax, 0.5, 7.5, 2.5, 3.5, c_nucleo, 'Nucleo-H743ZI2\n(STM32H743)',
            pins_left=['3.3V', 'GND', 'A0/PA3', 'D13/PA5', 'D11/PA7', 'D10/PA15', 'D1/PA9', 'D0/PA10'],
            pins_right=['5V', 'GND', 'VIN'])

# AD9833 DDS (top middle)
draw_module(ax, 5.0, 9.5, 2.0, 1.5, c_ad9833, 'AD9833\nDDS Module',
            pins_left=['VCC', 'GND', 'SCLK', 'SDATA', 'FSYNC'],
            pins_right=['OUT', 'AGND'])

# OPA1641 Buffer (top right of AD9833)
draw_module(ax, 8.0, 9.5, 1.8, 1.5, c_opa, 'OPA1641\nBuffer',
            pins_left=['V+', 'IN+', 'IN-', 'V-', 'OUT'],
            pins_right=[])

# OPA1641 TIA (middle)
draw_module(ax, 5.0, 6.0, 1.8, 1.5, c_opa, 'OPA1641\nTIA',
            pins_left=['V+', 'IN+', 'IN-', 'V-', 'OUT'],
            pins_right=[])

# ESP32-S3 (right side)
draw_module(ax, 12.5, 7.5, 2.5, 3.5, c_esp32, 'ESP32-S3\nDevKitC-1',
            pins_left=['3.3V', 'GND', 'GPIO43/TX', 'GPIO44/RX', 'GPIO5/SCK', 'GPIO6/MISO', 'GPIO7/MOSI', 'GPIO10/CS'],
            pins_right=['5V', 'GND', 'USB'])

# RFM95W LoRa (below ESP32)
draw_module(ax, 12.5, 4.0, 2.0, 1.5, c_lora, 'RFM95W\nLoRa 868MHz',
            pins_left=['VCC', 'GND', 'SCK', 'MISO', 'MOSI', 'CS', 'DIO0', 'RESET'],
            pins_right=['ANT'])

# Electrodes (bottom)
# Soil block
soil_rect = FancyBboxPatch((5.5, 1.0), 4.0, 2.0, boxstyle="round,pad=0.1",
                             facecolor='#DEB887', edgecolor=c_electrode, linewidth=2, alpha=0.7)
ax.add_patch(soil_rect)
ax.text(7.5, 2.0, 'SOIL\n(Z_soil)', ha='center', va='center', 
        fontsize=11, fontweight='bold', color=c_electrode)

# Electrodes
def draw_electrode(ax, x, y, label):
    rect = Rectangle((x-0.1, y), 0.2, 1.5, facecolor='silver', edgecolor='black', linewidth=1.5)
    ax.add_patch(rect)
    ax.text(x, y-0.3, label, ha='center', va='top', fontsize=9, fontweight='bold')

draw_electrode(ax, 6.0, 3.0, 'A\n(Drive)')
draw_electrode(ax, 7.0, 3.0, 'B\n(Sense)')
draw_electrode(ax, 8.0, 3.0, 'C\n(Ref)')
draw_electrode(ax, 9.0, 3.0, 'D\n(Ref)')

# =============================================================================
# WIRE CONNECTIONS
# =============================================================================

def draw_wire(ax, x1, y1, x2, y2, color, label=None, style='-', lw=1.5, offset=(0,0)):
    """Draw a wire with optional label."""
    if style == '--':
        ax.plot([x1, x2], [y1, y2], color=color, linestyle='--', linewidth=lw, alpha=0.7)
    else:
        # Draw with slight curve for cleaner look
        mid_x = (x1 + x2) / 2 + offset[0]
        mid_y = (y1 + y2) / 2 + offset[1]
        t = np.linspace(0, 1, 50)
        # Quadratic Bezier
        x = (1-t)**2 * x1 + 2*(1-t)*t * mid_x + t**2 * x2
        y = (1-t)**2 * y1 + 2*(1-t)*t * mid_y + t**2 * y2
        ax.plot(x, y, color=color, linewidth=lw, alpha=0.8)
    
    if label:
        lx = (x1 + x2) / 2 + offset[0] * 0.3
        ly = (y1 + y2) / 2 + offset[1] * 0.3
        ax.text(lx, ly, label, ha='center', va='center', 
                fontsize=7, color=color, fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.9, edgecolor=color))

# Power rails
ax.plot([0.5, 15.5], [11.3, 11.3], color=c_power, linewidth=3, alpha=0.5)
ax.text(8, 11.5, '+3.3V RAIL', ha='center', va='bottom', fontsize=9, color=c_power, fontweight='bold')
ax.plot([0.5, 15.5], [10.8, 10.8], color='black', linewidth=3, alpha=0.5)
ax.text(8, 10.6, 'GND RAIL', ha='center', va='top', fontsize=9, color='black', fontweight='bold')

# Nucleo power connections
draw_wire(ax, 0.3, 10.0, 0.3, 11.3, c_power, '3.3V', offset=(0,0.2))
draw_wire(ax, 0.3, 9.5, 0.3, 10.8, 'black', 'GND', offset=(0,-0.2))

# AD9833 power
draw_wire(ax, 4.8, 10.2, 4.8, 11.3, c_power, 'VCC', offset=(-0.3,0))
draw_wire(ax, 4.8, 9.8, 4.8, 10.8, 'black', 'GND', offset=(-0.3,0))

# SPI: Nucleo → AD9833
draw_wire(ax, 3.0, 9.8, 4.8, 9.8, '#17becf', 'D13/PA5→SCLK', offset=(0,0.3), lw=2)
draw_wire(ax, 3.0, 9.3, 4.8, 9.3, '#17becf', 'D11/PA7→SDATA', offset=(0,0.3), lw=2)
draw_wire(ax, 3.0, 8.8, 4.8, 8.8, '#17becf', 'D10/PA15→FSYNC', offset=(0,0.3), lw=2)

# AD9833 OUT → Buffer IN
draw_wire(ax, 7.0, 10.25, 8.0, 10.0, c_signal, 'Sine Out', offset=(0,0.2), lw=2)

# Buffer OUT → Electrode A (through 100Ω series)
draw_wire(ax, 9.8, 10.0, 9.8, 9.5, c_signal, '', lw=1)
# 100Ω resistor symbol
ax.plot([9.7, 9.9], [9.5, 9.5], 'k-', lw=2)
ax.text(9.8, 9.7, '100Ω', ha='center', va='bottom', fontsize=7)
draw_wire(ax, 9.8, 9.5, 9.8, 8.5, c_signal, '', lw=1)
# Then to electrode A via wire
draw_wire(ax, 9.8, 8.5, 6.0, 4.5, c_signal, '→A', offset=(0.5,0.3), lw=1.5)

# Electrode B → TIA IN-
draw_wire(ax, 7.0, 4.5, 7.0, 6.0, c_signal, 'B→TIA', offset=(-0.3,0), lw=1.5)

# TIA feedback resistor (1kΩ)
ax.plot([5.9, 6.9], [6.75, 6.75], 'k-', lw=2)
ax.text(6.4, 6.95, '1kΩ', ha='center', va='bottom', fontsize=7)

# TIA OUT → Nucleo ADC
draw_wire(ax, 5.0, 6.75, 3.0, 8.5, '#e377c2', 'TIA→A0/PA3', offset=(-0.3,0), lw=2)

# Nucleo UART → ESP32 UART
draw_wire(ax, 3.0, 7.5, 7.5, 7.5, '#ff7f0e', 'D1/PA9→GPIO44 RX', offset=(0,0.4), lw=2)
draw_wire(ax, 3.0, 7.0, 7.5, 7.0, '#ff7f0e', 'D0/PA10→GPIO43 TX', offset=(0,-0.4), lw=2)

# ESP32 power
draw_wire(ax, 12.3, 10.0, 12.3, 11.3, c_power, '3.3V', offset=(0,0.2))
draw_wire(ax, 12.3, 9.5, 12.3, 10.8, 'black', 'GND', offset=(0,-0.2))

# ESP32 SPI → RFM95W
draw_wire(ax, 12.3, 7.5, 12.3, 5.0, c_lora, 'GPIO5→SCK', offset=(-0.4,0), lw=1.5)
draw_wire(ax, 12.3, 7.0, 12.3, 4.5, c_lora, 'GPIO6→MISO', offset=(-0.4,0), lw=1.5)
draw_wire(ax, 12.3, 6.5, 12.3, 4.0, c_lora, 'GPIO7→MOSI', offset=(-0.4,0), lw=1.5)
draw_wire(ax, 14.0, 8.5, 14.5, 5.5, c_lora, 'GPIO10→CS', offset=(0.3,0), lw=1.5)
draw_wire(ax, 14.0, 8.0, 14.5, 4.5, c_lora, 'GPIO11→DIO0', offset=(0.3,0), lw=1.5)
draw_wire(ax, 14.0, 7.5, 14.5, 4.0, c_lora, 'GPIO12→RESET', offset=(0.3,0), lw=1.5)

# RFM95W power
draw_wire(ax, 12.3, 5.0, 12.3, 4.0, c_power, 'VCC', offset=(0,0.1), lw=1)
draw_wire(ax, 12.3, 4.5, 12.3, 4.0, 'black', 'GND', offset=(0,-0.1), lw=1)

# Antenna
draw_wire(ax, 14.5, 4.75, 15.5, 4.75, '#9467bd', 'ANT', offset=(0,0.2), lw=2)
ax.text(15.6, 4.75, '868MHz\nAntenna', ha='left', va='center', fontsize=8, color=c_lora)

# =============================================================================
# LEGEND
# =============================================================================
legend_y = 0.3
legend_items = [
    (c_nucleo, 'STM32 Nucleo-H743 (Measurement Core)'),
    (c_esp32, 'ESP32-S3 (Wireless Bridge)'),
    (c_ad9833, 'AD9833 DDS (Sine Generator)'),
    (c_opa, 'OPA1641 (TIA + Buffer)'),
    (c_lora, 'RFM95W LoRa Module'),
    (c_electrode, 'Stainless Steel Electrodes'),
    ('#17becf', 'SPI Bus'),
    (c_signal, 'Analog Signal Path'),
    ('#ff7f0e', 'UART Data Link'),
]

for i, (color, label) in enumerate(legend_items):
    x = 0.5 + (i % 3) * 5.0
    y = legend_y + (i // 3) * 0.4
    ax.plot([x, x+0.3], [y, y], color=color, linewidth=3)
    ax.text(x+0.4, y, label, ha='left', va='center', fontsize=8)

plt.tight_layout()
plt.savefig('hybrid_spectrometer_wiring.png', dpi=150, bbox_inches='tight', facecolor='white')
print("✓ Saved: hybrid_spectrometer_wiring.png")
