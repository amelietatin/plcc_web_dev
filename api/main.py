from fastapi import FastAPI
import pandas as pd
from .params import *
from .data import load_data_to_bq, get_data

app = FastAPI()

# Load CSV data
#df = pd.read_csv('api/final_data_2015_2035.csv')
#load_data_to_bq(df, GCP_PROJECT, BQ_DATASET, TABLE, True)

@app.get("/")
def read_root():
    return {"message": "Welcome to the CSV API"}

@app.get("/data")
def data(table_name):
    query = f"""
        SELECT *
        FROM [`lewagon-lc-amelietatin.landcover.bioregion`]
    """
    print(query)
    df_bq = get_data(GCP_PROJECT, query)
    return df_bq.to_dict(orient='records')

@app.get("/data/{item_id}")
def get_data_item(item_id: str):
    query = f"""
        SELECT *
        FROM `{GCP_PROJECT}.{BQ_DATASET}.{TABLE}`
        WHERE SITECODE IS {item_id}
    """
    # if item_id >= len(df):
    #     return {"error": "Item not found"}
    df_bq = get_data(GCP_PROJECT, query)
    return df_bq.to_dict(orient='records')
