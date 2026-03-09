
#%%


import sys
print(sys.executable)


import pandas as pd
import numpy as np

# importing spark session
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count, when, isnan, isnull, mean, min, max

# data visualization modules
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

# pyspark SQL functions
from pyspark.sql.functions import *

# pyspark data preprocessing modules
from pyspark.ml.feature import *
from pyspark.sql.functions import count, when, col
from pyspark.sql import DataFrame

# pyspark data modeling and model evaluation modules
from pyspark.ml.classification import *
from pyspark.ml.evaluation import *
from pyspark.ml import *

# AutoML prediction
from pyspark.sql import SparkSession
import pysparkling
from pysparkling import *
from h2o.automl import H2OAutoML

# SMOTE for class imbalance
from imblearn.over_sampling import SMOTE

# Feature importance utilities
from sklearn.preprocessing import LabelEncoder

import os
import warnings
warnings.filterwarnings('ignore')

# %%
# =============================================================================
# 0.0 SPARK SESSION & DATA INGESTION
# =============================================================================

spark = SparkSession.builder \
    .appName("Customer Churn - H2O AutoML with SMOTE") \
    .getOrCreate()

# Paths
data_dir = "Prediction_Data/final_data.csv"
absolute_path_data = os.path.abspath(data_dir)
print(f"Data path: {absolute_path_data}")

# Reading the data
final_data = spark.read.csv(absolute_path_data, header=True, inferSchema=True)
final_data.show(5)

data_df = final_data.toPandas()

# %%
# =============================================================================
# 1.0 EXPLORATORY IMBALANCE CHECK
# =============================================================================

print("\n--- Class Distribution (Before SMOTE) ---")
class_counts = data_df['Churn'].value_counts()
print(class_counts)
print(f"\nImbalance ratio (majority / minority): {class_counts.max() / class_counts.min():.2f}")

fig_imbalance = px.bar(
    x=class_counts.index,
    y=class_counts.values,
    labels={'x': 'Churn', 'y': 'Count'},
    title='Class Distribution Before SMOTE',
    color=class_counts.index,
)
fig_imbalance.show()

# %%
# =============================================================================
# 2.0 SMOTE — SYNTHETIC MINORITY OVERSAMPLING
# =============================================================================

x_cols = [
    'gender', 'SeniorCitizen', 'Partner', 'Dependents', 'tenure',
    'PhoneService', 'MultipleLines', 'InternetService', 'OnlineSecurity',
    'OnlineBackup', 'DeviceProtection', 'TechSupport', 'StreamingTV',
    'StreamingMovies', 'Contract', 'PaperlessBilling', 'PaymentMethod',
    'MonthlyCharges', 'TotalCharges',
]
y_col = 'Churn'

# --- Encode categorical features for SMOTE (requires numeric input) ---
label_encoders = {}
data_encoded = data_df.copy()

for col_name in x_cols:
    if data_encoded[col_name].dtype == 'object':
        le = LabelEncoder()
        data_encoded[col_name] = le.fit_transform(data_encoded[col_name].astype(str))
        label_encoders[col_name] = le

# Encode target
target_le = LabelEncoder()
data_encoded[y_col] = target_le.fit_transform(data_encoded[y_col].astype(str))

X = data_encoded[x_cols]
y = data_encoded[y_col]

# Apply SMOTE
smote = SMOTE(random_state=123, sampling_strategy='auto')
X_resampled, y_resampled = smote.fit_resample(X, y)

print(f"\n--- Class Distribution (After SMOTE) ---")
unique, counts = np.unique(y_resampled, return_counts=True)
for cls, cnt in zip(unique, counts):
    print(f"  {target_le.inverse_transform([cls])[0]}: {cnt}")

# --- Decode back to original categorical values for H2O ---
resampled_df = pd.DataFrame(X_resampled, columns=x_cols)
resampled_df[y_col] = target_le.inverse_transform(y_resampled)

for col_name, le in label_encoders.items():
    resampled_df[col_name] = le.inverse_transform(resampled_df[col_name].astype(int))

print(f"\nResampled dataset shape: {resampled_df.shape}")

# Visualize after SMOTE
after_counts = resampled_df[y_col].value_counts()
fig_after = px.bar(
    x=after_counts.index,
    y=after_counts.values,
    labels={'x': 'Churn', 'y': 'Count'},
    title='Class Distribution After SMOTE',
    color=after_counts.index,
)
fig_after.show()

# %%
# =============================================================================
# 3.0 H2O PREPARATION
# =============================================================================

h2o.init(
    max_mem_size=4,
    strict_version_check=False
)

# Convert SMOTE-resampled data to H2O Frame
data_h2o = h2o.H2OFrame(resampled_df)
data_h2o[y_col] = data_h2o[y_col].asfactor()

data_h2o.describe()
print(f"\nH2O frame dimensions: {data_h2o.shape}")

# Also keep the original (non-SMOTE) data as H2O Frame for final prediction
original_h2o = h2o.H2OFrame(data_df)
original_h2o[y_col] = original_h2o[y_col].asfactor()

