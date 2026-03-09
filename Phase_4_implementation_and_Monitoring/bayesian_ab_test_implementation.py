"""
Bayesian A/B Test Implementation for Customer Churn Reduction
Complete implementation ready to run with your data
"""
#%%
import pandas as pd
import numpy as np
import pymc as pm
import arviz as az
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from sklearn.model_selection import train_test_split
from pathlib import Path
import sys
import warnings
warnings.filterwarnings('ignore')

# Centralized path config
_PROJECT_DIR = Path(__file__).resolve().parents[1]
_CONFIG_DIR = _PROJECT_DIR / "Methodology for portfolio"
if str(_CONFIG_DIR) not in sys.path:
    sys.path.insert(0, str(_CONFIG_DIR))

from config import get_results_path, get_visualization_path

RECOMMENDATION_PATH = Path(get_results_path("recommendation.csv"))
RESULTS_DIR = Path(get_results_path(""))
VISUALIZATIONS_DIR = Path(get_visualization_path(""))
RESULTS_DIR.mkdir(parents=True, exist_ok=True)
VISUALIZATIONS_DIR.mkdir(parents=True, exist_ok=True)

# Set style
sns.set_style('whitegrid')
plt.rcParams['figure.figsize'] = (12, 6)


class ChurnTestPreparation:
    """Prepare data for Bayesian A/B testing"""
    
    def __init__(self, df):
        self.df = df.copy()
        self._prepare_features()
    
    def _prepare_features(self):
        """Create necessary features for testing"""
        # Binary churn
        self.df['churn_binary'] = (self.df['Actual_Churn'] == 'Yes').astype(int)
        
        # Risk tiers
        self.df['risk_tier'] = pd.cut(
            self.df['Churn_Rate'],
            bins=[0, 0.60, 0.75, 1.0],
            labels=['Moderate', 'High', 'Extreme']
        )
        
        # Tenure groups
        self.df['tenure_group'] = pd.cut(
            self.df['tenure'],
            bins=[0, 3, 6, 12, 100],
            labels=['0-3mo', '4-6mo', '7-12mo', '13+mo']
        )
        
        # Service counts
        tech_services = ['OnlineSecurity', 'OnlineBackup', 'DeviceProtection', 'TechSupport']
        self.df['tech_service_count'] = (self.df[tech_services] == 'Yes').sum(axis=1)
        
        streaming_services = ['StreamingTV', 'StreamingMovies']
        self.df['streaming_count'] = (self.df[streaming_services] == 'Yes').sum(axis=1)
        
        # Payment method binary
        self.df['uses_autopay'] = self.df['PaymentMethod'].str.contains('automatic').astype(int)
        self.df['uses_echeck'] = (self.df['PaymentMethod'] == 'Electronic check').astype(int)
        
        print("✓ Features prepared")
        print(f"  - Total customers: {len(self.df)}")
        print(f"  - Actual churn rate: {self.df['churn_binary'].mean():.1%}")
        print(f"  - Mean predicted churn: {self.df['Churn_Rate'].mean():.1%}")
    
    def create_test_segments(self, test_type='contract_payment'):
        """
        Create appropriate segments for different test types
        
        test_type options:
        - 'contract_payment': Contract + payment method test
        - 'tenure_intervention': Early tenure intervention
        - 'service_upsell': Service bundle upsell
        """
        if test_type == 'contract_payment':
            # All customers (99.9% on month-to-month)
            segment = self.df.copy()
            print(f"\n✓ Contract+Payment test segment: {len(segment)} customers")
            
        elif test_type == 'tenure_intervention':
            # Customers in first 6 months
            segment = self.df[self.df['tenure'] <= 6].copy()
            print(f"\n✓ Tenure intervention segment: {len(segment)} customers (tenure ≤6 months)")
            
        elif test_type == 'service_upsell':
            # Fiber customers with <2 tech services
            segment = self.df[
                (self.df['InternetService'] == 'Fiber optic') &
                (self.df['tech_service_count'] < 2)
            ].copy()
            print(f"\n✓ Service upsell segment: {len(segment)} customers (Fiber + <2 tech services)")
            
        else:
            raise ValueError(f"Unknown test_type: {test_type}")
        
        return segment
    
    def stratified_allocation(self, segment, n_arms=4, random_state=42):
        """
        Allocate customers to treatment arms with stratification
        """
        np.random.seed(random_state)
        
        # Create blocking variable
        segment['block'] = (
            segment['risk_tier'].astype(str) + '_' +
            segment['tenure_group'].astype(str)
        )
        
        # Allocate within blocks
        allocations = []
        
        for block in segment['block'].unique():
            block_mask = segment['block'] == block
            block_size = block_mask.sum()
            
            # Random assignment
            block_assignments = np.random.choice(
                range(n_arms),
                size=block_size,
                replace=True
            )
            
            allocations.extend(zip(segment[block_mask].index, block_assignments))
        
        # Assign to dataframe
        for idx, arm in allocations:
            segment.loc[idx, 'treatment_arm'] = arm
        
        segment['treatment_arm'] = segment['treatment_arm'].astype(int)
        
        # Check balance
        self._verify_balance(segment)
        
        return segment
    
    def _verify_balance(self, segment):
        """Verify covariate balance across treatment arms"""
        print("\n" + "="*60)
        print("BALANCE CHECK")
        print("="*60)
        
        # Count by arm
        print("\nCustomers per arm:")
        print(segment['treatment_arm'].value_counts().sort_index())
        
        # Key covariates
        covariates = ['Churn_Rate', 'MonthlyCharges', 'tenure', 'uses_echeck']
        
        print("\nCovariate balance:")
        balance_df = segment.groupby('treatment_arm')[covariates].mean()
        print(balance_df.round(2))
        
        # Statistical test (should NOT be significant if balanced)
        print("\nKruskal-Wallis tests (p-value, want >0.05 for balance):")
        for cov in covariates:
            groups = [segment[segment['treatment_arm'] == arm][cov].values 
                     for arm in range(4)]
            stat, pval = stats.kruskal(*groups)
            status = "✓ Balanced" if pval > 0.05 else "⚠ Imbalanced"
            print(f"  {cov}: p={pval:.3f} {status}")


