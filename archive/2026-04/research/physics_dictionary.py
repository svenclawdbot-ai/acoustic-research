"""
Physics-Informed Dictionary for Compressive Sensing
===================================================

Builds dictionary where atoms satisfy Zener dispersion relation.
Key insight: Shear waves in viscoelastic media follow
    ω(k) = k · c(ω, G₀, G∞, τσ)

This creates a structured, sparse dictionary that dramatically
reduces the search space compared to generic Fourier.

Author: DSP Challenge — March 18, 2026
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize_scalar
import sys
sys.path.append('/home/james/.openclaw/workspace/research/week2')
from zener_model import ZenerModel


class ZenerDispersionDictionary:
    """
    Build physics-informed dictionary for shear wave CS.
    
    Each atom has the form:
        ψ(x,t; k) = exp(i(k·x - ω(k)·t))
    where ω(k) follows the Zener dispersion relation.
    """
    
    def __init__(self, x_array, t_array, G0, G_inf, tau_sigma, rho=1000):
        """
        Initialize dictionary builder.
        
        Parameters:
        -----------
        x_array : array (nx,)
            Spatial grid (m)
        t_array : array (nt,)
            Time grid (s)
        G0, G_inf, tau_sigma : float
            Zener model parameters
        rho : float
            Density (kg/m³)
        """
        self.x = np.array(x_array)
        self.t = np.array(t_array)
        self.nx = len(x_array)
        self.nt = len(t_array)
        self.dx = x_array[1] - x_array[0]
        self.dt = t_array[1] - t_array[0]
        
        self.G0 = G0
        self.G_inf = G_inf
        self.tau_sigma = tau_sigma
        self.rho = rho
        
        self.zm = ZenerModel(G0, G_inf, tau_sigma)
        
        print(f"Zener Dictionary:")
        print(f"  Grid: {self.nx} × {self.nt}")
        print(f"  dx = {self.dx*1000:.2f} mm, dt = {self.dt*1000:.2f} ms")
        print(f"  Zener: G₀={G0}, G∞={G_inf}, τσ={tau_sigma*1000:.1f} ms")
    
    def compute_dispersion_relation(self, k_vals):
        """
        Compute ω(k) for given wavenumbers using Zener model.
        
        For Zener: c(ω) = √[2|G*|²/(ρ(G' + |G*|))]
        Then: ω = k · c(ω)  (implicit, solved iteratively)
        
        Parameters:
        -----------
        k_vals : array
            Wavenumbers (rad/m)
            
        Returns:
        --------
        omega_vals : array
            Frequencies (rad/s) satisfying dispersion
        c_vals : array
            Phase velocities (m/s)
        """
        omega_vals = []
        c_vals = []
        
        for k in k_vals:
            if k <= 0:
                omega_vals.append(0)
                c_vals.append(0)
                continue
            
            # Solve: ω = k · c(ω) where c(ω) from Zener
            # This is implicit, use root finding
            
            def dispersion_error(omega):
                if omega <= 0:
                    return 1e10
                c = self.zm.phase_velocity(omega)
                return (omega - k * c)**2
            
            # Initial guess: low-frequency limit
            c0 = np.sqrt(self.G0 / self.rho)
            omega_guess = k * c0
            
            # Search in reasonable range
            result = minimize_scalar(
                dispersion_error,
                bounds=(0.1, omega_guess * 5),
                method='bounded'
            )
            
            omega_opt = result.x
            c_opt = self.zm.phase_velocity(omega_opt)
            
            omega_vals.append(omega_opt)
            c_vals.append(c_opt)
        
        return np.array(omega_vals), np.array(c_vals)
    
    def build_dictionary(self, k_min=None, k_max=None, n_k=50):
        """
        Build space-time dictionary with Zener dispersion structure.
        
        Parameters:
        -----------
        k_min, k_max : float or None
            Wavenumber range. If None, use Nyquist limits.
        n_k : int
            Number of wavenumber atoms
            
        Returns:
        --------
        Psi : ndarray (nx*nt, n_k)
            Dictionary matrix (flattened space-time atoms)
        k_vals : array (n_k,)
            Wavenumbers for each atom
        omega_vals : array (n_k,)
            Frequencies for each atom
        """
        # Set wavenumber range
        k_nyquist = np.pi / self.dx
        if k_min is None:
            k_min = 2 * np.pi / (self.nx * self.dx)  # Fundamental
        if k_max is None:
            k_max = k_nyquist / 2  # Conservative
        
        # Log-spaced wavenumbers (better for dispersion)
        k_vals = np.logspace(np.log10(k_min), np.log10(k_max), n_k)
        
        print(f"\nBuilding dictionary:")
        print(f"  k range: {k_min:.1f} to {k_max:.1f} rad/m")
        print(f"  {n_k} atoms")
        
        # Compute dispersion
        omega_vals, c_vals = self.compute_dispersion_relation(k_vals)
        
        # Build atoms: ψ(x,t) = exp(i(k·x - ω·t))
        atoms = []
        X, T = np.meshgrid(self.x, self.t, indexing='ij')
        
        for k, omega in zip(k_vals, omega_vals):
            if omega <= 0:
                continue
            
            # Forward traveling wave
            atom_fwd = np.exp(1j * (k * X - omega * T))
            atoms.append(atom_fwd.flatten())
            
            # Backward traveling wave
            atom_bwd = np.exp(1j * (-k * X - omega * T))
            atoms.append(atom_bwd.flatten())
        
        Psi = np.column_stack(atoms)
        
        # Normalize columns
        for i in range(Psi.shape[1]):
            norm = np.linalg.norm(Psi[:, i])
            if norm > 0:
                Psi[:, i] /= norm
        
        print(f"  Dictionary shape: {Psi.shape}")
        print(f"  Atoms: {Psi.shape[1]}")
        
        self.Psi = Psi
        self.k_vals = k_vals
        self.omega_vals = omega_vals
        self.c_vals = c_vals
        
        return Psi, k_vals, omega_vals
    
    def visualize_dictionary(self, save_path='dictionary_structure.png'):
        """Visualize dictionary structure and dispersion."""
        if not hasattr(self, 'Psi'):
            print("Build dictionary first!")
            return
        
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        
        # 1. Dispersion relation
        ax = axes[0, 0]
        f_vals = self.omega_vals / (2 * np.pi)
        ax.loglog(f_vals, self.k_vals, 'b-o', markersize=4)
        ax.set_xlabel('Frequency f (Hz)')
        ax.set_ylabel('Wavenumber k (rad/m)')
        ax.set_title('Zener Dispersion Relation ω(k)')
        ax.grid(True, alpha=0.3)
        
        # 2. Phase velocity
        ax = axes[0, 1]
        ax.semilogx(f_vals, self.c_vals, 'r-s', markersize=4)
        ax.axhline(np.sqrt(self.G0/self.rho), color='g', linestyle='--', 
                  label=f'c₀ = {np.sqrt(self.G0/self.rho):.1f} m/s')
        ax.axhline(np.sqrt(self.G_inf/self.rho), color='orange', linestyle='--',
                  label=f'c∞ = {np.sqrt(self.G_inf/self.rho):.1f} m/s')
        ax.set_xlabel('Frequency f (Hz)')
        ax.set_ylabel('Phase Velocity c (m/s)')
        ax.set_title('Phase Velocity Dispersion')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # 3. Sample atoms (space-time)
        ax = axes[1, 0]
        # Reshape first few atoms
        n_show = min(3, self.Psi.shape[1])
        for i in range(n_show):
            atom = self.Psi[:, i].reshape(self.nx, self.nt)
            x_slice = self.nx // 2
            ax.plot(self.t * 1000, np.real(atom[x_slice, :]), 
                   label=f'k={self.k_vals[i]:.1f}')
        ax.set_xlabel('Time (ms)')
        ax.set_ylabel('Real part')
        ax.set_title('Sample Atoms (temporal slice)')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # 4. Dictionary matrix structure
        ax = axes[1, 1]
        # Show Gram matrix (inner products)
        Gram = np.abs(self.Psi.conj().T @ self.Psi)
        im = ax.imshow(Gram, cmap='hot', aspect='auto')
        ax.set_xlabel('Atom index')
        ax.set_ylabel('Atom index')
        ax.set_title('Dictionary Gram Matrix |ΨᴴΨ|')
        plt.colorbar(im, ax=ax)
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=150)
        print(f"\nSaved: {save_path}")
        
        return fig
    
    def get_sensing_matrix(self, receiver_indices):
        """
        Get sensing matrix for given receiver positions.
        
        A = S · Ψ where S samples at receiver positions
        """
        if not hasattr(self, 'Psi'):
            raise ValueError("Build dictionary first!")
        
        # Sampling matrix
        S = np.zeros((len(receiver_indices), self.nx))
        for i, idx in enumerate(receiver_indices):
            S[i, idx] = 1.0
        
        # Block diagonal for all time samples
        # A = kron(I_nt, S) · Ψ
        # For efficiency, work with (n_rec, nx) and multiply per time
        
        return S
    
    def coherence_analysis(self):
        """
        Analyze dictionary coherence.
        
        μ = max_{i≠j} |<ψᵢ, ψⱼ>|
        Lower coherence → better CS recovery
        """
        if not hasattr(self, 'Psi'):
            raise ValueError("Build dictionary first!")
        
        Gram = np.abs(self.Psi.conj().T @ self.Psi)
        # Zero diagonal
        np.fill_diagonal(Gram, 0)
        
        mu = np.max(Gram)
        
        print(f"\nDictionary Coherence Analysis:")
        print(f"  Mutual coherence μ = {mu:.4f}")
        print(f"  Sparsity guarantee: s < 0.5(1 + 1/μ) ≈ {0.5*(1+1/mu):.1f}")
        
        return mu, Gram


def demo_physics_dictionary():
    """Demonstrate physics-informed dictionary."""
    print("=" * 70)
    print("PHYSICS-INFORMED DICTIONARY FOR CS")
    print("=" * 70)
    
    # Setup
    nx = 100
    dx = 0.002
    x_array = np.arange(nx) * dx
    
    nt = 200
    dt = 0.0005
    t_array = np.arange(nt) * dt
    
    G0 = 2000
    G_inf = 4000
    tau_sigma = 0.005
    
    # Build dictionary
    print("\n[1] Building physics-informed dictionary...")
    zdd = ZenerDispersionDictionary(x_array, t_array, G0, G_inf, tau_sigma)
    
    Psi, k_vals, omega_vals = zdd.build_dictionary(n_k=30)
    
    # Analyze
    print("\n[2] Coherence analysis...")
    mu, Gram = zdd.coherence_analysis()
    
    # Compare to Fourier dictionary
    print("\n[3] Comparison to Fourier dictionary...")
    k_fourier = 2 * np.pi * np.fft.fftfreq(nx, dx)
    k_fourier = k_fourier[k_fourier > 0][:30]  # Same count
    
    # Fourier atoms (no dispersion structure)
    atoms_fourier = []
    X, T = np.meshgrid(x_array, t_array, indexing='ij')
    for k in k_fourier:
        omega = k * np.sqrt(G0/1000)  # Non-dispersive
        atom = np.exp(1j * (k * X - omega * T))
        atoms_fourier.append(atom.flatten())
    
    Psi_fourier = np.column_stack(atoms_fourier)
    for i in range(Psi_fourier.shape[1]):
        Psi_fourier[:, i] /= np.linalg.norm(Psi_fourier[:, i])
    
    Gram_fourier = np.abs(Psi_fourier.conj().T @ Psi_fourier)
    np.fill_diagonal(Gram_fourier, 0)
    mu_fourier = np.max(Gram_fourier)
    
    print(f"  Fourier dictionary μ = {mu_fourier:.4f}")
    print(f"  Zener dictionary μ = {mu:.4f}")
    print(f"  Improvement: {(mu_fourier/mu):.2f}× lower coherence")
    
    # Visualize
    print("\n[4] Visualization...")
    zdd.visualize_dictionary()
    
    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Physics-informed dictionary:")
    print(f"  - {Psi.shape[1]} atoms")
    print(f"  - Mutual coherence: μ = {mu:.4f}")
    print(f"  - vs Fourier: {(mu_fourier/mu):.2f}× better")
    print(f"\nNext: Use with ADMM/MM for CS reconstruction")


if __name__ == "__main__":
    demo_physics_dictionary()
