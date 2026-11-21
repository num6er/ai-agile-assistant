"""成员 API"""
import json
from flask import Blueprint, request, jsonify
from ..extensions import db
from ..models.member import Member

members_bp = Blueprint("members", __name__)


@members_bp.route("", methods=["POST"])
def create_member():
    data = request.get_json()
    member = Member(
        project_id=data["project_id"],
        name=data["name"],
        role=data["role"],
        skills=json.dumps(data.get("skills", []), ensure_ascii=False),
        capacity_hours=data.get("capacity_hours", 40),
    )
    db.session.add(member)
    db.session.commit()
    return jsonify(member.to_dict()), 201


@members_bp.route("", methods=["GET"])
def list_members():
    pid = request.args.get("project_id", type=int)
    q = Member.query
    if pid:
        q = q.filter_by(project_id=pid)
    return jsonify([m.to_dict() for m in q.all()])


@members_bp.route("/<int:mid>", methods=["DELETE"])
def delete_member(mid):
    member = Member.query.get_or_404(mid)
    db.session.delete(member)
    db.session.commit()
    return "", 204
