<<<<<<< HEAD
# 📝 MyNoteApp

Ứng dụng quản lý ghi chú cá nhân được xây dựng với **FastAPI** (backend) và **Streamlit** (frontend), tích hợp **Firebase Authentication** và **Firestore**.

> Bài thực hành số 2 — API & Firebase | Tư Duy Tính Toán — HCMUS

---

##  Cấu trúc dự án

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

| Tính năng | Mô tả |
|---|---|
| Đăng nhập | Email/Password qua Firebase Authentication |
| Đăng xuất | Xóa session, về trang đăng nhập |
| Tạo ghi chú | Nhập tiêu đề, nội dung, tags |
| Xem danh sách | Hiển thị tất cả ghi chú theo thứ tự mới nhất |
| Chỉnh sửa | Cập nhật nội dung ghi chú |
| Xóa | Xóa ghi chú khỏi Firestore |

---

##  API Endpoints

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

## Video Demo

> [Link video demo](https://www.youtube.com/watch?v=JZVAC-nDYYc))

---
# my_note_app
>>>>>>> 7afa1dbcb6f22df2bd3f5b5b7b9bc8133c7654f4
