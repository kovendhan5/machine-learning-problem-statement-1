import streamlit as st
import pandas as pd

# Load the dataset
data_path = 'dataset.csv'
df = pd.read_csv(data_path)

# Streamlit app
st.title("AI driven boolean query finder")

# Input for keyword search
keywords = st.text_input("Enter keywords (use 'AND' / 'OR' to refine):").upper()

# Function to filter the dataframe
def filter_dataframe(df, query):
    and_parts = [part.strip() for part in query.split(" AND ")]
    filtered_df = df.copy()

    for part in and_parts:
        or_keywords = [kw.strip() for kw in part.split(" OR ")]
        filtered_df = filtered_df[
            filtered_df.apply(
                lambda row: any(row.astype(str).str.contains(kw, case=False, regex=True).any() for kw in or_keywords), 
                axis=1
            )
        ]

    return filtered_df

# Perform search if keywords are entered
if keywords:
    result_df = filter_dataframe(df, keywords)
    if not result_df.empty:
        st.write("Results:")
        st.write(result_df)
    else:
        st.write("No results found for the given keywords.")
else:
    st.write("Please enter keywords to start the search.")
