"""
Power Analysis Diagnostic Tool
Run this to diagnose why you're getting nan values

This will show you:
1. What power is actually being achieved
2. What sample sizes you need
3. If there's an issue with effect sizes
"""

import numpy as np
import pandas as pd
from scipy import stats

print("="*80)
print("POWER ANALYSIS DIAGNOSTIC")
print("="*80)

# Your experiment parameters
baseline_churn = 0.609  # Control group
t2_churn = 0.459        # T2 (15% reduction)
effect_size = baseline_churn - t2_churn  # Should be 0.15

print(f"\nEffect Size Check:")
print(f"  Baseline (Control): {baseline_churn:.1%}")
print(f"  Treatment 2: {t2_churn:.1%}")
print(f"  Absolute effect: {effect_size:.1%}")
print(f"  Relative effect: {effect_size/baseline_churn:.1%}")

# Test different sample sizes
print(f"\n{'Sample Size':<15} {'Total N':<10} {'Power (Bayesian)':<20} {'Power (Frequentist)':<20}")
print("-"*70)

sample_sizes = [50, 75, 100, 150, 200, 300, 400]

for n in sample_sizes:
    # Bayesian simulation (simplified)
    # Run 100 quick simulations
    bayesian_detections = 0
    freq_detections = 0
    
    for _ in range(100):
        # Generate data
        control = np.random.binomial(1, baseline_churn, n)
        treatment = np.random.binomial(1, t2_churn, n)
        
        # Bayesian approach
        control_alpha = 2 + control.sum()
        control_beta = 2 + (n - control.sum())
        treatment_alpha = 2 + treatment.sum()
        treatment_beta = 2 + (n - treatment.sum())
        
        # Sample posteriors
        control_samples = np.random.beta(control_alpha, control_beta, 1000)
        treatment_samples = np.random.beta(treatment_alpha, treatment_beta, 1000)
        
        # Check if we detect >10% reduction with >90% probability
        diff = control_samples - treatment_samples
        prob_superior = (diff > 0.10).mean()
        
        if prob_superior > 0.90:
            bayesian_detections += 1
        
        # Frequentist approach
        obs = np.array([
            [control.sum(), n - control.sum()],
            [treatment.sum(), n - treatment.sum()]
        ])
        
        chi2, p_value, _, _ = stats.chi2_contingency(obs)
        
        if p_value < 0.05 and treatment.mean() < control.mean():
            freq_detections += 1
    
    bayesian_power = bayesian_detections / 100
    freq_power = freq_detections / 100
    
    marker = "✓" if bayesian_power >= 0.90 else "✗" if bayesian_power < 0.80 else "~"
    
    print(f"{n:<15} {n*4:<10} {bayesian_power:>8.1%} {marker:<11} {freq_power:>8.1%}")

print("\n" + "="*80)
print("INTERPRETATION:")
print("="*80)

print("""
✓ = Achieves 90%+ power (recommended)
~ = Achieves 80-89% power (acceptable)
✗ = Below 80% power (underpowered)

If ALL tested sample sizes show ✗:
  → The effect size (15%) may be too small to detect reliably
  → Consider larger sample sizes (300-500 per arm)
  → Or adjust effect size expectations

If you see ✓ for some sample sizes:
  → Use the smallest n with ✓
  → That's your optimal sample size
""")

# Calculate required sample size analytically
print("\n" + "="*80)
print("ANALYTICAL CALCULATION:")
print("="*80)

p1 = baseline_churn
p2 = t2_churn
pooled = (p1 + p2) / 2

# For 90% power, alpha = 0.05, two-tailed
z_alpha = 1.96
z_beta = 1.28  # For 90% power

n_required = 2 * ((z_alpha + z_beta)**2 * pooled * (1 - pooled)) / (p1 - p2)**2

print(f"\nFor 90% power to detect {effect_size:.1%} effect:")
print(f"  Required n per arm: {n_required:.0f}")
print(f"  Total N: {n_required * 4:.0f}")
print(f"  Total cost (at $75/customer): ${n_required * 4 * 75:,.0f}")

print("\n" + "="*80)
print("RECOMMENDATION:")
print("="*80)

if n_required > 200:
    print(f"\n⚠️ Required sample size ({n_required:.0f}) is large!")
    print(f"\n   Options:")
    print(f"   1. Accept lower power (80%) with n=150-175")
    print(f"   2. Increase sample size to n={int(n_required/10)*10}")
    print(f"   3. Focus on larger effect sizes (20% instead of 15%)")
else:
    print(f"\n✓ Use n={int(n_required/10)*10} per arm (rounded up)")
    print(f"  This gives 90%+ power for detecting 15% reduction")

print("\n" + "="*80)
