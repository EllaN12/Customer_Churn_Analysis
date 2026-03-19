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

# Import configuration
from config import (
    results_dir, logs_dir,
    get_log_path
)


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
        self.log_file = get_log_path(f'randomization_log_{experiment_name}.csv')
        
        print(f"✓ Initialized randomizer for '{experiment_name}'")
        print(f"  Arms: {n_arms}")
        print(f"  Block size: {self.block_size}")
        print(f"  Strata: {strata_vars if strata_vars else 'None'}")
        print(f"  Log file: {self.log_file}")
    
    def assign_customer(self, customer_id, strata_values=None):
        """
        Assign a customer to treatment arm
        
        Parameters:
        -----------
        customer_id : str
            Unique customer identifier
        strata_values : dict
            Values for stratification variables
            e.g., {'internet_service': 'Fiber', 'contract_type': 'MTM'}
        
        Returns:
        --------
        int : Treatment arm assignment (0 = control, 1+ = treatments)
        """
        # Determine stratum
        if strata_values and self.strata_vars:
            stratum = tuple(strata_values.get(var, 'Unknown') for var in self.strata_vars)
        else:
            stratum = ('default',)
        
        # Get or create block for this stratum
        if stratum not in self.current_blocks:
            self.current_blocks[stratum] = self._create_new_block()
        
        # Get next assignment from block
        if len(self.current_blocks[stratum]) == 0:
            self.current_blocks[stratum] = self._create_new_block()
        
        assignment = self.current_blocks[stratum].pop(0)
        
        # Log assignment
        self._log_assignment(customer_id, assignment, stratum, strata_values)
        
        return assignment
    
    def _create_new_block(self):
        """Create a new randomized block"""
        # Equal allocation across arms
        assignments_per_arm = self.block_size // self.n_arms
        block = []
        
        for arm in range(self.n_arms):
            block.extend([arm] * assignments_per_arm)
        
        # Randomly permute
        np.random.shuffle(block)
        
        return block
    
    def _log_assignment(self, customer_id, assignment, stratum, strata_values):
        """Log assignment to file"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'customer_id': customer_id,
            'assignment': assignment,
            'stratum': str(stratum),
        }
        
        # Add strata values
        if strata_values:
            log_entry.update(strata_values)
        
        self.assignments.append(log_entry)
        
        # Append to CSV
        df_log = pd.DataFrame([log_entry])
        
        # Write header if file doesn't exist
        write_header = not Path(self.log_file).exists()
        
        df_log.to_csv(self.log_file, mode='a', header=write_header, index=False)
    
    def check_balance(self):
        """
        Check balance of assignments
        
        Returns:
        --------
        dict : Balance statistics
        """
        if len(self.assignments) == 0:
            print("⚠️ No assignments yet")
            return None
        
        df = pd.DataFrame(self.assignments)
        
        print("\n" + "="*80)
        print("BALANCE CHECK")
        print("="*80)
        
        # Overall balance
        print("\nOverall assignment counts:")
        counts = df['assignment'].value_counts().sort_index()
        
        for arm, count in counts.items():
            arm_name = 'Control' if arm == 0 else f'Treatment {arm}'
            pct = count / len(df) * 100
            print(f"  {arm_name}: {count} ({pct:.1f}%)")
        
        # Chi-square test for balance
        expected = len(df) / self.n_arms
        chi_square = sum((counts - expected)**2 / expected)
        p_value = 1 - pd.Series(chi_square).apply(
            lambda x: pd.Series([x]).apply(lambda y: 0.05 if y > 5.99 else 0.95).iloc[0]
        ).iloc[0]
        
        print(f"\nChi-square test: χ² = {chi_square:.2f}")
        
        if chi_square < 5.99:  # Critical value for 3 df at α=0.05
            print("✓ Good balance (χ² < 5.99)")
        else:
            print("⚠️ Possible imbalance (χ² > 5.99)")
        
        # Stratified balance
        if self.strata_vars and len(self.strata_vars) > 0:
            print("\n" + "="*60)
            print("BALANCE WITHIN STRATA")
            print("="*60)
            
            for var in self.strata_vars:
                if var in df.columns:
                    print(f"\nBy {var}:")
                    
                    for value in df[var].unique():
                        subset = df[df[var] == value]
                        counts_strata = subset['assignment'].value_counts().sort_index()
                        
                        print(f"  {value}:")
                        for arm, count in counts_strata.items():
                            arm_name = 'Control' if arm == 0 else f'T{arm}'
                            print(f"    {arm_name}: {count}")
        
        return {
            'total_assignments': len(df),
            'counts_by_arm': counts.to_dict(),
            'chi_square': chi_square,
            'balanced': chi_square < 5.99
        }
    
    def export_assignments(self, filename=None):
        """
        Export all assignments to CSV
        
        Parameters:
        -----------
        filename : str
            Output filename (default: assignments_{experiment_name}.csv)
        
        Returns:
        --------
        pd.DataFrame : Assignment data
        """
        if filename is None:
            filename = get_log_path(f'assignments_{self.experiment_name}.csv')
        
        df = pd.DataFrame(self.assignments)
        df.to_csv(filename, index=False)
        
        print(f"\n✓ Exported {len(df)} assignments to: {filename}")
        
        return df


class EarlyTenureRandomizer(ExperimentRandomizer):
    """
    Specialized randomizer for early tenure intervention experiment
    """
    
    def __init__(self):
        super().__init__(
            experiment_name='early_tenure_v1',
            n_arms=4,  # Control + 3 treatments
            strata_vars=['internet_service', 'contract_type']
        )
    
    def assign_new_customer(self, customer_id, internet_service, contract_type):
        """
        Assign new customer in early tenure experiment
        
        Parameters:
        -----------
        customer_id : str
            Customer ID
        internet_service : str
            'Fiber' or 'DSL'
        contract_type : str
            'MTM' (month-to-month) or 'Long-term'
        
        Returns:
        --------
        dict : Assignment details
        """
        strata_values = {
            'internet_service': internet_service,
            'contract_type': contract_type
        }
        
        assignment = self.assign_customer(customer_id, strata_values)
        
        # Map to treatment names
        treatment_names = {
            0: 'Control (Standard onboarding)',
            1: 'Treatment 1 (Welcome call)',
            2: 'Treatment 2 (Smart Start package)',
            3: 'Treatment 3 (Concierge support)'
        }
        
        return {
            'customer_id': customer_id,
            'assignment_code': assignment,
            'treatment': treatment_names[assignment],
            'internet_service': internet_service,
            'contract_type': contract_type
        }


# =============================================================================
# DEMONSTRATION
# =============================================================================

def demo_randomization():
    """
    Demonstrate randomization system
    """
    print("="*80)
    print("RANDOMIZATION SYSTEM DEMONSTRATION")
    print("="*80)
    
    # Initialize randomizer
    randomizer = EarlyTenureRandomizer()
    
    # Simulate 100 customer assignments
    print("\n" + "="*80)
    print("ASSIGNING 100 CUSTOMERS")
    print("="*80)
    
    # Customer characteristics
    internet_types = ['Fiber', 'DSL']
    contract_types = ['MTM', 'Long-term']
    
    np.random.seed(42)
    
    for i in range(100):
        customer_id = f'CUST_{i+1:04d}'
        internet = np.random.choice(internet_types)
        contract = np.random.choice(contract_types)
        
        assignment = randomizer.assign_new_customer(customer_id, internet, contract)
        
        if i < 5:  # Show first 5
            print(f"  {assignment['customer_id']}: {assignment['treatment']}")
    
    print(f"  ...")
    print(f"  (Assigned {i+1} customers)")
    
    # Check balance
    balance = randomizer.check_balance()
    
    # Export assignments
    df_assignments = randomizer.export_assignments()
    
    print("\n" + "="*80)
    print("✅ DEMONSTRATION COMPLETE")
    print("="*80)
    
    print("\nGenerated files:")
    print(f"  ✓ {randomizer.log_file}")
    print(f"  ✓ {logs_dir}/assignments_early_tenure_v1.csv")
    
    return randomizer


# =============================================================================
# MAIN EXECUTION
# =============================================================================

if __name__ == '__main__':
    demo_randomization()
    
    print("\n" + "="*80)
    print("Portfolio Value:")
    print("="*80)
    print("""
This randomization system demonstrates:

✓ Stratified block randomization
  - Ensures balance within subgroups
  - Prevents selection bias
  
✓ Concealment
  - Unpredictable assignments
  - No one can guess next assignment
  
✓ Auditability
  - Complete assignment log
  - Timestamp every assignment
  
✓ Balance verification
  - Chi-square tests
  - Stratified balance checks
  
✓ Production-ready
  - Can integrate with signup system
  - Automated logging
  - Export capabilities
    """)
