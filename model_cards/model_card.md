





# Model Card for Telco Customer Churn — H2O AutoML Ensemble with Bayesian Causal Validation

## Model Details

### Overview
A five-phase pipeline on 7,043 Telco customers x 21 features: PySpark EDA and H2O AutoML prediction, Bayesian causal validation with an explicit collider-bias correction, power-analyzed experimental design, a hierarchical Bayesian A/B testing engine with sequential monitoring, and Docker/GCP Cloud Run deployment. Baseline churn is 26.5%, representing $1.53M of lifetime value at risk. 

### Version

name: 1.0.0  

### Owners

* Ella Ndalla, ndallaella@gmail.com


### Licenses

* MIT

### References

* [https://www.kaggle.com/datasets/blastchar/telco-customer-churn](https://www.kaggle.com/datasets/blastchar/telco-customer-churn)


### Citations

* Ella Ndalla. Telco Customer Churn — H2O AutoML Ensemble with Bayesian Causal Validation. GitHub repository: Customer_Churn_Analysis.



## Considerations

### Users

* Retention / CRM teams (illustrative)

* Data scientists studying causal ML workflows


### Use Cases

* Predicting churn risk to prioritize retention outreach.

* Estimating the causal effect of service add-on bundles on churn.

* Designing and sequentially monitoring randomized retention experiments.


### Limitations

* Predictive accuracy does not imply causal validity — the 93.4% AUC ensemble is not a guide to which interventions will work.

* The corrected causal model conditions ONLY on exogenous pre-treatment demographics (SeniorCitizen, Dependents, Partner, Gender). Tenure is a collider, contract type and payment method are other treatments, and charges are mediators — all are deliberately excluded, and observational limits remain even after correction.

* The strongest signal found (+52pp churn in the first 40 days) is NOT causally identified and requires a randomized experiment before acting on it.

* Static 2018-era Kaggle snapshot from one telco; no temporal validation or drift testing against live data.

* SMOTE oversampling can distort predicted probability calibration.


### Tradeoffs

* The H2O stacked ensemble is markedly more accurate than the PySpark decision tree (93.4% vs 72.0% AUC) at the cost of interpretability and heavier serving infrastructure.

* High recall on churners (~90.5%) with ~78% precision means a meaningful share of retention spend goes to customers who would have stayed.

* Correcting collider bias moves the add-on effect from -0.2pp to -5.8pp — the methodologically correct estimate is far larger, and the naive one would have led to abandoning a working lever.


### Ethical Considerations

* Risk: Demographic features (gender, senior citizen status, dependents, partner) sit in both the prediction and adjustment sets, so retention offers scored by this model could distribute unevenly across protected groups.
  * Mitigation Strategy: Demographics are used as backdoor-criterion adjustment variables rather than targeting rules; the project culminates in randomized experiments with stratified randomization rather than model-score-driven rollout.

* Risk: Collider bias silently inverting the estimated effect direction.
  * Mitigation Strategy: Collider bias was detected and empirically confirmed via stratification reversal; the corrected specification is the documented centerpiece of the project.

* Risk: Acting on the strong early-tenure correlation without identification.
  * Mitigation Strategy: Explicitly flagged as &#39;requires experiment&#39;; three prioritized randomized tests were designed at 95% Bayesian power with ROPE-based stopping rules.

## Graphics



## Metrics

|Name|Value|
-----|------
|AUC-ROC (H2O Stacked Ensemble)|93.4%|
|AUC-PR (H2O Stacked Ensemble)|96.72%|
|Recall on churners|~90.5%|
|Precision|~78%|
|AUC-ROC (PySpark Decision Tree baseline)|72.0%|
|AUC-PR (PySpark Decision Tree baseline)|52.6%|
|Baseline churn rate|26.5%|
|Causal effect of service add-on bundle (corrected)|-5.8pp, 95% CI [-8.2%, -3.4%]|
|P(add-ons reduce churn by 5%+)|87%|
|Naive (collider-biased) add-on effect|-0.2pp|
|Early tenure &lt;=40 days (correlational)|+52pp — requires experiment|
|Experiment design power|95% Bayesian power, 3 prioritized tests|

