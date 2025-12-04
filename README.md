
# PG&E Energy Analytics Challenge: Electricity Load Forecasting

Dự án này là giải pháp cho bài toán **dự báo phụ tải điện theo giờ (Hourly Electricity Load Forecasting)** thuộc cuộc thi **PG&E Energy Analytics Competition**. Dự án tập trung vào việc phân tích dữ liệu kinh doanh, xử lý đa cộng tuyến và xây dựng các mô hình học máy tiên tiến để dự báo nhu cầu tiêu thụ điện cho năm tiếp theo (Year 3) dựa trên dữ liệu lịch sử 02 năm trước đó.

---

## 1. Mô tả Dữ liệu (Dataset Description)

Bộ dữ liệu ghi nhận theo thời gian thực, thể hiện mối quan hệ giữa **thời gian**, **điều kiện thời tiết** và **mức tiêu thụ điện (Load)** tại khu vực California.

### 1.1. Các cột thời gian
* **Year**: Năm thứ nhất trong bộ dữ liệu huấn luyện.
* **Month**: Tháng trong năm (1 - 12).
* **Day**: Ngày trong tháng.
* **Hour**: Giờ trong ngày (1 - 24).
> *Ý nghĩa:* Giúp mô hình nhận biết chu kỳ tiêu thụ điện theo ngày (sáng/tối) và theo mùa.

### 1.2. Biến mục tiêu (Target)
* **Load**: Mức tiêu thụ điện năng trung bình theo giờ (MW/kW).
* **Quy luật:** Phụ tải thường thấp vào rạng sáng (giờ 1–4) và tăng cao vào ban ngày hoặc giờ cao điểm.

### 1.3. Biến ngoại sinh (Exogenous Variables)
* **Nhiệt độ (Temperature):** 5 cột (`Site-1 Temp` → `Site-5 Temp`) đo nhiệt độ (°C) tại 5 trạm quan trắc.
    * *Tác động:* Nhiệt độ cao làm tăng nhu cầu làm mát (AC), nhiệt độ thấp làm tăng nhu cầu sưởi ấm.
* **Bức xạ mặt trời (GHI):** 5 cột (`Site-1 GHI` → `Site-5 GHI`) đo tổng lượng bức xạ mặt trời.
    * *Đặc điểm:* GHI = 0 vào ban đêm. GHI cao thể hiện ban ngày có nắng, ảnh hưởng đến nguồn cấp điện mặt trời và nhiệt độ môi trường.

---

## 2. Mục tiêu & Phương pháp luận (Goals & Methodology)

### 2.1. Mục tiêu
1. **Phân tích khám phá (EDA):** Xác định tương quan giữa Load, Temp và GHI; trực quan hóa biến thiên theo thời gian.
2. **Xử lý dữ liệu nâng cao:** Giải quyết vấn đề đa cộng tuyến giữa các trạm đo và tạo các đặc trưng kỹ thuật (Feature Engineering).
3. **Mô hình hóa & Dự báo:** Huấn luyện và tối ưu hóa các mô hình (XGBoost, Random Forest, SARIMAX...) để dự báo phụ tải theo nguyên tắc "day-ahead".

### 2.2. Phương pháp tiếp cận (Key Techniques)
* **Xử lý Đa cộng tuyến (Multicollinearity):** Phát hiện hiện tượng tương quan chéo rất mạnh giữa các trạm (VIF > 700). Sử dụng **Partial Least Squares (PLS)** để nén 5 biến trạm thành 1 biến đại diện (Combined_Temp, Combined_GHI).
* **Feature Engineering:**
    * **Time Features:** Mã hóa Sin/Cos cho chu kỳ Giờ, Tuần, Năm.
    * **Lags & Deltas:** Tạo biến trễ (Lag 1h, 24h) và sai phân để nắm bắt xu hướng ngắn hạn.
    * **Behavioral Features:** Tính chỉ số sưởi ấm (HDH) và làm mát (CDH) dựa trên nhiệt độ cơ sở 20°C.
* **Chiến lược Validation:** Sử dụng **Rolling Window Cross-Validation** để tránh rò rỉ dữ liệu (data leakage) thay vì K-Fold ngẫu nhiên.
* **Tối ưu hóa:** Sử dụng **Bayesian Optimization** để tinh chỉnh siêu tham số (Hyperparameter Tuning).

