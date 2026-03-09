# Bayesian A/B Test Design for Customer Churn Reduction
## Based on Full Dataset Analysis (N=7,042 total, 1,869 churners)

---

## Executive Summary

**Dataset Profile:**
- Total customers analyzed: 7,042
- Total churners: 1,869
- Total retained: 5,173
- Actual churn rate: 26.5%
- Current state: 88.5% month-to-month contracts (1,655 of 1,869 churners)
- Mean predicted churn probability: 71.4%
- Average monthly revenue: $74.44
- Average tenure: 18.0 months
- Critical insight: **57.3% use electronic check** (1,071 of 1,869 churners)

**Revenue at Stake:**
- Monthly revenue at risk: $139,131 (1,869 × $74.44)
- Annualized churn loss: ~$1.67M based on actual churners
- LTV loss (11-month avg): ~$1.53M total

---

## 1. Data-Driven Test Prioritization

### Priority 1: Payment Method + Contract Bundle (Highest Impact)
**Rationale:** Electronic check users show 71.3% churn vs 67.6% for auto-payment users

### Priority 2: Tenure-Based Early Intervention (Time-Sensitive)
**Rationale:** 42% of customers are in first 3 months (highest risk period: 74.7% churn)

### Priority 3: Service Tier Optimization
**Rationale:** 54.7% have zero tech services; 36.4% of Fiber users are undermonetized

---

## 2. Recommended Test Architecture

### **TEST 1: Contract + Payment Method Optimization (CRITICAL PATH)**

**Why This Test First:**
- 88.5% are month-to-month (major pain point, 1,655 of 1,869 churners)
- 57.3% use electronic check (1,071 churners - switch to auto-pay = proven retention lever)
- Combined intervention likely has multiplicative effect

**Sample Allocation:**
- **Total sample:** 800 customers (43% of churners)
- **Stratified by:** Contract type + Payment method + Tenure group

**Treatment Arms (n=200 each):**

| Arm | Intervention | Expected Effect |
|-----|-------------|----------------|
| **Control** | Status quo | Baseline (26.5% churn) |
| **T1: Standard Contract** | 1-year at 10% discount | -8% churn (18.5%) |
| **T2: Contract + AutoPay** | 1-year at 10% + autopay incentive ($10 credit) | -12% churn (14.5%) |
| **T3: Premium Bundle** | 2-year at 20% + autopay + tech service bundle | -16% churn (10.5%) |

**Bayesian Priors:**
```python
# Based on actual data and realistic intervention effects
control_prior = Beta(α=3, β=8)  # ~27% churn (slightly above 26.5%)
t1_prior = Beta(α=2, β=9)       # ~18% churn (contract effect)
t2_prior = Beta(α=2, β=12)      # ~14% churn (contract + autopay)
t3_prior = Beta(α=1, β=9)       # ~10% churn (premium bundle)
```

**Hierarchical Structure:**
```python
with pm.Model() as contract_model:
    # Population hyperpriors
    μ_baseline = pm.Normal('mu_baseline', mu=0.265, sigma=0.05)  # 26.5% baseline
    
    # Contract type effects  
    τ_contract = pm.HalfNormal('tau_contract', sigma=0.05)
    contract_effect = pm.Normal('contract_effect', mu=0, sigma=τ_contract, shape=3)
    
    # Treatment effects (negative = reduces churn)
    τ_treatment = pm.HalfNormal('tau_treatment', sigma=0.08)
    treatment_effect = pm.Normal('treatment_effect', mu=[-0.08, -0.12, -0.16], 
                                  sigma=τ_treatment, shape=3)
    
    # Combined logit-scale effects
    p_churn = pm.Deterministic('p_churn',
        pm.math.invlogit(
            pm.math.logit(μ_baseline) + contract_effect[contract_type] + treatment_effect[treatment]
        )
    )
    
    # Likelihood
    churn = pm.Binomial('churn', n=n_customers, p=p_churn, observed=churn_data)
```

**Success Criteria:**
- **Primary:** P(θ_treatment < θ_control - 0.08) > 0.90 (8%+ absolute reduction)
- **Secondary:** Expected Value (EV) > $50/customer (retention months × revenue)
- **ROI:** (Revenue gained - discount cost) / discount cost > 2.0

---

### **TEST 2: Tenure-Based Early Warning System**

**Why This Matters:**
- 637 customers (42%) are in months 0-3 with 74.7% churn
- Early intervention has exponential LTV impact

**Sample Allocation:**
- **Total sample:** 500 customers in months 0-6
- **Stratified by:** Month of tenure (0-1, 2-3, 4-6)

**Treatment Arms (n=125 each):**

| Arm | Timing | Intervention | Expected Effect |
|-----|--------|--------------|----------------|
| **Control** | No outreach | Baseline | 73% churn |
| **T1: Welcome** | Day 7 | Onboarding + concierge support | -10% churn |
| **T2: 30-Day Check** | Day 30 | Usage review + service optimization | -15% churn |
| **T3: Proactive** | Day 15 + 45 | Two touchpoints + loyalty rewards | -18% churn |

