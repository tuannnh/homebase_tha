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