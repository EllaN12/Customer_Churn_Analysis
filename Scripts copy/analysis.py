
#%%
import pandas as pd
# importing spark session
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
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

# %%

#Building Spark Session
spark = SparkSession.builder.appName("Customer_Churn_Prediction").getOrCreate()
spark

# reading the data
data = spark.read.csv("/Users/ellandalla/Desktop/Customer_Churn_Analysis-/venv/Data/dataset.csv", header=True, inferSchema=True)
data.show(5)

#spark.stop()

# print the schema of the data
data.printSchema()

# Get data dimensions
print((data.count(), len(data.columns)))
columns = data.columns
data.describe().show()

data.dtypes

#Exploratory Data Analysis
# %%

#data_df = data.toPandas()

def numeric_profile_data(data):
    """Panda Profiling Function

    Args:
        data (DataFrame): A pandas DataFrame to profile

    Returns:
        DataFrame: A DataFrame with profiled data
    """
    # turn the data into a pandas DataFrame
    data_df = data.toPandas()
    
    # Filter numerical columns
    numerical_columns = data_df.select_dtypes(include=['int', 'float']).columns
    num_df = data_df[numerical_columns]
    profile_df = pd.concat([
        pd.Series(data_df[numerical_columns].dtypes, name="Dtype"),
        pd.Series(data_df[numerical_columns].count(), name="Count"),
        pd.Series(data_df[numerical_columns].isnull().sum(), name="NA Count"),
        pd.Series(data_df[numerical_columns].nunique(), name="Count Unique"),
        pd.Series(data_df[numerical_columns].min(), name="Min"),
        pd.Series(data_df[numerical_columns].max(), name="Max"),
        pd.Series(data_df[numerical_columns].mean(), name="Mean"),
        pd.Series(data_df[numerical_columns].median(), name="Median"),
        pd.Series(data_df[numerical_columns].mode().iloc[0], name="Mode"),
    ], axis=1)

    return profile_df, num_df
numeric_profile_data(data)



def category_profile_data(data):
    """Pandas Profiling Function for Categorical Data"""
    
    # turn the data into a pandas DataFrame
    data_df = data.toPandas()
    # Filter categorical columns
    categorical_columns = data_df.select_dtypes(include=['object']).columns
    
    cat_df = data_df[categorical_columns]

    profile_df = pd.concat([
        pd.Series(data_df[categorical_columns].dtypes, name="Dtype"),
        pd.Series(data_df[categorical_columns].count(), name="Count"),
        pd.Series(data_df[categorical_columns].isnull().sum(), name="NA Count"),
        pd.Series(data_df[categorical_columns].nunique(), name="Count Unique"),
        pd.Series(data_df[categorical_columns].min(), name="Min"),
        pd.Series(data_df[categorical_columns].max(), name="Max"),
        pd.Series(data_df[categorical_columns].mode().iloc[0], name="Mode"),
    ], axis=1)
    
    
    return profile_df
 
category_profile_data(data)
## Create a list of columns and their data types

category_profile_data(data)


data_df.columns

#obtain the data types of the columns
columns_with_datatypes = data.dtypes
numerical_cols = [col_name for col_name, col_type in columns_with_datatypes if col_type in ['int', 'bigint', 'float', 'double']]

categorical_cols = [col_name for col_name, col_type in columns_with_datatypes if col_type in ['string']]

categorical_cols

def visualize_categorical_data(data):
    """Visualize Categorical Data"""
    data_df = data.toPandas()
    categorical_columns = data_df.select_dtypes(include=['object']).columns
    # Iterate over each categorical column and create a bar plot
    for col in categorical_columns:
        # Calculate the count for each category in the column
        count_df = data_df[col].value_counts().reset_index()
        count_df.columns = [col, 'count']
        
        # Create the bar plot
        fig = px.bar(count_df, x=col, y='count', title=f"Customer Count by {col}", color='count')
        
        # Show the plot
        fig.show()


visualize_categorical_data(data)


def visualize_numerical_data(data):
    """Visualize Numerical Data"""
    data_df = data.toPandas()
    numerical_columns = data_df.select_dtypes(include=['int', 'float']).columns
    # Iterate over each numerical column and create a histogram
    for col in numerical_columns:
        # Create the histogram
        hist = px.histogram(data_df, x=col, title=f"{col} Histogram")
        box = px.box(data_df, y=col, title=f"{col} Boxplot")
        
        # Show the plot
        hist.show(), box.show()
    
visualize_numerical_data(data)
        

##Data Preprocessing
#%%
# Handling missing values using imputer
# Get column names and their corresponding data types


columns_with_missing_values = [column for column in data.columns if data.where(col(column).isNull()).count() > 0]
columns_with_missing_values

# Create an imputer object
imputer = Imputer(inputCols=columns_with_missing_values, outputCols=columns_with_missing_values).setStrategy("mean")
imputer = imputer.fit(data)
data = imputer.transform(data)

# Missing values Crosscheck
columns_with_missing_values_2 = [column for column in data.columns if data.where(col(column).isNull()).count() > 0]
columns_with_missing_values_2

## Removing outliers
# identifying outliers in the tenure column
data.select("*").where(col("tenure") > 100).show()
# Remove outliers
data = data.filter(data["tenure"]< 100)

# coutliers crosscheck
data.select("*").where(col("tenure") > 100).show()

#Save the preprocessed data
final_data = data
final_data.show(5)
data.write.mode("overwrite").option("header", "true").csv("/Users/ellandalla/Desktop/Customer_Churn_Analysis-/venv/Data/final_data.csv")

#%%
## Feature Engineering - Numerical
#Creating a Vector Assembler
numerical_vector_assembler = VectorAssembler(inputCols=numerical_cols, outputCol="numerical_features_vector")
numerical_vector_assembler
data = numerical_vector_assembler.transform(data)
data.show(5)

