import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import numpy as np
import calendar

# --- CẤU HÌNH MATPLOTLIB CHUNG (GIỮ NGUYÊN STYLE CỦA BẠN) ---
plt.rcParams["font.family"] = "serif"
# plt.rcParams["figure.dpi"] = 150 # Giảm DPI để load nhanh hơn trên web
plt.rcParams["font.size"] = 10     # Font nhỏ hơn cho web
plt.rcParams["axes.labelsize"] = 10
plt.rcParams["axes.titlesize"] = 12
plt.rcParams["legend.fontsize"] = 9

def plot_sales_time_series(filtered_data, selected_store=None, selected_store_name=None):
    """Generate time series plot of load"""
    fig, ax = plt.subplots(figsize=(6, 4))
    
    sales_by_date = filtered_data.groupby("date")["sales"].mean() # Mean load makes more sense than sum for hourly
    ax.plot(sales_by_date.index, sales_by_date.values, "b-", label="Daily Avg Load")

    if len(sales_by_date) > 7:
        ma7 = sales_by_date.rolling(window=7).mean()
        ax.plot(sales_by_date.index, ma7, "r--", label="7-Day Moving Avg")
    
    ax.legend()
    ax.set_xlabel("")
    ax.set_ylabel("Load (MW)")
    ax.set_title("Load Trends Over Time")
    fig.autofmt_xdate()
    return fig

def plot_day_of_week_pattern(filtered_data):
    """Generate bar chart showing load by day of week"""
    fig, ax = plt.subplots(figsize=(6, 4))
    day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    
    filtered_data["day_name"] = filtered_data["date"].dt.dayofweek.apply(lambda x: day_names[x])
    day_sales = filtered_data.groupby("day_name")["sales"].mean().reindex(day_names)
    
    avg_daily = day_sales.mean()
    bars = ax.bar(day_sales.index, day_sales.values, color="skyblue")
    ax.axhline(y=avg_daily, color="red", linestyle="--", label="Average")
    
    # --- ĐOẠN SỬA LỖI ---
    if not day_sales.empty:
        # Lấy nhãn (tên thứ) có giá trị lớn nhất/nhỏ nhất
        max_day_label = day_sales.idxmax()
        min_day_label = day_sales.idxmin()
        
        # Chuyển đổi từ tên thứ sang số thứ tự (integer index)
        # Ví dụ: "Wednesday" -> 2
        try:
            max_idx = day_sales.index.get_loc(max_day_label)
            min_idx = day_sales.index.get_loc(min_day_label)
            
            bars[max_idx].set_color("orange") # High load
            bars[min_idx].set_color("green")  # Low load
        except KeyError:
            pass # Bỏ qua nếu có lỗi tìm index (dữ liệu thiếu)
    # ---------------------

    ax.set_ylabel("Avg Load (MW)")
    ax.set_title("Average Load by Day of Week")
    plt.xticks(rotation=45)
    ax.legend()
    return fig

def plot_category_distribution(filtered_data):
    """Pie chart by Season (mapped from category)"""
    fig, ax = plt.subplots(figsize=(6, 6))
    cat_sales = filtered_data.groupby("category")["sales"].mean() # Avg load by season
    
    plt.pie(cat_sales, labels=cat_sales.index, autopct="%1.1f%%", startangle=90)
    plt.title("Average Load Distribution by Season")
    return fig

def plot_store_comparison(filtered_data, store_identifier="store"):
    """Bar chart comparing 'Stores' (Mapped to Years/Regions)"""
    fig, ax = plt.subplots(figsize=(6, 6))
    
    # We group by Year (which we mapped to something else or just create a dummy view)
    # Since we only have one region, let's group by Year if available
    if "Year" in filtered_data.columns:
        group_col = "Year"
    else:
        group_col = "category"

    comp_sales = filtered_data.groupby(group_col)["sales"].mean().sort_values(ascending=False)
    
    y_pos = np.arange(len(comp_sales))
    ax.barh(y_pos, comp_sales.values, align="center")
    ax.set_yticks(y_pos)
    ax.set_yticklabels(comp_sales.index)
    ax.invert_yaxis()
    ax.set_xlabel("Avg Load (MW)")
    ax.set_title(f"Comparison by {group_col}")
    return fig

def plot_sales_distribution(filtered_data):
    """Histogram of Load"""
    fig, ax = plt.subplots(figsize=(10, 4))
    sns.histplot(filtered_data["sales"], bins=30, kde=True, ax=ax)
    
    median_val = filtered_data["sales"].median()
    mean_val = filtered_data["sales"].mean()
    
    ax.axvline(x=median_val, color="r", linestyle="--", label=f"Median: {median_val:.0f}")
    ax.axvline(x=mean_val, color="g", linestyle="--", label=f"Mean: {mean_val:.0f}")
    
    ax.set_xlabel("Load (MW)")
    ax.set_title("Load Distribution")
    ax.legend()
    return fig

