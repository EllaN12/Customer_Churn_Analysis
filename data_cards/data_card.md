# Data Card — Telco Customer Churn

**Project:** `Customer_Churn_Analysis`  
**Owner:** Ella Ndalla (ndallaella@gmail.com)  
**Profiling:** pandas profile of the committed data in this repository — 1 table(s)

A widely used telecommunications customer dataset: 7,043 subscribers with account, service, billing, and demographic attributes plus a binary churn flag. Used for churn prediction, Bayesian causal validation, and experimental design.

## Provenance

- **Source:** Kaggle / IBM Sample Data — Telco Customer Churn
- **Link:** https://www.kaggle.com/datasets/blastchar/telco-customer-churn
- **Snapshot:** IBM sample dataset, circa 2018
- **License / terms:** Published by IBM as sample data and redistributed on Kaggle for public use. Commonly treated as freely usable for education and research; verify terms before commercial use.

### Collection

A fictionalized extract modeled on a telecommunications CRM, distributed by IBM as demonstration data for analytics tooling. It is a single flat snapshot with no temporal dimension beyond the `tenure` field — there is no event log, so churn timing cannot be reconstructed.

### Maintenance

Static sample dataset; IBM has not versioned it. No refresh path exists in this project.

## Labeling

`Churn` (Yes/No) is a system-of-record status flag at snapshot time, not a human annotation. Profiled churn rate is 26.54% (1,869 of 7,043), matching the project's stated baseline. The label carries no date, so 'churned' means 'had churned by the snapshot', which is what makes `tenure` a collider on the causal path.

## Preprocessing

PySpark EDA; SMOTE oversampling for class balance before H2O AutoML training. For causal work, adjustment is restricted to exogenous pre-treatment demographics (SeniorCitizen, Dependents, Partner, Gender) — tenure, contract type, payment method, and charges are deliberately excluded as collider, co-treatment, and mediator respectively.

## Splits

Standard train/test split for the predictive phase with SMOTE applied to training only. The causal and experimental phases do not split; they estimate on the full table and then design prospective randomized tests with stratified randomization.

## Sensitive & Personal Data

Contains customer-level demographics — gender, senior citizen status, partner and dependent status — alongside billing amounts. customerID is a surrogate key with no external meaning. Because these demographics appear in BOTH the predictive feature set and the causal adjustment set, model-scored retention offers could distribute unevenly across protected groups.

## Recommended Uses

- Churn modeling under class imbalance.
- Demonstrating collider bias detection and correction in observational causal analysis.

## Discouraged Uses

- Transferring coefficients or churn drivers to a real telco — the data is fictionalized.
- Using demographic effects to target or price offers.

## Known Issues, Skews & Gaps

- `TotalCharges` is stored as TEXT, not numeric, because 11 rows contain a blank string instead of a value. All 11 are customers with tenure = 0 (never billed). A naive pd.to_numeric or astype(float) will raise, and a silent coerce turns them into NaN — worth handling explicitly since these are exactly the new customers the early-tenure hypothesis concerns.
- No other missing values: 0% nulls across all 21 columns, and no duplicate rows.
- Service columns encode 'No internet service' / 'No phone service' as a third level rather than as missing — 21.67% of rows for the six internet-dependent columns. One-hot encoding without collapsing these creates perfectly collinear indicators.
- Class imbalance is moderate (26.54% churn), which SMOTE addresses but at the cost of probability calibration.
- `tenure` ranges 0-72 months with 73 distinct values, so the dataset spans at most six years of customer relationships — long-tenure behavior is unobserved.

## Profiled Schema

### `WA_Fn-UseC_-Telco-Customer-Churn — raw Telco extract`

**Rows:** 7,043  
**Columns:** 21  
**Duplicate rows:** 0  
**Source file:** `Customer_Churn_Analysis/Raw_data/WA_Fn-UseC_-Telco-Customer-Churn.csv.xls`

> Full file profiled. Despite the .xls extension the file is CSV.

| Field | Type | Null % | Distinct | Range / top values |
|---|---|---:|---:|---|
| `customerID` | object | 0.00 | 7,043 |  |
| `gender` | object | 0.00 | 2 | Male 50.48% · Female 49.52% |
| `SeniorCitizen` | int64 | 0.00 | 2 | min 0 · median 0 · max 1 · mean 0.1621 |
| `Partner` | object | 0.00 | 2 | No 51.7% · Yes 48.3% |
| `Dependents` | object | 0.00 | 2 | No 70.04% · Yes 29.96% |
| `tenure` | int64 | 0.00 | 73 | min 0 · median 29 · max 72 · mean 32.37 |
| `PhoneService` | object | 0.00 | 2 | Yes 90.32% · No 9.68% |
| `MultipleLines` | object | 0.00 | 3 | No 48.13% · Yes 42.18% · No phone service 9.68% |
| `InternetService` | object | 0.00 | 3 | Fiber optic 43.96% · DSL 34.37% · No 21.67% |
| `OnlineSecurity` | object | 0.00 | 3 | No 49.67% · Yes 28.67% · No internet service 21.67% |
| `OnlineBackup` | object | 0.00 | 3 | No 43.84% · Yes 34.49% · No internet service 21.67% |
| `DeviceProtection` | object | 0.00 | 3 | No 43.94% · Yes 34.39% · No internet service 21.67% |
| `TechSupport` | object | 0.00 | 3 | No 49.31% · Yes 29.02% · No internet service 21.67% |
| `StreamingTV` | object | 0.00 | 3 | No 39.9% · Yes 38.44% · No internet service 21.67% |
| `StreamingMovies` | object | 0.00 | 3 | No 39.54% · Yes 38.79% · No internet service 21.67% |
| `Contract` | object | 0.00 | 3 | Month-to-month 55.02% · Two year 24.07% · One year 20.91% |
| `PaperlessBilling` | object | 0.00 | 2 | Yes 59.22% · No 40.78% |
| `PaymentMethod` | object | 0.00 | 4 | Electronic check 33.58% · Mailed check 22.89% · Bank transfer (automatic) 21.92% |
| `MonthlyCharges` | float64 | 0.00 | 1,585 | min 18.25 · median 70.35 · max 118.8 · mean 64.76 |
| `TotalCharges` | object | 0.00 | 6,531 |  |
| `Churn` | object | 0.00 | 2 | No 73.46% · Yes 26.54% |

---

*Schema, null rates, cardinality, and distributions were computed directly from the committed data. Narrative sections are documented from the project README and source materials.*
