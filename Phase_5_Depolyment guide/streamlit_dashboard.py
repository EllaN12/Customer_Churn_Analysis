"""
Interactive Bayesian A/B Test Dashboard
Portfolio Project - Streamlit App

Run with: streamlit run streamlit_dashboard.py

This creates an interactive tool that demonstrates:
1. Bayesian experimental design
2. Real-time power calculations
3. Decision support system
4. ROI analysis under uncertainty
"""
#%%
import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# Page config
st.set_page_config(
    page_title="Bayesian A/B Test Designer",
    page_icon="📊",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 5px solid #1f77b4;
    }
    .success {
        color: #28a745;
        font-weight: bold;
    }
    .warning {
        color: #ffc107;
        font-weight: bold;
    }
    .danger {
        color: #dc3545;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)


# =============================================================================
# Helper Functions
# =============================================================================

def compute_beta_posterior(prior_alpha, prior_beta, successes, failures):
    """Compute Beta posterior parameters"""
    post_alpha = prior_alpha + successes
    post_beta = prior_beta + failures
    return post_alpha, post_beta


def sample_beta_posterior(alpha, beta, n_samples=10000):
    """Sample from Beta posterior"""
    return np.random.beta(alpha, beta, n_samples)


def compute_probability_superior(control_samples, treatment_samples, min_effect=0.08):
    """Compute P(treatment better than control + min_effect)"""
    diff = control_samples - treatment_samples
    return (diff > min_effect).mean()


def calculate_expected_value(churn_reduction_samples, monthly_revenue, avg_months, cost):
    """Calculate expected value per customer"""
    revenue_saved = churn_reduction_samples * avg_months * monthly_revenue
    net_value = revenue_saved - cost
    return net_value


def calculate_sample_size(effect_size, alpha=0.05, power=0.8, baseline=0.715):
    """
    Approximate sample size calculation for proportion test
    Using normal approximation
    """
    z_alpha = stats.norm.ppf(1 - alpha/2)
    z_beta = stats.norm.ppf(power)
    
    p1 = baseline
    p2 = baseline + effect_size
    p_avg = (p1 + p2) / 2
    
    n = ((z_alpha + z_beta)**2 * 2 * p_avg * (1 - p_avg)) / (effect_size**2)
    
    return int(np.ceil(n))


# =============================================================================
# Main App
# =============================================================================

def main():
    
    # Header
    st.markdown('<p class="main-header">🧪 Bayesian A/B Test Designer</p>', unsafe_allow_html=True)
    st.markdown("### Interactive Decision Support Tool for Churn Reduction Experiments")
    st.markdown("---")
    
    # Sidebar - Experiment Configuration
    st.sidebar.header("⚙️ Experiment Configuration")
    
    st.sidebar.subheader("Business Context")
    baseline_churn = st.sidebar.slider(
        "Baseline Churn Rate (%)",
        min_value=50,
        max_value=90,
        value=26.5,
        step=1,
        help="Current churn rate for high-risk customers"
    ) / 100
    
    monthly_revenue = st.sidebar.number_input(
        "Average Monthly Revenue ($)",
        min_value=10.0,
        max_value=200.0,
        value=78.76,
        step=1.0,
        help="Average monthly charges per customer"
    )
    
    avg_retention_months = st.sidebar.number_input(
        "Expected Retention Extension (months)",
        min_value=3,
        max_value=24,
        value=11,
        step=1,
        help="How many additional months a retained customer stays"
    )
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("Test Design")
    
    n_arms = st.sidebar.selectbox(
        "Number of Treatment Arms",
        options=[2, 3, 4],
        index=2,
        help="Including control"
    )
    
    sample_size_per_arm = st.sidebar.slider(
        "Sample Size per Arm",
        min_value=50,
        max_value=500,
        value=200,
        step=25,
        help="Number of customers in each treatment group"
    )
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("Treatment Effects")
    st.sidebar.markdown("*Expected churn reduction (absolute %)*")
    
    treatment_effects = [0]  # Control
    treatment_costs = [0]    # Control cost
    
    for i in range(1, n_arms):
        col1, col2 = st.sidebar.columns(2)
        
        with col1:
            effect = st.number_input(
                f"T{i} Effect",
                min_value=0,
                max_value=40,
                value=max(5, i * 8),
                step=1,
                key=f"effect_{i}"
            ) / 100
            treatment_effects.append(-effect)  # Negative = reduces churn
        
        with col2:
            cost = st.number_input(
                f"T{i} Cost ($)",
                min_value=0,
                max_value=500,
                value=50 + i * 50,
                step=10,
                key=f"cost_{i}"
            )
            treatment_costs.append(cost)
    
    # Main content tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Power Analysis",
        "🎯 Decision Simulator", 
        "💰 ROI Calculator",
        "📈 Posterior Visualizer"
    ])
    
    # =========================================================================
    # TAB 1: Power Analysis
    # =========================================================================
    with tab1:
        st.header("Statistical Power Analysis")
        st.markdown("Estimate probability of detecting treatment effects")
        
        # Calculate required sample size
        st.subheader("Sample Size Calculator")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            target_power = st.slider(
                "Target Power",
                min_value=0.7,
                max_value=0.95,
                value=0.8,
                step=0.05
            )
        
        with col2:
            target_effect = st.slider(
                "Minimum Detectable Effect (%)",
                min_value=5,
                max_value=20,
                value=8,
                step=1
            ) / 100
        
        with col3:
            alpha_level = st.selectbox(
                "Significance Level",
                options=[0.01, 0.05, 0.10],
                index=1
            )
        
        # Calculate
        required_n = calculate_sample_size(target_effect, alpha_level, target_power, baseline_churn)
        
        # Display results
        col1, col2, col3, col4 = st.columns(4)
        
        col1.metric(
            "Required Sample Size",
            f"{required_n:,}",
            help="Per arm"
        )
        
        col2.metric(
            "Total Customers",
            f"{required_n * n_arms:,}",
            help="All arms combined"
        )
        
        weeks_required = np.ceil(required_n / 25)  # Assume 25 per week
        col3.metric(
            "Estimated Duration",
            f"{int(weeks_required)} weeks",
            help="Assuming 25 customers/arm/week"
        )
        
        cost_total = sum(treatment_costs) / n_arms * required_n * n_arms
        col4.metric(
            "Estimated Cost",
            f"${cost_total:,.0f}",
            help="Average intervention cost"
        )
        
        st.markdown("---")
        
        # Power curve
        st.subheader("Power Curves by Treatment Arm")
        
        # Simulate power for different sample sizes
        sample_sizes = np.arange(50, 501, 25)
        
        power_data = []
        for n in sample_sizes:
            for arm in range(1, n_arms):
                # Simplified power calculation
                effect = abs(treatment_effects[arm])
                
                # Using normal approximation
                z_alpha = stats.norm.ppf(1 - alpha_level/2)
                z_beta = (effect * np.sqrt(n)) / np.sqrt(2 * baseline_churn * (1 - baseline_churn))
                power = stats.norm.cdf(z_beta - z_alpha)
                
                power_data.append({
                    'Sample Size': n,
                    'Arm': f'Treatment {arm} ({abs(treatment_effects[arm]):.0%})',
                    'Power': power
                })
        
        df_power = pd.DataFrame(power_data)
        
        fig = px.line(
            df_power,
            x='Sample Size',
            y='Power',
            color='Arm',
            title='Statistical Power vs Sample Size',
            labels={'Power': 'Statistical Power', 'Sample Size': 'Sample Size per Arm'}
        )
        
        fig.add_hline(y=0.8, line_dash="dash", line_color="green", 
                     annotation_text="80% Power")
        fig.add_hline(y=0.9, line_dash="dash", line_color="blue",
                     annotation_text="90% Power")
        
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)
        
        # Recommendation
        st.info(f"""
        **💡 Recommendation:** With {sample_size_per_arm} customers per arm, you have approximately:
        - Treatment 1: {df_power[(df_power['Sample Size'] == sample_size_per_arm) & (df_power['Arm'].str.contains('Treatment 1'))]['Power'].values[0]:.1%} power
        - Treatment 2: {df_power[(df_power['Sample Size'] == sample_size_per_arm) & (df_power['Arm'].str.contains('Treatment 2'))]['Power'].values[0]:.1%} power (if 3+ arms)
        
        This {'✅ meets' if df_power[(df_power['Sample Size'] == sample_size_per_arm)]['Power'].min() >= target_power else '⚠️ does not meet'} your {target_power:.0%} power target.
        """)
    
    # =========================================================================
    # TAB 2: Decision Simulator
    # =========================================================================
    with tab2:
        st.header("Live Decision Simulator")
        st.markdown("Simulate test results and see Bayesian decision-making in action")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("Simulated Test Results")
            weeks_elapsed = st.slider(
                "Weeks Elapsed",
                min_value=1,
                max_value=8,
                value=4,
                help="How many weeks of data collected"
            )
        
        with col2:
            st.subheader("Priors")
            prior_alpha = st.number_input("Prior α", value=2, min_value=1, max_value=10)
            prior_beta = st.number_input("Prior β", value=2, min_value=1, max_value=10)
        
        # Simulate data
        n_observed = int(weeks_elapsed * 25)  # 25 per week
        
        # Generate simulated outcomes
        results = []
        posteriors = {}
        
        for arm in range(n_arms):
            true_churn_rate = baseline_churn + treatment_effects[arm]
            true_churn_rate = np.clip(true_churn_rate, 0, 1)
            
            # Simulate outcomes
            churned = np.random.binomial(1, true_churn_rate, size=n_observed)
            n_churned = churned.sum()
            
            # Compute posterior
            post_alpha, post_beta = compute_beta_posterior(
                prior_alpha, prior_beta, n_churned, n_observed - n_churned
            )
            
            posteriors[arm] = {
                'alpha': post_alpha,
                'beta': post_beta,
                'samples': sample_beta_posterior(post_alpha, post_beta)
            }
            
            results.append({
                'Arm': f'{"Control" if arm == 0 else f"Treatment {arm}"}',
                'Customers': n_observed,
                'Churned': n_churned,
                'Observed Rate': n_churned / n_observed,
                'Posterior Mean': post_alpha / (post_alpha + post_beta),
                '95% CI Lower': stats.beta.ppf(0.025, post_alpha, post_beta),
                '95% CI Upper': stats.beta.ppf(0.975, post_alpha, post_beta)
            })
        
        df_results = pd.DataFrame(results)
        
        # Display results table
        st.dataframe(
            df_results.style.format({
                'Observed Rate': '{:.1%}',
                'Posterior Mean': '{:.1%}',
                '95% CI Lower': '{:.1%}',
                '95% CI Upper': '{:.1%}'
            }),
            use_container_width=True
        )
        
        st.markdown("---")
        
        # Decision analysis
        st.subheader("Bayesian Decision Analysis")
        
        control_samples = posteriors[0]['samples']
        
        decision_results = []
        
        for arm in range(1, n_arms):
            treatment_samples = posteriors[arm]['samples']
            
            # Probability of superiority
            pos = compute_probability_superior(control_samples, treatment_samples, 0.08)
            
            # In ROPE
            diff = control_samples - treatment_samples
            in_rope = ((diff > -0.02) & (diff < 0.02)).mean()
            
            # Expected churn reduction
            expected_reduction = diff.mean()
            
            # Expected value
            ev_samples = calculate_expected_value(
                diff,
                monthly_revenue,
                avg_retention_months,
                treatment_costs[arm]
            )
            
            # Decision
            if pos > 0.90 and ev_samples.mean() > 50:
                decision = "✅ IMPLEMENT"
                decision_class = "success"
            elif in_rope > 0.95:
                decision = "≈ EQUIVALENT"
                decision_class = "warning"
            elif pos > 0.70:
                decision = "⚠️ PROMISING"
                decision_class = "warning"
            else:
                decision = "❌ INSUFFICIENT"
                decision_class = "danger"
            
            decision_results.append({
                'Treatment': f'Treatment {arm}',
                'P(Superior >8%)': f'{pos:.1%}',
                'P(in ROPE)': f'{in_rope:.1%}',
                'Expected Reduction': f'{expected_reduction:.1%}',
                'Expected Value': f'${ev_samples.mean():.0f}',
                'Decision': decision
            })
        
        df_decisions = pd.DataFrame(decision_results)
        
        st.dataframe(df_decisions, use_container_width=True)
        
        # Interpretation
        st.info("""
        **Decision Criteria:**
        - ✅ **IMPLEMENT**: P(Superior >8%) > 90% AND Expected Value > $50
        - ≈ **EQUIVALENT**: P(in ROPE <±2%) > 95% (no meaningful difference)
        - ⚠️ **PROMISING**: P(Superior) > 70% (continue monitoring)
        - ❌ **INSUFFICIENT**: Not enough evidence yet
        """)
    
    # =========================================================================
    # TAB 3: ROI Calculator
    # =========================================================================
    with tab3:
        st.header("ROI Calculator with Uncertainty")
        st.markdown("Calculate expected returns accounting for uncertainty in outcomes")
        
        # Select treatment to analyze
        treatment_to_analyze = st.selectbox(
            "Select Treatment to Analyze",
            options=[f"Treatment {i}" for i in range(1, n_arms)],
            index=min(1, n_arms - 2)
        )
        
        arm_idx = int(treatment_to_analyze.split()[-1])
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            adoption_rate = st.slider(
                "Expected Adoption Rate (%)",
                min_value=10,
                max_value=100,
                value=30,
                step=5,
                help="% of customers who accept the offer"
            ) / 100
        
        with col2:
            fleet_size = st.number_input(
                "Fleet Size",
                min_value=100,
                max_value=10000,
                value=1521,
                step=100,
                help="Total number of high-risk customers"
            )
        
        with col3:
            discount_rate = st.slider(
                "Discount Rate (%)",
                min_value=0,
                max_value=20,
                value=10,
                step=1,
                help="Annual discount rate for NPV calculation"
            ) / 100
        
        # Calculate ROI
        expected_effect = abs(treatment_effects[arm_idx])
        intervention_cost = treatment_costs[arm_idx]
        
        # Year 1
        adopters = int(fleet_size * adoption_rate)
        customers_retained = int(adopters * expected_effect)
        revenue_saved_y1 = customers_retained * monthly_revenue * avg_retention_months
        total_cost = adopters * intervention_cost
        net_profit_y1 = revenue_saved_y1 - total_cost
        roi_y1 = (net_profit_y1 / total_cost * 100) if total_cost > 0 else 0
        
        # 3-year NPV
        npv_y1 = net_profit_y1
        npv_y2 = npv_y1 * 0.8 / (1 + discount_rate)  # Assume 80% effectiveness in Y2
        npv_y3 = npv_y2 * 0.8 / (1 + discount_rate)  # Assume 80% effectiveness in Y3
        total_npv = npv_y1 + npv_y2 + npv_y3
        
        # Display metrics
        st.subheader("Financial Projection")
        
        col1, col2, col3, col4 = st.columns(4)
        
        col1.metric(
            "Year 1 Net Profit",
            f"${net_profit_y1:,.0f}",
            delta=f"{roi_y1:.0f}% ROI"
        )
        
        col2.metric(
            "3-Year NPV",
            f"${total_npv:,.0f}",
            delta=f"vs. ${total_cost:,.0f} cost"
        )
        
        payback_months = (total_cost / (revenue_saved_y1 / avg_retention_months)) if revenue_saved_y1 > 0 else float('inf')
        col3.metric(
            "Payback Period",
            f"{payback_months:.1f} mo" if payback_months < 100 else "N/A"
        )
        
        col4.metric(
            "Customers Retained",
            f"{customers_retained:,}",
            delta=f"out of {adopters:,} adopters"
        )
        
        st.markdown("---")
        
        # Uncertainty analysis
        st.subheader("Sensitivity Analysis")
        
        # Vary key assumptions
        adoption_scenarios = np.linspace(0.15, 0.50, 20)
        effect_scenarios = np.linspace(max(0.05, expected_effect * 0.5), 
                                      min(0.40, expected_effect * 1.5), 20)
        
        npv_grid = []
        
        for adopt in adoption_scenarios:
            for effect in effect_scenarios:
                adopters_scenario = fleet_size * adopt
                retained_scenario = adopters_scenario * effect
                revenue_scenario = retained_scenario * monthly_revenue * avg_retention_months
                cost_scenario = adopters_scenario * intervention_cost
                npv_scenario = revenue_scenario - cost_scenario
                
                npv_grid.append({
                    'Adoption Rate': adopt,
                    'Churn Reduction': effect,
                    'NPV': npv_scenario
                })
        
        df_sensitivity = pd.DataFrame(npv_grid)
        
        # Create heatmap
        pivot_table = df_sensitivity.pivot_table(
            values='NPV',
            index='Churn Reduction',
            columns='Adoption Rate',
            aggfunc='mean'
        )
        
        fig = go.Figure(data=go.Heatmap(
            z=pivot_table.values,
            x=[f'{x:.0%}' for x in pivot_table.columns],
            y=[f'{y:.0%}' for y in pivot_table.index],
            colorscale='RdYlGn',
            zmid=0,
            text=pivot_table.values,
            texttemplate='$%{text:,.0f}',
            textfont={"size": 8},
            colorbar=dict(title="NPV ($)")
        ))
        
        fig.update_layout(
            title='NPV Sensitivity Analysis',
            xaxis_title='Adoption Rate',
            yaxis_title='Churn Reduction Effect',
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.success(f"""
        **Interpretation:** 
        - Green zones = Profitable scenarios
        - Red zones = Unprofitable scenarios
        - Current assumptions (⭐): {adoption_rate:.0%} adoption, {expected_effect:.0%} effect = ${net_profit_y1:,.0f} Year 1 profit
        """)
    
    # =========================================================================
    # TAB 4: Posterior Visualizer
    # =========================================================================
    with tab4:
        st.header("Posterior Distribution Visualizer")
        st.markdown("See how Bayesian posteriors evolve as data accumulates")
        
        # Simulate accumulating data
        max_weeks = st.slider(
            "Weeks of Data",
            min_value=1,
            max_value=8,
            value=4,
            help="Drag to see posterior evolution"
        )
        
        # Generate data for selected week
        n_cumulative = int(max_weeks * 25)
        
        fig = go.Figure()
        
        x = np.linspace(0, 1, 1000)
        
        for arm in range(n_arms):
            true_rate = np.clip(baseline_churn + treatment_effects[arm], 0, 1)
            
            # Simulate outcomes
            churned = np.random.binomial(1, true_rate, size=n_cumulative)
            n_churned = churned.sum()
            
            # Posterior
            post_alpha, post_beta = compute_beta_posterior(
                prior_alpha, prior_beta,
                n_churned,
                n_cumulative - n_churned
            )
            
            # PDF
            y = stats.beta.pdf(x, post_alpha, post_beta)
            
            label = f"{'Control' if arm == 0 else f'Treatment {arm}'} (Mean: {post_alpha/(post_alpha+post_beta):.1%})"
            
            fig.add_trace(go.Scatter(
                x=x, y=y,
                mode='lines',
                name=label,
                fill='tozeroy',
                opacity=0.6
            ))
        
        fig.update_layout(
            title=f'Posterior Distributions After {max_weeks} Weeks',
            xaxis_title='Churn Probability',
            yaxis_title='Density',
            height=500,
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Prior vs Posterior comparison
        st.subheader("Prior vs Posterior")
        
        fig2 = go.Figure()
        
        # Show for treatment 1
        prior_y = stats.beta.pdf(x, prior_alpha, prior_beta)
        fig2.add_trace(go.Scatter(
            x=x, y=prior_y,
            mode='lines',
            name='Prior (Before Data)',
            line=dict(dash='dash', width=2)
        ))
        
        # Posterior for treatment 1
        arm_to_show = min(1, n_arms - 1)
        true_rate = np.clip(baseline_churn + treatment_effects[arm_to_show], 0, 1)
        churned = np.random.binomial(1, true_rate, size=n_cumulative)
        n_churned = churned.sum()
        
        post_alpha_show, post_beta_show = compute_beta_posterior(
            prior_alpha, prior_beta,
            n_churned,
            n_cumulative - n_churned
        )
        
        post_y = stats.beta.pdf(x, post_alpha_show, post_beta_show)
        fig2.add_trace(go.Scatter(
            x=x, y=post_y,
            mode='lines',
            name=f'Posterior (After {n_cumulative} Observations)',
            fill='tozeroy',
            opacity=0.6
        ))
        
        # True value
        fig2.add_vline(
            x=true_rate,
            line_dash="dot",
            line_color="red",
            annotation_text=f"True Value: {true_rate:.1%}"
        )
        
        fig2.update_layout(
            title=f'Learning Process: Treatment {arm_to_show}',
            xaxis_title='Churn Probability',
            yaxis_title='Density',
            height=400
        )
        
        st.plotly_chart(fig2, use_container_width=True)
        
        st.info("""
        **Key Insight:** As we collect more data, the posterior (solid line) 
        becomes narrower and converges toward the true value (red dotted line), 
        while moving away from the prior (dashed line). This is Bayesian learning in action!
        """)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: gray; font-size: 0.9rem;'>
        <p>📊 Built with Streamlit | 🎯 Portfolio Project | 🧮 Bayesian A/B Testing Framework</p>
        <p>Created by [Ella Ndala] | <a href='https://github.com/EllaN12'>GitHub</a> | <a href='https://linkedin.com/in/en-3623abc'>LinkedIn</a></p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == '__main__':
    main()

# %%
