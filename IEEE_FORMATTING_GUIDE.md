# IEEE T-UFFC Paper Submission — Formatting Guide

---

## Files Generated

### Paper Content (Markdown)
- `ieee_abstract_final.md` — Abstract (248 words)
- `ieee_introduction.md` — Section I. Introduction (~1,100 words)
- `ieee_methods.md` — Section II. Theory & Methods (~1,800 words)
- `ieee_results.md` — Section III. Results (~1,400 words)
- `ieee_discussion.md` — Section IV. Discussion (~1,400 words)
- `ieee_conclusion.md` — Section V. Conclusion (~380 words)
- `ieee_references.md` — References (31 citations)

### LaTeX Template
- `ieee_paper.tex` — IEEEtran LaTeX template with placeholder sections

### Figures (300 DPI)
- `figure1_calibration.png` — Forward model calibration
- `figure2_posteriors.png` — Bayesian posterior distributions
- `figure3_noise_robustness.png` — Noise robustness analysis
- `figure4_landscapes.png` — 2D parameter misfit landscapes

---

## IEEE Formatting Requirements

### Page Setup
- **Paper size:** US Letter (8.5" × 11")
- **Columns:** Two-column format
- **Column width:** 3.5 inches
- **Column separation:** 0.25 inches
- **Margins:** 0.75 inches (top/bottom/left/right)

### Font Specifications
| Element | Font | Size |
|---------|------|------|
| Title | Times New Roman | 14 pt, bold |
| Author names | Times New Roman | 12 pt |
| Section headings | Times New Roman | 10 pt, bold, all caps |
| Subsection headings | Times New Roman | 10 pt, bold |
| Body text | Times New Roman | 9 pt |
| Captions | Times New Roman | 8 pt |
| References | Times New Roman | 8 pt |

### Figure Requirements
- **Format:** EPS or PNG/JPEG (300 DPI minimum)
- **Width:** Single column (3.5") or double column (7.25")
- **Font:** 8–10 pt for axis labels, 8 pt for tick labels
- **Lines:** 1–2 pt thickness
- **Color:** RGB or CMYK (CMYK preferred for print)

### Table Requirements
- **Format:** Three-line style (top, header, bottom rules)
- **Font:** 8–9 pt
- **Alignment:** Centered or left-aligned
- **Captions:** Above table, bold, sentence case

---

## Next Steps to Complete Submission

### 1. Convert Markdown to LaTeX
Copy content from each `.md` file into the corresponding section of `ieee_paper.tex`:

```
% In ieee_paper.tex, replace:
[CONTENT FROM ieee_methods.md TO BE INSERTED HERE]

% With actual content from ieee_methods.md
```

### 2. Format Equations
Convert Markdown equations to LaTeX:

**Markdown:**
```
$$
c_p(ω) = √(G₀/ρ · ...)
$$
```

**LaTeX:**
```latex
\begin{equation}
c_p(\omega) = \sqrt{\frac{G_0}{\rho} \cdot \frac{1 + \omega^2\tau_\varepsilon\tau_\sigma}{1 + \omega^2\tau_\sigma^2}}
\end{equation}
```

### 3. Insert Figures
Add figure environment in LaTeX:

```latex
\begin{figure}[!t]
\centering
\includegraphics[width=3.5in]{figure1_calibration.png}
\caption{Forward model calibration. (a) Phase velocity dispersion showing FDTD-extracted data (blue circles), analytical Zener model with ground-truth parameters (green dashed), and calibrated apparent Zener model (red solid). (b) Parameter comparison showing ground-truth versus calibrated values on logarithmic scale.}
\label{fig:calibration}
\end{figure}
```

### 4. Insert Tables
Convert markdown tables to LaTeX:

```latex
\begin{table}[!t]
\caption{MCMC Convergence Diagnostics}
\label{tab:convergence}
\centering
\begin{tabular}{|c|c|c|c|c|}
\hline
\textbf{Metric} & \textbf{Chain 1} & \textbf{Chain 2} & \textbf{Chain 3} & \textbf{Target} \\
\hline
Acceptance rate & 24.7\% & 25.1\% & 24.3\% & 20--30\% \\
\hline
Effective samples & 12,001 & 11,847 & 12,156 & >10,000 \\
\hline
\end{tabular}
\end{table}
```

