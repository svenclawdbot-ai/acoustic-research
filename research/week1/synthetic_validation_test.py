"""
Synthetic Validation Test for Shear Wave Inversion

This script validates that your inversion algorithm can recover 
known parameters from synthetic data before applying to real data.

Run this BEFORE any real data analysis to avoid overfitting.
"""

import numpy as np
import matplotlib.pyplot as plt
from shear_wave_1d_simulator import ShearWave1D


def generate_synthetic_data(G_true, eta_true, frequencies, noise_level=0.01):
    """
    Generate synthetic displacement data with known parameters.
    
    Parameters:
    -----------
    G_true : float
        True storage modulus (Pa)
    eta_true : float
        True viscosity (Pa·s)
    frequencies : list
        Frequencies to simulate (Hz)
    noise_level : float
        Fractional noise level (e.g., 0.01 = 1%)
    
    Returns:
    --------
    data_dict : dict
        Dictionary of synthetic data at each frequency
    """
    data_dict = {}
    
    for f0 in frequencies:
        # Calculate stable grid parameters
        c_s = np.sqrt(G_true / 1000)  # rho = 1000
        wavelength = c_s / f0
        dx = wavelength / 20
        dt = dx / (2 * c_s)
        
        nx = 800
        duration = 0.05
        n_steps = int(duration / dt)
        
        # Run FDTD
        sim = ShearWave1D(nx=nx, dx=dx, dt=dt, rho=1000, 
                         G_prime=G_true, eta=eta_true)
        
        # Store displacement at receiver positions
        receivers = [nx//2, 3*nx//4]  # Two receiver positions
        time_history = []
        displacement_history = []
        
        for n in range(n_steps):
            t = n * dt
            sim.add_source(t, source_type='tone_burst', f0=f0, amplitude=1e-6)
            sim.step()
            
            if n % 10 == 0:  # Store every 10th step
                time_history.append(t)
                displacement_history.append([sim.u[r] for r in receivers])
        
        # Add Gaussian noise
        displacement_array = np.array(displacement_history)
        noise_std = noise_level * np.max(np.abs(displacement_array))
        displacement_noisy = displacement_array + np.random.randn(*displacement_array.shape) * noise_std
        
        data_dict[f0] = {
            'time': np.array(time_history),
            'displacement': displacement_noisy,
            'receivers': receivers,
            'true_G': G_true,
            'true_eta': eta_true
        }
    
    return data_dict


def simple_inversion_lsq(data_dict, G_bounds=(1000, 20000), eta_bounds=(1, 50)):
    """
    Simple least-squares inversion (placeholder for your algorithm).
    
    Returns estimated (G', η) that minimize misfit to data.
    """
    # This is a placeholder - replace with your actual inversion
    # For now, just return values near the center of bounds
    G_est = np.mean(G_bounds)
    eta_est = np.mean(eta_bounds)
    
    # TODO: Implement your inversion here
    # Should minimize: sum over frequencies of ||u_measured - u_simulated(G, η)||^2
    
    return G_est, eta_est


def validate_inversion(G_true=5000, eta_true=5, frequencies=[50, 100, 200, 400]):
    """
    Full validation pipeline.
    
    Returns True if validation passes, False otherwise.
    """
    print("="*70)
    print("SYNTHETIC VALIDATION TEST")
    print("="*70)
    print(f"\nTrue parameters: G' = {G_true} Pa, η = {eta_true} Pa·s")
    print(f"Frequencies: {frequencies} Hz")
    print(f"Frequency span: {max(frequencies)/min(frequencies):.1f}x")
    
    # Generate synthetic data
    print("\n[1] Generating synthetic data...")
    data_dict = generate_synthetic_data(G_true, eta_true, frequencies, noise_level=0.01)
    print(f"    Generated data for {len(frequencies)} frequencies")
    
    # Run inversion
    print("\n[2] Running inversion...")
    G_est, eta_est = simple_inversion_lsq(data_dict)
    print(f"    Estimated: G' = {G_est:.1f} Pa, η = {eta_est:.2f} Pa·s")
    
    # Calculate errors
    G_error = abs(G_est - G_true) / G_true * 100
    eta_error = abs(eta_est - eta_true) / eta_true * 100
    
    print("\n[3] Validation Results:")
    print(f"    G' error:    {G_error:.1f}%")
    print(f"    η error:     {eta_error:.1f}%")
    
    # Acceptance criteria
    G_pass = G_error < 10  # Within 10%
    eta_pass = eta_error < 20  # Within 20%
    
    print("\n[4] Acceptance Criteria:")
    print(f"    G' < 10% error: {'✓ PASS' if G_pass else '✗ FAIL'}")
    print(f"    η < 20% error:  {'✓ PASS' if eta_pass else '✗ FAIL'}")
    
    overall = G_pass and eta_pass
    print(f"\n{'='*70}")
    print(f"OVERALL: {'✓ VALIDATION PASSED' if overall else '✗ VALIDATION FAILED'}")
    print(f"{'='*70}")
    
    if not overall:
        print("\n⚠️  Your inversion algorithm needs improvement before real data.")
        print("   Possible issues:")
        print("   - Insufficient regularization")
        print("   - Local minimum in optimization")
        print("   - Numerical instability in forward model")
        print("   - Need better initial guess")
    else:
        print("\n✓ Your inversion can recover known parameters.")
        print("  You may proceed to real data analysis.")
    
    return overall, G_error, eta_error


def plot_dispersion_validation(G_true, eta_true, G_est, eta_est):
    """
    Plot dispersion curves to visualize fit quality.
    """
    frequencies = np.linspace(50, 500, 100)
    rho = 1000
    
    # Calculate phase velocity for true and estimated parameters
    def phase_velocity(G, eta, omega):
        """Kelvin-Voigt dispersion relation."""
        G_star = np.sqrt(G**2 + (omega * eta)**2)
        c = np.sqrt(2 * (G**2 + (omega * eta)**2) / (rho * (G + G_star)))
        return c
    
    c_true = [phase_velocity(G_true, eta_true, 2*np.pi*f) for f in frequencies]
    c_est = [phase_velocity(G_est, eta_est, 2*np.pi*f) for f in frequencies]
    
    plt.figure(figsize=(10, 6))
    plt.plot(frequencies, c_true, 'b-', linewidth=2, label=f'True (G\'={G_true}, η={eta_true})')
    plt.plot(frequencies, c_est, 'r--', linewidth=2, label=f'Estimated (G\'={G_est:.0f}, η={eta_est:.1f})')
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Phase Velocity (m/s)')
    plt.title('Dispersion Curve: True vs Estimated')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig('dispersion_validation.png', dpi=150, bbox_inches='tight')
    plt.show()


if __name__ == "__main__":
    # Run validation with typical liver parameters
    passed, G_err, eta_err = validate_inversion(
        G_true=5000,      # 5 kPa, healthy liver
        eta_true=5,       # 5 Pa·s
        frequencies=[50, 100, 200, 400]  # 8x span
    )
    
    # If you have estimated parameters, plot dispersion comparison
    # plot_dispersion_validation(5000, 5, estimated_G, estimated_eta)
    
    exit(0 if passed else 1)
