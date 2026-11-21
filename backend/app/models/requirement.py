"""需求文档模型"""
from datetime import datetime
from ..extensions import db


class Requirement(db.Model):
    __tablename__ = "requirements"

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=False)
    title = db.Column(db.String(256), nullable=False)
    content = db.Column(db.Text, nullable=False)  # PRD 原文
    source = db.Column(db.String(32), default="manual")  # manual / upload
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # AI 解析后的功能点(JSON 字符串)
    parsed_features = db.Column(db.Text)

    stories = db.relationship("UserStory", backref="requirement", cascade="all, delete-orphan")

    def to_dict(self):
        import json
        return {
            "id": self.id,
            "project_id": self.project_id,
            "title": self.title,
            "content": self.content,
            "source": self.source,
            "parsed_features": json.loads(self.parsed_features) if self.parsed_features else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
