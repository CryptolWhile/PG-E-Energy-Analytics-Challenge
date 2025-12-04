import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

def sales_prediction_view(data, model_handler):
    st.title("Load Prediction Tool")

    # Lấy danh sách model khả dụng
    available_models = model_handler.get_available_models()

    if not available_models:
        st.error("Không có model nào khả dụng. Vui lòng kiểm tra file config và thư mục model.")
        return

    # --- Sidebar ---
    with st.sidebar:
        st.header("Configuration")
        
        # --- [MỚI] Chọn Model ---
        selected_model_name = st.selectbox(
            "Select AI Model", 
            options=available_models,
            index=0
        )
        st.success(f"Running: {selected_model_name}")
        st.markdown("---")

        st.header("Product Selection")
        st.selectbox("Select Region", ["System Wide"])
        st.selectbox("Select Load Type", ["Total Load"])

    # --- Inputs (3 Cột) ---
    st.subheader("Prediction Parameters")
    c1, c2, c3 = st.columns(3)

    with c1:
        pred_date = st.date_input("Prediction Date", datetime.now().date())
        pred_hour = st.slider("Hour", 0, 23, 12)
        is_holiday = st.checkbox("Holiday", False)
        
    with c2:
        temp = st.slider("Temperature (°C)", -10.0, 45.0, 25.0)
        temp_cat = "Hot" if temp > 25 else ("Warm" if temp > 15 else "Cool")
        st.write(f"Category: {temp_cat}")

    with c3:
        ghi = st.slider("Solar GHI (W/m2)", 0, 1200, 500) 
        st.write(f"Radiation Level: {'High' if ghi > 800 else 'Normal'}")
        st.select_slider("Grid Status", ["Stable", "High Demand"], "Stable")

    # --- Predict Button ---
    if st.button("Predict Load"):
        with st.spinner(f"Calculating using {selected_model_name}..."):
            # Feature Engineering
            input_df = pd.DataFrame([{
                'Hour': pred_hour,
                'Temperature': temp,     
                'Combined_Temp': temp,   
                'Humidity': 50,          
                'Combined_GHI': ghi,     
                'Month': pred_date.month,
                'Day': pred_date.day,
                'Year': pred_date.year,
                'DayOfYear': pd.Timestamp(pred_date).dayofyear
            }])
            
            # --- [MỚI] Gọi hàm predict với tên model ---
            pred_val = model_handler.predict(selected_model_name, input_df)
            
            # --- Results Layout ---
            st.header("Prediction Results")
            rc1, rc2 = st.columns(2)
            
            with rc1:
                st.metric("Predicted Load", f"{pred_val:,.2f} MW")
                st.caption(f"Model: {selected_model_name}")
                st.write(f"**Date:** {pred_date}")
                st.write(f"**Hour:** {pred_hour}:00")
            
            with rc2:
                if not data.empty and "Hour" in data.columns:
                    hist_avg = data[data["Hour"] == pred_hour]["sales"].mean()
                    st.metric("Historical Avg (This Hour)", f"{hist_avg:,.2f} MW", 
                              delta=f"{pred_val - hist_avg:,.2f}")
            
            # Chart
            st.subheader("Recent Load History (Context)")
            if not data.empty:
                recent = data.sort_values("date").tail(48)
                fig, ax = plt.subplots(figsize=(6, 2.5))
                ax.plot(recent["date"], recent["sales"], label="History")
                ax.scatter(pd.Timestamp(pred_date) + pd.Timedelta(hours=pred_hour), 
                           pred_val, color='r', label='Prediction')
                ax.legend()
                st.pyplot(fig)