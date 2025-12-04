import streamlit as st
from src.config import PAGE_TITLE, PAGE_ICON
from src.data_loader import load_data
from src.model_handler import ModelHandler
from src.ui.dashboard import historical_sales_view
from src.ui.prediction import sales_prediction_view
from src.ui.evaluation import model_evaluation_view 

# 1. Config Page
st.set_page_config(page_title=PAGE_TITLE, page_icon=PAGE_ICON, layout="wide")

# 2. Load Resources
data = load_data()
model_handler = ModelHandler()

# 3. Sidebar Navigation
st.sidebar.title("App Navigation")
page = st.sidebar.radio(  # Dùng radio cho đẹp
    "Chức năng:", 
    ["Historical Analysis", "Load Prediction", "Model Evaluation"] # <-- Thêm mục này
)

st.sidebar.markdown("---")

# 4. Router
if page == "Historical Analysis":
    historical_sales_view(data)
elif page == "Load Prediction":
    sales_prediction_view(data, model_handler)
elif page == "Model Evaluation":
    model_evaluation_view(data, model_handler) 