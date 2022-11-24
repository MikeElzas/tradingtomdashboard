import streamlit as st
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

##TO-DO MAKE THIS A LOOP TO EVENTUALLY GO OVER ALL TICKERS

table_ref = dataset_ref.table("BTC_USDT")
table = client.get_table(table_ref)

table_ref_eth = dataset_ref.table("ETH_USDT")
eth_table = client.get_table(table_ref_eth)

table_ref_sol = dataset_ref.table("SOL_USDT")
sol_table = client.get_table(table_ref_sol)


# Sidebar options
ticker = st.sidebar.selectbox(
    'Ticker to Plot',
    options = ['BTC_USDT', 'ETH_USDT', 'SOL_USDT']
)

days_to_plot = st.sidebar.slider(
    'Days to Plot',
    min_value = 1,
    max_value = 300,
    value = 120,
)

dict_options = {"BTC_USDT": table,
                "ETH_USDT": eth_table,
                "SOL_USDT": sol_table}

ticker = dict_options[ticker]



data = client.list_rows(ticker).to_dataframe()

data = data.sort_values(by = "datetime")

head = data.head()

head

data_chart = data.tail(days_to_plot * 24)

fig = go.Figure(data=[go.Candlestick(x=data_chart["datetime"], open=data_chart['open'], high=data_chart['high'], low=data_chart['low'], close=data_chart['close'])])


#fig.update_layout(
 #   yaxis_title='Prices',
  #  font=dict(
   #     family="Arial",
    #    size=14,
     #   color="MidnightBlue"
    #)
#)
st.plotly_chart(fig, use_container_width=True)