# %%
# =============================================================================
# 4.0 RUN H2O AUTOML (trained on SMOTE-balanced data)
# =============================================================================

aml = H2OAutoML(
    nfolds=5,
    max_runtime_secs=3 * 60,
    seed=123,
    balance_classes=True,          # H2O-level class balancing as extra safeguard
    exclude_algos=['DeepLearning'],
    sort_metric='AUC',
)

aml.train(
    x=x_cols,
    y=y_col,
    training_frame=data_h2o
)

leaderboard_df = aml.leaderboard.as_data_frame()
print("\n--- AutoML Leaderboard (Top 10) ---")
print(leaderboard_df.head(10).to_string(index=False))

# %%
# =============================================================================
# 5.0 BEST MODEL — SAVE & LOAD
# =============================================================================

best_model = aml.leader
best_model_id = leaderboard_df['model_id'][0]
print(f"\nBest model: {best_model_id}")

# Use a relative model save path
model_save_dir = os.path.abspath('Models')
os.makedirs(model_save_dir, exist_ok=True)

saved_path = h2o.save_model(
    best_model,
    path=model_save_dir,
    filename='model_h2o_stacked_ensemble',
    force=True
)
print(f"Model saved to: {saved_path}")

# %%
# =============================================================================
# 6.0 FEATURE IMPORTANCE — STACKED ENSEMBLE EXTRACTION
# =============================================================================

def extract_stacked_ensemble_feature_importance(model, x_cols):
    """
    Extract feature importance from an H2O Stacked Ensemble model.

    Stacked Ensembles don't have direct .varimp(), so we extract importance
    from each base learner and aggregate via weighted averaging (using the
    metalearner coefficients when available).

    Parameters
    ----------
    model : h2o model
        The trained H2O model (ideally a StackedEnsemble).
    x_cols : list
        List of predictor column names.

    Returns
    -------
    pd.DataFrame
        Aggregated feature importance ranked by importance.
    """
    model_type = model.__class__.__name__
    print(f"\nModel type: {model_type}")

    # --- Case 1: Non-ensemble model — use varimp directly ---
    if 'StackedEnsemble' not in str(model.model_id):
        print("Model is not a Stacked Ensemble. Extracting varimp directly.")
        varimp = model.varimp(use_pandas=True)
        if varimp is not None and not varimp.empty:
            return varimp
        else:
            print("No variable importance available for this model type.")
            return pd.DataFrame()

    # --- Case 2: Stacked Ensemble — aggregate base learner importances ---
    print("Extracting feature importance from Stacked Ensemble base learners...")

    # Get metalearner and base model IDs
    metalearner = h2o.get_model(model.metalearner().model_id)
    base_model_ids = model.params['base_models']['actual']
    base_model_ids = [m['name'] for m in base_model_ids]

    print(f"  Metalearner: {metalearner.model_id}")
    print(f"  Base models ({len(base_model_ids)}): {base_model_ids}")

    # Try to get metalearner coefficients for weighting
    try:
        meta_coeffs = metalearner.coef()
        # Filter out intercept; keys are base model names
        weights = {k: abs(v) for k, v in meta_coeffs.items() if k != 'Intercept'}
        total_weight = sum(weights.values())
        if total_weight > 0:
            weights = {k: v / total_weight for k, v in weights.items()}
        print(f"  Metalearner weights: {weights}")
    except Exception:
        # Equal weighting fallback
        weights = {mid: 1.0 / len(base_model_ids) for mid in base_model_ids}
        print("  Using equal weights (metalearner coefficients not available).")

    # Collect importances from each base learner
    importance_records = []

    for model_id in base_model_ids:
        try:
            base_model = h2o.get_model(model_id)
            varimp = base_model.varimp(use_pandas=True)

            if varimp is not None and not varimp.empty:
                weight = weights.get(model_id, 1.0 / len(base_model_ids))
                varimp = varimp.rename(columns={
                    'variable': 'feature',
                    'relative_importance': 'importance'
                })
                varimp['weighted_importance'] = varimp['importance'] * weight
                varimp['source_model'] = model_id
                importance_records.append(varimp[['feature', 'importance', 'weighted_importance', 'source_model']])
                print(f"    ✓ {model_id}: {len(varimp)} features")
            else:
                print(f"    ✗ {model_id}: no varimp available")
        except Exception as e:
            print(f"    ✗ {model_id}: error — {e}")

    if not importance_records:
        print("  No feature importances could be extracted from any base learner.")
        return pd.DataFrame()

    # Aggregate: sum weighted importances across base learners per feature
    all_importances = pd.concat(importance_records, ignore_index=True)

    aggregated = (
        all_importances
        .groupby('feature', as_index=False)
        .agg(
            weighted_importance=('weighted_importance', 'sum'),
            num_models=('source_model', 'nunique'),
        )
        .sort_values('weighted_importance', ascending=False)
        .reset_index(drop=True)
    )

    # Normalize to relative scale (0–1)
    max_imp = aggregated['weighted_importance'].max()
    if max_imp > 0:
        aggregated['scaled_importance'] = aggregated['weighted_importance'] / max_imp
    else:
        aggregated['scaled_importance'] = 0.0

    return aggregated, all_importances


