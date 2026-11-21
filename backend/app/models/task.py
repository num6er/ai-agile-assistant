"""任务模型"""
from datetime import datetime
from ..extensions import db


class Task(db.Model):
    __tablename__ = "tasks"

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=False)
    story_id = db.Column(db.Integer, db.ForeignKey("user_stories.id"), nullable=False)
    title = db.Column(db.String(256), nullable=False)
    description = db.Column(db.Text)
    type = db.Column(db.String(32), default="dev")  # dev/frontend/backend/test/docs
    estimate_hours = db.Column(db.Float, default=0)  # AI 估算工时
    actual_hours = db.Column(db.Float)  # 实际工时
    status = db.Column(db.String(16), default="todo")  # todo/doing/done
    assignee_id = db.Column(db.Integer, db.ForeignKey("members.id"))
    complexity = db.Column(db.String(16), default="medium")  # low/medium/high
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    assignee = db.relationship("Member", backref="tasks")

    def to_dict(self):
        return {
            "id": self.id,
            "project_id": self.project_id,
            "story_id": self.story_id,
            "title": self.title,
            "description": self.description,
            "type": self.type,
            "estimate_hours": self.estimate_hours,
            "actual_hours": self.actual_hours,
            "status": self.status,
            "assignee_id": self.assignee_id,
            "assignee_name": self.assignee.name if self.assignee else None,
            "complexity": self.complexity,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
