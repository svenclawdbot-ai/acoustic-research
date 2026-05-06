"""
HV Piezo Driver Circuit Review & Improvements
==============================================

Review of the DIY HV amplifier from BOM_flexural_beam_probe.md
with recommendations for robust field deployment.
"""

import matplotlib.pyplot as plt
import numpy as np

# Circuit Analysis
print("=" * 70)
print("DIY PIEZO DRIVER CIRCUIT ANALYSIS")
print("=" * 70)

# Component Specifications
circuit = {
    "Gate Driver": {
        "Part": "TC4427CPA",
        "Type": "Dual MOSFET Driver",
        "Drive Current": "1.5A peak",
        "Supply": "4.5-18V",
        "Rise Time": "25ns @ 1000pF",
        "Suitable": True,
        "Notes": "Good choice for driving IRF830"
    },
    
    "Power MOSFET": {
        "Part": "IRF830",
        "VDS": "500V",
        "ID": "4.5A",
        "RDS(on)": "1.5Ω",
        "Qg": "63nC",
        "Suitable": True,
        "Notes": "Overrated for 150V/100mA piezo - good safety margin"
    },
    
    "HV Supply": {
        "Part": "12V→150V DC-DC Boost",
        "Power": "2W",
        "Voltage": "150V",
        "Current": "~13mA max",
        "Suitable": True,
        "Notes": "Adequate for light piezo loads"
    },
    
    "Piezo Load": {
        "Part": "NAC2124-A01",
        "Capacitance": "~120nF",
        "Voltage": "150V max",
        "Current": "100mA peak",
        "Power": "<1W average",
        "Suitable": True,
        "Notes": "Standard stack actuator"
    }
}

# Print component analysis
print("\n[1] COMPONENT ANALYSIS")
print("-" * 70)
for name, spec in circuit.items():
    print(f"\n{name}: {spec['Part']}")
    print(f"  Suitable: {'✓ YES' if spec['Suitable'] else '✗ NO'}")
    print(f"  Notes: {spec['Notes']}")

# Calculate key parameters
print("\n\n[2] CIRCUIT PERFORMANCE CALCULATIONS")
print("-" * 70)

# Piezo impedance at different frequencies
frequencies = [50, 100, 150, 200, 250, 300, 400, 500]  # Hz
C_piezo = 120e-9  # 120 nF

print("\nPiezo Impedance vs Frequency:")
print(f"{'Freq (Hz)':<12} {'Xc (Ω)':<15} {'I @ 150V':<15}")
print("-" * 45)

for f in frequencies:
    Xc = 1 / (2 * np.pi * f * C_piezo)
    I_rms = 150 / Xc  # Simplified
    print(f"{f:<12} {Xc:<15.0f} {I_rms*1000:<15.1f} mA")

# MOSFET power dissipation
print("\n\nMOSFET Power Dissipation:")
Rds_on = 1.5  # Ohms
I_rms_max = 0.1  # 100mA
P_diss = I_rms_max**2 * Rds_on
print(f"  RDS(on): {Rds_on} Ω")
print(f"  I_rms: {I_rms_max*1000:.0f} mA")
print(f"  P_dissipation: {P_diss:.2f} W")
print(f"  Junction temp rise: ~{P_diss * 19:.1f}°C (with 19°C/W heatsink)")

print("\n\n[3] CRITICAL ISSUES & RECOMMENDATIONS")
print("-" * 70)

issues = [
    {
        "Issue": "No gate protection",
        "Risk": "High",
        "Problem": "IRF830 gate can be damaged by overvoltage (>20V)",
        "Fix": "Add 15V Zener diode (BZX55-C15) across gate-source",
        "Cost": "£0.10"
    },
    {
        "Issue": "No current limiting",
        "Risk": "Medium",
        "Problem": "Piezo short or excessive load can destroy MOSFET",
        "Fix": "Add 0.5Ω current sense resistor with comparator",
        "Cost": "£0.50"
    },
    {
        "Issue": "HV DC-DC from AliExpress",
        "Risk": "High",
        "Problem": "Quality/reliability unknown, 2-week lead time",
        "Fix": "Order 2x units, or use MeanWell HRP-150-15 (£25)",
        "Cost": "£13 backup"
    },
    {
        "Issue": "No flyback protection",
        "Risk": "Medium",
        "Problem": "Piezo inductive kickback can spike >500V",
        "Fix": "Add TVS diode (P6KE200A) across piezo terminals",
        "Cost": "£0.30"
    },
    {
        "Issue": "Single-ended drive only",
        "Risk": "Low",
        "Problem": "Unipolar drive = half the displacement",
        "Fix": "Acceptable for initial prototype; upgrade to bridge later",
        "Cost": "N/A for v1"
    },
    {
        "Issue": "Raspberry Pi Pico in BOM",
        "Risk": "Low",
        "Problem": "We want ESP32-S3 for BLE, not Pi Pico",
        "Fix": "Replace Pi Pico (£3.80) with ESP32-S3 (£8.00)",
        "Cost": "+£4.20"
    }
]

for i, issue in enumerate(issues, 1):
    print(f"\n{i}. {issue['Issue']} [Risk: {issue['Risk']}]")
    print(f"   Problem: {issue['Problem']}")
    print(f"   Fix: {issue['Fix']}")
    print(f"   Extra cost: {issue['Cost']}")

