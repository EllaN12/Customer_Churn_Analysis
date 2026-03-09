# Bayesian Experimental Design — Customer Churn Interventions
## Final Methodology Document

**Project:** Telco Customer Churn — Phase 3–4
**Dataset:** churn_prediction.csv — 7,042 customers, 1,869 confirmed churners
**Author:** Ella Ndalla

---

## 1. Guiding Principle: Segment-Specific Baselines

All experimental baselines are drawn from the **observed historical churn rate of the target segment**, not from either of the following (which are incorrect for this purpose):

| Source | Value | Why It Is Wrong Here |
|---|---|---|
| Full-population churn rate | 26.5% | Too dilute — mixes low-risk and high-risk customers; inflates required sample sizes and understates the signal |
| ML model mean predicted probability | 71.4% | This is a model score, not an observed outcome; produces circular reasoning |

The 26.5% full-population figure belongs in **fleet-wide ROI projections** (denominator for business impact), not in experimental power calculations or prior specification.

---

## 2. Dataset Foundation

| Metric | Value |
|---|---|
| Total customers | 7,042 |
| Total churners | 1,869 |
| Full-population churn rate | 26.5% |
| Average monthly revenue | $74.44 |
| Monthly revenue at risk | $139,131 |
| Annual revenue at risk | $1.67M |
| Month-to-month customers (churners) | 88.5% (1,655 / 1,869) |
| Electronic check customers (churners) | 57.3% (1,071 / 1,869) |

### Validated Causal Effects (Phase 2 — PyMC MCMC)

From `bayesian_analysis_engine.py` and `proper_causal_inference.py`, controlling for exogenous confounders (SeniorCitizen, Dependents, Partner, Gender):

| Factor | Naive Effect | Causal Effect | 95% Credible Interval |
|---|---|---|---|
| Add-on services (bundled) | −0.2pp | **−5.8pp** | [−8.2%, −3.4%] |
| Contract type (MTM → 1-yr) | — | **−31pp** | validated |
| AutoPay vs electronic check | — | **−20pp** | validated |

The naive add-on figure (−0.2pp) reflects confounding by tenure; the causal estimate (−5.8pp) is the figure used in all downstream experimental design and ROI calculations.

---

## 3. Segment Baselines for the Three Tests

Each test targets a distinct high-risk cohort. Baselines below are **observed historical churn rates** for those specific cohorts, extracted from the dataset.

| Test | Target Segment | Observed Segment Churn Rate |
|---|---|---|
| Test 1 — Early Tenure | Customers with tenure 0–6 months | **74.7%** |
| Test 2 — Contract + AutoPay | Month-to-month + electronic check customers | **~62%** |
| Test 3 — Service Upsell | Fiber customers with fewer than 2 add-ons | **~55%** |

---

## 4. Bayesian Decision Thresholds (All Tests)

The following thresholds apply uniformly across all three experiments, per the design specification in `BAYESIAN_TEST_DESIGN_UPDATES.md`:

| Criterion | Threshold | Previous (incorrect) Value |
|---|---|---|
| **Superiority** | P(reduction > 8pp) > **0.95** | P(>10pp) > 0.90 |
| **Minimum detectable effect** | **8 percentage points** | 10–15pp |
| **Futility** | Max P(any arm helps) < **0.05** | < 0.20 (4× too lenient) |
| **ROPE (practical equivalence)** | P(\|diff\| < 2pp) > 0.80 for all arms | Not implemented |
| **MCMC chains** | **4** | 2 |
| **Posterior samples** | 2,000 draws, 1,000 tuning, target_accept=0.95 | same |

---

## 5. Test 1 — Early Tenure Intervention ⭐⭐⭐ Highest Priority

### Rationale
The 0–6 month tenure window shows a 74.7% observed churn rate — the strongest signal in the dataset (+10.4pp above the 64.3% established-customer rate). The intervention window is time-constrained: if no action is taken within ~40 days, the onboarding opportunity closes permanently.

### Arms

