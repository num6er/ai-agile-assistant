"""用户故事模型"""
from datetime import datetime
from ..extensions import db


class UserStory(db.Model):
    __tablename__ = "user_stories"

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=False)
    requirement_id = db.Column(db.Integer, db.ForeignKey("requirements.id"), nullable=False)
    code = db.Column(db.String(32))  # 如 US-001
    role = db.Column(db.String(64), nullable=False)  # 作为...
    goal = db.Column(db.String(256), nullable=False)  # 我希望...
    benefit = db.Column(db.String(256), nullable=False)  # 以便...
    acceptance_criteria = db.Column(db.Text)  # 验收标准(JSON)
    priority = db.Column(db.String(16), default="medium")  # high/medium/low
    story_points = db.Column(db.Float, default=0)  # 故事点
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    tasks = db.relationship("Task", backref="story", cascade="all, delete-orphan")

    def to_dict(self):
        import json
        return {
            "id": self.id,
            "project_id": self.project_id,
            "requirement_id": self.requirement_id,
            "code": self.code,
            "role": self.role,
            "goal": self.goal,
            "benefit": self.benefit,
            "acceptance_criteria": json.loads(self.acceptance_criteria) if self.acceptance_criteria else None,
            "priority": self.priority,
            "story_points": self.story_points,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
