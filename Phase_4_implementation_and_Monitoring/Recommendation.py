#%%
# Importing Libraries
import pandas as pd
import os
from pathlib import Path


# ─── Resolve project root (works from any working directory) ──────────────────
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
DATA_PATH = PROJECT_ROOT / 'Results' / 'churn_prediction.csv'
OUTPUT_DIR = PROJECT_ROOT / 'Results'
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# Importing Data
path = DATA_PATH

Churn_data = pd.read_csv(path)
Churn_data.rename(columns ={'Churn': "Actual_Churn", 
                            'predict':"Predicted_Churn",
                            "No": "No_Churn_Rate",
                            "Yes": "Churn_Rate"}, inplace = True)	
df = Churn_data.copy()



# Filtering definitions

def contract_label(contract):
    if contract == 'Month-to-month' or contract == 'One year':
        return 'Create and Promote mid to long term contracts'
    else:
        return 'Other'

def tech_service_label(row):
    if row['TechSupport'] == 'No' or row['OnlineBackup'] == 'No' or row['OnlineSecurity'] == 'No' or row['DeviceProtection'] == 'No':
        return 'Promote Tech Services'
    else:
        return 'Other'

def entertainment_label(row):
    if row['StreamingTV'] == 'Yes' or row['StreamingMovies'] == 'Yes':
        return 'Enhance and Promote Entertainment Services'
    else:
        return 'Other'

def communication_label(row):
    if row['SeniorCitizen'] == 'Yes':
        return 'Engage with senior citizens to better understand their needs and concerns.'
    elif row['Dependents'] == 'No':
        return 'Customize communication for customers with no dependents.'
    else:
        return 'Other'

# Assuming definitions to the dataframe columns

recommendation_df = df[(df['Predicted_Churn'] == "Yes") & (df['Churn_Rate'] > 0.50)] \
    .assign(contract_label=df['Contract'].apply(contract_label)) \
    .assign(tech_service_label=df.apply(lambda row: tech_service_label(row), axis=1)) \
    .assign(entertainment_label=df.apply(lambda row: entertainment_label(row), axis=1)) \
    .assign(communication_label=df.apply(lambda row: communication_label(row), axis=1))

# Print or use recommendation_df as needed
print(recommendation_df)

recommendation_df

for column in recommendation_df.columns:
    # Check if the column is not numeric (assuming non-numeric columns contain "others")
    if recommendation_df[column].dtype == 'object':
        # Check if any value in the column is "others"
        if (recommendation_df[column] == 'Other').any():
            # Replace "others" with "No action needed"
            recommendation_df.loc[recommendation_df[column] == 'Other', column] = 'No action needed'
            
            
recommendation_df['contract_label'].unique()


#save
path = OUTPUT_DIR / 'recommendation.csv'
data_path = path.resolve()
recommendation_df.to_csv(data_path)
# %%
