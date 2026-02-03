# GreenSort - Hệ Thống Phân Loại Rác Thải AI

**GreenSort** là hệ thống phân loại rác thải thông minh sử dụng AI, được tối ưu hóa cho bối cảnh Việt Nam. Hệ thống kết hợp nhiều công nghệ deep learning tiên tiến để phân loại 9 loại rác thải khác nhau với độ chính xác cao.

## Tính Năng Nổi Bật

### Công Nghệ AI Tiên Tiến
- **YOLOv8s Object Detection**: Phát hiện đa vật thể thời gian thực (mAP@50 đạt **88.25%**)
- **Real-time Precision Safeguards**: Hệ thống logic bảo vệ (Anti-flicker, Voting, Hysteresis) giúp khung bao và nhãn cực kỳ ổn định, không bị nhấp nháy.
- **EfficientNet Classification**: Mô hình phân loại chuẩn xác cao (94.8% accuracy) dùng làm baseline so sánh.
- **Scene Diversity Training**: Sử dụng MixUp, Mosaic và Copy-Paste để mô phỏng rác trong môi trường phức tạp (nền nhiễu, vật thể che khuất).
- **Object Tracking**: Theo dõi vật thể qua từng frame ảnh để đảm bảo tính nhất quán.

### Tối Ưu Cho Việt Nam
- **9 Loại Rác Thải**: Pin, hữu cơ, hộp giấy, thủy tinh, kim loại, giấy, nhựa, vải, rác thải.
- **Thông Minh Mapping**: Tự động ánh xạ 9 loại rác vào **3 nhóm thùng rác chuẩn** (Tái chế, Vô cơ, Nguy hại).
- **Hướng Dẫn Tái Chế**: Cung cấp hàng chục mẹo và hướng dẫn xử lý rác bằng tiếng Việt.
- **Giao Diện Tiếng Việt**: Thân thiện với người dùng trong nước.

### Hệ Thống Backend & API (FastAPI)
- **WebSocket Loop**: Xử lý luồng video camera trực tiếp với độ trễ thấp (~10 FPS).
- **Asynchronous Processing**: Xử lý nhiều yêu cầu đồng thời nhờ kiến trúc bất đồng bộ của FastAPI.
- **Database Integration**: Tự động lưu trữ thống kê phân loại và phản hồi người dùng vào cơ sở dữ liệu.
- **REST API Comprehensive**: Cung cấp đầy đủ tài liệu OpenAPI (Swagger) cho việc tích hợp frontend.

---

## Loại Rác Được Hỗ Trợ & Ánh Xạ Thùng Rác

| Tiếng Anh | Tiếng Việt | Nhóm Thùng Rác | Mô Tả |
|-----------|------------|----------------|-------|
| Battery | Pin | **Nguy hại** | Pin điện tử, pin tiểu, acquy |
| Biological | Hữu cơ | **Vô cơ/Hữu cơ** | Thực phẩm thừa, rau củ quả, xương |
| Cardboard | Hộp giấy | **Tái chế** | Thùng carton, bao bì giấy cứng |
| Glass | Thủy tinh | **Tái chế** | Chai lọ, cốc thủy tinh |
| Metal | Kim loại | **Tái chế** | Lon nhôm, đồ sắt thép |
| Paper | Giấy | **Tái chế** | Giấy văn phòng, báo cũ, sách vở |
| Plastic | Nhựa | **Tái chế** | Chai nhựa, túi nilon, đồ nhựa |
| Textile | Vải | **Vô cơ** | Quần áo cũ, vải vụn |
| Trash | Rác thải | **Vô cơ** | Rác không tái chế được |

---

## Cấu Trúc Dự Án

