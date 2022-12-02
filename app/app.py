import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from htbuilder import div, big, h2, styles
from htbuilder.units import rem
import altair as alt
import random

from google.oauth2 import service_account
from google.cloud import bigquery

#color schemes
COLOR_RED = "#FF4B4B"
COLOR_BLUE = "#1C83E1"
COLOR_CYAN = "#00C0F2"

#Setting everything up to load in the data
client = bigquery.Client()
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"]
)
client = bigquery.Client(credentials= credentials)
dataset_ref = bigquery.DatasetReference(st.secrets["PROJECT_ID"], st.secrets["DATASET"])

#Setting up functions to use in variables later

def display_dial(title, value, color):
        st.markdown(
            div(
                style=styles(
                    text_align="center",
                    color=color,
                    padding=(rem(0.8), 0, rem(3), 0),
                )
            )(
                h2(style=styles(font_size=rem(0.8), font_weight=600, padding=0))(title),
                big(style=styles(font_size=rem(3), font_weight=800, line_height=1))(
                    value
                ),
            ),
            unsafe_allow_html=True,
        )

############################################

#setting page config
st.set_page_config(layout="wide", page_title="Trading Tom investor dashboard", page_icon=":rocket:")

row1_1, row1_2 = st.columns((2, 2))

with row1_1:
    st.title("Trading Tom investor dashboard")

with row1_2:
    st.write(
        """
    ##
   This dashboard highlights the investment amount, return development over time, total return and performance against a benchmark
   for our investors.
   """
    )



#Creating boxes for the Coin to plot and the days to plot
row3_1, row3_2 = st.columns((2))

#choose which coin to plot:
with row3_1:
    ticker = st.selectbox(
        'Coin to Plot',
        options = ['Bitcoin', 'Ethereum', 'Solana']
    )
#choose the amount of days displayed
with row3_2:
    days_to_plot = st.slider(
    'Days to Plot',
    min_value = 1,
    max_value = 365,
    value = 120,
    )


#changing the coin into a ticker
if ticker == "Bitcoin":
    ticker_plot = "BTC_USDT"
elif ticker == "Ethereum":
    ticker_plot = "ETH_USDT"
else:
    ticker_plot = "SOL_USDT"

table_ref = dataset_ref.table(ticker_plot)
table = client.get_table(table_ref)

#Manipulating data
data = client.list_rows(table).to_dataframe()
data = data.sort_values(by = "datetime")
head = data.head()

#using the slider variabel to determine how much data the chart highlights
data_chart = data.tail(days_to_plot * 24)

data_chart["return_coin"] = data_chart["close"].pct_change()*100
data_chart["Coin return"] = data_chart["return_coin"].cumsum()
data_chart["port_return"] = 0

#calculating the return on the porftolio
for i in range(data_chart.shape[0]):
    data_chart["port_return"].loc[i] = random.uniform(-0.5, 0.5)

data_chart["Portfolio return"] = data_chart["port_return"].cumsum()

latest_return = round(data_chart["Portfolio return"].iloc[-1],1)
latest_return_amount = round(((1 + (latest_return/100) * 100000)+100000))

st.write("## Overview of invest capital, current capital and the return on capital")

row2_1, row2_2, row2_3 = st.columns((3))

with row2_1:
    display_dial("Invested amount", f"100000", COLOR_BLUE)
with row2_2:
    display_dial("Current amount", f"{latest_return_amount}", COLOR_CYAN)
with row2_3:
    display_dial(f"% return", f"{latest_return}", COLOR_BLUE)



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

c= alt.Chart(data_chart).mark_line().encode(
    x=alt.X('datetime:T', axis=alt.Axis(tickCount= 12 )),
    y=alt.Y(alt.repeat("layer"), type= "quantitative"),
    color=alt.ColorDatum(alt.repeat('layer'))).repeat(layer= ["Coin return", "Portfolio return"])

st.write(f"""**Comparison of the portfolio return against the {ticker} return**""")
st.altair_chart(c, use_container_width= True)

st.write(f"""**Price development of {ticker} over the past {days_to_plot} days**""")
st.plotly_chart(fig, use_container_width=True)
