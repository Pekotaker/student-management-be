Dưới đây là một tài liệu hướng dẫn **rất chi tiết** (bằng tiếng Việt) giúp cài đặt và chạy dự án. Mục tiêu là đảm bảo bạn (khách hàng) chỉ cần làm theo từng bước **một cách đơn giản** mà **không cần** am hiểu sâu về Git, Python, Node, hay PostgreSQL. Mình sẽ mô tả mọi thứ từ cách **mở dự án**, **chạy backend**, **chạy frontend**, đến **kiểm tra kết quả**.

> **Lưu ý**: Mình đã cài đặt sẵn Git, Python, Node, và PostgreSQL trên máy tính của bạn. Tức là bạn **không** cần cài đặt các phần mềm này nữa.

---

## 1. Giải Thích Tổng Quan Về Dự Án

- **Backend**: Dùng **Python (FastAPI)** để làm máy chủ xử lý dữ liệu.
- **Frontend**: Dùng **React + Material UI** để xây dựng giao diện web.
- **Database**: Sử dụng **PostgreSQL** để lưu trữ dữ liệu.
- **Công cụ**:
  - **Git** để quản lý mã nguồn (dạng “chụp ảnh” dự án theo thời gian).
  - **Alembic** để quản lý “phiên bản” (migrations) của cơ sở dữ liệu.

Bạn chỉ cần làm đúng theo hướng dẫn dưới đây để **chạy** và **sử dụng**.

---

## 2. Lấy (Clone) Dự Án Về Máy

### 2.1. Mở Git Bash Hoặc Command Prompt

1. Bạn nhấn **phím Windows** trên bàn phím.
2. Gõ “**Git Bash**” hoặc “**Command Prompt**” (nếu đã cài Git Bash, khuyến khích dùng Git Bash cho dễ nhìn).
3. Nhấn Enter để mở cửa sổ dòng lệnh (màn hình đen/trắng).

### 2.2. Di Chuyển Đến Thư Mục Mong Muốn

Ví dụ, bạn muốn để dự án ở ổ D:\

- Gõ lệnh:
  ```bash
  cd /d D:\Work
  ```
  (hoặc bạn có thể tìm đường tới đúng thư mục mình muốn).

### 2.3. Clone Dự Án Từ GitHub (Hoặc Nguồn Khác)

Giả sử dự án có đường link Git là `https://github.com/username/student-management.git`, bạn làm như sau:

```bash
git clone https://github.com/username/student-management.git
```

Sau khi chạy lệnh xong, máy sẽ tải toàn bộ mã nguồn về thư mục `student-management` (hoặc tên bạn đã đặt).

> **Nếu bạn đã có sẵn code** (chứ không phải trên GitHub), thì có thể bỏ qua bước “clone” này và chỉ việc copy code về đúng thư mục.

---

## 3. Cài Đặt Môi Trường Ảo (Virtual Environment) Cho Backend

### 3.1. Vào Thư Mục `backend`

Giả sử bên trong dự án có cấu trúc:

```
student-management/
  ├─ backend/
  └─ frontend/
```

Bạn gõ:

```bash
cd student-management/backend
```

để di chuyển vào thư mục `backend`.

### 3.2. Tạo Và Kích Hoạt Venv

1. Tạo môi trường ảo (tên là `venv`):
   ```bash
   python -m venv venv
   ```
2. Kích hoạt môi trường ảo:
   - Nếu dùng **Windows (Command Prompt)**:
     ```bash
     venv\Scripts\activate
     ```
   - Nếu dùng **Windows (PowerShell)**:
     ```bash
     venv\\Scripts\\Activate.ps1
     ```
   - Nếu dùng **Git Bash**:
     `bash
source venv/Scripts/activate
`
     Sau bước này, bạn sẽ thấy trên dòng lệnh có hiển thị `(venv)` ở đầu, nghĩa là môi trường ảo đã bật.

### 3.3. Cài Đặt Thư Viện Cho Backend

Trong môi trường ảo `(venv)`:

```bash
pip install -r requirements.txt
```

Lệnh này sẽ cài toàn bộ thư viện cần thiết (FastAPI, SQLAlchemy, Alembic, bcrypt, v.v.).

---

## 4. Cấu Hình Và Tạo Cơ Sở Dữ Liệu

### 4.1. Mở pgAdmin Hoặc psql

Bạn đã có PostgreSQL, vì vậy hãy:

- Hoặc mở **pgAdmin**,
- Hoặc mở **psql** (dòng lệnh).

### 4.2. Tạo CSDL

Tạo một database tên `student_management_db` (nếu chưa có). Ví dụ với psql:

```sql
CREATE DATABASE student_management_db;
```

### 4.3. Cập Nhật Thông Tin Kết Nối Trong `database.py`

Bên trong `backend/app/database.py` (hoặc `database.py`), bạn kiểm tra biến `DATABASE_URL`:

```python
DATABASE_URL = "postgresql://postgres:password@localhost:5432/student_management_db"
```

- **Chỉnh** `password` thành mật khẩu thực tế của postgres trên máy bạn.
- **Chỉnh** `student_management_db` đúng tên database của bạn (nếu đổi khác).

