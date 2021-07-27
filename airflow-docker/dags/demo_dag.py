import logging
from datetime import timedelta
from airflow import DAG
from airflow.utils.dates import timezone
from airflow.models import Variable

from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.operators.dummy import DummyOperator

from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.providers.google.cloud.transfers.postgres_to_gcs import PostgresToGCSOperator
from airflow.providers.google.cloud.transfers.gcs_to_local import GCSToLocalFilesystemOperator
from airflow.providers.google.cloud.transfers.local_to_gcs import LocalFilesystemToGCSOperator
from airflow.providers.google.cloud.transfers.gcs_to_bigquery import GCSToBigQueryOperator
from airflow.utils.task_group import TaskGroup

import pandas as pd

GCS_BUCKET = Variable.get('gcs_landing_bucket')
PROJECT_ID = Variable.get('gcp_project')
DAGS_FOLDER = '/opt/airflow/dags'
DATASET_NAME = 'demo_dataset'


BUCKET_NAME = GCS_BUCKET[5:]

def _transform_data(file):
    df = pd.read_json(f'{DAGS_FOLDER}/{file}', lines=True)
    print(df)
    if 'status' in df.columns:
        df.rename(columns={'status':'success'}, inplace=True)
        df['success'] = df['success'].astype('bool')
    print(df.dtypes)
    df.to_csv(f'{DAGS_FOLDER}/{file}_cleaned.csv', index=False)

default_args = {
    'owner': 'natchanon',
    'tags':['demo']
}

schedule_interval = Variable.get('schedule_interval')

with DAG('demo_dag', 
         default_args=default_args,
         schedule_interval=f'{schedule_interval}',
         start_date=timezone.datetime(2021, 6, 8),
         catchup=False) as dag:

    start = DummyOperator(task_id='start')

    with TaskGroup(group_id='PostgresToDataLake') as PostgresToDataLake:
        extract_user_log_data = PostgresToGCSOperator(
            task_id='extract_user_log_data', 
            postgres_conn_id='my_postgres_conn',
            gcp_conn_id='google_cloud_default',
            sql='select * from user_log;',
            bucket=f'{BUCKET_NAME}', 
            filename=f'raw_data/user_log',
        )

        extract_users_data = PostgresToGCSOperator(
            task_id='extract_users_data', 
            postgres_conn_id='my_postgres_conn',
            gcp_conn_id='google_cloud_default',
            sql='select * from users;',
            bucket=f'{BUCKET_NAME}', 
            filename=f'raw_data/users',
        )

    with TaskGroup(group_id='Transformation') as Transformation:
        read_user_log = GCSToLocalFilesystemOperator(
            task_id='read_user_log',
            bucket=f'{BUCKET_NAME}',
            object_name=f'raw_data/user_log',
            filename=f'{DAGS_FOLDER}/user_log',
        )

        read_users = GCSToLocalFilesystemOperator(
            task_id='read_users',
            bucket=f'{BUCKET_NAME}',
            object_name=f'raw_data/users',
            filename=f'{DAGS_FOLDER}/users',
        )

        transform_user_log = PythonOperator(
            task_id='transform_user_log',
            python_callable=_transform_data,
            op_kwargs={'file': 'user_log'},
        )

        transform_users = PythonOperator(
            task_id='transform_users',
            python_callable=_transform_data,
            op_kwargs={'file': 'users'},
        )

        upload_user_log_cleaned_to_GCS = LocalFilesystemToGCSOperator(
            task_id='upload_user_log_cleaned_to_GCS',
            src=f'{DAGS_FOLDER}/user_log_cleaned.csv',
            dst=f'cleaned/user_log.csv',
            bucket=f'{BUCKET_NAME}'
        )

        upload_users_cleaned_to_GCS = LocalFilesystemToGCSOperator(
            task_id='upload_users_cleaned_to_GCS',
            src=f'{DAGS_FOLDER}/users_cleaned.csv',
            dst=f'cleaned/users.csv',
            bucket=f'{BUCKET_NAME}'
        )

        read_user_log >> transform_user_log >> upload_user_log_cleaned_to_GCS
        read_users >> transform_users >> upload_users_cleaned_to_GCS

    with TaskGroup(group_id='LoadToDataWarehouse') as LoadToDataWarehouse:
        load_user_log = GCSToBigQueryOperator(
            task_id='load_user_log',
            bucket=f'{BUCKET_NAME}',
            source_objects=['cleaned/user_log.csv'],
            source_format='CSV',
            destination_project_dataset_table=f"{DATASET_NAME}.user_log",
            write_disposition='WRITE_TRUNCATE',
            skip_leading_rows=1,
            autodetect=True
        )

        load_users = GCSToBigQueryOperator(
            task_id='load_users',
            bucket=f'{BUCKET_NAME}',
            source_objects=['cleaned/users.csv'],
            source_format='CSV',
            destination_project_dataset_table=f"{DATASET_NAME}.users",
            write_disposition='WRITE_TRUNCATE',
            skip_leading_rows=1,
            autodetect=True
        )
        

    end = DummyOperator(task_id='end')
    
    start >> PostgresToDataLake >> Transformation >> LoadToDataWarehouse >> end