# Quick Start — Portfolio Project with Full Dataset
## Version 2: Google GBS&O Aligned | Causal Inference Corrected

---

## What's New in Version 2

| Change | Original | Updated | Why |
|--------|----------|---------|-----|
| Causal framework | Controlled for tenure, contract, payment | Corrected: tenure is a COLLIDER — only control exogenous variables | Eliminates collider and post-treatment bias |
| Experiment design | 2×2×2 factorial, 100/cell, no holdout | 120/cell + 200 global holdout = 1,160 total | BH multiple comparisons correction + Google experimentation standard |
| Pre-registration | Not included | Required before enrollment begins | Compliance-grade analytics; prevents p-hacking |
| Business framing | A/B test / retention project | Controlled policy experiment / customer risk management | Aligns to Policy, Risk & Compliance role language |
| SQL layer | Not included | Add churn_risk_pipeline.sql to repo | Addresses SQL requirement for Google-level roles |
| DiD framework | Not included | Added as alternative causal method | Shows full causal inference toolkit |

---

## Full Dataset: Key Findings (7,042 Customers)

| Finding | Previous (1,521 subset) | NEW (7,042 full) | What This Means |
|---------|------------------------|------------------|-----------------|
| Early Tenure Churn | +10.4% | **+37.7%** | 4x STRONGER — #1 priority |
| Overall Churn Rate | 71.5% | 26.5% | Much more realistic baseline |
| Add-ons Effect | -0.2% (no signal) | -5.4% (signal present) | Validated — but causal status requires experiment |
| E-Check Payment | 73% of customers | 45.3% churn rate | Clear quick-win opportunity |
| Senior Citizens | +1.3% | +18.1% | Now significant — worth targeting |
| No Dependents | +1.8% | +15.8% | Now significant — worth targeting |

**The single strongest finding**: Customers in their first 40 days churn at 60.9% vs 23.2% baseline. A 38pp penalty. This is the centerpiece of the portfolio.

---

## Your Complete Portfolio Package

### Run These First

**1. `Scripts/full_dataset_causal_validation.py`** ⭐ START HERE
- Validates findings with all 7,042 customers
- Tests early tenure, add-ons, and payment effects
- Run time: ~3 minutes
- Output: `churn_drivers_ranked.png`, `causal_validation_summary.csv`

**2. `Scripts/proper_causal_inference.py`** ⭐ RUN SECOND
- Demonstrates the collider bias correction
- Shows add-on effect reversal when stratified by tenure
- Estimates effects using only valid exogenous confounders (age, dependents)
- This is the differentiating section of the portfolio

### Supporting Files

**3. `UPDATED_Bayesian_Test_Design.md`** (this repo)
- Complete v2 test framework with holdout group and BH correction
- All 3 phases + quick wins with expected ROI

**4. `GOOGLE_BIZOPS_TEST_DESIGN.md`** (this repo)
- Standalone testing document written in Google GBS&O language
- Policy experiment framing, CUPED, DiD framework, pre-registration

**5. `churn_risk_pipeline.sql`** (add to repo — see Section below)
- SQL pipeline from CRM to model-ready features
- Addresses SQL requirement for data science roles

---

## Execution Plan

### Step 1: Run the Scripts (2–3 hours)

```bash
# Install dependencies
pip install -r requirements.txt

# Run causal validation first
python Scripts/full_dataset_causal_validation.py

# Run corrected causal inference
python Scripts/proper_causal_inference.py
```

**Expected output from full_dataset_causal_validation.py**:
```
FINDINGS (Full Dataset, N=7,042):
1. Early Tenure (≤40 days): 60.9% vs 23.2% = +37.7% churn
2. Electronic Check: 45.3% vs 16.7% = +28.6% churn
3. Month-to-Month: 42.7% vs 2.8% (two-year) = +39.9% churn

CAUSAL ESTIMATES (exogenous confounders only):
- Early tenure: +35.3% (95% CI: [32.1%, 38.5%]) — approximately causal
- Add-ons: ~-3% to -5% — suggestive, experiment required for proof
- E-check: not identified observationally — experiment required
```

