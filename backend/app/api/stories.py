"""用户故事 API:CRUD + AI 生成"""
from flask import Blueprint, request, jsonify
from ..extensions import db
from ..models.user_story import UserStory
from ..services.story_service import generate_stories

stories_bp = Blueprint("stories", __name__)


@stories_bp.route("", methods=["GET"])
def list_stories():
    pid = request.args.get("project_id", type=int)
    rid = request.args.get("requirement_id", type=int)
    q = UserStory.query
    if pid:
        q = q.filter_by(project_id=pid)
    if rid:
        q = q.filter_by(requirement_id=rid)
    return jsonify([s.to_dict() for s in q.all()])


@stories_bp.route("/<int:sid>", methods=["GET"])
def get_story(sid):
    return jsonify(UserStory.query.get_or_404(sid).to_dict())


@stories_bp.route("/<int:sid>", methods=["PUT"])
def update_story(sid):
    story = UserStory.query.get_or_404(sid)
    data = request.get_json()
    for f in ("role", "goal", "benefit", "priority", "story_points"):
        if f in data:
            setattr(story, f, data[f])
    db.session.commit()
    return jsonify(story.to_dict())


@stories_bp.route("/generate", methods=["POST"])
def generate():
    """AI 根据需求生成用户故事"""
    data = request.get_json()
    try:
        stories = generate_stories(data["requirement_id"])
        return jsonify(stories), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500
