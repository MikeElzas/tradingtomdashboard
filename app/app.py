import streamlit as st

import numpy as np
import pandas as pd

#from google.oauth2 import service_account
#from google.cloud import bigquery

#credentials = service_account.Credentials.from_service_account_info(
#    st.secrets["gcp_service_account"]
#)

#client = bigquery.Client(credentials=credentials)


st.markdown("""# This is a header
## This is a sub header
This is text""")

df = pd.DataFrame({
    'first column': list(range(1, 11)),
    'second column': np.arange(10, 101, 10)
})

# this slider allows the user to select a number of lines
# to display in the dataframe
# the selected value is returned by st.slider
line_count = st.slider('Select a line count', 1, 10, 3)

# and used to select the displayed lines
head_df = df.head(line_count)

head_df
