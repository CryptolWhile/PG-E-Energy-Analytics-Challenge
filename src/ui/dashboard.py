import streamlit as st
import pandas as pd
import numpy as np
import calendar
from src.utils.plots import (
    plot_sales_time_series, plot_day_of_week_pattern,
    plot_sales_distribution, plot_weekly_comparison,
    plot_seasonal_comparison, plot_correlation_heatmap,
    plot_category_distribution, plot_store_comparison
)

def historical_sales_view(data):
    st.title("Electricity Load Dashboard") 

    if data.empty:
        st.warning("No data available.")
        return

    # --- Filters ---
    # Sidebar filters vẫn áp dụng cho toàn bộ dữ liệu
    filtered_data = configure_filters(data)
    if filtered_data.empty:
        st.warning("No data for selected filters.")
        return

    # --- TABS LAYOUT ---
    # Chia giao diện thành 3 Tabs
    tab1, tab2, tab3 = st.tabs(["📈 Overview Trends", "📅 Weekly & Seasonal Analysis", "🔗 Correlations & Stats"])

    # === TAB 1: TỔNG QUAN (Giữ lại code cũ của bạn) ===
    with tab1:
        # --- KPIs ---
        display_kpis(filtered_data)

        # --- Trends ---
        display_sales_trends(filtered_data)

        # --- Breakdown ---
        display_performance_breakdown(filtered_data)

        # --- Distribution ---
        st.header("Load Distribution")
        fig = plot_sales_distribution(filtered_data)
        st.pyplot(fig)

        # --- Table ---
        with st.expander("View Detailed Load Data"):
            st.dataframe(filtered_data.sort_values("date", ascending=False), use_container_width=True)

    # === TAB 2: PHÂN TÍCH SÂU (Code mới thêm vào) ===
    with tab2:
        st.header("Deep Dive Analysis")
        
        # 1. Weekly Variation Analysis
        st.subheader("1. Weekly Variation (Hour of Week)")
        
        c1, c2, c3 = st.columns(3)
        with c1:
            # Chọn tháng (Mặc định là Tháng 4 - Mid Spring)
            month_name = st.selectbox("Select Month", list(calendar.month_name)[1:], index=3) 
            month_idx = list(calendar.month_name).index(month_name)
        with c2:
            # Chọn loại biến số
            # Tự động tìm cột GHI/Temp trong data gốc (không bị filter) để lấy tên cột
            ghi_cols = [c for c in data.columns if 'GHI' in c] or ['Combined_GHI']
            temp_cols = [c for c in data.columns if 'Temp' in c] or ['Combined_Temp']
            
            variable_type = st.radio("Variable Type", ["Load", "GHI", "Temperature"], horizontal=True)
        
        with c3:
            # Chọn site cụ thể dựa trên loại biến
            target_col = "sales" # Mặc định là Load (đã map sang 'sales' ở data_loader)
            y_label = "Load (MW)"
            
            if variable_type == "GHI":
                target_col = st.selectbox("Select GHI Site", ghi_cols)
                y_label = "GHI (W/m²)"
            elif variable_type == "Temperature":
                target_col = st.selectbox("Select Temp Site", temp_cols)
                y_label = "Temperature (°C)"
        
        # Vẽ biểu đồ Weekly (Sử dụng filtered_data hoặc data gốc tùy mục đích, ở đây dùng data gốc để xem xu hướng tổng thể)
        # Lưu ý: Hàm plot_weekly_comparison cần được định nghĩa trong src/utils/plots.py
        fig_weekly = plot_weekly_comparison(data, month_idx, target_col, y_label, title_prefix=variable_type)
        if fig_weekly:
            st.pyplot(fig_weekly)
        else:
            st.info(f"Not enough data for {month_name}.")

        st.markdown("---")

        # 2. Seasonal Analysis
        st.subheader("2. Seasonal Variation (Monthly Comparison)")
        
        sc1, sc2 = st.columns(2)
        with sc1:
            season_sel = st.selectbox("Select Season", ["Spring", "Summer", "Autumn", "Winter"])
        
        # Vẽ biểu đồ Seasonal
        fig_seasonal = plot_seasonal_comparison(data, season_sel, target_col, y_label)
        if fig_seasonal:
            st.pyplot(fig_seasonal)
        else:
            st.info(f"No data found for {season_sel}.")

    # === TAB 3: THỐNG KÊ & VIF (Code mới thêm vào) ===
    with tab3:
        st.header("Statistical Analysis")
        
        # 1. Descriptive Statistics Table
        st.subheader("Descriptive Statistics by Year")
        if 'Year' in data.columns:
            # Lấy các cột quan trọng để thống kê
            stat_cols = ['sales'] + [c for c in data.columns if 'Temp' in c or 'GHI' in c]
            stat_cols = [c for c in stat_cols if c in data.columns] # Chỉ lấy cột có thật
            
            if stat_cols:
                stats_df = data.groupby('Year')[stat_cols].describe().T
                st.dataframe(stats_df, height=400, use_container_width=True)
        
        # 2. Correlation Matrix 
        st.subheader("Correlation Heatmap")
        
        # Cho user chọn cột muốn xem tương quan
        all_numeric = data.select_dtypes(include=np.number).columns.tolist()
        # Gợi ý sẵn một số cột quan trọng
        default_cols = ['sales', 'Combined_Temp', 'Combined_GHI'] 
        default_cols = [c for c in default_cols if c in all_numeric]
        
        cols_to_corr = st.multiselect("Select variables for Correlation", all_numeric, default=default_cols)
        
        if cols_to_corr:
            fig_corr = plot_correlation_heatmap(data, cols_to_corr)
            if fig_corr:
                st.pyplot(fig_corr)
            
        # 3. VIF Analysis
        st.subheader("Variance Inflation Factor (VIF)")
        st.info("Checks for multicollinearity among predictors.")
        
        if st.button("Calculate VIF"):
            from statsmodels.stats.outliers_influence import variance_inflation_factor
            
            # Clean data for VIF
            vif_data_clean = data[cols_to_corr].dropna()
            vif_data_clean = vif_data_clean.select_dtypes(include=[np.number])
            
            if not vif_data_clean.empty and len(vif_data_clean.columns) > 1:
                vif_df = pd.DataFrame()
                vif_df["Variable"] = vif_data_clean.columns
                vif_df["VIF"] = [variance_inflation_factor(vif_data_clean.values, i) 
                                 for i in range(len(vif_data_clean.columns))]
                
                # Highlight high VIF values
                st.dataframe(vif_df.style.background_gradient(cmap='Reds', subset=['VIF']).format({'VIF': '{:.2f}'}))
            else:
                st.error("Need at least 2 numeric variables to calculate VIF.")

