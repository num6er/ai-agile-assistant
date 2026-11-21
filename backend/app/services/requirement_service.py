"""需求服务:AI 解析 PRD → 功能点"""
import json
from ..extensions import db
from ..models.requirement import Requirement
from ..llm import llm_client, build_parse_requirement_prompt


def parse_requirement(requirement_id: int) -> dict:
    """调用 LLM 解析需求文档,抽取功能点并落库"""
    req = Requirement.query.get_or_404(requirement_id)
    user_prompt = build_parse_requirement_prompt(req.content)

    from ..llm.prompts import PARSE_REQUIREMENT_SYSTEM
    result = llm_client.chat_json(PARSE_REQUIREMENT_SYSTEM, user_prompt)

    # 落库
    req.parsed_features = json.dumps(result.get("features", []), ensure_ascii=False)
    db.session.commit()

    return {
        "summary": result.get("summary", ""),
        "features": result.get("features", []),
    }
