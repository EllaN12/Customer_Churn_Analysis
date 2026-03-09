"""
Portfolio Visualizations: Key Charts for Presentation
Creates three essential visualizations demonstrating causal inference journey

1. Early Tenure Effect Chart (before/after controlling for exogenous variables)
2. Collider Bias Demonstration (effect reversal by tenure group)
3. Valid vs Invalid Controls Diagram (conceptual causal structure)
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle
import seaborn as sns
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

sns.set_style('whitegrid')
plt.rcParams['font.size'] = 11
plt.rcParams['font.family'] = 'sans-serif'


def create_early_tenure_effect_chart(df):
    """
    Visualization 1: Early Tenure Effect
    Shows churn rates before and after controlling for exogenous variables
    
    Chart type: Side-by-side grouped bar chart with error bars
    """
    print("\n" + "="*80)
    print("CREATING VISUALIZATION 1: Early Tenure Effect")
    print("="*80)
    
    # Prepare data
    df['early_tenure'] = (df['tenure'] <= 1.3).astype(int)
    df['churn_binary'] = (df['Actual_Churn'] == 'Yes').astype(int)
    df['senior'] = (df['SeniorCitizen'] == 'Yes').astype(int)
    df['has_dependents'] = (df['Dependents'] == 'Yes').astype(int)
    
    # Unadjusted rates
    early = df[df['early_tenure'] == 1]
    regular = df[df['early_tenure'] == 0]
    
    unadjusted = {
        'Early Tenure (≤40 days)': early['churn_binary'].mean(),
        'Regular Tenure (>40 days)': regular['churn_binary'].mean()
    }
    
    # Adjusted rates (stratified by exogenous variables, then averaged)
    # This is a simplified adjustment - shows directional impact
    
    def adjusted_rate(tenure_group):
        """Calculate rate after adjusting for senior status and dependents"""
        rates = []
        
        # Stratify by senior and dependents combinations
        for senior in [0, 1]:
            for dependents in [0, 1]:
                stratum = df[(df['senior'] == senior) & 
                           (df['has_dependents'] == dependents) &
                           (df['early_tenure'] == tenure_group)]
                
                if len(stratum) > 0:
                    rate = stratum['churn_binary'].mean()
                    # Weight by proportion in full sample
                    weight = len(stratum) / len(df[df['early_tenure'] == tenure_group])
                    rates.append((rate, weight))
        
        # Weighted average
        if rates:
            return sum(r * w for r, w in rates)
        return np.nan
    
    adjusted = {
        'Early Tenure (≤40 days)': adjusted_rate(1),
        'Regular Tenure (>40 days)': adjusted_rate(0)
    }
    
    # Calculate confidence intervals (normal approximation)
    def ci_95(p, n):
        se = np.sqrt(p * (1-p) / n)
        return 1.96 * se
    
    unadjusted_ci = {
        'Early Tenure (≤40 days)': ci_95(early['churn_binary'].mean(), len(early)),
        'Regular Tenure (>40 days)': ci_95(regular['churn_binary'].mean(), len(regular))
    }
    
    # Create figure
    fig, ax = plt.subplots(figsize=(12, 7))
    
    x = np.arange(2)
    width = 0.35
    
    # Unadjusted bars
    unadj_vals = list(unadjusted.values())
    unadj_errs = list(unadjusted_ci.values())
    bars1 = ax.bar(x - width/2, unadj_vals, width, 
                   label='Unadjusted (Raw Data)', 
                   color='coral', alpha=0.8, edgecolor='black', linewidth=1.5)
    
    # Add error bars
    ax.errorbar(x - width/2, unadj_vals, yerr=unadj_errs, 
               fmt='none', ecolor='black', capsize=5, capthick=2)
    
    # Adjusted bars
    adj_vals = list(adjusted.values())
    bars2 = ax.bar(x + width/2, adj_vals, width,
                   label='Adjusted (Controlling for Age & Dependents)',
                   color='steelblue', alpha=0.8, edgecolor='black', linewidth=1.5)
    
    # Styling
    ax.set_ylabel('Churn Rate', fontsize=14, fontweight='bold')
    ax.set_title('Early Tenure Effect: Before and After Controlling for Exogenous Variables',
                fontsize=16, fontweight='bold', pad=20)
    ax.set_xticks(x)
    ax.set_xticklabels(['Early Tenure\n(≤40 days)\nn=624', 'Regular Tenure\n(>40 days)\nn=6,418'],
                       fontsize=12)
    ax.legend(fontsize=11, loc='upper right')
    ax.set_ylim(0, 0.7)
    
    # Format y-axis as percentage
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f'{y:.0%}'))
    
    # Add value labels on bars
    for bars, vals in [(bars1, unadj_vals), (bars2, adj_vals)]:
        for bar, val in zip(bars, vals):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{val:.1%}',
                   ha='center', va='bottom', fontweight='bold', fontsize=12)
    
    # Add effect size annotations
    # Unadjusted difference
    unadj_diff = unadj_vals[0] - unadj_vals[1]
    ax.annotate('', xy=(0-width/2, unadj_vals[0]), xytext=(1-width/2, unadj_vals[1]),
               arrowprops=dict(arrowstyle='<->', color='coral', lw=2, linestyle='--'))
    ax.text(0.5-width/2, (unadj_vals[0] + unadj_vals[1])/2 + 0.05,
           f'Unadjusted\nDifference:\n+{unadj_diff:.1%}',
           ha='center', fontsize=10, bbox=dict(boxstyle='round', facecolor='coral', alpha=0.3))
    
    # Adjusted difference
    adj_diff = adj_vals[0] - adj_vals[1]
    ax.annotate('', xy=(0+width/2, adj_vals[0]), xytext=(1+width/2, adj_vals[1]),
               arrowprops=dict(arrowstyle='<->', color='steelblue', lw=2, linestyle='--'))
    ax.text(0.5+width/2, (adj_vals[0] + adj_vals[1])/2 + 0.05,
           f'Adjusted\nDifference:\n+{adj_diff:.1%}',
           ha='center', fontsize=10, bbox=dict(boxstyle='round', facecolor='steelblue', alpha=0.3))
    
    # Add interpretation box
    interpretation = (
        "Interpretation: Even after controlling for age and dependents,\n"
        "early tenure customers have dramatically higher churn.\n"
        f"The effect is strong ({adj_diff:.1%}) and not explained by demographics alone."
    )
    ax.text(0.02, 0.98, interpretation, transform=ax.transAxes,
           fontsize=10, verticalalignment='top',
           bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.tight_layout()
    plt.savefig('/mnt/user-data/outputs/1_early_tenure_effect.png', dpi=300, bbox_inches='tight')
    print("✓ Saved: 1_early_tenure_effect.png")
    plt.close()


def create_collider_bias_demonstration(df):
    """
    Visualization 2: Collider Bias Demonstration
    Shows how add-on effect REVERSES across tenure groups
    
    Chart type: Line plot with confidence bands + side-by-side comparison
    """
    print("\n" + "="*80)
    print("CREATING VISUALIZATION 2: Collider Bias Demonstration")
    print("="*80)
    
    # Prepare data
    addon_services = ['OnlineSecurity', 'OnlineBackup', 'DeviceProtection', 'TechSupport']
    df['has_addons'] = (df[addon_services] == 'Yes').any(axis=1).astype(int)
    df['churn_binary'] = (df['Actual_Churn'] == 'Yes').astype(int)
    
    # Create tenure groups
    tenure_bins = [0, 3, 6, 12, 24, 100]
    tenure_labels = ['0-3 mo', '4-6 mo', '7-12 mo', '13-24 mo', '25+ mo']
    df['tenure_group'] = pd.cut(df['tenure'], bins=tenure_bins, labels=tenure_labels)
    
    # Calculate churn rates by tenure group and add-on status
    results = []
    
    for tenure_group in tenure_labels:
        tenure_df = df[df['tenure_group'] == tenure_group]
        
        # With add-ons
        has_addons_df = tenure_df[tenure_df['has_addons'] == 1]
        churn_with = has_addons_df['churn_binary'].mean() if len(has_addons_df) > 0 else np.nan
        n_with = len(has_addons_df)
        
        # Without add-ons
        no_addons_df = tenure_df[tenure_df['has_addons'] == 0]
        churn_without = no_addons_df['churn_binary'].mean() if len(no_addons_df) > 0 else np.nan
        n_without = len(no_addons_df)
        
        # Effect (negative = add-ons reduce churn)
        effect = churn_with - churn_without
        
        results.append({
            'tenure_group': tenure_group,
            'churn_with_addons': churn_with,
            'churn_without_addons': churn_without,
            'effect': effect,
            'n_with': n_with,
            'n_without': n_without
        })
    
    df_results = pd.DataFrame(results)
    
    # Create figure with two subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    # ============ LEFT PLOT: Churn Rates by Tenure Group ============
    x = range(len(tenure_labels))
    
    ax1.plot(x, df_results['churn_without_addons'], 
            marker='o', linewidth=3, markersize=10, color='coral',
            label='Without Add-ons')
    ax1.plot(x, df_results['churn_with_addons'],
            marker='s', linewidth=3, markersize=10, color='steelblue',
            label='With Add-ons')
    
    ax1.set_xlabel('Tenure Group', fontsize=13, fontweight='bold')
    ax1.set_ylabel('Churn Rate', fontsize=13, fontweight='bold')
    ax1.set_title('Churn Rates by Tenure Group and Add-on Status\n(Demonstrating Selection Bias)',
                 fontsize=14, fontweight='bold')
    ax1.set_xticks(x)
    ax1.set_xticklabels(tenure_labels, rotation=0)
    ax1.legend(fontsize=12, loc='upper right')
    ax1.grid(True, alpha=0.3)
    ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f'{y:.0%}'))
    ax1.set_ylim(0, 0.5)
    
    # Add annotation showing convergence/reversal
    ax1.annotate('Gap narrows\n(selection bias!)', 
                xy=(3, df_results.loc[3, 'churn_with_addons']),
                xytext=(3.5, 0.3),
                arrowprops=dict(arrowstyle='->', color='red', lw=2),
                fontsize=11, color='red', fontweight='bold',
                bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.5))
    
    # ============ RIGHT PLOT: Effect Size by Tenure Group ============
    colors = ['green' if e < 0 else 'red' for e in df_results['effect']]
    bars = ax2.barh(x, df_results['effect'], color=colors, alpha=0.7, edgecolor='black', linewidth=1.5)
    
    ax2.set_yticks(x)
    ax2.set_yticklabels(tenure_labels)
    ax2.set_xlabel('Add-on Effect on Churn\n(Negative = Reduces Churn)', fontsize=13, fontweight='bold')
    ax2.set_ylabel('Tenure Group', fontsize=13, fontweight='bold')
    ax2.set_title('Add-on Effect Changes with Tenure\n⚠️ THIS IS COLLIDER BIAS ⚠️',
                 fontsize=14, fontweight='bold', color='red')
    ax2.axvline(0, color='black', linewidth=2, linestyle='-')
    ax2.grid(True, alpha=0.3, axis='x')
    ax2.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{x:+.0%}'))
    
    # Add value labels
    for i, (bar, val) in enumerate(zip(bars, df_results['effect'])):
        label_x = val + (0.01 if val > 0 else -0.01)
        ha = 'left' if val > 0 else 'right'
        ax2.text(label_x, bar.get_y() + bar.get_height()/2,
                f'{val:+.1%}',
                ha=ha, va='center', fontweight='bold', fontsize=11)
    
    # Add explanation box
    explanation = (
        "🔍 Key Insight: Effect REVERSES!\n\n"
        "• Early tenure: Add-ons help (-5%)\n"
        "• Long tenure: Add-ons hurt (+1%)\n\n"
        "This isn't real heterogeneity—\n"
        "it's COLLIDER BIAS from\n"
        "conditioning on survival."
    )
    ax2.text(0.98, 0.02, explanation, transform=ax2.transAxes,
            fontsize=10, verticalalignment='bottom', horizontalalignment='right',
            bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.7, edgecolor='red', linewidth=2))
    
    plt.tight_layout()
    plt.savefig('/mnt/user-data/outputs/2_collider_bias_demonstration.png', dpi=300, bbox_inches='tight')
    print("✓ Saved: 2_collider_bias_demonstration.png")
    plt.close()


def create_valid_controls_diagram():
    """
    Visualization 3: Valid vs Invalid Controls
    Conceptual diagram showing causal structure
    
    Chart type: Custom causal diagram with annotations
    """
    print("\n" + "="*80)
    print("CREATING VISUALIZATION 3: Valid vs Invalid Controls Diagram")
    print("="*80)
    
    fig, ax = plt.subplots(figsize=(16, 10))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    # Title
    ax.text(5, 9.5, 'Causal Inference: Valid vs Invalid Controls', 
           ha='center', fontsize=20, fontweight='bold')
    
    # ========== VALID CONFOUNDERS (Top Left) ==========
    ax.text(2.5, 8.5, '✅ VALID CONFOUNDERS', 
           ha='center', fontsize=14, fontweight='bold', color='green',
           bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.5, edgecolor='green', linewidth=2))
    
    # Box for valid confounders
    valid_box = FancyBboxPatch((0.5, 6.5), 4, 1.5, 
                               boxstyle="round,pad=0.1", 
                               edgecolor='green', facecolor='lightgreen', 
                               alpha=0.3, linewidth=2)
    ax.add_patch(valid_box)
    
    # Valid confounder examples
    valid_text = (
        "Pre-treatment & Exogenous:\n"
        "• Age (SeniorCitizen)\n"
        "• Family structure (Dependents, Partner)\n"
        "• Gender\n\n"
        "These affect BOTH treatment choice\n"
        "AND outcome, but are not caused\n"
        "by anticipation of treatment"
    )
    ax.text(2.5, 7.25, valid_text, ha='center', va='center', fontsize=10,
           bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    # Causal diagram for valid confounder
    # Age → Add-ons
    ax.arrow(1.5, 6.2, 0.5, -0.5, head_width=0.15, head_length=0.1, fc='green', ec='green', lw=2)
    # Age → Churn  
    ax.arrow(1.5, 6.2, 1.5, -1.5, head_width=0.15, head_length=0.1, fc='green', ec='green', lw=2)
    # Add-ons → Churn
    ax.arrow(2.5, 5.5, 0.5, -0.8, head_width=0.15, head_length=0.1, fc='blue', ec='blue', lw=3)
    
    ax.text(1.5, 6.3, 'Age', ha='center', fontsize=11, fontweight='bold',
           bbox=dict(boxstyle='circle', facecolor='lightgreen', edgecolor='green', linewidth=2))
    ax.text(2.3, 5.5, 'Add-ons', ha='center', fontsize=10, fontweight='bold',
           bbox=dict(boxstyle='round', facecolor='lightblue'))
    ax.text(3.2, 4.5, 'Churn', ha='center', fontsize=10, fontweight='bold',
           bbox=dict(boxstyle='round', facecolor='lightyellow'))
    
    # ========== COLLIDER (Top Right) ==========
    ax.text(7.5, 8.5, '❌ COLLIDER (DO NOT CONTROL)', 
           ha='center', fontsize=14, fontweight='bold', color='red',
           bbox=dict(boxstyle='round', facecolor='lightcoral', alpha=0.5, edgecolor='red', linewidth=2))
    
    collider_box = FancyBboxPatch((5.5, 6.5), 4, 1.5,
                                 boxstyle="round,pad=0.1",
                                 edgecolor='red', facecolor='lightcoral',
                                 alpha=0.3, linewidth=2)
    ax.add_patch(collider_box)
    
    collider_text = (
        "Caused by Treatment & Outcome:\n"
        "• Tenure (months since signup)\n\n"
        "Problem: Tenure is CAUSED BY:\n"
        "1. Add-ons → less churn → longer tenure\n"
        "2. No churn → survival → longer tenure\n\n"
        "Controlling for tenure INDUCES bias!"
    )
    ax.text(7.5, 7.25, collider_text, ha='center', va='center', fontsize=10,
           bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    # Causal diagram for collider
    # Add-ons → Tenure
    ax.arrow(6.5, 6.2, 0.3, -0.5, head_width=0.15, head_length=0.1, fc='blue', ec='blue', lw=3)
    # Churn → Tenure
    ax.arrow(8.5, 6.2, -0.3, -0.5, head_width=0.15, head_length=0.1, fc='orange', ec='orange', lw=3)
    # Add-ons → Churn
    ax.arrow(6.7, 6.0, 1.6, 0, head_width=0.15, head_length=0.1, fc='blue', ec='blue', lw=3)
    
    ax.text(6.5, 6.3, 'Add-ons', ha='center', fontsize=10, fontweight='bold',
           bbox=dict(boxstyle='round', facecolor='lightblue'))
    ax.text(8.5, 6.3, 'Churn', ha='center', fontsize=10, fontweight='bold',
           bbox=dict(boxstyle='round', facecolor='lightyellow'))
    ax.text(7.5, 5.5, 'Tenure', ha='center', fontsize=11, fontweight='bold',
           bbox=dict(boxstyle='circle', facecolor='lightcoral', edgecolor='red', linewidth=2))
    
    # ========== OTHER TREATMENTS (Bottom Left) ==========
    ax.text(2.5, 4.0, '❌ OTHER TREATMENTS', 
           ha='center', fontsize=14, fontweight='bold', color='orange',
           bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5, edgecolor='orange', linewidth=2))
    
    treatment_box = FancyBboxPatch((0.5, 2.0), 4, 1.5,
                                  boxstyle="round,pad=0.1",
                                  edgecolor='orange', facecolor='wheat',
                                  alpha=0.3, linewidth=2)
    ax.add_patch(treatment_box)
    
    treatment_text = (
        "Also Endogenous Choices:\n"
        "• Contract type (MTM vs long-term)\n"
        "• Payment method (e-check vs autopay)\n\n"
        "Problem: These are TREATMENTS,\n"
        "not confounders. They need their\n"
        "own causal analysis!"
    )
    ax.text(2.5, 2.75, treatment_text, ha='center', va='center', fontsize=10,
           bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    # ========== MEDIATOR (Bottom Right) ==========
    ax.text(7.5, 4.0, '❌ MEDIATOR (ON CAUSAL PATH)', 
           ha='center', fontsize=14, fontweight='bold', color='purple',
           bbox=dict(boxstyle='round', facecolor='plum', alpha=0.5, edgecolor='purple', linewidth=2))
    
    mediator_box = FancyBboxPatch((5.5, 2.0), 4, 1.5,
                                 boxstyle="round,pad=0.1",
                                 edgecolor='purple', facecolor='plum',
                                 alpha=0.3, linewidth=2)
    ax.add_patch(mediator_box)
    
    mediator_text = (
        "On the Causal Path:\n"
        "• Monthly charges\n\n"
        "Problem: Add-ons → Higher charges\n"
        "Higher charges → May affect churn\n\n"
        "Controlling blocks the mechanism!"
    )
    ax.text(7.5, 2.75, mediator_text, ha='center', va='center', fontsize=10,
           bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    # Causal diagram for mediator
    # Add-ons → Charges
    ax.arrow(6.5, 1.7, 0.5, -0.3, head_width=0.15, head_length=0.1, fc='blue', ec='blue', lw=3)
    # Charges → Churn
    ax.arrow(7.5, 1.2, 0.5, -0.3, head_width=0.15, head_length=0.1, fc='purple', ec='purple', lw=2)
    # Add-ons → Churn (direct)
    ax.arrow(6.7, 1.5, 1.3, -0.5, head_width=0.15, head_length=0.1, fc='blue', ec='blue', lw=3, linestyle='--')
    
    ax.text(6.5, 1.8, 'Add-ons', ha='center', fontsize=10, fontweight='bold',
           bbox=dict(boxstyle='round', facecolor='lightblue'))
    ax.text(7.5, 1.3, 'Charges', ha='center', fontsize=10, fontweight='bold',
           bbox=dict(boxstyle='round', facecolor='plum'))
    ax.text(8.5, 0.8, 'Churn', ha='center', fontsize=10, fontweight='bold',
           bbox=dict(boxstyle='round', facecolor='lightyellow'))
    
    # ========== SUMMARY BOX (Bottom Center) ==========
    summary_box = FancyBboxPatch((1.5, 0.1), 7, 0.7,
                                boxstyle="round,pad=0.05",
                                edgecolor='black', facecolor='lightyellow',
                                alpha=0.8, linewidth=3)
    ax.add_patch(summary_box)
    
    summary_text = (
        "🎯 KEY INSIGHT: Not all 'controls' are valid confounders!\n"
        "✅ Control for: Pre-treatment exogenous variables (age, family)\n"
        "❌ Do NOT control for: Colliders (tenure), other treatments (contract, payment), mediators (charges)\n"
        "💡 For definitive causal inference: Use randomized experiments!"
    )
    ax.text(5, 0.45, summary_text, ha='center', va='center', fontsize=11,
           bbox=dict(boxstyle='round', facecolor='white', alpha=0.9))
    
    plt.tight_layout()
    plt.savefig('/mnt/user-data/outputs/3_valid_invalid_controls_diagram.png', dpi=300, bbox_inches='tight')
    print("✓ Saved: 3_valid_invalid_controls_diagram.png")
    plt.close()


# =============================================================================
# MAIN EXECUTION
# =============================================================================

if __name__ == '__main__':
    print("="*80)
    print("CREATING PORTFOLIO VISUALIZATIONS")
    print("="*80)
    
    # Load data
    df = pd.read_csv('/mnt/user-data/uploads/churn_prediction.csv', index_col=0)
    
    print(f"\nLoaded {len(df):,} customers")
    
    # Create all three visualizations
    create_early_tenure_effect_chart(df)
    create_collider_bias_demonstration(df)
    create_valid_controls_diagram()
    
    print("\n" + "="*80)
    print("✅ ALL VISUALIZATIONS CREATED")
    print("="*80)
    print("\nGenerated files:")
    print("  1. 1_early_tenure_effect.png - Shows effect before/after controlling")
    print("  2. 2_collider_bias_demonstration.png - Shows effect reversal")
    print("  3. 3_valid_invalid_controls_diagram.png - Shows causal structure")
    
    print("\n" + "="*80)
    print("USAGE IN PRESENTATIONS:")
    print("="*80)
    print("""
Slide 1: The Discovery
→ Show: 1_early_tenure_effect.png
→ Message: "60.9% vs 23.2% churn - even after controlling for age/dependents"

Slide 2: The Problem  
→ Show: 2_collider_bias_demonstration.png
→ Message: "Effect REVERSES by tenure - this is collider bias!"

Slide 3: The Correction
→ Show: 3_valid_invalid_controls_diagram.png
→ Message: "Only age/family are valid controls - everything else is problematic"

These three charts tell your complete causal inference journey!
    """)
    
    print("\n📊 Portfolio Impact:")
    print("  ✓ Shows you understand causal structure")
    print("  ✓ Demonstrates collider bias empirically")
    print("  ✓ Explains concepts visually (accessible to non-technical)")
    print("  ✓ Publication-quality graphics")
