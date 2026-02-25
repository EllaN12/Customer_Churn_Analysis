# Customer Risk Mitigation: Controlled Policy Experiment Design
## Google GBS&O Data Science — Portfolio Alignment Document

> **Framing note**: This document presents the experimental design using the language and standards of a Google Global Business Strategy & Operations (GBS&O) Data Science team. Churn is reframed as *customer risk*. Interventions are framed as *policies*. The experimental framework mirrors Google's internal experimentation standards: pre-registration, global holdout, Bayesian sequential analysis, and retrospective causal validation.

---

## 1. Business Problem Statement

**The ambiguous challenge (as received)**: A telecom operator's leadership identified elevated customer cancellations as a strategic concern but lacked clarity on which customers, why, or what interventions would be most effective.

**Reframed as a risk problem**: 26.5% of 7,042 customers cancel annually, representing ~$1.9M in annual revenue at risk. Three distinct risk cohorts are identifiable from CRM data, each requiring a different policy response. Without intervention, the operator will continue to over-invest in low-risk customers and under-invest in high-risk ones.

**Analytical mandate**: Establish the *causal* effect of three candidate policies — add-on service bundling, contract migration, and payment method incentives — on customer churn risk, using a randomized experiment free of the selection bias present in observational comparisons.

---

## 2. Customer Risk Taxonomy

Before designing any experiment, the customer base is segmented into three risk tiers. This drives enrollment prioritization and ensures interventions target the right populations.

| Risk Tier | Definition | N | Churn Rate | Revenue at Risk/Month |
|-----------|------------|---|------------|----------------------|
| **CRITICAL** | Tenure ≤40 days | 624 (8.9%) | 60.9% | ~$19,000 |
| **ELEVATED** | MTM contract, e-check, no add-ons | ~2,100 (29.8%) | 38–45% | ~$52,000 |
| **STANDARD** | Two-year contract or autopay | ~4,318 (61.3%) | <15% | Low |

**Basis for risk classification**: Derived from observational analysis of `results/churn_prediction.csv` (N=7,042). Causal status of each factor is assessed separately (see Section 4).

---

## 3. Causal Framework: What We Can and Cannot Claim

This section is critical for analytical credibility. Not all observed associations support causal policy recommendations.

### 3.1 Valid Causal Estimates (Observational)

These factors are exogenous — not customer choices — so observational estimates are approximately causal:

| Factor | Effect | Basis |
|--------|--------|-------|
| Early tenure (≤40d) | +37.7pp churn increase | Exogenous: all customers start at tenure=0 |
| Senior citizen | +18.1pp churn increase | Exogenous: age is not a telecom choice |
| No dependents | +15.8pp churn increase | Mostly exogenous: family structure predates telecom |

### 3.2 Not Causally Identified (Observational) — Experiment Required

These factors are endogenous customer choices. Observational comparisons are biased by unobserved loyalty and satisfaction:

| Factor | Naive Association | Problem | Resolution |
|--------|------------------|---------|------------|
| Contract type | MTM 42.7% vs 2yr 2.8% churn | Customers choosing long contracts are already more loyal | Randomized contract offer (Phase 2, Factor B) |
| Payment method | E-check 45.3% vs autopay 16.7% | Payment-careful customers may also be more committed | Randomized payment incentive (Phase 2, Factor C) |
| Add-on services | No add-ons 29.8% vs with add-ons 24.4% | Tenure is a collider — see Section 3.3 | Randomized add-on offer (Phase 2, Factor A) |

### 3.3 The Collider Problem (Key Methodological Finding)

The initial analysis controlled for tenure in causal models for add-ons. This is wrong. **Tenure is a collider**: it is caused by both add-on adoption (add-ons may retain customers longer) and churn (customers who churned have low tenure by definition). Conditioning on a collider opens a spurious association between add-ons and churn.

**Empirical evidence**:

