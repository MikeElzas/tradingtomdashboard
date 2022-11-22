import streamlit as st
import os
import numpy as np
import pandas as pd
import plotly.graph_objects as go



from google.oauth2 import service_account
from google.cloud import bigquery

client = bigquery.Client()
#PROJECT_ID = os.environ.get("PROJECT_ID")
#DATASET = os.environ.get("DATASET")

credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"]
)

client = bigquery.Client(credentials= credentials)

dataset_ref = bigquery.DatasetReference(st.secrets["PROJECT_ID"], st.secrets["DATASET"])
table_ref = dataset_ref.table("BTC_USDT")
table = client.get_table(table_ref)




st.markdown("""# This is a chart
## This is a sub header
This is text""")

data = client.list_rows(table).to_dataframe()

fig = go.Figure(data=[go.Candlestick(x=data["datetime"], open=data['open'], high=data['high'], low=data['low'], close=data['close'])])

fig.update_layout(
    yaxis_title='Prices',
    font=dict(
        family="Arial",
        size=14,
        color="MidnightBlue"
    )
)
fig.show()
