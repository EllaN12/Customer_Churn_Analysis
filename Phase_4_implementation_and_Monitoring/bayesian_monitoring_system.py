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
import sys
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

sns.set_style('whitegrid')

# Centralized path config
_SCRIPT_DIR = Path(__file__).resolve().parent
_CONFIG_DIR = None
for parent in _SCRIPT_DIR.parents:
    candidate = parent / "Methodology for portfolio"
    if candidate.exists():
        _CONFIG_DIR = candidate
        break
if _CONFIG_DIR is None:
    raise ModuleNotFoundError(
        f"Could not locate 'Methodology for portfolio' from {_SCRIPT_DIR}"
    )

if str(_CONFIG_DIR) not in sys.path:
    sys.path.insert(0, str(_CONFIG_DIR))

try:
    from config import CONVERGENCE_PLOT_FILE, get_monitoring_path
except ModuleNotFoundError as exc:
    raise ModuleNotFoundError(
        f"Could not import config.py from {_CONFIG_DIR}"
    ) from exc


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
        
        # Informed treatment priors from BAYESIAN_TEST_DESIGN_UPDATES.md:
        # T1 → Beta(2,9): modest reduction expected
        # T2 → Beta(2,12): moderate reduction expected
        # T3 → Beta(1,9): largest reduction expected
        # Additional treatment arms beyond 3 fall back to Beta(2,9)
        treatment_priors = [
            (2, 9),   # T1
            (2, 12),  # T2
            (1, 9),   # T3
        ]

        with pm.Model() as model:
            # Priors for each arm
            # Control uses informed prior based on segment baseline_rate
            # Treatments use design-informed priors (not flat Beta(2,2))
            priors = []
            for i in range(self.n_arms):
                if i == 0:  # Control — informed from segment baseline
                    alpha_prior = self.baseline_rate * 10
                    beta_prior = (1 - self.baseline_rate) * 10
                else:  # Treatments — use design-doc informed priors
                    t_idx = min(i - 1, len(treatment_priors) - 1)
                    alpha_prior, beta_prior = treatment_priors[t_idx]

                p = pm.Beta(f'p_arm_{i}', alpha=alpha_prior, beta=beta_prior)
                priors.append(p)

            # Likelihood for each arm
            for i, (p, d) in enumerate(zip(priors, arm_data)):
                if d['n'] > 0:  # Only if we have data
                    pm.Binomial(f'obs_arm_{i}', n=d['n'], p=p, observed=d['successes'])

            # Sample — 4 chains per design spec (was 2)
            trace = pm.sample(2000, tune=1000, chains=4, return_inferencedata=True,
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

            # P(treatment better than control by at least 8pp) — design spec: min_effect=0.08
            diff = control - treatment
            prob_superior_8 = (diff > 0.08).mean()

            # Expected effect size
            effect_size = diff.mean()

            # ROPE check: P(|diff| < 0.02) — Region Of Practical Equivalence
            rope_prob = (np.abs(diff) < 0.02).mean()

            superiority_probs[arm] = prob_superior_8
            effect_sizes[arm] = effect_size

            print(f"\nArm {arm}:")
            print(f"  P(reduces churn >8pp): {prob_superior_8:.1%}")
            print(f"  Expected effect:        {effect_size*100:+.1f} percentage points")
            print(f"  P(within ROPE ±2pp):    {rope_prob:.1%}")
        
        # DECISION RULES
        decision = {
            'action': 'continue',
            'reason': None,
            'recommended_winner': None,
            'week': week_number
        }
        
        # Rule 1: SUPERIORITY — design spec: P > 0.95 AND effect > 8pp (was 0.90 / 10pp)
        best_arm = max(superiority_probs, key=superiority_probs.get)
        best_prob = superiority_probs[best_arm]

        if best_prob > 0.95 and effect_sizes[best_arm] > 0.08:
            arm_data = data[data['arm'] == best_arm]
            # Require minimum sample (at least 50 per arm)
            if len(arm_data) >= 50:
                decision = {
                    'action': 'superiority',
                    'reason': f'Arm {best_arm} shows >95% probability of >8pp improvement',
                    'recommended_winner': best_arm,
                    'probability': best_prob,
                    'effect_size': effect_sizes[best_arm],
                    'week': week_number
                }
                print(f"\n🎉 SUPERIORITY DETECTED: Arm {best_arm}")
                print(f"   Probability: {best_prob:.1%}")
                print(f"   Effect: {effect_sizes[best_arm]*100:+.1f} pp")

        # Rule 2: FUTILITY — design spec: P < 0.05 (was 0.20 — 4x too lenient)
        if decision['action'] == 'continue':
            max_prob_helps = max([(posteriors[0] - posteriors[i] > 0).mean()
                                  for i in range(1, self.n_arms)])

            if week_number >= 6 and max_prob_helps < 0.05:
                decision = {
                    'action': 'futility',
                    'reason': 'No treatment shows >5% probability of helping',
                    'max_prob_helps': max_prob_helps,
                    'week': week_number
                }
                print(f"\n⚠️ FUTILITY: No treatments effective")
        
        # Rule 3: ROPE EQUIVALENCE — design spec: ROPE = (-0.02, 0.02)
        # If P(|diff| < 0.02) > 80% for all arms → treatments are practically equivalent
        if decision['action'] == 'continue' and week_number >= 8:
            all_in_rope = True
            for i in range(1, self.n_arms):
                diff = control - posteriors[i]
                prob_in_rope = (np.abs(diff) < 0.02).mean()
                if prob_in_rope < 0.80:
                    all_in_rope = False
                    break

            if all_in_rope:
                decision = {
                    'action': 'equivalence',
                    'reason': 'All arms within ROPE (±2pp) with >80% probability',
                    'week': week_number
                }
                print(f"\n= ROPE EQUIVALENCE: All treatments practically identical")
        
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
            prob = (control - posteriors[arm] > 0.08).mean()  # 8pp minimum effect
            probs.append(prob)
            arms.append(f'T{arm}')

        colors = ['green' if p > 0.95 else 'orange' if p > 0.80 else 'red' for p in probs]
        bars = ax.barh(arms, probs, color=colors, alpha=0.7, edgecolor='black')

        ax.axvline(0.95, color='green', linestyle='--', linewidth=2, label='95% threshold (design spec)')
        ax.set_xlabel('P(Reduction > 8pp)', fontsize=11)
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
        
        ax.axvline(8, color='green', linestyle='--', linewidth=2, label='8pp minimum effect (design spec)')
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
        
        filename = get_monitoring_path(f'monitoring_week_{week_number}.png')
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        print(f"\n✓ Saved: {filename}")
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
                prob = (control - treatment > 0.08).mean()  # 8pp minimum effect
                probs_over_time.append(prob)

            ax.plot(weeks, probs_over_time, marker='o', linewidth=2,
                   markersize=8, label=f'Treatment {arm}')

        ax.axhline(0.95, color='green', linestyle='--', linewidth=2, label='95% threshold (design spec)')
        ax.axhline(0.80, color='orange', linestyle='--', linewidth=1, alpha=0.5)

        ax.set_xlabel('Week', fontsize=12)
        ax.set_ylabel('P(Reduction > 8pp)', fontsize=12)
        ax.set_title('Convergence: Probability of Superiority Over Time',
                    fontsize=14, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.set_ylim(0, 1)
        
        plt.tight_layout()
        plt.savefig(CONVERGENCE_PLOT_FILE, dpi=300, bbox_inches='tight')
        print(f"\n✓ Saved: {CONVERGENCE_PLOT_FILE}")
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
    # Segment baseline: observed churn rate for 0–6 month tenure customers = 74.7%
    # (NOT the full-population 26.5%, NOT the ML model's mean predicted probability)
    monitor = BayesianMonitoringSystem(
        experiment_name='Early Tenure Intervention (0–6 months)',
        n_arms=4,
        baseline_rate=0.747
    )

    # Simulate 8 weeks of data collection
    # True effects based on segment baseline 74.7%
    # T1 (Welcome Call):   −10pp → 64.7%
    # T2 (Smart Start):    −15pp → 59.7%
    # T3 (Concierge):      −20pp → 54.7%
    true_rates = [0.747, 0.647, 0.597, 0.547]
    
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

    """)
