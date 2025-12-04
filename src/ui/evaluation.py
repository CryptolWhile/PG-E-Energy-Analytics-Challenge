import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sklearn.metrics import mean_squared_error, mean_absolute_error
import os

# --- Import dcor ---
try:
    import dcor
    HAS_DCOR = True
except ImportError:
    HAS_DCOR = False

# --- CÁC HÀM TÍNH TOÁN ---
def weighted_absolute_percentage_error(y_true, y_pred):
    y_true, y_pred = np.array(y_true), np.array(y_pred)
    if np.sum(y_true) == 0: return np.nan
    return np.sum(np.abs(y_true - y_pred)) / np.sum(y_true) * 100

def mean_absolute_percentage_error(y_true, y_pred):
    y_true, y_pred = np.array(y_true), np.array(y_pred)
    mask = y_true != 0
    if np.any(mask):
        return np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100
    return np.nan

def calculate_metrics(y_true, y_pred):
    y_true = np.array(y_true)
    y_pred = np.array(y_pred)
    
    mse = mean_squared_error(y_true, y_pred)
    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mse)
    wape = weighted_absolute_percentage_error(y_true, y_pred)
    mape = mean_absolute_percentage_error(y_true, y_pred)
    
    energy_dist = 0.0
    if HAS_DCOR:
        try:
            if len(y_true) < 10000: # Chỉ tính nếu data không quá lớn để tránh treo máy
                energy_dist = dcor.energy_distance(y_pred, y_true)
        except:
            energy_dist = np.nan
            
    return {
        "MSE": mse,
        "MAE": mae,
        "RMSE": rmse,
        "WAPE (%)": wape,
        "MAPE (%)": mape,
        "Energy Dist": energy_dist
    }

def load_ground_truth():
    """Load file results.xlsx"""
    file_path = "results.xlsx"
    if os.path.exists(file_path):
        try:
            df = pd.read_excel(file_path, header=None, names=['Actual_Load'])
            return df
        except Exception as e:
            st.error(f"Lỗi đọc file results.xlsx: {e}")
            return None
    return None

def model_evaluation_view(data, model_handler):
    st.title("⚖️ Đánh giá Model (Dựa trên results.xlsx)")

    # 1. Chọn Dữ liệu Features (X) - Lọc lấy Year 3
    st.sidebar.header("Cấu hình")
    
    # Tự động lọc lấy Year 3 (năm cuối cùng trong data)
    max_year = data['Year'].max()
    X_test_final = data[data['Year'] == max_year].copy()
    
    if X_test_final.empty:
        st.error(f"Không tìm thấy dữ liệu cho Năm {max_year}.")
        return

    # 2. Load Ground Truth (y)
    actual_df = load_ground_truth()
    
    if actual_df is None:
        st.warning("⚠️ Không tìm thấy file `results.xlsx` tại thư mục gốc.")
        uploaded_file = st.file_uploader("Vui lòng tải lên file kết quả thực tế (Excel)", type=['xlsx'])
        if uploaded_file:
            actual_df = pd.read_excel(uploaded_file, header=None, names=['Actual_Load'])
        else:
            return

    # 3. Đồng bộ dữ liệu (Xử lý chênh lệch 8760 vs 8784)
    st.divider()
    st.subheader("📊 Trạng thái Dữ liệu")
    
    len_actual = len(actual_df)
    len_features = len(X_test_final)
    min_len = min(len_actual, len_features)
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Thực tế (Excel)", f"{len_actual:,} dòng")
    c2.metric("Features (Year 3)", f"{len_features:,} dòng")
    c3.metric("Dữ liệu dùng để test", f"{min_len:,} dòng")

    if len_actual != len_features:
        if len_features > len_actual:
            diff = len_features - len_actual
            st.info(f"ℹ️ Giải thích: Features ({len_features}) nhiều hơn Thực tế ({len_actual}) là **{diff} dòng** (đúng bằng 1 ngày 24h). Có thể Year 3 là năm nhuận nhưng file kết quả chỉ có 365 ngày. Hệ thống sẽ tự động cắt bỏ phần dư.")
        else:
            st.warning(f"⚠️ Dữ liệu không khớp. Hệ thống sẽ cắt về {min_len} dòng.")

    # --- CẮT DỮ LIỆU ---
    y_true = actual_df['Actual_Load'].values[:min_len]
    
    # Cắt Features và Reset Index để đảm bảo khớp dòng
    X_test_eval = X_test_final.iloc[:min_len].reset_index(drop=True)
    eval_dates = X_test_eval['date']

    # 4. Chạy Đánh giá
    available_models = model_handler.get_available_models()
    if not available_models:
        st.error("Chưa load được model nào.")
        return

    if st.button("🚀 Chạy Đánh Giá Ngay"):
        results = []
        chart_df = pd.DataFrame({'Date': eval_dates, 'Actual Load': y_true})
        
        progress_bar = st.progress(0)
        
        for i, model_name in enumerate(available_models):
            with st.spinner(f"Đang chạy {model_name}..."):
                # Dự báo
                y_pred = model_handler.predict_batch(model_name, X_test_eval)
                
                if y_pred is not None:
                    # Đảm bảo y_pred cùng độ dài
                    y_pred = y_pred[:min_len]
                    
                    # Lưu vào chart data
                    chart_df[model_name] = y_pred
                    
                    # Tính toán metric
                    metrics = calculate_metrics(y_true, y_pred)
                    
                    # Format kết quả
                    res_row = {"Model": model_name}
                    res_row.update(metrics)
                    results.append(res_row)
            
            progress_bar.progress((i + 1) / len(available_models))
        
        progress_bar.empty()

        # --- HIỂN THỊ KẾT QUẢ ---
        if results:
            st.divider()
            st.subheader("🏆 Bảng Kết Quả Chi Tiết")
            
            metrics_df = pd.DataFrame(results).set_index("Model")
            
            st.dataframe(
                metrics_df.style.format({
                    "MSE": "{:.3f}",
                    "MAE": "{:.3f}",
                    "RMSE": "{:.3f}",
                    "WAPE (%)": "{:.2f}%",
                    "MAPE (%)": "{:.2f}%",
                    "Energy Dist": "{:.3f}"
                }).highlight_min(axis=0, color='#d1e7dd'),
                use_container_width=True
            )

            # --- Biểu đồ ---
            st.divider()
            st.subheader("📈 Biểu đồ: Thực tế vs Dự báo")
            
            # Zoom vào 1 tuần đầu tiên để nhìn rõ hơn (nếu data quá dày)
            st.caption("Mẹo: Bạn có thể zoom vào biểu đồ để xem chi tiết từng giờ.")
            
            melted_df = chart_df.melt(id_vars=['Date'], var_name='Source', value_name='Load')
            
            fig = px.line(melted_df, x='Date', y='Load', color='Source',
                          color_discrete_map={'Actual Load': 'black'}, 
                          title=f"So sánh trên {min_len} giờ")
            
            fig.update_traces(line=dict(width=1.5))
            fig.update_traces(patch={"line": {"width": 2.5}}, selector={"legendgroup": "Actual Load"})
            
            st.plotly_chart(fig, use_container_width=True)
            
        else:
            st.error("Có lỗi xảy ra khi dự báo.")