class BayesianChurnModel:
    """Bayesian hierarchical model for churn A/B test"""
    
    def __init__(self, data, treatment_costs):
        """
        Parameters:
        -----------
        data : DataFrame with columns:
            - treatment_arm: 0 (control), 1, 2, 3
            - churn_binary: 0 or 1
            - risk_tier: Moderate, High, Extreme
        treatment_costs : list of costs per arm [control, T1, T2, T3]
        """
        self.data = data.copy()
        self.costs = treatment_costs
        self.model = None
        self.trace = None
        
        # Encode categorical variables
        self.data['risk_idx'] = pd.Categorical(self.data['risk_tier']).codes
    
    def build_model(self, prior_effects=[0, -0.12, -0.20, -0.28]):
        """
        Build hierarchical Bayesian model
        
        prior_effects: Expected treatment effects (negative = reduces churn)
        """
        with pm.Model() as model:
            # Data
            treatment_idx = self.data['treatment_arm'].values
            risk_idx = self.data['risk_idx'].values
            churn = self.data['churn_binary'].values
            
            n_treatments = 4
            n_tiers = 3
            
            # Hyperpriors
            baseline_alpha = pm.Gamma('baseline_alpha', alpha=7, beta=10)
            baseline_beta = pm.Gamma('baseline_beta', alpha=3, beta=10)
            μ_baseline = pm.Beta('mu_baseline', alpha=baseline_alpha, beta=baseline_beta)
            
            # Risk tier effects (varying intercepts)
            σ_tier = pm.HalfNormal('sigma_tier', sigma=0.15)
            tier_offset_raw = pm.Normal('tier_offset_raw', mu=0, sigma=1, shape=n_tiers)
            tier_offset = pm.Deterministic('tier_offset', tier_offset_raw * σ_tier)
            
            # Treatment effects (varying slopes)
            σ_treatment = pm.HalfNormal('sigma_treatment', sigma=0.15)
            treatment_effect_raw = pm.Normal(
                'treatment_effect_raw',
                mu=0,
                sigma=1,
                shape=n_treatments
            )
            treatment_effect = pm.Deterministic(
                'treatment_effect',
                prior_effects + treatment_effect_raw * σ_treatment
            )
            
            # Combine on logit scale
            logit_baseline = pm.math.log(μ_baseline / (1 - μ_baseline))
            
            logit_p_churn = (
                logit_baseline +
                tier_offset[risk_idx] +
                treatment_effect[treatment_idx]
            )
            
            p_churn = pm.Deterministic('p_churn', pm.math.invlogit(logit_p_churn))
            
            # Likelihood
            obs_churn = pm.Bernoulli('churn', p=p_churn, observed=churn)
        
        self.model = model
        print("✓ Model built successfully")
        return model
    
    def run_inference(self, draws=2000, tune=1000, chains=4, target_accept=0.95):
        """Run MCMC sampling"""
        print("\nRunning MCMC sampling...")
        print(f"  Draws: {draws}, Tune: {tune}, Chains: {chains}")
        
        with self.model:
            self.trace = pm.sample(
                draws=draws,
                tune=tune,
                chains=chains,
                target_accept=target_accept,
                return_inferencedata=True,
                cores=4
            )
        
        print("✓ Sampling complete")
        
        # Diagnostics
        print("\nConvergence diagnostics:")
        print(az.summary(
            self.trace,
            var_names=['treatment_effect', 'mu_baseline'],
            round_to=3
        ))
        
        return self.trace
    
    def decision_analysis(self, min_effect=0.08, revenue_per_month=74.44):
        """
        Compute decision metrics for each treatment
        
        min_effect: Minimum worthwhile effect size (8% churn reduction)
        revenue_per_month: Average monthly revenue per customer
        """
        print("\n" + "="*80)
        print("BAYESIAN DECISION ANALYSIS")
        print("="*80)
        
        # Extract posterior samples
        treatment_effects = self.trace.posterior['treatment_effect'].values
        # Shape: (chains, draws, n_treatments) -> reshape to (total_samples, n_treatments)
        treatment_effects = treatment_effects.reshape(-1, treatment_effects.shape[-1])
        
        results = {}
        
        for i in range(1, 4):  # Skip control (arm 0)
            # 1. Probability of superiority (POS)
            diff = treatment_effects[:, 0] - treatment_effects[:, i]  # Control - Treatment
            pos = (diff > min_effect).mean()
            
            # 2. Region of practical equivalence (ROPE)
            in_rope = np.logical_and(diff > -0.02, diff < 0.02).mean()
            
            # 3. Expected churn reduction
            churn_reduction = diff.mean()
            churn_reduction_ci = np.percentile(diff, [2.5, 97.5])
            
            # 4. Expected value calculation
            # Assume: reduced churn extends lifetime by avg 11 months
            retention_lift = diff  # Absolute reduction in churn probability
            expected_months_saved = retention_lift * 11
            revenue_saved = expected_months_saved * revenue_per_month
            net_ev = revenue_saved - self.costs[i]
            
            # 5. ROI
            roi = (net_ev / self.costs[i]).mean()
            prob_positive_ev = (net_ev > 0).mean()
            prob_roi_2x = (roi > 2.0).mean()
            
            results[f'Treatment_{i}'] = {
                'P(Superiority >8%)': pos,
                'P(in ROPE <2%)': in_rope,
                'Mean Churn Reduction': churn_reduction,
                'Churn Reduction 95% CI': churn_reduction_ci,
                'Expected Value ($)': net_ev.mean(),
                'EV 95% CI ($)': np.percentile(net_ev, [2.5, 97.5]),
                'Mean ROI': roi,
                'P(Positive EV)': prob_positive_ev,
                'P(ROI > 2x)': prob_roi_2x,
                'Decision': self._make_decision(pos, in_rope, net_ev.mean())
            }
        
        df_results = pd.DataFrame(results).T
        print(df_results.round(3))
        
        return df_results
    
    def _make_decision(self, pos, in_rope, mean_ev):
        """Decision rule based on multiple criteria"""
        if pos > 0.95 and mean_ev > 50:
            return "✓ IMPLEMENT"
        elif in_rope > 0.95:
            return "≈ EQUIVALENT (no effect)"
        elif pos > 0.80 and mean_ev > 0:
            return "⚠ PROMISING (monitor)"
        elif pos < 0.20:
            return "✗ INFERIOR (stop)"
        else:
            return "? INCONCLUSIVE (continue)"
    
    def plot_results(self, save_path='./'):
        """Generate comprehensive plots"""
        print("\nGenerating plots...")
        save_dir = Path(save_path)
        save_dir.mkdir(parents=True, exist_ok=True)
        
        # 1. Posterior distributions of treatment effects
        fig, ax = plt.subplots(figsize=(12, 6))
        az.plot_posterior(
            self.trace,
            var_names=['treatment_effect'],
            ref_val=0,
            ax=ax
        )
        plt.suptitle('Posterior Distributions: Treatment Effects on Churn', fontsize=14, y=1.02)
        plt.tight_layout()
        output_file = save_dir / 'posterior_treatment_effects.png'
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"  ✓ Saved: {output_file}")
        plt.close()
        
        # 2. Forest plot with credible intervals
        fig, ax = plt.subplots(figsize=(10, 6))
        az.plot_forest(
            self.trace,
            var_names=['treatment_effect'],
            combined=True,
            ax=ax,
            figsize=(10, 6)
        )
        ax.axvline(0, color='red', linestyle='--', linewidth=2, label='No effect')
        ax.axvline(-0.08, color='green', linestyle='--', linewidth=2, label='Target (-8%)')
        ax.set_xlabel('Effect on Churn Probability (negative = reduces churn)', fontsize=12)
        ax.set_title('Treatment Effects with 95% Credible Intervals', fontsize=14)
        ax.legend()
        plt.tight_layout()
        output_file = save_dir / 'forest_plot.png'
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"  ✓ Saved: {output_file}")
        plt.close()
        
        # 3. Trace plots (convergence check)
        az.plot_trace(
            self.trace,
            var_names=['treatment_effect', 'mu_baseline'],
            compact=True
        )
        output_file = save_dir / 'trace_plots.png'
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"  ✓ Saved: {output_file}")
        plt.close()
        
        # 4. Pairwise comparison plot
        self._plot_pairwise_comparisons(save_dir)
        
        print("✓ All plots generated")
    
    def _plot_pairwise_comparisons(self, save_dir):
        """Plot probability that each treatment beats control"""
        treatment_effects = self.trace.posterior['treatment_effect'].values
        treatment_effects = treatment_effects.reshape(-1, treatment_effects.shape[-1])
        
        fig, axes = plt.subplots(1, 3, figsize=(15, 5))
        
        for i, ax in enumerate(axes):
            treatment_idx = i + 1
            
            # Difference distribution
            diff = treatment_effects[:, 0] - treatment_effects[:, treatment_idx]
            
            ax.hist(diff, bins=50, alpha=0.7, edgecolor='black')
            ax.axvline(0, color='red', linestyle='--', linewidth=2, label='No difference')
            ax.axvline(0.08, color='green', linestyle='--', linewidth=2, label='Target (8%)')
            
            # Probability annotations
            prob_better = (diff > 0).mean()
            prob_target = (diff > 0.08).mean()
            
            ax.set_title(f'Treatment {treatment_idx} vs Control', fontsize=12)
            ax.set_xlabel('Churn Reduction', fontsize=11)
            ax.set_ylabel('Frequency', fontsize=11)
            
            # Add text box with probabilities
            textstr = f'P(Better) = {prob_better:.1%}\nP(>8%) = {prob_target:.1%}'
            ax.text(0.05, 0.95, textstr, transform=ax.transAxes,
                   verticalalignment='top',
                   bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5),
                   fontsize=10)
            
            ax.legend()
        
        plt.tight_layout()
        output_file = save_dir / 'pairwise_comparisons.png'
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"  ✓ Saved: {output_file}")
        plt.close()