**Expected output from proper_causal_inference.py**:
```
COLLIDER BIAS DEMONSTRATION:
- All customers: add-ons effect = -5.4%
- 0–3 month customers: add-ons effect = -5.0% (consistent)
- 12+ month customers: add-ons effect = +1.0% (REVERSED)
→ Reversal confirms tenure is a collider. Original controls were wrong.

CORRECTED APPROACH:
- Valid confounders: SeniorCitizen, Dependents, Partner
- Invalid controls removed: tenure, contract, payment, charges
- Residual confounding acknowledged; experiment proposed as solution
```

---

### Step 2: Explore the Python Data Pipeline (30 min)

The production-ready data pipeline is already built into `Scripts/full_dataset_causal_validation.py` as the `ChurnDataPipeline` class. Review it to understand the architecture — it mirrors BigQuery/dbt CTE patterns and is the piece that signals production readiness for data science roles.

**Architecture overview** (5 CTE-style static methods):

```python
# Scripts/full_dataset_causal_validation.py — ChurnDataPipeline class

class ChurnDataPipeline:
    """
    Production-style data pipeline structured as composable CTE stages.
    Production analog: BigQuery CTEs orchestrated via dbt or Dataform.
    """
    def __init__(self, filepath: str):
        raw = pd.read_csv(filepath, index_col=0)
        self.df = self._run_pipeline(raw)

    @staticmethod
    def _customer_base(df):
        """
        CTE 1 — Exogenous demographics only (valid confounders).
        Production: dim_customer table. Includes ONLY pre-treatment variables
        (SeniorCitizen, Dependents, Partner). Gender excluded — no causal role.
        """

    @staticmethod
    def _subscription_features(df):
        """
        CTE 2 — Endogenous subscription choices (treatments, not controls).
        Production: fact_subscription JOIN fact_addon_enrollment.
        Contract type = treatment variable. MonthlyCharges = mediator — flagged.
        """

    @staticmethod
    def _payment_features(df):
        """
        CTE 3 — Endogenous payment choice (treatment, not control).
        Production: fact_payment, most recent snapshot per customer.
        """

    @staticmethod
    def _churn_labels(df):
        """
        CTE 4 — Ground truth label + ML model scores.
        Production: fact_churn_event + Vertex AI model predictions joined here.
        """

    @staticmethod
    def _risk_tiers(merged):
        """
        CTE 5 — Risk taxonomy: CRITICAL / ELEVATED / STANDARD.
        Production: materialised as customer_risk_scores in BigQuery for Looker BI.
        """
```

**How to use the pipeline in your own scripts**:

```python
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'Scripts'))

from full_dataset_causal_validation import ChurnDataPipeline

# Load and transform in one call
pipeline = ChurnDataPipeline('Results/churn_prediction.csv')
df = pipeline.data   # fully feature-engineered DataFrame

# Risk tier counts — mirrors a BigQuery GROUP BY query
print(df['risk_tier'].value_counts())
# STANDARD    4318
# ELEVATED    2100
# CRITICAL     624

# Filter to CRITICAL customers for targeted intervention
critical = df[df['risk_tier'] == 'CRITICAL']
print(f"CRITICAL pool: {len(critical)} customers, "
      f"{critical['Actual_Churn'].mean():.1%} churn rate")
```

**What to highlight in your GitHub README** (add to the pipeline section):

```
## Data Pipeline: ChurnDataPipeline

Production-style ETL pipeline structured as five composable CTE stages
(customer_base → subscription_features → payment_features →
churn_labels → risk_tiers), mirroring BigQuery/dbt patterns.

Key design decision: exogenous confounders (SeniorCitizen, Dependents,
Partner) are isolated in CTE 1 and propagated as the only valid controls
through all downstream causal models. Endogenous variables (contract,
payment, charges) are loaded in later CTEs and treated as treatments
or mediators — never as confounders.

Production analog: BigQuery CTEs → dbt models → Vertex AI feature store
→ customer_risk_scores table → Looker BI dashboard.
```

