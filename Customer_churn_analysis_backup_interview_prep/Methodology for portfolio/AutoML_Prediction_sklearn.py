"""
AutoML Churn Prediction Pipeline
Portfolio Project: Automated Machine Learning for Churn Prediction

Uses multiple classifiers with cross-validation, SMOTE for imbalanced data,
and saves predictions for downstream analysis.
"""
#%%
import os
import sys
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Import config for centralized directory management
_SCRIPT_DIR = Path(__file__).resolve().parent if "__file__" in globals() else Path.cwd()
_PROJECT_DIR = _SCRIPT_DIR.parent
if str(_PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(_PROJECT_DIR))

try:
    from config import results_dir
except ModuleNotFoundError:
    results_dir = str(Path(__file__).resolve().parents[1] / "Results")
    Path(results_dir).mkdir(parents=True, exist_ok=True)

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import cross_val_score, StratifiedKFold, train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import classification_report, roc_auc_score, confusion_matrix
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.svm import SVC
from imblearn.over_sampling import SMOTE
import joblib

sns.set_style('whitegrid')

#%%
# =============================================================================
# 1.0 Load Data
# =============================================================================

print("="*80)
print("AUTOML CHURN PREDICTION PIPELINE")
print("="*80)

# Load raw telco churn data
# Expects WA_Fn-UseC_-Telco-Customer-Churn.csv in the working directory
# or in the project root
data_candidates = [
    os.path.join(str(_PROJECT_DIR), 'WA_Fn-UseC_-Telco-Customer-Churn.csv'),
    'WA_Fn-UseC_-Telco-Customer-Churn.csv',
    os.path.join(results_dir, 'churn_raw.csv')
]

df = None
for candidate in data_candidates:
    if os.path.exists(candidate):
        df = pd.read_csv(candidate)
        print(f"✓ Loaded data from: {candidate}")
        break

if df is None:
    print("⚠️  Raw data file not found. Creating synthetic dataset for demonstration.")
    np.random.seed(42)
    n = 7043
    df = pd.DataFrame({
        'customerID': [f'CUST_{i:04d}' for i in range(n)],
        'gender': np.random.choice(['Male', 'Female'], n),
        'SeniorCitizen': np.random.choice([0, 1], n, p=[0.84, 0.16]),
        'Partner': np.random.choice(['Yes', 'No'], n),
        'Dependents': np.random.choice(['Yes', 'No'], n, p=[0.30, 0.70]),
        'tenure': np.random.exponential(30, n).clip(0, 72).astype(int),
        'PhoneService': np.random.choice(['Yes', 'No'], n, p=[0.90, 0.10]),
        'MultipleLines': np.random.choice(['Yes', 'No', 'No phone service'], n),
        'InternetService': np.random.choice(['Fiber optic', 'DSL', 'No'], n, p=[0.44, 0.34, 0.22]),
        'OnlineSecurity': np.random.choice(['Yes', 'No', 'No internet service'], n),
        'OnlineBackup': np.random.choice(['Yes', 'No', 'No internet service'], n),
        'DeviceProtection': np.random.choice(['Yes', 'No', 'No internet service'], n),
        'TechSupport': np.random.choice(['Yes', 'No', 'No internet service'], n),
        'StreamingTV': np.random.choice(['Yes', 'No', 'No internet service'], n),
        'StreamingMovies': np.random.choice(['Yes', 'No', 'No internet service'], n),
        'Contract': np.random.choice(['Month-to-month', 'One year', 'Two year'], n, p=[0.55, 0.21, 0.24]),
        'PaperlessBilling': np.random.choice(['Yes', 'No'], n),
        'PaymentMethod': np.random.choice(['Electronic check', 'Mailed check', 'Bank transfer (automatic)', 'Credit card (automatic)'], n),
        'MonthlyCharges': np.random.uniform(18, 119, n),
        'TotalCharges': np.random.uniform(18, 8685, n),
        'Churn': np.random.choice(['Yes', 'No'], n, p=[0.265, 0.735])
    })

