import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go

from google.oauth2 import service_account
from google.cloud import bigquery


#Setting everything up to load in the data
client = bigquery.Client()
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"]
)
client = bigquery.Client(credentials= credentials)
dataset_ref = bigquery.DatasetReference(st.secrets["PROJECT_ID"], st.secrets["DATASET"])


#Creating variables for all possible data options

##TO-DO MAKE THIS A LOOP TO EVENTUALLY GO OVER ALL TICKERS



table_ref_eth = dataset_ref.table("ETH_USDT")
eth_table = client.get_table(table_ref_eth)

table_ref_sol = dataset_ref.table("SOL_USDT")
sol_table = client.get_table(table_ref_sol)

#setting page config
st.set_page_config(layout="wide", page_title="Trading Tom invester dashboard", page_icon=":rocket:")

row1_1, row1_2 = st.columns((2, 3))

with row1_1:
    st.title("Trading Tom invester dashboard")


with row1_2:
    st.write(
        """
    ##
   This dashboard highlights the investment amount, return development over time, total return and performance against the S&P500
   for our investors.
   """
    )


# choose which ticker is displayed
ticker = st.sidebar.selectbox(
    'Ticker to Plot',
    options = ['BTC_USDT', 'ETH_USDT', 'SOL_USDT']
)

table_ref = dataset_ref.table(ticker)
table = client.get_table(table_ref)

#choose the amount of days displayed in the chart
days_to_plot = st.sidebar.slider(
    'Days to Plot',
    min_value = 1,
    max_value = 300,
    value = 120,
)

#Manipulating data
data = client.list_rows(table).to_dataframe()
data = data.sort_values(by = "datetime")
head = data.head()


#using the slider variabole to determine how much data the chart highlights
data_chart = data.tail(days_to_plot * 24)

#chart set-up
fig = go.Figure(data=[go.Candlestick(x=data_chart["datetime"], open=data_chart['open'], high=data_chart['high'], low=data_chart['low'], close=data_chart['close'])])

fig.update_layout(
    yaxis_title='Prices',
    xaxis_rangeslider_visible=False,
    font=dict(
        family="Arial",
        size=14,
    )

)

#setting up middle section of the dashboard
row2_1, row2_2 = st.columns((2, 1))

with row2_1:
    st.write(
        f"""**Price development of {ticker} over the past {days_to_plot} days**"""
    )
    st.plotly_chart(fig, use_container_width=True)


with row2_2:
    st.write(
        f"""**showing the price for {ticker}**"""
    )
    head