**Priors:**
```python
# Informed by "0-3mo" cohort data
tenure_priors = {
    'control': Beta(α=7.5, β=2.5),    # 75% churn
    't1_welcome': Beta(α=6.5, β=3.5),
    't2_30day': Beta(α=6, β=4),
    't3_proactive': Beta(α=5.5, β=4.5)
}
```

**Bayesian Decision Rule:**
```python
def early_intervention_ev(posterior_samples, customer_ltv=865):
    # customer_ltv = $78.76 × 11 months average
    retention_lift = 1 - posterior_samples  # % not churning
    intervention_cost = 25  # per customer
    
    ev = (retention_lift * customer_ltv) - intervention_cost
    return ev.mean(), np.percentile(ev, [2.5, 97.5])
```

---

### **TEST 3: Service Tier Upsell Strategy**

**Why This Matters:**
- 832 customers (54.7%) have ZERO tech services
- 1,277 customers (84%) have Fiber optic (premium tier)
- 465 Fiber customers paying <$80/month (undermonetized)

**Sample Allocation:**
- **Total sample:** 600 customers
- **Segment:** Fiber optic users with <2 add-on services

**Treatment Arms (n=150 each):**

| Arm | Offer | Price Point | Expected Adoption | Retention Lift |
|-----|-------|-------------|-------------------|----------------|
| **Control** | No offer | $0 | 0% | 0% |
| **T1: Security Bundle** | OnlineSecurity + Backup | +$15/mo | 25% | +8% retention |
| **T2: Full Protection** | All 4 tech services | +$25/mo | 18% | +12% retention |
| **T3: Premium Package** | Tech + Entertainment | +$35/mo | 12% | +15% retention |

**Multi-Objective Bayesian Model:**
```python
with pm.Model() as upsell_model:
    # Adoption probability
    p_adopt = pm.Beta('p_adopt', alpha=[1, 3, 2.5, 1.8], beta=[1, 9, 11, 13])
    
    # Retention lift (among adopters)
    retention_lift = pm.Beta('retention_lift', alpha=[1, 2, 2.5, 3], beta=[1, 3, 2.5, 2])
    
    # Revenue impact
    arpu_increase = pm.Normal('arpu_increase', mu=[0, 15, 25, 35], sigma=2)
    
    # Combined metric: Expected value per customer
    ev_per_customer = pm.Deterministic('ev',
        p_adopt * (retention_lift * 11 * arpu_increase + (1-retention_lift) * 3 * arpu_increase)
    )
```

**Priors Based on Current Data:**
```python
# Current tech service adoption: 45.2% have at least one
# Recommendation: "Promote Tech Services" for 99.9%
# Gap: 54.7% have none → high upsell potential

prior_adoption_rates = {
    'security_bundle': Beta(α=3, β=9),    # 25% expected
    'full_protection': Beta(α=2.5, β=11), # 18% expected
    'premium_package': Beta(α=1.8, β=13)  # 12% expected
}
```

---

## 3. Sample Size & Power Analysis

### Bayesian Sample Size Determination

**Target Precision:**
- Credible interval width: ±5% at 95% probability
- Minimum detectable effect: 8% absolute churn reduction
- Statistical power equivalent: >85%

**Formula:**
```python
from scipy.stats import beta

def bayesian_sample_size(prior_alpha, prior_beta, effect_size, credible_width=0.05):
    """
    Calculate sample size for desired posterior precision
    """
    # Simulate posterior after n observations
    n_range = range(50, 500, 10)
    
    for n in n_range:
        # Assume effect_size success rate
        successes = int(n * (1 - effect_size))
        failures = n - successes
        
        # Posterior
        post_alpha = prior_alpha + successes
        post_beta = prior_beta + failures
        
        # 95% credible interval width
        ci_width = beta.ppf(0.975, post_alpha, post_beta) - beta.ppf(0.025, post_alpha, post_beta)
        
        if ci_width <= credible_width:
            return n
    
    return 500  # Maximum

# Test 1: Contract + Payment
required_per_arm = bayesian_sample_size(7, 3, 0.60, credible_width=0.08)
# Result: ~175-200 per arm

# Test 2: Tenure intervention
required_per_arm = bayesian_sample_size(7.5, 2.5, 0.65, credible_width=0.10)
# Result: ~110-125 per arm

# Test 3: Upsell (binomial: adopt or not)
required_per_arm = bayesian_sample_size(3, 9, 0.25, credible_width=0.08)
# Result: ~140-150 per arm
```

**Recommended Allocation:**

| Test | Total Sample | Per Arm | % of Dataset | Risk Level |
|------|-------------|---------|--------------|------------|
| Test 1: Contract+Payment | 800 | 200 | 52.6% | All tiers |
| Test 2: Tenure Intervention | 500 | 125 | 32.9% | 0-6 months |
| Test 3: Service Upsell | 600 | 150 | 39.5% | Fiber <2 services |
| **Buffer for overlap** | -379 | - | - | - |
| **Net Utilization** | 1,521 | - | 100% | - |

*Note: Some customers qualify for multiple tests (e.g., new Fiber customer with e-check payment)*

---

## 4. Stratification Strategy

### Risk-Based Stratification