#scaling the numerical features
scaler = StandardScaler(inputCol="numerical_features_vector", outputCol="scaled_numerical_features", withStd=True, withMean=True)

data = scaler.fit(data).transform(data)
data.show(5)

## Feature Engineering - Categorical

categorical_cols_indexed = [name + "_Indexed" for name in categorical_cols ]
categorical_cols_indexed
indexer = StringIndexer(inputCols = categorical_cols, outputCols = categorical_cols_indexed)
data = indexer.fit(data).transform(data)
data.show(5)

categorical_cols_indexed.remove("Churn_Indexed")
categorical_cols_indexed.remove("customerID_Indexed")
categorical_cols_indexed

categorical_vector_assembler = VectorAssembler(inputCols=categorical_cols_indexed, outputCol="categorical_features_vector")
data = categorical_vector_assembler.transform(data)
data.show(5)

final_vector_assembler = VectorAssembler(inputCols=["scaled_numerical_features", "categorical_features_vector"], outputCol="final_feature_vector")
data = final_vector_assembler.transform(data)
data.show(5)
data.select(["final_feature_vector", "Churn_Indexed"]).show(5)

#%%
#DecisionTreeClassifier
train, test = data.randomSplit([0.7, 0.3], seed = 42)
train.count(), test.count()

# Train the decision tree model
train.show(5)
dt = DecisionTreeClassifier(featuresCol="final_feature_vector", labelCol="Churn_Indexed", maxDepth=7)
pipeline = Pipeline(stages=[dt])
model = pipeline.fit(train)

# Make predictions using test data
predictions_test = model.transform(test)
predictions_test.select("Churn", "Churn_Indexed", "prediction").show()

#%%
## Model Evaluation
evaluator = BinaryClassificationEvaluator(labelCol="Churn_Indexed")
auc_test = evaluator.evaluate(predictions_test, {evaluator.metricName: "areaUnderROC"})
auc_test

# evaluate the model using the training data
predictions_train = model.transform(train)
auc_train = evaluator.evaluate(predictions_train, {evaluator.metricName: "areaUnderROC"})
auc_train

def evaluate_dt(model_params):
    test_accuracies = []
    train_accuracies = []
    
    for maxDepth in model_params:
        # Train the decision tree model based on the maxDepth parameter
        dt = DecisionTreeClassifier(featuresCol="final_feature_vector", labelCol="Churn_Indexed", maxDepth=maxDepth)
        pipeline = Pipeline(stages=[dt])
        model = pipeline.fit(train)
        
        # Calculate the test error
        predictions_test = model.transform(test)
        evaluator = BinaryClassificationEvaluator(labelCol="Churn_Indexed")
        auc_test = evaluator.evaluate(predictions_test, {evaluator.metricName: "areaUnderROC"})
        # Append the test error to the test_accuracies list
        test_accuracies.append(auc_test)
        
        # Calculate the train error
        predictions_training = model.transform(train)
        evaluator = BinaryClassificationEvaluator(labelCol="Churn_Indexed")
        auc_training = evaluator.evaluate(predictions_training, {evaluator.metricName: "areaUnderROC"})
        train_accuracies.append(auc_training)
    return(test_accuracies, train_accuracies)

maxDepths = [2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20]
test_accs, train_accs = evaluate_dt(maxDepths)
df = pd.DataFrame(list(zip(maxDepths, test_accs, train_accs)), columns = ["maxDepth", "test_accuracy", "train_accuracy"], index= [numerical_cols + categorical_cols_indexed]
                  )

df


#%%
#Model Deployment
# How to reduce the churn rate ?
 # Get the feature importances
dt_model = model.stages[-1]
feature_importance = dt_model.featureImportances
feature_importance
scores = []
for  index, importance in enumerate(feature_importance):
    score = [index, importance]
    scores.append(score)
        
#?model.featureImportances  
print(scores)
df = pd.DataFrame(scores, columns=[ "feature_number", "score"], index = categorical_cols_indexed + numerical_cols)
df
df_sorted = df.sort_values(by="score", ascending=False)
fig = px.bar(df_sorted, x=df_sorted.index, y="score", title="Feature Importance")
fig.update_layout(xaxis = {'categoryorder':'total descending'})

#%%
# lets create a Bar Chart to visualize the customer churn rate by tenure, by gender and  device protection plans,

df = data.groupBy("tenure", "Churn").count().toPandas()
#df['tenure_quartile'] = pd.qcut(df['tenure'], q=4, labels=["Quart_1", "Quart_2", "Quart_3", "Quart_4"])
df_sorted = df.sort_values(by="tenure", ascending=True)
df_sorted 
# ReviewChurn Rate by Tenure Quartile
fig = px.bar(df_sorted, x="tenure", y="count", color="Churn", title="Customer Churn Rate by Tenure", barmode = "group") 
fig.show()  
#import pyspark
#print(pyspark.__version__)
#print(nbformat.__version__)
#!pip install --upgrade nbformat
# %%
gender_df = data.groupBy('gender', 'Churn').count().toPandas()
gender_df
fig = px.bar(gender_df, x = "gender", y="count", color="Churn", title="Customer Churn Rate by Gender", barmode = "group")   
fig.show()


# Understanding the churn rate by device protection plan

device_protection_df = data.groupBy('DeviceProtection', 'Churn').count().toPandas()
device_protection_df
fig = px.bar(device_protection_df, x = "DeviceProtection", y="count", color="Churn", title="Customer Churn Rate by Device Protection Plan", barmode = "group")
fig.show()


# %%
# Let's rerun the model By using a stacked model