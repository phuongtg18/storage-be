# Storage Manager API

Backend quản lý một kho hàng: FastAPI + SQLite + SQLModel + JWT.

## Chạy local

Yêu cầu Python 3.12+.

```bash
python -m venv .venv
# Linux/macOS:
source .venv/bin/activate
# Windows:
# .venv\Scripts\activate

pip install -r requirements.txt
cp .env.example .env
```

Sửa `.env`:
- `ADMIN_PASSWORD`: đặt mật khẩu admin mạnh.
- `SECRET_KEY`: đặt chuỗi bí mật ngẫu nhiên dài tối thiểu 32 ký tự.
- Khi chạy local, đổi `DATABASE_URL` thành `sqlite:///./data/storage.db`.

Chạy:
```bash
uvicorn app.main:app --reload
```

Mở `http://127.0.0.1:8000/docs`.

## Chạy Docker

```bash
cp .env.example .env
```

Trong `.env`, giữ `DATABASE_URL=sqlite:////app/data/storage.db`, thay `ADMIN_PASSWORD` và `SECRET_KEY`, sau đó:

```bash
docker compose up -d --build
docker compose logs -f
```

SQLite được lưu ở thư mục `./data` trên host. Không xóa thư mục này khi cập nhật container.

## Đăng nhập

`POST /api/v1/auth/login`

```json
{
  "username": "admin",
  "password": "your-admin-password"
}
```

Dùng `access_token` trả về trong header:
`Authorization: Bearer <access_token>`

## Ví dụ thao tác

Tạo danh mục:
```http
POST /api/v1/categories
```
```json
{"name":"Electronics","description":"Electronic supplies"}
```

Tạo mặt hàng:
```http
POST /api/v1/items
```
```json
{
  "name":"USB Cable",
  "category_id":1,
  "unit":"pcs",
  "quantity":20,
  "alert_threshold":5,
  "notes":"Type-C"
}
```

Nhập kho:
```http
POST /api/v1/stock/in
```
```json
{"item_id":1,"quantity":10,"note":"Initial restock"}
```

Xuất kho:
```http
POST /api/v1/stock/out
```
```json
{"item_id":1,"quantity":2,"note":"Used"}
```

Dashboard: `GET /api/v1/dashboard`

## Trạng thái tồn kho

- `CRITICAL_OUT`: quantity <= 0
- `RUNNING_LOW`: 0 < quantity <= alert_threshold
- `IN_STOCK`: quantity > alert_threshold

## Lưu ý vận hành

- API quản lý yêu cầu JWT; `/`, `/health`, `/docs` và `/api/v1/auth/login` không yêu cầu JWT.
- Admin được tạo lần đầu khi khởi động từ biến môi trường. Nếu admin đã tồn tại, thay đổi `ADMIN_PASSWORD` trong `.env` không tự đổi mật khẩu trong database.
- Lịch sử giao dịch không có API sửa/xóa. Mặt hàng đã có lịch sử không được xóa.
- Đây là bản khởi đầu gọn. Trước khi mở internet công khai, hãy giới hạn `CORS_ORIGINS` về domain FE, dùng HTTPS/reverse proxy và sao lưu định kỳ thư mục `data`.
- Với môi trường cần nhiều tiến trình ghi đồng thời hoặc nhiều bản backend, nên chuyển SQLite sang PostgreSQL.
