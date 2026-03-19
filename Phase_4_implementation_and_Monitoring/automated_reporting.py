"""
Automated Reporting System
Portfolio Project: Stakeholder-Friendly Experiment Reports

Generates:
- Weekly experiment summaries
- Executive dashboards
- Decision memos
- Technical reports

Can be scheduled via cron or integrated with data pipeline
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Import configuration
from config import (
    results_dir, reports_dir, visualizations_dir,
    get_report_path, get_visualization_path
)

sns.set_style('whitegrid')


class AutomatedReporter:
    """
    Generates stakeholder reports for running experiments.
    """
    
    def __init__(self, experiment_name, output_dir=None):
        """
        Parameters:
        -----------
        experiment_name : str
            Name of the experiment
        output_dir : str, optional
            Output directory (default: uses config.reports_dir)
        """
        self.experiment_name = experiment_name
        
        # Use config directory if not specified
        if output_dir is None:
            self.output_dir = Path(reports_dir)
        else:
            self.output_dir = Path(output_dir)
        
        self.output_dir.mkdir(exist_ok=True)
        
        print(f"✓ AutomatedReporter initialized for '{experiment_name}'")
        print(f"  Output directory: {self.output_dir}")
        
    def generate_weekly_summary(self, data, week_number, posteriors, decision):
        """
        Generate concise weekly summary for stakeholders
        """
        report = []
        
        # Header
        report.append("="*80)
        report.append(f"WEEKLY EXPERIMENT SUMMARY - WEEK {week_number}")
        report.append(f"Experiment: {self.experiment_name}")
        report.append(f"Date: {datetime.now().strftime('%B %d, %Y')}")
        report.append("="*80)
        
        # Executive Summary
        report.append("\n📊 EXECUTIVE SUMMARY")
        report.append("-"*80)
        
        summary_stats = data.groupby('arm').agg({
            'outcome': ['count', 'sum', 'mean']
        })
        summary_stats.columns = ['N', 'Churned', 'Rate']
        
        total_enrolled = len(data)
        overall_churn = data['outcome'].mean()
        
        report.append(f"\nTotal Enrolled: {total_enrolled:,} customers")
        report.append(f"Overall Churn: {overall_churn:.1%}")
        report.append(f"Duration: {week_number} weeks")
        
        # Current Results
        report.append("\n\n📈 CURRENT RESULTS")
        report.append("-"*80)
        
        report.append(f"\n{'Arm':<15} {'N':>8} {'Churned':>10} {'Rate':>10}")
        report.append("-"*50)
        
        for arm in sorted(summary_stats.index):
            arm_name = 'Control' if arm == 0 else f'Treatment {arm}'
            n = int(summary_stats.loc[arm, 'N'])
            churned = int(summary_stats.loc[arm, 'Churned'])
            rate = summary_stats.loc[arm, 'Rate']
            
            report.append(f"{arm_name:<15} {n:>8} {churned:>10} {rate:>9.1%}")
        
        # Treatment Performance
        if len(posteriors) > 1:
            report.append("\n\n🎯 TREATMENT PERFORMANCE")
            report.append("-"*80)
            
            control = posteriors[0]
            
            for arm in range(1, len(posteriors)):
                treatment = posteriors[arm]
                diff = control - treatment
                
                prob_helps = (diff > 0).mean()
                prob_10plus = (diff > 0.10).mean()
                expected_effect = diff.mean()
                ci_lower = np.percentile(diff, 2.5)
                ci_upper = np.percentile(diff, 97.5)
                
                report.append(f"\nTreatment {arm}:")
                report.append(f"  Probability helps at all: {prob_helps:.1%}")
                report.append(f"  Probability >10% reduction: {prob_10plus:.1%}")
                report.append(f"  Expected effect: {expected_effect*100:+.1f} pp")
                report.append(f"  95% Confidence: [{ci_lower*100:.1f}%, {ci_upper*100:.1f}%]")
        
        # Decision
        report.append("\n\n🎯 DECISION & NEXT STEPS")
        report.append("-"*80)
        
        if decision['action'] == 'superiority':
            report.append(f"\n✅ SUPERIORITY DETECTED")
            report.append(f"\nWinner: Treatment {decision['winner']}")
            report.append(f"Confidence: {decision['probability']:.1%}")
            report.append(f"Expected Impact: {decision['effect']*100:+.1f} percentage points")
            report.append(f"\n⚡ RECOMMENDATION: STOP EXPERIMENT & IMPLEMENT T{decision['winner']}")
        
        elif decision['action'] == 'futility':
            report.append(f"\n⚠️ FUTILITY DETECTED")
            report.append(f"\n{decision['reason']}")
            report.append(f"\n⚡ RECOMMENDATION: STOP EXPERIMENT (No effective treatment)")
        
        elif decision['action'] == 'equivalence':
            report.append(f"\n= EQUIVALENCE DETECTED")
            report.append(f"\nAll treatments perform similarly")
            report.append(f"\n⚡ RECOMMENDATION: Choose lowest-cost option")
        
        else:
            report.append(f"\n→ CONTINUE MONITORING")
            report.append(f"\n{decision['reason']}")
            report.append(f"\n⚡ NEXT REVIEW: Week {week_number + 1}")
        
        # Footer
        report.append("\n" + "="*80)
        report.append("For technical details, see full analysis report")
        report.append("Questions? Contact: Data Science Team")
        report.append("="*80)
        
        # Save report
        report_text = "\n".join(report)
        
        filename = get_report_path(f'weekly_summary_week_{week_number}.txt')
        with open(filename, 'w') as f:
            f.write(report_text)
        
        print(f"✓ Saved weekly summary: {filename}")
        
        return report_text
    
    def generate_executive_dashboard(self, data, week_number, posteriors, decision):
        """
        Generate visual dashboard for executives.
        """
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle(f'{self.experiment_name} - Week {week_number} Dashboard',
                    fontsize=18, fontweight='bold', y=0.98)
        
        # Plot 1: Enrollment over time
        ax = axes[0, 0]
        
        # Simulate enrollment timeline
        weeks = np.arange(1, week_number + 1)
        cumulative = []
        
        for w in weeks:
            n = len(data[data['arm'] == 0]) * w / week_number
            cumulative.append(n * 4)  # 4 arms
        
        ax.plot(weeks, cumulative, marker='o', linewidth=3, markersize=8, color='steelblue')
        ax.set_xlabel('Week', fontsize=12, fontweight='bold')
        ax.set_ylabel('Cumulative Enrollment', fontsize=12, fontweight='bold')
        ax.set_title('Enrollment Progress', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        
        # Target line
        target = len(data)
        ax.axhline(target, color='green', linestyle='--', linewidth=2, label=f'Target: {target}')
        ax.legend()
        
        # Plot 2: Current churn rates
        ax = axes[0, 1]
        
        summary = data.groupby('arm')['outcome'].mean().sort_index()
        arms = ['Control' if i == 0 else f'T{i}' for i in summary.index]
        
        colors = ['coral'] + ['steelblue'] * (len(summary) - 1)
        bars = ax.bar(arms, summary.values, color=colors, alpha=0.7, edgecolor='black', linewidth=2)
        
        ax.set_ylabel('Churn Rate', fontsize=12, fontweight='bold')
        ax.set_title('Current Churn Rates by Arm', fontsize=14, fontweight='bold')
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f'{y:.0%}'))
        ax.grid(True, alpha=0.3, axis='y')
        
        # Add value labels
        for bar, val in zip(bars, summary.values):
            ax.text(bar.get_x() + bar.get_width()/2, val,
                   f'{val:.1%}', ha='center', va='bottom', fontweight='bold', fontsize=11)
        
        # Plot 3: Probability of superiority
        ax = axes[1, 0]
        
        if len(posteriors) > 1:
            control = posteriors[0]
            
            probs = []
            arms_list = []
            
            for arm in range(1, len(posteriors)):
                treatment = posteriors[arm]
                prob = (control - treatment > 0.10).mean()
                probs.append(prob)
                arms_list.append(f'T{arm}')
            
            colors = ['green' if p > 0.90 else 'orange' if p > 0.70 else 'red' for p in probs]
            bars = ax.barh(arms_list, probs, color=colors, alpha=0.7, edgecolor='black', linewidth=2)
            
            ax.axvline(0.90, color='green', linestyle='--', linewidth=2.5, label='90% threshold')
            ax.set_xlabel('Probability of >10% Reduction', fontsize=12, fontweight='bold')
            ax.set_title('Treatment Performance', fontsize=14, fontweight='bold')
            ax.legend()
            ax.grid(True, alpha=0.3)
            
            # Add value labels
            for bar, prob in zip(bars, probs):
                ax.text(prob + 0.02, bar.get_y() + bar.get_height()/2,
                       f'{prob:.0%}', va='center', fontweight='bold', fontsize=11)
        
        # Plot 4: Decision status
        ax = axes[1, 1]
        ax.axis('off')
        
        # Decision text box
        if decision['action'] == 'superiority':
            text = (
                f"✅ WINNER FOUND\n\n"
                f"Treatment {decision['winner']}\n"
                f"Confidence: {decision['probability']:.0%}\n"
                f"Effect: {decision['effect']*100:+.1f} pp\n\n"
                f"STOP & IMPLEMENT"
            )
            box_color = 'lightgreen'
        elif decision['action'] == 'futility':
            text = (
                f"⚠️ NO WINNER\n\n"
                f"No effective treatment\n\n"
                f"STOP EXPERIMENT"
            )
            box_color = 'lightcoral'
        elif decision['action'] == 'equivalence':
            text = (
                f"= ALL SIMILAR\n\n"
                f"No significant difference\n\n"
                f"Choose cheapest option"
            )
            box_color = 'lightyellow'
        else:
            best_arm = max(range(1, len(posteriors)), 
                          key=lambda x: (posteriors[0] - posteriors[x] > 0.10).mean())
            text = (
                f"→ CONTINUE\n\n"
                f"Week {week_number} of 8-10\n"
                f"Leading: T{best_arm}\n\n"
                f"Review next week"
            )
            box_color = 'lightblue'
        
        ax.text(0.5, 0.5, text, ha='center', va='center',
               fontsize=16, fontweight='bold',
               bbox=dict(boxstyle='round,pad=1', facecolor=box_color, 
                        edgecolor='black', linewidth=3, alpha=0.9))
        ax.set_title('Decision Status', fontsize=14, fontweight='bold', pad=20)
        
        plt.tight_layout()
        
        filename = get_visualization_path(f'executive_dashboard_week_{week_number}.png')
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        print(f"✓ Saved executive dashboard: {filename}")
        plt.close()
    
    def generate_decision_memo(self, decision, week_number, expected_roi=None):
        """
        Generate executive decision memo.
        """
        memo = []
        
        memo.append("="*80)
        memo.append("EXECUTIVE DECISION MEMO")
        memo.append("="*80)
        
        memo.append(f"\nTO: Executive Leadership")
        memo.append(f"FROM: Data Science Team")
        memo.append(f"DATE: {datetime.now().strftime('%B %d, %Y')}")
        memo.append(f"RE: {self.experiment_name} - Week {week_number} Decision")
        
        memo.append("\n" + "="*80)
        memo.append("RECOMMENDATION")
        memo.append("="*80)
        
        if decision['action'] == 'superiority':
            memo.append(f"\n✅ IMPLEMENT TREATMENT {decision['winner']}")
            memo.append(f"\n**Confidence Level:** {decision['probability']:.0%}")
            memo.append(f"**Expected Impact:** {decision['effect']*100:+.1f} percentage point reduction in churn")
            
            if expected_roi:
                memo.append(f"\n**Financial Impact:**")
                memo.append(f"  - Expected annual profit: ${expected_roi['annual_profit']:,.0f}")
                memo.append(f"  - ROI: {expected_roi['roi']:.0%}")
                memo.append(f"  - Payback period: {expected_roi['payback_months']:.1f} months")
            
            memo.append(f"\n**Next Steps:**")
            memo.append(f"  1. Stop enrolling new customers to control/other treatments")
            memo.append(f"  2. Implement Treatment {decision['winner']} for all new customers")
            memo.append(f"  3. Monitor performance for 90 days")
            memo.append(f"  4. Scale to existing customer base if successful")
        
        elif decision['action'] == 'futility':
            memo.append(f"\n⚠️ STOP EXPERIMENT - NO EFFECTIVE TREATMENT FOUND")
            memo.append(f"\n**Finding:** {decision['reason']}")
            memo.append(f"\n**Recommendation:** Do not implement any tested interventions")
            memo.append(f"\n**Next Steps:**")
            memo.append(f"  1. Stop experiment immediately")
            memo.append(f"  2. Conduct root cause analysis")
            memo.append(f"  3. Design new interventions based on learnings")
        
        elif decision['action'] == 'equivalence':
            memo.append(f"\n= ALL TREATMENTS PERFORM SIMILARLY")
            memo.append(f"\n**Recommendation:** Implement lowest-cost option")
            memo.append(f"\n**Next Steps:**")
            memo.append(f"  1. Compare implementation costs")
            memo.append(f"  2. Choose most cost-effective approach")
            memo.append(f"  3. Monitor for 60 days")
        
        else:
            memo.append(f"\n→ CONTINUE EXPERIMENT")
            memo.append(f"\n**Status:** Insufficient evidence to make decision")
            memo.append(f"**Current Week:** {week_number} of 8-10 planned")
            memo.append(f"\n**Next Review:** Week {week_number + 1}")
            memo.append(f"\n**Next Steps:**")
            memo.append(f"  1. Continue enrollment as planned")
            memo.append(f"  2. Weekly monitoring continues")
            memo.append(f"  3. Decision expected by Week 8-10")
        
        memo.append("\n" + "="*80)
        memo.append("METHODOLOGY")
        memo.append("="*80)
        memo.append("\nBayesian sequential testing with automated stopping rules:")
        memo.append("  - Superiority: P(>10% improvement) > 90%")
        memo.append("  - Futility: No treatment shows >20% probability of helping")
        memo.append("  - Confidence intervals: 95% Bayesian credible intervals")
        
        memo.append("\n" + "="*80)
        memo.append("\nFor questions or detailed analysis, contact Data Science Team")
        memo.append("="*80)
        
        memo_text = "\n".join(memo)
        
        filename = get_report_path(f'decision_memo_week_{week_number}.txt')
        with open(filename, 'w') as f:
            f.write(memo_text)
        
        print(f"✓ Saved decision memo: {filename}")
        
        return memo_text
    
    def generate_all_reports(self, data, week_number, posteriors, decision, expected_roi=None):
        """
        Generate complete report package
        """
        print(f"\nGenerating reports for Week {week_number}...")
        print("="*60)
        
        # Weekly summary
        summary = self.generate_weekly_summary(data, week_number, posteriors, decision)
        
        # Executive dashboard
        self.generate_executive_dashboard(data, week_number, posteriors, decision)
        
        # Decision memo (if decision made)
        if decision['action'] != 'continue':
            memo = self.generate_decision_memo(decision, week_number, expected_roi)
        
        print("\n✅ All reports generated successfully")
        print(f"   Saved to: {reports_dir}")
        
        return {
            'summary': summary,
            'dashboard_saved': True,
            'memo_saved': decision['action'] != 'continue'
        }


# =============================================================================
# DEMO
# =============================================================================

def demo_automated_reporting():
    """
    Demonstrate automated reporting system
    """
    print("="*80)
    print("AUTOMATED REPORTING SYSTEM DEMONSTRATION")
    print("="*80)
    
    # Initialize reporter
    reporter = AutomatedReporter(
        experiment_name='Early Tenure Intervention'
    )
    
    # Simulate Week 6 data
    np.random.seed(42)
    true_rates = [0.609, 0.509, 0.459, 0.409]
    
    data = []
    for arm, rate in enumerate(true_rates):
        outcomes = np.random.binomial(1, rate, size=300)  # 6 weeks * 50/week
        for outcome in outcomes:
            data.append({'arm': arm, 'outcome': outcome})
    
    df = pd.DataFrame(data)
    
    # Calculate posteriors (simplified)
    posteriors = {}
    for arm in range(4):
        arm_data = df[df['arm'] == arm]
        n = len(arm_data)
        successes = arm_data['outcome'].sum()
        
        alpha = 2 + successes
        beta = 2 + (n - successes)
        samples = np.random.beta(alpha, beta, 10000)
        posteriors[arm] = samples
    
    # Determine decision
    control = posteriors[0]
    best_arm = 2  # T2 (15% reduction)
    treatment = posteriors[best_arm]
    prob_superior = (control - treatment > 0.10).mean()
    expected_effect = (control - treatment).mean()
    
    decision = {
        'action': 'superiority' if prob_superior > 0.90 else 'continue',
        'winner': best_arm if prob_superior > 0.90 else None,
        'probability': prob_superior,
        'effect': expected_effect,
        'reason': f'T{best_arm} shows {prob_superior:.0%} probability of >10% improvement'
    }
    
    # Expected ROI (example)
    expected_roi = {
        'annual_profit': 82000,
        'roi': 7.0,  # 700%
        'payback_months': 1.7
    }
    
    # Generate all reports
    reports = reporter.generate_all_reports(
        data=df,
        week_number=6,
        posteriors=posteriors,
        decision=decision,
        expected_roi=expected_roi if decision['action'] == 'superiority' else None
    )
    
    print("\n" + "="*80)
    print("✅ DEMONSTRATION COMPLETE")
    print("="*80)


# =============================================================================
# MAIN EXECUTION
# =============================================================================

if __name__ == '__main__':
    demo_automated_reporting()
    
    print("\n" + "="*80)
    print("Portfolio Value:")
    print("="*80)
    print("""
This automated reporting system demonstrates:

✓ Stakeholder communication
  - Executive summaries (non-technical)
  - Visual dashboards (quick understanding)
  - Decision memos (actionable recommendations)
  
✓ Production-ready automation
  - Can be scheduled (cron job)
  - Integrates with data pipeline
  - Consistent format week-over-week
  
✓ Multi-level reporting
  - Weekly summaries (team level)
  - Executive dashboards (leadership)
  - Decision memos (action-oriented)
  
✓ Clear recommendations
  - Not just "here's the data"
  - Explicit next steps
  - ROI quantified

    """)