| Subgroup | Add-ons Effect |
|----------|---------------|
| All customers | -5.4pp (add-ons appear to help) |
| 0–3 month customers | -5.0pp (consistent) |
| 12+ month customers | **+1.0pp (REVERSED)** |

The reversal at long tenure is a collider bias signature: 12-month customers *without* add-ons are unusually loyal (they survived without help), inflating the no-add-on group's apparent performance. The effect is not real heterogeneity.

**Corrected approach**: Control only for exogenous pre-treatment variables (age, dependents, partner). Observational add-on estimate: ~-3% to -5%, labeled "suggestive." Definitive causal estimate comes from the randomized experiment.

---

## 4. Experimental Design

### 4.1 Pre-Registration (Required Before Enrollment)

Pre-registration is standard practice for compliance-grade analytics. It prevents p-hacking, provides an audit trail, and is expected for policy-influencing experiments.

**Submit to**: OSF (osf.io/registries) or internal experiment management system before first customer is enrolled.

**Document before enrollment**:
- Primary outcome: 90-day churn rate per condition
- Secondary outcomes: contract adoption rate (14d), payment switch rate (30d), add-on retention (30d post-trial)
- Primary comparison: Full bundle (Condition 8) vs. pure control (Condition 1)
- Secondary comparisons: each main effect vs. control; all two-way interactions
- Stopping rules (pre-specified — see Section 4.5)
- Subgroup analyses: Fiber vs. DSL; senior vs. non-senior
- Intent-to-treat as primary analysis; per-protocol as sensitivity check

---

### 4.2 Core Design: 2×2×2 Factorial Policy Experiment

**Target population**: Month-to-month customers, ≥3 months tenure, not already under a long-term contract or using autopay.
**Available pool**: ~3,270 customers

**Why factorial?** Three separate A/B tests would require 3× the sample and miss interaction effects (e.g., are add-ons more effective when bundled with a contract offer?). The factorial design estimates 7 effects — 3 main, 3 two-way, 1 three-way — in a single experiment.

| Factor | Control (0) | Treatment (1) | Policy Question |
|--------|------------|---------------|-----------------|
| **A: Add-ons** | No add-on offer | Free 30-day bundle trial (4 protective services) | Do add-ons causally reduce churn, free of selection bias? |
| **B: Contract** | Month-to-month (status quo) | 1-year contract offer + 10% discount | Does contract commitment causally reduce churn? |
| **C: Payment** | Electronic check (status quo) | $10 bill credit for switching to autopay | Does payment friction causally drive churn? |

**The 8 Policy Conditions**:

| # | A | B | C | Label | Expected Churn |
|---|---|---|---|-------|----------------|
| 1 | 0 | 0 | 0 | Pure control | ~42.7% |
| 2 | 1 | 0 | 0 | Add-ons only | ~37–38% |
| 3 | 0 | 1 | 0 | Contract only | ~11–15% |
| 4 | 0 | 0 | 1 | Payment only | ~22–25% |
| 5 | 1 | 1 | 0 | Add-ons + Contract | ~9–13% |
| 6 | 1 | 0 | 1 | Add-ons + Payment | ~20–23% |
| 7 | 0 | 1 | 1 | Contract + Payment | ~7–11% |
| 8 | 1 | 1 | 1 | Full bundle | ~5–9% |

---

### 4.3 Sample Size and Power

**Multiple comparisons correction**: With 7 effect estimates, a Benjamini-Hochberg (BH) correction at q=0.10 reduces the effective alpha per test. Increasing from 100 to **120 per cell** restores target power.

| Effect | Target Power | n=100 (uncorrected) | n=100 (BH adjusted) | n=120 (BH adjusted) |
|--------|-------------|--------------------|--------------------|---------------------|
| Main effect A | 90% | 90% | ~84% | ~90% |
| Main effect B | >99% | >99% | >98% | >99% |
| Main effect C | 90% | 90% | ~84% | ~90% |
| Two-way AB, AC, BC | 80% | 80% | ~72% | ~80% |
| Three-way ABC | 70% | 68% | ~60% | ~68% |

