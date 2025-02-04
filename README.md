# Project Title

## Overview
This project aims to predict customer churn for a telecommunications company using a dataset of 7043 customers. By analyzing customer demographics and developing predictive models, we can identify key factors driving churn, such as contract types, service usage, and customer tenure. These insights will enable the company to proactively address customer concerns, improve customer retention strategies, and ultimately reduce revenue loss due to churn.

## Business Problem / Context
- Develop predictive models to accurately forecast customer churn
- Conduct in-depth analysis to identify key demographic factors that significantly influence churn rates
- Formulate targeted customer retention strategies based on the identified churn drivers.

## Data Sources
- A dataset of 7,043 customers with 21 attributes
- Source of the data: Kaggle : https://www.kaggle.com/datasets/blastchar/telco-customer-churn

## Methods and Tools
### Data Processing & Analysis
- Data Analysis and Feature Engineering:
  . Pandas and Spark: Utilized for data cleaning, exploration, and manipulation.
  . Spark ML: Employed feature engineering techniques like imputation for missing values, vector assembly for combining features, and scaling/encoding for numerical and categorical data, respectively.
- Machine Learning: (Assuming you use a library like scikit-learn)
  . Predictive Modeling: Developed churn prediction models using machine learning algorithms from scikit-learn (or similar library).- 

### Machine Learning
- Models tested:
. Decision Tree Classifier:
. H20 AutoML stacked ensemble model  
- Evaluation metrics:
. DTC:
Auc = 72 %
Auc_pr = 52.6%
F1 score = 78.5 % 
Roc_Auc curve: upward sloppping and steeper
PR_curve: upwards splopping up to 20% recall rate then downward slopping 
Feature Importance: Tenure, Gender, Device Protection
. H20 AutoML satcked Ensemble: 
Auc = 87%
Roc_Auc curve. Upward slopping with 80% TPR at 20% FPR
Auc_pr = downward slopping 
F1 score: 64%

- Performance summary:
. DTC:
The ROC AUC score suggests marginal performance beyond random guessing. While the F1 score of 78% indicates a reasonable balance between precision and recall, precision drops sharply at a threshold where approximately 20% of instances are predicted as positive, suggesting a potential trade-off between recall and precision

. H20 AutoML satcked Ensemble:
"The stacked ensemble model outperforms the Decision Tree Classifier (DTC), achieving an AUC score of 87% in distinguishing customers likely to churn. It demonstrates strong performance in identifying a significant portion of true positive cases early in testing."
"However, the model exhibits a downward-sloping Precision-Recall curve and an F1 score of 66%, indicating potential room for improvement in balancing precision and recall."
"Based on its overall performance, the stacked ensemble model was selected for making predictions."

The stacked ensemble model was retained to make predictions .

- Model limitations:
. Both models may be susceptible to biases arising from class imbalance within the dataset.
. Features such as gender, TV streaming, and movie streaming subscriptions demonstrated limited predictive power.
This is likely due to an approximately equal distribution of subscribers and non-subscribers for these services within the population, hindering their ability to effectively distinguish between churning and non-churning customers.


## Key Findings
- Main insights discovered;
- Some feature classified as important did not provide enough details about users ability to churn ( example : gender and equal % of men and women were likely to churn).
- From the exploratory analysis and the review of feature importance from the Decision Tree Classifier, it is evident that customers with a tenure of 40 days or less and those who subscribe to monthly contracts are more likely to churn. Additional factors contributing to churn include: Demographics: Senior citizens and customers without dependents. Lack of Subscriptions: Customers not subscribing to add-on services such as device protection plans, online backups, and tech support.
Refer to the dashbaord:  http://dashapp-env-v7-env.eba-m32nwi36.us-east-1.elasticbeanstalk.com
- Business implications:
. Telco company reduce customers attrition 
.. by Developing Comprehensive Contract Plans with Enhanced Add-On Services for Data and Voice Customers
.. Develop and Conduct Targeted Marketing Campaigns based on demeographics ( senior citizens, customers more likely to churn)


## Deliverables
List of what's included in the repository:
- 
- Scripts
- Documentation
- Models
- Datasets (if public)

## Installation Instructions

### Prerequisites
- Python 3.9+
- Docker (optional, for containerized deployment)

### Setup
1. Clone the repository:
   ```
   git clone https://github.com/EllaN12/Customer_Churn_Analysis.git
   cd Customer_Churn_analysis
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage Instructions

1. Start the Dash application:
   ```
   python app.py
   ```
 or visit http://dashapp-env-v7-env.eba-m32nwi36.us-east-1.elasticbeanstalk.com


## Project Structure
```
project/
│
├── prediction_data/               # Data files
├── src/               # Source code
├── models/            # Trained models
├── results/           # Figures, tables, etc.
├── requirements.txt   # Dependencies
└── README.md
```

### Key Components
- **Analysis.py implements** Exploratory Data Aanalysis and decision Tree Classifier modeling and evaluation
- **AutoML_Prediction.py**  predictive modeling using H20 AutoML 
- **recommendation.py** list of customers who are more likely than not to churn.



## Acknowledgments
- Dash for the web framework
- SparkML for machine learning lifecycle management
- SparkSQL, Pandas and NumPy for data manipulation 
- Matplotlib for data visualization
- Scikit-learn for machine learning utilities
- H20 AutoML and Decition Tree Classifier for modeling