| Arm | Description | Intervention Cost |
|---|---|---|
| Control | Standard onboarding | $0 |
| T1 — Welcome Bundle | Day-7 contract upgrade offer (6-mo) + free add-on trial | $75 |
| T2 — Smart Start | Days 5/15/30 proactive check-ins + tech support | $50 |
| T3 — Concierge | Contract upgrade + 2 add-ons + dedicated support (60 days) | $125 |

### Design Parameters

| Parameter | Value |
|---|---|
| Segment baseline | 74.7% (observed 0–6 month cohort) |
| Target minimum effect | 8pp reduction |
| Arms | 4 (Control + T1 + T2 + T3) |
| Sample size | 100 customers per arm (400 total) |
| Duration | 6–8 weeks |
| Stopping rule | Superiority: P(reduction > 8pp) > 0.95 OR Futility: P(any arm helps) < 0.05 (after week 6) |

### Bayesian Priors

```python
# Control: informed by segment observed baseline
control_prior  = pm.Beta('p_arm_0', alpha=7.47, beta=2.53)  # 74.7% churn

# Treatment priors: reflect expected direction of effect, not flat
t1_prior = pm.Beta('p_arm_1', alpha=2, beta=9)   # Beta(2,9) — modest reduction
t2_prior = pm.Beta('p_arm_2', alpha=2, beta=12)  # Beta(2,12) — moderate reduction
t3_prior = pm.Beta('p_arm_3', alpha=1, beta=9)   # Beta(1,9) — largest reduction
```

### Expected Outcomes

| Scenario | Churn Reduction | New Churn Rate | Revenue Saved (per 100) | Net Profit |
|---|---|---|---|---|
| Conservative | 10pp | 64.7% | $18,900 | $11,400 |
| Realistic | 15pp | 59.7% | $28,350 | $20,850 |
| Optimistic | 20pp | 54.7% | $37,800 | $30,300 |

### Power

At 100 customers/arm with a 74.7% segment baseline, detecting an 8pp reduction achieves **≥95% Bayesian power** (validated by `power_analysis_experiments.py` Monte Carlo simulation, 1,000 runs).

---

## 6. Test 2 — Contract + AutoPay ⭐⭐ High Priority

### Rationale
88.5% of churners are month-to-month customers; 57.3% use electronic check. Phase 2 causal analysis confirms a −31pp churn reduction from contract migration and a −20pp reduction from AutoPay adoption. This is the highest-leverage intervention on the largest addressable segment.

### Arms

| Arm | Contract Offer | Payment Incentive | Total Discount |
|---|---|---|---|
| Control | Status quo | None | $0 |
| T1 — Contract | 6-month at 10% discount | None | ~$47 |
| T2 — AutoPay | Status quo | AutoPay switch + bill credit | ~$25 |

### Design Parameters

| Parameter | Value |
|---|---|
| Segment baseline | ~62% (observed MTM + electronic check cohort) |
| Target minimum effect | 8pp reduction |
| Arms | 3 (Control + T1 + T2) |
| Sample size | 150 customers per arm (450 total) |
| Duration | 12 weeks |
| Stratification | Block by tenure tier (0–6 mo vs 7+ mo) and internet service (DSL vs Fiber) |
| Stopping rule | Superiority: P(reduction > 8pp) > 0.95; Futility after week 6: max P(helps) < 0.05 |

### Bayesian Priors

```python
# Control: informed by segment observed baseline (~62%)
control_prior = pm.Beta('p_arm_0', alpha=6.2, beta=3.8)

# Treatment priors
t1_prior = pm.Beta('p_arm_1', alpha=2, beta=9)   # Beta(2,9) — contract effect
t2_prior = pm.Beta('p_arm_2', alpha=2, beta=12)  # Beta(2,12) — autopay effect
```

### Key Hypothesis
The test answers definitively: **"Does bundling add-ons with a contract produce greater retention than either intervention alone?"** Phase 2 established the causal effect of each component independently; this test quantifies the combined effect in a prospective setting.

### Expected Outcomes

