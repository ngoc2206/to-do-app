"""
To-Do App - Flask Web Version
Mở trình duyệt: http://localhost:5000
"""

from flask import Flask, render_template, request, jsonify
from todo_app import TaskManager, Task, Priority, Status
import json

app = Flask(__name__)
manager = TaskManager()


def task_to_json(task: Task) -> dict:
    d = task.to_dict()
    d["is_overdue"] = task.is_overdue()
    d["days_until"] = task.days_until_deadline()
    return d


# ── ROUTES ────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/tasks", methods=["GET"])
def get_tasks():
    status_filter = request.args.get("status")
    search = request.args.get("search", "").strip()

    manager._refresh_overdue()

    if search:
        tasks = manager.search_tasks(search)
    elif status_filter and status_filter != "all":
        try:
            status = Status(status_filter)
            tasks = manager.filter_by_status(status)
        except ValueError:
            tasks = manager.get_all_tasks()
    else:
        tasks = manager.get_all_tasks()

    return jsonify([task_to_json(t) for t in tasks])


@app.route("/api/tasks", methods=["POST"])
def add_task():
    data = request.json
    try:
        priority = Priority(data.get("priority", Priority.MEDIUM.value))
        task = manager.add_task(
            title=data["title"],
            description=data.get("description", ""),
            deadline=data.get("deadline") or None,
            priority=priority,
        )
        return jsonify(task_to_json(task)), 201
    except (ValueError, KeyError) as e:
        return jsonify({"error": str(e)}), 400


@app.route("/api/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    data = request.json
    try:
        priority = Priority(data["priority"]) if "priority" in data else None
        status = Status(data["status"]) if "status" in data else None
        task = manager.update_task(
            task_id,
            title=data.get("title"),
            description=data.get("description"),
            deadline=data.get("deadline") or None,
            priority=priority,
            status=status,
        )
        return jsonify(task_to_json(task))
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@app.route("/api/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    try:
        manager.delete_task(task_id)
        return jsonify({"success": True})
    except ValueError as e:
        return jsonify({"error": str(e)}), 404


@app.route("/api/reminders")
def reminders():
    r = manager.check_reminders()
    return jsonify({
        "overdue": [task_to_json(t) for t in r["overdue"]],
        "upcoming": [task_to_json(t) for t in r["upcoming_3days"]],
    })


@app.route("/api/stats")
def stats():
    return jsonify(manager.get_statistics())


if __name__ == "__main__":
    print("\nTo-Do App Web đang chạy tại: http://localhost:5000\n")
    app.run(debug=True, port=5000)
    # Flask backend completed