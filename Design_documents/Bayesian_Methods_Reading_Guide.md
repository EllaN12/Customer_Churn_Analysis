# Bayesian Methods Reading Guide
### Telco Churn Portfolio — Methodology Reference

Each section maps a specific method used in this portfolio to the most targeted books and courses for deep study. Organised in the order methods appear across the pipeline (Phase 2 → Phase 3 → Phase 4).

---

## 1. Bayesian Foundations & Beta-Binomial Conjugate Model

**Where used:** `bayesian_monitoring_system.py` — weekly Beta posterior updates on churn proportions; all prior specifications (Beta(2,9), Beta(2,12), Beta(1,9)).

### Books

**Doing Bayesian Data Analysis** — John Kruschke (2nd ed., 2015)
Chapter 5–6 cover Beta-Binomial conjugacy in depth with business-oriented examples. Kruschke's "BEST" framework directly underpins the ROPE and HDI logic used in this portfolio. The most accessible starting point.

**Bayesian Data Analysis** — Gelman, Carlin, Stern, Dunson, Vehtari, Rubin (3rd ed., 2013)
Chapters 1–3 cover prior specification, conjugate families, and posterior derivation rigorously. Chapter 5 introduces hierarchical structures. This is the field's canonical reference — dense but comprehensive.

**A First Course in Bayesian Statistical Methods** — Peter Hoff (2009)
Chapters 3–4 walk through Beta-Binomial conjugacy and prior elicitation for proportions step by step. More approachable than BDA3 while still being mathematically precise.

### Courses

**Statistical Rethinking** — Richard McElreath (free, YouTube — Winter 2023 lectures)
Lectures 1–4 build intuition for priors and likelihoods from scratch using coin-flip / proportion examples. McElreath's approach to thinking about priors as scientific claims directly maps to how treatment priors are set in this portfolio. Companion textbook (same title, 2nd ed., 2020) is equally recommended.
→ https://www.youtube.com/playlist?list=PLDcUM9US4XdPz-KxHM4XHt7uUVGWWVSus

**Bayesian Statistics: From Concept to Data Analysis** — UC Santa Cruz / Coursera (Herbert Lee)
Covers Beta-Binomial, conjugate priors, and posterior predictive distributions in the first two weeks. Good structured complement to self-study.

---

## 2. Prior Elicitation — Informed & Weakly Informative Priors

**Where used:** Treatment priors Beta(2,9)/Beta(2,12)/Beta(1,9) encoding expected effect directions; hyperpriors Gamma(7,10)/Gamma(3,10) in hierarchical model.

### Books

**Bayesian Data Analysis (BDA3)** — Gelman et al., Chapter 2 & Appendix A
Section 2.9 specifically addresses weakly informative priors and prior predictive checks — the recommended method for validating the treatment priors used here.

**Statistical Rethinking** — McElreath, Chapter 4
The section on prior predictive simulation is the clearest practical guide to choosing priors that encode domain knowledge without over-constraining the likelihood. The "garden of forking data" framing applies directly to how Beta(2,9) encodes "probably helpful, not certain."

**Regression and Other Stories** — Gelman, Hill, Vehtari (2020), Chapter 9
Focused on weakly informative priors in regression contexts, with concrete guidance on scale choices — directly relevant to the logit-scale priors in `BayesianChurnModel.build_model()`.

### Courses

**Statistical Rethinking** (McElreath), Lectures 4–5
The prior predictive check workflow shown here is the exact procedure to use when auditing treatment priors. Highly recommended to watch before modifying any prior specification in Phase 3 or 4.

---

## 3. MCMC Sampling — NUTS, Hamiltonian Monte Carlo, PyMC

**Where used:** All `pm.sample()` calls across `bayesian_monitoring_system.py`, `bayesian_ab_test_implementation.py`, `proper_causal_inference.py`, `full_dataset_causal_validation.py`, `bayesian_analysis_engine.py`. Parameters: `chains=4`, `tune=1000`, `target_accept=0.95`.

### Books

**Probabilistic Programming and Bayesian Methods for Hackers** — Cam Davidson-Pilon (free online)
The PyMC-native guide. Chapter 1–3 cover the mechanics of MCMC in the context of PyMC syntax. Best for understanding why `tune`, `chains`, and `target_accept` are set the way they are.
→ https://github.com/CamDavidsonPilon/Probabilistic-Programming-and-Bayesian-Methods-for-Hackers

