"""需求 API:CRUD + AI 解析"""
from flask import Blueprint, request, jsonify
from ..extensions import db
from ..models.requirement import Requirement
from ..services.requirement_service import parse_requirement

requirements_bp = Blueprint("requirements", __name__)


@requirements_bp.route("", methods=["POST"])
def create_requirement():
    data = request.get_json()
    req = Requirement(
        project_id=data["project_id"],
        title=data["title"],
        content=data["content"],
        source=data.get("source", "manual"),
    )
    db.session.add(req)
    db.session.commit()
    return jsonify(req.to_dict()), 201


@requirements_bp.route("", methods=["GET"])
def list_requirements():
    pid = request.args.get("project_id", type=int)
    q = Requirement.query
    if pid:
        q = q.filter_by(project_id=pid)
    return jsonify([r.to_dict() for r in q.all()])


@requirements_bp.route("/<int:rid>", methods=["GET"])
def get_requirement(rid):
    return jsonify(Requirement.query.get_or_404(rid).to_dict())


@requirements_bp.route("/<int:rid>/parse", methods=["POST"])
def parse(rid):
    """AI 解析需求文档,抽取功能点"""
    try:
        result = parse_requirement(rid)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