**Final sample sizes**:
- 120 per cell × 8 conditions = **960 experiment participants**
- 200 **global holdout** (excluded from all experiments) = **1,160 total**
- Duration: 8–10 weeks at ~116 new eligible enrollments per week

**CUPED variance reduction** (optional enhancement): Use pre-experiment churn probability score from `Results/churn_prediction.csv` as a covariate. CUPED (Controlled-experiment Using Pre-Experiment Data) can reduce variance by 30–50%, effectively increasing power without additional participants.

---

### 4.4 Global Holdout Group

**Definition**: 200 customers randomly selected from the eligible pool *before* any experiment enrollment begins. These customers receive no interventions for the duration of all experiments.

**Purpose**:
1. Validate that simultaneous experiments do not contaminate each other
2. Measure long-run churn trajectory without any treatment (12-month baseline)
3. Provide a clean retrospective comparison at 6 and 12 months post-experiment

**Holdout selection**: Random sample stratified by internet service type (Fiber/DSL) and tenure bucket (3–6 months, 6–12 months, 12+ months). Locked before any other randomization.

---

### 4.5 Randomization Protocol

1. Select and lock holdout group (200 customers) — document in pre-registration
2. Stratify remaining pool by internet service type (Fiber vs. DSL)
3. Within each stratum, randomly assign customers 1:1:1:1:1:1:1:1 to 8 conditions
4. Assignment is fixed at enrollment — no re-randomization
5. Condition assignment is blinded to customer service representatives delivering interventions

**Stratification rationale**: Fiber customers churn at 41.9% vs. DSL at 19.0%. Without stratification, imbalanced Fiber/DSL proportions across conditions could confound treatment effect estimates.

---

### 4.6 Bayesian Analysis Plan

**Model**: Bayesian hierarchical logistic regression

```python
with pm.Model() as factorial_model:
    # Informed prior from observational data
    baseline = pm.Beta('baseline', alpha=43, beta=57)   # 42.7% observed MTM churn

    # Main effects — weakly informative on logit scale
    alpha_A = pm.Normal('addon_main',    mu=0,    sigma=0.10)
    alpha_B = pm.Normal('contract_main', mu=-0.50, sigma=0.10)  # informed by data
    alpha_C = pm.Normal('payment_main',  mu=-0.20, sigma=0.10)

    # Interaction effects — tighter prior (expected smaller than main effects)
    alpha_AB  = pm.Normal('AB_interaction',  mu=0, sigma=0.05)
    alpha_AC  = pm.Normal('AC_interaction',  mu=0, sigma=0.05)
    alpha_BC  = pm.Normal('BC_interaction',  mu=0, sigma=0.05)
    alpha_ABC = pm.Normal('ABC_interaction', mu=0, sigma=0.03)

    logit_p = (
        pm.math.logit(baseline)
        + alpha_A  * A[i]
        + alpha_B  * B[i]
        + alpha_C  * C[i]
        + alpha_AB * A[i] * B[i]
        + alpha_AC * A[i] * C[i]
        + alpha_BC * B[i] * C[i]
        + alpha_ABC * A[i] * B[i] * C[i]
    )
    p_churn = pm.math.invlogit(logit_p)
    churn_obs = pm.Bernoulli('churn', p=p_churn, observed=data)

    # MCMC: 4 chains, 2000 draws, 1000 tuning steps, target_accept=0.95
    trace = pm.sample(2000, tune=1000, chains=4, target_accept=0.95)
```

**Prior sensitivity analysis**: Run the model with vague priors (sigma=0.5) and compare posteriors. If estimates converge, prior choice is validated. Document in final report.

---

### 4.7 Pre-specified Decision Rules

**These rules are locked in pre-registration before any data is collected.**