**Bayesian Data Analysis (BDA3)** — Gelman et al., Chapter 11–12
Covers Metropolis-Hastings, HMC, and NUTS derivations. Chapter 11.5 on the no-U-turn sampler explains why `target_accept=0.95` trades sampling speed for accuracy in high-curvature posteriors (as encountered in the hierarchical model).

**Statistical Rethinking** — McElreath, Chapter 9
"Markov Chain Monte Carlo" chapter — the most intuitive explanation of why chains need warmup (tuning), what divergences mean, and how to interpret trace plots. Required reading before diagnosing any convergence issues.

### Courses

**PyMC Documentation — "Getting Started" + "Model Building" tutorials**
→ https://www.pymc.io/projects/docs/en/stable/learn/core_notebooks/
The official notebook series walks through the exact API used in this portfolio. The "GLM" and "Hierarchical Models" notebooks are directly applicable.

**Bayesian Computation with Stan** — Michael Betancourt (free, case studies)
Although written for Stan, Betancourt's essays on HMC geometry and divergence diagnostics are the definitive reference for understanding what PyMC's sampler is doing internally.
→ https://betanalpha.github.io/writing/

---

## 4. Convergence Diagnostics — R-hat, ESS, ArviZ

**Where used:** `az.summary()` calls for R-hat and ESS reporting; convergence threshold R-hat < 1.01 used in `bayesian_monitoring_system.py`; trace plots and forest plots via ArviZ in `bayesian_ab_test_implementation.py`.

### Books

**Bayesian Data Analysis (BDA3)** — Gelman et al., Chapter 11.4–11.5
Original derivation of the $\hat{R}$ (R-hat) statistic and effective sample size. The 2019 update to R-hat (Vehtari et al.) improved the estimator — ArviZ implements the updated version.

**Statistical Rethinking** — McElreath, Chapter 9
Explains R-hat and n_eff (ESS) in plain language with visual intuition for what "mixing" means. The `traceplot` interpretation guide here is the clearest available.

### Papers (primary sources)

**Rank-normalization, folding, and localization: An improved R-hat for assessing convergence of MCMC** — Vehtari, Gelman et al. (2021, Bayesian Analysis)
The paper behind ArviZ's current R-hat implementation. Read this to understand why R-hat < 1.01 is the threshold used here rather than the older 1.1.

**ArviZ Documentation**
→ https://python.arviz.org/en/stable/
Covers `az.summary()`, `az.plot_trace()`, `az.plot_forest()`, and `az.plot_posterior()` — every ArviZ function used in this portfolio.

---

## 5. Hierarchical (Multilevel) Bayesian Models

**Where used:** `BayesianChurnModel.build_model()` in `bayesian_ab_test_implementation.py` — hyperpriors over baseline, risk-tier varying intercepts (`tier_offset`), treatment varying slopes (`treatment_effect`).

### Books

**Statistical Rethinking** — McElreath, Chapters 13–14
The clearest available treatment of partial pooling, varying intercepts, and varying slopes — exactly the structure in `build_model()`. McElreath's "coffee robot" and "classroom" examples map directly to "risk tier as grouping variable" and "treatment as slope." Essential.

**Bayesian Data Analysis (BDA3)** — Gelman et al., Chapters 5, 15–17
Chapter 5 introduces hierarchical models formally; Chapters 15–17 cover linear hierarchical models with full posterior derivation. More mathematical depth than McElreath.

**Data Analysis Using Regression and Multilevel/Hierarchical Models** — Gelman & Hill (2006)
The applied companion to BDA3. Chapter 11–13 cover multilevel models in a regression framework. Particularly useful for understanding the logit-scale linear predictor structure used in `build_model()`.

### Courses

**Statistical Rethinking** (McElreath), Lectures 13–15
These three lectures on multilevel models are the best 6 hours you can spend understanding why varying-intercept/varying-slope structures outperform separate or pooled models for segmented A/B tests.

**Hierarchical Models in PyMC** — PyMC official tutorial
→ https://www.pymc.io/projects/examples/en/latest/generalized_linear_models/multilevel_modeling.html

---

## 6. Sequential Bayesian Testing & Stopping Rules

