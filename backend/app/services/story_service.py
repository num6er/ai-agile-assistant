"""用户故事服务:AI 生成用户故事"""
import json
from ..extensions import db
from ..models.user_story import UserStory
from ..llm import llm_client, build_generate_stories_prompt
from ..llm.prompts import GENERATE_STORIES_SYSTEM


def generate_stories(requirement_id: int) -> list:
    """根据需求解析出的功能点,生成用户故事"""
    from ..models.requirement import Requirement
    req = Requirement.query.get_or_404(requirement_id)
    if not req.parsed_features:
        raise ValueError("需求尚未解析,请先调用 /parse")

    features = json.loads(req.parsed_features)
    user_prompt = build_generate_stories_prompt(features)
    result = llm_client.chat_json(GENERATE_STORIES_SYSTEM, user_prompt)

    created = []
    for idx, s in enumerate(result.get("stories", []), 1):
        story = UserStory(
            project_id=req.project_id,
            requirement_id=req.id,
            code=f"US-{idx:03d}",
            role=s.get("role", ""),
            goal=s.get("goal", ""),
            benefit=s.get("benefit", ""),
            acceptance_criteria=json.dumps(s.get("acceptance_criteria", []), ensure_ascii=False),
            priority=s.get("priority", "medium"),
            story_points=s.get("story_points", 0),
        )
        db.session.add(story)
        created.append(story)
    db.session.commit()
    return [s.to_dict() for s in created]
