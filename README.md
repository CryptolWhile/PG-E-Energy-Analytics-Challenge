
# PG&E Energy Analytics Challenge
Bảng dữ liệu trên là một phần trong bộ dữ liệu dùng cho bài toán **dự báo phụ tải điện theo giờ** trong cuộc thi **PG&E Energy Analytics Competition**. Dữ liệu được ghi nhận theo thời gian thực, thể hiện mối quan hệ giữa **thời gian**, **điều kiện thời tiết** và **mức tiêu thụ điện (Load)** tại nhiều trạm đo khác nhau trong một khu vực của California.


**1. Các cột thời gian (Year, Month, Day, Hour)**
Bốn cột đầu tiên biểu diễn thời điểm đo dữ liệu:

* **Year**: Năm thứ nhất trong bộ dữ liệu huấn luyện.
* **Month**: Tháng trong năm (1 = Tháng 1).
* **Day**: Ngày trong tháng.
* **Hour**: Giờ trong ngày (từ 1 đến 24).

Những biến này giúp mô hình nhận biết **chu kỳ tiêu thụ điện theo thời gian** — ví dụ, phụ tải điện thường thấp vào ban đêm và cao vào ban ngày, hoặc thay đổi theo mùa.


**2. Load (Phụ tải điện)**
Cột **Load** thể hiện **mức tiêu thụ điện năng trung bình theo giờ** (đơn vị có thể là megawatt hoặc kilowatt tùy theo dữ liệu gốc).
Đây là **biến mục tiêu (target)** mà mô hình cần dự báo.
Ví dụ:

* Giờ 1: Load = 1997
* Giờ 4: Load = 1833
  Ta thấy vào rạng sáng (giờ 1–4), phụ tải thấp dần, phản ánh quy luật sinh hoạt — ít người sử dụng điện hơn trong thời gian này.


**3. Các cột nhiệt độ (Site-1 Temp → Site-5 Temp)**
Các cột này là **nhiệt độ theo °C** tại 5 trạm đo khác nhau (Site 1–5) trong cùng khu vực.
Chúng là **biến ngoại sinh (exogenous variables)**, nghĩa là ảnh hưởng đến phụ tải điện nhưng không bị ảnh hưởng ngược lại bởi nó.
Nhiệt độ thay đổi theo thời điểm trong ngày và giữa các vị trí.
Ví dụ:

* Site-3 thường có nhiệt độ thấp hơn các site khác → có thể nằm ở vùng cao hơn.
* Khi nhiệt độ cao, nhu cầu dùng điện cho làm mát (máy lạnh) có thể tăng, làm tăng Load.



**4. Các cột GHI (Site-1 GHI → Site-5 GHI)**
GHI (Global Horizontal Irradiance) là **tổng lượng bức xạ mặt trời chiếu lên một bề mặt nằm ngang** tại từng trạm.

* Các giá trị GHI = 0 thể hiện **ban đêm hoặc rạng sáng**, khi không có ánh nắng mặt trời.
* Khi GHI > 0 (ban ngày), có ánh sáng mặt trời → có thể ảnh hưởng đến phụ tải điện (vì điện mặt trời được khai thác).

Trong đoạn dữ liệu này, từ giờ 1 đến 8, **GHI = 0** tại tất cả các trạm, cho thấy đây là **khoảng thời gian trước khi mặt trời mọc**. Điều này phù hợp với thực tế khi Load có xu hướng thấp, do hầu hết thiết bị điện chưa được sử dụng nhiều.



**Tóm tắt mối quan hệ trong bảng**
Dữ liệu cho thấy Load phụ thuộc vào ba yếu tố chính:

* **Thời gian:** thể hiện chu kỳ tiêu thụ điện trong ngày và theo mùa.
* **Nhiệt độ:** càng nóng hoặc càng lạnh, nhu cầu sử dụng điện (cho điều hòa, sưởi) càng cao.
* **Bức xạ mặt trời (GHI):** ban ngày có nắng, hệ thống điện mặt trời phát điện nhiều → Load từ lưới giảm.

Như vậy, bảng dữ liệu phản ánh rõ mối quan hệ **giữa điều kiện thời tiết và hành vi tiêu thụ điện năng**, là nền tảng để huấn luyện mô hình dự báo phụ tải điện trong thực tế.


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
│   └── hourly_electricity_load_*.pdf...
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
   git clone https://github.com/CryptolWhile/PG-E-Energy-Analytics-Challenge.git
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