print(f"Dataset shape: {df.shape}")
print(f"Churn rate: {(df['Churn'] == 'Yes').mean():.1%}")

#%%
# =============================================================================
# 2.0 Preprocessing
# =============================================================================

print("\n" + "="*60)
print("PREPROCESSING")
print("="*60)

df_clean = df.copy()

# Convert TotalCharges to numeric
if 'TotalCharges' in df_clean.columns:
    df_clean['TotalCharges'] = pd.to_numeric(df_clean['TotalCharges'], errors='coerce')
    df_clean['TotalCharges'].fillna(df_clean['TotalCharges'].median(), inplace=True)

# Drop customerID if present
if 'customerID' in df_clean.columns:
    df_clean.drop('customerID', axis=1, inplace=True)

# Encode binary columns
binary_cols = ['gender', 'Partner', 'Dependents', 'PhoneService', 'PaperlessBilling']
for col in binary_cols:
    if col in df_clean.columns:
        df_clean[col] = (df_clean[col] == 'Yes').astype(int)

# Encode multi-category columns
multi_cols = ['MultipleLines', 'InternetService', 'OnlineSecurity', 'OnlineBackup',
              'DeviceProtection', 'TechSupport', 'StreamingTV', 'StreamingMovies',
              'Contract', 'PaymentMethod']

for col in multi_cols:
    if col in df_clean.columns:
        le = LabelEncoder()
        df_clean[col] = le.fit_transform(df_clean[col].astype(str))

# Target variable
df_clean['Churn_binary'] = (df_clean['Churn'] == 'Yes').astype(int)
df_clean.drop('Churn', axis=1, inplace=True)

print(f"✓ Preprocessed: {df_clean.shape}")
print(f"  - Features: {df_clean.shape[1] - 1}")
print(f"  - Missing values: {df_clean.isnull().sum().sum()}")

#%%
# =============================================================================
# 3.0 Feature Engineering
# =============================================================================

print("\n" + "="*60)
print("FEATURE ENGINEERING")
print("="*60)

# Add interaction features
if 'tenure' in df_clean.columns and 'MonthlyCharges' in df_clean.columns:
    df_clean['tenure_charges'] = df_clean['tenure'] * df_clean['MonthlyCharges']
    df_clean['early_tenure'] = (df_clean['tenure'] <= 1).astype(int)
    print("✓ Added: tenure_charges, early_tenure")

print(f"Final features: {df_clean.shape[1] - 1}")

#%%
# =============================================================================
# 4.0 Train/Test Split
# =============================================================================

X = df_clean.drop('Churn_binary', axis=1)
y = df_clean['Churn_binary']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

print(f"\nTrain: {X_train.shape[0]:,} samples")
print(f"Test:  {X_test.shape[0]:,} samples")
print(f"Train churn rate: {y_train.mean():.1%}")
print(f"Test churn rate:  {y_test.mean():.1%}")

#%%
# =============================================================================
# 5.0 Handle Imbalance with SMOTE
# =============================================================================

print("\n" + "="*60)
print("HANDLING CLASS IMBALANCE (SMOTE)")
print("="*60)

smote = SMOTE(random_state=42)
X_train_bal, y_train_bal = smote.fit_resample(X_train, y_train)

print(f"Before SMOTE: {y_train.value_counts().to_dict()}")
print(f"After SMOTE:  {pd.Series(y_train_bal).value_counts().to_dict()}")

#%%
# =============================================================================
# 6.0 Scale Features
# =============================================================================

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train_bal)
X_test_scaled = scaler.transform(X_test)

#%%
# =============================================================================
# 7.0 Train Models
# =============================================================================

print("\n" + "="*60)
print("TRAINING MODELS")
print("="*60)

