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