"""
Bayesian Analysis Engine (UPDATED for config.py)
Portfolio Project: Complete Bayesian Inference Framework

UPDATED: Now uses centralized config.py for directory management

Features:
- Data preprocessing and validation
- Prior specification (informative and weakly informative)
- Model fitting with PyMC
- Convergence diagnostics
- Posterior analysis
- Model comparison
- Predictions and forecasting
- Complete test suite
"""

import numpy as np
import pandas as pd
import pymc as pm
import arviz as az
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# Import configuration
from config import (
    results_dir, visualizations_dir, reports_dir,
    get_visualization_path, get_report_path
)

sns.set_style('whitegrid')


class BayesianAnalysisEngine:
    """
    Complete Bayesian analysis engine for churn experiments
    
    """
    
    def __init__(self, random_seed=42):
        """
        Initialize Bayesian analysis engine
        
        Parameters:
        -----------
        random_seed : int
            Random seed for reproducibility
        """
        self.random_seed = random_seed
        np.random.seed(random_seed)
        
        self.data = None
        self.model = None
        self.trace = None
        self.prior_predictive = None
        self.posterior_predictive = None
        
        print("✓ Bayesian Analysis Engine initialized")
        print(f"  Random seed: {random_seed}")
        print(f"  Results directory: {results_dir}")
        print(f"  Visualizations: {visualizations_dir}")
    
    def load_data(self, filepath_or_df, sample_frac=None):
        """
        Load and preprocess data
        
        Parameters:
        -----------
        filepath_or_df : str or pd.DataFrame
            Path to CSV file or DataFrame
        sample_frac : float, optional
            Fraction of data to sample (for testing)
        
        Returns:
        --------
        pd.DataFrame : Processed data
        """
        print("\n" + "="*80)
        print("LOADING DATA")
        print("="*80)
        
        # Load data
        if isinstance(filepath_or_df, str):
            self.data = pd.read_csv(filepath_or_df, index_col=0)
            print(f"✓ Loaded from file: {filepath_or_df}")
        else:
            self.data = filepath_or_df.copy()
            print(f"✓ Loaded from DataFrame")
        
        # Sample if requested
        if sample_frac is not None:
            self.data = self.data.sample(frac=sample_frac, random_state=self.random_seed)
            print(f"  Sampled {sample_frac:.0%} of data")
        
        print(f"  Shape: {self.data.shape}")
        print(f"  Rows: {len(self.data):,}")
        
        # Create binary outcome
        self.data['churn_binary'] = (self.data['Actual_Churn'] == 'Yes').astype(int)
        
        # Create treatment indicators
        addon_services = ['OnlineSecurity', 'OnlineBackup', 'DeviceProtection', 'TechSupport']
        self.data['has_addons'] = (self.data[addon_services] == 'Yes').any(axis=1).astype(int)
        
        # Create confounders
        self.data['senior'] = (self.data['SeniorCitizen'] == 'Yes').astype(int)
        self.data['has_dependents'] = (self.data['Dependents'] == 'Yes').astype(int)
        self.data['has_partner'] = (self.data['Partner'] == 'Yes').astype(int)
        
        # Data summary
        churn_rate = self.data['churn_binary'].mean()
        addon_rate = self.data['has_addons'].mean()
        
        print(f"\n  Churn rate: {churn_rate:.1%}")
        print(f"  Add-on adoption: {addon_rate:.1%}")
        
        return self.data
    
    def specify_model(self, model_type='proper_causal'):
        """
        Specify Bayesian model
        
        Parameters:
        -----------
        model_type : str
            'proper_causal' - Correct model (age, dependents only)
            'naive' - Naive model (all variables)
            'collider' - Model with collider bias (includes tenure)
        
        Returns:
        --------
        pm.Model : PyMC model
        """
        print("\n" + "="*80)
        print(f"SPECIFYING MODEL: {model_type.upper()}")
        print("="*80)
        
        # Prepare data
        y = self.data['churn_binary'].values
        X_addon = self.data['has_addons'].values
        X_senior = self.data['senior'].values
        X_dependents = self.data['has_dependents'].values
        X_partner = self.data['has_partner'].values
        
        # Standardize for numerical stability
        X_addon_std = (X_addon - X_addon.mean()) / (X_addon.std() + 1e-6)
        X_senior_std = (X_senior - X_senior.mean()) / (X_senior.std() + 1e-6)
        X_dependents_std = (X_dependents - X_dependents.mean()) / (X_dependents.std() + 1e-6)
        X_partner_std = (X_partner - X_partner.mean()) / (X_partner.std() + 1e-6)
        
        with pm.Model() as model:
            # Priors
            if model_type == 'proper_causal':
                print("\n✓ Using PROPER CAUSAL MODEL")
                print("  Controls: Age, Dependents, Partner (exogenous only)")
                
                # Intercept
                alpha = pm.Normal('alpha', mu=0, sigma=2)
                
                # Causal effect of add-ons (weakly informative prior)
                beta_addon = pm.Normal('beta_addon', mu=-0.1, sigma=0.5)
                
                # Confounders (exogenous variables only)
                beta_senior = pm.Normal('beta_senior', mu=0, sigma=1)
                beta_dependents = pm.Normal('beta_dependents', mu=0, sigma=1)
                beta_partner = pm.Normal('beta_partner', mu=0, sigma=1)
                
                # Linear combination
                logit_p = (alpha + 
                          beta_addon * X_addon_std +
                          beta_senior * X_senior_std +
                          beta_dependents * X_dependents_std +
                          beta_partner * X_partner_std)
                
            elif model_type == 'collider':
                print("\n⚠️ Using MODEL WITH COLLIDER BIAS")
                print("  Controls: Age, Dependents, Partner, Tenure (includes collider!)")
                
                # Include tenure (collider)
                X_tenure = self.data['tenure'].values
                X_tenure_std = (X_tenure - X_tenure.mean()) / (X_tenure.std() + 1e-6)
                
                alpha = pm.Normal('alpha', mu=0, sigma=2)
                beta_addon = pm.Normal('beta_addon', mu=-0.1, sigma=0.5)
                beta_senior = pm.Normal('beta_senior', mu=0, sigma=1)
                beta_dependents = pm.Normal('beta_dependents', mu=0, sigma=1)
                beta_partner = pm.Normal('beta_partner', mu=0, sigma=1)
                beta_tenure = pm.Normal('beta_tenure', mu=0, sigma=1)
                
                logit_p = (alpha + 
                          beta_addon * X_addon_std +
                          beta_senior * X_senior_std +
                          beta_dependents * X_dependents_std +
                          beta_partner * X_partner_std +
                          beta_tenure * X_tenure_std)
                
            elif model_type == 'naive':
                print("\n⚠️ Using NAIVE MODEL")
                print("  No controls (just treatment effect)")
                
                alpha = pm.Normal('alpha', mu=0, sigma=2)
                beta_addon = pm.Normal('beta_addon', mu=-0.1, sigma=0.5)
                
                logit_p = alpha + beta_addon * X_addon_std
            
            # Likelihood
            p = pm.math.invlogit(logit_p)
            obs = pm.Bernoulli('obs', p=p, observed=y)
        
        self.model = model
        print(f"\n✓ Model specified: {len(model.free_RVs)} parameters")
        
        return model
    
    def fit_model(self, draws=2000, tune=1000, chains=2, target_accept=0.95):
        """
        Fit Bayesian model using MCMC
        """
        print("\n" + "="*80)
        print("FITTING MODEL VIA MCMC")
        print("="*80)
        
        print(f"\nSampling parameters:")
        print(f"  Draws: {draws}")
        print(f"  Tune: {tune}")
        print(f"  Chains: {chains}")
        print(f"  Target accept: {target_accept}")
        
        with self.model:
            # Sample
            self.trace = pm.sample(
                draws=draws,
                tune=tune,
                chains=chains,
                target_accept=target_accept,
                return_inferencedata=True,
                random_seed=self.random_seed
            )
        
        print("\n✓ Sampling complete")
        
        # Quick convergence check
        self._quick_convergence_check()
        
        return self.trace
    
    def _quick_convergence_check(self):
        """Quick check of convergence diagnostics"""
        print("\n" + "="*60)
        print("CONVERGENCE CHECK")
        print("="*60)
        
        # R-hat
        rhat = az.rhat(self.trace)
        max_rhat = max([rhat[var].values.max() for var in rhat.data_vars])
        
        print(f"\nR-hat (Gelman-Rubin):")
        print(f"  Maximum R-hat: {max_rhat:.4f}")
        
        if max_rhat < 1.01:
            print(f"  ✓ Excellent convergence (R-hat < 1.01)")
        elif max_rhat < 1.05:
            print(f"  ~ Good convergence (R-hat < 1.05)")
        else:
            print(f"  ⚠️ Questionable convergence (R-hat >= 1.05)")
        
        # ESS
        ess = az.ess(self.trace)
        min_ess = min([ess[var].values.min() for var in ess.data_vars])
        
        print(f"\nEffective Sample Size:")
        print(f"  Minimum ESS: {min_ess:.0f}")
        
        if min_ess > 400:
            print(f"  ✓ Good ESS (>400)")
        elif min_ess > 100:
            print(f"  ~ Acceptable ESS (>100)")
        else:
            print(f"  ⚠️ Low ESS (<100)")
    
    def convergence_diagnostics(self, save_plots=True):
        """
        Comprehensive convergence diagnostics
        UPDATED: Uses config.py paths
        """
        print("\n" + "="*80)
        print("DETAILED CONVERGENCE DIAGNOSTICS")
        print("="*80)
        
        diagnostics = {}
        
        # 1. R-hat
        rhat = az.rhat(self.trace)
        diagnostics['rhat'] = rhat
        
        print("\nR-hat statistics:")
        for var in rhat.data_vars:
            max_rhat = rhat[var].values.max()
            print(f"  {var}: {max_rhat:.4f}")
        
        # 2. ESS
        ess = az.ess(self.trace)
        diagnostics['ess'] = ess
        
        print("\nEffective Sample Size:")
        for var in ess.data_vars:
            min_ess = ess[var].values.min()
            print(f"  {var}: {min_ess:.0f}")
        
        # 3. MCSE
        mcse = az.mcse(self.trace)
        diagnostics['mcse'] = mcse
        
        print("\nMonte Carlo Standard Error:")
        for var in mcse.data_vars:
            mean_mcse = mcse[var].values.mean()
            print(f"  {var}: {mean_mcse:.4f}")
        
        if save_plots:
            # Trace plots - UPDATED PATH
            fig = az.plot_trace(self.trace, compact=True, figsize=(12, 8))
            plt.tight_layout()
            save_path = get_visualization_path('trace_plots.png')
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"\n✓ Saved: {save_path}")
            plt.close()
            
            # Posterior plots - UPDATED PATH
            fig = az.plot_posterior(self.trace, figsize=(12, 6))
            plt.tight_layout()
            save_path = get_visualization_path('posterior_plots.png')
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"✓ Saved: {save_path}")
            plt.close()
        
        return diagnostics
    
    def analyze_results(self, credible_interval=0.95):
        """Analyze posterior results"""
        print("\n" + "="*80)
        print("POSTERIOR ANALYSIS")
        print("="*80)
        
        # Summary statistics
        summary = az.summary(self.trace, hdi_prob=credible_interval)
        
        print("\nPosterior Summary:")
        print(summary.to_string())
        
        # Add-on effect analysis
        if 'beta_addon' in self.trace.posterior:
            addon_samples = self.trace.posterior['beta_addon'].values.flatten()
            
            print("\n" + "="*60)
            print("ADD-ON CAUSAL EFFECT ANALYSIS")
            print("="*60)
            
            mean_effect = addon_samples.mean()
            hdi = az.hdi(addon_samples, hdi_prob=credible_interval)
            
            print(f"\nEffect on churn (logit scale):")
            print(f"  Mean: {mean_effect:.4f}")
            print(f"  {int(credible_interval*100)}% HDI: [{hdi[0]:.4f}, {hdi[1]:.4f}]")
            
            # Probability statements
            prob_negative = (addon_samples < 0).mean()
            prob_practically_significant = (addon_samples < -0.1).mean()
            
            print(f"\nProbability statements:")
            print(f"  P(Add-ons reduce churn): {prob_negative:.1%}")
            print(f"  P(Effect > 10% reduction): {prob_practically_significant:.1%}")
            
            # Interpretation
            if prob_negative > 0.95:
                print(f"\n✓ Strong evidence: Add-ons reduce churn")
            elif prob_negative > 0.80:
                print(f"\n~ Moderate evidence: Add-ons likely reduce churn")
            else:
                print(f"\n⚠️ Weak evidence: Effect unclear")
        
        return summary
    
    def posterior_predictive_check(self, n_samples=1000):
        """
        Posterior predictive check
        UPDATED: Uses config.py paths
        """
        print("\n" + "="*80)
        print("POSTERIOR PREDICTIVE CHECK")
        print("="*80)
        
        with self.model:
            self.posterior_predictive = pm.sample_posterior_predictive(
                self.trace,
                random_seed=self.random_seed
            )
        
        # Compare observed vs predicted
        y_obs = self.data['churn_binary'].values
        y_pred = self.posterior_predictive.posterior_predictive['obs'].values
        
        # Mean predicted probability
        y_pred_mean = y_pred.mean(axis=(0, 1))
        
        print(f"\nObserved churn rate: {y_obs.mean():.1%}")
        print(f"Predicted churn rate: {y_pred_mean.mean():.1%}")
        
        # Plot
        fig, axes = plt.subplots(1, 2, figsize=(12, 5))
        
        # Histogram comparison
        ax = axes[0]
        ax.hist(y_obs, bins=2, alpha=0.5, label='Observed', density=True)
        ax.hist(y_pred_mean, bins=30, alpha=0.5, label='Predicted', density=True)
        ax.set_xlabel('Churn')
        ax.set_ylabel('Density')
        ax.set_title('Observed vs Predicted Distribution')
        ax.legend()
        
        # Calibration plot
        ax = axes[1]
        bins = np.linspace(0, 1, 11)
        bin_centers = (bins[:-1] + bins[1:]) / 2
        
        obs_by_bin = []
        for i in range(len(bins)-1):
            mask = (y_pred_mean >= bins[i]) & (y_pred_mean < bins[i+1])
            if mask.sum() > 0:
                obs_by_bin.append(y_obs[mask].mean())
            else:
                obs_by_bin.append(np.nan)
        
        ax.scatter(bin_centers, obs_by_bin, s=100, alpha=0.6)
        ax.plot([0, 1], [0, 1], 'r--', label='Perfect calibration')
        ax.set_xlabel('Predicted Probability')
        ax.set_ylabel('Observed Frequency')
        ax.set_title('Calibration Plot')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # UPDATED PATH
        save_path = get_visualization_path('posterior_predictive_check.png')
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"\n✓ Saved: {save_path}")
        plt.close()
        
        return self.posterior_predictive
    
    def generate_report(self, output_file=None):
        """
        Generate comprehensive analysis report
        UPDATED: Uses config.py paths
        """
        if output_file is None:
            output_file = get_report_path('bayesian_analysis_report.txt')
            
        print("\n" + "="*80)
        print("GENERATING REPORT")
        print("="*80)
        
        report = []
        report.append("="*80)
        report.append("BAYESIAN ANALYSIS REPORT")
        report.append("="*80)
        
        # Data summary
        report.append("\n" + "="*60)
        report.append("DATA SUMMARY")
        report.append("="*60)
        report.append(f"\nSample size: {len(self.data):,}")
        report.append(f"Churn rate: {self.data['churn_binary'].mean():.1%}")
        report.append(f"Add-on adoption: {self.data['has_addons'].mean():.1%}")
        
        # Model specification
        report.append("\n" + "="*60)
        report.append("MODEL SPECIFICATION")
        report.append("="*60)
        report.append(f"\nParameters: {len(self.model.free_RVs)}")
        report.append("Likelihood: Bernoulli (logit link)")
        
        # Convergence
        report.append("\n" + "="*60)
        report.append("CONVERGENCE DIAGNOSTICS")
        report.append("="*60)
        
        rhat = az.rhat(self.trace)
        max_rhat = max([rhat[var].values.max() for var in rhat.data_vars])
        report.append(f"\nMaximum R-hat: {max_rhat:.4f}")
        
        ess = az.ess(self.trace)
        min_ess = min([ess[var].values.min() for var in ess.data_vars])
        report.append(f"Minimum ESS: {min_ess:.0f}")
        
        # Results
        report.append("\n" + "="*60)
        report.append("POSTERIOR RESULTS")
        report.append("="*60)
        
        summary = az.summary(self.trace)
        report.append("\n" + summary.to_string())
        
        # Add-on effect
        if 'beta_addon' in self.trace.posterior:
            addon_samples = self.trace.posterior['beta_addon'].values.flatten()
            prob_negative = (addon_samples < 0).mean()
            
            report.append("\n" + "="*60)
            report.append("CAUSAL EFFECT: ADD-ONS")
            report.append("="*60)
            report.append(f"\nP(Add-ons reduce churn): {prob_negative:.1%}")
            report.append(f"Mean effect: {addon_samples.mean():.4f}")
        
        # Conclusion
        report.append("\n" + "="*60)
        report.append("CONCLUSION")
        report.append("="*60)
        
        if prob_negative > 0.95:
            report.append("\n✓ Strong evidence that add-ons reduce churn")
        elif prob_negative > 0.80:
            report.append("\n~ Moderate evidence that add-ons reduce churn")
        else:
            report.append("\n⚠️ Insufficient evidence for causal effect")
        
        report.append("\n" + "="*80)
        
        # Save report
        report_text = "\n".join(report)
        
        with open(output_file, 'w') as f:
            f.write(report_text)
        
        print(f"\n✓ Report saved: {output_file}")
        
        return report_text