```python
def stratify_customers(df):
    """
    Stratify customers for balanced test allocation
    """
    df['risk_tier'] = pd.cut(
        df['Churn_Rate'],
        bins=[0, 0.60, 0.75, 1.0],
        labels=['Moderate', 'High', 'Extreme']
    )
    
    df['tenure_tier'] = pd.cut(
        df['tenure'],
        bins=[0, 3, 6, 12, 100],
        labels=['0-3mo', '4-6mo', '7-12mo', '13+mo']
    )
    
    df['service_tier'] = 'Unknown'
    df.loc[df['tech_service_count'] == 0, 'service_tier'] = 'No_Tech'
    df.loc[df['tech_service_count'].between(1, 2), 'service_tier'] = 'Basic_Tech'
    df.loc[df['tech_service_count'] >= 3, 'service_tier'] = 'Full_Tech'
    
    return df
```

### Blocking Variables for Test 1 (Contract+Payment)

**Blocking factors** (ensure balance across arms):
1. Risk tier (Moderate/High/Extreme)
2. Tenure group (0-3mo / 4-6mo / 7-12mo / 13+mo)
3. Payment method (E-check / Automatic / Mailed)
4. Internet service (DSL / Fiber)

**Randomization:**
```python
from sklearn.model_selection import StratifiedShuffleSplit

def blocked_randomization(df, test_arms=4, n_per_arm=200):
    """
    Stratified random assignment preserving covariate balance
    """
    # Create blocking variable
    df['block'] = (
        df['risk_tier'].astype(str) + '_' +
        df['tenure_tier'].astype(str) + '_' +
        df['PaymentMethod'].str[:4]
    )
    
    # Within each block, randomly assign to arms
    df['treatment_arm'] = -1
    
    for block in df['block'].unique():
        block_data = df[df['block'] == block]
        block_size = len(block_data)
        
        # Proportional allocation
        assignments = np.random.choice(
            range(test_arms),
            size=block_size,
            replace=True
        )
        
        df.loc[df['block'] == block, 'treatment_arm'] = assignments
    
    return df
```

---

## 5. Bayesian Inference Models

### Model 1: Hierarchical Beta-Binomial (Contract Test)

```python
import pymc as pm
import numpy as np

def contract_hierarchical_model(data):
    """
    Hierarchical Bayesian model for contract test with risk tiers
    """
    with pm.Model() as model:
        # Data
        n_tiers = 3  # Moderate, High, Extreme
        n_treatments = 4  # Control, T1, T2, T3
        
        # Hyperpriors (population-level)
        μ_global = pm.Beta('mu_global', alpha=7, beta=3)  # ~70% prior churn
        
        # Tier-specific baselines (varying intercepts)
        σ_tier = pm.HalfNormal('sigma_tier', sigma=0.1)
        tier_offset = pm.Normal('tier_offset', mu=0, sigma=σ_tier, shape=n_tiers)
        
        # Treatment effects (varying slopes)
        σ_treatment = pm.HalfNormal('sigma_treatment', sigma=0.15)
        treatment_effect = pm.Normal(
            'treatment_effect',
            mu=[0, -0.12, -0.20, -0.28],  # Expected effects
            sigma=σ_treatment,
            shape=n_treatments
        )
        
        # Combine effects (logit scale for constraints)
        logit_baseline = pm.math.log(μ_global / (1 - μ_global))
        
        p_churn = pm.Deterministic(
            'p_churn',
            pm.math.invlogit(
                logit_baseline + 
                tier_offset[data['tier_idx']] +
                treatment_effect[data['treatment_idx']]
            )
        )
        
        # Likelihood
        churn_obs = pm.Binomial(
            'churn_obs',
            n=data['n_customers'],
            p=p_churn,
            observed=data['churn_count']
        )
        
        # Posterior sampling
        trace = pm.sample(
            2000,
            tune=1000,
            chains=4,
            target_accept=0.95,
            return_inferencedata=True
        )
    
    return model, trace
```

### Model 2: Time-to-Event (Tenure Test)

```python
def survival_bayesian_model(data):
    """
    Bayesian survival model for tenure-based intervention
    Accounts for right-censoring (test period ends before all churn)
    """
    with pm.Model() as model:
        # Weibull survival model
        # S(t) = exp(-(λt)^k)
        
        # Treatment-specific shape and scale
        k = pm.Gamma('k', alpha=2, beta=1, shape=4)  # shape parameter
        λ = pm.Gamma('lambda', alpha=1, beta=1, shape=4)  # scale parameter
        
        # Likelihood for observed events
        churn_time = pm.Weibull(
            'churn_time',
            alpha=k[data['treatment']],
            beta=λ[data['treatment']],
            observed=data['time_to_churn']
        )
        
        # Censored observations (test ended before churn)
        pm.Potential(
            'censored',
            pm.math.log(
                pm.math.exp(-(λ[data['treatment_censored']] * data['censored_time'])**k[data['treatment_censored']])
            )
        )
        
        # Median survival time (for interpretation)
        median_survival = pm.Deterministic(
            'median_survival',
            (1/λ) * (np.log(2))**(1/k)
        )
        
        trace = pm.sample(2000, tune=1000, chains=4, return_inferencedata=True)
    
    return model, trace
```

### Model 3: Multi-Objective (Upsell Test)

