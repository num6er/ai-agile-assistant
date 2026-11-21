"""Flask 应用工厂"""
import os
from flask import Flask, send_file
from .config import config_map
from .extensions import db, cors


def create_app(env: str = "development") -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_map[env])

    # 初始化扩展
    db.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})

    # 注册蓝图
    from .api.projects import projects_bp
    from .api.requirements import requirements_bp
    from .api.stories import stories_bp
    from .api.tasks import tasks_bp
    from .api.members import members_bp

    app.register_blueprint(projects_bp, url_prefix="/api/projects")
    app.register_blueprint(requirements_bp, url_prefix="/api/requirements")
    app.register_blueprint(stories_bp, url_prefix="/api/stories")
    app.register_blueprint(tasks_bp, url_prefix="/api/tasks")
    app.register_blueprint(members_bp, url_prefix="/api/members")

    # 建表
    with app.app_context():
        from . import models  # noqa: F401 保证模型被加载
        db.create_all()

    @app.route("/api/health")
    def health():
        return {"status": "ok"}

    @app.route("/")
    def index():
        return send_file(os.path.join(app.root_path, "templates", "index.html"))

    return app
