import joblib
import pickle
import pandas as pd
import streamlit as st
import warnings
from src.config import MODEL_DIR, MODEL_CONFIG

# Tắt warning
warnings.filterwarnings("ignore")

# Import thư viện model để tránh lỗi khi load pickle
try:
    import xgboost
except ImportError:
    pass
try:
    import lightgbm
except ImportError:
    pass
try:
    from statsmodels.tsa.statespace.sarimax import SARIMAXResultsWrapper
except ImportError:
    pass
try:
    from sklearn.ensemble import RandomForestRegressor, AdaBoostRegressor
    from sklearn.tree import DecisionTreeRegressor
    from sklearn.linear_model import LinearRegression, Ridge
except ImportError:
    pass

class ModelHandler:
    def __init__(self):
        self.loaded_models = {} 
        self.load_all_models()

    def _load_single_file(self, file_path):
        """Hàm hỗ trợ load 1 file bất kỳ, thử nhiều cách"""
        # 1. Ưu tiên thử load bằng statsmodels (Dành cho SARIMAX)
        try:
            from statsmodels.tsa.statespace.sarimax import SARIMAXResults
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                return SARIMAXResults.load(file_path)
        except:
            pass

        # 2. Thử load bằng joblib (Chuẩn cho Sklearn/XGBoost)
        try:
            return joblib.load(file_path)
        except:
            pass

        # 3. Thử load bằng pickle (Fallback cuối cùng)
        try:
            with open(file_path, "rb") as f:
                return pickle.load(f)
        except Exception:
            return None

    def load_all_models(self):
        """Vòng lặp load tất cả model trong Config"""
        success_count = 0
        
        for display_name, filename in MODEL_CONFIG.items():
            file_path = MODEL_DIR / filename
            
            if file_path.exists():
                model = self._load_single_file(file_path)
                if model is not None:
                    self.loaded_models[display_name] = model
                    success_count += 1
                else:
                    # Log lỗi ra terminal
                    print(f"❌ Lỗi đọc file: {filename}")
            else:
                print(f"⚠️ Không tìm thấy file: {filename}")

        if success_count == 0:
            st.error("Không load được model nào cả! Vui lòng kiểm tra thư mục model.")

    def get_available_models(self):
        return list(self.loaded_models.keys())

    def _prepare_features(self, model, input_df):
        """Chuẩn bị features đúng định dạng cho từng loại model"""
        model_type = str(type(model))
        
        # --- TRƯỜNG HỢP 1: SARIMAX (Statsmodels) ---
        if "statsmodels" in model_type:
            # SARIMAX yêu cầu biến ngoại sinh (Exog) đúng như lúc train (thường là 21 features)
            cols_to_drop = [
                'Load', 'sales', 'Date', 'date', 'store_name', 'store', 'category', 
                'Day_Clipped', 'Season', 'dow',
                'Year', 'Month', 'Day', 'DayOfYear', 'Timestep' 
            ]
            # Chỉ giữ lại các cột có trong input và KHÔNG nằm trong danh sách loại bỏ
            exog_cols = [c for c in input_df.columns if c not in cols_to_drop]
            return input_df[exog_cols]
            
        # --- TRƯỜNG HỢP 2: Các Model Machine Learning khác ---
        required_features = None
        
        # Kiểm tra attribute lưu tên feature (tùy thư viện)
        if hasattr(model, "feature_name_"): # LightGBM
            required_features = model.feature_name_
        elif hasattr(model, "feature_names_in_"): # Sklearn (RF, DT, Ada, Linear) / XGBoost
            required_features = model.feature_names_in_
        
        # Nếu không tìm thấy tên feature, trả về nguyên input (hy vọng khớp)
        if required_features is None:
            return input_df

        # Tạo bản sao để xử lý
        X_pred = input_df.copy()
        
        # Điền 0 cho các cột thiếu
        for col in required_features:
            if col not in X_pred.columns:
                X_pred[col] = 0
        
        # Trả về đúng thứ tự cột như lúc train
        return X_pred[required_features]

    def predict(self, model_name, input_df):
        """Dự báo đơn lẻ"""
        if model_name not in self.loaded_models:
            return 0.0
        
        model = self.loaded_models[model_name]
        X_pred = self._prepare_features(model, input_df)
        
        try:
            # Xử lý SARIMAX
            if "statsmodels" in str(type(model)):
                forecast = model.get_forecast(steps=1, exog=X_pred)
                return forecast.predicted_mean.iloc[0]
            
            # Các model khác
            return model.predict(X_pred)[0]
            
        except Exception as e:
            st.error(f"Lỗi dự báo {model_name}: {e}")
            return 0.0
        
    def predict_batch(self, model_name, input_df):
        """Dự báo batch (cho Evaluation)"""
        if model_name not in self.loaded_models:
            return None
        
        model = self.loaded_models[model_name]
        X_pred = self._prepare_features(model, input_df)
        
        try:
            # Xử lý SARIMAX
            if "statsmodels" in str(type(model)):
                steps = len(input_df)
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    # Dùng forecast để tránh lỗi index warning
                    forecast = model.forecast(steps=steps, exog=X_pred)
                return forecast.values if hasattr(forecast, 'values') else forecast
            
            # Các model khác
            return model.predict(X_pred)
            
        except Exception as e:
            print(f"Batch predict error ({model_name}): {e}")
            return None