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