#!/usr/bin/env python3
"""Generate _quarto.yml sidebar from module notebooks."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

MODULES = {
    "00": ("Introduction", []),
    "01": ("Python Foundations", "Track A"),
    "02": ("Exploratory Data Analysis", "Track A"),
    "03": ("Statistical Inference", "Track A"),
    "04": ("Machine Learning", "Track A"),
    "05": ("NLP for Clinical Text", "Track A"),
    "06": ("Causal Inference", "Track B"),
    "07": ("Geospatial Epidemiology", "Track B"),
    "08": ("Reproducible Research & Deployment", "Track B"),
}

NB_LABELS: dict[str, str] = {
    "MOD00_NTRO_HealthPy_Tutorial_Series.ipynb": "Series Overview",
    "MOD01_NB01_Python_Foundations_Health_Data.ipynb": "NB-01 · Python Foundations for Health Data",
    "MOD01_NB02_Descriptive_Statistics_Health_Metrics.ipynb": "NB-02 · Descriptive Statistics & Health Metrics",
    "MOD01_NB03_Health_Data_Ecosystem_Codes.ipynb": "NB-03 · Health Data Ecosystem & Codes",
    "MOD02_NB01_Data_Loading_Profiling.ipynb": "Data Loading & Automated Profiling",
    "MOD02_NB02_Descriptive_Statistics.ipynb": "Descriptive Statistics for Clinical Variables",
    "MOD02_NB03_Clinical_Visualisation.ipynb": "Visualising Clinical Distributions",
    "MOD02_NB04_TimeSeries_Admissions.ipynb": "Time-Series of Admissions & Clinical Events",
    "MOD02_NB05_Missingness_Imputation.ipynb": "Missingness Analysis & Imputation",
    "MOD02_NB06_Comorbidity_Heatmap.ipynb": "Comorbidity Co-occurrence Heatmap",
    "MOD02_NB07_Geospatial_Disparities.ipynb": "Geospatial Health Disparities Map",
    "MOD02_NB08_Capstone_Readmission_EDA.ipynb": "Capstone · End-to-End EDA on Readmission Risk",
    "MOD03_NB01_Hypothesis_Testing.ipynb": "Hypothesis Testing for Health Outcomes",
    "MOD03_NB02_RR_OR_CI.ipynb": "Relative Risk, Odds Ratios & Confidence Intervals",
    "MOD03_NB03_Survival_Analysis.ipynb": "Survival Analysis (Kaplan-Meier & Log-Rank)",
    "MOD03_NB04_Linear_Regression.ipynb": "Linear Regression for Continuous Outcomes",
    "MOD03_NB05_Logistic_Regression.ipynb": "Logistic Regression for Binary Outcomes",
    "MOD03_NB06_Count_Regression.ipynb": "Poisson & Negative Binomial Regression",
    "MOD03_NB07_Confounding_EffectModification.ipynb": "Confounding & Effect Modification",
    "MOD03_NB08_Capstone_Inference.ipynb": "Capstone · Multivariable Inference Pipeline",
    "MOD04_NB01_Pipeline_Splits.ipynb": "ML Pipeline Setup & Train/Test Splits",
    "MOD04_NB02_DecisionTree_RandomForest.ipynb": "Decision Trees & Random Forest",
    "MOD04_NB03_XGBoost_LightGBM.ipynb": "XGBoost & LightGBM",
    "MOD04_NB04_Clinical_Model_Evaluation.ipynb": "Clinical Model Evaluation",
    "MOD04_NB05_Hyperparameter_Tuning.ipynb": "Hyperparameter Tuning & Cross-Validation",
    "MOD04_NB06_SHAP_Explainability.ipynb": "SHAP Explainability",
    "MOD04_NB07_Clinical_Prediction_Models.ipynb": "Three Clinical Prediction Models",
    "MOD04_NB08_Capstone_ML_Pipeline.ipynb": "Capstone · End-to-End Clinical ML Pipeline",
    "MOD05_NB01_Clinical_Text_Preprocessing.ipynb": "Clinical Text Preprocessing",
    "MOD05_NB02_Clinical_NER.ipynb": "Clinical Named Entity Recognition",
    "MOD05_NB03_TF_IDF_Classification.ipynb": "TF-IDF & Clinical Text Classification",
    "MOD05_NB04_Word_Embeddings.ipynb": "Word Embeddings & Word2Vec",
    "MOD05_NB05_Clinical_BERT.ipynb": "Clinical BERT (BioBERT & ClinicalBERT)",
    "MOD05_NB06_ICD_Coding_Medications.ipynb": "ICD Coding & Medication Extraction",
    "MOD05_NB07_Summarisation_ZeroShot.ipynb": "Summarisation & Zero-Shot NLP",
    "MOD05_NB08_Capstone_Clinical_NLP.ipynb": "Capstone · End-to-End Clinical NLP Pipeline",
    "MOD06_NB01_DAGs_Confounding.ipynb": "DAGs, Confounding & Identification",
    "MOD06_NB02_Propensity_Scores.ipynb": "Propensity Score Methods",
    "MOD06_NB03_DiD_EventStudy.ipynb": "Difference-in-Differences & Event Studies",
    "MOD06_NB04_ITS_SyntheticControl.ipynb": "Interrupted Time Series & Synthetic Control",
    "MOD06_NB05_IV_RDD.ipynb": "Instrumental Variables & RDD",
    "MOD06_NB06_GComp_TMLE.ipynb": "G-Computation, TMLE & Mediation",
    "MOD06_NB07_Sensitivity_Reporting.ipynb": "Sensitivity Analysis & Reporting",
    "MOD06_NB08_Capstone_Causal_Pipeline.ipynb": "Capstone · Causal Inference Pipeline",
    "MOD07_NB01_Spatial_Data_Choropleth.ipynb": "Spatial Data & Choropleth Mapping",
    "MOD07_NB02_Spatial_Autocorrelation.ipynb": "Spatial Autocorrelation & Moran's I",
    "MOD07_NB03_Spatial_Regression_GWR.ipynb": "Spatial Regression: Lag, Error & GWR",
    "MOD07_NB04_Disease_Mapping_Bayes.ipynb": "Disease Mapping & Bayesian Smoothing",
    "MOD07_NB05_Cluster_Detection.ipynb": "Spatial Cluster Detection",
    "MOD07_NB06_Environmental_Epidemiology.ipynb": "Environmental Epidemiology",
    "MOD07_NB07_Health_Service_Access.ipynb": "Health Service Area & Access Metrics",
    "MOD07_NB08_Capstone_Spatial_Atlas.ipynb": "Capstone · Spatial Health Inequity Atlas",
    "MOD08_NB01_Reproducible_Foundations.ipynb": "Reproducible Research Foundations",
    "MOD08_NB02_Quarto_Reports.ipynb": "Quarto Documents for Health Reports",
    "MOD08_NB03_Streamlit_Dashboards.ipynb": "Streamlit Dashboards",
    "MOD08_NB04_MLflow_Tracking.ipynb": "MLflow Model Tracking & Registry",
    "MOD08_NB05_FastAPI_Serving.ipynb": "FastAPI for Clinical Model Serving",
    "MOD08_NB06_Testing_CICD.ipynb": "Testing, CI/CD & Code Quality",
    "MOD08_NB07_ModelCards_Governance.ipynb": "Model Cards & Clinical AI Governance",
    "MOD08_NB08_Capstone_Deployment.ipynb": "Capstone · Full Deployment Pipeline",
}


def yaml_quote(value: str) -> str:
    if any(ch in value for ch in ':&*?#[]{}|>!%@`"'):
        return json.dumps(value)
    return value


def notebook_label(path: Path) -> str:
    return NB_LABELS.get(path.name, path.stem.replace("_", " "))


def group_notebooks() -> dict[str, list[Path]]:
    groups: dict[str, list[Path]] = {k: [] for k in MODULES}
    for path in sorted(ROOT.glob("MOD*.ipynb")):
        mod = re.match(r"MOD(\d{2})_", path.name)
        if mod:
            groups[mod.group(1)].append(path)
    return groups


def yaml_sidebar() -> str:
    lines: list[str] = []
    groups = group_notebooks()

    lines.append('      - section: "**Health Analytics with Python**"')
    lines.append("        contents:")
    lines.append("          - index.qmd")
    for nb in groups["00"]:
        lines.append(f"          - href: {nb.name}")
        lines.append(f"            text: {yaml_quote(notebook_label(nb))}")

    for mod_id in sorted(MODULES.keys()):
        if mod_id == "00":
            continue
        title, track = MODULES[mod_id]
        section = f"**Module {mod_id} — {title}**"
        if track:
            section += f" ({track})"
        lines.append(f'      - section: "{section}"')
        lines.append("        contents:")
        for nb in groups[mod_id]:
            lines.append(f"          - href: {nb.name}")
            lines.append(f"            text: {yaml_quote(notebook_label(nb))}")

    return "\n".join(lines)


def main() -> None:
    sidebar = yaml_sidebar()
    yml = f"""project:
  type: website
  output-dir: docs
  render:
    - index.qmd
    - "MOD*.ipynb"

