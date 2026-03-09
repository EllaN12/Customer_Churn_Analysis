"""
Randomization System for Churn Experiments
Portfolio Project: Stratified Block Randomization with Balance Checks

Implements:
- Stratified random assignment
- Block randomization for balance
- Concealment (unpredictable assignments)
- Logging and auditability
- Balance verification
"""

import pandas as pd
import numpy as np
from datetime import datetime
import json
from pathlib import Path


class ExperimentRandomizer:
    """
    Stratified block randomization system for churn experiments
    """
    
    def __init__(self, experiment_name, n_arms, block_size=None, strata_vars=None):
        """
        Parameters:
        -----------
        experiment_name : str
            Name of experiment (e.g., 'early_tenure_v1')
        n_arms : int
            Number of treatment arms (including control)
        block_size : int
            Block size for permuted block randomization (default: n_arms * 2)
        strata_vars : list
            Variables to stratify on (e.g., ['internet_service', 'contract_type'])
        """
        self.experiment_name = experiment_name
        self.n_arms = n_arms
        self.block_size = block_size or (n_arms * 2)
        self.strata_vars = strata_vars or []
        
        # Storage
        self.assignments = []
        self.current_blocks = {}  # One per stratum
        
        # Logging
        self.log_file = Path(f'/mnt/user-data/outputs/randomization_log_{experiment_name}.csv')
        
        print(f"✓ Initialized randomizer for '{experiment_name}'")
        print(f"  - Arms: {n_arms}")
        print(f"  - Block size: {self.block_size}")
        print(f"  - Strata: {strata_vars or 'None (simple randomization)'}")
    
    def get_stratum_key(self, customer_data):
        """
        Create stratum identifier from customer characteristics
        """
        if not self.strata_vars:
            return 'all'
        
        stratum_values = [str(customer_data.get(var, 'unknown')) for var in self.strata_vars]
        return '_'.join(stratum_values)
    
    def create_new_block(self):
        """
        Create a randomized block of assignments
        Ensures perfect balance within each block
        """
        # Create block with equal representation
        assignments_in_block = []
        for arm in range(self.n_arms):
            assignments_in_block.extend([arm] * (self.block_size // self.n_arms))
        
        # Randomize order
        np.random.shuffle(assignments_in_block)
        
        return assignments_in_block
    
    def assign_customer(self, customer_id, customer_data):
        """
        Assign customer to treatment arm using stratified block randomization
        
        Parameters:
        -----------
        customer_id : str
            Unique customer identifier
        customer_data : dict
            Customer characteristics for stratification
            Example: {'internet_service': 'Fiber', 'contract': 'MTM'}
        
        Returns:
        --------
        int : Assigned treatment arm (0 = control, 1+ = treatments)
        """
        # Get stratum
        stratum = self.get_stratum_key(customer_data)
        
        # Initialize block for this stratum if needed
        if stratum not in self.current_blocks:
            self.current_blocks[stratum] = self.create_new_block()
        
        # Get next assignment from current block
        if len(self.current_blocks[stratum]) == 0:
            # Block exhausted, create new one
            self.current_blocks[stratum] = self.create_new_block()
        
        assignment = self.current_blocks[stratum].pop(0)
        
        # Log assignment
        self._log_assignment(customer_id, assignment, stratum, customer_data)
        
        return assignment
    
    def _log_assignment(self, customer_id, assignment, stratum, customer_data):
        """
        Log assignment for auditability and balance checking
        """
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'customer_id': customer_id,
            'assignment': assignment,
            'stratum': stratum,
            **customer_data
        }
        
        self.assignments.append(log_entry)
        
        # Append to log file
        df_log = pd.DataFrame([log_entry])
        if self.log_file.exists():
            df_log.to_csv(self.log_file, mode='a', header=False, index=False)
        else:
            df_log.to_csv(self.log_file, mode='w', header=True, index=False)
    
    def check_balance(self, verbose=True):
        """
        Check balance across treatment arms
        Returns imbalance statistics
        """
        if len(self.assignments) == 0:
            print("No assignments yet")
            return None
        
        df = pd.DataFrame(self.assignments)
        
        if verbose:
            print("\n" + "="*60)
            print("BALANCE CHECK")
            print("="*60)
        
        # Overall balance
        print("\nOverall assignment distribution:")
        arm_counts = df['assignment'].value_counts().sort_index()
        print(arm_counts)
        
        # Chi-square test for balance
        expected = len(df) / self.n_arms
        chi2_stat = ((arm_counts - expected)**2 / expected).sum()
        p_value = 1 - stats.chi2.cdf(chi2_stat, df=self.n_arms - 1)
        
        print(f"\nChi-square test for overall balance:")
        print(f"  χ² = {chi2_stat:.3f}, p = {p_value:.4f}")
        
        if p_value < 0.05:
            print("  ⚠️ WARNING: Significant imbalance detected!")
        else:
            print("  ✓ Good balance across arms")
        
        # Balance within strata
        if self.strata_vars:
            print("\nBalance within strata:")
            for stratum in df['stratum'].unique():
                stratum_df = df[df['stratum'] == stratum]
                stratum_counts = stratum_df['assignment'].value_counts().sort_index()
                print(f"\n  Stratum '{stratum}':")
                print(f"  {stratum_counts.to_dict()}")
        
        # Check covariate balance
        print("\nCovariate balance across arms:")
        for var in df.columns:
            if var not in ['timestamp', 'customer_id', 'assignment', 'stratum']:
                try:
                    # For categorical
                    if df[var].dtype == 'object':
                        crosstab = pd.crosstab(df['assignment'], df[var], normalize='index')
                        print(f"\n  {var}:")
                        print(crosstab.to_string())
                except:
                    pass
        
        return {
            'n_assigned': len(df),
            'arm_counts': arm_counts.to_dict(),
            'chi2_stat': chi2_stat,
            'p_value': p_value,
            'balanced': p_value >= 0.05
        }
    
    def export_assignment_list(self, filepath=None):
        """
        Export current assignments to CSV
        """
        filepath = filepath or f'/mnt/user-data/outputs/assignments_{self.experiment_name}.csv'
        
        df = pd.DataFrame(self.assignments)
        df.to_csv(filepath, index=False)
        
        print(f"\n✓ Exported {len(df)} assignments to {filepath}")
        
        return df


# =============================================================================
# EXPERIMENT-SPECIFIC RANDOMIZERS
# =============================================================================

class EarlyTenureRandomizer(ExperimentRandomizer):
    """
    Randomizer for Experiment 1: Early Tenure Intervention
    
    4 arms:
    0 = Control
    1 = Welcome Call
    2 = Smart Start (contract + add-on)
    3 = Concierge (multi-touchpoint)
    
    Stratified by: Internet service (Fiber/DSL), Contract type (MTM/Contract)
    """
    
    def __init__(self):
        super().__init__(
            experiment_name='early_tenure_v1',
            n_arms=4,
            block_size=8,
            strata_vars=['internet_service', 'contract_type']
        )
    
    def assign_new_customer(self, customer_id, internet_service, contract_type):
        """
        Convenience method for early tenure assignment
        """
        customer_data = {
            'internet_service': internet_service,
            'contract_type': contract_type
        }
        
        assignment = self.assign_customer(customer_id, customer_data)
        
        # Map to intervention name
        intervention_names = {
            0: 'Control (Standard onboarding)',
            1: 'T1: Welcome Call (Day 7)',
            2: 'T2: Smart Start (Day 14 contract offer)',
            3: 'T3: Concierge (Days 7, 14, 30 touchpoints)'
        }
        
        print(f"Customer {customer_id} assigned to: {intervention_names[assignment]}")
        
        return assignment


class FactorialRandomizer(ExperimentRandomizer):
    """
    Randomizer for Experiment 2: 2×2×2 Factorial Design
    
    8 combinations:
    Assignment codes combine three factors:
    - Contract: 0=MTM, 1=1-year
    - Payment: 0=Current, 1=Autopay
    - Add-ons: 0=No offer, 1=Bundle offer
    """
    
    def __init__(self):
        super().__init__(
            experiment_name='factorial_v1',
            n_arms=8,
            block_size=16,
            strata_vars=['tenure_group', 'revenue_tier']
        )
    
    def assign_mtm_customer(self, customer_id, tenure_months, monthly_charges):
        """
        Assign month-to-month customer to factorial condition
        """
        # Derive strata
        tenure_group = 'early' if tenure_months <= 6 else 'established'
        revenue_tier = 'low' if monthly_charges < 60 else 'high'
        
        customer_data = {
            'tenure_group': tenure_group,
            'revenue_tier': revenue_tier,
            'tenure_months': tenure_months,
            'monthly_charges': monthly_charges
        }
        
        assignment = self.assign_customer(customer_id, customer_data)
        
        # Decode assignment to treatment components
        contract = (assignment >> 2) & 1  # Bit 2
        payment = (assignment >> 1) & 1   # Bit 1
        addon = assignment & 1            # Bit 0
        
        intervention_desc = []
        intervention_desc.append('1-year contract' if contract else 'Month-to-month')
        intervention_desc.append('Autopay incentive' if payment else 'Current payment')
        intervention_desc.append('Add-on bundle' if addon else 'No add-on offer')
        
        print(f"Customer {customer_id} assigned to: {' + '.join(intervention_desc)}")
        
        return {
            'assignment_code': assignment,
            'contract_offer': contract,
            'payment_switch': payment,
            'addon_offer': addon
        }


# =============================================================================
# SIMULATION DEMO
# =============================================================================

def demo_randomization():
    """
    Demonstrate randomization system with simulated customers
    """
    print("="*80)
    print("RANDOMIZATION SYSTEM DEMONSTRATION")
    print("="*80)
    
    # Experiment 1: Early Tenure
    print("\n" + "="*60)
    print("EXPERIMENT 1: EARLY TENURE INTERVENTION")
    print("="*60)
    
    randomizer_1 = EarlyTenureRandomizer()
    
    # Simulate 100 new customers
    np.random.seed(42)
    for i in range(100):
        customer_id = f"CUST_{i+1:04d}"
        internet = np.random.choice(['Fiber', 'DSL'])
        contract = np.random.choice(['MTM', 'Contract'])
        
        assignment = randomizer_1.assign_new_customer(customer_id, internet, contract)
    
    # Check balance
    balance_1 = randomizer_1.check_balance()
    
    # Export
    df_1 = randomizer_1.export_assignment_list()
    
    # Experiment 2: Factorial
    print("\n" + "="*60)
    print("EXPERIMENT 2: FACTORIAL DESIGN")
    print("="*60)
    
    randomizer_2 = FactorialRandomizer()
    
    # Simulate 200 MTM customers
    for i in range(200):
        customer_id = f"MTM_{i+1:04d}"
        tenure = np.random.randint(3, 25)
        charges = np.random.uniform(40, 100)
        
        assignment = randomizer_2.assign_mtm_customer(customer_id, tenure, charges)
    
    # Check balance
    balance_2 = randomizer_2.check_balance()
    
    # Export
    df_2 = randomizer_2.export_assignment_list()
    
    print("\n" + "="*60)
    print("✅ DEMONSTRATION COMPLETE")
    print("="*60)
    print("\nGenerated files:")
    print(f"  - {randomizer_1.log_file}")
    print(f"  - {randomizer_2.log_file}")
    print("\nKey Features Demonstrated:")
    print("  ✓ Stratified randomization (balance within strata)")
    print("  ✓ Block randomization (perfect balance within blocks)")
    print("  ✓ Automated balance checking")
    print("  ✓ Full logging and auditability")
    print("  ✓ Experiment-specific implementations")


# =============================================================================
# PRODUCTION USAGE EXAMPLE
# =============================================================================

def production_example():
    """
    How this would be used in production
    """
    print("\n" + "="*80)
    print("PRODUCTION USAGE EXAMPLE")
    print("="*80)
    
    print("""
# In production system:

# Initialize randomizer (once per experiment)
randomizer = EarlyTenureRandomizer()

# When new customer signs up:
def onboard_new_customer(customer_id, customer_data):
    # Assign to treatment
    assignment = randomizer.assign_new_customer(
        customer_id=customer_id,
        internet_service=customer_data['internet_service'],
        contract_type=customer_data['contract_type']
    )
    
    # Deliver intervention based on assignment
    if assignment == 0:
        send_standard_welcome_email(customer_id)
    elif assignment == 1:
        schedule_welcome_call(customer_id, day=7)
    elif assignment == 2:
        send_smart_start_offer(customer_id, day=14)
    elif assignment == 3:
        assign_concierge_manager(customer_id)
    
    # Log for analysis
    log_experiment_enrollment(customer_id, assignment)

# Daily balance check:
def daily_monitoring():
    balance = randomizer.check_balance(verbose=True)
    
    if not balance['balanced']:
        send_alert_to_analysts("Randomization imbalance detected!")
    
    if balance['n_assigned'] >= 400:
        trigger_interim_analysis()
    """)


# =============================================================================
# MAIN EXECUTION
# =============================================================================

if __name__ == '__main__':
    from scipy import stats  # Import here for demo
    
    # Run demonstration
    demo_randomization()
    
    # Show production example
    production_example()
    
    print("\n" + "="*80)
    print("Portfolio Value:")
    print("="*80)
    print("""
This randomization system demonstrates:

✓ Understanding of experimental design principles
  - Stratification to reduce variance
  - Block randomization for balance
  - Concealment to prevent selection bias

✓ Practical implementation skills
  - Production-ready code
  - Logging and auditability
  - Automated balance checks

✓ Statistical rigor
  - Proper randomization procedures
  - Balance verification (chi-square tests)
  - Experiment-specific customization

In interviews, you can show:
1. The code (clean, documented)
2. Simulated balance checks (proving it works)
3. Production integration example
4. Understanding of WHY each feature matters
    """)
