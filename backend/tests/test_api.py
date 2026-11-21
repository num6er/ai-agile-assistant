"""API 接口测试(不依赖真实 LLM 调用的部分)"""
import json


def test_health(client):
    resp = client.get("/api/health")
    assert resp.status_code == 200
    assert resp.get_json() == {"status": "ok"}


def test_create_project(client):
    resp = client.post("/api/projects", json={"name": "AI敏捷助手", "description": "demo"})
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["name"] == "AI敏捷助手"
    assert data["id"] == 1


def test_list_projects(client, project_id):
    resp = client.get("/api/projects")
    assert resp.status_code == 200
    assert len(resp.get_json()) == 1


def test_create_requirement(client, project_id):
    resp = client.post("/api/requirements", json={
        "project_id": project_id,
        "title": "PRD v1",
        "content": "系统需要支持用户注册登录、任务管理、看板视图",
    })
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["title"] == "PRD v1"
    assert data["project_id"] == project_id


def test_create_member(client, project_id):
    resp = client.post("/api/members", json={
        "project_id": project_id,
        "name": "张三",
        "role": "backend",
        "skills": ["python", "flask"],
        "capacity_hours": 40,
    })
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["name"] == "张三"
    assert data["skills"] == ["python", "flask"]


def test_update_task_status(client, project_id):
    """先建故事和任务,再更新状态"""
    # 建需求
    r = client.post("/api/requirements", json={
        "project_id": project_id, "title": "PRD", "content": "demo"
    })
    rid = r.get_json()["id"]
    # 直接建故事(跳过 AI 生成)
    from app.extensions import db
    from app import create_app
    app = create_app("development")
    # 用 client 的 app
    from app.models.user_story import UserStory
    with client.application.app_context():
        story = UserStory(
            project_id=project_id, requirement_id=rid, code="US-001",
            role="用户", goal="登录", benefit="使用系统",
            acceptance_criteria=json.dumps([]), priority="high", story_points=3,
        )
        db.session.add(story)
        db.session.commit()
        sid = story.id
        # 建任务
        from app.models.task import Task
        task = Task(
            project_id=project_id, story_id=sid, title="实现登录接口",
            type="backend", complexity="medium",
        )
        db.session.add(task)
        db.session.commit()
        tid = task.id

    # 更新任务状态
    resp = client.put(f"/api/tasks/{tid}", json={"status": "doing"})
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "doing"


def test_delete_project(client, project_id):
    resp = client.delete(f"/api/projects/{project_id}")
    assert resp.status_code == 204