**Where used:** All stopping logic in `bayesian_monitoring_system.py` and `config.py` — superiority (P > 0.95, effect > 8pp), futility (P < 0.05), ROPE equivalence (±2pp, P > 0.80).

### Books

**Doing Bayesian Data Analysis** — Kruschke, Chapters 11–12
Kruschke developed the Bayesian stopping rule framework that directly inspired the superiority/futility/ROPE structure used here. Chapter 12 explicitly covers when to stop data collection, with the HDI+ROPE decision procedure.

**Bayesian Data Analysis (BDA3)** — Gelman et al., Chapter 7
Section 7.4 covers posterior predictive checks and sequential model evaluation — the theoretical grounding for interim analyses.

### Papers (primary sources)

**Bayesian Estimation Supersedes the t Test (BEST)** — Kruschke (2013, Journal of Experimental Psychology)
Introduces HDI+ROPE as a decision framework. The superiority/ROPE logic in this portfolio is a direct application of BEST to proportions.

**A/B Testing Intuition Busters** — Ron Kohavi & Stefan Thomke (Harvard Business Review)
Practical framing for why sequential Bayesian tests avoid the p-hacking problem of frequentist sequential designs.

**Peeking at A/B Tests: Why It Matters and What to Do About It** — Johari et al. (2017)
The statistical paper behind the "always-valid" Bayesian testing arguments. Explains the inflation problem that the 0.95 threshold and minimum-weeks constraint in this portfolio are designed to address.

### Courses

**Bayesian Methods for A/B Testing** — Chris Stucchio (blog series, free)
Stucchio's series specifically covers the Beta-Binomial sequential test with business decision framing. Translates directly to the monitoring system architecture.
→ https://www.chrisstucchio.com/blog/2014/bayesian_ab_decision_rule.html

---

## 7. ROPE — Region of Practical Equivalence

**Where used:** `P(|diff| < 0.02) > 0.80` check in `bayesian_monitoring_system.py`; `in_rope = np.logical_and(diff > -0.02, diff < 0.02).mean()` in `bayesian_ab_test_implementation.py`; ROPE visualization in `streamlit_dashboard.py`.

### Books

**Doing Bayesian Data Analysis** — Kruschke, Chapter 12
ROPE is Kruschke's original contribution. This chapter is the definitive reference. The ±2pp choice in this portfolio should be revisited against the guidance in Section 12.2 on how to set ROPE bounds from domain knowledge.

**Introduction to Bayesian Inference for Psychology** — Etz & Vandekerckhove (2018, Psychonomic Bulletin)
A concise review of ROPE and HDI-based decision-making that is more accessible than Kruschke's textbook for communicating the framework to stakeholders.

---

## 8. Thompson Sampling & Adaptive Allocation

**Where used:** `_thompson_sampling_allocation()` in `bayesian_monitoring_system.py` — active from week 5 onward; uses posterior Beta samples to up-weight better-performing arms.

### Books

