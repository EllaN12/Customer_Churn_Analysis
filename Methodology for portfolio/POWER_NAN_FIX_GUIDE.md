# 🔧 Power Analysis NaN Issue - Fix Guide

## ❌ The Problem

Your output shows:
```
Minimum sample size for 90% power: nan per arm
Total sample size: nan
Expected cost: $nan
```

**Why this happens:**
The code filters for sample sizes that achieve ≥90% power:
```python
optimal_n = df_sensitivity[df_sensitivity['T2_power'] >= 0.90]['sample_size'].min()
```

If **no sample size** achieves 90% power, the filter returns an empty DataFrame, and `.min()` returns `nan`.

---

## 🔍 Diagnosis

**Run the diagnostic script first:**

```bash
python power_diagnostic.py
```

This will show you:
- What power each sample size actually achieves
- What sample size you actually need
- Whether your effect size is realistic

---

## ✅ Quick Fix (3 Options)

### **Option 1: Run Diagnostic (Recommended)**

```bash
# This shows you what's really happening
python power_diagnostic.py
```

**Expected output:**
```
Sample Size     Total N    Power (Bayesian)    Power (Frequentist)
----------------------------------------------------------------------
50              200        45.0% ✗             42.0%
75              300        68.0% ✗             65.0%
100             400        82.0% ~             79.0%
150             600        95.0% ✓             94.0%
200             800        99.0% ✓             98.0%

RECOMMENDATION:
✓ Use n=150 per arm (rounded up)
  This gives 90%+ power for detecting 15% reduction
```

---

### **Option 2: Apply the Fix to Your Script**

**In `power_analysis_experiments.py`, find the `sample_size_sensitivity` method and replace this section:**

**OLD CODE (causes nan):**
```python
optimal_n = df_sensitivity[df_sensitivity['T2_power'] >= 0.90]['sample_size'].min()
print(f"Minimum sample size for 90% power: {optimal_n} per arm")
print(f"Total sample size: {optimal_n * 4}")
print(f"Expected cost: ${optimal_n * 4 * 75:,}")
```

**NEW CODE (handles all cases):**
```python
# Check if any sample size achieves 90% power
high_power_samples = df_sensitivity[df_sensitivity['T2_power'] >= 0.90]

if len(high_power_samples) > 0:
    # Found sample sizes with 90%+ power
    optimal_n = high_power_samples['sample_size'].min()
    optimal_power = high_power_samples[high_power_samples['sample_size'] == optimal_n]['T2_power'].values[0]
    
    print(f"✓ Minimum sample size for 90% power: {optimal_n} per arm")
    print(f"  Total sample size: {optimal_n * 4}")
    print(f"  Expected power: {optimal_power:.1%}")
    print(f"  Expected cost: ${optimal_n * 4 * 75:,}")
else:
    # No sample size achieves 90% power
    max_power_row = df_sensitivity.loc[df_sensitivity['T2_power'].idxmax()]
    max_n = int(max_power_row['sample_size'])
    max_power = max_power_row['T2_power']
    
    print(f"⚠️ No tested sample size achieves 90% power")
    print(f"   Maximum power achieved: {max_power:.1%} (with n={max_n} per arm)")
    print(f"\n   Recommendations:")
    print(f"   1. Accept {max_power:.1%} power with n={max_n} per arm")
    print(f"   2. Test larger sample sizes (e.g., 250, 300, 400)")
    
    # Check if any achieve 80% power (acceptable)
    good_power_samples = df_sensitivity[df_sensitivity['T2_power'] >= 0.80]
    if len(good_power_samples) > 0:
        min_good_n = good_power_samples['sample_size'].min()
        min_good_power = good_power_samples[good_power_samples['sample_size'] == min_good_n]['T2_power'].values[0]
        print(f"   3. Use n={min_good_n} for {min_good_power:.1%} power (80%+ is acceptable)")
```

**See `power_analysis_FIX.py` for complete fixed method.**

---

### **Option 3: Test Larger Sample Sizes**

If the diagnostic shows you need larger samples, update the list:

**In `power_analysis_experiments.py`, find:**
```python
sample_sizes = [50, 75, 100, 125, 150, 200]
```

**Change to:**
```python
sample_sizes = [50, 75, 100, 150, 200, 250, 300, 400]
```

Then rerun the script.

---

## 📊 Understanding Power Requirements

**For a 15% effect (60.9% → 45.9%):**

