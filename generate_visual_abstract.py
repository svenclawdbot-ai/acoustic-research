import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrowPatch, FancyBboxPatch, Circle, Wedge
import matplotlib.patches as mpatches

fig = plt.figure(figsize=(11, 8))
fig.patch.set_facecolor('white')

# Create 3-panel layout: left=schematic, middle=wave physics, right=result
# Main panel
ax_main = fig.add_axes([0.02, 0.35, 0.96, 0.60])
ax_main.set_xlim(0, 11)
ax_main.set_ylim(0, 5)
ax_main.axis('off')
ax_main.set_facecolor('white')

# Bottom panel for summary
ax_bottom = fig.add_axes([0.05, 0.02, 0.90, 0.28])
ax_bottom.set_xlim(0, 10)
ax_bottom.set_ylim(0, 10)
ax_bottom.axis('off')
ax_bottom.set_facecolor('#f8f8f8')

# ─────────────────────────────────────────────────────────────────
# PANEL A: The Setup (left side)
# ─────────────────────────────────────────────────────────────────

# Carbon fiber composite panel
panel = FancyBboxPatch((0.3, 1.0), 3.2, 3.5, boxstyle="round,pad=0.05",
                        facecolor='#2c3e50', edgecolor='black', linewidth=2)
ax_main.add_patch(panel)

# Carbon fiber weave pattern
for i in range(8):
    y = 1.2 + i * 0.4
    ax_main.plot([0.4, 3.4], [y, y+0.3], color='#34495e', linewidth=1, alpha=0.5)
    ax_main.plot([0.4, 3.4], [y+0.3, y], color='#34495e', linewidth=1, alpha=0.5)

# Defect (delamination)
defect = Rectangle((1.2, 2.0), 1.0, 0.15, facecolor='#e74c3c', edgecolor='none', alpha=0.8)
ax_main.add_patch(defect)
ax_main.text(1.7, 2.08, 'DELAMINATION', ha='center', va='center', fontsize=7,
             color='white', fontweight='bold', rotation=0)

# Ultrasound transducer
probe = FancyBboxPatch((1.3, 4.6), 0.8, 0.5, boxstyle="round,pad=0.02",
                        facecolor='#3498db', edgecolor='black', linewidth=1.5)
ax_main.add_patch(probe)
ax_main.text(1.7, 4.85, 'PROBE', ha='center', va='center', fontsize=7,
             color='white', fontweight='bold')

# Arrows: push pulse
for i in range(3):
    x = 1.0 + i * 0.4
    ax_main.annotate('', xy=(x, 4.5), xytext=(x, 4.7),
                    arrowprops=dict(arrowstyle='->', color='#3498db', lw=2))

# Shear wave propagation (concentric arcs)
for r in [0.5, 1.0, 1.5, 2.0]:
    wedge = Wedge((1.7, 3.5), r, 180, 360, fill=False, edgecolor='#e67e22',
                  linewidth=1.5, alpha=0.7, linestyle='--')
    ax_main.add_patch(wedge)

# Label A
ax_main.text(1.8, 0.5, 'A. EXPERIMENT', ha='center', va='bottom',
             fontsize=10, fontweight='bold', color='#2c3e50')

# ─────────────────────────────────────────────────────────────────
# PANEL B: The Physics (middle)
# ─────────────────────────────────────────────────────────────────

# Material cross-section showing waves
ax_main.add_patch(FancyBboxPatch((4.0, 1.0), 3.0, 3.5, boxstyle="round,pad=0.05",
                                  facecolor='#ecf0f1', edgecolor='black', linewidth=2))

# Healthy region: uniform wave pattern
x_healthy = np.linspace(4.2, 5.2, 50)
y_wave = 2.5 + 0.3 * np.sin(x_healthy * 8)
ax_main.plot(x_healthy, y_wave, color='#27ae60', linewidth=2.5, label='Healthy')
ax_main.fill_between(x_healthy, y_wave - 0.05, y_wave + 0.05, color='#27ae60', alpha=0.2)

# Defect region: wave slows + scatters
x_defect = np.linspace(5.2, 6.2, 50)
y_wave_defect = 2.5 + 0.3 * np.sin(x_defect * 5 + 0.5) * 0.6  # slower + attenuated
ax_main.plot(x_defect, y_wave_defect, color='#e74c3c', linewidth=2.5, label='Defect')
ax_main.fill_between(x_defect, y_wave_defect - 0.05, y_wave_defect + 0.05, color='#e74c3c', alpha=0.2)

# Arrow showing wave slows down
ax_main.annotate('', xy=(5.2, 3.0), xytext=(6.0, 3.0),
                arrowprops=dict(arrowstyle='->', color='#e67e22', lw=2))
ax_main.text(5.6, 3.15, 'SLOWER', ha='center', va='bottom', fontsize=8,
             color='#e67e22', fontweight='bold')

# Stiffness labels
ax_main.text(4.7, 1.5, 'Stiff: 45 kPa', ha='center', va='center',
             fontsize=8, color='#27ae60', fontweight='bold',
             bbox=dict(boxstyle='round', facecolor='white', edgecolor='#27ae60'))
ax_main.text(5.7, 1.5, 'Soft: 12 kPa', ha='center', va='center',
             fontsize=8, color='#e74c3c', fontweight='bold',
             bbox=dict(boxstyle='round', facecolor='white', edgecolor='#e74c3c'))

# Label B
ax_main.text(5.5, 0.5, 'B. PHYSICS', ha='center', va='bottom',
             fontsize=10, fontweight='bold', color='#2c3e50')

# ─────────────────────────────────────────────────────────────────
# PANEL C: The Result (right side)
# ─────────────────────────────────────────────────────────────────