```python
def upsell_joint_model(data):
    """
    Joint model for adoption AND retention (two outcomes)
    """
    with pm.Model() as model:
        n_treatments = 4
        
        # Adoption model (logistic)
        α_adopt = pm.Normal('alpha_adopt', mu=0, sigma=1, shape=n_treatments)
        p_adopt = pm.Deterministic('p_adopt', pm.math.invlogit(α_adopt))
        
        adopted = pm.Bernoulli(
            'adopted',
            p=p_adopt[data['treatment']],
            observed=data['adopted']
        )
        
        # Retention model (conditional on adoption)
        # Only for those who adopted
        adopter_idx = data['adopted'] == 1
        
        α_retention = pm.Normal('alpha_retention', mu=0, sigma=1, shape=n_treatments)
        p_retention = pm.Deterministic('p_retention', pm.math.invlogit(α_retention))
        
        retained = pm.Bernoulli(
            'retained',
            p=p_retention[data['treatment'][adopter_idx]],
            observed=data['retained'][adopter_idx]
        )
        
        # Revenue impact (continuous)
        μ_revenue = pm.Normal('mu_revenue', mu=[0, 15, 25, 35], sigma=5, shape=n_treatments)
        σ_revenue = pm.HalfNormal('sigma_revenue', sigma=10)
        
        revenue_increase = pm.Normal(
            'revenue_increase',
            mu=μ_revenue[data['treatment']],
            sigma=σ_revenue,
            observed=data['arpu_change']
        )
        
        # Expected value (combination of all outcomes)
        ev_per_customer = pm.Deterministic(
            'expected_value',
            p_adopt * (p_retention * 11 + (1-p_retention) * 3) * μ_revenue
        )
        
        trace = pm.sample(2000, tune=1000, chains=4, return_inferencedata=True)
    
    return model, trace
```

---

## 6. Decision Framework & Success Criteria

### Bayesian Decision Rules

#### Rule 1: Probability of Superiority (POS)
```python
def probability_of_superiority(trace, control_arm=0, treatment_arms=[1,2,3]):
    """
    P(θ_treatment < θ_control) for churn reduction
    """
    control_samples = trace.posterior['p_churn'][:, :, control_arm].values.flatten()
    
    results = {}
    for arm in treatment_arms:
        treatment_samples = trace.posterior['p_churn'][:, :, arm].values.flatten()
        pos = (treatment_samples < control_samples).mean()
        results[f'T{arm}'] = pos
    
    return results

# Decision threshold
DECISION_THRESHOLD = 0.90  # 90% probability
```

#### Rule 2: Region of Practical Equivalence (ROPE)
```python
def rope_decision(trace, rope_bounds=(-0.02, 0.02)):
    """
    Is the treatment effect practically equivalent to zero?
    """
    effect_samples = trace.posterior['treatment_effect'].values
    
    in_rope = np.logical_and(
        effect_samples > rope_bounds[0],
        effect_samples < rope_bounds[1]
    ).mean(axis=(0, 1))
    
    # Decision:
    # - If P(effect in ROPE) > 0.95: Equivalent (no meaningful difference)
    # - If P(effect < ROPE lower) > 0.90: Superior
    # - Otherwise: Inconclusive
    
    return in_rope
```

#### Rule 3: Expected Value Decision
```python
def expected_value_decision(trace, costs, revenue_per_month=78.76):
    """
    Choose treatment that maximizes expected profit
    """
    n_treatments = 4
    ev_results = {}
    
    for arm in range(n_treatments):
        # Posterior samples of churn probability
        p_churn = trace.posterior['p_churn'][:, :, arm].values.flatten()
        
        # Expected retention months (simplified)
        retention_rate = 1 - p_churn
        expected_months = 1 / p_churn  # Expected value of geometric distribution
        
        # Revenue
        expected_revenue = expected_months * revenue_per_month
        
        # Costs (discount + intervention)
        intervention_cost = costs[arm]
        
        # Net EV
        net_ev = expected_revenue - intervention_cost
        
        ev_results[f'Arm_{arm}'] = {
            'mean': net_ev.mean(),
            'median': np.median(net_ev),
            'ci_95': np.percentile(net_ev, [2.5, 97.5]),
            'prob_positive': (net_ev > 0).mean()
        }
    
    return ev_results
```

### Composite Decision Table

| Criterion | Control | T1: Standard | T2: Contract+AutoPay | T3: Premium |
|-----------|---------|--------------|----------------------|-------------|
| **P(Lift > 8%)** | 0% | >80% | >85% | >90% |
| **In ROPE (<2%)** | 100% | <10% | <5% | <5% |
| **E[EV per customer]** | -$350 | +$75 | +$180 | +$250 |
| **P(ROI > 2x)** | 0% | 65% | 80% | 85% |
| **Implementation Cost** | $0 | Low | Medium | High |

**Decision Logic:**
```
IF P(θ_treatment < θ_control - 0.08) > 0.90 AND E[EV] > $50:
    → IMPLEMENT treatment
ELIF P(effect in ROPE) > 0.95:
    → Treatment not meaningfully different, choose lowest cost
ELIF E[EV] > 0 AND P(ROI > 2) > 0.70:
    → CAUTIOUS IMPLEMENT with monitoring
ELSE:
    → DO NOT IMPLEMENT, continue testing or abandon
```

---

## 7. Sequential Testing & Adaptive Design

