# Customer Churn Prediction Analysis

## Overview

This project predicts customer churn for a telecommunications company using a dataset of 7,043 customers with 21 attributes. By analyzing customer demographics and developing predictive models, we identify key factors driving churn, such as contract types, service usage, and customer tenure. These insights enable the company to proactively address customer concerns, improve retention strategies, and reduce revenue loss.

## Business Problem

- Develop predictive models to accurately forecast customer churn
- Identify key demographic factors that significantly influence churn rates
- Formulate targeted customer retention strategies based on identified churn drivers

## Data Source

- **Dataset**: 7,043 customers with 21 attributes
- **Source**: [Kaggle - Telco Customer Churn](https://www.kaggle.com/datasets/blastchar/telco-customer-churn)

## Technical Stack

### Data Processing & Analysis
- **PySpark & Spark SQL**: Data cleaning, exploration, and manipulation at scale
- **Pandas & NumPy**: Data manipulation and analysis
- **Spark ML**: Feature engineering (imputation, vector assembly, scaling, encoding)

### Machine Learning
- **Decision Tree Classifier**: Baseline interpretable model
- **H2O AutoML Stacked Ensemble**: Advanced ensemble model for optimal performance
- **MLflow**: Experiment tracking and model versioning

### Visualization & Deployment
- **Matplotlib & Plotly**: Data visualization
- **Dash**: Interactive web dashboard
- **AWS Elastic Beanstalk**: Cloud deployment

## Model Performance

| Model | AUC-ROC | AUC-PR | F1 Score |
|-------|---------|--------|----------|
| Decision Tree Classifier | 72% | 52.6% | 78.5% |
| H2O AutoML Stacked Ensemble | **87%** | - | 64% |

**Selected Model**: H2O AutoML Stacked Ensemble (87% AUC-ROC)

The stacked ensemble model significantly outperforms the baseline Decision Tree Classifier, achieving strong performance in identifying customers likely to churn with 80% True Positive Rate at 20% False Positive Rate.

## Key Findings

### Churn Drivers Identified
1. **Tenure**: Customers with tenure of 40 days or less are significantly more likely to churn
2. **Contract Type**: Monthly contract subscribers show higher churn rates
3. **Demographics**: Senior citizens and customers without dependents are at higher risk
4. **Service Subscriptions**: Customers not subscribing to add-on services (device protection, online backup, tech support) churn more frequently

### Feature Importance
- **High Impact**: Tenure, Contract Type, Device Protection
- **Low Impact**: Gender, TV Streaming, Movie Streaming (equal distribution in churn/non-churn groups)

### Model Limitations
- Potential bias from class imbalance in the dataset
- Some features showed limited predictive power due to equal distribution across churn categories

## Business Recommendations

1. **Enhanced Contract Plans**: Develop comprehensive contract options with attractive add-on services for data and voice customers
2. **Targeted Marketing**: Conduct campaigns focused on senior citizens and customers identified as high-churn risk
3. **Early Intervention**: Implement retention programs for customers in their first 40 days
4. **Service Bundling**: Promote device protection, online backup, and tech support packages

## Live Dashboard

Access the interactive dashboard: [Customer Churn Dashboard](http://dashapp-env-v7-env.eba-m32nwi36.us-east-1.elasticbeanstalk.com)

## Project Structure

```
Customer_Churn_Analysis/
|
+-- Prediction_Data/          # Data files
|   +-- dataset.csv           # Original dataset
|   +-- final_data.csv/       # Processed data
|   +-- recommendation.csv    # Churn predictions
|
+-- Scripts/                  # Source code
|   +-- CC_analysis.py        # EDA and Decision Tree modeling
|   +-- AutoML_Prediction.py  # H2O AutoML modeling
|   +-- Recommendation.py     # Generate churn recommendations
|
+-- Models/                   # Trained models
|   +-- decision_tree_model/
|   +-- model_h2o_stacked_ensemble
|
+-- Results/                  # Outputs and reports
+-- app.py                    # Dash web application
+-- requirements.txt          # Dependencies
+-- Dockerfile                # Container configuration
```

## Installation

### Prerequisites
- Python 3.9+
- Docker (optional, for containerized deployment)

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/EllaN12/Customer_Churn_Analysis.git
   cd Customer_Churn_Analysis
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Start the Dash application locally:
```bash
python app.py
```

Or visit the deployed dashboard: [Live Demo](http://dashapp-env-v7-env.eba-m32nwi36.us-east-1.elasticbeanstalk.com)

## Acknowledgments

- **Dash** - Web framework for interactive dashboards
- **PySpark & Spark ML** - Distributed data processing and ML
- **H2O AutoML** - Automated machine learning
- **Scikit-learn** - ML utilities and evaluation metrics
- **MLflow** - Experiment tracking
