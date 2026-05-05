"""
Fourier Series Derivation — Section 1.1
Equations written as code for readability
"""

# ============================================================================
# INNER PRODUCT ON L^2([-L, L])
# ============================================================================

# <f, g> = integral from -L to L of f(x) * conjugate(g(x)) dx
#
# In code notation:
# inner_product = integral(f(x) * g.conjugate(x), x=-L..L)


# ============================================================================
# STEP 1: PROVE ORTHOGONALITY
# ============================================================================

# Basis functions: phi_n(x) = exp(i * n * pi * x / L)
# 
# Show: <phi_n, phi_m> = 2L * delta_nm
#
# <exp(i*n*pi*x/L), exp(i*m*pi*x/L)>
#   = integral from -L to L of exp(i*n*pi*x/L) * exp(-i*m*pi*x/L) dx
#   = integral from -L to L of exp(i*(n-m)*pi*x/L) dx

# Case n == m:
#   = integral from -L to L of 1 dx
#   = 2*L

# Case n != m:
#   = [exp(i*(n-m)*pi*x/L) / (i*(n-m)*pi/L)] from -L to L
#   = (L / (i*(n-m)*pi)) * (exp(i*(n-m)*pi) - exp(-i*(n-m)*pi))
#   = 0   [since exp(i*k*pi) = (-1)^k for integer k]

# Result:
# <phi_n, phi_m> = 2*L if n == m
#                = 0   if n != m
#
# Or: <phi_n, phi_m> = 2*L * delta_nm


# ============================================================================
# STEP 2: DERIVE FOURIER COEFFICIENTS
# ============================================================================

# Assume f(x) = sum from n=-inf to +inf of c_n * exp(i*n*pi*x/L)
#
# Take inner product with phi_m = exp(i*m*pi*x/L):
#
# <f, phi_m> = <sum_n c_n*phi_n, phi_m>
#            = sum_n c_n * <phi_n, phi_m>
#            = sum_n c_n * (2*L * delta_nm)
#            = 2*L * c_m
#
# Therefore:
# c_m = (1 / 2*L) * <f, phi_m>
#
# EXPANDED:
# c_m = (1 / 2*L) * integral from -L to L of f(x) * exp(-i*m*pi*x/L) dx


# ============================================================================
# STEP 3: PARSEVAL'S IDENTITY
# ============================================================================

# Energy norm squared:
# ||f||^2 = <f, f> = integral from -L to L of |f(x)|^2 dx
#
# Substitute series:
# = integral of (sum_n c_n*exp(i*n*pi*x/L)) * (sum_m conj(c_m)*exp(-i*m*pi*x/L)) dx
# = sum_n sum_m c_n * conj(c_m) * integral of exp(i*(n-m)*pi*x/L) dx
# = sum_n sum_m c_n * conj(c_m) * (2*L * delta_nm)
# = 2*L * sum_n |c_n|^2
#
# PARSEVAL'S IDENTITY:
# (1 / 2*L) * integral from -L to L of |f(x)|^2 dx = sum from n=-inf to +inf of |c_n|^2
#
# OR:
# (1/2L) * int_{-L}^{L} |f(x)|^2 dx = sum_n |c_n|^2


# ============================================================================
# PHYSICAL INTERPRETATION
# ============================================================================

# Time domain:         integral of |f|^2 dx  = total energy
# Frequency domain:    sum of |c_n|^2        = energy per mode
#
# Energy is conserved! The Fourier transform is a unitary operator.


# ============================================================================
# WHY ORTHOGONALITY MATTERS
# ============================================================================

# If basis functions were NOT orthogonal:
#
# 1. Coefficients would COUPLE
#    - Changing c_n would affect projection onto other modes
#
# 2. No simple coefficient formula
#    - Couldn't just do c_n = <f, phi_n> / ||phi_n||^2
#    - Would need to solve a coupled linear system
#
# 3. Lose physical interpretation
#    - |c_n|^2 would NOT be "energy in mode n"
#
# Orthogonality = Independence of frequency components
# Each mode contributes separately to the total signal


# ============================================================================
# KEY FORMULAS SUMMARY (CODE FORMAT)
# ============================================================================

# COEFFICIENT:
# c_n = (1/(2*L)) * integral_{-L}^{L} f(x) * exp(-1j*n*pi*x/L) dx
#
# SERIES:
# f(x) = sum_{n=-inf}^{+inf} c_n * exp(1j*n*pi*x/L)
#
# PARSEVAL:
# (1/(2*L)) * integral_{-L}^{L} |f(x)|^2 dx = sum_{n=-inf}^{+inf} |c_n|^2
