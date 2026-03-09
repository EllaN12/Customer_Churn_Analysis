"""
Streamlit Experiment Monitoring Dashboard (UPDATED)
Portfolio Project: Interactive Real-Time Experiment Monitoring

UPDATED: Now uses config.py for directory management

Features:
- Live experiment status
- Posterior distributions
- Probability of superiority
- Decision recommendations
- What-if analysis

Run with: streamlit run streamlit_experiment_monitor.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# Import configuration
from config import results_dir, visualizations_dir, reports_dir

# Page configuration
st.set_page_config(
    page_title="Bayesian Experiment Monitor",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem 0;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .success-box {
        background-color: #d4edda;
        border-left: 4px solid #28a745;
        padding: 1rem;
        border-radius: 0.5rem;
    }
    .warning-box {
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
        padding: 1rem;
        border-radius: 0.5rem;
    }
    .danger-box {
        background-color: #f8d7da;
        border-left: 4px solid #dc3545;
        padding: 1rem;
        border-radius: 0.5rem;
    }
    .info-box {
        background-color: #d1ecf1;
        border-left: 4px solid #17a2b8;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-top: 1rem;
    }
</style>
""", unsafe_allow_html=True)


def generate_simulated_data(week, n_per_arm=50, true_rates=None):
    """Generate simulated experiment data"""
    if true_rates is None:
        true_rates = [0.609, 0.509, 0.459, 0.409]  # Early tenure experiment
    
    data = []
    for arm, rate in enumerate(true_rates):
        n_total = n_per_arm * week
        churned = np.random.binomial(1, rate, size=n_total)
        for outcome in churned:
            data.append({
                'arm': arm,
                'arm_name': 'Control' if arm == 0 else f'Treatment {arm}',
                'outcome': outcome
            })
    
    return pd.DataFrame(data)


def calculate_posteriors(data, n_samples=10000):
    """Calculate Bayesian posteriors for each arm"""
    posteriors = {}
    
    for arm in data['arm'].unique():
        arm_data = data[data['arm'] == arm]
        n = len(arm_data)
        successes = arm_data['outcome'].sum()
        
        # Beta posterior
        alpha = 2 + successes
        beta = 2 + (n - successes)
        
        # Sample from posterior
        samples = np.random.beta(alpha, beta, n_samples)
        posteriors[arm] = samples
    
    return posteriors


def calculate_probabilities(posteriors):
    """Calculate probability of superiority"""
    control = posteriors[0]
    
    probs = {}
    for arm in range(1, len(posteriors)):
        treatment = posteriors[arm]
        
        # P(reduction > 10%)
        diff = control - treatment
        prob_superior = (diff > 0.10).mean()
        
        probs[arm] = {
            'prob_superior_10': prob_superior,
            'expected_effect': diff.mean(),
            'ci_lower': np.percentile(diff, 2.5),
            'ci_upper': np.percentile(diff, 97.5)
        }
    
    return probs


def make_decision(probs, week, min_week=4):
    """Determine experiment decision"""
    if week < min_week:
        return {
            'action': 'continue',
            'reason': f'Too early (min {min_week} weeks)',
            'winner': None
        }
    
    # Check for superiority
    for arm, metrics in probs.items():
        if metrics['prob_superior_10'] > 0.90 and metrics['expected_effect'] > 0.10:
            return {
                'action': 'superiority',
                'reason': f'Treatment {arm} shows >90% probability of >10% improvement',
                'winner': arm,
                'probability': metrics['prob_superior_10'],
                'effect': metrics['expected_effect']
            }
    
    # Check for futility
    if week >= 6:
        max_prob = max([p['prob_superior_10'] for p in probs.values()])
        if max_prob < 0.20:
            return {
                'action': 'futility',
                'reason': 'No treatment shows >20% probability of helping',
                'winner': None
            }
    
    # Default: continue
    best_arm = max(probs.items(), key=lambda x: x[1]['prob_superior_10'])[0]
    return {
        'action': 'continue',
        'reason': f'Continue monitoring (best: T{best_arm})',
        'winner': None
    }


# ============================================================================
# SIDEBAR
# ============================================================================