website:
  title: "Health Analytics with Python"
  site-url: https://zia207.github.io/Health-Analytics-with-Python/
  description: "From raw EHR data to production-ready clinical models — 8 modules, 60 notebooks."
  repo-url: https://github.com/zia207/Health-Analytics-with-Python
  repo-actions: [edit, issue]
  page-navigation: true
  search:
    location: navbar
    type: overlay
  navbar:
    background: primary
    foreground: light
    pinned: true
    left:
      - href: index.qmd
        text: Home
    right:
      - icon: github
        href: https://github.com/zia207/Health-Analytics-with-Python
      - icon: linkedin
        href: https://www.linkedin.com/in/zia-ahmed207
      - text: "zia207@gmail.com"
        href: mailto:zia207@gmail.com
  sidebar:
    logo: Images/chapter_logo_health_analytices.png
    style: docked
    search: true
    collapse-level: 1
    contents:
{sidebar}
  page-footer:
    left: "© CC-By Zia Ahmed, Upatta Analytics, 2026"
    right: "Built with [Quarto](https://quarto.org/)"

title-block-banner: true

format:
  html:
    theme:
      - cosmo
      - _quarto.scss
    toc: true
    toc-depth: 3
    code-copy: true
    code-overflow: wrap
    smooth-scroll: true
    grid:
      sidebar-width: 300px
      body-width: 900px
      margin-width: 200px

execute:
  enabled: false
  freeze: auto

resources:
  - Images/**
"""
    out = ROOT / "_quarto.yml"
    out.write_text(yml, encoding="utf-8")
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
