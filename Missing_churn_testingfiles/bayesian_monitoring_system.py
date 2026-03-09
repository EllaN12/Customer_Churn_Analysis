"""
Bayesian Sequential Monitoring System
Portfolio Project: Real-time Experiment Monitoring with Stopping Rules

Monitors experiments continuously and applies Bayesian decision criteria:
- Superiority: Clear winner detected
- Futility: No treatment helps
- Equivalence: All treatments similar

Used in conjunction with experiment_randomization.py
"""

import pandas as pd
import numpy as np
import pymc as pm
import arviz as az
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

sns.set_style('whitegrid')


class BayesianMonitoringSystem:
    """
    Continuous monitoring system for randomized experiments
    
    Features:
    - Weekly posterior updates
    - Automated stopping rule checks
    - Visualization of convergence
    - Decision recommendations
    """
    
    def __init__(self, experiment_name, n_arms, baseline_rate=None):
        """
        Parameters:
        -----------
        experiment_name : str
            Name of the experiment
        n_arms : int
            Number of arms (including control)
        baseline_rate : float
            Prior estimate of control group rate (e.g., 0.609 for early tenure)
        """
        self.experiment_name = experiment_name
        self.n_arms = n_arms
        self.baseline_rate = baseline_rate or 0.5
        
        # Storage for updates
        self.weekly_updates = []
        self.traces = []
        
        print(f"✓ Initialized monitoring for '{experiment_name}'")
        print(f"  - Arms: {n_arms}")
        print(f"  - Baseline prior: {self.baseline_rate:.1%}")
    
    def weekly_update(self, data, week_number):
        """
        Perform weekly Bayesian analysis
        
        Parameters:
        -----------
        data : pd.DataFrame
            Columns: arm (0, 1, 2...), outcome (0=no churn, 1=churn)
        week_number : int
            Current week of experiment
        
        Returns:
        --------
        dict : Analysis results and stopping decision
        """
        print("\n" + "="*80)
        print(f"WEEK {week_number} ANALYSIS - {self.experiment_name}")
        print("="*80)
        
        # Data summary
        summary = data.groupby('arm').agg({
            'outcome': ['count', 'sum', 'mean']
        }).round(3)
        summary.columns = ['N', 'Churned', 'Churn_Rate']
        
        print("\nCurrent Data:")
        print(summary)
        
        # Bayesian analysis
        trace = self._fit_bayesian_model(data)
        
        # Stopping criteria
        stopping_decision = self._check_stopping_rules(trace, data, week_number)
        
        # Store results
        update_record = {
            'week': week_number,
            'data_summary': summary.to_dict(),
            'stopping_decision': stopping_decision,
            'timestamp': datetime.now()
        }
        
        self.weekly_updates.append(update_record)
        self.traces.append(trace)
        
        # Visualization
        self._plot_weekly_update(trace, week_number, stopping_decision)
        
        return stopping_decision
    
    def _fit_bayesian_model(self, data):
        """
        Fit Bayesian Beta-Binomial model
        """
        print("\nFitting Bayesian model...")
        
        # Prepare data by arm
        arm_data = []
        for arm in range(self.n_arms):
            arm_df = data[data['arm'] == arm]
            arm_data.append({
                'n': len(arm_df),
                'successes': arm_df['outcome'].sum()
            })
        
        with pm.Model() as model:
            # Priors for each arm
            # Control uses informed prior, treatments use weakly informative
            priors = []
            for i in range(self.n_arms):
                if i == 0:  # Control
                    # Informed prior based on baseline
                    alpha_prior = self.baseline_rate * 10
                    beta_prior = (1 - self.baseline_rate) * 10
                else:  # Treatments
                    # Weakly informative (expect reduction)
                    alpha_prior = 2
                    beta_prior = 2
                
                p = pm.Beta(f'p_arm_{i}', alpha=alpha_prior, beta=beta_prior)
                priors.append(p)
            
            # Likelihood for each arm
            for i, (p, d) in enumerate(zip(priors, arm_data)):
                if d['n'] > 0:  # Only if we have data
                    pm.Binomial(f'obs_arm_{i}', n=d['n'], p=p, observed=d['successes'])
            
            # Sample
            trace = pm.sample(2000, tune=1000, chains=2, return_inferencedata=True,
                            progressbar=False, target_accept=0.95)
        
        print("✓ Model fitted successfully")
        
        return trace
    
    def _check_stopping_rules(self, trace, data, week_number):
        """
        Check Bayesian stopping criteria
        
        Returns decision: 'continue', 'superiority', 'futility', or 'equivalence'
        """
        print("\n" + "-"*60)
        print("CHECKING STOPPING RULES")
        print("-"*60)
        
        # Extract posterior samples
        posteriors = {}
        for i in range(self.n_arms):
            posteriors[i] = trace.posterior[f'p_arm_{i}'].values.flatten()
        
        # Calculate probabilities of superiority
        control = posteriors[0]
        
        superiority_probs = {}
        effect_sizes = {}
        
        for arm in range(1, self.n_arms):
            treatment = posteriors[arm]
            
            # P(treatment better than control by at least 10%)
            diff = control - treatment
            prob_superior_10 = (diff > 0.10).mean()
            
            # Expected effect size
            effect_size = diff.mean()
            
            superiority_probs[arm] = prob_superior_10
            effect_sizes[arm] = effect_size
            
            print(f"\nArm {arm}:")
            print(f"  P(reduces churn >10%): {prob_superior_10:.1%}")
            print(f"  Expected effect: {effect_size*100:+.1f} percentage points")
        
        # DECISION RULES
        decision = {
            'action': 'continue',
            'reason': None,
            'recommended_winner': None,
            'week': week_number
        }
        
        # Rule 1: SUPERIORITY (at least one treatment clearly wins)
        best_arm = max(superiority_probs, key=superiority_probs.get)
        best_prob = superiority_probs[best_arm]
        
        if best_prob > 0.90 and effect_sizes[best_arm] > 0.10:
            # Get sample size for this arm
            arm_data = data[data['arm'] == best_arm]
            
            # Require minimum sample (at least 50 per arm)
            if len(arm_data) >= 50:
                decision = {
                    'action': 'superiority',
                    'reason': f'Arm {best_arm} shows >90% probability of >10% improvement',
                    'recommended_winner': best_arm,
                    'probability': best_prob,
                    'effect_size': effect_sizes[best_arm],
                    'week': week_number
                }
                print(f"\n🎉 SUPERIORITY DETECTED: Arm {best_arm}")
                print(f"   Probability: {best_prob:.1%}")
                print(f"   Effect: {effect_sizes[best_arm]*100:+.1f} pp")
        
        # Rule 2: FUTILITY (no treatment helps)
        if decision['action'] == 'continue':
            max_prob_helps = max([(posteriors[0] - posteriors[i] > 0).mean() 
                                 for i in range(1, self.n_arms)])
            
            if week_number >= 6 and max_prob_helps < 0.20:
                decision = {
                    'action': 'futility',
                    'reason': 'No treatment shows >20% probability of helping',
                    'max_prob_helps': max_prob_helps,
                    'week': week_number
                }
                print(f"\n⚠️ FUTILITY: No treatments effective")
        
        # Rule 3: EQUIVALENCE (all treatments similar)
        if decision['action'] == 'continue' and week_number >= 8:
            # Check if all arms within 3% of each other
            all_similar = True
            for i in range(1, self.n_arms):
                diff = control - posteriors[i]
                prob_within_3 = (np.abs(diff) < 0.03).mean()
                if prob_within_3 < 0.80:
                    all_similar = False
                    break
            
            if all_similar:
                decision = {
                    'action': 'equivalence',
                    'reason': 'All arms within 3% of each other (>80% probability)',
                    'week': week_number
                }
                print(f"\n= EQUIVALENCE: All treatments similar")
        
        # Default: Continue
        if decision['action'] == 'continue':
            print(f"\n→ CONTINUE: Keep collecting data")
            print(f"   Best arm so far: {best_arm} ({best_prob:.1%})")
        
        return decision
    
    def _plot_weekly_update(self, trace, week_number, decision):
        """
        Create visualization of current state
        """
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        
        # Extract posteriors
        posteriors = {}
        for i in range(self.n_arms):
            posteriors[i] = trace.posterior[f'p_arm_{i}'].values.flatten()
        
        # Plot 1: Posterior distributions
        ax = axes[0, 0]
        for arm in range(self.n_arms):
            label = 'Control' if arm == 0 else f'Treatment {arm}'
            ax.hist(posteriors[arm], bins=50, alpha=0.6, label=label, density=True)
        
        ax.set_xlabel('Churn Rate', fontsize=11)
        ax.set_ylabel('Density', fontsize=11)
        ax.set_title(f'Week {week_number}: Posterior Distributions', fontsize=12, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Plot 2: Probability of superiority
        ax = axes[0, 1]
        control = posteriors[0]
        
        probs = []
        arms = []
        for arm in range(1, self.n_arms):
            prob = (control - posteriors[arm] > 0.10).mean()
            probs.append(prob)
            arms.append(f'T{arm}')
        
        colors = ['green' if p > 0.90 else 'orange' if p > 0.70 else 'red' for p in probs]
        bars = ax.barh(arms, probs, color=colors, alpha=0.7, edgecolor='black')
        
        ax.axvline(0.90, color='green', linestyle='--', linewidth=2, label='90% threshold')
        ax.set_xlabel('P(Reduction > 10%)', fontsize=11)
        ax.set_title('Probability of Superiority', fontsize=12, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Add value labels
        for bar, prob in zip(bars, probs):
            ax.text(prob + 0.02, bar.get_y() + bar.get_height()/2,
                   f'{prob:.1%}', va='center', fontweight='bold')
        
        # Plot 3: Expected effect sizes
        ax = axes[1, 0]
        effects = []
        for arm in range(1, self.n_arms):
            effect = (control - posteriors[arm]).mean()
            effects.append(effect)
        
        colors = ['green' if e > 0.10 else 'orange' if e > 0.05 else 'red' for e in effects]
        bars = ax.barh(arms, [e*100 for e in effects], color=colors, alpha=0.7, edgecolor='black')
        
        ax.axvline(10, color='green', linestyle='--', linewidth=2, label='10% target')
        ax.set_xlabel('Effect Size (percentage points)', fontsize=11)
        ax.set_title('Expected Effect Sizes', fontsize=12, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Plot 4: Decision status
        ax = axes[1, 1]
        ax.axis('off')
        
        # Decision box
        decision_text = f"WEEK {week_number} DECISION\n\n"
        decision_text += f"Action: {decision['action'].upper()}\n\n"
        
        if decision['action'] == 'superiority':
            decision_text += f"Winner: Treatment {decision['recommended_winner']}\n"
            decision_text += f"Probability: {decision['probability']:.1%}\n"
            decision_text += f"Effect: {decision['effect_size']*100:+.1f} pp\n\n"
            decision_text += "✅ STOP & IMPLEMENT"
            box_color = 'lightgreen'
        elif decision['action'] == 'futility':
            decision_text += "No treatments effective\n\n"
            decision_text += "⚠️ STOP EXPERIMENT"
            box_color = 'lightcoral'
        elif decision['action'] == 'equivalence':
            decision_text += "All treatments similar\n\n"
            decision_text += "= STOP (No difference)"
            box_color = 'lightyellow'
        else:
            decision_text += "Continue data collection\n\n"
            decision_text += "→ Monitor next week"
            box_color = 'lightblue'
        
        ax.text(0.5, 0.5, decision_text, ha='center', va='center',
               fontsize=12, fontweight='bold',
               bbox=dict(boxstyle='round', facecolor=box_color, alpha=0.8, 
                        edgecolor='black', linewidth=2))
        
        plt.suptitle(f'{self.experiment_name} - Week {week_number} Update',
                    fontsize=14, fontweight='bold', y=0.98)
        
        plt.tight_layout()
        
        filename = f'/mnt/user-data/outputs/monitoring_week_{week_number}.png'
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        print(f"\n✓ Saved: monitoring_week_{week_number}.png")
        plt.close()
    
    def generate_final_report(self):
        """
        Generate final experiment report
        """
        print("\n" + "="*80)
        print("FINAL EXPERIMENT REPORT")
        print("="*80)
        
        if not self.weekly_updates:
            print("No updates recorded yet")
            return
        
        final_update = self.weekly_updates[-1]
        final_decision = final_update['stopping_decision']
        
        print(f"\nExperiment: {self.experiment_name}")
        print(f"Duration: {len(self.weekly_updates)} weeks")
        print(f"Final Decision: {final_decision['action'].upper()}")
        
        if final_decision['action'] == 'superiority':
            print(f"\n✅ WINNER DETECTED:")
            print(f"   Treatment {final_decision['recommended_winner']}")
            print(f"   Probability: {final_decision['probability']:.1%}")
            print(f"   Effect Size: {final_decision['effect_size']*100:+.1f} pp")
            print(f"\n   RECOMMENDATION: Implement Treatment {final_decision['recommended_winner']}")
        
        elif final_decision['action'] == 'futility':
            print(f"\n⚠️ NO EFFECTIVE TREATMENT FOUND")
            print(f"   RECOMMENDATION: Do not implement any intervention")
        
        elif final_decision['action'] == 'equivalence':
            print(f"\n= ALL TREATMENTS EQUIVALENT")
            print(f"   RECOMMENDATION: Choose cheapest option")
        
        else:
            print(f"\n→ EXPERIMENT ONGOING")
            print(f"   RECOMMENDATION: Continue monitoring")
        
        # Convergence plot
        self._plot_convergence()
    
    def _plot_convergence(self):
        """
        Plot how probabilities evolved over time
        """
        if len(self.traces) < 2:
            return
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        weeks = range(1, len(self.traces) + 1)
        
        # Calculate P(superior) for each week
        for arm in range(1, self.n_arms):
            probs_over_time = []
            
            for trace in self.traces:
                control = trace.posterior[f'p_arm_0'].values.flatten()
                treatment = trace.posterior[f'p_arm_{arm}'].values.flatten()
                prob = (control - treatment > 0.10).mean()
                probs_over_time.append(prob)
            
            ax.plot(weeks, probs_over_time, marker='o', linewidth=2, 
                   markersize=8, label=f'Treatment {arm}')
        
        ax.axhline(0.90, color='green', linestyle='--', linewidth=2, label='90% threshold')
        ax.axhline(0.80, color='orange', linestyle='--', linewidth=1, alpha=0.5)
        
        ax.set_xlabel('Week', fontsize=12)
        ax.set_ylabel('P(Reduction > 10%)', fontsize=12)
        ax.set_title('Convergence: Probability of Superiority Over Time',
                    fontsize=14, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.set_ylim(0, 1)
        
        plt.tight_layout()
        plt.savefig('/mnt/user-data/outputs/convergence_plot.png', dpi=300, bbox_inches='tight')
        print("\n✓ Saved: convergence_plot.png")
        plt.close()


# =============================================================================
# SIMULATION DEMO
# =============================================================================

def demo_monitoring_system():
    """
    Demonstrate the monitoring system with simulated weekly data
    """
    print("="*80)
    print("BAYESIAN MONITORING SYSTEM DEMONSTRATION")
    print("="*80)
    
    # Initialize for early tenure experiment
    monitor = BayesianMonitoringSystem(
        experiment_name='Early Tenure Intervention',
        n_arms=4,
        baseline_rate=0.609
    )
    
    # Simulate 8 weeks of data collection
    # True effects: Control 60.9%, T1: 50.9%, T2: 45.9%, T3: 40.9%
    true_rates = [0.609, 0.509, 0.459, 0.409]
    
    np.random.seed(42)
    
    all_data = []
    
    for week in range(1, 9):
        # Generate data for this week (50 customers per arm per week)
        week_data = []
        
        for arm, rate in enumerate(true_rates):
            outcomes = np.random.binomial(1, rate, size=50)
            for outcome in outcomes:
                week_data.append({'arm': arm, 'outcome': outcome})
        
        all_data.extend(week_data)
        
        # Cumulative data
        cumulative_df = pd.DataFrame(all_data)
        
        # Weekly analysis
        decision = monitor.weekly_update(cumulative_df, week)
        
        # Stop if decision made
        if decision['action'] != 'continue':
            print(f"\n🛑 STOPPING at Week {week}")
            break
    
    # Final report
    monitor.generate_final_report()
    
    print("\n" + "="*80)
    print("✅ DEMONSTRATION COMPLETE")
    print("="*80)


# =============================================================================
# MAIN EXECUTION
# =============================================================================

if __name__ == '__main__':
    demo_monitoring_system()
    
    print("\n" + "="*80)
    print("Portfolio Value:")
    print("="*80)
    print("""
This monitoring system demonstrates:

✓ Bayesian sequential testing
  - Update posteriors weekly
  - No alpha inflation from peeking
  
✓ Automated decision making
  - Superiority (winner detected)
  - Futility (no treatment helps)
  - Equivalence (all similar)
  
✓ Visual convergence tracking
  - Probability evolution over time
  - Weekly status dashboards
  
✓ Production-ready framework
  - Can integrate with real data pipeline
  - Automated alerts and reporting

In interviews, you can show:
1. The code (demonstrates Bayesian expertise)
2. Weekly monitoring charts (visual convergence)
3. Automated stopping rules (practical decision framework)
4. Expected early stopping (save time & money)

This shows you don't just design experiments—
you build systems to monitor and decide optimally.
    """)
