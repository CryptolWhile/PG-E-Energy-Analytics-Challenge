import pandas as pd
import streamlit as st
from src.config import DATA_PATH

@st.cache_data
def load_data():
    """Load preprocessed electricity data"""
    try:
        # Load the data
        df = pd.read_csv(DATA_PATH)

        # Convert date column to datetime
        if "Date" in df.columns:
            df["Date"] = pd.to_datetime(df["Date"])
            # Mapping columns to match the template's expected logic
            df["date"] = df["Date"]  # Template uses lowercase 'date'
            df["sales"] = df["Load"] # Template uses 'sales', we map Load to it
            
            # Create dummy columns to satisfy the template's layout filters
            # Mapping 'Year' to 'store_name' allows using the Store filter as Year filter
            df["store_name"] = "Region A" 
            df["store"] = 1
            
            # Map Season to category
            if "Month" in df.columns:
                df["category"] = df["Month"].apply(
                    lambda x: "Spring" if x in [3,4,5] else 
                             ("Summer" if x in [6,7,8] else 
                             ("Fall" if x in [9,10,11] else "Winter"))
                )

        return df
    except FileNotFoundError:
        st.error(f"Data file not found. Please ensure '{DATA_PATH}' exists.")
        return pd.DataFrame(columns=["date", "store", "sales"])
    
    