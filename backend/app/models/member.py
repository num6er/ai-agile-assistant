"""团队成员模型"""
from datetime import datetime
from ..extensions import db


class SkillEnum:
    BACKEND = "backend"
    FRONTEND = "frontend"
    TEST = "test"
    DEVOPS = "devops"
    PRODUCT = "product"


class Member(db.Model):
    __tablename__ = "members"

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=False)
    name = db.Column(db.String(64), nullable=False)
    role = db.Column(db.String(32), nullable=False)  # leader/backend/frontend/test/devops
    skills = db.Column(db.Text)  # 技能列表(JSON)
    capacity_hours = db.Column(db.Float, default=40)  # 周可用工时
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        import json
        return {
            "id": self.id,
            "project_id": self.project_id,
            "name": self.name,
            "role": self.role,
            "skills": json.loads(self.skills) if self.skills else [],
            "capacity_hours": self.capacity_hours,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
