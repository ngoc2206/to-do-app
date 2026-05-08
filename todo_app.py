"""
To-Do App - Hệ thống quản lý công việc
Author: Nhóm sinh viên
Version: 1.0.0
"""

import json
import os
from datetime import datetime, date
from enum import Enum


class Priority(Enum):
    LOW = "Thấp"
    MEDIUM = "Trung bình"
    HIGH = "Cao"


class Status(Enum):
    PENDING = "Chờ xử lý"
    IN_PROGRESS = "Đang thực hiện"
    DONE = "Hoàn thành"
    OVERDUE = "Quá hạn"


class Task:
    """Lớp đại diện cho một công việc"""

    def __init__(self, task_id: int, title: str, description: str = "",
                 deadline: str = None, priority: Priority = Priority.MEDIUM):
        self.task_id = task_id
        self.title = title
        self.description = description
        self.deadline = deadline  # format: "YYYY-MM-DD"
        self.priority = priority
        self.status = Status.PENDING
        self.created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.updated_at = self.created_at

    def to_dict(self) -> dict:
        return {
            "task_id": self.task_id,
            "title": self.title,
            "description": self.description,
            "deadline": self.deadline,
            "priority": self.priority.value,
            "status": self.status.value,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        task = cls(
            task_id=data["task_id"],
            title=data["title"],
            description=data.get("description", ""),
            deadline=data.get("deadline"),
            priority=Priority(data.get("priority", Priority.MEDIUM.value))
        )
        task.status = Status(data.get("status", Status.PENDING.value))
        task.created_at = data.get("created_at", "")
        task.updated_at = data.get("updated_at", "")
        return task

    def is_overdue(self) -> bool:
        if self.deadline and self.status != Status.DONE:
            deadline_date = datetime.strptime(self.deadline, "%Y-%m-%d").date()
            return date.today() > deadline_date
        return False

    def days_until_deadline(self) -> int | None:
        if self.deadline:
            deadline_date = datetime.strptime(self.deadline, "%Y-%m-%d").date()
            return (deadline_date - date.today()).days
        return None

    def __str__(self) -> str:
        deadline_str = self.deadline if self.deadline else "Không có"
        overdue_flag = " ⚠️ QUÁ HẠN" if self.is_overdue() else ""
        return (f"[{self.task_id}] {self.title} | {self.status.value} | "
                f"Deadline: {deadline_str}{overdue_flag} | Ưu tiên: {self.priority.value}")


class TaskManager:
    """Lớp quản lý danh sách công việc"""

    DATA_FILE = "tasks.json"

    def __init__(self):
        self.tasks: list[Task] = []
        self._next_id = 1
        self.load_from_file()

    # ── CRUD ─────────────────────────────────────────────────────────────────

    def add_task(self, title: str, description: str = "",
                 deadline: str = None, priority: Priority = Priority.MEDIUM) -> Task:
        """Thêm công việc mới"""
        if not title.strip():
            raise ValueError("Tiêu đề công việc không được để trống!")
        if deadline:
            datetime.strptime(deadline, "%Y-%m-%d")  # validate format

        task = Task(self._next_id, title.strip(), description, deadline, priority)
        self._next_id += 1
        self.tasks.append(task)
        self.save_to_file()
        return task

    def update_task(self, task_id: int, title: str = None, description: str = None,
                    deadline: str = None, priority: Priority = None,
                    status: Status = None) -> Task:
        """Sửa công việc theo ID"""
        task = self.get_task_by_id(task_id)
        if title is not None:
            task.title = title.strip()
        if description is not None:
            task.description = description
        if deadline is not None:
            datetime.strptime(deadline, "%Y-%m-%d")
            task.deadline = deadline
        if priority is not None:
            task.priority = priority
        if status is not None:
            task.status = status
        task.updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.save_to_file()
        return task

    def delete_task(self, task_id: int) -> bool:
        """Xóa công việc theo ID"""
        task = self.get_task_by_id(task_id)
        self.tasks.remove(task)
        self.save_to_file()
        return True

    def get_task_by_id(self, task_id: int) -> Task:
        for task in self.tasks:
            if task.task_id == task_id:
                return task
        raise ValueError(f"Không tìm thấy công việc với ID {task_id}")

    # ── LỌC / TÌM KIẾM ───────────────────────────────────────────────────────

    def filter_by_status(self, status: Status) -> list[Task]:
        """Lọc công việc theo trạng thái"""
        self._refresh_overdue()
        return [t for t in self.tasks if t.status == status]

    def get_overdue_tasks(self) -> list[Task]:
        """Lấy danh sách công việc quá hạn"""
        self._refresh_overdue()
        return [t for t in self.tasks if t.status == Status.OVERDUE]

    def get_upcoming_tasks(self, days: int = 3) -> list[Task]:
        """Lấy công việc sắp đến hạn trong N ngày"""
        result = []
        for task in self.tasks:
            if task.status in (Status.PENDING, Status.IN_PROGRESS):
                remaining = task.days_until_deadline()
                if remaining is not None and 0 <= remaining <= days:
                    result.append(task)
        return sorted(result, key=lambda t: t.deadline)

    def search_tasks(self, keyword: str) -> list[Task]:
        """Tìm kiếm công việc theo từ khóa"""
        kw = keyword.lower()
        return [t for t in self.tasks
                if kw in t.title.lower() or kw in t.description.lower()]

    def get_all_tasks(self) -> list[Task]:
        self._refresh_overdue()
        return list(self.tasks)

    # ── NHẮC NHỞ ─────────────────────────────────────────────────────────────

    def check_reminders(self) -> dict:
        """Kiểm tra nhắc nhở: quá hạn + sắp hạn"""
        self._refresh_overdue()
        return {
            "overdue": self.get_overdue_tasks(),
            "upcoming_3days": self.get_upcoming_tasks(days=3)
        }

    def _refresh_overdue(self):
        """Tự động cập nhật trạng thái OVERDUE"""
        for task in self.tasks:
            if task.status not in (Status.DONE, Status.OVERDUE) and task.is_overdue():
                task.status = Status.OVERDUE

    # ── LƯU / TẢI ────────────────────────────────────────────────────────────

    def save_to_file(self):
        data = {
            "next_id": self._next_id,
            "tasks": [t.to_dict() for t in self.tasks]
        }
        with open(self.DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load_from_file(self):
        if not os.path.exists(self.DATA_FILE):
            return
        try:
            with open(self.DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            self._next_id = data.get("next_id", 1)
            self.tasks = [Task.from_dict(t) for t in data.get("tasks", [])]
        except (json.JSONDecodeError, KeyError):
            self.tasks = []

    def get_statistics(self) -> dict:
        self._refresh_overdue()
        total = len(self.tasks)
        by_status = {s: 0 for s in Status}
        for t in self.tasks:
            by_status[t.status] += 1
        return {"total": total, "by_status": {s.value: c for s, c in by_status.items()}}


# ── GIAO DIỆN DÒNG LỆNH (CLI) ────────────────────────────────────────────────

class TodoCLI:
    """Giao diện người dùng dạng dòng lệnh"""

    def __init__(self):
        self.manager = TaskManager()

    def run(self):
        print("\n" + "="*55)
        print("        HỆ THỐNG QUẢN LÝ CÔNG VIỆC  ")
        print("="*55)
        self._show_reminders()

        while True:
            self._print_menu()
            choice = input("Nhập lựa chọn: ").strip()
            actions = {
                "1": self._add_task,
                "2": self._list_tasks,
                "3": self._update_task,
                "4": self._delete_task,
                "5": self._filter_tasks,
                "6": self._show_reminders,
                "7": self._search_tasks,
                "8": self._show_stats,
                "0": self._exit,
            }
            action = actions.get(choice)
            if action:
                action()
            else:
                print(" Lựa chọn không hợp lệ!")

    def _print_menu(self):
        print("\n" + "-"*40)
        print("  1. + Thêm công việc")
        print("  2.  Xem tất cả công việc")
        print("  3.   Sửa công việc")
        print("  4.   Xóa công việc")
        print("  5.  Lọc theo trạng thái")
        print("  6.  Kiểm tra nhắc nhở")
        print("  7.  Tìm kiếm")
        print("  8.  Thống kê")
        print("  0.  Thoát")
        print("-"*40)

    def _add_task(self):
        print("\n── THÊM CÔNG VIỆC MỚI ──")
        title = input("Tiêu đề (*): ").strip()
        description = input("Mô tả: ").strip()
        deadline = input("Deadline (YYYY-MM-DD, Enter để bỏ qua): ").strip() or None
        print("Mức độ ưu tiên: 1=Thấp  2=Trung bình  3=Cao")
        p_map = {"1": Priority.LOW, "2": Priority.MEDIUM, "3": Priority.HIGH}
        priority = p_map.get(input("Chọn (mặc định 2): ").strip(), Priority.MEDIUM)
        try:
            task = self.manager.add_task(title, description, deadline, priority)
            print(f" Đã thêm: {task}")
        except ValueError as e:
            print(f" Lỗi: {e}")

    def _list_tasks(self):
        tasks = self.manager.get_all_tasks()
        if not tasks:
            print("\n Chưa có công việc nào.")
            return
        print(f"\n── DANH SÁCH CÔNG VIỆC ({len(tasks)}) ──")
        for t in tasks:
            print(f"  {t}")

    def _update_task(self):
        self._list_tasks()
        try:
            task_id = int(input("\nID cần sửa: "))
            task = self.manager.get_task_by_id(task_id)
            print(f"Đang sửa: {task}")
            title = input(f"Tiêu đề mới [{task.title}]: ").strip() or task.title
            desc = input(f"Mô tả mới [{task.description}]: ").strip() or task.description
            dl = input(f"Deadline mới [{task.deadline}]: ").strip() or task.deadline
            print("Trạng thái: 1=Chờ  2=Đang làm  3=Xong  4=Quá hạn")
            s_map = {"1": Status.PENDING, "2": Status.IN_PROGRESS,
                     "3": Status.DONE, "4": Status.OVERDUE}
            status = s_map.get(input("Chọn (Enter để giữ nguyên): ").strip())
            self.manager.update_task(task_id, title, desc, dl, status=status)
            print(" Đã cập nhật!")
        except (ValueError, TypeError) as e:
            print(f" Lỗi: {e}")

    def _delete_task(self):
        self._list_tasks()
        try:
            task_id = int(input("\nID cần xóa: "))
            task = self.manager.get_task_by_id(task_id)
            confirm = input(f"Xóa '{task.title}'? (y/n): ").strip().lower()
            if confirm == "y":
                self.manager.delete_task(task_id)
                print("Đã xóa!")
            else:
                print("Đã hủy.")
        except ValueError as e:
            print(f" Lỗi: {e}")

    def _filter_tasks(self):
        print("\nLọc theo: 1=Chờ  2=Đang làm  3=Xong  4=Quá hạn")
        s_map = {"1": Status.PENDING, "2": Status.IN_PROGRESS,
                 "3": Status.DONE, "4": Status.OVERDUE}
        status = s_map.get(input("Chọn: ").strip())
        if not status:
            print(" Lựa chọn không hợp lệ!"); return
        tasks = self.manager.filter_by_status(status)
        print(f"\n── {status.value.upper()} ({len(tasks)}) ──")
        for t in tasks:
            print(f"  {t}")
        if not tasks:
            print("  (Không có công việc nào)")

    def _show_reminders(self):
        reminders = self.manager.check_reminders()
        if reminders["overdue"]:
            print(f"\n QUÁ HẠN ({len(reminders['overdue'])} việc):")
            for t in reminders["overdue"]:
                print(f"     {t}")
        if reminders["upcoming_3days"]:
            print(f"\n SẮP ĐẾN HẠN ({len(reminders['upcoming_3days'])} việc trong 3 ngày):")
            for t in reminders["upcoming_3days"]:
                days = t.days_until_deadline()
                print(f"    {t} | còn {days} ngày")

    def _search_tasks(self):
        kw = input("\nNhập từ khóa tìm kiếm: ").strip()
        results = self.manager.search_tasks(kw)
        print(f"\n── KẾT QUẢ ({len(results)}) ──")
        for t in results:
            print(f"  {t}")

    def _show_stats(self):
        stats = self.manager.get_statistics()
        print(f"\n── THỐNG KÊ ({stats['total']} công việc) ──")
        for status, count in stats["by_status"].items():
            bar = "█" * count
            print(f"  {status:<18} {count:3}  {bar}")

    def _exit(self):
        print("\nTạm biệt!\n")
        exit(0)


if __name__ == "__main__":
    TodoCLI().run()