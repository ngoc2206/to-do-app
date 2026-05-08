"""
seed_data.py — Tạo dữ liệu mẫu cho To-Do App
Chạy: python seed_data.py
"""
from todo_app import TaskManager, Priority, Status
from datetime import date, timedelta

manager = TaskManager()

# Xóa dữ liệu cũ nếu có
manager.tasks = []
manager._next_id = 1

today = date.today()
fmt = lambda d: d.strftime("%Y-%m-%d")

tasks = [
    # ── Chờ xử lý ──
    dict(title="Làm báo cáo môn Python",
         description="Hoàn thành báo cáo cuối kì theo mẫu giáo viên yêu cầu",
         deadline=fmt(today + timedelta(days=7)),
         priority=Priority.HIGH),

    dict(title="Vẽ sơ đồ UML class diagram",
         description="Dùng draw.io vẽ sơ đồ cho 3 lớp: Task, TaskManager, TodoCLI",
         deadline=fmt(today + timedelta(days=5)),
         priority=Priority.HIGH),

    dict(title="Viết README trên GitHub",
         description="Mô tả dự án, hướng dẫn cài đặt, link UML, bảng thành viên",
         deadline=fmt(today + timedelta(days=6)),
         priority=Priority.MEDIUM),

    dict(title="Ôn tập môn Cơ sở dữ liệu",
         description="Ôn lại SQL cơ bản, JOIN, GROUP BY trước khi thi",
         deadline=fmt(today + timedelta(days=3)),
         priority=Priority.MEDIUM),

    dict(title="Đọc tài liệu Flask",
         description="Đọc phần Routing, Templates, REST API trên docs.flask.palletsprojects.com",
         deadline=fmt(today + timedelta(days=10)),
         priority=Priority.LOW),

    # ── Đang thực hiện ──
    dict(title="Code chức năng thêm/sửa/xóa task",
         description="Hoàn thiện CRUD trong lớp TaskManager, test đầy đủ các trường hợp",
         deadline=fmt(today + timedelta(days=2)),
         priority=Priority.HIGH),

    dict(title="Thiết kế giao diện web Flask",
         description="Xây dựng index.html với HTML/CSS/JS, kết nối API backend",
         deadline=fmt(today + timedelta(days=4)),
         priority=Priority.HIGH),

    dict(title="Push code lên GitHub",
         description="Tạo repo, commit ít nhất 3 lần mỗi thành viên, viết commit message rõ ràng",
         deadline=fmt(today + timedelta(days=8)),
         priority=Priority.MEDIUM),

    # ── Hoàn thành ──
    dict(title="Khởi tạo project Python",
         description="Tạo cấu trúc thư mục, tạo file todo_app.py, app.py",
         deadline=fmt(today - timedelta(days=3)),
         priority=Priority.MEDIUM),

    dict(title="Định nghĩa class Task và Enum",
         description="Tạo class Task, Priority, Status với đầy đủ thuộc tính",
         deadline=fmt(today - timedelta(days=2)),
         priority=Priority.HIGH),

    dict(title="Cài đặt môi trường Flask",
         description="pip install flask, kiểm tra chạy hello world thành công",
         deadline=fmt(today - timedelta(days=5)),
         priority=Priority.LOW),

    # ── Quá hạn ──
    dict(title="Nộp bản phác thảo thiết kế",
         description="Nộp sơ đồ class và mô tả chức năng cho giáo viên duyệt",
         deadline=fmt(today - timedelta(days=4)),
         priority=Priority.HIGH),

    dict(title="Họp nhóm phân công công việc",
         description="Phân chia từng chức năng cho từng thành viên, thống nhất deadline",
         deadline=fmt(today - timedelta(days=6)),
         priority=Priority.MEDIUM),
]

# Thêm tất cả tasks
for t in tasks:
    manager.add_task(**t)

# Cập nhật trạng thái
in_progress_ids = [6, 7, 8]
done_ids = [9, 10, 11]

for tid in in_progress_ids:
    manager.update_task(tid, status=Status.IN_PROGRESS)

for tid in done_ids:
    manager.update_task(tid, status=Status.DONE)

# Quá hạn sẽ tự động cập nhật khi app chạy
manager._refresh_overdue()
manager.save_to_file()

print(f" Đã tạo {len(manager.tasks)} công việc mẫu!")
print(f"   • Chờ xử lý  : {len(manager.filter_by_status(__import__('todo_app').Status.PENDING))}")
print(f"   • Đang làm   : {len(manager.filter_by_status(__import__('todo_app').Status.IN_PROGRESS))}")
print(f"   • Hoàn thành : {len(manager.filter_by_status(__import__('todo_app').Status.DONE))}")
print(f"   • Quá hạn    : {len(manager.filter_by_status(__import__('todo_app').Status.OVERDUE))}")
