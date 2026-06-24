#!/usr/bin/env bash
# Re-run previously failed notebooks in-place.
set -uo pipefail
cd "$(dirname "$0")/.."

PYTHON="${PYTHON:-python3}"
LOG=scripts/nbconvert_retry.log
TIMEOUT=1200

FAILED=(
  MOD02_NB01_Data_Loading_Profiling.ipynb
  MOD02_NB04_TimeSeries_Admissions.ipynb
  MOD02_NB05_Missingness_Imputation.ipynb
  MOD02_NB08_Capstone_Readmission_EDA.ipynb
  MOD03_NB01_Hypothesis_Testing.ipynb
  MOD03_NB02_RR_OR_CI.ipynb
  MOD03_NB03_Survival_Analysis.ipynb
  MOD03_NB04_Linear_Regression.ipynb
  MOD03_NB05_Logistic_Regression.ipynb
  MOD03_NB06_Count_Regression.ipynb
  MOD03_NB07_Confounding_EffectModification.ipynb
  MOD03_NB08_Capstone_Inference.ipynb
  MOD04_NB01_Pipeline_Splits.ipynb
  MOD04_NB02_DecisionTree_RandomForest.ipynb
  MOD04_NB03_XGBoost_LightGBM.ipynb
  MOD04_NB04_Clinical_Model_Evaluation.ipynb
  MOD04_NB05_Hyperparameter_Tuning.ipynb
  MOD04_NB06_SHAP_Explainability.ipynb
  MOD04_NB07_Clinical_Prediction_Models.ipynb
  MOD04_NB08_Capstone_ML_Pipeline.ipynb
  MOD05_NB07_Summarisation_ZeroShot.ipynb
  MOD06_NB03_DiD_EventStudy.ipynb
  MOD06_NB06_GComp_TMLE.ipynb
  MOD07_NB02_Spatial_Autocorrelation.ipynb
  MOD07_NB03_Spatial_Regression_GWR.ipynb
  MOD07_NB06_Environmental_Epidemiology.ipynb
  MOD07_NB08_Capstone_Spatial_Atlas.ipynb
  MOD08_NB03_Streamlit_Dashboards.ipynb
  MOD08_NB04_MLflow_Tracking.ipynb
  MOD08_NB08_Capstone_Deployment.ipynb
)

: > "$LOG"
ok=0; fail=0

for nb in "${FAILED[@]}"; do
  echo "==> $(date -Iseconds) Processing $nb" | tee -a "$LOG"
  if "$PYTHON" -m jupyter nbconvert \
      --execute \
      --to notebook \
      --inplace \
      --ExecutePreprocessor.timeout="$TIMEOUT" \
      "$nb" >> "$LOG" 2>&1; then
    echo "OK: $nb" | tee -a "$LOG"
    ok=$((ok + 1))
  else
    echo "FAIL: $nb" | tee -a "$LOG"
    fail=$((fail + 1))
  fi
done

echo "==> Retry done: $ok succeeded, $fail failed" | tee -a "$LOG"
