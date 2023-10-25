<a id="Overview"></a>
## Overview
<a id="structure"></a>
- **Structure**
_Get data from UCI Machine Learning Repository, do some simple clean and transformation tasks, then save the cleaned data to csv file.
_Load data from csv file to Postgres and then load to Clickhouse
_Use Airflow to schedule the tasks
![image](https://github.com/tuannnh/homebase_tha/assets/51945324/e6334acd-a777-4603-947a-d1e3d065240f)

<a id="resources"></a>
- **Resources**
	- Vagrant
	- Docker
	- **Database:** PostgreSQL, ClickHouse
	- **ETL Pipeline:**
		- OS: Ubuntu 22.04
		- Apache Airflow
		- Python 3
		- Libraries: included in requirements.txt
<a id="etl_implementation"></a>
<a id="SetupEnvironment"></a>
### Setup environment, install packages and dependencies
#### 1. Install Vagrant
```bash
	brew install hashicorp/tap/hashicorp-vagrant
```
- Navigate to a folder. In this project I use **homebase_assignment**. Create a file named **Vagrantfile**

#### 2. Install Ubuntu 22.04
- Open created **Vagrantfile**
- Specify OS image to Ubuntu 22.04 and synced_folder for virtual machine and host machine
```ruby
# -*- mode: ruby -*-  
# vi: set ft=ruby :  
  
Vagrant.configure("2") do |config|  
 
  config.vm.provider "virtualbox" do |v|  
      v.memory = 4096  
      v.cpus = 2  
  end  
"forwarded_port", guest: 8080, host: 8080  
  config.vm.network "forwarded_port", guest: 5432, host: 5432  
  config.vm.network "forwarded_port", guest: 8123, host: 8123  
  
```
- Run the following command to start and access to the virtual the machine:
```bash
vagrant up
vagrant ssh
```
#### 3. Install Docker
```shell
# First, update existing list of packages
sudo apt update

# Next, install a few prerequisite packages which let `apt` use packages over HTTPS
sudo apt install apt-transport-https ca-certificates curl software-properties-common

# Then add the GPG key for the official Docker repository to system
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Add the Docker repository to APT sources
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Update existing list of packages again for the addition to be recognized
sudo apt update

# Make sure to install from the Docker repo instead of the default Ubuntu repo
apt-cache policy docker-ce

# Finally, install Docker
sudo apt install docker-ce

# addition, install docker compose
sudo apt install docker-compose
```
#### 4. Install Postgres and ClickHouse using Docker
- Create a **docker-compose.yaml** file as below
```yaml
version: "3"  
services:  
  
  # ----------------- #  
  #     PostgreSQL    #  # ----------------- #  postgres:  
    container_name: postgres  
    image: postgres:latest  
    environment:  
      POSTGRES_USER: postgres  
      POSTGRES_PASSWORD: postgres  
      PGDATA: /data/postgres  
    volumes:  
      - postgres-db:/data/postgres  
    ports:  
      - "5432:5432"  
  
  # ----------------- #  
  # ClickHouse Server #  # ----------------- #  
  clickhouse-server:  
    container_name: clickhouse-server  
    image: clickhouse/clickhouse-server:latest  
    volumes:  
      - ./dbfiles:/var/lib/clickhouse  
    ports:  
      - "8123:8123"  
      - "9000:9000"  
  
  # ----------------- #  
  # ClickHouse Client #  # ----------------- #  
  clickhouse-client:  
    container_name: clickhouse-client  
    image: clickhouse/clickhouse-client:latest  
    entrypoint:  
      - /bin/sleep  
    command:  
      - infinity  
  
volumes:  
  postgres-db:  
    driver: local
```
- Start Postgres and ClickHouse
```shell
docker compose up -d
```

#### 5. Install Apache Airflow and Setup Connection
```shell
# Update the System

apt-get update

# Install the required packages.**

apt-get install software-properties-common   apt-add-repository universe

# Update the packages.

apt-get update

# Install the required dependencies for Apache Airflow

apt-get install libmysqlclient-dev   
apt-get install libssl-dev   
apt-get install libkrb5-dev

# Install the Apache-Airflow on system

# Install the python-virtual Environment.

apt install python3-virtualenv   
virtualenv airflow_example

# Activate the source.

source airflow_example/bin/activate

# Install the apache-airflow.

export AIRFLOW_HOME=~/airflow   
pip3 install apache-airflow

# Install typing_extension.

pip3 install typing_extensions

# Init Airflow SQLite DB
airflow db init


# Set the Apache-Airflow login credentials for airflow web interface

airflow users create --username admin --firstname admin --lastname testing --role Admin --email admin@domain.com

# Start the Apache-Airflow web interface.

airflow webserver -p 8080

# Set up connection for Postgres and ClickHouse

Navigate to Admin - Connection - Add a new record:

# Postgres:
Connection Id: homebase_postgres
Connection Type: Postgres
Host: localhost
Schema: <created-schema>
Login: postgres
Password: homebase_postgres
Port: 5432

Save

# ClickHouse:
Connection Id: homebase_clickhouse
Connection Type: Sqlite
Host: localhost
Schema: <created-schema>
Login: default
Password: <leave_empty>
Port: <leave_empty> (default port 9000)

Save
```

- Install packages and dependencies
```shell
pip install -r requirements.txt
```

<a id="ETL"></a>
## ETL Implementation
Use Python to implement the ETL tasks 
<a id="extract"></a>
- **Extract and Transform:** Download data from remote source **[UCI Machine Learning Repository](https://archive.ics.uci.edu/ml/index.php).** Implement some simple transformations and  summary statistics
```python
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
```
<a id="transform"></a>
- **Load data to Postgres:** Having some simple reformation: replace '-' character in "**restaurant_names**" field, capitalize names
```python
import pandas as pd
import psycopg2

# Connect to the PostgreSQL database
conn = psycopg2.connect(
    host="localhost",
    port="5432",
    database="homebase_assignment",
    user="postgres",
    password="postgres"
)

cursor = conn.cursor()
cursor.execute("DROP TABLE IF EXISTS stg_wine_quality")
create_table_query = '''
CREATE TABLE stg_wine_quality
(
    fixed_acidity        real,
    volatile_acidity     real,
    citric_acid          real,
    residual_sugar       real,
    chlorides            real,
    free_sulfur_dioxide  real,
    total_sulfur_dioxide real,
    density              real,
    pH                   real,
    sulphates            real,
    alcohol              real,
    alcohol_level        VARCHAR(6)
);
'''
cursor.execute(create_table_query)

# Execute the COPY command to insert new data
try:
    with open('/home/vagrant/airflow/dags/data/cleaned_data.csv', 'r') as file:
        # skip header
        next(file)
        cursor.copy_from(file, 'stg_wine_quality', sep=',')
        conn.commit()
        row_count = cursor.rowcount
        print("Data loaded successfully. Rows affected:", row_count)
except (Exception, psycopg2.Error) as e:
    conn.rollback()
    print("Error during data copy:", str(e))

conn.commit()
conn.close()
```
<a id="load"></a>
- **Load data to ClickHouse:** Load the transformed data to PostgreSQL
```python
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow_clickhouse_plugin.hooks.clickhouse import ClickHouseHook

# Connect to Postgres
postgres_hook = PostgresHook(postgres_conn_id='homebase_postgres')
postgres_conn = postgres_hook.get_conn()
postgres_cursor = postgres_conn.cursor()

# Connect to ClickHouse
clickhouse_hook = ClickHouseHook(clickhouse_conn_id='homebase_clickhouse')
postgres_cursor.execute('SELECT * FROM stg_wine_quality')
data = postgres_cursor.fetchall()
clickhouse_hook.execute('TRUNCATE TABLE wine_quality;')
clickhouse_hook.execute('INSERT INTO wine_quality VALUES', data)
```
<a id="orchestration"></a>
- **Orchestration:** Schedule the ETL task to run daily, monitor running processes and logs using **Apache Airflow**
```shell
# Change directory to airflow home
cd $AIRFLOW_HOME

# Create dags folder to put the dag file
mkdir dags

# Create data folder to store csv file
mkdir data

# Don't forget copy tasks folder to dags folder
```

```python
from datetime import timedelta
from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.utils.dates import days_ago

default_args = {
    'owner': 'Tuan Nguyen',
    'start_date': days_ago(0),
    'email': ['mail@hungtuan.me'],
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

dag = DAG(
    'homebase_assignment',
    default_args=default_args,
    description='Homebase take home assignment',
    schedule_interval='@hourly'
)

# ETL tasks
extract_and_transform = BashOperator(
    task_id='extract_and_transform',
    bash_command='python ${AIRFLOW_HOME}/dags/tasks/extract_and_transform.py',
    dag=dag
)

# Load data to postgres task
load_data_to_postgres = BashOperator(
    task_id='load_data_to_postgres',
    bash_command='python ${AIRFLOW_HOME}/dags/tasks/load_data_to_postgres.py',
    dag=dag
)

# Load data to clickhouse task
load_data_to_clickhouse = BashOperator(
    task_id='load_data_to_clickhouse',
    bash_command='python ${AIRFLOW_HOME}/dags/tasks/load_data_to_clickhouse.py',
    dag=dag
)

# Schedule Pipeline
extract_and_transform >> load_data_to_postgres >> load_data_to_clickhouse

if __name__ == "__main__":
    dag.test()
```
<a id="dashboard_and_reports"></a>