### 4.4. Chạy Migration (Alembic)

1. Vẫn ở trong `backend`, với môi trường ảo `(venv)` đang bật.
2. Gõ lệnh:
   ```bash
   alembic upgrade head
   ```
   Lệnh này sẽ tạo các bảng trong `student_management_db` dựa trên file migration.

> Nếu bạn thấy báo lỗi “KeyError: url” hay “ModuleNotFoundError” gì đó, hãy kiểm tra lại file `alembic.ini` và `migrations/env.py` để chắc chắn `sqlalchemy.url` có giá trị trỏ đúng đến Postgres.

---

## 5. Chạy Lệnh Seed (Nếu Có)

Dự án có file `seed.py` để **wipe** dữ liệu cũ và **thêm** dữ liệu mẫu (5 admin, 10 classes, v.v.). Bạn có thể chạy:

```bash
python seed.py
```

- Script này sẽ tạo các bản ghi mẫu (admin, teacher, student...) trong database.
- Sau khi chạy xong, bạn có dữ liệu để kiểm tra.

---

## 6. Khởi Động Backend (FastAPI)

Vẫn ở thư mục `backend`:

```bash
uvicorn app.main:app --reload
```

- `--reload` nghĩa là nếu bạn sửa code Python, server tự động restart.
- Server lắng nghe mặc định tại `http://127.0.0.1:8000`

Hãy để cửa sổ này **mở** và **chạy**. Đừng tắt nó khi chuyển sang làm việc với frontend.

---

## 7. Cài Đặt Và Chạy Frontend (React)

### 7.1. Di Chuyển Vào Thư Mục `frontend`

Mở **tab mới** hoặc **cửa sổ mới** của dòng lệnh:

```bash
cd ../frontend
```

(sao cho bạn đang ở `student-management/frontend`).

### 7.2. Cài Đặt Thư Viện

Chạy:

```bash
npm install
```

nếu lần đầu tiên bạn mở. Lệnh này cài các package (React, axios, MUI, v.v.).

### 7.3. Khởi Động React Dev Server

```bash
npm start
```

- Mở trình duyệt tại `http://localhost:3000`
- Mỗi lần bạn thay đổi code JavaScript/React, trang sẽ tự động refresh.

---

## 8. Kiểm Tra Ứng Dụng

1. **Kiểm Tra Backend**
   - Mở `http://127.0.0.1:8000/docs` hoặc `http://127.0.0.1:8000/redoc` xem tài liệu API tự động do FastAPI tạo.
2. **Kiểm Tra Frontend**
   - Mở `http://localhost:3000` trong trình duyệt.
   - Đăng nhập theo tài khoản Admin/Teacher/Student đã tạo sẵn từ lệnh seed (hoặc từ script `seed.py`).
3. **Thực Hiện Chức Năng**
   - Admin: Tạo lịch, gán giáo viên, v.v.
   - Teacher: Cập nhật điểm.
   - Student: Xem lịch, xem điểm.

---

## 9. Upload Lên Git (Nếu Muốn Lưu Thay Đổi)

Trong trường hợp bạn có chỉnh sửa gì (không bắt buộc nếu chỉ chạy):

```bash
git status
git add .
git commit -m "Update x, y, z"
git push
```

- Nhưng như bạn nói, **bạn chưa biết Git**, tạm thời chỉ cần commit/push khi muốn đồng bộ code với người khác.

---

## 10. Xử Lý Một Số Lỗi Phổ Biến

1. **CORS Error**:

   - Nếu thấy dòng:  
     “Access to XMLHttpRequest at `http://localhost:8000/...` from origin `http://localhost:3000` has been blocked...”
   - Thì cần cấu hình CORS trong `app/main.py`:

     ```python
     from fastapi.middleware.cors import CORSMiddleware

     app = FastAPI()
     origins = ["http://localhost:3000"]
     app.add_middleware(
         CORSMiddleware,
         allow_origins=origins,
         allow_credentials=True,
         allow_methods=["*"],
         allow_headers=["*"],
     )
     ```

2. **Không Kết Nối Được PostgreSQL**:
   - Kiểm tra file `database.py` có `DATABASE_URL` trỏ đúng `user:password@host:port/db_name` chưa.
   - Chắc chắn PostgreSQL đang **chạy**.
3. **Port 3000** hay **8000** Đã Dùng Bởi Ứng Dụng Khác:
   - Tắt ứng dụng cũ, hoặc đổi port (`uvicorn app.main:app --port 9000` chẳng hạn).

---

## 11. Kết Luận

- Chỉ cần **làm đúng theo từng bước** trên là bạn sẽ chạy được **backend** (FastAPI) và **frontend** (React).
- Muốn thay đổi giao diện, bạn **chỉnh code** trong `frontend/src/...`.
- Muốn thay đổi logic, bạn **chỉnh code** trong `backend/app/...` (hoặc các file `.py` khác).
- Nếu cần dữ liệu mẫu, hãy nhớ chạy `python seed.py`.

Cảm ơn bạn đã làm theo hướng dẫn! Nếu còn thắc mắc, hãy liên hệ mình trực tiếp để hỗ trợ thêm. Chúc bạn triển khai dự án thành công!