def simulate_test_outcomes(data, treatment_effects, random_state=42):
    """
    Simulate test outcomes based on assumed treatment effects
    Useful for power analysis and planning
    
    treatment_effects: dict like {0: 0, 1: -0.12, 2: -0.20, 3: -0.28}
    """
    np.random.seed(random_state)
    
    simulated = data.copy()
    simulated['simulated_churn'] = 0
    
    for arm in range(4):
        arm_mask = simulated['treatment_arm'] == arm
        
        # Base churn probability
        base_p = simulated.loc[arm_mask, 'Churn_Rate'].values
        
        # Adjusted by treatment effect
        adjusted_p = np.clip(base_p + treatment_effects[arm], 0, 1)
        
        # Simulate outcomes
        outcomes = np.random.binomial(1, adjusted_p)
        simulated.loc[arm_mask, 'simulated_churn'] = outcomes
    
    print("\n" + "="*60)
    print("SIMULATED TEST RESULTS")
    print("="*60)
    
    sim_results = simulated.groupby('treatment_arm').agg({
        'simulated_churn': ['count', 'sum', 'mean'],
        'Churn_Rate': 'mean'
    }).round(3)
    
    sim_results.columns = ['N', 'Churned', 'Observed_Rate', 'Predicted_Rate']
    print(sim_results)
    
    return simulated