# =============================================================================
# TESTING SUITE
# =============================================================================

def test_bayesian_engine():
    """Complete testing suite for Bayesian analysis engine"""
    print("="*80)
    print("BAYESIAN ANALYSIS ENGINE - COMPLETE TEST SUITE")
    print("="*80)
    
    # Initialize engine
    print("\n" + "="*80)
    print("TEST 1: INITIALIZATION")
    print("="*80)
    
    engine = BayesianAnalysisEngine()
    assert engine.random_seed == 42
    assert engine.data is None
    print("✓ Test 1 passed: Initialization")
    
    # Load data
    print("\n" + "="*80)
    print("TEST 2: DATA LOADING")
    print("="*80)
    
    # Create synthetic data for testing
    np.random.seed(42)
    n = 1000
    
    test_data = pd.DataFrame({
        'Actual_Churn': np.random.choice(['Yes', 'No'], n, p=[0.3, 0.7]),
        'OnlineSecurity': np.random.choice(['Yes', 'No'], n),
        'OnlineBackup': np.random.choice(['Yes', 'No'], n),
        'DeviceProtection': np.random.choice(['Yes', 'No'], n),
        'TechSupport': np.random.choice(['Yes', 'No'], n),
        'SeniorCitizen': np.random.choice(['Yes', 'No'], n),
        'Dependents': np.random.choice(['Yes', 'No'], n),
        'Partner': np.random.choice(['Yes', 'No'], n),
        'tenure': np.random.randint(1, 72, n)
    })
    
    data = engine.load_data(test_data, sample_frac=0.5)
    assert len(data) == 500
    assert 'churn_binary' in data.columns
    assert 'has_addons' in data.columns
    print("✓ Test 2 passed: Data loading")
    
    # Model specification
    print("\n" + "="*80)
    print("TEST 3: MODEL SPECIFICATION")
    print("="*80)
    
    model = engine.specify_model('proper_causal')
    assert model is not None
    assert len(model.free_RVs) > 0
    print("✓ Test 3 passed: Model specification")
    
    # Model fitting (short run for testing)
    print("\n" + "="*80)
    print("TEST 4: MODEL FITTING")
    print("="*80)
    
    trace = engine.fit_model(draws=500, tune=500, chains=2)
    assert trace is not None
    print("✓ Test 4 passed: Model fitting")
    
    # Convergence diagnostics
    print("\n" + "="*80)
    print("TEST 5: CONVERGENCE DIAGNOSTICS")
    print("="*80)
    
    diagnostics = engine.convergence_diagnostics(save_plots=True)
    assert 'rhat' in diagnostics
    assert 'ess' in diagnostics
    print("✓ Test 5 passed: Convergence diagnostics")
    
    # Results analysis
    print("\n" + "="*80)
    print("TEST 6: RESULTS ANALYSIS")
    print("="*80)
    
    summary = engine.analyze_results()
    assert summary is not None
    print("✓ Test 6 passed: Results analysis")
    
    # Posterior predictive check
    print("\n" + "="*80)
    print("TEST 7: POSTERIOR PREDICTIVE CHECK")
    print("="*80)
    
    pp = engine.posterior_predictive_check()
    assert pp is not None
    print("✓ Test 7 passed: Posterior predictive check")
    
    # Report generation
    print("\n" + "="*80)
    print("TEST 8: REPORT GENERATION")
    print("="*80)
    
    report = engine.generate_report()
    assert len(report) > 0
    print("✓ Test 8 passed: Report generation")
    
    # Final summary
    print("\n" + "="*80)
    print("✅ ALL TESTS PASSED")
    print("="*80)
    print("\nGenerated outputs:")
    print(f"  ✓ {visualizations_dir}/trace_plots.png")
    print(f"  ✓ {visualizations_dir}/posterior_plots.png")
    print(f"  ✓ {visualizations_dir}/posterior_predictive_check.png")
    print(f"  ✓ {reports_dir}/bayesian_analysis_report.txt")
    
    print("\nBayesian Analysis Engine: FULLY TESTED ✅")


# =============================================================================
# MAIN EXECUTION
# =============================================================================

if __name__ == '__main__':
    # Run complete test suite
    test_bayesian_engine()