# --- Run feature importance extraction ---
feature_importance_result = extract_stacked_ensemble_feature_importance(best_model, x_cols)

if isinstance(feature_importance_result, tuple):
    aggregated_importance, per_model_importance = feature_importance_result
else:
    aggregated_importance = feature_importance_result
    per_model_importance = pd.DataFrame()

print("\n--- Aggregated Feature Importance (Stacked Ensemble) ---")
print(aggregated_importance.to_string(index=False))

# %%
# =============================================================================
# 6.1 FEATURE IMPORTANCE VISUALIZATION
# =============================================================================

if not aggregated_importance.empty:
    # Bar chart — aggregated importance
    fig_importance = px.bar(
        aggregated_importance.sort_values('scaled_importance', ascending=True),
        x='scaled_importance',
        y='feature',
        orientation='h',
        title='Stacked Ensemble — Aggregated Feature Importance',
        labels={'scaled_importance': 'Relative Importance', 'feature': 'Feature'},
        color='scaled_importance',
        color_continuous_scale='Viridis',
    )
    fig_importance.update_layout(height=600, yaxis={'categoryorder': 'total ascending'})
    fig_importance.show()

    # Heatmap — per-base-learner importance
    if not per_model_importance.empty:
        pivot_df = per_model_importance.pivot_table(
            index='feature', columns='source_model', values='importance', fill_value=0
        )
        fig_heatmap, ax = plt.subplots(figsize=(12, 8))
        sns.heatmap(pivot_df, annot=True, fmt='.1f', cmap='YlOrRd', ax=ax)
        ax.set_title('Feature Importance by Base Learner')
        plt.tight_layout()
        plt.show()

# %%
# =============================================================================
# 7.0 PREDICTION (on original unbalanced data)
# =============================================================================

predictions_h2o = best_model.predict(original_h2o)
predictions_df = predictions_h2o.as_data_frame()

print(f"\nPredictions shape: {predictions_df.shape}")
print(predictions_df.head())

final_prediction_df = pd.concat([data_df.reset_index(drop=True), predictions_df], axis=1)
df = final_prediction_df

print(df.head())

# %%
# =============================================================================
# 8.0 MODEL EVALUATION
# =============================================================================

model_performance = best_model.model_performance(original_h2o)
print("\n--- Model Performance Summary ---")
print(model_performance)

roc_plot = model_performance.plot(type='roc')
pr_plot = model_performance.plot(type='pr')
auc_roc_plot = model_performance.plot(type='auc_roc')
gain_lift_plot = model_performance.plot(type='gains_lift')

# Confusion matrix
print("\n--- Confusion Matrix ---")
print(model_performance.confusion_matrix())

# %%
# =============================================================================
# 9.0 SAVE RESULTS
# =============================================================================

results_dir = os.path.abspath('Results')
os.makedirs(results_dir, exist_ok=True)

# Save predictions
predictions_path = os.path.join(results_dir, 'churn_prediction_df.pkl')
df.to_pickle(predictions_path)
print(f"\nPredictions saved to: {predictions_path}")

# Save feature importance
if not aggregated_importance.empty:
    importance_path = os.path.join(results_dir, 'feature_importance.csv')
    aggregated_importance.to_csv(importance_path, index=False)
    print(f"Feature importance saved to: {importance_path}")

# %%
# =============================================================================
# 10.0 VISUALIZATION — POTENTIAL CHURN CUSTOMERS
# =============================================================================

def visualize_categorical_data(data):
    """Visualize Categorical Data for predicted churn customers."""
    df_viz = data.copy()
    categorical_columns = df_viz.select_dtypes(include=['object']).columns.tolist()

    # Remove non-feature columns
    cols_to_remove = ['customerID', 'predict']
    categorical_columns = [c for c in categorical_columns if c not in cols_to_remove]

    for col_name in categorical_columns:
        count_df = df_viz[col_name].value_counts().reset_index()
        count_df.columns = [col_name, 'count']
        fig = px.bar(
            count_df, x=col_name, y='count',
            title=f"Customer Count by {col_name}",
            color='count'
        )
        fig.show()


def visualize_numerical_data(data):
    """Visualize Numerical Data for predicted churn customers."""
    df_viz = data.copy()
    numerical_columns = df_viz.select_dtypes(include=['int', 'float']).columns.tolist()

    # Remove probability columns from viz if present
    cols_to_skip = ['No', 'Yes']
    numerical_columns = [c for c in numerical_columns if c not in cols_to_skip]

    for col_name in numerical_columns:
        hist = px.histogram(df_viz, x=col_name, title=f"{col_name} Histogram")
        box = px.box(df_viz, y=col_name, title=f"{col_name} Boxplot")
        hist.show()
        box.show()


visualize_categorical_data(df)
visualize_numerical_data(df)

# Minimum churn probability
min_prob = df[df['predict'] == 'Yes']['Yes'].min()
print(f"\nMinimum churn probability (among predicted churners): {min_prob:.4f}")

# %%
