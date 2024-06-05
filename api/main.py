from fastapi import FastAPI
import pandas as pd
from .params import *
from .data import load_data_to_bq, get_data

app = FastAPI()

# Load CSV data
#df = pd.read_csv('api/final_data_2015_2035.csv')
#load_data_to_bq(df, GCP_PROJECT, BQ_DATASET, TABLE, True)
GCP_PROJECT = 'lewagon-lc-amelietatin'
BQ_DATASET = 'landcover'

@app.get("/")
def read_root():
    return {"message": "Welcome to the CSV API"}

@app.get("/data")
def data(table_name):
    print(f"{GCP_PROJECT}.{BQ_DATASET}.{table_name}")
    query = f"""
        SELECT *
        FROM `{GCP_PROJECT}.{BQ_DATASET}.{table_name}`
    """
    print(query)
    df_bq = get_data(query)
    return df_bq.to_dict(orient='records')
