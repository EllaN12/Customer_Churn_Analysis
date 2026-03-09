# 🎯 Bayesian Churn Reduction: From Correlation to Causation

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![PyMC](https://img.shields.io/badge/PyMC-5.0+-red.svg)](https://www.pymc.io/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**A Portfolio Project Demonstrating Advanced Causal Inference and Experimental Design**

---

## 🔥 The Dramatic Finding

Analyzing 7,042 telecom customers, I discovered that **customers in their first 40 days have 60.9% churn** versus 23.2% baseline—a **+37.7 percentage point penalty**.

But the real story isn't the finding. It's what I did next.

---

## 📖 The Story

### Part 1: Discovery
Found strong correlations between churn and multiple factors (tenure, contracts, payment methods, add-on services).

### Part 2: Attempted Causal Validation
Built Bayesian model controlling for tenure, contract type, payment method to isolate add-on effects.

### Part 3: Critical Realization ⚡
**Tenure is a COLLIDER**—it's caused by BOTH add-ons AND churn. Controlling for it induces bias, not removes it.

Contract and payment are **OTHER TREATMENTS**, not confounders—they need causal analysis themselves.

### Part 4: Methodological Correction
Rebuilt model controlling only for truly exogenous pre-treatment variables (age, family structure). Acknowledged limitations of observational data.

### Part 5: Rigorous Solution
Designed three randomized experiments to establish causality definitively, including factorial design to test interactions.

**Why This Matters:** Most data scientists miss collider bias. Catching it, correcting it, and designing proper experiments demonstrates top 1% statistical sophistication.

---

## 🎯 What This Project Demonstrates

### **Statistical Rigor**
- ✅ Deep understanding of causal inference (colliders, mediators, confounders)
- ✅ Bayesian hierarchical models
- ✅ Monte Carlo power analysis
- ✅ Sequential testing with stopping rules
- ✅ Stratified block randomization

### **Intellectual Honesty**
- ✅ Questioned own assumptions
- ✅ Identified and corrected methodological error
- ✅ Acknowledged limitations of observational data
- ✅ Proposed rigorous experimental solution

### **Business Acumen**
- ✅ ROI-focused analysis ($372K projected annual profit)
- ✅ Prioritized interventions by impact and feasibility
- ✅ Designed implementable experimental framework
- ✅ Created stakeholder-friendly decision tools

### **Technical Skills**
- ✅ Production-ready Python code
- ✅ Interactive dashboards (Streamlit)
- ✅ Automated randomization system
- ✅ Complete experimental infrastructure

---

## 📊 Key Results

### **Observational Findings**

| Finding | Effect Size | Population | Status |
|---------|-------------|------------|--------|
| **Early tenure (≤40 days)** | +37.7% churn | 624 customers (8.9%) | ⚠️ Confounded by selection |
| **E-check vs Autopay** | +28.6% churn | 2,364 e-check users | ⚠️ Treatment, not confounder |
| **Month-to-month vs Long-term** | +35.6% churn | 3,874 MTM (55%) | ⚠️ Treatment, not confounder |
| **Add-ons (corrected estimate)** | -3.2% churn | 4,249 with add-ons | ⚠️ Residual confounding |

### **Experimental Projections**

| Experiment | Population | Sample Size | Expected Impact | ROI |
|------------|-----------|-------------|-----------------|-----|
| **Early Tenure Intervention** | New customers | 400 (100/arm) | $82K annual profit | 700% |
| **Contract + Payment + Add-ons** | MTM customers | 800 (100/cell) | $93K annual profit | 179% |
| **Fiber Service Quality** | Fiber customers | 300 (100/arm) | $85K annual profit | 320% |
| **TOTAL PORTFOLIO** | - | - | **$372K annual** | - |

---

## 🚀 Quick Start

### **Installation**

```bash
git clone https://github.com/yourusername/bayesian-churn-portfolio
cd bayesian-churn-portfolio
pip install -r requirements.txt
```

### **Run the Analysis**

```bash
# 1. Proper causal inference (corrected approach)
python proper_causal_inference.py

# 2. Power analysis for experiments
python power_analysis_experiments.py

# 3. Demonstration of randomization system
python experiment_randomization.py

# 4. Interactive dashboard
streamlit run streamlit_monitoring.py
```

---

## 📁 Repository Structure

```
bayesian-churn-portfolio/
│
├── README.md                                    ← You are here
├── requirements.txt
│
├── 📊 ANALYSIS/
│   ├── proper_causal_inference.py              ← Corrected causal analysis
│   ├── full_dataset_causal_validation.py       ← Comprehensive validation
│   └── visualizations/                         ← Generated charts
│
├── 🧪 EXPERIMENTAL_DESIGN/
│   ├── RANDOMIZED_EXPERIMENT_DESIGN_COMPLETE.md  ← Full protocol
│   ├── power_analysis_experiments.py           ← Monte Carlo simulations
│   ├── experiment_randomization.py             ← Stratified assignment
│   └── bayesian_monitoring_system.py           ← Sequential testing
│
├── 📄 DOCUMENTATION/
│   ├── CAUSAL_INFERENCE_JOURNEY.md             ⭐ Key narrative document
│   ├── CAUSAL_INFERENCE_CORRECTION.md          ← Why I corrected my approach
│   ├── PROJECT_COMPLETION_GUIDE.md             ← How to complete this
│   └── INTERVIEW_GUIDE.md                      ← How to present this
│
└── 📈 OUTPUTS/ (generated)
    ├── churn_drivers_ranked.png
    ├── collider_bias_demonstration.png
    ├── power_analysis_results.png
    └── assignments_*.csv
```

---

## 🎓 The Causal Inference Journey (Centerpiece)

**Read: [`CAUSAL_INFERENCE_JOURNEY.md`](CAUSAL_INFERENCE_JOURNEY.md)**

This document chronicles the complete methodological journey:

1. **Discovery:** Finding dramatic churn patterns
2. **Attempt:** Initial causal validation (flawed)
3. **Realization:** Understanding collider bias
4. **Correction:** Proper causal inference
5. **Solution:** Experimental design

**Why it's valuable:** Shows not just what I found, but how I think—including catching and correcting my own errors.

---

## 🔬 Technical Highlights

### **Collider Bias Demonstration**

```python
# Tenure is caused by BOTH add-ons AND churn
# Controlling for it induces bias

# Empirical evidence:
# Early tenure (0-3 months): Add-ons reduce churn by 5%
# Long tenure (13+ months): Add-ons INCREASE churn by 1% ❌

# This reversal is signature of collider bias!
```

### **Proper Causal Model**

```python
with pm.Model() as proper_model:
    # ONLY exogenous pre-treatment confounders
    addon_effect = pm.Normal('addon_causal_effect', mu=-0.03, sigma=0.05)
    
    β_senior = pm.Normal('beta_senior', ...)       # ✅ Age (exogenous)
    β_dependents = pm.Normal('beta_dependents', ...)  # ✅ Family (exogenous)
    
    # DO NOT INCLUDE:
    # ❌ Tenure (collider)
    # ❌ Contract (other treatment)
    # ❌ Payment (other treatment)
    # ❌ Charges (mediator)
```

### **Experimental Design**

**Factorial 2×2×2 Design:**
- Factor 1: Contract (MTM vs 1-year)
- Factor 2: Payment (Current vs Autopay)
- Factor 3: Add-ons (No offer vs Bundle)

**Advantages:**
- Tests 3 interventions in one experiment
- Estimates interaction effects
- 90%+ power for main effects with n=100 per cell

---

## 📊 Visualizations

### Churn Drivers Ranked
![Churn Drivers](outputs/churn_drivers_ranked.png)

### Power Analysis Results
![Power Analysis](outputs/power_analysis_results.png)

### Collider Bias Demonstration
![Collider Bias](outputs/collider_bias_demonstration.png)

---

## 💼 For Employers

### **What This Shows**

**Most Candidates:**
```
1. Found churn patterns
2. Ran regression with controls
3. "Add-ons reduce churn, p < 0.05"
4. Recommend promoting add-ons
```

**What I Did:**
```
1. Found dramatic patterns (+37.7% early tenure penalty)
2. Attempted causal validation
3. Realized tenure is a collider → corrected approach
4. Acknowledged observational limitations
5. Designed rigorous randomized experiments
6. Built complete experimental infrastructure
7. Quantified ROI with uncertainty
```

**Difference:** I don't just run models—I think deeply about causality, catch subtle issues, and design rigorous solutions.

### **Skills Demonstrated**

| Category | Skills |
|----------|--------|
| **Statistics** | Causal inference, Bayesian methods, experimental design, power analysis |
| **Programming** | Python, PyMC, Pandas, NumPy, Matplotlib, Streamlit |
| **Communication** | Technical writing, data visualization, stakeholder materials |
| **Business** | ROI analysis, prioritization, implementation planning |
| **Thinking** | Critical analysis, intellectual honesty, problem-solving |

---

## 🎤 Interview Preparation

### **5-Minute Pitch**

> "I analyzed 7,000 telecom customers and found that those in their first 40 days have 61% churn versus 23%—a 38-point penalty.
>
> I initially tried causal validation using observational data, controlling for tenure and other factors. But I realized **tenure is a collider**—it's caused by both the treatment and outcome. Controlling for it actually induces bias.
>
> I corrected this by using only exogenous variables, but acknowledged that observational data has fundamental limits. The proper solution is randomization.
>
> I designed a factorial experiment testing contracts, payment methods, and add-ons. Monte Carlo simulation shows 90%+ power with 200 customers per arm. Conservative projection: $372K annual profit."

**See [`INTERVIEW_GUIDE.md`](INTERVIEW_GUIDE.md) for full preparation.**

---

## 📚 Learn More

**Key Documents:**
- [`CAUSAL_INFERENCE_JOURNEY.md`](CAUSAL_INFERENCE_JOURNEY.md) - Complete narrative
- [`RANDOMIZED_EXPERIMENT_DESIGN_COMPLETE.md`](RANDOMIZED_EXPERIMENT_DESIGN_COMPLETE.md) - Experimental protocol
- [`CAUSAL_INFERENCE_CORRECTION.md`](CAUSAL_INFERENCE_CORRECTION.md) - Why I corrected my approach

**Code:**
- [`proper_causal_inference.py`](proper_causal_inference.py) - Corrected analysis
- [`power_analysis_experiments.py`](power_analysis_experiments.py) - Monte Carlo
- [`experiment_randomization.py`](experiment_randomization.py) - Randomization system

---

## 🤝 Contact

**Portfolio:** [yourportfolio.com](https://yourportfolio.com)  
**LinkedIn:** [linkedin.com/in/yourprofile](https://linkedin.com/in/yourprofile)  
**Email:** your.email@example.com

---

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) for details.

---

## ⭐ Acknowledgments

- Dataset inspired by [Telco Customer Churn](https://www.kaggle.com/datasets/blastchar/telco-customer-churn)
- Causal inference guidance from *Causal Inference: The Mixtape* and *Mostly Harmless Econometrics*
- Bayesian methods from PyMC community

---

<div align="center">

### 🎯 Ready to Discuss How I Can Apply This Rigor to Your Team?

**Looking for Data Scientist roles where causal thinking matters.**

[Schedule a conversation →](https://calendly.com/yourlink)

</div>

---

## 🚀 Next Steps

**If you're an employer:**
1. Read [`CAUSAL_INFERENCE_JOURNEY.md`](CAUSAL_INFERENCE_JOURNEY.md) (10 min)
2. Review the experimental design (5 min)
3. Run the code to see it in action (5 min)
4. [Reach out](mailto:your.email@example.com) to discuss

**If you're a data scientist:**
1. Fork this repo
2. Apply the framework to your data
3. Customize the experimental design
4. Use it for your own portfolio

---

**Built with ❤️ using Python, PyMC, and rigorous causal thinking.**

*Last updated: February 2026*