# =============================================================================
# MAIN EXECUTION EXAMPLE
# =============================================================================

if __name__ == '__main__':
    print("="*80)
    print("BAYESIAN CHURN REDUCTION A/B TEST")
    print("="*80)
    
    # -------------------------------------------------------------------------
    # STEP 1: Load and prepare data
    # -------------------------------------------------------------------------
    print("\nSTEP 1: Loading data...")
    if not RECOMMENDATION_PATH.exists():
        raise FileNotFoundError(f"Recommendation file not found at: {RECOMMENDATION_PATH}")
    print(f"✓ Using recommendation file: {RECOMMENDATION_PATH}")
    df = pd.read_csv(RECOMMENDATION_PATH, index_col=0)
    
    prep = ChurnTestPreparation(df)
    
    # -------------------------------------------------------------------------
    # STEP 2: Create test segment and allocate
    # -------------------------------------------------------------------------
    print("\nSTEP 2: Creating test segment...")
    
    # For Contract + Payment Method test
    segment = prep.create_test_segments(test_type='contract_payment')
    
    # Take first 800 for the test
    test_data = segment.head(800).copy()
    
    # Allocate to treatment arms
    test_data = prep.stratified_allocation(test_data, n_arms=4, random_state=42)
    
    # -------------------------------------------------------------------------
    # STEP 3: Simulate outcomes (in real test, use actual observed churn)
    # -------------------------------------------------------------------------
    print("\nSTEP 3: Simulating test outcomes...")
    
    # Expected effects based on analysis
    treatment_effects = {
        0: 0,       # Control: no change
        1: -0.12,   # T1: -12% churn
        2: -0.20,   # T2: -20% churn
        3: -0.28    # T3: -28% churn
    }
    
    test_data = simulate_test_outcomes(test_data, treatment_effects, random_state=42)
    
    # Use simulated outcomes as observed data
    test_data['churn_binary'] = test_data['simulated_churn']
    
    # -------------------------------------------------------------------------
    # STEP 4: Build and run Bayesian model
    # -------------------------------------------------------------------------
    print("\nSTEP 4: Building Bayesian model...")
    
    # Treatment costs
    costs = [0, 94.51, 104.51, 250]  # Control, T1, T2, T3
    
    # Initialize model
    model = BayesianChurnModel(test_data, costs)
    
    # Build model with informative priors
    model.build_model(prior_effects=[0, -0.12, -0.20, -0.28])
    
    # Run inference
    trace = model.run_inference(draws=1000, tune=500, chains=4)
    
    # -------------------------------------------------------------------------
    # STEP 5: Decision analysis
    # -------------------------------------------------------------------------
    print("\nSTEP 5: Decision analysis...")
    
    decision_results = model.decision_analysis(
        min_effect=0.08,
        revenue_per_month=74.44
    )
    
    # -------------------------------------------------------------------------
    # STEP 6: Generate plots
    # -------------------------------------------------------------------------
    print("\nSTEP 6: Generating visualizations...")
    
    model.plot_results(save_path=VISUALIZATIONS_DIR)
    
    # -------------------------------------------------------------------------
    # STEP 7: Summary and recommendations
    # -------------------------------------------------------------------------
    print("\n" + "="*80)
    print("FINAL RECOMMENDATIONS")
    print("="*80)
    
    # Find best treatment
    ev_values = {}
    for i in range(1, 4):
        ev = decision_results.loc[f'Treatment_{i}', 'Expected Value ($)']
        pos = decision_results.loc[f'Treatment_{i}', 'P(Superiority >8%)']
        ev_values[f'Treatment_{i}'] = (ev, pos)
    
    best_treatment = max(ev_values.items(), key=lambda x: x[1][0])
    
    print(f"\n✓ Recommended action: {best_treatment[0]}")
    print(f"  - Expected value: ${best_treatment[1][0]:.2f} per customer")
    print(f"  - Probability of >8% churn reduction: {best_treatment[1][1]:.1%}")
    
    print("\n" + "="*80)
    print("✓ Analysis complete!")
    print("="*80)
    
    # Save results
    decision_path = Path(get_results_path('decision_results.csv'))
    decision_results.to_csv(decision_path)
    print(f"\n✓ Results saved to {decision_path}")