models = {
    'Logistic Regression': LogisticRegression(max_iter=1000, random_state=42),
    'Random Forest': RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1),
    'Gradient Boosting': GradientBoostingClassifier(n_estimators=100, random_state=42),
}

cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
results = {}

for name, model in models.items():
    print(f"\nTraining {name}...")
    
    cv_scores = cross_val_score(model, X_train_scaled, y_train_bal, 
                                cv=cv, scoring='roc_auc', n_jobs=-1)
    
    model.fit(X_train_scaled, y_train_bal)
    
    y_pred = model.predict(X_test_scaled)
    y_prob = model.predict_proba(X_test_scaled)[:, 1]
    
    test_auc = roc_auc_score(y_test, y_prob)
    
    results[name] = {
        'model': model,
        'cv_auc_mean': cv_scores.mean(),
        'cv_auc_std': cv_scores.std(),
        'test_auc': test_auc,
        'y_pred': y_pred,
        'y_prob': y_prob
    }
    
    print(f"  CV AUC: {cv_scores.mean():.3f} ± {cv_scores.std():.3f}")
    print(f"  Test AUC: {test_auc:.3f}")

#%%
# =============================================================================
# 8.0 Select Best Model
# =============================================================================

print("\n" + "="*60)
print("MODEL COMPARISON")
print("="*60)

best_model_name = max(results, key=lambda k: results[k]['test_auc'])
best_result = results[best_model_name]

print(f"\n{'Model':<25} {'CV AUC':>10} {'Test AUC':>10}")
print("-"*50)
for name, res in sorted(results.items(), key=lambda x: x[1]['test_auc'], reverse=True):
    marker = " <- BEST" if name == best_model_name else ""
    print(f"{name:<25} {res['cv_auc_mean']:>10.3f} {res['test_auc']:>10.3f}{marker}")

print(f"\n✓ Best model: {best_model_name} (AUC={best_result['test_auc']:.3f})")

#%%
# =============================================================================
# 9.0 Generate Predictions on Full Dataset
# =============================================================================

# Save predictions  (results_dir from config)
print("\n" + "="*60)
print("GENERATING PREDICTIONS")
print("="*60)

# Predict on full preprocessed dataset
X_full = df_clean.drop('Churn_binary', axis=1)
X_full_scaled = scaler.transform(X_full)

best_model = best_result['model']
y_full_pred = best_model.predict(X_full_scaled)
y_full_prob = best_model.predict_proba(X_full_scaled)

# Build output dataframe
output_df = df[['gender', 'SeniorCitizen', 'Partner', 'Dependents', 'tenure',
                'InternetService', 'Contract', 'PaymentMethod', 
                'MonthlyCharges', 'Churn']].copy() if 'Contract' in df.columns else df.copy()

output_df = output_df.rename(columns={'Churn': 'Actual_Churn'})
output_df['predict'] = ['Yes' if p == 1 else 'No' for p in y_full_pred]
output_df['No'] = y_full_prob[:, 0]
output_df['Yes'] = y_full_prob[:, 1]

predictions_path = os.path.join(results_dir, 'churn_prediction_df.pkl')
output_df.to_pickle(predictions_path)
print(f"✓ Saved predictions pickle: {predictions_path}")

csv_path = os.path.join(results_dir, 'churn_prediction.csv')
output_df.to_csv(csv_path)
print(f"✓ Saved predictions CSV: {csv_path}")

# Feature importance (for tree-based models)
if hasattr(best_model, 'feature_importances_'):
    importance_df = pd.DataFrame({
        'feature': X_full.columns,
        'importance': best_model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    importance_path = os.path.join(results_dir, 'feature_importance.csv')
    importance_df.to_csv(importance_path, index=False)
    print(f"✓ Saved feature importance: {importance_path}")
    
    print("\nTop 10 Features:")
    print(importance_df.head(10).to_string(index=False))

print("\n✅ AUTOML PIPELINE COMPLETE")
print(f"Results saved to: {results_dir}")

# %%