**Bandit Algorithms for Website Optimization** — John Myles White (O'Reilly, 2012)
Short, practical book covering Thompson Sampling, UCB, and epsilon-greedy in detail with Python code. Chapter 4 covers Thompson Sampling specifically in the A/B test context. Best entry point.

**Reinforcement Learning: An Introduction** — Sutton & Barto (2nd ed., 2018), Chapter 2
The k-armed bandit formulation that Thompson Sampling solves. Free online:
→ http://incompleteideas.net/book/the-book-2nd.html

### Papers

**Thompson Sampling for Contextual Bandits with Linear Payoffs** — Agrawal & Goyal (2013, ICML)
The paper that re-established Thompson Sampling's theoretical guarantees after decades of neglect. Not required for application but important if extending to contextual allocation (e.g., allocating differently per risk tier).

**An Empirical Evaluation of Thompson Sampling** — Chapelle & Li (2011, NeurIPS)
Practical benchmarking study. Shows Thompson Sampling matches or beats UCB in most realistic A/B testing scenarios — the justification for using it from week 5 rather than week 1.

---

## 9. Causal Inference — DAGs, Collider Bias, G-computation, IPW

**Where used:** `proper_causal_inference.py` (primary), `full_dataset_causal_validation.py` (ChurnDataPipeline) — causal effect estimation using only exogenous confounders (SeniorCitizen, Dependents, Partner, Gender); collider bias exclusion of tenure/MonthlyCharges/InternetService; G-computation and IPW propensity scoring.

### Books

**Causal Inference: The Mixtape** — Scott Cunningham (free online, 2021)
Chapter 3–4 cover DAGs and the backdoor criterion that determines valid adjustment sets (why tenure is excluded as a collider). Chapter 9 covers propensity score methods (IPW). Written for social scientists but directly applicable.
→ https://mixtape.scunning.com/

**The Book of Why** — Judea Pearl & Dana Mackenzie (2018)
The accessible introduction to Pearl's causal hierarchy (association → intervention → counterfactual) and why collider bias occurs. Not technical but builds the right intuition for why the confounder selection in `proper_causal_inference.py` is non-obvious.

**Causal Inference in Statistics: A Primer** — Pearl, Glymour, Jewell (2016)
The compact technical companion to *The Book of Why*. Chapter 3 on the backdoor criterion and Chapter 4 on intervention vs. conditioning are the key sections. Essential for understanding why conditioning on tenure inflates the causal effect estimate.

**What If** — Hernán & Robins (free online, 2020)
The epidemiological causal inference textbook. Chapters 2–3 cover g-computation and IPW rigorously. The `G-computation` function in `proper_causal_inference.py` is a direct implementation of the procedure in Chapter 2.
→ https://www.hsph.harvard.edu/miguel-hernan/causal-inference-book/

### Courses

**Causal Diagrams: Draw Your Assumptions Before Your Conclusions** — Harvard / edX (Miguel Hernán, free)
A short course (4–5 hours) specifically on DAG construction and reading. Directly applicable to the confounder analysis in Phase 2. The only course that explicitly covers collider bias through DAGs.
→ https://www.edx.org/course/causal-diagrams-draw-your-assumptions-before-your

**Causal Inference Bootcamp** — Matt Masten / Marginal Revolution University (free)
Shorter video series covering DAGs, backdoor criterion, and identification strategies. Good complement to Cunningham.

---

## 10. Bayesian Power Analysis & Sample Size

**Where used:** `power_analysis_experiments.py` (Phase 3) — Monte Carlo simulation of posterior distributions to estimate detection probability at given N; `monte_carlo_simulation.py` (Phase 3).

### Books

**Statistical Rethinking** — McElreath, Chapter 16 (2nd ed.)
The "Power and Sample Size" chapter in McElreath is explicitly Bayesian and simulation-based — the same approach used in `power_analysis_experiments.py`. He argues strongly against analytic power formulas in hierarchical settings and for the simulation approach used here.

**Bayesian Data Analysis (BDA3)** — Gelman et al., Chapter 8
Section 8.3 on posterior predictive model checking and design analysis. BDA3's approach to power is framed as "what data will I likely see?" rather than frequentist rejection probability.

### Papers

**Beyond Power Calculations: Assessing Type S (Sign) and Type M (Magnitude) Errors** — Gelman & Carlin (2014, Perspectives on Psychological Science)
Argues that traditional power analysis asks the wrong question; Type M (magnitude) error is more relevant in business A/B tests. Directly relevant to why the simulation approach in Phase 3 reports full posterior distributions rather than a single power number.

---

## Suggested Study Path

For someone new to the Bayesian stack used in this portfolio, the following sequence minimises redundancy and builds intuition before formalism:

1. **McElreath** *Statistical Rethinking* (full book or lecture series) — covers items 1, 2, 3, 4, 5, 7, 10 with a unified framework
2. **Kruschke** *Doing Bayesian Data Analysis* Ch 5–6, 11–12 — adds ROPE / stopping rule depth (items 1, 6, 7)
3. **Cunningham** *Causal Inference: The Mixtape* Ch 3–4, 9 — covers all of item 9
4. **Davidson-Pilon** *Probabilistic Programming and Bayesian Methods for Hackers* — PyMC syntax and MCMC practice (item 3)
5. **White** *Bandit Algorithms for Website Optimization* — Thompson Sampling in context (item 8)

Items 4 (ArviZ), 5 (hierarchical models in PyMC), and 9 (Hernán & Robins for G-computation) can be read in parallel once the McElreath foundation is in place.

---

*Last updated: March 2026 | Telco Churn Portfolio — Phase 2–4 methodology reference*
