
import pandas as pd
import geopandas as gpd

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
    client = bigquery.Client(credentials=credentials, location='EU')

    query_job = client.query(query)
    result = query_job.result()
    df = result.to_dataframe()

    print(f"✅ Data loaded, with shape {df.shape}")
    print(df.head(1))

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
    client = bigquery.Client(project=GCP_PROJECT,credentials=credentials, location='EU')

    assert isinstance(data, pd.DataFrame)
    full_table_name = f"{gcp_project}.{bq_dataset}.{table}"
    print(Fore.BLUE + f"\nSave data to BigQuery @ {full_table_name}...:" + Style.RESET_ALL)

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

    files_dict = {
         'final_df' : 'final_table_no_negative.csv',
         'bioregion' : 'pa_infos_csv/new_csvs/bioregion.csv',
         'habitat_class' : 'pa_infos_csv/new_csvs/habitat_class.csv',
        'impact_management' : 'pa_infos_csv/new_csvs/impact_management.csv',
        'species' : 'pa_infos_csv/new_csvs/species.csv',
        'date_ranges': 'date_ranges.csv'
    }

    for tablename, filename in files_dict.items():

        path = os.path.join(root, 'raw_data', filename)
        table = pd.read_csv(path)
        #table_2 = table.drop(columns=["Unnamed: 0"])
        #print(table_2.head())
        load_data_to_bq(table, GCP_PROJECT, BQ_DATASET, tablename, True)

    # shapefile = gpd.read_file(os.path.join(root, 'raw_data/sample_protected_areas_624', "protected_areas_624.shp"))
    # load_data_to_bq(shapefile, GCP_PROJECT, BQ_DATASET, 'protected_areas_shp', True)
