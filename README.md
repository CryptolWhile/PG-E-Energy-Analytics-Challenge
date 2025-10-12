### Acknowledgment

This project was developed with reference to public resources from 
[Quang-Nguyen Vo-Huynh](https://github.com/vohuynhquangnguyen).  
Some parts of the code structure and analytical workflow were inspired by his open-source repositories.  
All implementations, interpretations, and analyses in this project were independently reproduced and extended for the PG&E Energy Analytics Challenge.

# PG&E Energy Analytics Challenge

## 1. Mục tiêu dự án
Dự án nhằm phân tích và mô hình hóa mối quan hệ giữa tải điện (Electrical Load) và các yếu tố môi trường bao gồm:
- Nhiệt độ (Temperature) tại 5 trạm quan trắc (Site-1 đến Site-5).
- Bức xạ mặt trời (Global Horizontal Irradiance – GHI) tại 5 trạm tương ứng.

Mục tiêu cụ thể:
1. Xác định mức độ tương quan giữa Load, Temperature và GHI.
2. Trực quan hóa sự biến thiên của các biến theo thời gian, tháng và mùa.
3. Huấn luyện mô hình Random Forest để đánh giá tầm quan trọng của từng đặc trưng (Feature Importance) trong việc dự đoán tải điện.

---

## 2. Cấu trúc thư mục

```markdown

PG&E Energy Analytics Challenge/
│
├── datasets/
│   ├── training.xlsx          # Dữ liệu thô ban đầu
│   └── training.csv           # Dữ liệu được chuyển sang định dạng CSV
│
├── figures/
│   ├── hourly_GHI_variation_*.pdf
│   ├── hourly_temperature_variation_*.pdf
│   └── hourly_electricity_load_*.pdf
│
├── site_correlations.ipynb    # Phân tích tương quan giữa Load, Temp và GHI
├── visualization.ipynb        # Trực quan hóa xu hướng GHI, Temp, Load theo thời gian
├── requirements.txt           # Danh sách thư viện cần thiết
└── README.md                  # Tài liệu hướng dẫn

```

---

## 3. Hướng dẫn thiết lập môi trường

### 3.1. Tạo môi trường Conda
Khuyến nghị sử dụng Conda để quản lý môi trường và thư viện.  
Mở terminal hoặc Anaconda Prompt và chạy các lệnh sau:

```bash
conda create -n is403 python=3.10
conda activate is403
````

### 3.2. Cài đặt các thư viện cần thiết

#### Cách 1: Cài đặt thủ công

```bash
conda install pandas numpy matplotlib seaborn scikit-learn openpyxl
```

#### Cách 2: Sử dụng file requirements.txt

Sau đó cài đặt toàn bộ thư viện bằng lệnh:

```bash
pip install -r requirements.txt
```

---

## 4. Cách chạy Notebook

1. Clone repository:

   ```bash
   git clone https://github.com/<your-username>/PG-E-Energy-Analytics-Challenge.git
   cd PG-E-Energy-Analytics-Challenge
   ```

2. Kích hoạt môi trường conda:

   ```bash
   conda activate is403
   ```

3. Mở và chạy các file:

   * `site_correlations.ipynb`: Phân tích tương quan và trực quan hóa Load, Temp, GHI.
   * `visualization.ipynb`: Biểu đồ biến động theo thời gian và các đặc trưng trung bình.

---

## 5. Nội dung phân tích

### 5.1. Tiền xử lý dữ liệu

* Chuyển đổi giá trị `Load` từ chuỗi chứa dấu phẩy thành số thực (`float`).
* Gom nhóm dữ liệu theo `Year`, `Month`, `Hour` để tính trung bình.
* Loại bỏ các cột không phải số và xử lý giá trị thiếu (`NaN`).

### 5.2. Phân tích tương quan

* Tính hệ số tương quan Pearson giữa `Load` và:

  * `Site-x Temp`
  * `Site-x GHI`
* Vẽ biểu đồ cột thể hiện tương quan từng trạm.
* Chuẩn hóa giá trị tương quan để so sánh mức độ ảnh hưởng tương đối.

### 5.3. Trực quan hóa dữ liệu

* Biểu đồ GHI, Temp và Load theo giờ, tháng và quý.
* Vẽ đường trung bình (Centroid) thể hiện xu hướng tổng thể trong từng giai đoạn.
* Xuất biểu đồ sang định dạng `.pdf` trong thư mục `figures`.

### 5.4. Mô hình học máy (Random Forest)

* Huấn luyện ba mô hình:

  1. Temperature Only
  2. GHI Only
  3. All Features (Temp + GHI)
* Đánh giá Feature Importance của từng biến đầu vào.
* So sánh độ chính xác giữa các nhóm đặc trưng.

---

## 6. Kết quả chính

* Nhiệt độ tại các trạm có tương quan dương nhẹ (~0.4) với Load, cho thấy khi nhiệt độ tăng, phụ tải điện có xu hướng tăng do nhu cầu làm mát.
* GHI có thể có tương quan âm nhẹ, phản ánh khi trời nắng sáng, nhu cầu chiếu sáng giảm.
* Các trạm thể hiện mức tương quan tương đối đồng đều, trong đó Site-5 có xu hướng ảnh hưởng mạnh nhất.
* Kết quả từ mô hình Random Forest xác nhận rằng nhóm đặc trưng Temperature có tầm ảnh hưởng lớn hơn nhóm GHI trong việc dự đoán phụ tải điện.

---

## 7. Hướng phát triển

* Bổ sung các đặc trưng thời gian như `Hour`, `Month`, `DayType`, hoặc chỉ báo thời tiết.
* Thử nghiệm các mô hình khác như XGBoost, Gradient Boosting, hoặc LSTM cho chuỗi thời gian.
* Sử dụng phương pháp TimeSeriesSplit để đánh giá mô hình theo chuỗi thời gian thay vì chia ngẫu nhiên.

---


## 8. License

The project is licensed under the MIT License.

