# BibTeX References

## Quick Start

The `references.bib` file contains 15+ citations formatted for LaTeX/BibTeX.

### Essential Papers (Cite These)

```bibtex
@article{Sarvazyan1998, ...}  % Foundation: G = ρc_s²
@article{Nightingale2002, ...} % ARFI imaging
@article{Chen2009, ...}        % SDUV multi-frequency
@article{Parker2014, ...}      % KV model justification
@article{Barr2022, ...}        % Clinical viscosity relevance
```

### Using in LaTeX

```latex
\documentclass{article}
\begin{document}

Shear wave elastography was first proposed by Sarvazyan et al. \cite{Sarvazyan1998}.
Multi-frequency approaches allow separation of elastic and viscous components \cite{Chen2009}.

\bibliographystyle{ieeetr}  % or plain, apalike, unsrt
\bibliography{references}

\end{document}
```

### Citation Commands

| Command | Result |
|---------|--------|
| `\cite{Sarvazyan1998}` | [1] or (Sarvazyan et al., 1998) |
| `\cite[page 5]{Sarvazyan1998}` | [1, page 5] |
| `\cite{Sarvazyan1998,Chen2009}` | [1,2] or [1-2] |
| `\citeauthor{Sarvazyan1998}` | Sarvazyan et al. |
| `\citeyear{Sarvazyan1998}` | 1998 |

### Bibliography Styles

| Style | Format | Best For |
|-------|--------|----------|
| `plain` | [1] Author. Title. Journal. Year | General |
| `ieeetr` | [1] Author, "Title," Journal, Year | Engineering |
| `apalike` | (Author, Year) Author. Year. Title. | Social sciences |
| `unsrt` | [1] Same as plain, but order of appearance | When citation order matters |

---

## Categories in references.bib

### Essential (5 papers)
1. Sarvazyan1998 - Foundation
2. Nightingale2002 - ARFI
3. Chen2009 - SDUV
4. Parker2014 - Models
5. Barr2022 - Clinical

### Supporting (4 papers)
6. Manduca2001 - Inverse problem
7. Zhang2008 - KV validation
8. Wang2021 - Deep learning review
9. Barry2021 - Limitations

### Experimental (2 papers)
10. Bercoff2004 - Supersonic
11. Klatt2007 - Broadband MRE

### Clinical (2 papers)
12. Sandrin2003 - FibroScan
13. Bavu2011 - 2D SWE

### Foundational (1 paper)
14. Ophir1991 - First elastography

### ML/Computational (1 paper)
15. Raissi2019 - PINNs

### Optional (2 papers)
16. Ormachea2019 - Anisotropy
17. Schmerr2015 - NDE textbook

---

## Key Equations in Citations

| Paper | Key Equation |
|-------|-------------|
| Sarvazyan1998 | $G = \\rho c_s^2$ |
| Chen2009 | $c_s(\\omega) = \\sqrt{\\sqrt{G'^2 + (\\omega\\eta)^2} / \\rho}$ |
| Parker2014 | $\sigma = G'\\varepsilon + \\eta \\dot{\\varepsilon}$ |

---

## BibTeX Fields Explained

```bibtex
@article{Key,           % Citation key (use this in \cite{})
  author    = {},       % Author names
  title     = {},       % Paper title
  journal   = {},       % Journal name
  year      = {},       % Publication year
  volume    = {},       % Volume number
  number    = {},       % Issue number
  pages     = {},       % Page range
  doi       = {},       % Digital Object Identifier
  pmid      = {},       % PubMed ID
  url       = {},       % Direct URL
  keywords  = {},       % Search terms
  note      = {},       % Personal notes
  arxiv     = {}        % arXiv ID (for preprints)
}
```

---

## Export to Other Formats

### Zotero Import
1. Open Zotero
2. File → Import
3. Select `references.bib`

### Mendeley Import
1. File → Add Files
2. Select `references.bib`

### EndNote Import
1. File → Import
2. Choose `BibTeX` as filter

---

*References compiled: March 7, 2026*
*For: Acoustic NDE Research Project*
