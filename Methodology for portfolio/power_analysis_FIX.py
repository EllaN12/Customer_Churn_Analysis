"""
FIX for power_analysis_experiments.py

Replace the sample_size_sensitivity method with this fixed version
"""

def sample_size_sensitivity(self, experiment='early_tenure'):
    """
    Test different sample sizes to find optimal
    FIXED: Handles case where no sample size achieves 90% power
    """
    print("\n" + "="*80)
    print("SAMPLE SIZE SENSITIVITY ANALYSIS")
    print("="*80)
    
    sample_sizes = [50, 75, 100, 125, 150, 200]
    power_results = []
    
    for n in sample_sizes:
        print(f"\nTesting n={n} per arm...")
        
        if experiment == 'early_tenure':
            df_power, _ = self.simulate_experiment_1_early_tenure(
                n_per_arm=n, 
                n_simulations=200  # Reduced for speed
            )
            
            power_results.append({
                'sample_size': n,
                'total_n': n * 4,
                'T2_power': df_power.loc[1, 'Bayesian_Power'],
                'cost_per_experiment': n * 4 * 75  # Assume avg cost $75
            })
    
    df_sensitivity = pd.DataFrame(power_results)
    
    # FIXED: Better recommendation logic
    print("\n" + "="*60)
    print("SAMPLE SIZE SENSITIVITY RESULTS")
    print("="*60)
    print(df_sensitivity.to_string(index=False))
    
    # Visualize
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # Power vs sample size
    ax = axes[0]
    ax.plot(df_sensitivity['sample_size'], df_sensitivity['T2_power'], 
           marker='o', linewidth=3, markersize=10, color='steelblue')
    ax.axhline(0.8, color='green', linestyle='--', linewidth=2, label='80% power')
    ax.axhline(0.9, color='blue', linestyle='--', linewidth=2, label='90% power')
    ax.set_xlabel('Sample Size per Arm', fontsize=12)
    ax.set_ylabel('Statistical Power', fontsize=12)
    ax.set_title('Power vs Sample Size (T2: 15% reduction)', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_ylim(0, 1)
    
    # Cost vs power
    ax = axes[1]
    ax.plot(df_sensitivity['cost_per_experiment'], df_sensitivity['T2_power'],
           marker='s', linewidth=3, markersize=10, color='coral')
    ax.axhline(0.8, color='green', linestyle='--', linewidth=2, alpha=0.5)
    ax.axhline(0.9, color='blue', linestyle='--', linewidth=2, alpha=0.5)
    ax.set_xlabel('Total Experiment Cost ($)', fontsize=12)
    ax.set_ylabel('Statistical Power', fontsize=12)
    ax.set_title('Power vs Cost Trade-off', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.set_ylim(0, 1)
    
    plt.tight_layout()
    plt.savefig('Results/sample_size_sensitivity.png', dpi=300, bbox_inches='tight')
    print("\n✓ Saved: Results/sample_size_sensitivity.png")
    plt.close()
    
    # FIXED: Smart recommendation logic
    print("\n" + "="*60)
    print("RECOMMENDATION:")
    print("="*60)
    
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
        # No sample size achieves 90% power - recommend highest power option
        max_power_row = df_sensitivity.loc[df_sensitivity['T2_power'].idxmax()]
        max_n = int(max_power_row['sample_size'])
        max_power = max_power_row['T2_power']
        
        print(f"⚠️ No tested sample size achieves 90% power")
        print(f"   Maximum power achieved: {max_power:.1%} (with n={max_n} per arm)")
        print(f"\n   Options:")
        print(f"   1. Accept {max_power:.1%} power with n={max_n} per arm")
        print(f"      Total: {max_n * 4}, Cost: ${max_n * 4 * 75:,}")
        
        # Check if any achieve 80% power
        good_power_samples = df_sensitivity[df_sensitivity['T2_power'] >= 0.80]
        if len(good_power_samples) > 0:
            min_good_n = good_power_samples['sample_size'].min()
            min_good_power = good_power_samples[good_power_samples['sample_size'] == min_good_n]['T2_power'].values[0]
            print(f"   2. Use n={min_good_n} for {min_good_power:.1%} power (acceptable)")
            print(f"      Total: {min_good_n * 4}, Cost: ${min_good_n * 4 * 75:,}")
        
        # Suggest larger sample size
        suggested_n = int(max_n * 1.5)
        print(f"   3. Test larger sample: n={suggested_n} per arm (recommended)")
        print(f"      (Rerun with larger sample sizes in the list)")
    
    return df_sensitivity


# USAGE:
# Replace the sample_size_sensitivity method in your ExperimentPowerAnalysis class
# with the code above
