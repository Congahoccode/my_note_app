# 📝 MyNoteApp

Ứng dụng quản lý ghi chú cá nhân được xây dựng với **FastAPI** (backend) và **Streamlit** (frontend), tích hợp **Firebase Authentication** và **Firestore**.

> Bài thực hành số 2 — API & Firebase | Tư Duy Tính Toán — HCMUS

---

## 🏗️ Cấu trúc dự án

```
mynoteapp/
├── backend/
│   ├── main.py              # FastAPI app, routes
│   ├── models.py            # Pydantic schemas
│   ├── firebase_config.py   # Firebase Admin SDK init
│   ├── requirements.txt
│   └── serviceAccountKey.json  ← KHÔNG commit file này
├── frontend/
│   ├── app.py               # Streamlit UI
│   └── requirements.txt
├── .gitignore
└── README.md
```

---

## ⚙️ Cài đặt môi trường

### Yêu cầu
- Python 3.10+
- Tài khoản Firebase với project đã tạo

### 1. Clone repository

```bash
git clone https://github.com/<your-username>/mynoteapp.git
cd mynoteapp
```

### 2. Cài đặt Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Đặt file `serviceAccountKey.json` (tải từ Firebase Console → Project Settings → Service Accounts) vào thư mục `backend/`.

### 3. Cài đặt Frontend

```bash
cd frontend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

---

## 🚀 Chạy ứng dụng

### Chạy Backend

```bash
cd backend
source venv/bin/activate
uvicorn main:app --reload --port 8000
```

Sau đó expose ra internet bằng ngrok:

```bash
ngrok http 8000
```

Copy URL ngrok (dạng `https://xxxx.ngrok-free.app`) và cập nhật vào `frontend/app.py`:

```python
BACKEND_URL = "https://xxxx.ngrok-free.app"
```

API docs có tại: `http://localhost:8000/docs`

### Chạy Frontend

```bash
cd frontend
source venv/bin/activate
streamlit run app.py
```

Truy cập: `http://localhost:8501`

---

## 🔑 Tính năng

| Tính năng | Mô tả |
|---|---|
| Đăng nhập | Email/Password qua Firebase Authentication |
| Đăng xuất | Xóa session, về trang đăng nhập |
| Tạo ghi chú | Nhập tiêu đề, nội dung, tags |
| Xem danh sách | Hiển thị tất cả ghi chú theo thứ tự mới nhất |
| Chỉnh sửa | Cập nhật nội dung ghi chú |
| Xóa | Xóa ghi chú khỏi Firestore |

---

## 🔌 API Endpoints

| Method | Endpoint | Mô tả | Auth |
|---|---|---|---|
| GET | `/` | Root | ❌ |
| GET | `/health` | Health check | ❌ |
| POST | `/auth/login` | Đăng nhập | ❌ |
| GET | `/auth/me` | Thông tin user | ✅ |
| POST | `/notes` | Tạo ghi chú | ✅ |
| GET | `/notes` | Danh sách ghi chú | ✅ |
| GET | `/notes/{id}` | Chi tiết ghi chú | ✅ |
| PUT | `/notes/{id}` | Cập nhật ghi chú | ✅ |
| DELETE | `/notes/{id}` | Xóa ghi chú | ✅ |

---

## 🎥 Video Demo

> [Link video demo](https://your-video-link-here)

---

## ⚠️ Lưu ý bảo mật

- **Không commit** `serviceAccountKey.json` lên GitHub
- **Không commit** file `.env` hoặc bất kỳ file chứa secret nào
- File `.gitignore` đã được cấu hình sẵn để tránh điều này