| Scenario | Churn Reduction | Annual Fleet Impact |
|---|---|---|
| Conservative | 8pp | ~$104K |
| Realistic | 15pp | ~$196K |
| Optimistic | 22pp | ~$287K |

---

## 7. Test 3 — Service Upsell (Fiber, <2 Add-ons) ⭐ Lower Priority

### Rationale
Fiber customers with fewer than 2 add-ons show ~55% churn. Phase 2 confirmed a −5.8pp causal effect from add-on adoption (after controlling for tenure confounding). At low intervention cost, this test has a high ROI-per-dollar even with a modest effect, and covers a large scalable segment.

### Arms

| Arm | Intervention | Cost |
|---|---|---|
| Control | No outreach | $0 |
| T1 — OnlineSecurity offer | Personalised outreach: bill clarity + security add-on | $15 |
| T2 — TechSupport offer | Personalised outreach: tech support add-on | $15 |

### Design Parameters

| Parameter | Value |
|---|---|
| Segment baseline | ~55% (observed Fiber customers, <2 add-ons) |
| Target minimum effect | 8pp reduction |
| Arms | 3 (Control + T1 + T2) |
| Sample size | 200 customers per arm (600 total) |
| Duration | 8 weeks |
| Stopping rule | Superiority: P(reduction > 8pp) > 0.95; Futility after week 6: max P(helps) < 0.05 |

### Bayesian Priors

```python
# Control: segment-specific baseline (~55%)
control_prior = pm.Beta('p_arm_0', alpha=5.5, beta=4.5)

# Treatment priors
t1_prior = pm.Beta('p_arm_1', alpha=2, beta=9)   # Beta(2,9)
t2_prior = pm.Beta('p_arm_2', alpha=2, beta=12)  # Beta(2,12)
```

### Expected Outcomes

| Scenario | Churn Reduction | Cost per Customer | Revenue Saved | ROI |
|---|---|---|---|---|
| Conservative | 5pp | $15 | $4,450 | ~197% |
| Realistic | 8pp | $15 | $7,120 | ~315% |
| Optimistic | 12pp | $15 | $10,680 | ~472% |

---

## 8. Sequential Monitoring Protocol (All Tests)

All three tests use **Bayesian sequential monitoring** implemented in `bayesian_monitoring_system.py`.

### Weekly Update Procedure

Each week:
1. Fit a Beta-Binomial model on cumulative data
2. Sample 2,000 draws across 4 chains (NUTS sampler, target_accept=0.95)
3. Verify convergence: R-hat ≈ 1.0, effective samples > 400 per parameter
4. Apply all three stopping rules below

### Stopping Rules

```python
# Rule 1 — SUPERIORITY: stop and implement winner
if P(control_churn - treatment_churn > 0.08) > 0.95:
    STOP → implement winning arm

# Rule 2 — FUTILITY: stop and abandon (checked from week 6 onward)
if max(P(any arm helps)) < 0.05:
    STOP → no treatment is effective

# Rule 3 — ROPE EQUIVALENCE: stop, all arms practically identical (checked from week 8)
if P(|control - treatment| < 0.02) > 0.80 for ALL treatment arms:
    STOP → choose cheapest option
```

### Thompson Sampling (adaptive allocation)

From week 5 onward, allocation shifts toward the arm with the highest current posterior probability of superiority. This reduces exposure to inferior arms while maintaining valid inference.

---

## 9. Decision Framework

```python
def make_decision(posterior_samples, arm_costs, min_ev=50):
    """
    Unified decision rule applied at each weekly update.
    posterior_samples: dict {arm_idx: np.array of churn probability samples}
    arm_costs: dict {arm_idx: cost per customer}
    min_ev: minimum expected net value per customer to justify implementation ($)
    """
    control = posterior_samples[0]

    for arm in range(1, n_arms):
        treatment = posterior_samples[arm]
        diff = control - treatment  # positive = treatment reduces churn

        pos = (diff > 0.08).mean()                         # P(superior by ≥8pp)
        in_rope = (np.abs(diff) < 0.02).mean()             # P(within ROPE)
        ev = (diff * 11 * 74.44 - arm_costs[arm]).mean()   # expected net value

        if pos > 0.95 and ev > min_ev:
            return "IMPLEMENT"
        elif in_rope > 0.95:
            return "ROPE_EQUIVALENT"
        elif pos > 0.80:
            return "PROMISING — continue"
        else:
            return "INSUFFICIENT EVIDENCE"
```