# Stiffness map (heatmap mockup)
ax_main.add_patch(FancyBboxPatch((7.5, 1.0), 3.0, 3.5, boxstyle="round,pad=0.05",
                                  facecolor='white', edgecolor='black', linewidth=2))

# Create heatmap grid for stiffness map
grid_size = 15
x_grid = np.linspace(7.7, 10.3, grid_size)
y_grid = np.linspace(1.2, 4.3, grid_size)
X, Y = np.meshgrid(x_grid, y_grid)

# Stiffness values: uniform except defect region
defect_center_x, defect_center_y = 9.0, 2.8
defect_sigma = 0.4
Z = 40 - 25 * np.exp(-((X - defect_center_x)**2 + (Y - defect_center_y)**2) / (2 * defect_sigma**2))

# Plot heatmap
im = ax_main.pcolormesh(X, Y, Z, cmap='RdYlGn_r', shading='auto',
                        vmin=10, vmax=45, alpha=0.9)

# Add colorbar manually
for i, (val, color) in enumerate(zip([40, 30, 20, 10], ['#27ae60', '#f1c40f', '#e67e22', '#e74c3c'])):
    ax_main.add_patch(Rectangle((10.4, 1.2 + i * 0.7), 0.25, 0.5, facecolor=color))
    ax_main.text(10.75, 1.45 + i * 0.7, f'{val} kPa', ha='left', va='center', fontsize=7)

# Defect circle outline
circle = Circle((9.0, 2.8), 0.4, fill=False, edgecolor='white', linewidth=2, linestyle='--')
ax_main.add_patch(circle)
ax_main.text(9.0, 2.4, 'DEFECT', ha='center', va='top', fontsize=8,
             color='white', fontweight='bold')

# Label C
ax_main.text(9.0, 0.5, 'C. STIFFNESS MAP', ha='center', va='bottom',
             fontsize=10, fontweight='bold', color='#2c3e50')

# ─────────────────────────────────────────────────────────────────
# TITLE
# ─────────────────────────────────────────────────────────────────
ax_main.text(5.5, 5.5, 'Ultrasonic Shear Wave Elastography', ha='center', va='center',
             fontsize=16, fontweight='bold', color='#2c3e50')
ax_main.text(5.5, 5.15, 'for Non-Destructive Evaluation of Carbon Fiber Composites', ha='center', va='center',
             fontsize=13, color='#7f8c8d')

# ─────────────────────────────────────────────────────────────────
# BOTTOM PANEL: TEXT SUMMARY
# ─────────────────────────────────────────────────────────────────

# Title bar
ax_bottom.add_patch(Rectangle((0, 8.5), 10, 1.5, facecolor='#2c3e50', edgecolor='none'))
ax_bottom.text(5, 9.25, 'SUMMARY', ha='center', va='center',
               fontsize=12, fontweight='bold', color='white')

# 150-word summary
summary_text = """Carbon fiber composites are used in aircraft wings and wind turbine blades, but internal damage like delaminations is invisible until catastrophic failure. Traditional ultrasound checks for cracks by looking for echoes, but this misses early-stage stiffness changes.

We use shear wave elastography — the same technique doctors use to detect liver fibrosis — to map stiffness across composite panels. An ultrasonic probe pushes the material with acoustic force, generating shear waves. We track how fast these waves travel: healthy carbon fiber is stiff (≈45 kPa), while damaged areas soften dramatically (≈12 kPa). By scanning the probe across the surface, we build a 2D stiffness map that reveals hidden delaminations without disassembly.

On a 5 mm carbon-epoxy panel with artificial defects, we detected delaminations as small as 3 mm with 94% accuracy. The method is non-contact, requires no coupling gel, and works on curved surfaces."""

ax_bottom.text(0.3, 7.5, summary_text, ha='left', va='top',
               fontsize=9, color='#2c3e50', linespacing=1.6,
               wrap=True, transform=ax_bottom.transData)

# Takeaways box
ax_bottom.add_patch(FancyBboxPatch((0.3, 0.5), 4.5, 3.5, boxstyle="round,pad=0.1",
                                    facecolor='#ecf0f1', edgecolor='#bdc3c7', linewidth=1))
ax_bottom.text(2.55, 3.6, 'ENGINEER TAKEAWAYS', ha='center', va='center',
               fontsize=9, fontweight='bold', color='#2c3e50')

takeaways = [
    "• Shear wave speed is proportional to √(stiffness/density) — measure speed, infer damage",
    "• Delaminations reduce stiffness 2–4× before visible cracks form — early detection window",
    "• 8-channel phased array enables 50× faster scanning than single-element mechanical raster"
]
for i, t in enumerate(takeaways):
    ax_bottom.text(0.5, 3.0 - i * 0.8, t, ha='left', va='top',
                   fontsize=8, color='#2c3e50', linespacing=1.3,
                   wrap=True)

# Why it matters box
ax_bottom.add_patch(FancyBboxPatch((5.2, 0.5), 4.5, 3.5, boxstyle="round,pad=0.1",
                                    facecolor='#e8f6f3', edgecolor='#1abc9c', linewidth=2))
ax_bottom.text(7.45, 3.6, 'WHY THIS MATTERS', ha='center', va='center',
               fontsize=9, fontweight='bold', color='#16a085')

ax_bottom.text(5.4, 2.5, '"Airline passengers and wind energy consumers rely on carbon fiber structures that silently degrade from the inside — this technique spots that degradation before it becomes dangerous, without taking the plane apart."',
               ha='left', va='top', fontsize=9, color='#2c3e50',
               linespacing=1.4, wrap=True, style='italic')

plt.savefig('visual_abstract_swe_composites.png', dpi=150, bbox_inches='tight',
            facecolor='white', edgecolor='none')
print("✓ Saved: visual_abstract_swe_composites.png")
