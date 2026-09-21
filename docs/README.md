# Report

[Read regulator.pdf](regulator.pdf). Source: regulator.tex; bibliography: references.bib.

Build in this directory with a LaTeX installation providing IEEEtran and the packages in the preamble:

```text
pdflatex -interaction=nonstopmode -halt-on-error regulator.tex
biber regulator
pdflatex -interaction=nonstopmode -halt-on-error regulator.tex
pdflatex -interaction=nonstopmode -halt-on-error regulator.tex
```

The included figure PDFs are used directly. Simulation results describe the stated model conditions; detailed physical measurements remain pending. The PDF was built and visually checked locally before this snapshot.