| Decision | Criterion | Action |
|----------|-----------|--------|
| Declare main effect winner | P(reduction > 10pp \| data) > 0.90 | Roll out winning policy to all eligible customers |
| Early stop — success | P(reduction > 15pp \| data) > 0.95 at any weekly check | Stop enrollment; implement immediately |
| Early stop — futility | P(reduction > 5pp \| data) < 0.10 by week 5 | Abandon arm; redirect budget |
| Interaction present | P(\|interaction\| > 5pp) > 0.80 | Report interaction; do not combine effects additively |
| Declare no interaction | P(\|interaction\| < 3pp) > 0.90 | Report effects as approximately additive |

**Weekly monitoring cadence**: Posterior update every Monday. Stopping rules evaluated by experiment analyst. Decision memo issued to stakeholders if any stopping criterion is met.

---

## 5. Alternative Causal Methods Considered

| Method | Applicable Here? | Why Considered | Decision |
|--------|-----------------|----------------|----------|
| **Randomized Controlled Trial** | ✅ Yes — final design | Gold standard; eliminates all selection bias | **SELECTED** |
| **Difference-in-Differences (DiD)** | Conditionally | If historical data shows a regional policy rollout (e.g., autopay incentive launched in one region before others), DiD identifies causal effect using region × time variation | **Propose as supplement** if geographic variation exists in historical data |
| **Propensity Score Weighting** | Limited | Valid for exogenous confounders only (age, dependents). Cannot handle endogenous choices (contract, payment) | **Used for observational estimates only** |
| **Instrumental Variables (IV)** | Possibly | If marketing team randomly varied which customers received add-on promotions, that randomization is a valid instrument | **Flag for future work** if promotion data is available |
| **Regression Discontinuity (RD)** | Conditionally | If contract renewal is triggered at a sharp tenure threshold (e.g., exactly 12 months), RD exploits the threshold for identification | **Assess viability** with contract renewal data |

**Recommended addition for portfolio**: Add a DiD sketch showing the identification strategy if a regional pricing experiment existed. Even as a proposed framework, this signals awareness of the full causal toolkit.

---

## 6. Phases and Timeline

| Phase | Activity | Duration | N | Expected Annual Value |
|-------|----------|----------|---|----------------------|
| Pre-experiment | Pre-registration; holdout selection; randomization list | 2 weeks | — | — |
| Quick Win 1 | Autopay incentive campaign (no experiment) | Months 1–2 | ~1,869 eligible | $67K |
| Quick Win 2 | Two-year contract renewal protection | Months 1–2 | Ongoing | $53K |
| Phase 1 | Early tenure 4-arm RCT | Months 3–10 | 400 | $82K |
| Phase 2 | 2×2×2 factorial experiment | Months 3–6 | 960 + 200 holdout | $93K (contract arm) |
| Phase 3A | Senior citizen retention program | Months 9–11 | 400 | $45K |
| Phase 3B | Fiber optic retention program | Months 9–11 | 600 | $85K |
| Retrospective | Holdout comparison; causal validation | Month 12 | Holdout group | Confirms $425K total |

---

## 7. Implementation and Measurement Framework

### 7.1 Post-Experiment Rollout Decision Memo (BLUF Format)

Every experiment concludes with a BLUF memo to senior stakeholders:

```
BOTTOM LINE: [Winning condition] reduced 90-day churn by [X]pp
(95% credible interval: [Y, Z]pp). Recommend full rollout to [N]
eligible customers. Expected annual net value: $[X]K.

FINDINGS:
• [Main effect result with credible interval]
• [Interaction finding if any]
• [Subgroup finding if any]

RISKS:
• [Effect decay risk — holdout comparison schedule]
• [Compliance or cost risk]

NEXT STEPS: [Owner] to implement by [date]. [Metric] tracked weekly
in BI dashboard. Retrospective at 6 months.
```

### 7.2 Ongoing BI Monitoring Metrics

| Metric | Frequency | Alert Threshold | Owner |
|--------|-----------|-----------------|-------|
| Churn rate by risk tier | Weekly | CRITICAL tier > 65% | Risk Analytics |
| Autopay adoption (QW1) | Weekly | < 25% adoption rate | Growth Operations |
| Contract upgrade adoption | Weekly | < 10% adoption rate | Retention Policy |
| Holdout vs. rollout delta | Monthly | Delta < 10pp (effect decaying) | Causal Inference |
| Revenue at risk (CRITICAL cohort) | Monthly | > $25K/month | Finance Operations |