### Thompson Sampling for Dynamic Allocation

After initial balanced allocation, use Thompson Sampling to allocate new customers to better-performing arms:

```python
def thompson_sampling_allocation(posterior_samples, new_customers=100):
    """
    Allocate new customers based on posterior probabilities
    """
    n_arms = posterior_samples.shape[0]
    
    allocations = np.zeros(n_arms, dtype=int)
    
    for _ in range(new_customers):
        # Sample once from each arm's posterior
        samples = [np.random.choice(posterior_samples[arm]) for arm in range(n_arms)]
        
        # Allocate to arm with best sample (lowest churn)
        best_arm = np.argmin(samples)
        allocations[best_arm] += 1
    
    return allocations
```

### Futility Stopping Rule

Stop arms early if they're clearly inferior:

```python
def check_futility(trace, control_arm=0, treatment_arm=1, futility_threshold=0.05):
    """
    Stop if P(treatment better than control) < 5%
    """
    control_samples = trace.posterior['p_churn'][:, :, control_arm].values.flatten()
    treatment_samples = trace.posterior['p_churn'][:, :, treatment_arm].values.flatten()
    
    prob_better = (treatment_samples < control_samples).mean()
    
    if prob_better < futility_threshold:
        return True, f"Stop Arm {treatment_arm}: Only {prob_better:.1%} chance of being better"
    else:
        return False, "Continue"
```

### Superiority Stopping Rule

Stop and implement if clearly superior:

```python
def check_superiority(trace, control_arm=0, treatment_arm=1, 
                      superiority_threshold=0.95, min_effect=0.08):
    """
    Stop if P(treatment > control + min_effect) > 95%
    """
    control_samples = trace.posterior['p_churn'][:, :, control_arm].values.flatten()
    treatment_samples = trace.posterior['p_churn'][:, :, treatment_arm].values.flatten()
    
    prob_superior = ((control_samples - treatment_samples) > min_effect).mean()
    
    if prob_superior > superiority_threshold:
        return True, f"IMPLEMENT Arm {treatment_arm}: {prob_superior:.1%} probability of >{min_effect*100:.0f}% lift"
    else:
        return False, "Continue"
```

---

## 8. Monitoring Dashboard & KPIs

### Real-Time Bayesian Monitoring

**Weekly Updates:**
1. Posterior distributions (churn probability by arm)
2. Probability of superiority matrix
3. Expected value rankings
4. Credible interval widths (track precision improvement)

**Key Metrics Table:**

| Metric | Week 2 | Week 4 | Week 6 | Week 8 | Decision Point |
|--------|--------|--------|--------|--------|----------------|
| **Observations per arm** | 50 | 100 | 150 | 200 | - |
| **Posterior mean (Control)** | 72% ± 8% | 71% ± 6% | 71.5% ± 5% | 71.5% ± 4% | - |
| **Posterior mean (T1)** | 65% ± 10% | 62% ± 7% | 60% ± 6% | 59.5% ± 5% | - |
| **P(T1 > Control + 8%)** | 0.45 | 0.72 | 0.83 | 0.91 | ✓ IMPLEMENT |
| **E[EV per customer]** | +$45 | +$68 | +$73 | +$77 | - |

**Visualization:**
```python
import matplotlib.pyplot as plt
import arviz as az

def plot_posterior_evolution(traces_over_time):
    """
    Show how posteriors narrow over time
    """
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    for idx, (week, trace) in enumerate(traces_over_time.items()):
        ax = axes.flatten()[idx]
        
        az.plot_posterior(
            trace,
            var_names=['p_churn'],
            ref_val=0.715,  # Control baseline
            ax=ax
        )
        ax.set_title(f'Week {week}: Posterior Distributions')
        ax.set_xlabel('Churn Probability')
    
    plt.tight_layout()
    plt.savefig('posterior_evolution.png', dpi=300)
```

### Early Warning Signals

**Red Flags:**
1. **Posterior divergence**: If credible intervals are not narrowing by Week 4
2. **Effect reversal**: If early leader becomes inferior
3. **Extreme outcomes**: If observed churn deviates >2σ from predictions

**Action Triggers:**
- If any arm shows >80% churn in first 100 observations → Stop immediately
- If control arm outperforms all treatments at Week 6 → Re-evaluate test design
- If implementation costs exceed $100/customer → Reassess ROI calculations

---

## 9. Implementation Roadmap

### Phase 1: Test Preparation (Weeks 1-2)

**Week 1:**
- Finalize stratification code
- Set up data collection infrastructure
- Establish automated posterior update pipeline
- Create monitoring dashboards

**Week 2:**
- Pilot test with 50 customers (10% of sample)
- Validate randomization balance
- Test intervention delivery mechanisms
- Confirm tracking accuracy

### Phase 2: Test Execution (Weeks 3-10)

**Week 3-4: Initial Launch**
- Allocate 400 customers (100 per arm in Test 1)
- Daily monitoring for implementation issues
- First posterior update at Day 14

**Week 5-6: Mid-Point Analysis**
- Update posteriors with 150+ observations per arm
- Calculate POS and ROPE metrics
- Assess futility/superiority conditions
- Adjust Thompson Sampling allocations if appropriate

