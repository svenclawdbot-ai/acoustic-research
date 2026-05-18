# 2026-05-12 - Physics & Mathematics Challenge

**Topic:** Wave Mechanics — Derive the Dispersion Relation for Viscoelastic Shear Waves

## Challenge

Starting from the equation of motion for a viscoelastic medium under shear deformation:

$$\rho \frac{\partial^2 u}{\partial t^2} = \frac{\partial \sigma}{\partial x}$$

With the Kelvin-Voigt constitutive relation:

$$\sigma = G' \gamma + \eta \frac{\partial \gamma}{\partial t}$$

Where:
- $\rho$ = material density
- $G'$ = storage modulus (elastic)
- $\eta$ = viscosity
- $\gamma = \partial u / \partial x$ = shear strain

### Tasks

1. **Derive the dispersion relation** $\omega(k)$ for plane wave solutions $u(x,t) = u_0 e^{i(kx - \omega t)}$
2. **Find the phase velocity** $c_p = \omega / k$ and **group velocity** $c_g = d\omega/dk$
3. **Show that the wave is attenuated** — find the attenuation coefficient $\alpha$ as a function of frequency
4. **Compare limits:** What happens when $\eta \to 0$ (purely elastic) and when $\omega \to 0$ (quasi-static)?
5. **Numerical check:** Plot $c_p(\omega)$ and $\alpha(\omega)$ for liver tissue ($\rho \approx 1060$ kg/m³, $G' \approx 2.5$ kPa, $\eta \approx 0.5$ Pa·s) over 10–500 Hz

### Deliverable

- Hand derivation or LaTeX write-up of steps 1–4
- Python/MATLAB plot for step 5
- One paragraph: What does this mean for ARFI / shear wave elastography?

**Time Budget:** 2–3 hours focused work  
**Log progress in:** `memory/2026-05-12.md`
