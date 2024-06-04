
import pandas as pd
# import geopandas as gpd

from google.cloud import bigquery
from colorama import Fore, Style
from pathlib import Path
from google.cloud import bigquery
from google.oauth2 import service_account
from api.params import *

import os


def get_data(
        query:str,
        data_has_header=True
    ) -> pd.DataFrame:
    """
    Retrieve `query` data from BigQuery, or from `cache_path` if the file exists
    Store at `cache_path` if retrieved from BigQuery for future use
    """
    credentials = service_account.Credentials.from_service_account_file(GOOGLE_APP)
    print(Fore.BLUE + "\nLoad data from BigQuery server..." + Style.RESET_ALL)
    client = bigquery.Client(project=GCP_PROJECT,credentials=credentials)

    query_job = client.query(query)
    result = query_job.result()
    df = result.to_dataframe()

    # Store as CSV if the BQ query returned at least one valid line
    if df.shape[0] > 1:
        df.to_csv('test.csv', header=data_has_header, index=False)

    print(f"✅ Data loaded, with shape {df.shape}")

    return df

def load_data_to_bq(
        data: pd.DataFrame,
        gcp_project:str,
        bq_dataset:str,
        table: str,
        truncate: bool
    ) -> None:
    """
    - Save the DataFrame to BigQuery
    - Empty the table beforehand if `truncate` is True, append otherwise
    """
    credentials = service_account.Credentials.from_service_account_file(GOOGLE_APP)
    print(Fore.BLUE + "\nLoad data from BigQuery server..." + Style.RESET_ALL)
    client = bigquery.Client(project=GCP_PROJECT,credentials=credentials)

    assert isinstance(data, pd.DataFrame)
    full_table_name = f"{gcp_project}.{bq_dataset}.{table}"
    print(Fore.BLUE + f"\nSave data to BigQuery @ {full_table_name}...:" + Style.RESET_ALL)

    # Load data onto full_table_name

    # 🎯 HINT for "*** TypeError: expected bytes, int found":
    # After preprocessing the data, your original column names are gone (print it to check),
    # so ensure that your column names are *strings* that start with either
    # a *letter* or an *underscore*, as BQ does not accept anything else

    # TODO: simplify this solution if possiBble, but students may very well choose another way to do it
    # We don't test directly against their own BQ tables, but only the result of their query
    #data.columns = [f"_{column}" if not str(column)[0].isalpha() and not str(column)[0] == "_" else str(column) for column in data.columns]

    #client = bigquery.Client()
    #credentials = service_account.Credentials.from_service_account_file(GOOGLE_APP)
    #client = bigquery.Client(project=gcp_project,credentials=credentials)

    # Define write mode and schema
    write_mode = "WRITE_TRUNCATE" if truncate else "WRITE_APPEND"
    job_config = bigquery.LoadJobConfig(write_disposition=write_mode)

    print(f"\n{'Write' if truncate else 'Append'} {full_table_name} ({data.shape[0]} rows)")

    # Load data
    job = client.load_table_from_dataframe(data, full_table_name, job_config=job_config)
    result = job.result()  # wait for the job to complete

    print(f"✅ Data saved to bigquery, with shape {data.shape}")


if __name__ == '__main__':
    root = os.path.dirname(os.path.dirname(__file__))

    # files_dict = {
    #     'final_df' : 'final_data_2015_2035.csv',
    #     'bioregion' : 'pa_infos_csv/new_csvs/bioregion.csv',
    #     'habitat_class' : 'pa_infos_csv/new_csvs/habitat_class.csv',
    #     'impact_management' : 'pa_infos_csv/new_csvs/impact_management.csv',
    #     'species' : 'pa_infos_csv/new_csvs/species.csv',
    #     'date_ranges': 'date_ranges.csv'
    # }

    # for tablename, filename in files_dict.items():

    #     path = os.path.join(root, 'raw_data', filename)
    #     table = pd.read_csv(path)
    #     load_data_to_bq(table, GCP_PROJECT, BQ_DATASET, tablename, True)

    # shapefile = gpd.read_file(os.path.join(root, 'raw_data/sample_protected_areas_624', "protected_areas_624.shp"))
    # load_data_to_bq(shapefile, GCP_PROJECT, BQ_DATASET, 'protected_areas_shp', True)

    # python api/data.py

    # query = f"""
    #     SELECT *
    #     FROM `{GCP_PROJECT}.{BQ_DATASET}.{TABLE}`
    #     LIMIT 100
    # """
    # name = f'{GCP_PROJECT}.{BQ_DATASET}.{TABLE}'
    # print(name)
    #     #WHERE pickup_datetime BETWEEN '{min_date}' AND '{max_date}'
    # df = get_data(GCP_PROJECT, query)
    # print(df.head())