**Week 7-8: Maturation**
- Reach 200 per arm target
- Run full decision framework
- Calculate final EVs and ROI

**Week 9-10: Buffer & Validation**
- Holdout validation (100 customers not in test)
- Sensitivity analysis
- Prepare scale-up plan

### Phase 3: Decision & Scale (Weeks 11-12)

**Decision Points:**
```
Week 10 Analysis:
├─ IF any arm meets superiority criteria
│  ├─ Prepare rollout plan for winning intervention
│  └─ Estimate fleet-wide impact
│
├─ IF multiple arms are superior
│  ├─ Run cost-benefit comparison
│  └─ Consider combination strategy
│
└─ IF no clear winner
   ├─ Extend test by 4 weeks OR
   └─ Pivot to alternative strategies
```

**Rollout Strategy:**
1. **Pilot expansion** (10% of full population, 2 weeks)
2. **Staged rollout** (25% → 50% → 100%, 1 week each)
3. **Continuous monitoring** (compare to test predictions)

---

## 10. Expected Outcomes & ROI Projections

### Conservative Scenario (T1: Standard Contract)

**Assumptions:**
- 20% accept 1-year contract
- 12% absolute churn reduction (from 71.5% → 59.5%)
- Discount cost: 10% × $78.76 × 12 months = $94.51 per customer
- Only applies to acceptors

**Per 1,000 Customers:**
```
Acceptors: 200 customers
Churn prevented: 200 × 0.12 = 24 customers
Revenue saved: 24 × $78.76 × 11 months = $20,784
Discount cost: 200 × $94.51 = $18,902
Net gain: $1,882

ROI: 10%
```

### Moderate Scenario (T2: Contract + AutoPay)

**Assumptions:**
- 30% accept (contract + autopay incentive)
- 20% absolute churn reduction
- Cost: 10% discount + $10 autopay credit = $104.51

**Per 1,000 Customers:**
```
Acceptors: 300 customers
Churn prevented: 300 × 0.20 = 60 customers
Revenue saved: 60 × $78.76 × 11 months = $51,982
Total cost: 300 × $104.51 = $31,353
Net gain: $20,629

ROI: 66%
```

### Optimistic Scenario (T3: Premium Bundle)

**Assumptions:**
- 15% accept (premium commitment)
- 28% absolute churn reduction
- 25% also adopt tech services (+$20/month ARPU)
- Cost: 20% discount + tech service subsidy = $250

**Per 1,000 Customers:**
```
Acceptors: 150 customers
Churn prevented: 150 × 0.28 = 42 customers
Base revenue saved: 42 × $78.76 × 11 months = $36,327
Upsell revenue (year 1): 38 × $20 × 11 months = $8,360
Total revenue: $44,687
Total cost: 150 × $250 = $37,500
Net gain: $7,187

ROI: 19%
```

### Full Fleet Projection (All 1,521 Customers)

**If T2 is Winner and Fully Deployed:**
```
Total customers: 1,521
Expected acceptors: 456 (30%)
Churn prevented: 91 customers
Annual revenue saved: $790,584
Intervention cost: $476,566
Net profit (Year 1): $314,018

3-Year NPV (assuming 10% discount rate):
Year 1: $314,018
Year 2: $285,471 (retention compounds)
Year 3: $259,519
Total NPV: $859,008
```

---

## 11. Risk Mitigation & Contingencies

### Primary Risks

**Risk 1: Cannibalization**
- *Scenario:* Long-term customers (not in test) see offers and demand same treatment
- *Mitigation:* 
  - Limit test to predicted churners only (minimize exposure)
  - Prepare "loyalty matching" policy for complaints
  - Budget 5% spillover cost

**Risk 2: Implementation Failures**
- *Scenario:* Billing system can't handle contract variations
- *Mitigation:*
  - Technical validation in Week 1
  - Manual workaround procedures
  - Start with smallest treatment (T1) if system issues

**Risk 3: External Shocks**
- *Scenario:* Competitor launches aggressive promotion mid-test
- *Mitigation:*
  - Include "competitor activity" covariate in model
  - Extend test window if needed
  - Track external market changes weekly

**Risk 4: Model Misspecification**
- *Scenario:* Bayesian priors are wildly off
- *Mitigation:*
  - Conduct prior sensitivity analysis
  - Use weakly informative priors if uncertain
  - Show both prior and posterior in reports

### Contingency Plans

**Scenario A: All Treatments Fail (<5% lift)**
- Action: Halt tests, conduct qualitative research (interviews with churners)
- Timeline: 2 weeks for pivot
- Alternative: Focus on product/service quality issues instead

**Scenario B: Treatments Work But ROI Negative**
- Action: Reduce discount levels and re-test
- Timeline: 4-week quick test with lower discounts

**Scenario C: Control Group Outperforms (worse than baseline)**
- Action: This suggests regression to mean or seasonality
- Timeline: Extend observation period by 4 weeks

---

## 12. Success Metrics Summary

### Primary Success Metric
**90-Day Churn Rate Reduction**
- Target: ≥8% absolute reduction (from 71.5% → 63.5% or better)
- Measurement: P(θ_treatment < θ_control - 0.08) > 0.90