---

## 3. Cấu trúc thư mục

```markdown
PG&E Energy Analytics Challenge/
│
├── datasets/
│   ├── training.xlsx          # Dữ liệu thô ban đầu
│   └── training.csv           # Dữ liệu được chuyển sang định dạng CSV
│
├── figures/                   # Chứa biểu đồ xuất ra từ quá trình phân tích
│   ├── hourly_GHI_variation_*.pdf
│   ├── hourly_temperature_variation_*.pdf
│   └── hourly_electricity_load_*.pdf
│
├── site_correlations.ipynb    # Phân tích tương quan Load, Temp, GHI và kiểm tra Đa cộng tuyến
├── visualization.ipynb        # Trực quan hóa xu hướng và tạo các biến đặc trưng
├── requirements.txt           # Danh sách thư viện cần thiết
└── README.md                  # Tài liệu hướng dẫn
````

-----

## 4\. Hướng dẫn thiết lập & Chạy (Setup & Usage)

### 4.1. Tạo môi trường Conda

Khuyến nghị sử dụng Conda để quản lý môi trường Python 3.10.

```bash
conda create -n is403 python=3.10
conda activate is403
```

### 4.2. Cài đặt thư viện

```bash
pip install -r requirements.txt
```

*Các thư viện chính:* `pandas`, `numpy`, `matplotlib`, `seaborn`, `scikit-learn`, `openpyxl`, `xgboost`, `lightgbm`.

### 4.3. Chạy Notebook phân tích

1.  Clone repository:

    ```bash
    git clone [https://github.com/CryptolWhile/PG-E-Energy-Analytics-Challenge.git](https://github.com/CryptolWhile/PG-E-Energy-Analytics-Challenge.git)
    cd PG-E-Energy-Analytics-Challenge
    ```

2.  Chạy các file phân tích:

      * `site_correlations.ipynb`: Để xem ma trận tương quan, phân tích VIF và áp dụng PLS.
      * `visualization.ipynb`: Để xem biến động phụ tải theo giờ/mùa và kết quả so sánh mô hình.

-----

## 5\. Kết quả Thực nghiệm (Experimental Results)

Dựa trên quá trình huấn luyện và kiểm thử trên dữ liệu năm thứ 3, dưới đây là kết quả so sánh giữa các mô hình:

### 5.1. Hiệu suất mô hình (Accuracy)

  * **XGBoost (Optimized)** là mô hình tốt nhất với sai số thấp nhất:
      * **MAPE:** 4.37%
      * **RMSE:** 126.29 MW
      * *Lý do:* Gradient Boosting xử lý tốt các mối quan hệ phi tuyến tính phức tạp giữa thời tiết và phụ tải.
  * **Random Forest** bám đuổi sát sao với MAPE tương đương (4.37%) và MAE \~93.26 MW.
  * **Linear Regression & SARIMAX** hoạt động kém hiệu quả (MAPE \> 9%) do không bắt được tính chất phi tuyến của dữ liệu.

### 5.2. Độ ổn định & Phân phối (Stability)

  * **Energy Distance (ED):**
      * **Random Forest** đạt chỉ số ED thấp nhất (**0.914**), thấp hơn XGBoost (1.141).
      * *Ý nghĩa:* Random Forest mô phỏng cấu trúc phân phối xác suất và độ biến thiên của dữ liệu thực tế tốt hơn, phù hợp cho các bài toán đánh giá rủi ro.
  * **WAPE:** Các mô hình top đầu (XGBoost, RF, AdaBoost) đều có WAPE ổn định ở mức \~4.33% - 4.36% trên toàn bộ dải công suất.

### 5.3. Kết luận Feature Importance

  * Nhóm đặc trưng **Temperature** (sau khi xử lý PLS và tạo Feature Engineering) đóng vai trò quan trọng nhất trong việc dự đoán phụ tải, ảnh hưởng mạnh hơn nhóm GHI.
  * Các biến thời gian (Giờ, Ngày trong tuần) đóng vai trò then chốt trong việc xác định chu kỳ sinh hoạt.

-----

## 6\. License

The project is licensed under the MIT License.

```
```