```
waste-classification-vn/
│
├── backend/                    # FastAPI Backend Service
│   ├── app/
│   │   ├── api/v1/            # API Endpoints (Real-time, Classify, Stats)
│   │   ├── core/              # Config, Model Loader, Database
│   │   ├── services/          # Inference & Preprocessing Logic
│   │   ├── utils/             # Bin Mapping & Recycling Tips
│   │   └── main.py            # FastAPI Application Entry
│   ├── requirements.txt       # Backend dependencies
│   └── .env                   # Cấu hình môi trường (API port, Model path)
│
├── models/                   # Trọng số mô hình đã huấn luyện
│   ├── yolov8s_best.pt      # YOLOv8 (Sản xuất)
│   └── efficientnet_b0_best_optimized.pth # EfficientNet (Baseline)
│
├── notebooks/                # Jupyter Notebooks (EDA & Training logs)
├── src/                       # Mã nguồn huấn luyện EfficientNet
├── yolo-scripts/             # Công cụ xử lý Dataset YOLO
├── data/                     # Dữ liệu ảnh và Cơ sở dữ liệu SQLite
├── outputs/                  # Kết quả huấn luyện (Logs & Charts)
├── requirements.txt         # Dependencies tổng cho toàn hệ thống
└── README.md               # Tài liệu hướng dẫn chính
```

---

## Hướng Dẫn Cài Đặt & Khởi Chạy

### 1. Cài Đặt Môi Trường

Yêu cầu: **Python 3.9+**.

```bash
# Clone repository
git clone https://github.com/caoduong126s/waste-classification-vn.git
cd waste-classification-vn

# Tạo và kích hoạt môi trường ảo
python -m venv venv
source venv/bin/activate  # Trên Windows dùng: venv\Scripts\activate

# Cài đặt tất cả thư viện cần thiết
pip install -r requirements.txt
```

### 2. Cấu Hình Hệ Thống

Tạo file `.env` bên trong thư mục `backend/`:

```env
MODEL_PATH=../models/yolov8s_best.pt
MODEL_TYPE=yolo
DEVICE=cpu  # Hoặc 'cuda' nếu có GPU NVIDIA, 'mps' nếu dùng Mac M1/M2
API_PORT=8000
CONF_THRESHOLD=0.25
IOU_THRESHOLD=0.45
```

### 3. Tải Model Weights (Quan Trọng) ⚠️
Do file model (`.pt`) quá lớn để lưu trên GitHub, bạn cần tải thủ công hoặc dùng script:

**Cách 1: Dùng script (Nếu tác giả đã cập nhật link)**
```bash
python scripts/download_models.py
```

**Cách 2: Tải thủ công**
1. Liên hệ tác giả để lấy file `yolov8s_best.pt` (hoặc train lại từ đầu).
2. Copy file vào thư mục `models/`:
   ```bash
   waste-classification-vn/models/yolov8s_best.pt
   ```


### 3. Chạy Backend Server

```bash
cd backend
# Chạy ở chế độ phát triển
uvicorn app.main:app --reload

# Hoặc chạy trực tiếp với module
python -m app.main
```

Hệ thống sẽ khả dụng tại:
- **API Server**: `http://localhost:8000`
- **Tài liệu API (Swagger)**: `http://localhost:8000/docs`

---

## API Endpoints Chính

### Health Check
`GET /api/v1/health`
- Kiểm tra trạng thái server và trạng thái tải mô hình AI.

### Phân Loại Hình Ảnh (REST)
`POST /api/v1/classify`
- Gửi một file ảnh lên để nhận kết quả phân loại, ánh xạ thùng rác và mẹo tái chế.

### Nhận Diện Thời Gian Thực (WebSocket)
`WS /api/v1/ws/realtime-detect`
- Truyền nhận Base64 hình ảnh liên tục để phát hiện vật thể với độ ổn định cao.

### Thống Kê & Phản Hồi
`GET /api/v1/statistics` - Xem biểu đồ phân bố rác.
`POST /api/v1/feedback` - Gửi phản hồi khi AI nhận diện sai.

---

## Kết Quả Huấn Luyện

| Mô hình | Chỉ số chính | Trạng thái |
|---------|--------------|------------|
| **YOLOv8s** | **88.25% mAP@50** | Sẵn sàng sản xuất |
| **EfficientNetB0** | **94.8% Accuracy** | Baseline so sánh |

---

## Tác Giả

**Dự án GreenSort**
- Người thực hiện: **Lê Huỳnh Cao Dương**
- Email: [caoduong22102004@gmail.com](mailto:caoduong22102004gmail.com)

---
**Cùng chung tay bảo vệ môi trường với AI!**