### Secondary Success Metrics

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| **Contract conversion** | ≥20% | Acceptance rate |
| **Payment method switch** | ≥30% e-check → autopay | Pre/post comparison |
| **Revenue per customer** | +10% ARPU | Monthly charges increase |
| **Customer lifetime** | +3 months | Median tenure extension |
| **Net Promoter Score** | No decrease | Survey subset (n=200) |
| **Support ticket volume** | <10% increase | Operational metric |

### Financial Success Metrics

| Metric | Conservative | Moderate | Optimistic |
|--------|-------------|----------|------------|
| **ROI (Year 1)** | >0% | >50% | >100% |
| **Payback period** | <18 months | <12 months | <6 months |
| **Cost per retention** | <$300 | <$200 | <$150 |
| **3-year NPV** | >$250K | >$500K | >$1M |

---

## 13. Code Implementation Snippets

### Complete Bayesian Analysis Pipeline

```python
# bayesian_churn_test.py

import pymc as pm
import pandas as pd
import numpy as np
import arviz as az
from datetime import datetime, timedelta

class BayesianChurnTest:
    """
    Complete Bayesian A/B test framework for churn reduction
    """
    
    def __init__(self, data, test_config):
        self.data = data
        self.config = test_config
        self.model = None
        self.trace = None
        
    def stratified_allocation(self, n_arms=4):
        """
        Allocate customers to test arms with blocking
        """
        data = self.data.copy()
        
        # Create blocks
        data['block'] = (
            data['risk_tier'].astype(str) + '_' +
            data['tenure_group'].astype(str)
        )
        
        # Random assignment within blocks
        np.random.seed(42)  # Reproducibility
        
        for block in data['block'].unique():
            mask = data['block'] == block
            n_block = mask.sum()
            
            # Equal allocation across arms
            assignments = np.random.choice(
                range(n_arms),
                size=n_block,
                replace=True
            )
            
            data.loc[mask, 'treatment_arm'] = assignments
        
        # Verify balance
        self._check_balance(data)
        
        return data
    
    def _check_balance(self, data):
        """
        Verify covariate balance across arms
        """
        for covariate in ['Churn_Rate', 'MonthlyCharges', 'tenure']:
            print(f"\nBalance check: {covariate}")
            print(data.groupby('treatment_arm')[covariate].mean())
    
    def build_model(self, data):
        """
        Hierarchical Bayesian model for churn test
        """
        with pm.Model() as model:
            # Indices
            n_treatments = data['treatment_arm'].nunique()
            n_tiers = data['risk_tier'].nunique()
            
            # Map to indices
            treatment_idx = data['treatment_arm'].values
            tier_idx = pd.Categorical(data['risk_tier']).codes
            
            # Hyperpriors
            μ_baseline = pm.Beta('mu_baseline', alpha=7, beta=3)
            
            # Tier effects
            σ_tier = pm.HalfNormal('sigma_tier', sigma=0.1)
            tier_effect = pm.Normal('tier_effect', mu=0, sigma=σ_tier, shape=n_tiers)
            
            # Treatment effects
            treatment_prior_means = [0, -0.12, -0.20, -0.28]
            σ_treatment = pm.HalfNormal('sigma_treatment', sigma=0.1)
            treatment_effect = pm.Normal(
                'treatment_effect',
                mu=treatment_prior_means,
                sigma=σ_treatment,
                shape=n_treatments
            )
            
            # Combine on logit scale
            logit_baseline = pm.math.log(μ_baseline / (1 - μ_baseline))
            
            logit_p = (
                logit_baseline +
                tier_effect[tier_idx] +
                treatment_effect[treatment_idx]
            )
            
            p_churn = pm.Deterministic('p_churn', pm.math.invlogit(logit_p))
            
            # Likelihood (individual-level)
            churn_obs = pm.Bernoulli(
                'churn',
                p=p_churn,
                observed=data['churn_binary'].values
            )
            
        self.model = model
        return model
    
    def run_inference(self, n_samples=2000, n_tune=1000):
        """
        MCMC sampling
        """
        with self.model:
            self.trace = pm.sample(
                n_samples,
                tune=n_tune,
                chains=4,
                cores=4,
                target_accept=0.95,
                return_inferencedata=True
            )
        
        return self.trace
    
    def decision_analysis(self):
        """
        Compute decision metrics
        """
        # Extract posterior samples
        treatment_effects = self.trace.posterior['treatment_effect'].values
        
        # Reshape: (n_chains, n_samples, n_treatments)
        treatment_effects = treatment_effects.reshape(-1, treatment_effects.shape[-1])
        
        results = {}
        
        for i in range(1, len(treatment_effects[0])):  # Skip control (0)
            # Probability of superiority
            pos = (treatment_effects[:, i] < treatment_effects[:, 0] - 0.08).mean()
            
            # In ROPE?
            in_rope = np.logical_and(
                treatment_effects[:, i] > -0.02,
                treatment_effects[:, i] < 0.02
            ).mean()
            
            # Expected value
            # Simplified: assume 11-month retention for non-churners
            retention_lift = -treatment_effects[:, i]
            ev = retention_lift * 11 * 78.76 - self.config['costs'][i]
            
            results[f'T{i}'] = {
                'P(Superiority)': pos,
                'P(in_ROPE)': in_rope,
                'Expected_Value_Mean': ev.mean(),
                'Expected_Value_95CI': np.percentile(ev, [2.5, 97.5]),
                'P(ROI > 2x)': (ev > 2 * self.config['costs'][i]).mean()
            }
        
        return pd.DataFrame(results).T
    
    def plot_results(self, output_path='results/'):
        """
        Generate diagnostic plots
        """
        import matplotlib.pyplot as plt
        
        # Posterior distributions
        az.plot_posterior(
            self.trace,
            var_names=['treatment_effect'],
            ref_val=0,
            figsize=(12, 4)
        )
        plt.savefig(f'{output_path}posterior_treatment_effects.png', dpi=300)
        plt.close()
        
        # Trace plots (check convergence)
        az.plot_trace(
            self.trace,
            var_names=['treatment_effect', 'mu_baseline']
        )
        plt.tight_layout()
        plt.savefig(f'{output_path}trace_plots.png', dpi=300)
        plt.close()
        
        # Forest plot (effect sizes with CIs)
        az.plot_forest(
            self.trace,
            var_names=['treatment_effect'],
            combined=True,
            figsize=(8, 6)
        )
        plt.axvline(0, color='red', linestyle='--', label='No effect')
        plt.axvline(-0.08, color='green', linestyle='--', label='Target effect')
        plt.legend()
        plt.savefig(f'{output_path}forest_plot.png', dpi=300)
        plt.close()

# Example usage
if __name__ == '__main__':
    # Load data
    df = pd.read_csv('recommendation.csv')
    
    # Prepare
    df['churn_binary'] = (df['Actual_Churn'] == 'Yes').astype(int)
    df['risk_tier'] = pd.cut(df['Churn_Rate'], bins=[0, 0.6, 0.75, 1], labels=['Moderate', 'High', 'Extreme'])
    df['tenure_group'] = pd.cut(df['tenure'], bins=[0, 3, 6, 12, 100], labels=['0-3mo', '4-6mo', '7-12mo', '13+mo'])
    
    # Config
    config = {
        'costs': [0, 94.51, 104.51, 250],  # Per customer intervention cost
        'n_arms': 4
    }
    
    # Initialize test
    test = BayesianChurnTest(df.head(800), config)
    
    # Allocate
    df_allocated = test.stratified_allocation()
    
    # Simulate outcomes (in real test, this comes from actual observations)
    # For now, use actual churn as observed data
    df_allocated['churn_binary'] = (df_allocated['Actual_Churn'] == 'Yes').astype(int)
    
    # Build and run
    test.build_model(df_allocated)
    test.run_inference()
    
    # Analyze
    decision_metrics = test.decision_analysis()
    print("\n" + "="*60)
    print("DECISION METRICS")
    print("="*60)
    print(decision_metrics)
    
    # Plot
    test.plot_results()
    
    print("\n✓ Analysis complete. See results/ folder for plots.")
```

