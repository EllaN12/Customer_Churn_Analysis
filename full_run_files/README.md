# 🧪 Bayesian A/B Testing Framework for Churn Reduction
### Portfolio Project: Demonstrating Advanced Experimental Design Skills

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![PyMC](https://img.shields.io/badge/PyMC-5.0+-red.svg)](https://www.pymc.io/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.0+-FF4B4B.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 📋 Project Overview

**Business Problem:** A telecommunications company is losing $942K annually to customer churn among high-risk customers (71.5% churn rate). They need to test retention interventions but want to minimize experiment duration and maximize ROI.

**Solution:** I designed a complete Bayesian A/B testing framework that:
- ✅ Enables **30% faster decision-making** vs traditional methods through sequential testing
- ✅ Quantifies **uncertainty and ROI** to support business decisions
- ✅ **Simulates outcomes** to validate design before spending $$$
- ✅ Provides **interactive tools** for stakeholder communication

**Portfolio Value:** This project demonstrates end-to-end capabilities in statistical design, Bayesian inference, Monte Carlo simulation, and product thinking—without requiring a 90-day experiment.

---

## 🎯 Key Features

### 1. **Comprehensive Experimental Design** 📊
- Hierarchical Bayesian models accounting for customer segments
- Power analysis for 3 intervention strategies
- Sample size optimization (power vs cost trade-offs)
- Early stopping rules (superiority & futility)

### 2. **Monte Carlo Simulation Engine** 🎲
- Simulates 1,000+ experiment runs in minutes
- Demonstrates power analysis, convergence, decision-making
- Sensitivity analysis for robustness testing
- Enables "show, don't tell" portfolio presentations

### 3. **Interactive Decision Dashboard** 📱
- **Streamlit app** for real-time experimentation
- Visual posterior updates as data accumulates
- ROI calculator with uncertainty quantification
- Stakeholder-friendly interface (no stats knowledge required)

### 4. **Production-Ready Code** 💻
- Clean, documented, testable Python
- Modular design for extensibility
- Complete with usage examples
- Ready for deployment

---

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/bayesian-churn-ab-test
cd bayesian-churn-ab-test

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Run the Analysis

```bash
# 1. Run comprehensive analysis (generates all artifacts)
python bayesian_ab_test_implementation.py

# 2. Run Monte Carlo simulations (power analysis)
python monte_carlo_simulation.py

# 3. Launch interactive dashboard
streamlit run streamlit_dashboard.py
```

---

## 📂 Repository Structure

```
bayesian-churn-ab-test/
│
├── README.md                          # You are here!
├── requirements.txt                   # Python dependencies
│
├── data/
│   ├── recommendation.csv            # Churn prediction dataset (1,521 customers)
│   └── data_insights_summary.png     # Exploratory analysis visualization
│
├── notebooks/
│   ├── 01_exploratory_analysis.ipynb # Data exploration
│   ├── 02_experimental_design.ipynb  # Test design & justification
│   └── 03_simulation_study.ipynb     # Monte Carlo analysis
│
├── src/
│   ├── bayesian_ab_test_implementation.py  # Main analysis code
│   ├── monte_carlo_simulation.py           # Power analysis simulator
│   └── streamlit_dashboard.py              # Interactive app
│
├── docs/
│   ├── bayesian_ab_test_design.md          # Complete technical design (39KB)
│   ├── portfolio_project_recommendations.md # Alternative approaches
│   └── methodology.md                      # Statistical methodology
│
└── outputs/
    ├── power_analysis_results.png          # Main power analysis viz
    ├── sample_size_comparison.png          # Sample size trade-offs
    ├── sensitivity_analysis.png            # Robustness testing
    ├── simulation_summary_report.md        # Executive summary
    └── simulation_detailed_results.csv     # Raw simulation data
```

---

## 💡 Technical Highlights

### Bayesian Hierarchical Model

```python
with pm.Model() as model:
    # Population-level baseline
    μ_baseline = pm.Beta('mu_baseline', alpha=7, beta=3)  # ~70% prior churn
    
    # Risk tier effects (varying intercepts)
    σ_tier = pm.HalfNormal('sigma_tier', sigma=0.15)
    tier_offset = pm.Normal('tier_offset', mu=0, sigma=σ_tier, shape=3)
    
    # Treatment effects (varying slopes)
    treatment_effect = pm.Normal(
        'treatment_effect',
        mu=[0, -0.12, -0.20, -0.28],  # Informative priors
        sigma=0.15,
        shape=4
    )
    
    # Combine on logit scale
    logit_p_churn = logit_baseline + tier_offset[tier_idx] + treatment_effect[treatment_idx]
    p_churn = pm.math.invlogit(logit_p_churn)
    
    # Likelihood
    churn_obs = pm.Bernoulli('churn', p=p_churn, observed=data)
```

### Decision Framework

Three-stage decision rule:

1. **Probability of Superiority (POS)**
   ```
   IF P(θ_treatment < θ_control - 8%) > 90% → Strong evidence
   ```

2. **Region of Practical Equivalence (ROPE)**
   ```
   IF P(|θ_treatment - θ_control| < 2%) > 95% → No meaningful difference
   ```

3. **Expected Value**
   ```
   IF E[Revenue - Cost] > $50 per customer → ROI positive
   ```

### Monte Carlo Power Analysis

Simulates running the experiment 1,000 times with different random outcomes:

```python
def run_power_analysis(n_simulations=1000):
    results = []
    for sim in range(n_simulations):
        # Simulate one complete experiment
        data = simulate_experiment(true_effects, sample_size)
        
        # Run Bayesian inference
        posterior = fit_model(data)
        
        # Check decision criteria
        detected = check_superiority(posterior, threshold=0.90)
        
        results.append({
            'simulation': sim,
            'detected_effect': detected,
            'weeks_to_decision': get_stopping_week(data)
        })
    
    power = mean(detected_effect)  # % of times we correctly identified winner
    return power, results
```

**Result:** 92% power to detect 20% churn reduction with 200 customers per arm

---

## 📊 Key Results

### Business Impact Projection

| Metric | Conservative | Realistic | Optimistic |
|--------|--------------|-----------|------------|
| **Churn Reduction** | 12% | 20% | 28% |
| **Adoption Rate** | 20% | 30% | 40% |
| **Year 1 Net Profit** | $94K | $314K | $580K |
| **3-Year NPV** | $270K | $859K | $1.6M |
| **ROI** | 25% | 66% | 135% |
| **Payback Period** | 18 mo | 12 mo | 6 mo |

### Statistical Performance

- **Power:** 92% to detect 20% effect, 85% to detect 12% effect
- **Time savings:** Average 6.2 weeks vs 8 weeks (fixed horizon)
- **Early stopping:** 68% of simulations stopped before week 8
- **False positive rate:** <5% (well-controlled Type I error)

### Methodological Advantages

**Bayesian vs Frequentist:**
- ✅ Interpretable probabilities: "90% confident Treatment 2 works" vs p=0.03
- ✅ Continuous monitoring without alpha inflation
- ✅ Can incorporate prior knowledge (e.g., payment method insights)
- ✅ Natural decision framework (probability statements → business decisions)
- ✅ Hierarchical structure handles multiple segments elegantly

---

## 🎨 Visualizations

### 1. Data Insights Dashboard
![Data Insights](outputs/data_insights_summary.png)
*9-panel exploratory analysis showing churn patterns, service gaps, and intervention opportunities*

### 2. Power Analysis Results
![Power Analysis](outputs/power_analysis_results.png)
*Statistical power by treatment arm, test duration distribution, early stopping rates*

### 3. Interactive Streamlit App
![Dashboard](docs/streamlit_screenshot.png)
*Live dashboard for experiment simulation, decision support, and ROI calculation*

---

## 🧠 What This Demonstrates

### For Employers

**Statistical Expertise:**
- ✅ Bayesian inference (PyMC, MCMC, hierarchical models)
- ✅ Experimental design (power analysis, sample size, blocking)
- ✅ Causal inference (confounding, observational vs experimental)
- ✅ Monte Carlo simulation (sensitivity, robustness)

**Engineering Skills:**
- ✅ Production Python (modular, tested, documented)
- ✅ Data visualization (Matplotlib, Plotly, Seaborn)
- ✅ Interactive dashboards (Streamlit)
- ✅ Reproducible workflows

**Business Acumen:**
- ✅ ROI-focused decision-making
- ✅ Stakeholder communication (non-technical audiences)
- ✅ Risk management (uncertainty quantification)
- ✅ Product thinking (build tools, not just analyses)

### Talking Points for Interviews

**"Walk me through your approach"**
> "I started with observational analysis to identify promising interventions—autopay users showed 12% lower churn. Then I designed a 4-arm Bayesian experiment to validate causally. Monte Carlo simulations showed 92% power with 200 per arm. I built a Streamlit dashboard so stakeholders could interact with the decision framework."

**"Why Bayesian methods?"**
> "Three reasons: 1) Probability statements that stakeholders understand ('90% confident it works'), 2) Can stop early when we detect a winner, saving time and money, 3) Hierarchical structure elegantly handles different customer segments. For this problem, it reduces test duration by ~30%."

**"How would you validate this in production?"**
> "I'd implement sequential monitoring with automated stopping rules, use Thompson Sampling for adaptive allocation after the initial phase, maintain a holdout group for long-term validation, and build dashboards for real-time posterior tracking. I'd also set up A/A tests first to validate the infrastructure."

---

## 🎓 Learning Resources

Want to learn Bayesian A/B testing? I found these helpful:

**Books:**
- *Bayesian Data Analysis* - Gelman et al. (bible of Bayesian stats)
- *Statistical Rethinking* - McElreath (intuitive intro)
- *Trustworthy Online Controlled Experiments* - Kohavi et al. (A/B testing)

**Courses:**
- [Bayesian Methods for Hackers](https://github.com/CamDavidsonPilon/Probabilistic-Programming-and-Bayesian-Methods-for-Hackers) (Free)
- [PyMC Tutorial](https://www.pymc.io/projects/docs/en/stable/learn.html) (Official docs)

**Papers:**
- [Multi-Armed Bandit for A/B Testing](https://arxiv.org/abs/1111.1797)
- [Bayesian AB Testing at VWO](https://vwo.com/downloads/VWO_SmartStats_technical_whitepaper.pdf)

---

## 📧 Contact & Connect

**Portfolio:** [yourportfolio.com](https://yourportfolio.com)  
**LinkedIn:** [linkedin.com/in/yourprofile](https://linkedin.com/in/yourprofile)  
**GitHub:** [github.com/yourusername](https://github.com/yourusername)  
**Email:** your.email@example.com

---

## 🤝 Acknowledgments

- Dataset inspired by [Telco Customer Churn](https://www.kaggle.com/datasets/blastchar/telco-customer-churn) on Kaggle
- Bayesian methods guidance from PyMC community
- Dashboard design inspired by Streamlit gallery examples

---

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

---

## ⭐ Final Notes

**This is a portfolio project** designed to showcase skills without running a 90-day experiment. The analysis uses simulated outcomes and historical data patterns to demonstrate methodology.

**Want to use this template?**
1. Fork this repository
2. Replace data with your own use case
3. Adjust treatment effects and costs
4. Customize the dashboard
5. Add your personal branding

**Questions or feedback?** Open an issue or reach out directly!

---

<div align="center">
  
### Built with ❤️ using Python, PyMC, and Streamlit
  
**Ready to discuss how I can bring these skills to your team?**
  
[Schedule a conversation →](https://calendly.com/yourlink)

</div>
