# Fourier Series Derivation — 2026-04-07

## 1.1 Orthogonal Basis

**Inner Product on L²([-L,L]):**

$$\langle f, g \rangle = \int_{-L}^{L} f(x)\,\overline{g(x)}\,dx$$

---

## Step 1: Prove Orthogonality

Show that $\bigl\{e^{in\pi x/L}\bigr\}_{n\in\mathbb{Z}}$ forms an orthogonal set:

$$\langle e^{in\pi x/L}, e^{im\pi x/L} \rangle = \int_{-L}^{L} e^{in\pi x/L}\,e^{-im\pi x/L}\,dx = \int_{-L}^{L} e^{i(n-m)\pi x/L}\,dx$$

**Case n = m:**
$$= \int_{-L}^{L} 1\,dx = 2L$$

**Case n ≠ m:**
$$= \left[\frac{e^{i(n-m)\pi x/L}}{i(n-m)\pi/L}\right]_{-L}^{L} = \frac{L}{i(n-m)\pi}\Bigl(e^{i(n-m)\pi} - e^{-i(n-m)\pi}\Bigr)$$

Using $e^{ik\pi} = (-1)^k$ for integer $k$:
$$= \frac{L}{i(n-m)\pi}\Bigl((-1)^{n-m} - (-1)^{n-m}\Bigr) = 0 \quad\checkmark$$

**Result:**
$$\langle e^{in\pi x/L}, e^{im\pi x/L} \rangle = 2L\,\delta_{nm}$$

---

## Step 2: Derive Fourier Coefficients

Assume expansion:
$$f(x) = \sum_{n=-\infty}^{\infty} c_n\,e^{in\pi x/L}$$

Project onto basis element $e^{im\pi x/L}$:
$$\langle f, e^{im\pi x/L} \rangle = \sum_{n=-\infty}^{\infty} c_n\,\langle e^{in\pi x/L}, e^{im\pi x/L} \rangle = \sum_{n} c_n \cdot 2L\,\delta_{nm} = 2L\,c_m$$

Therefore:
$$\boxed{c_m = \frac{1}{2L}\int_{-L}^{L} f(x)\,e^{-im\pi x/L}\,dx}$$

---

## Step 3: Parseval's Identity

Compute energy norm:
$$\|f\|^2 = \langle f, f \rangle = \int_{-L}^{L} |f(x)|^2\,dx$$

Substitute series expansion:
$$= \int_{-L}^{L} \left(\sum_{n} c_n\,e^{in\pi x/L}\right)\left(\sum_{m} \overline{c_m}\,e^{-im\pi x/L}\right)dx$$

$$= \sum_{n}\sum_{m} c_n\,\overline{c_m} \int_{-L}^{L} e^{i(n-m)\pi x/L}\,dx$$

Apply orthogonality:
$$= \sum_{n}\sum_{m} c_n\,\overline{c_m} \cdot 2L\,\delta_{nm} = 2L\sum_{n=-\infty}^{\infty}|c_n|^2$$

**Parseval's Identity:**
$$\boxed{\frac{1}{2L}\int_{-L}^{L}|f(x)|^2\,dx = \sum_{n=-\infty}^{\infty}|c_n|^2}$$

---

## Physical Interpretation

| Time Domain | Frequency Domain |
|-------------|------------------|
| $\int|f|^2\,dx$ — total energy | $\sum|c_n|^2$ — energy per mode |
| Continuous distribution | Discrete spectrum |

**Energy Conservation:** The total signal energy equals the sum of energies in each harmonic component. The Fourier transform preserves energy (unitary operator).

---

## Why Orthogonality Matters

If basis functions weren't orthogonal:
- Coefficients would **couple** — changing $c_n$ would affect the projection onto other modes
- No simple formula $c_n = \langle f, \phi_n \rangle / \|\phi_n\|^2$
- Would need to solve coupled linear system for coefficients
- Physical interpretation as "energy per mode" would be lost

Orthogonality = **independence of frequency components**