---

### Step 3: Update GitHub README (1 hour)

Add these three sections to your README:

**Section 1 — Project framing** (replace generic description):
```
## Customer Risk & Retention Analysis
End-to-end data science lifecycle: CRM data pipeline → ML churn prediction →
Bayesian causal inference → controlled policy experiment design →
executive recommendation with $372K projected annual impact.

Key skills demonstrated: causal inference (collider bias identification,
propensity score weighting), Bayesian sequential experimentation,
factorial experimental design, data pipeline engineering, executive communication.
```

**Section 2 — Causal inference correction** (new — this is your differentiator):
```
## Causal Inference: What I Got Wrong and Fixed

Initial analysis incorrectly treated tenure, contract type, and payment method
as confounders. I identified that:
- **Tenure is a collider** — caused by both add-on adoption AND churn.
  Controlling for it induces survivorship bias.
- **Contract and payment are other treatments** — endogenous customer choices
  that require causal treatment, not statistical control.

Evidence: the add-on effect reverses from -5.4% to +1.0% when stratified
by long-tenure customers — a textbook collider signature.

Corrected approach: control only for exogenous demographics (age, dependents).
Residual confounding acknowledged. Randomized experiment proposed as the
definitive causal test.
```

**Section 3 — Experiment design** (summarize the 2×2×2):
```
## Experimental Design: 2×2×2 Factorial Policy Experiment

To establish causal effects free of selection bias, I designed a randomized
2×2×2 factorial experiment with:
- Factor A: Add-on bundle offer (none vs. free 30-day trial)
- Factor B: Contract offer (month-to-month vs. 1-year + 10% discount)
- Factor C: Payment incentive (e-check vs. $10 autopay credit)

8 conditions × 120 customers each = 960 experiment + 200 global holdout = 1,160 total.
Benjamini-Hochberg correction applied for multiple comparisons.
Pre-registered before enrollment. Bayesian hierarchical model with
sequential stopping rules.
```

---

### Step 4: Practice the Pitch (1 hour)

**The Google BizOps narrative arc**:
1. **Problem** (30s): "26.5% churn — $1.9M annual revenue at risk. No clear cause."
2. **Discovery** (45s): "First-40-day customers churn at 61% — 38pp above baseline. Strongest signal in the dataset."
3. **Complication** (60s): "My initial causal model was wrong. I was conditioning on tenure — a collider. The add-on effect reversed when I stratified by tenure. Classic bias signature."
4. **Correction** (45s): "Corrected by removing endogenous controls. Observational estimates now labeled 'suggestive.' Designed a randomized experiment as the definitive test."
5. **Strategy** (60s): "Two immediate policy changes ($120K/year, no experiment needed). Three experimental phases for the remaining $252K. All with pre-registration, holdout group, and Bayesian sequential monitoring."
6. **Impact** (30s): "$372K projected annual value. 700% ROI on early tenure intervention alone."

---

## Key Numbers (Memorize These)

**Dataset**
- 7,042 total customers | 26.5% overall churn | $64.76 avg monthly revenue

**Risk Tiers**
- CRITICAL (≤40d tenure): 60.9% churn → 624 customers
- ELEVATED (MTM, no autopay): 38–45% churn → ~2,100 customers
- STANDARD (2yr contract or autopay): <15% churn → ~4,000 customers

**Effect Sizes**
- Early tenure: +37.7pp | E-check: +28.6pp | Contract gradient: 43% → 11% → 3%
- Add-ons (corrected): ~-3% to -5% (experiment required for causal proof)