### 7.3 12-Month Retrospective Analysis

At 12 months post-experiment:
1. Compare holdout churn rate to rollout churn rate — validates that effects are sustained
2. Re-estimate causal model on full post-experiment data — test whether effect sizes match predictions
3. Update risk tier thresholds if baseline rates have shifted
4. Publish internal findings memo; update BI dashboard with validated effect sizes

---

## 8. Expected Impact Summary

| Policy | Population | Effect | Annual Value |
|--------|-----------|--------|-------------|
| Autopay incentive | ~1,869 e-check users | -28.6pp churn (45.3% → 16.7%) | $67K net |
| Contract renewal protection | 2yr customers at expiration | Prevents 42.7% churn regression | $53K net |
| Early tenure onboarding (T2) | ≤40d customers | -25pp churn (60.9% → 35.9%) | $82K net |
| Contract migration (factorial B) | MTM customers | -31pp churn (42.7% → 11.3%) | $93K net |
| Senior citizen program | 1,142 seniors | -12pp churn (41.7% → 29.7%) | $45K net |
| Fiber retention (price lock) | 3,096 fiber customers | -15pp churn (41.9% → 26.9%) | $85K net |
| **Total** | | | **$425K/year** |

---

## 9. Technical Stack

| Component | Portfolio Implementation | Production Analog |
|-----------|------------------------|-------------------|
| Data pipeline | `ChurnDataPipeline` class in `Scripts/full_dataset_causal_validation.py` (5 CTE-style static methods) | BigQuery + dbt models |
| ML prediction | `Scripts/AutoML_Prediction.py` + MLflow | Vertex AI + Vertex Experiments |
| Causal inference | `Scripts/proper_causal_inference.py` (PyMC) | Cloud Run or Vertex AI Custom |
| Experiment analysis | `Scripts/full_dataset_causal_validation.py` (`FullDatasetCausalAnalysis` class) | Internal A/B framework |
| BI dashboard | Streamlit decision-support tool | Looker + Looker ML |
| Experiment tracking | MLflow (local, `Scripts/mlruns/`) | Vertex AI Experiments |
| Pre-registration | OSF or equivalent | Internal experiment registry |

**ChurnDataPipeline — CTE Stage Summary**:

| CTE Stage | Method | Variables Loaded | Causal Role |
|-----------|--------|-----------------|-------------|
| 1 — Customer base | `_customer_base()` | SeniorCitizen, Dependents, Partner | Exogenous confounders — valid controls |
| 2 — Subscription features | `_subscription_features()` | Contract, InternetService, MonthlyCharges, add-on count | Treatments + mediator — not controls |
| 3 — Payment features | `_payment_features()` | PaymentMethod, is_autopay | Treatment — not control |
| 4 — Churn labels | `_churn_labels()` | Actual_Churn, Predicted_Churn, churn probability | Outcome + ML score |
| 5 — Risk tiers | `_risk_tiers()` | risk_tier (CRITICAL / ELEVATED / STANDARD) | Derived feature for targeting |

This architecture enforces the causal separation in code: exogenous confounders are loaded first and explicitly marked as valid controls; endogenous variables are loaded in later stages and flagged as treatments or mediators. Any downstream model that accidentally uses a CTE-2 or CTE-3 variable as a control is identifiable by code review.

---

*This document is written for a Google GBS&O Data Science portfolio. It uses policy experiment framing, BLUF communication, and Google-standard experimentation practices (holdout groups, pre-registration, CUPED, multiple comparisons correction) to demonstrate readiness for a role in Policy, Risk, and Compliance analytics. The data pipeline uses a Python-native `ChurnDataPipeline` class structured as composable CTE stages — the production analog of BigQuery + dbt.*
