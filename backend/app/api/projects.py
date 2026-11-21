"""项目 API"""
from flask import Blueprint, request, jsonify
from ..extensions import db
from ..models.project import Project

projects_bp = Blueprint("projects", __name__)


@projects_bp.route("", methods=["POST"])
def create_project():
    data = request.get_json()
    project = Project(name=data["name"], description=data.get("description", ""))
    db.session.add(project)
    db.session.commit()
    return jsonify(project.to_dict()), 201


@projects_bp.route("", methods=["GET"])
def list_projects():
    projects = Project.query.all()
    return jsonify([p.to_dict() for p in projects])


@projects_bp.route("/<int:pid>", methods=["GET"])
def get_project(pid):
    return jsonify(Project.query.get_or_404(pid).to_dict())


@projects_bp.route("/<int:pid>", methods=["DELETE"])
def delete_project(pid):
    project = Project.query.get_or_404(pid)
    db.session.delete(project)
    db.session.commit()
    return "", 204