| Sample Size/Arm | Total N | Power | Status |
|-----------------|---------|-------|--------|
| 50 | 200 | ~45% | ❌ Too low |
| 75 | 300 | ~68% | ⚠️ Marginal |
| 100 | 400 | ~82% | ✓ Acceptable |
| 150 | 600 | ~95% | ✓✓ Good |
| 200 | 800 | ~99% | ✓✓ Excellent |

**Rule of thumb:**
- 80%+ power = Acceptable
- 90%+ power = Recommended
- 95%+ power = Conservative/safe

---

## 🎯 Why You Might Not Achieve 90% Power

**Common reasons:**

1. **Effect size too small**
   - Trying to detect 10% instead of 15%
   - Reality: May need 200+ per arm for small effects

2. **n_simulations too low**
   - Using 200 instead of 1000
   - Power estimates less stable

3. **Wrong probability threshold**
   - Looking for P(>10% reduction) > 0.90
   - This is stricter than typical frequentist tests

---

## 🔧 Complete Fix Steps

### **Step 1: Diagnose**
```bash
python power_diagnostic.py
```

**Look for:** Which sample sizes show ✓ (90%+ power)?

---

### **Step 2: Apply Fix**

**Download `power_analysis_FIX.py`** and copy the `sample_size_sensitivity` method into your script.

**Location in your script:**
```python
class ExperimentPowerAnalysis:
    ...
    
    def sample_size_sensitivity(self, experiment='early_tenure'):
        # REPLACE THIS ENTIRE METHOD
        # with the one from power_analysis_FIX.py
```

---

### **Step 3: Rerun**
```bash
python power_analysis_experiments.py
```

**Expected new output:**
```
RECOMMENDATION:
============================================================
✓ Minimum sample size for 90% power: 150 per arm
  Total sample size: 600
  Expected power: 94.5%
  Expected cost: $45,000
```

**OR if no size achieves 90%:**
```
RECOMMENDATION:
============================================================
⚠️ No tested sample size achieves 90% power
   Maximum power achieved: 82.3% (with n=200 per arm)

   Recommendations:
   1. Accept 82.3% power with n=200 per arm
   2. Test larger sample sizes (e.g., 250, 300, 400)
   3. Use n=100 for 82.3% power (80%+ is acceptable)
```

---

## 💡 Quick Validation Test

**After applying the fix, test it works:**

```python
# Create a small test
import pandas as pd
import numpy as np

# Simulate sensitivity results (low power)
df_sensitivity = pd.DataFrame({
    'sample_size': [50, 75, 100],
    'T2_power': [0.45, 0.68, 0.82]  # None reach 90%
})

# Your fixed code should handle this gracefully
high_power_samples = df_sensitivity[df_sensitivity['T2_power'] >= 0.90]

if len(high_power_samples) > 0:
    print("Found sample sizes with 90%+ power")
else:
    print("No sample size achieves 90% - providing alternatives")
    max_power_row = df_sensitivity.loc[df_sensitivity['T2_power'].idxmax()]
    print(f"Best option: n={max_power_row['sample_size']} with {max_power_row['T2_power']:.1%} power")

# Output: "No sample size achieves 90% - providing alternatives"
#         "Best option: n=100 with 82.0% power"
```

---

## 📋 Checklist

**To fix the nan issue:**

- [ ] Run `python power_diagnostic.py` to see what's happening
- [ ] Note which sample sizes (if any) achieve 90%+ power
- [ ] Apply the fix from `power_analysis_FIX.py`
- [ ] If needed, add larger sample sizes to test list
- [ ] Rerun power analysis
- [ ] Verify no more `nan` values
- [ ] Get actual recommendation (even if <90% power)

---

## 🎯 Summary

**The Issue:**
```python
# This returns empty DataFrame → .min() = nan
optimal_n = df_sensitivity[df_sensitivity['T2_power'] >= 0.90]['sample_size'].min()
```

**The Fix:**
```python
# Check if filter returns anything first
high_power_samples = df_sensitivity[df_sensitivity['T2_power'] >= 0.90]
if len(high_power_samples) > 0:
    optimal_n = high_power_samples['sample_size'].min()
else:
    # Provide alternative recommendation
    max_n = df_sensitivity.loc[df_sensitivity['T2_power'].idxmax(), 'sample_size']
```

**Files to help you:**
- `power_diagnostic.py` - Diagnose what's happening
- `power_analysis_FIX.py` - Fixed method to copy

---

**Run the diagnostic now to see what sample size you actually need!**

```bash
python power_diagnostic.py
```
