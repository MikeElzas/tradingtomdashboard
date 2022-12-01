import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from htbuilder import div, big, h2, styles
from htbuilder.units import rem
import altair as alt

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
st.set_page_config(layout="wide", page_title="Trading Tom invester dashboard", page_icon=":rocket:")

row1_1, row1_2 = st.columns((2, 2))

with row1_1:
    st.title("Trading Tom invester dashboard")

with row1_2:
    st.write(
        """
    ##
   This dashboard highlights the investment amount, return development over time, total return and performance against a benchmark
   for our investors.
   """
    )

# choose which ticker is displayed
ticker = st.sidebar.selectbox(
    'Coin to Plot',
    options = ['Bitcoin', 'Ethereum', 'Solana']
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

data_chart["return_coin"] = data_chart["close"].pct_change()*100
data_chart["return_coin_cum"] = data_chart["return_coin"].cumsum()
data_chart["return_port"] = -2



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

st.write("## Overview of invest capital, current capital and the return on capital")

row2_1, row2_2, row2_3 = st.columns((3))

with row2_1:
    display_dial("Invested amount", f"100K", COLOR_BLUE)
with row2_2:
    display_dial("Current amount", f"120K", COLOR_CYAN)
with row2_3:
    display_dial(f"% return", f"20%", COLOR_BLUE)


#c = alt.Chart(data_chart).mark_circle().encode(
 #   x='datetime', y='return_coin_cum', tooltip=['return_coin_cum']).interactive()

#c= alt.Chart(data_chart).mark_line().encode(
#    x=alt.X('datetime:T', axis=alt.Axis(tickCount= 12 )),
#    y=alt.Y('return_coin_cum:Q'))

c= alt.Chart(data_chart).mark_line().encode(
    x=alt.X('datetime:T', axis=alt.Axis(tickCount= 12 )),
    y=alt.Y(alt.repeat("layer"), type= "quantitative"),
    color=alt.ColorDatum(alt.repeat('layer'))).repeat(layer= ["return_coin_cum", "return_port"])

st.write(f"""**Comparison of the portfolio return against the {ticker} return**""")
st.altair_chart(c, use_container_width= True)

st.write(f"""**Price development of {ticker} over the past {days_to_plot} days**""")
st.plotly_chart(fig, use_container_width=True)
