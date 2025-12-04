import os
from pathlib import Path

# Định nghĩa đường dẫn gốc
ROOT_DIR = Path(__file__).parent.parent

# Thư mục chứa data và model
DATA_PATH = ROOT_DIR / "datasets" / "features_final.csv"
MODEL_DIR = ROOT_DIR / "model"

# --- CẤU HÌNH DANH SÁCH MODEL ---
MODEL_CONFIG = {
    "XGBoost": "final_model_xgboost_robust.pkl",
    "LightGBM": "final_model_lightgbm_robust.pkl",
    "SARIMAX": "final_model_sarimax_robust.pkl",
    "AdaBoost": "final_model_adaboost_robust.pkl",
    "Decision Tree": "final_model_decisiontree_robust.pkl",
    "Linear Regression": "final_model_linear_regression.pkl",
    "Random Forest": "final_model_randomforest_robust.pkl",
}

# Cấu hình trang
PAGE_TITLE = "Electricity Load Forecasting"
PAGE_ICON = "⚡"