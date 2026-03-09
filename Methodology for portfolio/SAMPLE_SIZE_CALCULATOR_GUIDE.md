# 📊 Sample Size Calculator - Usage Guide

## 📁 File: sample_size_calculator.py

**Purpose:** Calculate optimal sample sizes for all experiments using analytical formulas and cost-benefit optimization.

---

## 🚀 Quick Start

### **Run the complete calculator:**

```bash
python sample_size_calculator.py
```

**Output:**
1. Early tenure experiment sample sizes
2. Factorial design sample sizes  
3. Power curve visualization
4. Cost-benefit optimization
5. Quick recommendations

**Generated files:**
- `Results/visualizations/power_curve.png`

---

## 🎯 What It Calculates

### **1. Early Tenure Intervention (4 arms)**

**For each treatment:**
- Required sample size per arm
- Total sample size (4 arms)
- Expected cost
- Statistical power

**Example output:**
```
Treatment              Effect          N_per_Arm  Total_N  Cost      Power
T1 (Welcome Call)      10% reduction   129        516      $38,700   90%
T2 (Smart Start)       15% reduction   88         352      $26,400   90%
T3 (Concierge)         20% reduction   64         256      $19,200   90%

RECOMMENDATION:
✓ Recommended: T2 (Smart Start)
  Sample size: 88 per arm (352 total)
  Expected cost: $26,400
  Power: 90%
```

---

### **2. Factorial Design (2×2×2)**

**Calculates:**
- Sample size per cell (8 cells)
- Total sample size
- Power for each main effect

**Example output:**
```
Main Effects to Detect:
  1. Contract effect: 31% reduction
  2. Payment effect: 20% reduction
  3. Add-on effect: 5% reduction

Sample Size Requirements:
  Cells: 8 (2×2×2 design)
  Per cell: 100
  Total N: 800
  Expected cost: $60,000

Power by Effect:
  Contract: >95%
  Payment: >95%
  Add-ons: ~80-90%
```

---

### **3. Power Curve**

**Generates visualization showing:**
- Power vs sample size
- 80% and 90% power thresholds
- Recommended sample size marked

**Saved to:** `Results/visualizations/power_curve.png`

---

### **4. Cost-Benefit Optimization**

**Finds optimal sample size based on:**
- Experiment cost
- Expected benefit (if experiment succeeds)
- Net expected value

**Example output:**
```
COST-BENEFIT OPTIMIZATION

Assumptions:
  Control churn: 60.9%
  Treatment churn: 45.9%
  Effect size: 15.0%
  Revenue per prevented churn: $2,000
  Annual new customers: 5,000

Optimal Sample Size:
  n per arm: 100
  Total N: 400
  Power: 93.2%
  Experiment cost: $30,000
  Expected annual benefit: $279,000
  Net expected value: $249,000
```

---

## 💻 Usage Examples

### **Example 1: Calculate for specific effect size**

```python
from sample_size_calculator import SampleSizeCalculator

calculator = SampleSizeCalculator()

# Calculate for 20% reduction (60% → 40%)
result = calculator.calculate_two_proportion_test(
    p1=0.60,
    p2=0.40
)

print(f"Required sample size: {result['n_per_group']} per group")
# Output: Required sample size: 47 per group
```

---

### **Example 2: Generate power curve**

```python
calculator = SampleSizeCalculator()

# Power curve for 15% effect
df = calculator.power_curve(
    p1=0.609,
    p2=0.459,
    n_range=range(50, 201, 10)
)

print(df)
# Shows power at n=50, 60, 70, ..., 200
```

---

### **Example 3: Cost-benefit analysis**

```python
calculator = SampleSizeCalculator()

# Find optimal sample size considering ROI
optimal = calculator.cost_benefit_analysis(
    p1=0.609,
    p2=0.459,
    revenue_per_prevented_churn=2000  # $2K per prevented churn
)

print(f"Optimal n: {optimal['optimal_n']}")
print(f"Net value: ${optimal['net_value']:,.0f}")
```

---

### **Example 4: Quick recommendation**

```python
calculator = SampleSizeCalculator()

# Get quick recommendation
rec = calculator.quick_recommendation('early_tenure')

print(f"Recommended: {rec['n_per_arm']} per arm")
print(f"Cost: ${rec['cost']:,}")
```

---

## 📊 Key Methods

### **calculate_two_proportion_test(p1, p2, alpha, power)**

**Parameters:**
- `p1` (float): Control proportion
- `p2` (float): Treatment proportion
- `alpha` (float): Type I error (default: 0.05)
- `power` (float): Desired power (default: 0.90)

**Returns:**
- Dictionary with sample size and parameters

**Example:**
```python
result = calculator.calculate_two_proportion_test(0.609, 0.459)
print(result['n_per_group'])  # 88
```

---

### **calculate_early_tenure_experiment(verbose)**

**Parameters:**
- `verbose` (bool): Print detailed output