st.sidebar.title("🔬 Experiment Controls")

# Experiment selection
experiment = st.sidebar.selectbox(
    "Select Experiment",
    ["Early Tenure Intervention", "Contract + Payment + Add-ons", "Fiber Quality"]
)

# Time controls
st.sidebar.subheader("⏰ Time Controls")
week = st.sidebar.slider("Current Week", 1, 12, 6)

# Sample size
st.sidebar.subheader("📊 Sample Size")
n_per_arm_per_week = st.sidebar.number_input(
    "Customers per arm per week",
    min_value=10,
    max_value=200,
    value=50,
    step=10
)

# True effect sizes (for simulation)
st.sidebar.subheader("🎯 True Effects (Simulation)")
st.sidebar.info("Adjust to see how the experiment would perform under different scenarios")

control_rate = st.sidebar.slider("Control churn rate", 0.0, 1.0, 0.609, 0.01)
t1_reduction = st.sidebar.slider("T1 reduction", 0.0, 0.30, 0.10, 0.01)
t2_reduction = st.sidebar.slider("T2 reduction", 0.0, 0.30, 0.15, 0.01)
t3_reduction = st.sidebar.slider("T3 reduction", 0.0, 0.30, 0.20, 0.01)

true_rates = [
    control_rate,
    control_rate - t1_reduction,
    control_rate - t2_reduction,
    control_rate - t3_reduction
]

# UPDATED: Show directory configuration
st.sidebar.markdown("---")
st.sidebar.subheader("📁 Configuration")
st.sidebar.markdown(f"""
<div class="info-box">
<b>Results Directory:</b><br>
{results_dir}<br><br>
<b>Subdirectories:</b><br>
• visualizations/<br>
• reports/<br>
• logs/<br>
• monitoring/
</div>
""", unsafe_allow_html=True)

# ============================================================================
# MAIN CONTENT
# ============================================================================

st.markdown('<div class="main-header">🔬 Bayesian Experiment Monitor</div>', unsafe_allow_html=True)
st.markdown(f"**Experiment:** {experiment} | **Week {week}** | **Status:** Active")

st.markdown("---")

# Generate data
np.random.seed(42 + week)  # Different seed each week
data = generate_simulated_data(week, n_per_arm_per_week, true_rates)

# Calculate posteriors
posteriors = calculate_posteriors(data)
probs = calculate_probabilities(posteriors)
decision = make_decision(probs, week)

# ============================================================================
# KEY METRICS ROW
# ============================================================================

st.subheader("📊 Key Metrics")

col1, col2, col3, col4 = st.columns(4)

with col1:
    total_enrolled = len(data)
    st.metric("Total Enrolled", f"{total_enrolled:,}")
    st.caption(f"{total_enrolled // 4} per arm")

with col2:
    overall_churn = data['outcome'].mean()
    st.metric("Overall Churn", f"{overall_churn:.1%}")

with col3:
    best_arm = max(probs.items(), key=lambda x: x[1]['prob_superior_10'])[0]
    best_prob = probs[best_arm]['prob_superior_10']
    st.metric("Best Treatment", f"T{best_arm}", f"{best_prob:.0%} confidence")

with col4:
    weeks_remaining = max(0, 8 - week)
    st.metric("Weeks Remaining", f"{weeks_remaining}")
    if decision['action'] != 'continue':
        st.caption("⚠️ Stop criteria met!")

st.markdown("---")

# ============================================================================
# DECISION BOX
# ============================================================================

st.subheader("🎯 Decision Status")

if decision['action'] == 'superiority':
    st.markdown(f"""
    <div class="success-box">
        <h3>✅ SUPERIORITY DETECTED</h3>
        <p><strong>Winner:</strong> Treatment {decision['winner']}</p>
        <p><strong>Probability:</strong> {decision['probability']:.1%}</p>
        <p><strong>Expected Effect:</strong> {decision['effect']*100:+.1f} percentage points</p>
        <p><strong>Recommendation:</strong> STOP EXPERIMENT & IMPLEMENT T{decision['winner']}</p>
    </div>
    """, unsafe_allow_html=True)
