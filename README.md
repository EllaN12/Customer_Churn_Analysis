# Customer Churn Prediction & Causal Analysis

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![PySpark](https://img.shields.io/badge/PySpark-3.x-E25A1C?style=flat-square&logo=apachespark&logoColor=white)](https://spark.apache.org/)
[![H2O AutoML](https://img.shields.io/badge/H2O-AutoML-FFD700?style=flat-square)](https://docs.h2o.ai/)
[![PyMC](https://img.shields.io/badge/PyMC-5.0+-FF6B35?style=flat-square)](https://www.pymc.io/)
[![MLflow](https://img.shields.io/badge/MLflow-Tracking-0194E2?style=flat-square&logo=mlflow)](https://mlflow.org/)
[![GCP](https://img.shields.io/badge/GCP-Cloud%20Run-4285F4?style=flat-square&logo=googlecloud&logoColor=white)](https://cloud.google.com/run)
[![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED?style=flat-square&logo=docker&logoColor=white)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-22C55E?style=flat-square)](LICENSE)

> **An end-to-end data science pipeline** — from raw telco CRM data to live cloud deployment — demonstrating machine learning, causal inference, Bayesian experimental design, and production monitoring.

---

## Table of Contents

- [Project Overview](#project-overview)
- [The Scientific Narrative](#the-scientific-narrative)
- [Key Results](#key-results)
- [Project Structure](#project-structure)
- [Phase 1: ML Analysis](#phase-1-ml-analysis)
- [Phase 2: Causal Validation](#phase-2-causal-validation)
- [Phase 3: Experimental Design](#phase-3-experimental-design)
- [Phase 4: Implementation & Monitoring](#phase-4-implementation--monitoring)
- [Phase 5: Cloud Deployment](#phase-5-cloud-deployment)
- [Installation & Quickstart](#installation--quickstart)
- [Reproducing Results](#reproducing-results)
- [Business Recommendations](#business-recommendations)
- [Technology Stack](#technology-stack)
- [Design Documents](#design-documents)
- [License](#license)

---

## Project Overview

This project addresses a core business problem in telecommunications: **predicting and causally understanding customer churn** at scale. It goes well beyond a standard predictive model by rigorously applying causal inference to distinguish correlation from causation — a distinction that separates actionable strategy from misleading analysis.

**Dataset:** 7,043 customers × 21 features (Kaggle Telco Customer Churn)
**Outcome:** Binary churn indicator — 26.5% overall churn rate, 41.4% minimum churn probability among predicted churners
**Revenue at Risk:** $1.53M LTV (1,869 actual churners × $74.44/mo × 11-month avg lifetime)

### Five-Phase Pipeline

| Phase | Focus | Primary Output |
|-------|-------|----------------|
| **1. ML Analysis** | PySpark EDA + H2O AutoML | 96.4% AUC-ROC stacked ensemble |
| **2. Causal Validation** | Collider correction, Bayesian causal estimation | −5.8pp causal add-on effect (87% probability) |
| **3. Experimental Design** | Power analysis, stratified randomisation | 3 targeted Bayesian tests, 95% power |
| **4. Implementation & Monitoring** | Hierarchical Bayesian A/B engine, sequential monitoring | Week 6 winner declared, 99% confidence |
| **5. Deployment** | Docker + GCP Cloud Run | Live Bayesian dashboard |

---

## The Scientific Narrative

### Discovery: Strong Early Tenure Signal

Exploratory analysis revealed that customers in their **first 40 days** churn at 79% versus a 26.5% baseline — a **+52 percentage point penalty** affecting roughly 25% of the customer base. This became the central hypothesis for intervention.

### Attempted Causal Validation — and a Critical Correction

The initial Bayesian model controlled for tenure, contract type, and payment method as confounders. This is a common but methodologically incorrect choice:

- **Tenure is a collider.** It is caused by both service add-on adoption *and* churn (survivorship bias). Conditioning on it opens a non-causal path — a textbook case of collider bias, empirically confirmed via stratification reversal.
- **Contract type and payment method are other treatments** — endogenous customer choices correlated with loyalty, not pre-treatment confounders.
- **Monthly and total charges are mediators** — they sit on the causal path from add-ons to churn. Controlling for them blocks the effect we want to estimate.

Catching and correcting this bias is the methodological centrepiece of the project. The corrected model conditions only on **exogenous pre-treatment demographics** (SeniorCitizen, Dependents, Partner, Gender) — the only variables that satisfy the backdoor criterion.

### Rigorous Solution: Randomised Experimentation

Because observational data has fundamental limits even after correction, the project culminates in **three prioritised randomised experiments** designed with 95% Bayesian power, sequential monitoring with ROPE-based stopping rules, and automated decision memos — ready for production rollout.

---

## Key Results

### Machine Learning Performance

| Model | AUC-ROC | AUC-PR | Recall (Churners) | Precision |
|-------|---------|--------|-------------------|-----------|
| Decision Tree (PySpark) | 72.0% | 52.6% | ~65% | ~72% |
| **H2O Stacked Ensemble** | **93.4%** | **96.72%** | **~90.5%** | **~78%** |

**Selected model:** H2O AutoML Stacked Ensemble — combines GBM, XGBoost, and GLM base learners via metalearner. SMOTE applied for class balancing.

### Causal Estimates 

| Driver | Naive Effect | Corrected Causal Effect | Notes |
|--------|-------------|-------------------------|-------|
| Service add-on bundle | −0.2pp | **−5.8pp** | 95% CI: [−8.2%, −3.4%]. P(reduces churn by 5%+) = 87% |
| Early tenure ≤40 days | +52pp | Requires experiment | Strongest signal, time-sensitive window |
| Month-to-month contract | +36pp | Endogenous treatment | Needs own causal identification |
| Electronic check payment | +28pp | Endogenous treatment | Needs own causal identification |

### Projected Business Impact (Conservative, $74.44/mo revenue base)

| Test | Target Segment | Sample | Annual Impact |
|------|---------------|--------|---------------|
| Test 1 — Early Intervention | Customers ≤40 days (74.7% churn) | 100/arm | ~$204K |
| Test 2 — Contract + Add-on Bundle | Month-to-month customers (62% churn) | 150/arm | ~$98K |
| Test 3 — Targeted Messaging | Senior citizens / No-dependents (~55% churn) | 200/arm | ~$47K |
| **Total Portfolio** | | | **~$350K** |

### Phase 4 Monitoring Result

Week 6 interim analysis declared **Treatment 2 (Smart Start $125)** the winner:
- Confidence level: **99%**
- Churn reduction: **+18.8pp** (95% CI: [11.0%, 26.5%])
- Annual profit: **$82K** — 700% ROI, 1.7-month payback

---

## Project Structure

```
Customer_Churn_Analysis/
│
├── README.md
├── LICENSE
├── Customer_Churn_Final.pptx              ← 17-slide executive presentation
│
├── Design_documents/                      ← Methodology reference
│   ├── Bayesian_Experimental_Design_Final.md  ← Authoritative design spec
│   
│   ├── REVENUE_CALCULATIONS_BREAKDOWN.md      ← Revenue at risk calculations
│   └── bayesian_ab_test_design.md             ← Original test design notes
│
├── Phase_1_ML_Analysis/
│   ├── Decision_Tress_analysis.py         ← EDA + PySpark Decision Tree
│   ├── AutoML_h20_Prediction.py           ← H2O AutoML + SMOTE + MLflow
│   ├── Recommendation.py                  ← Rule-based recommendation engine
│   └── Results/                           ← AUC curves, confusion matrix, feature importance
│
├── Phase_2_Causal_Validation/
│   ├── proper_causal_inference.py         ← Causal model (primary)
│   ├── full_dataset_causal_validation.py  ← ChurnDataPipeline class + validation
│   ├── bayesian_analysis_engine.py        ← Reusable Bayesian engine (4 chains)
│   └── Results/
│       ├── posterior_plots.png            ← MCMC posterior distributions
│       ├── trace_plots.png                ← Convergence diagnostics (R-hat ≈ 1.0)
│       ├── posterior_predictive_check.png ← Calibration check
│       ├── churn_drivers_ranked.png       ← Effect sizes ranked
│       ├── variable_causal_roles.png      ← DAG variable classification
│       ├── collider_bias_demo.png         ← Stratification reversal proof
│       └── causal_correction_summary.csv  ← Naive vs corrected estimates
│
├── Phase_3_Experimental_Design/
│   ├── power_analysis_experiments.py      ← Monte Carlo power (3 approved tests)
│   ├── experiment_randomization.py        ← Stratified block randomisation
│   ├── monte_carlo_simulation.py          ← 1,000-iteration power simulation
│   ├── sample_size_calculator.py          ← Sample size optimisation tool
│   └── Results/
│       ├── power_curve.png                ← Power by sample size
│       ├── sample_size_sensitivity.png    ← Sensitivity to effect size
│       └── power_comparison.png           ← Bayesian vs Frequentist power
│
├── Phase_4_implementation_and_Monitoring/
│   ├── bayesian_ab_test_implementation.py ← Full hierarchical Bayesian A/B engine
│   ├── bayesian_monitoring_system.py      ← Week-by-week sequential monitor
│   ├── streamlit_dashboard.py             ← Interactive Bayesian dashboard
│   ├── streamlit_experiment_monitor.py    ← Experiment-specific monitor UI
│   ├── automated_reporting.py             ← Automated stakeholder reports
│   └── Results/
│       ├── executive_dashboard_week_6.png ← Week 6 snapshot
│       ├── posterior_plots.png            ← Final posterior distributions
│       ├── trace_plots.png                ← MCMC convergence
│       ├── weekly_summary_week_6.txt      ← Automated weekly summary
│       ├── decision_memo_week_6.txt       ← Stopping decision memo
│       └── logs/                          ← Randomisation & assignment logs
│
├── Phase_5_Depolyment guide/
│   ├── Dockerfile                         ← Python 3.9-slim container
│   ├── .dockerignore                      ← Build context exclusions
│   ├── requirements.txt                   ← Pinned dependencies
│   ├── deploy_to_cloud_run.sh             ← GCP Cloud Run deployment script
│   ├── DEPLOYMENT.md                      ← Step-by-step Cloud Run protocol
│   ├── streamlit_dashboard.py             ← Production dashboard entry point
│   └── Results/
│       └── executive_dashboard_week_6.png
│
└── Models/
    ├── decision_tree_model/               ← PySpark ML Pipeline (Parquet)
    └── model_h2o_stacked_ensemble/        ← H2O MOJO binary model
```

---

## Phase 1: ML Analysis

**Scripts:** `Phase_1_ML_Analysis/Decision_Tress_analysis.py`, `AutoML_h20_Prediction.py`, `Recommendation.py`
**Tracking:** MLflow experiment `Churn_Analysis`

### Data Pipeline (PySpark)

A production-portable ETL pipeline built on PySpark:

1. **Ingestion** — `SparkSession` CSV read with schema inference
2. **Schema validation** — dimension checks + null audit per column
3. **Type casting** — `TotalCharges` string → double; `SeniorCitizen` int → string
4. **Imputation** — median for numerics; mode for categoricals
5. **Outlier handling** — IQR-based clipping on continuous features
6. **Feature encoding** — `StringIndexer` → `OneHotEncoder` via `PipelineModel`
7. **Train/test split** — 80/20 stratified by churn label

### H2O AutoML Stacked Ensemble

```python
import h2o
from h2o.automl import H2OAutoML

h2o.init()
aml = H2OAutoML(max_models=20, seed=42, balance_classes=True)
aml.train(x=features, y="Churn", training_frame=train_h2o)
leader = aml.leader  # Stacked Ensemble: GBM + XGBoost + GLM via metalearner
```

**Results:** AUC-ROC 93.4% · AUC-PR 96.72% · Recall ~90.5% · Precision ~78%

SMOTE oversampling (`imblearn`) was applied to address class imbalance (26.5% positive class) before H2O training. All runs tracked with MLflow — hyperparameters, AUC-ROC, AUC-PR, F1, confusion matrix, ROC curve, and feature importance.

### Top Churn Drivers (H2O Feature Importance)

| Rank | Driver | Naive Churn Differential |
|------|--------|--------------------------|
| #1 | Tenure ≤ 40 days | +52pp (79% vs 26.5% baseline) |
| #2 | Month-to-month contract | +36pp (42.7% vs 6.8%) |
| #3 | Electronic check payment | +28pp (45.3% vs 17.1%) |
| #4 | Fiber optic service | +27pp (41.9% vs 14.5%) |
| — | Service add-ons (naive) | −0.2pp → **causal paradox** |

---

## Phase 2: Causal Validation

**Scripts:** `Phase_2_Causal_Validation/proper_causal_inference.py`, `full_dataset_causal_validation.py`, `bayesian_analysis_engine.py`

### Variable Role Classification

Before running any causal model, every variable must be classified relative to the treatment (service add-on adoption):

| Variable | Causal Role | Valid Control? | Reason |
|----------|-------------|----------------|--------|
| `SeniorCitizen` | Exogenous confounder | ✅ Yes | Predates service; not a customer choice |
| `Dependents` | Exogenous confounder | ✅ Yes | Family structure predates signup |
| `Partner` | Exogenous confounder | ✅ Yes | Largely exogenous at signup |
| `Gender` | Exogenous confounder | ✅ Yes | Not a customer choice |
| `tenure` | **Collider** | ❌ No | Caused by *both* add-ons AND churn (survivorship bias) |
| `Contract` | Other treatment | ❌ No | Endogenous customer choice |
| `PaymentMethod` | Other treatment | ❌ No | Endogenous customer choice |
| `MonthlyCharges` | **Mediator** | ❌ No | On causal path: add-ons → charges → churn |
| `TotalCharges` | Downstream mediator | ❌ No | Downstream of add-ons and tenure |

### Bayesian Model (PyMC)

```python
import pymc as pm
import arviz as az

with pm.Model() as corrected_model:
    # Exogenous confounders only — satisfies backdoor criterion
    beta_senior     = pm.Normal("beta_senior",     mu=0, sigma=1)
    beta_dependents = pm.Normal("beta_dependents", mu=0, sigma=1)
    beta_partner    = pm.Normal("beta_partner",    mu=0, sigma=1)
    beta_addon      = pm.Normal("beta_addon",      mu=0, sigma=1)
    alpha           = pm.Normal("alpha",           mu=0, sigma=2)

    logit_p = (alpha
               + beta_senior     * df["SeniorCitizen"]
               + beta_dependents * df["Dependents"]
               + beta_partner    * df["Partner"]
               + beta_addon      * df["HasAddOn"])

    p   = pm.Deterministic("p", pm.math.sigmoid(logit_p))
    obs = pm.Bernoulli("obs", p=p, observed=df["Churn"])

    # 4 chains for robust convergence diagnostics
    trace = pm.sample(2000, tune=1000, chains=4,
                      target_accept=0.95, return_inferencedata=True)

# Convergence: R-hat ≈ 1.0, ESS > 1,000 for all parameters
az.plot_trace(trace)
print(az.summary(trace))
```

**Corrected estimate:** Add-on bundle reduces churn by **−5.8pp** (posterior mean). 95% CI: [−8.2%, −3.4%]. P(reduces churn by ≥5%) = **87%**. The naive −0.2pp was entirely artefactual — driven by conditioning on the collider `tenure`.

---

## Phase 3: Experimental Design

**Scripts:** `Phase_3_Experimental_Design/power_analysis_experiments.py`, `experiment_randomization.py`, `monte_carlo_simulation.py`, `sample_size_calculator.py`

### Three Prioritised Bayesian Tests

| Test | Segment | Observed Baseline | Arms | Sample | Duration |
|------|---------|------------------|------|--------|----------|
| **1 — Early Intervention** ⭐⭐⭐ | Customers ≤ 40 days | 74.7% churn | 3 + control | 100/arm | 6–8 weeks |
| **2 — Contract + Add-on Bundle** ⭐⭐ | Month-to-month | ~62% churn | 2×2 factorial | 150/arm | 12 weeks |
| **3 — Targeted Messaging** ⭐ | Senior citizens / No-dependents | ~55% churn | 2 + control | 200/arm | 8 weeks |

All three tests share unified stopping rules (see Phase 4). Segment baselines are **observed churn rates** from the dataset, not ML model scores.

### Monte Carlo Power Analysis

```bash
python Phase_3_Experimental_Design/power_analysis_experiments.py
```

Runs 1,000 simulated experiments per test per sample size, reporting the proportion of simulations where `P(churn_reduction > 8pp) > 0.95`. Produces:

- `power_curve.png` — power by N per arm
- `sample_size_sensitivity.png` — sensitivity to assumed effect size
- `power_comparison.png` — Bayesian vs Frequentist comparison

**Target:** 95% Bayesian power to detect ≥8pp churn reduction.

### Stratified Block Randomisation

```bash
python Phase_3_Experimental_Design/experiment_randomization.py
```

Allocates customers to arms while balancing on risk tier (`Churn_Rate` quintiles) and tenure cohort. Outputs assignment CSV ready for CRM import.

---

## Phase 4: Implementation & Monitoring

**Scripts:** `Phase_4_implementation_and_Monitoring/`

### Bayesian A/B Test Engine (`bayesian_ab_test_implementation.py`)

Full hierarchical model with risk-tier varying intercepts and treatment varying slopes:

```python
with pm.Model() as model:
    # Hyperpriors over baseline churn
    baseline_alpha = pm.Gamma('baseline_alpha', alpha=7, beta=10)
    baseline_beta  = pm.Gamma('baseline_beta',  alpha=3, beta=10)
    mu_baseline    = pm.Beta('mu_baseline', alpha=baseline_alpha,
                              beta=baseline_beta)

    # Informed treatment priors (from design spec)
    # T1 (Welcome Call): Beta(2,9)  — expected ~18% reduction
    # T2 (Smart Start):  Beta(2,12) — expected ~14% reduction
    # T3 (Concierge):    Beta(1,9)  — expected ~10% reduction

    # Risk-tier varying intercepts + treatment varying slopes
    sigma_tier      = pm.HalfNormal('sigma_tier',      sigma=0.15)
    sigma_treatment = pm.HalfNormal('sigma_treatment', sigma=0.15)

    trace = pm.sample(2000, tune=1000, chains=4,
                      target_accept=0.95, return_inferencedata=True)

# Decision analysis (revenue_per_month = $74.44)
results = model.decision_analysis(min_effect=0.08, revenue_per_month=74.44)
```

### Sequential Bayesian Monitor (`bayesian_monitoring_system.py`)

Week-by-week stopping rules applied at each interim look:

| Rule | Threshold | Interpretation |
|------|-----------|----------------|
| **Superiority** | P(reduction > 8pp) > **0.95** | Declare winner, stop early |
| **Futility** | P(any arm helps) < **0.05** | Stop for futility |
| **Equivalence (ROPE)** | P(\|diff\| < 2pp) > **0.80** | Treatments are practically equivalent |

Thompson Sampling adaptive allocation activates from **Week 5** — increasing traffic to better-performing arms.

**Week 6 Result:** Treatment 2 (Smart Start $125) declared winner:
- 99% confidence · +18.8pp churn reduction · 95% CI [11.0%, 26.5%]
- $82K projected annual profit · 700% ROI · 1.7-month payback

### Interactive Dashboard (`streamlit_dashboard.py`)

```bash
streamlit run Phase_4_implementation_and_Monitoring/streamlit_dashboard.py
```

Features: Real-time posterior distributions, ROPE visualisation, preset selectors for all 3 approved tests, automated decision memos, weekly executive summaries.

---

## Phase 5: Cloud Deployment

**Scripts:** `Phase_5_Depolyment guide/`

**Live demo:** https://bayesian-dashboard-128505233033.us-central1.run.app

### Architecture

Streamlit app → Docker container → Google Cloud Run (serverless, auto-scaling)

```bash
# Deploy to GCP Cloud Run
bash "Phase_5_Depolyment guide/deploy_to_cloud_run.sh"
```

### Local Docker

```bash
# Build image
docker build -t churn-dashboard "Phase_5_Depolyment guide/"

# Run locally
docker run -p 8080:8080 churn-dashboard
# Access at http://localhost:8080
```

---

## Installation & Quickstart

### Prerequisites

- Python 3.11+
- Java 11+ (required for PySpark and H2O)
- Docker (for Phase 5 deployment)

### Setup

```bash
# Clone repository
git clone https://github.com/ellaNdalla/customer-churn-causal-analysis.git
cd customer-churn-causal-analysis

# Create virtual environment
python -m venv venv
source venv/bin/activate        # macOS/Linux
# venv\Scripts\activate         # Windows

# Install dependencies
pip install --upgrade pip
pip install -r "Phase_5_Depolyment guide/requirements.txt"
```

> **Note:** H2O requires Java 11. macOS: `brew install openjdk@11`. Ubuntu: `sudo apt install openjdk-11-jdk`.

---

## Reproducing Results

Run in order to reproduce the full pipeline:

```bash
# ── Phase 1: ML Analysis ──────────────────────────────────────────────────────
python Phase_1_ML_Analysis/Decision_Tress_analysis.py     # EDA + PySpark Decision Tree
python Phase_1_ML_Analysis/AutoML_h20_Prediction.py       # H2O AutoML + MLflow
python Phase_1_ML_Analysis/Recommendation.py              # Recommendation scores

# ── Phase 2: Causal Validation ────────────────────────────────────────────────
python Phase_2_Causal_Validation/proper_causal_inference.py        # Primary causal model
python Phase_2_Causal_Validation/full_dataset_causal_validation.py # Bayesian validation

# ── Phase 3: Experimental Design ──────────────────────────────────────────────
python Phase_3_Experimental_Design/power_analysis_experiments.py   # Power analysis
python Phase_3_Experimental_Design/experiment_randomization.py     # Randomisation plan
python Phase_3_Experimental_Design/monte_carlo_simulation.py       # 1,000-iter simulation

# ── Phase 4: Monitoring (Bayesian A/B) ────────────────────────────────────────
python Phase_4_implementation_and_Monitoring/bayesian_ab_test_implementation.py
python Phase_4_implementation_and_Monitoring/bayesian_monitoring_system.py
streamlit run Phase_4_implementation_and_Monitoring/streamlit_dashboard.py

# ── Phase 5: Deploy ───────────────────────────────────────────────────────────
bash "Phase_5_Depolyment guide/deploy_to_cloud_run.sh"
```

---

## Business Recommendations

Based on corrected causal estimates, validated experiment results, and conservative revenue projections:

**1. Deploy Smart Start Package to all new customers immediately**
Treatment 2 was declared winner at Week 6 with 99% confidence and +18.8pp churn reduction. Net ROI 700%, payback period 1.7 months. Extend to all new customer onboarding.

**2. Prioritise the first 40 days**
The early tenure window is the highest-leverage intervention point in the portfolio. Customers in this window churn at 74.7% (observed). Test 1 targets this segment with Welcome Bundle, Smart Start, and Concierge Onboarding options.

**3. Migrate month-to-month customers to annual contracts**
Month-to-month customers represent 99.9% of the customer base and churn at 3× the rate of contract subscribers. Even modest migration (10%) generates material LTV uplift. Test 2 quantifies the combined contract + add-on bundle effect.

**4. Invest in add-on bundles based on causal evidence**
The naive −0.2pp add-on effect masked a true causal −5.8pp effect once collider bias was removed. Device Protection, Online Security, and Tech Support bundles have genuine churn-reducing properties — promotion is justified on causal grounds.

---

## Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Data Ingestion** | PySpark 3.x | Distributed CSV processing |
| **Data Transformation** | Spark SQL, Pandas, NumPy | Feature engineering, type casting, imputation |
| **ML — Baseline** | PySpark MLlib (Decision Tree) | Interpretable baseline model |
| **ML — Production** | H2O AutoML, Sparkling Water | Stacked ensemble (GBM + XGBoost + GLM) |
| **Class Balancing** | SMOTE (imbalanced-learn) | Address 26.5% positive class |
| **Experiment Tracking** | MLflow | Run logging, artifact storage, model registry |
| **Causal Inference** | PyMC 5, ArviZ | Bayesian logistic regression, NUTS sampler, 4 chains |
| **Power Analysis** | NumPy, SciPy, Matplotlib | Monte Carlo simulation (1,000 iterations) |
| **Experiment Design** | Custom Python | Stratified block randomisation, factorial assignment |
| **Dashboards** | Streamlit, Plotly | Interactive Bayesian monitoring, stakeholder reporting |
| **Containerisation** | Docker | Reproducible, portable environment |
| **Deployment** | Google Cloud Run, GCP | Serverless auto-scaling production serving |

---

## Design Documents

| Document | Location | Description |
|----------|----------|-------------|
| `Bayesian_Experimental_Design_Final.md` | `Design_documents/` | Authoritative methodology spec — segment baselines, stopping rules, priors, decision framework |
| `bayesian_ab_test_design.md` | `Design_documents/` | Original test design notes |
| `Customer_Churn_Final.pptx` | Root | 17-slide executive presentation covering all 5 phases |

---

## License

MIT License. See [LICENSE](LICENSE) for details.

---

## Acknowledgements

- Dataset: [Telco Customer Churn](https://www.kaggle.com/datasets/blastchar/telco-customer-churn) — Kaggle
- Causal inference foundations: *Causal Inference: The Mixtape* (Cunningham), *The Book of Why* (Pearl & Mackenzie)
- Bayesian methodology: *Statistical Rethinking* (McElreath), PyMC development team, ArviZ contributors

---



**Ella Ndalla** ·  Data Scientist
[ndallaella@gmail.com](mailto:ndallaella@gmail.com)

*Built with Python, PyMC, H2O, PySpark, and rigorous causal thinking.*