**Business Impact**
- Quick Wins: $120K/year (Months 1–2)
- Phase 1 (onboarding): $82K/year | 700% ROI
- Phase 2 (factorial): $93K/year | 179% ROI
- Phase 3 (segments): $130K/year
- **Total: $425K/year**

---

## Traffic Light Priorities

### 🔴 Do This Weekend
1. Run `Scripts/full_dataset_causal_validation.py` — screenshot the output
2. Run `Scripts/proper_causal_inference.py` — review collider demo
3. Update GitHub README with the three new sections above
4. Review `ChurnDataPipeline` class in `full_dataset_causal_validation.py` — understand the 5 CTE stages and production analogs in the docstrings
5. Practice the 6-step pitch — time it at under 5 minutes

### 🟡 Do Next Week
1. Add `GOOGLE_BIZOPS_TEST_DESIGN.md` to repo (already in this project folder)
2. Write LinkedIn post: "I Found Collider Bias in My Own Analysis" (most engaging framing)
3. Apply to 5–10 target roles with GitHub link
4. Create or update slide deck — use Problem→Discovery→Complication→Correction→Strategy→Impact arc

### 🟢 Nice to Have
1. Add a CUPED variance reduction note to the experiment design
2. Record 5-minute Loom video walkthrough
3. Write Medium post expanding on the collider bias story
4. Add unit tests to causal inference scripts
5. Create Jupyter notebook version for interactive exploration

---

## Interview Talking Points (Updated)

**"Tell me about a time you solved an ambiguous problem"**
> "A telecom operator gave me one sentence: figure out why customers are churning. No metric, no hypothesis, no scope. I structured it as a risk taxonomy problem first — classifying 7,042 customers into critical, elevated, and standard risk tiers based on observable signals. That framing drove every subsequent analytical and strategic decision."

**"How did you handle confounding?"**
> "This is actually where the most interesting methodological work happened. I initially controlled for tenure, contract type, and payment method — standard practice. But I realized tenure is a collider: it's caused by both add-on adoption and churn, so conditioning on it opens a spurious association rather than closing one. The evidence was in the data: the add-on effect reversed among long-tenure customers — a textbook collider signature. I removed the invalid controls, acknowledged residual confounding, and designed a randomized experiment as the only clean solution."

**"Why Bayesian instead of frequentist?"**
> "Three reasons specific to this context. First, sequential testing: I wanted to check results weekly and stop early when confident, without inflating Type I error — Bayesian posteriors update naturally. Second, interpretability: stakeholders understand '87% confident this works' much better than 'p=0.04.' Third, prior incorporation: strong baseline rates from the observational data (42.7% MTM churn) tighten the experiment's estimates, reducing the required sample size."

**"What would you do differently in production?"**
> "I'd add real-time posterior updates through an automated pipeline — each week's data flows in, the model updates, and alerts fire if a stopping criterion is met. I'd use CUPED (Controlled-experiment Using Pre-Experiment Data) to reduce variance with the pre-experiment churn rate as a covariate — Google's experimentation teams use this routinely. And I'd maintain the holdout group for 12 months, not just 90 days, to catch effect decay."

---

## Success Checklist

**Before You Apply**
- [ ] Both causal scripts run cleanly end-to-end
- [ ] GitHub README has causal correction section
- [ ] `ChurnDataPipeline` class reviewed — can explain 5 CTE stages and production analogs
- [ ] 5-minute pitch practiced and timed
- [ ] 4 interview talking points prepared
- [ ] Business impact quantified ($372–425K/year)

**When You're Ready**
- [ ] LinkedIn post published
- [ ] Applied to 5–10 companies with GitHub link
- [ ] BLUF executive memo prepared (one-pager from roadmap)
- [ ] Slide deck updated with v2 narrative arc

---

*Version 2 — Updated from original to reflect: causal inference correction, Google GBS&O role alignment, holdout group, BH correction, pre-registration, Python ChurnDataPipeline class (replacing SQL template), and revised pitch narrative.*
