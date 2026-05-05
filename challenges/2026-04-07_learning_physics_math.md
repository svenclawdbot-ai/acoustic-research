# Learning Challenge — 2026-04-07 (Tuesday)
## Physics/Mathematics: Fourier Analysis & The Wave Equation

### Objective
Develop deep intuition for how complex signals decompose into simple harmonics, and derive the 1D wave equation from first principles.

---

## Part 1: Mathematical Foundations (Paper + Pen)

### 1.1 Derive the Fourier Series
Starting from the inner product on $L^2([-L, L])$:
- Show that $\{e^{in\pi x/L}\}_{n \in \mathbb{Z}}$ forms an orthogonal basis
- Derive the coefficients: $c_n = \frac{1}{2L} \int_{-L}^{L} f(x) e^{-in\pi x/L} dx$
- Prove Parseval's identity: $\frac{1}{2L} \int |f|^2 = \sum |c_n|^2$

**Key insight:** What does this identity tell us about energy conservation?

### 1.2 From Series to Transform
- Take the limit $L \to \infty$ formally
- Show how the discrete sum becomes the continuous Fourier transform
- Derive the duality: $\mathcal{F}[\mathcal{F}[f]](x) = 2\pi f(-x)$

**Question:** Why does the Fourier transform of a Gaussian yield another Gaussian?

---

## Part 2: The Wave Equation

### 2.1 Physical Derivation
Consider a string under tension $T$ with linear density $\rho$:
- Draw the free-body diagram for a small segment $\Delta x$
- Apply Newton's second law
- Take the limit $\Delta x \to 0$ to derive: $\frac{\partial^2 u}{\partial t^2} = c^2 \frac{\partial^2 u}{\partial x^2}$, where $c = \sqrt{T/\rho}$

### 2.2 General Solution (d'Alembert)
Show that $u(x,t) = f(x-ct) + g(x+ct)$ solves the wave equation.
- What do $f(x-ct)$ and $g(x+ct)$ represent physically?
- Sketch how a pulse propagates in both directions

### 2.3 Separation of Variables
Assume $u(x,t) = X(x)T(t)$:
- Separate and derive the eigenvalue problem
- Show that this leads to normal modes
- Express the general solution as a superposition of modes

**Connection:** How does this relate to the Fourier series from Part 1?

---

## Part 3: Computational Exploration (Python)

### 3.1 Numerical Fourier Analysis
```python
# Tasks:
# 1. Implement DFT from scratch (no numpy.fft) - O(n²) version
# 2. Compare to numpy.fft.fft for verification
# 3. Plot amplitude spectrum of: square wave, sawtooth, Gaussian pulse
# 4. Demonstrate Gibbs phenomenon
```

### 3.2 Wave Equation Simulation
```python
# Tasks:
# 1. Implement finite difference scheme for 1D wave equation
# 2. Simulate: plucked string (triangular initial condition)
# 3. Simulate: Gaussian pulse propagation
# 4. Verify energy conservation numerically
# 5. Add fixed vs. free boundary conditions
```

### 3.3 Connect to Acoustics
Yesterday you worked with ultrasonic A-scans. Today:
- Take the FFT of a simulated A-scan signal
- Identify the frequency content of different defect echoes
- Explain why higher frequencies give better resolution but worse penetration
- Calculate the theoretical resolution limit given bandwidth $B$

---

## Part 4: Deep Questions

1. **Uncertainty Principle:** $\Delta t \cdot \Delta f \geq \frac{1}{4\pi}$. Why can't we have perfect time AND frequency resolution? Connect to Heisenberg.

2. **Dispersion:** Real materials have frequency-dependent wave speed $c(\omega)$. What happens to a pulse as it propagates? Why does this matter for NDE?

3. **Dimensionality:** The 3D wave equation has different solutions than 1D (Huygens' principle). Why does sound behave differently in 3D vs. 1D?

---

## Deliverables

- [ ] Full derivations on paper (scan/photo or LaTeX)
- [ ] Working DFT implementation
- [ ] Wave simulation with visualizations
- [ ] Written answers to at least 2 of the "Deep Questions"
- [ ] Connection summary: How does this math enable yesterday's NDE engineering?

---

## Resources
- "The Fourier Transform and Its Applications" — Bracewell (Ch 1-5)
- 3Blue1Brown: "But what is the Fourier Transform?" (YouTube)
- MIT OCW 18.085: Computational Science and Engineering

---

## Success Criteria
This is about **depth**, not speed. Don't just run code — understand WHY each line works. Ask yourself at each step: "What does this mean physically?"

*Focus: Mathematical foundations → Physical intuition → Engineering application*

---
*Tuesday Challenge | Physics/Mathematics | 2026-04-07*
