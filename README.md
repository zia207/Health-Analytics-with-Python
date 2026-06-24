# Health Analytics with Python

A comprehensive tutorial series — **from raw EHR data to production-ready clinical models**.

[![View Tutorial Site](https://img.shields.io/badge/View_Tutorial-GitHub_Pages-0d6e8a?style=for-the-badge)](https://zia207.github.io/Health-Analytics-with-Python/)

## Overview

| | |
|---|---|
| **Modules** | 8 |
| **Notebooks** | 64 |
| **Level** | Intermediate to Advanced |
| **Language** | Python 3.10+ · Colab-compatible |
| **Data** | Synthetic (MIMIC-III inspired) · `seed=42` throughout |

## Browse Online

**[https://zia207.github.io/Health-Analytics-with-Python/](https://zia207.github.io/Health-Analytics-with-Python/)**

All notebooks are pre-rendered as HTML in the [`docs/`](docs/) folder for GitHub Pages.

## Modules

| # | Module | Focus |
|---|--------|-------|
| 01 | Python Foundations | EHR data structures, HIPAA-safe workflows |
| 02 | Exploratory Data Analysis | Readmission cohort, missingness, comorbidity heatmaps |
| 03 | Statistical Inference | RR/OR/CI, survival analysis, confounding |
| 04 | Machine Learning | Clinical prediction, SHAP, calibration, DCA |
| 05 | NLP for Clinical Text | De-identification, ICD coding, BERT, summarisation |
| 06 | Causal Inference | DAGs, PS matching, DiD, ITS, TMLE |
| 07 | Geospatial Epidemiology | Cluster detection, BYM smoothing, 2SFCA access |
| 08 | Reproducible Research & Deployment | Quarto, Streamlit, MLflow, FastAPI, CI/CD |

Start with [`MOD00_NTRO_HealthPy_Tutorial_Series.ipynb`](MOD00_NTRO_HealthPy_Tutorial_Series.ipynb) for the full series guide.

## Local Setup

```bash
git clone https://github.com/zia207/Health-Analytics-with-Python.git
cd Health-Analytics-with-Python
pip install -r requirements.txt
jupyter lab
```

## GitHub Pages

This site is published from the `/docs` folder using a [Quarto](https://quarto.org/) website — the same layout style as [Python for Beginners](https://python-beginners-zia207.netlify.app/) (navbar, sidebar navigation, search, and footer).

**Live site:** [https://zia207.github.io/Health-Analytics-with-Python/](https://zia207.github.io/Health-Analytics-with-Python/)

### Build the site locally

```bash
./scripts/build_site.sh
```

Or step by step:

```bash
python3 scripts/prepare_quarto_notebooks.py
python3 scripts/generate_quarto_yml.py
quarto render
```

### Enable GitHub Pages

1. Go to **Settings → Pages**
2. Set **Source** to **Deploy from a branch**
3. Choose branch `main` (or `master`) and folder **`/docs`**
4. Save — the site will be live at `https://zia207.github.io/Health-Analytics-with-Python/`

## Author

**Dr. Zia U. Ahmed** · [Upatta Analytics](https://github.com/zia207)