---

## 10. Implementation Sequence

### Weeks 1–8: Test 1 — Early Tenure
- Enroll customers entering 0–40 day window
- Weekly posterior updates; check stopping rules at weeks 4, 6, 8
- Decision memo produced at each check

### Weeks 4–12: Test 2 — Contract + AutoPay (overlapping)
- Stratified enrolment (block by tenure tier, internet type)
- Automated weekly summaries via `automated_reporting.py`

### Weeks 9–13: Test 3 — Service Upsell (after Test 1 concludes)
- Outreach to Fiber segment
- Decision by week 13

### Week 14+: Rollout
- Winning arm(s) deployed to full segment via Streamlit dashboard (`streamlit_dashboard.py`) and GCP Cloud Run
- 90-day post-launch monitoring
- Scale to remaining customer base if metrics hold

---

## 11. Business Impact Summary

All figures use the segment-specific baselines and the causal effect estimates validated in Phase 2.

| Test | Segment | Realistic Churn Reduction | Annual Profit Impact |
|---|---|---|---|
| Test 1 — Early Tenure | 0–6 month customers | 15pp | ~$216K |
| Test 2 — Contract + AutoPay | MTM + e-check customers | 15pp | ~$104K |
| Test 3 — Service Upsell | Fiber, <2 add-ons | 8pp | ~$50K |
| **Combined** | | | **~$370K (conservative)** |

Full uncertainty quantification (credible intervals, Monte Carlo sensitivity) is available in `monte_carlo_simulation.py` and the live Streamlit dashboard.

---

## 12. Code Reference

| Script | Phase | Purpose |
|---|---|---|
| `bayesian_analysis_engine.py` | Phase 2 | Causal effect estimation (PyMC logistic regression) |
| `power_analysis_experiments.py` | Phase 3 | Monte Carlo power simulation (1,000 runs per test) |
| `experiment_randomization.py` | Phase 3 | Stratified randomisation and assignment logging |
| `sample_size_calculator.py` | Phase 3 | Frequentist and Bayesian sample size formulae |
| `monte_carlo_simulation.py` | Phase 3 | ROI uncertainty simulation under varying assumptions |
| `bayesian_ab_test_implementation.py` | Phase 4 | Full PyMC hierarchical A/B test engine |
| `bayesian_monitoring_system.py` | Phase 4 | Weekly sequential monitoring and stopping rules |
| `automated_reporting.py` | Phase 4 | Weekly decision memos and executive summaries |
| `streamlit_dashboard.py` | Phase 4–5 | Interactive dashboard with live posterior and ROPE visualisation |

---

## 13. Key Methodological Decisions — Rationale Log

| Decision | Rationale |
|---|---|
| Segment baselines over population baseline | Population rate (26.5%) dilutes signal; segment rates reflect the true experimental population |
| P > 0.95 superiority threshold | Stricter than the common 90% — appropriate for deployment decisions with real per-customer cost |
| 8pp minimum effect | Smallest practically meaningful improvement that justifies intervention cost across all three test segments |
| ROPE ±2pp | Differences smaller than 2pp are not actionable at a per-customer cost of $15–$125 |
| Futility at P < 0.05 | Prevents wasting budget on experiments with negligible probability of any detectable benefit |
| Informed priors Beta(2,9) / Beta(2,12) / Beta(1,9) | Encode prior knowledge that treatments reduce churn relative to control, without being overconfident |
| 4 MCMC chains | Required for reliable R-hat convergence diagnostics; 2 chains is insufficient to detect non-convergence |
| Thompson Sampling from week 5 | Reduces customer exposure to inferior arms while maintaining valid posterior inference |
