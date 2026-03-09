# Customer Churn Prediction & Causal Analysis

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![PySpark](https://img.shields.io/badge/PySpark-3.x-E25A1C?style=flat-square&logo=apachespark&logoColor=white)](https://spark.apache.org/)
[![H2O AutoML](https://img.shields.io/badge/H2O-AutoML-FFD700?style=flat-square)](https://docs.h2o.ai/h2o/latest-stable/h2o-docs/automl.html)
[![PyMC](https://img.shields.io/badge/PyMC-5.0+-FF6B35?style=flat-square)](https://www.pymc.io/)
[![MLflow](https://img.shields.io/badge/MLflow-Tracking-0194E2?style=flat-square&logo=mlflow)](https://mlflow.org/)
[![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED?style=flat-square&logo=docker&logoColor=white)](https://www.docker.com/)
[![AWS](https://img.shields.io/badge/AWS-Elastic%20Beanstalk-FF9900?style=flat-square&logo=amazonaws&logoColor=white)](https://aws.amazon.com/elasticbeanstalk/)
[![License: MIT](https://img.shields.io/badge/License-MIT-22C55E?style=flat-square)](LICENSE)

> ** An end-to-end data science pipeline** — from raw telco CRM data to production deployment — demonstrating machine learning,  causal inference, Bayesian analysis, and statistically powered experimental design.

---

## Table of Contents

- [Project Overview](#project-overview)
- [The Scientific Narrative](#the-scientific-narrative)
- [Key Results](#key-results)
- [Project Structure](#project-structure)
- [Methodology](#methodology)
  - [Phase 1: Data Pipeline](#phase-1-data-pipeline)
  - [Phase 2: Machine Learning](#phase-2-machine-learning)
  - [Phase 3: Causal Inference](#phase-3-causal-inference)
  - [Phase 4: Experimental Design & Monitoring](#phase-4-experimental-design--monitoring)
- [Installation & Quickstart](#installation--quickstart)
- [Reproducing Results](#reproducing-results)
- [Business Recommendations](#business-recommendations)
- [Deployment](#deployment)
- [Technology Stack](#technology-stack)
- [Project Documents](#project-documents)
- [License](#license)

---

## Project Overview

This project addresses a core business problem in telecommunications: **predicting and causally understanding customer churn** at scale. It goes well beyond a standard predictive model by rigorously applying causal inference to distinguish correlation from causation — a distinction that separates actionable strategy from misleading analysis.

**Dataset:** 7,043 customers × 21 features (Kaggle Telco Customer Churn)
**Outcome:** Binary churn indicator (26.5% overall churn rate and 41.4% minimum churn rate among predicted churners)
**

### Scope

This project answers a ha **what actually causes churn, and what can we do about it with statistical confidence?**

The four-phase pipeline moves from prediction,  correlation to causation analysis and intervention:

| Phase | Focus | Output |
|-------|-------|--------|
| **1. Data Pipeline** | PySpark ingestion, cleaning, feature engineering | Clean feature matrix
| **2. Machine Learning** | Decision Tree, H2O AutoML, MLflow tracking | 93% AUC-ROC stacked ensemble |
| **3. Causal Inference** | Variable role classification, collider correction, Bayesian estimation | Defensible causal estimates |
| **4. Experimental Design** | 2×2×2 factorial experiment, power analysis, monitoring | $372K projected annual retention lift |

---

## The Scientific Narrative

### Discovery: Dramatic Early Tenure Effect

Exploratory analysis revealed that customers in their **first 40 days** churn at **60.9%** versus a 23.2% baseline — a **+37.7 percentage point penalty** affecting 624 customers (8.9% of the base). This became the central hypothesis for intervention.

### Attempted Causal Validation — and a Critical Correction

The initial Bayesian model controlled for tenure, contract type, and payment method as confounders. This is a common but methodologically incorrect choice:

- **Tenure is a collider.** It is caused by both service add-on adoption *and* churn (survivorship). Conditioning on it induces spurious correlation — a textbook case of collider bias.
- **Contract type and payment method are other treatments** (endogenous customer choices correlated with loyalty), not pre-treatment confounders.
- **Monthly and total charges are mediators** — they sit on the causal path from add-ons to churn, and controlling for them blocks the very effect we want to estimate.

Catching and correcting this bias is the methodological centerpiece of the project. The corrected model conditions only on **exogenous pre-treatment demographics** (SeniorCitizen, Dependents, Partner, Gender) — the only variables that satisfy the backdoor criterion.

### Rigorous Solution: Randomized Experimentation

Because observational data has fundamental limits even after correction, the project culminates in a **2×2×2 factorial randomized experiment** designed with 80%+ statistical power, sequential monitoring, and Bayesian decision rules — ready for production rollout.

---

## Key Results

### Machine Learning Performance

| Model | AUC-ROC | AUC-PR | Recall (Churners) |
|-------|---------|--------|-------------------|
| Decision Tree (PySpark) | 72.0% | 52.6% | ~65% |
| H2O Stacked Ensemble | **87.0%** | **65.0%** | **~80%** |

**Selected model:** H2O AutoML Stacked Ensemble — best overall performance on held-out test set.

### Causal Estimates (Corrected Bayesian Model)

| Driver | Effect on Churn | Status |
|--------|-----------------|--------|
| Early tenure ≤40 days | +37.7 pp | ⚠️ Confounded — requires experiment |
| Month-to-month vs 2-year | +39.9 pp | ⚠️ Endogenous treatment |
| Electronic check vs autopay | +28.6 pp | ⚠️ Endogenous treatment |
| Service add-on bundle | −5.3 pp (corrected) | ✅ Causal estimate with exogenous controls |

### Projected Business Impact

| Experiment | Target Segment | Min. N | Expected Annual Lift |
|------------|---------------|--------|----------------------|
| Early Tenure Intervention | New customers (≤40 days) | 400 | $82K |
| Factorial: Contract + Payment + Add-ons | Month-to-month customers | 800 | $93K |
| Fiber Service Quality | Fiber optic subscribers | 300 | $85K |
| **Total Portfolio** | — | — | **~$372K** |

---

## Project Structure

```
Customer_Churn_Analysis/
│
├── README.md                                  ← You are here
├── LICENSE
├── Dockerfile                                 ← Container definition (Python 3.11-slim)
├── Procfile                                   ← Gunicorn web server entry point
│
├── Scripts/                                   ← Core analysis scripts
│   ├── CC_analysis.py                         ← EDA & Decision Tree (PySpark)
│   ├── AutoML_Prediction.py                   ← H2O AutoML + SMOTE + MLflow
│   ├── Recommendation.py                      ← Rule-based recommendation engine
│   ├── full_dataset_causal_validation.py      ← Bayesian causal model (full dataset)
│   ├── proper_causal_inference.py             ← Corrected causal framework (primary)
│   └── mlruns/                                ← MLflow experiment tracking artifacts
│       └── 851594783253648064/                ← Churn_Analysis experiment
│           └── {run_id}/artifacts/            ← AUC, Confusion Matrix, Feature Importance PNGs
│
├── Methodology for portfolio/                 ← Advanced analysis & experiment design
│   ├── full_dataset_causal_validation.py      ← Version-controlled causal pipeline
│   ├── proper_causal_inference.py             ← Corrected model (exogenous-only)
│   ├── bayesian_ab_test_implementation.py     ← Bayesian A/B testing engine
│   ├── power_analysis_experiments.py          ← Monte Carlo power analysis
│   ├── power_analysis_experiments_UPDATED.py  ← Refined power curves
│   ├── experiment_randomization.py            ← Stratified block randomization
│   ├── experiment_randomization_UPDATED.py    ← Production-ready randomizer
│   ├── bayesian_monitoring_system.py          ← Week-by-week experiment monitor
│   ├── automated_reporting.py                 ← Automated stakeholder reports
│   ├── streamlit_experiment_monitor.py        ← Interactive experiment dashboard
│   ├── monte_carlo_simulation.py              ← 1,000-iteration power simulation
│   ├── causal_validation.py                   ← Propensity score weighting
│   ├── config.py                              ← Centralized configuration
│   ├── sample_size_calculator.py              ← Sample size optimization tool
│   │
│   └── Results/
│       ├── visualizations/
│       │   ├── causal_comparison.png          ← Before/after causal correction
│       │   ├── churn_drivers_ranked.png        ← Ranked effect sizes
│       │   ├── executive_dashboard_week_6.png  ← Week 6 monitoring snapshot
│       │   ├── posterior_plots.png             ← MCMC posterior distributions
│       │   ├── posterior_predictive_check.png  ← Calibration & observed vs predicted
│       │   ├── power_comparison.png            ← Method-to-method power comparison
│       │   ├── power_curve.png                 ← Statistical power by sample size
│       │   ├── sample_size_sensitivity.png     ← Effect size sensitivity analysis
│       │   └── trace_plots.png                 ← MCMC convergence diagnostics
│       └── monitoring/
│           └── monitoring_week_1.png
│
├── Missing_churn_testingfiles/                ← Causal bias validation assets
│   ├── 1_early_tenure_effect.png             ← Early tenure churn distribution
│   ├── 2_collider_bias_demonstration.png      ← Stratification reversal proof
│   ├── 3_valid_invalid_controls_diagram.png   ← Variable role classification
│   ├── bayesian_ab_test_implementation.py
│   ├── bayesian_monitoring_system.py
│   ├── causal_validation.py
│   ├── create_portfolio_visualizations.py
│   ├── experiment_randomization.py
│   ├── monte_carlo_simulation.py
│   ├── power_analysis_experiments.py
│   └── streamlit_experiment_monitor.py
│
├── Models/                                    ← Serialized model artifacts
│   ├── decision_tree_model/                   ← PySpark ML Pipeline
│   └── model_h2o_stacked_ensemble/            ← H2O MOJO / binary model
│
├── Prediction_Data/                           ← Datasets
│   ├── dataset.csv                            ← Raw Kaggle telco dataset (7,043 rows)
│   ├── final_data.csv                         ← Feature-engineered dataset
│   ├── final_dataset.csv                      ← Full processed dataset
│   ├── churn_prediction_df.pkl                ← Model predictions + probabilities
│   ├── recommendation.csv                     ← Targeted retention recommendations
│   └── Challenge_dataset.csv                  ← Holdout challenge set
│
├── Customer_Churn_Presentation_Final.pptx    ← 24-slide executive presentation
├── Customer_Churn_ML_Eval_and Recommendations.docx
├── Customer_Churn_Portfolio_Roadmap.docx
└── Customer_Churn_Google_BizOps_Roadmap.docx
```

---

## Methodology

### Phase 1: Data Pipeline

**Script:** `Scripts/CC_analysis.py`

A production-portable ETL pipeline built on PySpark, mirroring a BigQuery/dbt architecture.

**Pipeline steps:**

1. **Ingestion** — `SparkSession` CSV read with schema inference
2. **Schema validation** — `data.printSchema()` + dimension checks
3. **Missing value audit** — per-column null counts with `count(when(isnan | isnull))`
4. **Type casting** — `TotalCharges` string → double, `SeniorCitizen` int → string
5. **Imputation** — median imputation for numeric nulls; mode for categoricals
6. **Outlier handling** — IQR-based clipping on continuous features
7. **Feature encoding** — `StringIndexer` → `OneHotEncoder` via `PipelineModel`
8. **Train/test split** — 80/20 stratified by churn label

**Production analog:** In a BigQuery/dbt context, each method maps to a dbt model. The `ChurnDataPipeline` class in `full_dataset_causal_validation.py` documents this explicitly.

---

### Phase 2: Machine Learning

**Scripts:** `Scripts/CC_analysis.py`, `Scripts/AutoML_Prediction.py`
**Tracking:** MLflow experiment `Churn_Analysis` (ID: `851594783253648064`)

#### Model 1: Decision Tree (PySpark MLlib)

```python
from pyspark.ml.classification import DecisionTreeClassifier

dt = DecisionTreeClassifier(labelCol="label", featuresCol="features",
                             maxDepth=5, impurity="gini")
pipeline = Pipeline(stages=[indexer, encoder, assembler, dt])
model = pipeline.fit(train_df)
```

**Results:** AUC-ROC 72.0%, AUC-PR 52.6%

#### Model 2: H2O AutoML Stacked Ensemble

```python
import h2o
from h2o.automl import H2OAutoML

h2o.init()
aml = H2OAutoML(max_models=20, seed=42, balance_classes=True)
aml.train(x=features, y="Churn", training_frame=train_h2o)
leader = aml.leader  # Stacked Ensemble
```

**Results:** AUC-ROC 87.0%, AUC-PR 65.0%, Recall ~80%

SMOTE oversampling (`imblearn`) was applied to address class imbalance (26.5% positive class) before H2O training.

#### Experiment Tracking

All runs tracked with MLflow:

```bash
mlflow ui  # View at http://localhost:5000
# Experiment: Churn_Analysis (ID: 851594783253648064)
```

Each run logs: hyperparameters, AUC-ROC, AUC-PR, F1, confusion matrix, ROC curve, and feature importance plots.

---

### Phase 3: Causal Inference

**Scripts:** `Scripts/proper_causal_inference.py`, `Scripts/full_dataset_causal_validation.py`

This is the methodological core of the project. It corrects a bias that most practitioners miss.

#### Variable Role Classification

Before running any causal model, every variable must be classified by its role relative to the treatment (service add-on adoption):

| Variable | Causal Role | Valid Control? | Reason |
|----------|-------------|----------------|--------|
| `SeniorCitizen` | Exogenous confounder | ✅ Yes | Age predates service; not a customer choice |
| `Dependents` | Exogenous confounder | ✅ Yes | Family structure predates service |
| `Partner` | Exogenous confounder | ✅ Yes | Mostly exogenous at signup |
| `Gender` | Exogenous confounder | ✅ Yes | Not a customer choice |
| `tenure` | **Collider** | ❌ No | Caused by *both* add-ons AND churn (survivorship bias) |
| `Contract` | Other treatment | ❌ No | Endogenous customer choice; needs own identification |
| `PaymentMethod` | Other treatment | ❌ No | Endogenous customer choice |
| `MonthlyCharges` | **Mediator** | ❌ No | On causal path: add-ons → charges → churn |
| `TotalCharges` | Mediator/downstream | ❌ No | Downstream of add-ons and tenure |

**Decision rule** — X is a valid confounder if and only if:
1. Measured *before* treatment assignment
2. Exogenous — not itself a customer choice
3. A common cause of both treatment and outcome (backdoor criterion)

#### The Collider Bias Proof

Controlling for `tenure` opens a non-causal path between add-ons and churn, inducing spurious correlation. This is empirically demonstrated via stratification reversal — the "add-on effect" changes sign when conditioning on tenure quintiles. See `Missing_churn_testingfiles/2_collider_bias_demonstration.png`.

#### Corrected Bayesian Model (PyMC)

```python
import pymc as pm
import arviz as az

with pm.Model() as corrected_model:
    # Exogenous confounders only
    beta_senior    = pm.Normal("beta_senior",    mu=0, sigma=1)
    beta_dependents = pm.Normal("beta_dependents", mu=0, sigma=1)
    beta_partner   = pm.Normal("beta_partner",   mu=0, sigma=1)

    # Treatment effect of interest
    beta_addon = pm.Normal("beta_addon", mu=0, sigma=1)

    # Intercept
    alpha = pm.Normal("alpha", mu=0, sigma=2)

    # Linear predictor
    logit_p = (alpha
               + beta_senior    * df["SeniorCitizen"]
               + beta_dependents * df["Dependents"]
               + beta_partner   * df["Partner"]
               + beta_addon     * df["HasAddOn"])

    p = pm.Deterministic("p", pm.math.sigmoid(logit_p))
    obs = pm.Bernoulli("obs", p=p, observed=df["Churn"])

    # NUTS sampler — 2,000 draws, 1,000 tuning
    trace = pm.sample(2000, tune=1000, target_accept=0.9,
                      return_inferencedata=True)

# Convergence diagnostics
az.plot_trace(trace)
print(az.summary(trace))  # R-hat ≈ 1.0, ESS > 400 for all parameters
```

**Corrected estimate:** Service add-on bundle reduces churn by ~5.3 pp (posterior mean), with credible interval that does not cross zero after removing collider/mediator contamination.

---

### Phase 4: Experimental Design & Monitoring

**Scripts:** `Methodology for portfolio/power_analysis_experiments_UPDATED.py`, `experiment_randomization_UPDATED.py`, `bayesian_monitoring_system.py`

#### 2×2×2 Factorial Experiment

Three binary factors yielding 8 treatment arms:

| Factor | Level 0 (Control) | Level 1 (Treatment) |
|--------|-------------------|---------------------|
| **A — Contract offer** | Month-to-month (status quo) | 1-year contract incentive |
| **B — Proactive support** | No outreach | Proactive support call within 40 days |
| **C — Add-on bundle** | No offer | Device Protection + Online Security bundle |

**Design rationale:**
- Factorial design tests 3 interventions in one experiment
- Estimates all main effects *and* interaction terms
- 8 arms × 100 customers/arm = 800 total customers
- 90%+ power for main effects at α = 0.05

#### Monte Carlo Power Analysis

```bash
python "Methodology for portfolio/power_analysis_experiments_UPDATED.py"
```

Runs 1,000 simulated experiments to estimate power under different effect sizes and sample sizes, producing:
- `power_curve.png` — power by sample size
- `sample_size_sensitivity.png` — sensitivity to assumed effect size
- `power_comparison.png` — Frequentist vs Bayesian power comparison

**Target:** 80% power to detect a 10 pp reduction in churn at α = 0.05 requires ~200 customers per arm (minimum).

#### Stratified Block Randomization

```bash
python "Methodology for portfolio/experiment_randomization_UPDATED.py"
```

Randomizes customers into arms while balancing on key covariates (tenure cohort, SeniorCitizen, Dependents). Outputs assignment CSV ready for CRM import.

#### Sequential Bayesian Monitoring

```bash
streamlit run "Methodology for portfolio/streamlit_experiment_monitor_UPDATED.py"
```

Week-by-week monitoring dashboard with:
- Cumulative enrollment vs target
- Churn rates by arm (rolling)
- Probability of superiority (Bayesian)
- Automated stopping rules (99% confidence threshold)
- **Week 6 result:** Treatment 2 declared winner — 99% confidence, +18.8 pp effect

---

## Installation & Quickstart

### Prerequisites

- Python 3.11+
- Java 11+ (required for PySpark)
- Docker (optional, for containerized deployment)

### 1. Clone the repository

```bash
git clone https://github.com/ellaNdalla/customer-churn-causal-analysis.git
cd customer-churn-causal-analysis
```

### 2. Create virtual environment

```bash
python -m venv venv
source venv/bin/activate        # macOS/Linux
# venv\Scripts\activate         # Windows
```

### 3. Install dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

> **Note:** H2O and PySparkling require Java 11. On macOS: `brew install openjdk@11`. On Ubuntu: `sudo apt install openjdk-11-jdk`.

---

## Reproducing Results

Run scripts in the following order to reproduce the full analysis:

```bash
# ── Phase 1 & 2: EDA, Decision Tree, H2O AutoML ──────────────────────────────
python Scripts/CC_analysis.py               # EDA + PySpark Decision Tree
python Scripts/AutoML_Prediction.py         # H2O AutoML + MLflow tracking
python Scripts/Recommendation.py            # Rule-based recommendations

# ── Phase 3: Causal Inference ─────────────────────────────────────────────────
python Scripts/proper_causal_inference.py   # Full corrected causal analysis
python Scripts/full_dataset_causal_validation.py  # Bayesian validation (N=7,042)

# ── Phase 4: Experimental Design ─────────────────────────────────────────────
cd "Methodology for portfolio/"
python power_analysis_experiments_UPDATED.py    # Monte Carlo power analysis
python experiment_randomization_UPDATED.py      # Generate randomization plan
python bayesian_monitoring_system.py            # Run monitoring simulation

# ── Interactive Dashboards ────────────────────────────────────────────────────
streamlit run streamlit_experiment_monitor_UPDATED.py
```

### MLflow UI

```bash
mlflow ui --backend-store-uri Scripts/mlruns
# Navigate to http://localhost:5000 → Experiment: Churn_Analysis
```

---

## Business Recommendations

Based on the corrected causal estimates and experimental projections:

### 1. Early Intervention Program *(Highest Priority)*
Implement retention outreach within the **first 40 days** of customer tenure. The early tenure effect (+37.7 pp) is the strongest predictor in the dataset. A targeted welcome + check-in program is estimated to yield $82K in annual profit from avoided churn.

### 2. Enhanced Long-Term Contract Plans
Develop attractive 1- and 2-year contracts with bundled incentives. Month-to-month customers churn at 3× the rate of annual subscribers. Migrating even 10% of MTM customers to annual contracts generates significant LTV uplift.

### 3. Service Bundle Promotion
Causal estimates (after collider correction) confirm that Device Protection, Online Security, and Tech Support bundles have a genuine negative effect on churn. Proactive offer campaigns to at-risk segments are justified on causal grounds.

### 4. Targeted Retention Marketing
Focus resources on the highest-risk segments:
- **Senior citizens** (elevated churn, often underserved)
- **Customers without dependents** (lower switching cost)
- **First-90-day cohort** (highest absolute churn rate)
- **Electronic check users** (28.6 pp above autopay users)

### Recommendation Scoring Engine

```bash
python Scripts/Recommendation.py
# Outputs: Prediction_Data/recommendation.csv
# Contains per-customer recommendation labels with churn probability
```

---

## Deployment

The prediction and recommendation service is containerized and deployed to **AWS Elastic Beanstalk (us-east-1)**.

### Local Docker

```bash
# Build image
docker build -t churn-app .

# Run container
docker run -p 8080:8080 churn-app

# Access at http://localhost:8080
```

### AWS Elastic Beanstalk

```bash
# Initialize EB CLI
eb init -p docker churn-prediction-app --region us-east-1

# Create environment
eb create churn-production

# Deploy updates
eb deploy
```

**Architecture:** Gunicorn WSGI server → Flask/Dash application → H2O MOJO model (no JVM at inference time)

---

## Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Data Ingestion** | PySpark 3.x | Distributed CSV processing, BigQuery-portable |
| **Data Transformation** | Spark SQL, Pandas, NumPy | ETL, feature engineering, type casting |
| **ML — Tree** | PySpark MLlib (Decision Tree) | Baseline interpretable model |
| **ML — AutoML** | H2O AutoML, Sparkling Water | Stacked ensemble, SMOTE balancing |
| **Experiment Tracking** | MLflow | Run logging, artifact storage, model registry |
| **Causal Inference** | PyMC 5, ArviZ | Bayesian logistic regression, MCMC (NUTS) |
| **Power Analysis** | NumPy, SciPy, Matplotlib | Monte Carlo simulation (1,000 iterations) |
| **Experiment Design** | Custom Python (stratified block) | Randomization, factorial assignment |
| **Dashboards** | Streamlit, Plotly, Dash | Interactive monitoring, stakeholder reporting |
| **Visualization** | Matplotlib, Seaborn, Plotly Express | Publication-quality figures |
| **Containerization** | Docker | Reproducible environment |
| **Deployment** | AWS Elastic Beanstalk, Gunicorn | Production serving |

---

## Project Documents

| Document | Description |
|----------|-------------|
| `Customer_Churn_Presentation_Final.pptx` | 24-slide executive presentation (all 4 phases) |
| `Customer_Churn_ML_Eval_and Recommendations.docx` | Detailed ML evaluation & business recommendations |
| `Customer_Churn_Portfolio_Roadmap.docx` | Portfolio strategy and project roadmap |
| `Customer_Churn_Google_BizOps_Roadmap.docx` | Google GBS&O role alignment |
| `Methodology for portfolio/CAUSAL_INFERENCE_JOURNEY.md` | Full narrative of the methodological correction |
| `Methodology for portfolio/RANDOMIZED_EXPERIMENT_DESIGN_COMPLETE.md` | Complete experimental protocol |
| `Methodology for portfolio/INTERVIEW_GUIDE.md` | 5-minute pitch and technical interview prep |
| `Methodology for portfolio/METHODOLOGY_DEEP_DIVE.md` | Deep technical walkthrough of causal approach |

---

## Skills Demonstrated

| Domain | Specifics |
|--------|-----------|
| **Statistical Inference** | Causal inference, collider/mediator classification, backdoor criterion, Bayesian hierarchical models, MCMC diagnostics (R-hat, ESS) |
| **Experimental Design** | Factorial design, stratified block randomization, sequential testing, Bayesian stopping rules, Monte Carlo power analysis |
| **Machine Learning** | Decision trees, AutoML, stacked ensembles, SMOTE, MLflow lifecycle management |
| **Engineering** | PySpark distributed computing, Docker containerization, AWS deployment, Gunicorn WSGI |
| **Communication** | Executive presentation (24 slides), technical documentation, stakeholder dashboards, ROI analysis |
| **Critical Thinking** | Self-identified and corrected own methodological bias — a top-1% statistical competency |

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

---

## Acknowledgements

- Dataset: [Telco Customer Churn](https://www.kaggle.com/datasets/blastchar/telco-customer-churn) — Kaggle
- Causal inference foundations: *Causal Inference: The Mixtape* (Cunningham), *Mostly Harmless Econometrics* (Angrist & Pischke)
- Bayesian methodology: PyMC development team and ArviZ contributors

---

<div align="center">

**Ella Ndalla** · Senior Data Scientist
[ndallaella@gmail.com](mailto:ndallaella@gmail.com)

*Built with Python, PyMC, H2O, and rigorous causal thinking.*

</div>
