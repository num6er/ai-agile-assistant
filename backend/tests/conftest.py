"""pytest fixtures"""
import pytest
from app import create_app
from app.extensions import db


@pytest.fixture
def app():
    """测试用 app,内存数据库"""
    app = create_app("development")
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["TESTING"] = True
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def project_id(client):
    """创建一个测试项目"""
    resp = client.post("/api/projects", json={"name": "测试项目", "description": "用于测试"})
    return resp.get_json()["id"]