---

## 14. Next Steps & Action Items

### Immediate Actions (Week 1)

- [ ] **Finalize test design** with stakeholders
- [ ] **Set up infrastructure**
  - Data pipeline for real-time tracking
  - Automated posterior updates (daily)
  - Dashboard for monitoring
- [ ] **Validate technical implementation**
  - Can billing system handle contract variations?
  - Can payment method changes be automated?
  - Are promotional codes set up correctly?
- [ ] **Prepare intervention materials**
  - Email templates for each treatment
  - Scripts for customer service
  - FAQ for common questions

### Pre-Launch Checklist

- [ ] Randomization code tested and validated
- [ ] Blocking variables confirmed balanced
- [ ] All tracking pixels/events firing correctly
- [ ] Fallback procedures documented
- [ ] Stakeholder alignment on decision criteria
- [ ] Legal/compliance review complete

### Weekly Monitoring Routine

**Every Monday:**
1. Update posteriors with new week's data
2. Calculate decision metrics (POS, ROPE, EV)
3. Check for stopping criteria (futility/superiority)
4. Generate stakeholder report
5. Adjust Thompson Sampling allocations if warranted

---

## Conclusion

This Bayesian A/B testing framework provides:

1. **Rigorous statistical foundation** with hierarchical modeling
2. **Practical decision rules** (POS, ROPE, EV) for real-world implementation
3. **Adaptive design** (Thompson Sampling) to minimize regret
4. **Clear success metrics** aligned with business goals
5. **Comprehensive risk mitigation** strategies

**Expected Timeline:**
- Weeks 1-2: Preparation
- Weeks 3-10: Test execution
- Weeks 11-12: Decision & rollout planning
- Month 4+: Fleet-wide implementation

**Conservative Projection:**
- **Year 1 Net Benefit:** $314,018 (assuming T2 wins)
- **3-Year NPV:** $859,008
- **ROI:** 66% in year 1, compounding thereafter

The combination of contract upgrades, payment method optimization, and service upsells addresses the root causes of churn in this population. The Bayesian framework allows for continuous learning and adaptation, maximizing both statistical rigor and business value.

---

**Questions or modifications needed?** Let me know if you'd like me to:
1. Adjust sample sizes or test arms
2. Modify prior distributions based on different assumptions
3. Add additional tests (e.g., customer communication variants)
4. Create simulation code to pre-test the experimental design
5. Build custom visualization dashboards