def add_week_info(df):
    """Hàm phụ trợ tính WeekOfYear và DayOfWeek"""
    df = df.copy()
    # Logic tính toán giống code của bạn
    if 'DayOfYear' not in df.columns:
        # Simple approximation if DayOfYear missing
        df['DayOfYear'] = df['date'].dt.dayofyear
        
    df['WeekOfYear'] = df['date'].dt.isocalendar().week
    df['DayOfWeek'] = df['date'].dt.dayofweek # 0=Mon, 6=Sun
    return df

def plot_weekly_comparison(df, month, site_col, y_label, title_prefix="GHI"):
    """Vẽ biểu đồ biến thiên theo tuần (Weekly Variation)"""
    # Đảm bảo có thông tin tuần
    df = add_week_info(df)
    
    # Lọc theo tháng
    month_df = df[df['date'].dt.month == month].copy()
    
    if month_df.empty:
        return None

    # Tạo trục x liên tục cho cả tuần (0 - 168 giờ)
    # Giả sử cột 'Hour' có sẵn (0-23)
    if 'Hour' not in month_df.columns:
        month_df['Hour'] = month_df['date'].dt.hour
        
    month_df['HourOfWeek'] = month_df['DayOfWeek'] * 24 + month_df['Hour']
    
    fig, ax = plt.subplots(figsize=(10, 5))
    
    # Vẽ từng tuần (mờ)
    weeks = month_df['WeekOfYear'].unique()
    for week in weeks:
        subset = month_df[month_df['WeekOfYear'] == week]
        ax.plot(subset['HourOfWeek'], subset[site_col], alpha=0.2, color='gray', lw=1)
        
    # Vẽ đường trung bình (đậm)
    centroid = month_df.groupby('HourOfWeek')[site_col].mean()
    ax.plot(centroid.index, centroid, color='blue', lw=2, label='Monthly Average')
    
    # Format trục X (Thứ 2 -> CN)
    tick_locs = [i*24 for i in range(7)]
    tick_labs = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    ax.set_xticks(tick_locs)
    ax.set_xticklabels(tick_labs)
    ax.set_xlim(0, 168)
    
    ax.set_ylabel(y_label)
    ax.set_title(f"Weekly {title_prefix} Variation in {calendar.month_name[month]}")
    ax.legend()
    ax.grid(True, alpha=0.3)
    return fig

def plot_seasonal_comparison(df, season, site_col, y_label):
    """Vẽ biểu đồ so sánh giữa các tháng trong cùng 1 mùa (Seasonal Comparison)"""
    # Map season nếu chưa có
    if 'Season' not in df.columns:
        # Simple mapping
        season_map = {
            12:'Winter', 1:'Winter', 2:'Winter',
            3:'Spring', 4:'Spring', 5:'Spring',
            6:'Summer', 7:'Summer', 8:'Summer',
            9:'Autumn', 10:'Autumn', 11:'Autumn'
        }
        df['Season'] = df['date'].dt.month.map(season_map)
        
    season_df = df[df['Season'] == season].copy()
    if 'Hour' not in season_df.columns:
        season_df['Hour'] = season_df['date'].dt.hour

    if season_df.empty:
        return None

    fig, ax = plt.subplots(figsize=(10, 5))
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c']
    
    months = sorted(season_df['date'].dt.month.unique())
    
    for i, m in enumerate(months):
        subset = season_df[season_df['date'].dt.month == m]
        # Tính trung bình theo giờ
        hourly_avg = subset.groupby('Hour')[site_col].mean()
        
        color = colors[i] if i < len(colors) else None
        ax.plot(hourly_avg.index, hourly_avg, label=calendar.month_name[m], marker='o', ms=4, color=color)
        
    ax.set_xlabel("Hour of Day")
    ax.set_ylabel(y_label)
    ax.set_title(f"Monthly Variation in {season} - {site_col}")
    ax.set_xticks(range(0, 24, 2))
    ax.legend()
    ax.grid(True, alpha=0.3)
    return fig

def plot_correlation_heatmap(df, cols_to_corr):
    """Vẽ Heatmap tương quan"""
    # Lọc các cột tồn tại
    valid_cols = [c for c in cols_to_corr if c in df.columns]
    
    if len(valid_cols) < 2:
        return None
        
    corr_matrix = df[valid_cols].corr()
    
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt='.2f', ax=ax)
    ax.set_title("Correlation Matrix")
    return fig