### 5. Complete References
Replace the sample bibliography in `ieee_paper.tex` with all 31 references from `ieee_references.md`. Ensure IEEE formatting:

```latex
\bibitem{label}
Initials.~Surname, ``Title,'' \emph{Abbrev. Journal}, vol.~x, no.~x, pp.~xx--xx, year.
```

### 6. Add Author Information
Update author block in `ieee_paper.tex`:

```latex
\author{Author~One,~\IEEEmembership{Member,~IEEE,}
        Author~Two,~\IEEEmembership{Member,~IEEE,}
        and~Author~Three,~\IEEEmembership{Member,~IEEE}%
\thanks{This work was supported by [funding source].}
\thanks{Author One is with the Department, Institution, 
        City, Country (e-mail: email@domain).}
```

### 7. Generate PDF
Compile LaTeX (requires IEEEtran.cls):

```bash
pdflatex ieee_paper.tex
bibtex ieee_paper
pdflatex ieee_paper.tex
pdflatex ieee_paper.tex
```

---

## IEEE T-UFFC Submission Checklist

### Content
- [ ] Abstract: 150–300 words
- [ ] Paper length: 8–12 pages typical
- [ ] Figures: 300 DPI, proper fonts
- [ ] Tables: Three-line style
- [ ] Equations: Numbered, properly formatted
- [ ] References: 20–50 typical, properly formatted

### Format
- [ ] IEEEtran document class
- [ ] Two-column layout
- [ ] 9 pt body font
- [ ] 10 pt section headings
- [ ] Proper margins
- [ ] Figure captions below figures
- [ ] Table captions above tables

### Supplementary Materials
- [ ] Cover letter highlighting contributions
- [ ] Suggested reviewers (3–5)
- [ ] Author biographies (50–100 words each)
- [ ] Data availability statement
- [ ] Code repository link (optional but recommended)

---

## Common IEEE LaTeX Issues

### Equation Numbering
```latex
% Use \begin{equation} for numbered equations
\begin{equation}
c_p = \sqrt{G/\rho}
\label{eq:velocity}
\end{equation}

% Reference with: see (\ref{eq:velocity})
```

### Special Characters
```latex
% Use proper LaTeX commands
$G_\infty$       % G_infinity
$\tau_\sigma$    % tau_sigma
$\pm$            % plus-minus
dB               % dB (no special handling)
```

### Citations
```latex
% Single citation
\cite{label}

% Multiple citations
\cite{label1,label2,label3}

% Citation with note
\cite[see][p.~12]{label}
```

### Units
```latex
% Use siunitx package for proper units
\SI{20}{\decibel}      % 20 dB
\SI{150}{\hertz}       % 150 Hz
\SI{2000}{\pascal}     % 2000 Pa
```

---

## Word Count Summary

| Section | Words | Pages (est.) |
|---------|-------|--------------|
| Abstract | 248 | 0.3 |
| Introduction | 1,100 | 1.5 |
| Methods | 1,800 | 2.5 |
| Results | 1,400 | 2.0 |
| Discussion | 1,400 | 2.0 |
| Conclusion | 380 | 0.5 |
| **Total** | **~6,330** | **~9 pages** |

Target: 8–12 pages ✓

---

## Submission Portal

**Journal:** IEEE Transactions on Ultrasonics, Ferroelectrics, and Frequency Control

**Submission site:** https://mc.manuscriptcentral.com/tuffc-ieee

**Article type:** Regular Paper

**Required files:**
- Main manuscript (PDF)
- Source files (LaTeX or Word)
- Figure files (separate, high resolution)
- Cover letter
- Author information form

---

## Useful Resources

- **IEEE Author Center:** https://journals.ieeeauthorcenter.ieee.org/
- **IEEEtran LaTeX class:** https://www.ctan.org/pkg/ieeetran
- **T-UFFC website:** https://ieee-tuffc.org/
- **Template downloads:** Available on submission portal

---

Last updated: 2026-03-19
