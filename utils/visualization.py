import os
import sys
import subprocess
import importlib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.stattools import adfuller
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
import calendar

# kiểm tra và cài đặt tự động các thư viện Python cần thiết
def install_packages():
    """Check and install required Python packages if not already installed."""
    required = {'pandas': 'pandas', 'numpy': 'numpy', 'matplotlib': 'matplotlib',
                'statsmodels': 'statsmodels', 'openpyxl': 'openpyxl'}
    for pkg, import_name in required.items():
        try:
            importlib.import_module(import_name)
        except ImportError:
            print(f"Installing {pkg}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])
    print("All required packages are installed.")

#thiết lập cấu hình hiển thị mặc định cho Matplotlib
def setup_mpl_params():
    """Configure Matplotlib for professional, consistent plot appearance."""
    plt.rcParams["font.family"] = "serif"
    plt.rcParams["figure.dpi"] = 100
    plt.rcParams["font.size"] = 20
    plt.rcParams["axes.labelsize"] = 20
    plt.rcParams["axes.titlesize"] = 20
    plt.rcParams["legend.fontsize"] = 20
    plt.rcParams["xtick.direction"] = "in"
    plt.rcParams["ytick.direction"] = "in"
    plt.rcParams["xtick.major.size"] = 5.0
    plt.rcParams["xtick.minor.size"] = 3.0
    plt.rcParams["ytick.major.size"] = 5.0
    plt.rcParams["ytick.minor.size"] = 3.0
    plt.rcParams["axes.linewidth"] = 1.5
    plt.rcParams["legend.handlelength"] = 2.0


#đọc dữ liệu từ file Excel-tạo thư mục lưu kết quả nếu chưa có, và trả về DataFrame
def load_data(excel_file, output_dir):
    """Load dataset from Excel, save as CSV, and create output directory."""
    df = pd.read_excel(excel_file, sheet_name='Data')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    return df

#Vẽ biến thiên theo giờ trong ngày (Hourly variation) của một đại lượng (ví dụ: Temperature, GHI) 
# Mỗi tháng là một đường trên cùng biểu đồ.
def plot_hourly_variation(df, column, year, output_dir):
    """Plot hourly variation (centroids) for each month for a given column and year."""
    plt.figure(figsize=(10, 6))
    for month in range(1, 13):
        filtered_df = df[(df["Year"] == year) & (df["Month"] == month)]
        centroid = filtered_df.groupby("Hour")[column].mean()
        plt.plot(centroid.index, centroid, lw=2.5, marker='D', linestyle='-', 
                 label=calendar.month_name[month])
    plt.xlabel("Hour of the Day")
    plt.ylabel("GHI (Global Horizontal Irradiance)" if "GHI" in column else "Temperature")
    plt.legend(loc="upper left", bbox_to_anchor=(1, 1))
    output_filename = os.path.join(output_dir, f"hourly_{column.replace(' ', '_')}_Year_{year}.pdf")
    plt.savefig(output_filename, format='pdf', bbox_inches='tight') # Lưu biểu đồ dưới dạng file PDF
    plt.close()




# Phân tích chuỗi thời gian Load (tải điện, ví dụ MW):
# Phân rã thành trend + seasonal + residual
# Kiểm tra tính dừng (stationarity) bằng ADF test
# Tạo ACF/PACF plot phục vụ chọn tham số cho SARIMA/SARIMAX
def analyze_load(df, output_dir, seasonal_period=24):
    """Perform seasonal decomposition, stationarity testing, and ACF/PACF plotting for the load."""
    
    #Load=Trend+Seasonal+Residual
    decomp_result = seasonal_decompose(df["Load"], period=seasonal_period)
    
    # Vẽ Trend
    plt.plot(decomp_result.trend, label="Electric Load")
    plt.xlabel("Time")
    plt.ylabel("Load")
    plt.legend()
    plt.savefig(os.path.join(output_dir, f"trend_{seasonal_period}.pdf"), format='pdf', bbox_inches='tight')
    plt.close()

    # Vẽ Seasonal
    plt.plot(decomp_result.seasonal[:100])
    plt.xlabel("Time")
    plt.ylabel("Normalized Seasonal Magnitude")
    plt.savefig(os.path.join(output_dir, f"seasonality_{seasonal_period}.pdf"), format='pdf', bbox_inches='tight')
    plt.close()
    
    # Vẽ Residual
    residual = decomp_result.resid
    plt.figure(figsize=(10, 6))
    plt.plot(residual, label="Residual from Decomposition")
    plt.xlabel("Time")
    plt.ylabel("Load Residual")
    plt.legend()
    plt.savefig(os.path.join(output_dir, "load_decomposition_residual.pdf"), format='pdf', bbox_inches='tight')
    plt.close()
    
    #Thực hiện seasonal differencing để làm chuỗi stationary (tĩnh).
    #Nếu dữ liệu có chu kỳ 24h, phép sai phân này loại bỏ yếu tố lặp theo ngày.
    target_seasonal_diff = df["Load"] - df["Load"].shift(seasonal_period)
    plt.figure(figsize=(10, 6))
    plt.plot(target_seasonal_diff, label="Seasonally Differenced Load")
    plt.xlabel("Time")
    plt.ylabel("Differenced Load")
    plt.legend()
    plt.savefig(os.path.join(output_dir, "load_seasonal_difference.pdf"), format='pdf', bbox_inches='tight')
    plt.close()

    #Kiểm tra tính dừng của chuỗi đã sai phân bằng Augmented Dickey-Fuller (ADF) test
    # Nếu p-value < 0.05, chuỗi được coi là dừng.
    adf_result = adfuller(target_seasonal_diff.dropna())
    print('\nStationarity Test for Seasonally Differenced Load:')
    print(f'ADF Statistic: {adf_result[0]:.4f}')
    print(f'p-value: {adf_result[1]:.4f} (Stationary if p < 0.05)')
    print('Critical Values:')
    for key, value in adf_result[4].items():
        print(f'   {key}: {value:.4f}')

    plot_acf(target_seasonal_diff.dropna(), lags=50)
    plt.savefig(os.path.join(output_dir, "load_acf.pdf"), format='pdf', bbox_inches='tight')
    plt.close()
    plot_pacf(target_seasonal_diff.dropna(), lags=50)
    plt.savefig(os.path.join(output_dir, "load_pacf.pdf"), format='pdf', bbox_inches='tight')
    plt.close()

# Exploratory Data Analysis – EDA
def run_exploratory_analysis():
    install_packages()
    setup_mpl_params()
    excel_file = './datasets/training.xlsx'
    output_dir = './figures'
    train_df = load_data(excel_file, output_dir)

    # tạo 12 đường (12 tháng) cho mỗi năm và mỗi đại lượng (GHI)
    print("### Analyzing Hourly GHI Variation")
    ghi_columns = ["Site-1 GHI", "Site-2 GHI", "Site-3 GHI", "Site-4 GHI", "Site-5 GHI"]
    for column in ghi_columns:
        for year in [1, 2]:
            plot_hourly_variation(train_df, column, year, output_dir)

    # tạo 12 đường (12 tháng) cho mỗi năm và mỗi đại lượng (Temperature)
    print("### Analyzing Hourly Temperature Variation")
    temp_columns = ["Site-1 Temp", "Site-2 Temp", "Site-3 Temp", "Site-4 Temp", "Site-5 Temp"]
    for column in temp_columns:
        for year in [1, 2]:
            plot_hourly_variation(train_df, column, year, output_dir)

    print("### Analyzing Electricity Load")
    analyze_load(train_df, output_dir)

if __name__ == "__main__":
    run_exploratory_analysis()