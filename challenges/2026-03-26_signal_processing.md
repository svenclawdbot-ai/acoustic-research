# Engineering Challenge — March 26, 2026
## Thursday Signal Processing Challenge: Dispersion Analysis

### Problem

A 1D shear wave propagates through a viscoelastic material characterized by a complex shear modulus:

$$G^*(\omega) = G'(\omega) + iG''(\omega)$$

where $G'$ is the storage modulus and $G''$ is the loss modulus. For soft biological tissue, these follow a power-law relaxation:

$$G'(\omega) = G_0 \left(\frac{\omega}{\omega_0}\right)^\alpha$$
$$G''(\omega) = G_0 \tan\left(\frac{\pi\alpha}{2}\right) \left(\frac{\omega}{\omega_0}\right)^\alpha$$

with $G_0 = 5$ kPa, $\omega_0 = 100$ rad/s, and $\alpha = 0.2$ (fractional derivative order).

### Task 1: Phase Velocity and Attenuation

Derive expressions for:
1. **Phase velocity** $c_p(\omega)$ as a function of frequency
2. **Attenuation coefficient** $\alpha_{att}(\omega)$ in Np/m

Show that:
$$c_p(\omega) = \sqrt{\frac{|G^*(\omega)|}{\rho}} \sec\left(\frac{\phi}{2}\right)$$
$$\alpha_{att}(\omega) = \frac{\omega}{c_p(\omega)} \tan\left(\frac{\phi}{2}\right)$$

where $\phi = \arctan(G''/G')$ and $\rho = 1000$ kg/m³.

### Task 2: Numerical Analysis

Write Python code to:
1. Plot $c_p(\omega)$ vs frequency (1–1000 Hz)
2. Plot $\alpha_{att}(\omega)$ vs frequency on log-log axes
3. Calculate the **dispersion index**: $DI = \frac{c_p(500 \text{ Hz}) - c_p(50 \text{ Hz})}{c_p(50 \text{ Hz})} \times 100\%$

### Task 3: Physical Interpretation

Explain in 2–3 sentences:
- Why does phase velocity increase with frequency in viscoelastic materials?
- What clinical relevance does this have for elastography imaging?

### Bonus: Group Velocity

Calculate the **group velocity** $c_g(\omega)$ numerically and compare to $c_p(\omega)$. When would significant group velocity dispersion matter for wave propagation?

---

**Difficulty:** Intermediate  
**Time estimate:** 45–60 minutes  
**Relevant skills:** Complex analysis, Python/MATLAB, wave physics