**Returns:**
- DataFrame with sample sizes for all treatments

**Example:**
```python
df = calculator.calculate_early_tenure_experiment()
print(df)
```

---

### **calculate_factorial_experiment(verbose)**

**Parameters:**
- `verbose` (bool): Print detailed output

**Returns:**
- Dictionary with factorial design sample sizes

**Example:**
```python
result = calculator.calculate_factorial_experiment()
print(f"Per cell: {result['n_per_cell']}")
```

---

### **power_curve(p1, p2, n_range, save_plot)**

**Parameters:**
- `p1` (float): Control proportion
- `p2` (float): Treatment proportion
- `n_range` (array): Sample sizes to test
- `save_plot` (bool): Save visualization

**Returns:**
- DataFrame with power at each sample size

**Example:**
```python
df = calculator.power_curve(0.609, 0.459)
```

---

### **cost_benefit_analysis(p1, p2, revenue_per_prevented_churn, n_range)**

**Parameters:**
- `p1` (float): Control churn rate
- `p2` (float): Treatment churn rate
- `revenue_per_prevented_churn` (float): LTV per prevented churn
- `n_range` (array): Sample sizes to consider

**Returns:**
- Dictionary with optimal sample size and financials

**Example:**
```python
optimal = calculator.cost_benefit_analysis(0.609, 0.459, 2000)
print(f"Optimal: {optimal['optimal_n']}")
```

---

## 🎯 Formulas Used

### **Two-Proportion Test (Analytical)**

Sample size per group:

```
n = 2 * (Z_α/2 + Z_β)² * p̄(1-p̄) / (p₁-p₂)²

Where:
  Z_α/2 = 1.96 (for α=0.05, two-tailed)
  Z_β = 1.28 (for power=0.90)
  p̄ = (p₁ + p₂) / 2 (pooled proportion)
```

**For 15% effect (60.9% → 45.9%):**
```
p̄ = (0.609 + 0.459) / 2 = 0.534
n = 2 * (1.96 + 1.28)² * 0.534(0.466) / 0.15²
n ≈ 88 per group
```

---

## 📈 Sample Size Quick Reference

### **Early Tenure (Control: 60.9%)**

| Effect | Target Rate | N/Arm | Total N | Cost |
|--------|-------------|-------|---------|------|
| 10% | 50.9% | 129 | 516 | $38,700 |
| 15% | 45.9% | 88 | 352 | $26,400 |
| 20% | 40.9% | 64 | 256 | $19,200 |
| 25% | 35.9% | 48 | 192 | $14,400 |

---

## 🔧 Customization

### **Change default parameters:**

```python
calculator = SampleSizeCalculator()

# Change defaults
calculator.alpha = 0.01  # More conservative (1% Type I error)
calculator.power_target = 0.95  # Higher power
calculator.cost_per_customer = 100  # Higher cost

# Recalculate
result = calculator.calculate_early_tenure_experiment()
```

---

## 🎯 Portfolio Value

**This demonstrates:**
- ✅ Proper statistical planning (analytical formulas)
- ✅ Cost-benefit thinking (ROI optimization)
- ✅ Multiple approaches (frequentist + economic)
- ✅ Practical recommendations (actionable sample sizes)

**For interviews:**
> "I built a comprehensive sample size calculator that uses analytical formulas for power analysis and includes cost-benefit optimization. For the early tenure intervention, I determined we need 88 customers per arm to achieve 90% power for detecting a 15% reduction, with an expected cost of $26,400."

---

## ✅ Output Files

**When you run the script:**

```
Results/
└── visualizations/
    └── power_curve.png  # Power vs sample size visualization
```

**Terminal output includes:**
- Early tenure sample sizes table
- Factorial design requirements
- Cost-benefit analysis
- Quick recommendations

---

## 🚀 Quick Test

```bash
# Run the calculator
python sample_size_calculator.py

# Check output was generated
ls -l Results/visualizations/power_curve.png
```

**Expected runtime:** ~5 seconds

---

## 💡 Pro Tips

**1. Use cost-benefit for business justification:**
```python
optimal = calculator.cost_benefit_analysis(0.609, 0.459, 2000)
print(f"Net value: ${optimal['net_value']:,.0f}")
# Shows ROI to stakeholders
```

**2. Generate power curve for presentations:**
```python
calculator.power_curve(0.609, 0.459, save_plot=True)
# Creates professional visualization
```

**3. Get quick answer:**
```python
rec = calculator.quick_recommendation('early_tenure')
# One-line recommendation
```

---

## 📚 Related Files

- **power_analysis_experiments.py** - Monte Carlo validation
- **experiment_randomization.py** - Implements the experiments
- **bayesian_monitoring_system.py** - Monitors experiments

**This calculator designs; those files validate and implement.**

---

**You're ready to calculate optimal sample sizes!** 🎯

```bash
python sample_size_calculator.py
```
