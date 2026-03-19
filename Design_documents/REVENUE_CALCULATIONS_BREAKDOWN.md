# Revenue at Stake Calculations

---

## Input Parameters

| Parameter | Value | Source |
|-----------|-------|--------|
| Total customers in dataset | 7,042 | churn_prediction.csv |
| Total churners (actual) | 1,869 | Actual_Churn column |
| Total retained | 5,173 | Dataset |
| Actual churn rate | 26.5% | 1,869 / 7,042 |
| Average monthly revenue | $74.44 | Mean of MonthlyCharges (churners) |
| Month-to-month contracts | 88.5% | 1,655 / 1,869 |
| Electronic check users | 57.3% | 1,071 / 1,869 |
| Average tenure | 18.0 months | Mean tenure (churners) |
| Average LTV assumption | 11 months | Conservative estimate |

---

## Revenue Calculations

### 1. Monthly Revenue at Risk

```
Monthly Revenue at Risk = Total Churners × Average Monthly Revenue
                       = 1,869 × $74.44
                       = $139,130.85
                       ≈ $139,131
```

This represents total monthly recurring revenue from all 1,869 actual churners.

---

### 2. Annualized Churn Loss

```
Monthly churner revenue = 1,869 × $74.44 = $139,131
Annual loss = $139,131 × 12 months
            = $1,669,572
            ≈ $1.67M
```

If we continue to lose 1,869 customers like this annually, we lose $1.67M per year in recurring revenue.

---

### 3. LTV Loss Calculation

Using 11-month average LTV:

```
LTV per churner = $74.44/month × 11 months
                = $818.85

Total LTV loss = 1,869 churners × $818.85
               = $1,530,438.65
               ≈ $1.53M
```

Total customer lifetime value lost from these 1,869 churners.

---

## Summary Table

| Metric | Value | Calculation |
|--------|-------|-------------|
| **Total Customers** | 7,042 | Full dataset |
| **Total Churners** | 1,869 | Actual_Churn = Yes |
| **Total Retained** | 5,173 | Actual_Churn = No |
| **Churn Rate** | 26.5% | 1,869 / 7,042 |
| **Monthly Revenue/Churner** | $74.44 | Mean MonthlyCharges |
| **Monthly Revenue at Risk** | **$139,131** | 1,869 × $74.44 |
| **Annual Churn Loss** | **~$1.67M** | $139,131 × 12 |
| **Per-Churner LTV** | $818.85 | $74.44 × 11 months |
| **Total LTV Loss** | **~$1.53M** | 1,869 × $818.85 |
| **Month-to-Month %** | 88.5% | 1,655 / 1,869 |
| **Electronic Check %** | 57.3% | 1,071 / 1,869 |

---

## Segment Breakdown

### Contract Type (Churners)

```
Month-to-month: 1,655 (88.5%) × $74.44 = $123,198/month
One year:         166 ( 8.9%) × $74.44 =  $12,357/month
Two year:          48 ( 2.6%) × $74.44 =   $3,573/month
Total:          1,869                   = $139,128/month
```

### Payment Method (Churners)

```
Electronic check:      1,071 (57.3%) × $74.44 = $79,725/month
Mailed check:            308 (16.5%) × $74.44 = $22,927/month
Bank transfer (auto):    258 (13.8%) × $74.44 = $19,205/month
Credit card (auto):      232 (12.4%) × $74.44 = $17,270/month
Total:                 1,869                   = $139,127/month
```

---

## Business Implications

**Annual revenue at risk:** $1.67M
**Addressable with interventions:** Potentially 30–60% reduction
**Conservative savings:** $500K–$1M annually

### Target Segments

1. **Month-to-month (88.5%):** $123K/month at risk
2. **Electronic check (57.3%):** $80K/month at risk
3. **Overlap:** Significant portion in both categories

### Intervention Impact

```
If we reduce churn by 10 percentage points (26.5% → 16.5%):
- Customers saved: 7,042 × 0.10 = 704 customers
- Annual savings: 704 × $74.44 × 12 = $629K

If we reduce churn by 15 percentage points (26.5% → 11.5%):
- Customers saved: 7,042 × 0.15 = 1,056 customers
- Annual savings: 1,056 × $74.44 × 12 = $944K
```

---

**Data Source:** churn_prediction.csv
**Analysis Date:** March 2026
**Total Records:** 7,042
**Actual Churners:** 1,869
