#!/usr/bin/env python3
"""
Compost Validation Script
=========================
Calibrates the soil impedance model against real glasshouse compost samples.
Run this after collecting dry, moist, and saturated compost measurements.

Usage:
    python validate_compost.py --dry-z 850 --moist-z 320 --saturated-z 95

Outputs a calibrated `compost_states` dict for use in firmware.
"""

import argparse
import json
import sys
from pathlib import Path

# Add parent to path to import existing models
sys.path.insert(0, str(Path(__file__).parent))

try:
    from soil_impedance_model import soil_states, z_soil, K_g
except ImportError:
    print("ERROR: soil_impedance_model.py not found in simulation/ directory.")
    print("Copy it from the workspace root to simulation/")
    sys.exit(1)

import numpy as np


# ─── Configuration ──────────────────────────────────────────────────────────
FREQ_CALIBRATION_HZ = 100_000  # Single-point calibration at 100 kHz


def compute_calibration(dry_z: float, moist_z: float, saturated_z: float) -> dict:
    """
    Given measured |Z| values at 100 kHz for three compost states,
    estimate bulk resistivity and derive a calibrated compost_states dict.
    """
    # The model: |Z| ≈ rho_bulk / K_g at high frequency (CPE is small)
    # So rho_bulk ≈ |Z| * K_g
    rho_dry = dry_z * K_g
    rho_moist = moist_z * K_g
    rho_sat = saturated_z * K_g

    compost_states = {
        "dry_compost": {
            "vwc": 0.08,
            "sigma_bulk": 1.0 / rho_dry,
            "rho_bulk": rho_dry,
            "epsilon_r": 8,
            "cpe_Q": 8e-7,
            "cpe_alpha": 0.60,
            "color": "#8B4513",
        },
        "moist_compost": {
            "vwc": 0.28,
            "sigma_bulk": 1.0 / rho_moist,
            "rho_bulk": rho_moist,
            "epsilon_r": 18,
            "cpe_Q": 2.5e-6,
            "cpe_alpha": 0.68,
            "color": "#CD853F",
        },
        "saturated_compost": {
            "vwc": 0.50,
            "sigma_bulk": 1.0 / rho_sat,
            "rho_bulk": rho_sat,
            "epsilon_r": 28,
            "cpe_Q": 7e-6,
            "cpe_alpha": 0.72,
            "color": "#4682B4",
        },
    }

    return compost_states


def print_calibration_report(states: dict):
    print("=" * 70)
    print("COMPOST CALIBRATION REPORT")
    print("=" * 70)
    print(f"\nFrequency: {FREQ_CALIBRATION_HZ / 1000:.0f} kHz")
    print(f"Geometric factor K_g: {K_g:.4f} m\n")

    print(f"{'State':<20} {'VWC':>8} {'|Z| (Ω)':>12} {'ρ_bulk (Ω·m)':>14} {'σ_bulk (mS/m)':>14}")
    print("-" * 70)
    for name, props in states.items():
        z = props["rho_bulk"] / K_g
        sigma_ms = props["sigma_bulk"] * 1000
        print(
            f"{name.replace('_', ' '):<20} "
            f"{props['vwc']:>8.0%} "
            f"{z:>12.1f} "
            f"{props['rho_bulk']:>14.1f} "
            f"{sigma_ms:>14.2f}"
        )

    print("\n" + "=" * 70)
    print("FIRMWARE CALIBRATION CONSTANTS")
    print("=" * 70)
    print("\n// Paste this into firmware/glasshouse_node_v1/config.h")
    print("struct SoilCalibration {")
    print("    float vwc;")
    print("    float rho_bulk;")
    print("    float sigma_bulk;")
    print("};")
    print("")
    for name, props in states.items():
        c_name = name.upper()
        print(f"const SoilCalibration {c_name} = {{")
        print(f"    .vwc = {props['vwc']:.2f}f,")
        print(f"    .rho_bulk = {props['rho_bulk']:.1f}f,")
        print(f"    .sigma_bulk = {props['sigma_bulk']:.6f}f,")
        print("};")

    print("\n" + "=" * 70)
    print("MOISTURE SENSITIVITY CHECK")
    print("=" * 70)
    z_dry = states["dry_compost"]["rho_bulk"] / K_g
    z_moist = states["moist_compost"]["rho_bulk"] / K_g
    z_sat = states["saturated_compost"]["rho_bulk"] / K_g

    sensitivity_dry_moist = (z_dry - z_moist) / z_dry * 100
    sensitivity_moist_sat = (z_moist - z_sat) / z_moist * 100
    dynamic_range = z_dry / z_sat

    print(f"Dry → Moist impedance drop: {sensitivity_dry_moist:.1f}%")
    print(f"Moist → Saturated drop:     {sensitivity_moist_sat:.1f}%")
    print(f"Total dynamic range:        {dynamic_range:.1f}×")
    print("")
    if dynamic_range > 5.0:
        print("✓ PASS: Dynamic range > 5× — excellent for measurement")
    elif dynamic_range > 2.0:
        print("⚠ WARN: Dynamic range 2–5× — usable but watch noise")
    else:
        print("✗ FAIL: Dynamic range < 2× — may need better electrodes or higher excitation")


def main():
    parser = argparse.ArgumentParser(
        description="Calibrate soil impedance model against real compost measurements."
    )
    parser.add_argument(
        "--dry-z",
        type=float,
        required=True,
        help="Measured |Z| in Ohms for dry compost at 100 kHz",
    )
    parser.add_argument(
        "--moist-z",
        type=float,
        required=True,
        help="Measured |Z| in Ohms for moist compost at 100 kHz",
    )
    parser.add_argument(
        "--saturated-z",
        type=float,
        required=True,
        help="Measured |Z| in Ohms for saturated compost at 100 kHz",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="simulation/compost_calibration.json",
        help="Output JSON file for calibrated states",
    )
    args = parser.parse_args()

    states = compute_calibration(args.dry_z, args.moist_z, args.saturated_z)
    print_calibration_report(states)

    # Write JSON
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(states, f, indent=2)
    print(f"\n✓ Calibration saved to: {output_path}")


if __name__ == "__main__":
    main()
