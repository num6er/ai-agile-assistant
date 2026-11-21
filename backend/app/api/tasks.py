"""任务 API:CRUD + AI 拆解/估算/分配"""
from flask import Blueprint, request, jsonify
from ..extensions import db
from ..models.task import Task
from ..services.task_service import decompose_story, estimate_tasks, assign_tasks

tasks_bp = Blueprint("tasks", __name__)


@tasks_bp.route("", methods=["GET"])
def list_tasks():
    pid = request.args.get("project_id", type=int)
    sid = request.args.get("story_id", type=int)
    q = Task.query
    if pid:
        q = q.filter_by(project_id=pid)
    if sid:
        q = q.filter_by(story_id=sid)
    return jsonify([t.to_dict() for t in q.all()])


@tasks_bp.route("/<int:tid>", methods=["GET"])
def get_task(tid):
    return jsonify(Task.query.get_or_404(tid).to_dict())


@tasks_bp.route("/<int:tid>", methods=["PUT"])
def update_task(tid):
    task = Task.query.get_or_404(tid)
    data = request.get_json()
    for f in ("title", "description", "type", "status", "assignee_id", "actual_hours"):
        if f in data:
            setattr(task, f, data[f])
    db.session.commit()
    return jsonify(task.to_dict())


@tasks_bp.route("/decompose", methods=["POST"])
def decompose():
    """AI 把用户故事拆解为任务"""
    data = request.get_json()
    try:
        tasks = decompose_story(data["story_id"])
        return jsonify(tasks), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@tasks_bp.route("/estimate", methods=["POST"])
def estimate():
    """AI 批量估算项目任务的工时"""
    data = request.get_json()
    try:
        tasks = estimate_tasks(data["project_id"])
        return jsonify(tasks)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@tasks_bp.route("/assign", methods=["POST"])
def assign():
    """AI 分配任务给成员"""
    data = request.get_json()
    try:
        tasks = assign_tasks(data["project_id"])
        return jsonify(tasks)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