elif decision['action'] == 'futility':
    st.markdown(f"""
    <div class="danger-box">
        <h3>⚠️ FUTILITY DETECTED</h3>
        <p><strong>Reason:</strong> {decision['reason']}</p>
        <p><strong>Recommendation:</strong> STOP EXPERIMENT (No effective treatment)</p>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown(f"""
    <div class="warning-box">
        <h3>→ CONTINUE MONITORING</h3>
        <p><strong>Status:</strong> {decision['reason']}</p>
        <p><strong>Next Action:</strong> Review again next week</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ============================================================================
# VISUALIZATIONS
# ============================================================================

# Row 1: Posterior Distributions + Probability Bars
col1, col2 = st.columns(2)

with col1:
    st.subheader("📈 Posterior Distributions")
    
    fig = go.Figure()
    
    colors = ['#ff7f0e', '#2ca02c', '#1f77b4', '#d62728']
    
    for arm, samples in posteriors.items():
        name = 'Control' if arm == 0 else f'Treatment {arm}'
        fig.add_trace(go.Histogram(
            x=samples,
            name=name,
            opacity=0.7,
            nbinsx=50,
            marker_color=colors[arm]
        ))
    
    fig.update_layout(
        barmode='overlay',
        xaxis_title='Churn Rate',
        yaxis_title='Density',
        height=400,
        showlegend=True,
        hovermode='x unified'
    )
    
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("🎯 Probability of Superiority")
    
    arms = [f'T{i}' for i in range(1, 4)]
    probabilities = [probs[i]['prob_superior_10'] for i in range(1, 4)]
    
    colors_bars = ['green' if p > 0.90 else 'orange' if p > 0.70 else 'red' for p in probabilities]
    
    fig = go.Figure(go.Bar(
        x=probabilities,
        y=arms,
        orientation='h',
        marker_color=colors_bars,
        text=[f'{p:.1%}' for p in probabilities],
        textposition='outside'
    ))
    
    fig.add_vline(x=0.90, line_dash="dash", line_color="green", 
                  annotation_text="90% threshold")
    
    fig.update_layout(
        xaxis_title='P(Reduction > 10%)',
        yaxis_title='Treatment',
        height=400,
        xaxis_range=[0, 1]
    )
    
    st.plotly_chart(fig, use_container_width=True)

# Row 2: Effect Sizes + Data Table
col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 Expected Effect Sizes")
    
    arms = [f'T{i}' for i in range(1, 4)]
    effects = [probs[i]['expected_effect'] * 100 for i in range(1, 4)]
    ci_lower = [probs[i]['ci_lower'] * 100 for i in range(1, 4)]
    ci_upper = [probs[i]['ci_upper'] * 100 for i in range(1, 4)]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=effects,
        y=arms,
        orientation='h',
        marker_color=['green' if e > 10 else 'orange' if e > 5 else 'red' for e in effects],
        error_x=dict(
            type='data',
            symmetric=False,
            array=[u - e for e, u in zip(effects, ci_upper)],
            arrayminus=[e - l for e, l in zip(effects, ci_lower)]
        ),
        text=[f'{e:+.1f}%' for e in effects],
        textposition='outside'
    ))
    
    fig.add_vline(x=10, line_dash="dash", line_color="green",
                  annotation_text="10% target")
    
    fig.update_layout(
        xaxis_title='Effect Size (percentage points)',
        yaxis_title='Treatment',
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("📋 Current Data Summary")
    
    summary = data.groupby('arm_name').agg({
        'outcome': ['count', 'sum', 'mean']
    }).round(3)
    summary.columns = ['N', 'Churned', 'Churn Rate']
    summary['Churn Rate'] = summary['Churn Rate'].apply(lambda x: f'{x:.1%}')
    
    st.dataframe(summary, use_container_width=True)
    
    st.caption("📊 Detailed Treatment Probabilities")
    
    detail_data = []
    for arm in range(1, 4):
        detail_data.append({
            'Treatment': f'T{arm}',
            'P(>10% reduction)': f"{probs[arm]['prob_superior_10']:.1%}",
            'Expected Effect': f"{probs[arm]['expected_effect']*100:+.1f}%",
            '95% CI': f"[{probs[arm]['ci_lower']*100:.1f}%, {probs[arm]['ci_upper']*100:.1f}%]"
        })
    
    st.dataframe(pd.DataFrame(detail_data), use_container_width=True, hide_index=True)

# ============================================================================
# WHAT-IF ANALYSIS
# ============================================================================

st.markdown("---")
st.subheader("🔮 What-If Analysis")

st.info("**Question:** What if we had different sample sizes or effect sizes?")

col1, col2 = st.columns(2)

with col1:
    st.markdown("##### Sample Size Impact")
    
    sample_sizes = np.array([25, 50, 75, 100, 150, 200])
    
    # Calculate power for each sample size (simplified)
    powers_t2 = []
    for n in sample_sizes:
        # Approximate power using normal approximation
        p1 = control_rate
        p2 = control_rate - t2_reduction
        pooled = (p1 + p2) / 2
        effect = abs(p1 - p2)
        
        z = (effect - 0.10) / np.sqrt(2 * pooled * (1 - pooled) / n)
        power = 1 - stats.norm.cdf(1.96 - z)
        powers_t2.append(power)
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=sample_sizes,
        y=powers_t2,
        mode='lines+markers',
        marker=dict(size=10, color='steelblue'),
        line=dict(width=3)
    ))
    
    fig.add_hline(y=0.80, line_dash="dash", line_color="green",
                  annotation_text="80% power")
    fig.add_hline(y=0.90, line_dash="dash", line_color="blue",
                  annotation_text="90% power")
    
    # Mark current sample size
    current_n = n_per_arm_per_week * week
    fig.add_vline(x=current_n, line_dash="dot", line_color="red",
                  annotation_text=f"Current (n={current_n})")
    
    fig.update_layout(
        xaxis_title='Sample Size per Arm',
        yaxis_title='Power (T2: 15% reduction)',
        height=350,
        yaxis_range=[0, 1]
    )
    
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown("##### Effect Size Impact")
    
    effect_sizes = np.arange(0.05, 0.31, 0.05)
    
    # Calculate power for each effect size
    powers_by_effect = []
    for delta in effect_sizes:
        p1 = control_rate
        p2 = control_rate - delta
        pooled = (p1 + p2) / 2
        n = current_n
        
        z = (delta - 0.10) / np.sqrt(2 * pooled * (1 - pooled) / n)
        power = 1 - stats.norm.cdf(1.96 - z)
        powers_by_effect.append(power)
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=effect_sizes * 100,
        y=powers_by_effect,
        mode='lines+markers',
        marker=dict(size=10, color='coral'),
        line=dict(width=3)
    ))
    
    fig.add_hline(y=0.80, line_dash="dash", line_color="green")
    fig.add_hline(y=0.90, line_dash="dash", line_color="blue")
    
    # Mark current effect
    fig.add_vline(x=t2_reduction * 100, line_dash="dot", line_color="red",
                  annotation_text=f"T2 effect ({t2_reduction*100:.0f}%)")
    
    fig.update_layout(
        xaxis_title='True Effect Size (%)',
        yaxis_title='Power',
        height=350,
        yaxis_range=[0, 1]
    )
    
    st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
st.caption("🔬 Bayesian Experiment Monitor | Portfolio Project | Real-time Sequential Testing")

# Download data button
csv = data.to_csv(index=False)
st.download_button(
    label="📥 Download Current Data",
    data=csv,
    file_name=f'experiment_week_{week}.csv',
    mime='text/csv'
)

# Show configuration info
with st.expander("ℹ️ Configuration Details"):
    st.markdown(f"""
    **Directory Structure:**
    - Results: `{results_dir}`
    - Visualizations: `{visualizations_dir}`
    - Reports: `{reports_dir}`
    
    **Experiment Parameters:**
    - Arms: 4 (1 control + 3 treatments)
    - Current week: {week}
    - Customers per arm: {n_per_arm_per_week * week}
    - Total enrolled: {total_enrolled}
    
    **Decision Criteria:**
    - Superiority: P(reduction > 10%) > 90%
    - Futility: Max P(helps) < 20% after week 6
    - Minimum weeks before stopping: 4
    """)
