import pandas
from ucimlrepo import fetch_ucirepo
import pandas as pd

# Import dataset from UCI Machine Learning Repository
car_evaluation = fetch_ucirepo(id=186)
# Get pandas dataframe

data = pandas.DataFrame(car_evaluation.data.features)
print(f"Raw data: {data}")

# Clean and Transform
# Fill missing values with N/A value for better reporting
data = data.fillna(0)

# Remove duplicates
data = data.drop_duplicates()


# Transform data
def group_alcohol(alcohol: float):
    alcohol_bucket_levels = [(8, 10, 'Low'), (10, 13, 'Medium'), (13, 15, 'High')]
    for bucket in alcohol_bucket_levels:
        if bucket[0] <= alcohol < bucket[1]:
            return bucket[2]
    return None


data['alcohol_level'] = data['alcohol'].apply(group_alcohol)
# Processed data
print(f"Processed data: {data}")

# Save the cleaned data to CSV file
data.to_csv('/home/vagrant/airflow/dags/data/cleaned_data.csv', index=False)

# Generate summary statistic for three key variables
key_variables = ['alcohol', 'fixed_acidity', 'citric_acid']

# Define summary statistic attributes
summary_stat_attributes = {
    'column': [],
    'mean': [],
    'median': [],
    'std_dev': [],
    'min': [],
    'max': [],
    'count': [],
}

# Calculate summary statistics
for column in key_variables:
    summary_stat_attributes['column'].append(column)
    summary_stat_attributes['mean'].append(data[column].mean())
    summary_stat_attributes['median'].append(data[column].median())
    summary_stat_attributes['std_dev'].append(data[column].std())
    summary_stat_attributes['min'].append(data[column].min())
    summary_stat_attributes['max'].append(data[column].max())
    summary_stat_attributes['count'].append(data[column].count())

summary_statistic = pd.DataFrame(summary_stat_attributes)
print(f"Summary statistic: #{summary_statistic}")