def configure_filters(data):
    with st.sidebar:
        st.header("Dashboard Filters")
        
        # Date Range
        st.subheader("Date Range")
        min_date = data["date"].min().date()
        max_date = data["date"].max().date()
        start_date = st.date_input("From", min_date, min_value=min_date, max_value=max_date)
        end_date = st.date_input("To", max_date, min_value=min_date, max_value=max_date)

        # Region/Store Filter
        st.subheader("Region Selection")
        store_names = ["System Wide"]
        selected_store = st.selectbox("Select Region", options=["All Regions"] + store_names)
        
        # Category Filter
        st.subheader("Seasons")
        if "category" in data.columns:
            cats = sorted(data["category"].unique())
            selected_cats = st.multiselect("Select Seasons", cats, default=cats)
        else:
            selected_cats = None

    # Apply filters
    mask = (data["date"].dt.date >= start_date) & (data["date"].dt.date <= end_date)
    filtered_data = data.loc[mask].copy()
    
    if selected_cats and "category" in filtered_data.columns:
        filtered_data = filtered_data[filtered_data["category"].isin(selected_cats)]
    
    st.session_state.selected_store = selected_store
    return filtered_data

def display_kpis(df):
    st.header("Key Performance Indicators")
    
    total_load = df["sales"].sum()
    avg_load = df["sales"].mean()
    peak_load = df["sales"].max()
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Load (MWh)", f"{total_load:,.0f}")
    col2.metric("Avg Load (MW)", f"{avg_load:,.2f}")
    col3.metric("Peak Load (MW)", f"{peak_load:,.2f}")
    col4.metric("Data Points", f"{len(df):,}")

def display_sales_trends(df):
    st.header("Load Trends")
    col1, col2 = st.columns(2)
    with col1:
        fig = plot_sales_time_series(df)
        st.pyplot(fig)
    with col2:
        fig = plot_day_of_week_pattern(df)
        st.pyplot(fig)

def display_performance_breakdown(df):
    st.header("Performance Breakdown")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Seasonal Performance")
        fig = plot_category_distribution(df)
        st.pyplot(fig)
    with col2:
        st.subheader("Yearly Comparison")
        fig = plot_store_comparison(df)
        st.pyplot(fig)