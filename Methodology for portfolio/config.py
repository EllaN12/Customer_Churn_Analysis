"""
Configuration File for Portfolio Project
Centralizes all directory paths and settings
"""

import os
from pathlib import Path

# =============================================================================
# DIRECTORY CONFIGURATION
# =============================================================================

# Use a stable project root, independent of the current working directory.
ROOT_DIR = Path(__file__).resolve().parents[1]

# Results directory (main output location)
results_dir = str(ROOT_DIR / 'venv' / 'Results')

# Create Results directory if it doesn't exist
os.makedirs(results_dir, exist_ok=True)

# Subdirectories
visualizations_dir = os.path.join(results_dir, 'visualizations')
reports_dir = os.path.join(results_dir, 'reports')
logs_dir = os.path.join(results_dir, 'logs')
monitoring_dir = os.path.join(results_dir, 'monitoring')

# Create all subdirectories
for subdir in [visualizations_dir, reports_dir, logs_dir, monitoring_dir]:
    os.makedirs(subdir, exist_ok=True)

# =============================================================================
# FILE PATHS
# =============================================================================

# Data (filename only; resolved through get_results_path)
DATA_FILE = 'churn_prediction.csv'

# Outputs
POWER_COMPARISON_FILE = os.path.join(visualizations_dir, 'power_comparison.png')
SAMPLE_SIZE_SENSITIVITY_FILE = os.path.join(visualizations_dir, 'sample_size_sensitivity.png')
CONVERGENCE_PLOT_FILE = os.path.join(monitoring_dir, 'convergence_plot.png')

# Visualizations
EARLY_TENURE_VIZ = os.path.join(visualizations_dir, '1_early_tenure_effect.png')
COLLIDER_BIAS_VIZ = os.path.join(visualizations_dir, '2_collider_bias_demonstration.png')
VALID_CONTROLS_VIZ = os.path.join(visualizations_dir, '3_valid_invalid_controls_diagram.png')

# Reports
WEEKLY_SUMMARY_TEMPLATE = os.path.join(reports_dir, 'weekly_summary_week_{}.txt')
EXECUTIVE_DASHBOARD_TEMPLATE = os.path.join(reports_dir, 'executive_dashboard_week_{}.png')
DECISION_MEMO_TEMPLATE = os.path.join(reports_dir, 'decision_memo_week_{}.txt')

# Logs
RANDOMIZATION_LOG_TEMPLATE = os.path.join(logs_dir, 'randomization_log_{}.csv')
ASSIGNMENTS_TEMPLATE = os.path.join(logs_dir, 'assignments_{}.csv')

# Monitoring
MONITORING_WEEK_TEMPLATE = os.path.join(monitoring_dir, 'monitoring_week_{}.png')

# =============================================================================
# EXPERIMENT SETTINGS
# =============================================================================

# Early Tenure Experiment
EARLY_TENURE_CONFIG = {
    'experiment_name': 'Early Tenure Intervention',
    'n_arms': 4,
    'baseline_rate': 0.747,  # Observed 0-6 month cohort churn rate
    'target_sample_size': 400,  # Total (100 per arm)
    'planned_weeks': 8,
    'min_weeks_before_stopping': 4
}

# Factorial Experiment
FACTORIAL_CONFIG = {
    'experiment_name': 'Contract + Payment + Add-ons',
    'n_cells': 8,
    'target_sample_size': 800,  # Total (100 per cell)
    'planned_weeks': 8
}

# =============================================================================
# STOPPING RULES
# =============================================================================

STOPPING_RULES = {
    'superiority': {
        'threshold': 0.08,  # 8pp minimum detectable effect
        'probability': 0.95,  # 95% posterior probability
        'min_effect_value': 50  # $50 per customer net EV
    },
    'futility': {
        'max_probability': 0.05,  # <5% chance any treatment helps
        'min_weeks': 6
    },
    'equivalence': {
        'threshold': 0.02,  # ROPE: within ±2pp
        'probability': 0.80,
        'min_weeks': 8
    }
}

# =============================================================================
# BAYESIAN SETTINGS
# =============================================================================

BAYESIAN_CONFIG = {
    'n_samples': 10000,  # Posterior samples for Monte Carlo
    'n_chains': 4,
    'n_tune': 1000,
    'n_draws': 2000,
    'target_accept': 0.95
}

# =============================================================================
# POWER ANALYSIS SETTINGS
# =============================================================================

POWER_ANALYSIS_CONFIG = {
    'n_simulations': 1000,  # Monte Carlo iterations
    'alpha': 0.05,
    'power_target': 0.90,
    'sample_sizes_to_test': [50, 75, 100, 125, 150, 200]
}

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_results_path(filename):
    """Get full path for a results file"""
    return os.path.join(results_dir, filename)

def get_visualization_path(filename):
    """Get full path for a visualization"""
    return os.path.join(visualizations_dir, filename)

def get_report_path(filename):
    """Get full path for a report"""
    return os.path.join(reports_dir, filename)

def get_log_path(filename):
    """Get full path for a log file"""
    return os.path.join(logs_dir, filename)

def get_monitoring_path(filename):
    """Get full path for a monitoring file"""
    return os.path.join(monitoring_dir, filename)

def print_directory_structure():
    """Print the current directory structure"""
    print("="*60)
    print("DIRECTORY STRUCTURE")
    print("="*60)
    print(f"\nProject Root: {ROOT_DIR}")
    print(f"\nResults Directory: {results_dir}")
    print(f"  ├── visualizations/")
    print(f"  ├── reports/")
    print(f"  ├── logs/")
    print(f"  └── monitoring/")
    print("\n✓ All directories created")
    print("="*60)

# =============================================================================
# INITIALIZATION
# =============================================================================

if __name__ == '__main__':
    print_directory_structure()
    
    print("\nConfiguration loaded:")
    print(f"  - Results directory: {results_dir}")
    print(f"  - Early tenure experiment: {EARLY_TENURE_CONFIG['experiment_name']}")
    print(f"  - Target sample size: {EARLY_TENURE_CONFIG['target_sample_size']}")
    print(f"  - Monte Carlo simulations: {POWER_ANALYSIS_CONFIG['n_simulations']}")