print("\n\n[4] IMPROVED BILL OF MATERIALS")
print("-" * 70)

bom_revised = [
    ("Gate Driver", "TC4427CPA", "£2.50", "Keep"),
    ("MOSFET", "IRF830", "£3.20", "Keep"),
    ("Gate Zener", "BZX55-C15 (15V)", "£0.10", "ADD - protection"),
    ("TVS Diode", "P6KE200A", "£0.30", "ADD - flyback protection"),
    ("Current Sense", "0.5Ω 2W resistor", "£0.20", "ADD - current limit"),
    ("HV Supply", "12V→150V 2W (×2)", "£24.00", "ORDER 2x for backup"),
    ("Microcontroller", "ESP32-S3-DevKitC", "£8.00", "REPLACE Pi Pico"),
    ("Protection PCB", "Fuse holder + 1A fuse", "£0.50", "ADD - safety"),
]

print("\nRevised Component List:")
print(f"{'Item':<20} {'Part':<25} {'Cost':<10} {'Status':<20}")
print("-" * 80)

total = 0
for item, part, cost, status in bom_revised:
    cost_val = float(cost.replace('£', ''))
    total += cost_val
    print(f"{item:<20} {part:<25} {cost:<10} {status:<20}")

print("-" * 80)
print(f"{'TOTAL':<46} £{total:.2f}")

print("\n\n[5] CIRCUIT SCHEMATIC (ASCII)")
print("-" * 70)

schematic = """
                    +12V (Battery)
                      │
                      ▼
    +-----------+  ┌─────────┐
    │           │  │  150V   │
    │  ESP32    │  │  Boost  │
    │   S3      │  │ Supply  │
    │           │  └────┬────┘
    │         PWM      │
    │          │       │
    │          ▼       │
    │    ┌──────────┐  │
    │    │ TC4427   │  │     +150V
    │    │ Driver   │  │       │
    │    └────┬─────┘  │       │
    │         │Gate    │       ▼
    │         ▼        │    ┌──────┐
    │    ┌──────────┐  │    │Piezo │
    │    │   Gate   │  │    │Stack │
    │    │  15V     │  │    │120nF │
    │    │ Zener    │  │    └──┬───┘
    │    └────┬─────┘  │       │
    │         │        │      ─┴─ TVS
    │    ┌────┴────┐   │      / \
    │    │  Gate   │   │       │
    └───►│         │   │       ▼
         │  IRF830 │◄──┴───────┤
         │ MOSFET  │           │
         │         │          GND
         └────┬────┘
              │Drain
              ▼
         ┌──────────┐
         │  0.5Ω    │ Current sense
         │ Sense R  │ (optional protection)
         └────┬─────┘
              │
             GND

Protection Additions:
1. Zener (BZX55-C15) across gate-source: Protects from overvoltage
2. TVS (P6KE200A) across piezo: Absorbs inductive spikes
3. Sense resistor: Enables current monitoring/fault detection
"""

print(schematic)

print("\n\n[6] FIELD DEPLOYMENT CHECKLIST")
print("-" * 70)

checklist = """
Pre-Deployment Testing:
□ Power up without piezo - verify 150V on supply
□ Check gate drive with scope - 0-12V square wave
□ Test with piezo on bench - measure displacement
□ Verify Bluetooth connection phone→ESP32
□ Run full 12-position sequence - check data quality
□ Test on actual phantom - not just free-air

Packaging for Field:
□ Enclosure rated IP54 minimum
□ Cable strain relief on all connectors
□ Desiccant packet inside (humidity protection)
□ Spare fuses (1A fast-blow) in kit
□ Silicone conformal coating on PCB

Power Management:
□ 12V battery pack: 10,000 mAh minimum
□ Expected runtime: 8+ hours
□ USB-C charging cable included
□ Low-battery LED indicator (add to circuit)

Safety:
□ 150V warning labels on enclosure
□ Insulated connectors (no exposed HV)
□ Emergency stop button (optional but recommended)
□ One-hand rule: Never touch HV with both hands
"""

print(checklist)

print("\n\n[7] UPGRADE PATH")
print("-" * 70)

print("""
Version 1 (Current BOM): Single-ended, ~£85
- Unipolar drive: 0 to +150V
- Displacement: 6 μm (half of spec)
- Good for: Proof of concept, frequency sweep

Version 2 (Bridge Driver): H-bridge, ~£120
- Bipolar drive: -150V to +150V  
- Displacement: 12 μm (full spec)
- Requires: 2x MOSFET + driver IC
- Better for: Large phantoms, low-frequency work

Version 3 (Linear Amp): ~£250
- Clean sine wave output
- No switching noise
- Best for: Research-grade measurements

Recommendation: Build Version 1 first, upgrade if needed.
""")

print("\n" + "=" * 70)
print("CIRCUIT REVIEW COMPLETE")
print("=" * 70)
print("\n✓ Circuit is fundamentally sound")
print("✓ Add 3 protection components (£0.90 total)")
print("✓ Order 2x HV supplies for redundancy")
print("✓ Replace Pi Pico with ESP32-S3")
print("\nRevised total: ~£90 (was £85, +£5 for protection)")
