"""任务服务:AI 拆解任务、估算工时、分配"""
import json
from ..extensions import db
from ..models.task import Task
from ..llm import llm_client
from ..llm.prompts import (
    build_decompose_tasks_prompt,
    build_estimate_hours_prompt,
    build_assign_tasks_prompt,
    DECOMPOSE_TASKS_SYSTEM,
    ESTIMATE_HOURS_SYSTEM,
    ASSIGN_TASKS_SYSTEM,
)


def decompose_story(story_id: int) -> list:
    """把用户故事拆解为开发任务"""
    from ..models.user_story import UserStory
    story = UserStory.query.get_or_404(story_id)
    story_dict = story.to_dict()
    user_prompt = build_decompose_tasks_prompt(story_dict)
    result = llm_client.chat_json(DECOMPOSE_TASKS_SYSTEM, user_prompt)

    created = []
    for t in result.get("tasks", []):
        task = Task(
            project_id=story.project_id,
            story_id=story.id,
            title=t.get("title", ""),
            description=t.get("description", ""),
            type=t.get("type", "dev"),
            complexity=t.get("complexity", "medium"),
        )
        db.session.add(task)
        created.append(task)
    db.session.commit()
    return [t.to_dict() for t in created]


# 单次 LLM 调用的最大任务数。任务过多时 LLM 输出会超过 max_tokens 被截断,
# 导致 JSON 解析失败,因此按批调用后合并结果。
BATCH_SIZE = 30


def _chunks(items: list, size: int) -> list:
    return [items[i:i + size] for i in range(0, len(items), size)]


def estimate_tasks(project_id: int) -> list:
    """批量估算项目下所有任务的工时"""
    tasks = Task.query.filter_by(project_id=project_id).all()
    if not tasks:
        return []
    task_list = [{"title": t.title, "type": t.type, "complexity": t.complexity} for t in tasks]

    # 分批估算,避免单次输出被截断
    estimates = {}
    for batch in _chunks(task_list, BATCH_SIZE):
        user_prompt = build_estimate_hours_prompt(batch)
        result = llm_client.chat_json(ESTIMATE_HOURS_SYSTEM, user_prompt)
        for e in result.get("estimates", []):
            if e.get("title"):
                estimates[e["title"]] = e

    # 用 title 做匹配
    for t in tasks:
        est = estimates.get(t.title)
        if est:
            t.estimate_hours = est.get("estimate_hours", 0)
    db.session.commit()
    return [t.to_dict() for t in tasks]


def assign_tasks(project_id: int) -> list:
    """AI 分配任务给成员"""
    from ..models.member import Member
    tasks = Task.query.filter_by(project_id=project_id).all()
    members = Member.query.filter_by(project_id=project_id).all()
    if not tasks or not members:
        raise ValueError("项目缺少任务或成员")

    task_list = [
        {"title": t.title, "type": t.type, "estimate_hours": t.estimate_hours}
        for t in tasks
    ]
    member_list = [
        {
            "name": m.name,
            "role": m.role,
            "skills": json.loads(m.skills) if m.skills else [],
            "capacity_hours": m.capacity_hours,
        }
        for m in members
    ]

    # 分批分配,避免单次输出被截断
    assignments = []
    for batch in _chunks(task_list, BATCH_SIZE):
        user_prompt = build_assign_tasks_prompt(batch, member_list)
        result = llm_client.chat_json(ASSIGN_TASKS_SYSTEM, user_prompt)
        assignments.extend(result.get("assignments", []))

    # 用 name 匹配成员
    name_to_member = {m.name: m for m in members}
    title_to_task = {t.title: t for t in tasks}
    for a in assignments:
        task = title_to_task.get(a.get("task_title"))
        member = name_to_member.get(a.get("assignee_name"))
        if task and member:
            task.assignee_id = member.id
    db.session.commit()
    return [t.to_dict() for t in tasks]
