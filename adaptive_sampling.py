"""
Adaptive Sampling for Ultrasonic Wavefield Reconstruction
=========================================================

Iterative receiver placement strategies:
1. Energy-guided: Place where signal energy is detected
2. Uncertainty-guided: Place where reconstruction is uncertain  
3. Two-stage: Coarse scan → detect → dense local sampling

This maximizes information per receiver for sparse arrays.
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize
import sys
sys.path.insert(0, '/home/james/.openclaw/workspace')
sys.path.insert(0, '/home/james/.openclaw/workspace/research/week2')

from shear_wave_2d_zener import ShearWave2DZener
from zener_model import ZenerModel


def compute_receiver_importance(u_full, x, strategy='energy', sigma_noise=1e-7):
    """
    Compute importance score for each potential receiver location.
    
    Parameters:
    -----------
    u_full : array (nx, nt)
        Full wavefield (for simulation/testing)
    x : array (nx,)
        Spatial grid
    strategy : str
        'energy' - signal energy
        'curvature' - spatial curvature (peaks/troughs)
        'information' - Fisher information
    sigma_noise : float
        Expected noise level
        
    Returns:
    --------
    importance : array (nx,)
        Importance score for each position
    """
    nx, nt = u_full.shape
    importance = np.zeros(nx)
    
    if strategy == 'energy':
        # Energy over time at each position
        importance = np.sum(np.abs(u_full)**2, axis=1)
        
    elif strategy == 'curvature':
        # Spatial second derivative (captures peaks/valleys)
        for t in range(nt):
            u_t = u_full[:, t]
            # Second derivative (Laplacian in 1D)
            curvature = np.abs(np.convolve(u_t, [1, -2, 1], mode='same'))
            importance += curvature
            
    elif strategy == 'information':
        # Approximate Fisher information
        # I(x) ≈ |∂u/∂x|² / σ²
        for t in range(nt):
            u_t = u_full[:, t]
            grad = np.abs(np.gradient(u_t))
            importance += grad**2 / sigma_noise**2
    
    # Normalize
    importance = importance / np.max(importance) if np.max(importance) > 0 else importance
    
    return importance


def adaptive_sample_iterative(u_full, x, n_receivers, strategy='energy', 
                               initial_spacing='uniform'):
    """
    Iteratively place receivers based on importance scores.
    
    Parameters:
    -----------
    u_full : array (nx, nt)
        Full wavefield (ground truth for simulation)
    x : array (nx,)
        Spatial grid
    n_receivers : int
        Total number of receivers to place
    strategy : str
        Importance scoring strategy
    initial_spacing : str
        'uniform' or 'random' for first batch
        
    Returns:
    --------
    rec_idx : array
        Receiver indices
    placement_history : list
        History of receiver placements
    """
    nx = len(x)
    rec_idx = []
    placement_history = []
    
    # Initial placement (first ~30%)
    n_initial = max(3, n_receivers // 3)
    
    if initial_spacing == 'uniform':
        initial_idx = np.linspace(0, nx-1, n_initial, dtype=int)
    else:
        np.random.seed(42)
        initial_idx = np.sort(np.random.choice(nx, n_initial, replace=False))
    
    rec_idx.extend(initial_idx)
    placement_history.append(initial_idx.copy())
    
    # Iterative placement
    for i in range(n_initial, n_receivers):
        # Compute importance with current receivers
        importance = compute_receiver_importance(u_full, x, strategy)
        
        # Exclude already-placed receivers
        mask = np.ones(nx, dtype=bool)
        mask[rec_idx] = False
        
        # Add minimum spacing constraint
        min_spacing = nx // (2 * n_receivers)
        for idx in rec_idx:
            start = max(0, idx - min_spacing//2)
            end = min(nx, idx + min_spacing//2 + 1)
            mask[start:end] = False
        
        # Find best position among remaining
        if np.any(mask):
            available_importance = importance.copy()
            available_importance[~mask] = -1
            best_idx = np.argmax(available_importance)
            rec_idx.append(best_idx)
        else:
            # Fallback: random available position
            available = np.where(mask)[0]
            if len(available) > 0:
                rec_idx.append(available[0])
        
        placement_history.append(np.array(rec_idx).copy())
    
    return np.array(sorted(rec_idx)), placement_history


def two_stage_sampling(u_full, x, n_receivers_stage1, n_receivers_stage2,
                       detection_threshold=1e-7):
    """
    Two-stage adaptive sampling:
    1. Coarse uniform scan to detect wave location
    2. Dense sampling around detected regions
    
    Parameters:
    -----------
    u_full : array (nx, nt)
        Full wavefield
    x : array (nx,)
        Spatial grid
    n_receivers_stage1 : int
        Number for initial coarse scan
    n_receivers_stage2 : int
        Number for focused dense sampling
    detection_threshold : float
        Energy threshold for detecting wave presence
        
    Returns:
    --------
    rec_idx : array
        All receiver indices
    stage1_idx : array
        Stage 1 receiver indices
    stage2_idx : array
        Stage 2 receiver indices
    detected_regions : list
        Regions where wave was detected
    """
    nx = len(x)
    
    # Stage 1: Coarse uniform scan
    print(f"  Stage 1: Coarse scan with {n_receivers_stage1} receivers")
    stage1_idx = np.linspace(0, nx-1, n_receivers_stage1, dtype=int)
    
    # Measure at stage 1 positions (simulate)
    y_stage1 = u_full[stage1_idx, :]
    energy_stage1 = np.sum(np.abs(y_stage1)**2, axis=1)
    
    # Detect regions with signal
    detected_mask = energy_stage1 > detection_threshold * np.max(energy_stage1)
    detected_regions = stage1_idx[detected_mask]
    
    print(f"    Detected signal at {len(detected_regions)} locations")
    
    # Stage 2: Dense sampling around detected regions
    print(f"  Stage 2: Dense sampling with {n_receivers_stage2} receivers")
    
    stage2_idx = []
    receivers_per_region = n_receivers_stage2 // max(1, len(detected_regions))
    
    for region_center in detected_regions:
        # Place receivers around this region
        region_width = nx // n_receivers_stage1  # Approximate region size
        start = max(0, region_center - region_width // 2)
        end = min(nx, region_center + region_width // 2)
        
        # Uniform within region
        if end - start > receivers_per_region:
            local_idx = np.linspace(start, end-1, receivers_per_region, dtype=int)
            stage2_idx.extend(local_idx)
    
    # Remove duplicates and combine
    stage2_idx = np.array(sorted(set(stage2_idx)))
    
    # If we have budget left, add more globally
    if len(stage2_idx) < n_receivers_stage2:
        remaining = n_receivers_stage2 - len(stage2_idx)
        available = [i for i in range(nx) 
                     if i not in stage1_idx and i not in stage2_idx]
        if len(available) >= remaining:
            extra = np.random.choice(available, remaining, replace=False)
            stage2_idx = np.sort(np.concatenate([stage2_idx, extra]))
    
    # Combine stages
    rec_idx = np.sort(np.concatenate([stage1_idx, stage2_idx]))
    
    return rec_idx, stage1_idx, stage2_idx, detected_regions


def compare_sampling_strategies(u_full, x, n_receivers=20):
    """
    Compare different sampling strategies on the same wavefield.
    """
    print("\n" + "=" * 70)
    print("ADAPTIVE SAMPLING COMPARISON")
    print("=" * 70)
    
    strategies = {
        'Uniform': np.linspace(0, len(x)-1, n_receivers, dtype=int),
        'Random': np.sort(np.random.choice(len(x), n_receivers, replace=False)),
    }
    
    # Energy-guided adaptive
    rec_energy, _ = adaptive_sample_iterative(u_full, x, n_receivers, 
                                               strategy='energy')
    strategies['Energy-Guided'] = rec_energy
    
    # Curvature-guided
    rec_curv, _ = adaptive_sample_iterative(u_full, x, n_receivers,
                                             strategy='curvature')
    strategies['Curvature-Guided'] = rec_curv
    
    # Two-stage
    rec_two, stage1, stage2, detected = two_stage_sampling(
        u_full, x, n_receivers//3, 2*n_receivers//3
    )
    strategies['Two-Stage'] = rec_two
    
    # Visualize
    fig, axes = plt.subplots(2, 3, figsize=(16, 10))
    
    # Ground truth wavefield
    extent = [0, u_full.shape[1]*0.001, 0, len(x)*x[1]*100]
    vmax = np.percentile(np.abs(u_full), 99)
    
    im = axes[0, 0].imshow(np.real(u_full), aspect='auto', origin='lower',
                           extent=extent, cmap='RdBu_r', vmin=-vmax, vmax=vmax)
    axes[0, 0].set_title('Ground Truth Wavefield')
    axes[0, 0].set_ylabel('Position (cm)')
    plt.colorbar(im, ax=axes[0, 0])
    
    # Importance map
    importance = compute_receiver_importance(u_full, x, 'energy')
    axes[0, 1].plot(x*100, importance, 'b-', linewidth=2)
    axes[0, 1].fill_between(x*100, importance, alpha=0.3)
    axes[0, 1].set_xlabel('Position (cm)')
    axes[0, 1].set_ylabel('Importance')
    axes[0, 1].set_title('Energy-Based Importance')
    axes[0, 1].grid(True, alpha=0.3)
    
    # Compare strategies
    strategy_names = list(strategies.keys())
    for idx, (name, rec_idx) in enumerate(strategies.items()):
        if idx == 0:
            ax = axes[0, 2]
        elif idx == 1:
            ax = axes[1, 0]
        elif idx == 2:
            ax = axes[1, 1]
        else:
            ax = axes[1, 2]
        
        # Show wavefield background
        ax.imshow(np.abs(u_full), aspect='auto', origin='lower',
                 extent=extent, cmap='hot', alpha=0.3, vmin=0, vmax=vmax)
        
        # Mark receiver positions
        for i, ri in enumerate(rec_idx):
            ax.axhline(y=x[ri]*100, color=f'C{i % 10}', linewidth=2, 
                      xmin=0.02, xmax=0.1)
        
        # Compute coverage metric
        y_sparse = u_full[rec_idx, :]
        energy_captured = np.sum(np.abs(y_sparse)**2)
        total_energy = np.sum(np.abs(u_full)**2)
        coverage = energy_captured / total_energy * 100
        
        ax.set_title(f'{name}\n{coverage:.1f}% energy captured')
        ax.set_xlabel('Time (ms)')
        ax.set_ylabel('Position (cm)')
        ax.set_ylim(extent[2], extent[3])
    
    plt.tight_layout()
    plt.savefig('adaptive_sampling_comparison.png', dpi=150)
    print("\n  Saved: adaptive_sampling_comparison.png")
    
    # Summary table
    print("\n" + "=" * 70)
    print("SAMPLING STRATEGY COMPARISON")
    print("=" * 70)
    print(f"{'Strategy':<20} {'Coverage':>12} {'Avg Spacing':>15}")
    print("-" * 70)
    
    for name, rec_idx in strategies.items():
        y_sparse = u_full[rec_idx, :]
        energy_captured = np.sum(np.abs(y_sparse)**2)
        coverage = energy_captured / np.sum(np.abs(u_full)**2) * 100
        
        spacings = np.diff(rec_idx) * x[1] * 100  # cm
        avg_spacing = np.mean(spacings)
        
        print(f"{name:<20} {coverage:>11.1f}% {avg_spacing:>14.2f} cm")
    
    print("=" * 70)
    
    return strategies


def run_adaptive_demo():
    """Demonstrate adaptive sampling concepts."""
    print("=" * 70)
    print("ADAPTIVE SAMPLING FOR SPARSE ULTRASONIC ARRAYS")
    print("=" * 70)
    
    # Generate wavefield
    print("\n[1] Generating wavefield...")
    nx, ny = 100, 80
    dx = 0.002
    sim = ShearWave2DZener(nx, ny, dx, rho=1000,
                           G0=2000, G_inf=4000, tau_sigma=0.005)
    
    nt_steps = 600
    wavefield = []
    
    for n in range(nt_steps):
        t = n * sim.dt
        if t < 0.012:
            f_inst = 80 + (250 - 80) * (t / 0.012)
            envelope = np.exp(-(t - 0.006)**2 / (2 * 0.003**2))
            sim.add_source(t, nx//5, ny//2, amplitude=2e-5 * envelope,
                          f0=f_inst, source_type='ricker')
        sim.step()
        if n % 2 == 0:
            wavefield.append(sim.vy[:, ny//2].copy())
    
    u_full = np.array(wavefield).T
    x = sim.x
    
    print(f"  Shape: {u_full.shape}")
    print(f"  Peak amplitude: {np.abs(u_full).max():.2e}")
    print(f"  Signal at positions: {np.where(np.sum(np.abs(u_full), axis=1) > 1e-8)[0]}")
    
    # Compare strategies
    strategies = compare_sampling_strategies(u_full, x, n_receivers=15)
    
    # Detailed two-stage example
    print("\n" + "=" * 70)
    print("TWO-STAGE SAMPLING EXAMPLE")
    print("=" * 70)
    
    rec_idx, stage1, stage2, detected = two_stage_sampling(
        u_full, x, n_receivers_stage1=5, n_receivers_stage2=10
    )
    
    print(f"\nStage 1 (coarse): {len(stage1)} receivers")
    print(f"  Positions: {[round(x[i]*100,1) for i in stage1]} cm")
    print(f"\nDetected regions: {len(detected)}")
    print(f"  At positions: {[round(x[i]*100,1) for i in detected]} cm")
    print(f"\nStage 2 (dense): {len(stage2)} receivers")
    print(f"  Positions: {[round(x[i]*100,1) for i in stage2]} cm")
    
    # Energy captured
    y_total = np.sum(np.abs(u_full)**2)
    y_stage1 = np.sum(np.abs(u_full[stage1, :])**2)
    y_stage2 = np.sum(np.abs(u_full[stage2, :])**2)
    y_all = np.sum(np.abs(u_full[rec_idx, :])**2)
    
    print(f"\nEnergy captured:")
    print(f"  Stage 1 only: {y_stage1/y_total*100:.1f}%")
    print(f"  Stage 2 only: {y_stage2/y_total*100:.1f}%")
    print(f"  Combined: {y_all/y_total*100:.1f}%")
    
    print("\n" + "=" * 70)
    print("ADAPTIVE SAMPLING DEMO COMPLETE")
    print("=" * 70)
    
    return strategies


if __name__ == "__main__":
    strategies = run_adaptive_demo()
