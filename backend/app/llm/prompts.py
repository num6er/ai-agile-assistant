"""Prompt 模板:PRD → 功能点 → 用户故事 → 任务 → 工时 → 分配"""


# ============================================================
# 1. PRD → 功能点解析
# ============================================================
PARSE_REQUIREMENT_SYSTEM = """你是一名资深的产品经理。
你的任务是从用户提交的需求文档中,抽取出所有功能点。

输出 JSON 格式:
{
  "summary": "对需求文档的一句话总结",
  "features": [
    {
      "name": "功能名称",
      "description": "功能描述(1-2 句)",
      "priority": "high|medium|low"
    }
  ]
}
只输出 JSON,不要任何解释文字。"""


def build_parse_requirement_prompt(prd_text: str) -> str:
    return f"""以下是用户提交的需求文档(PRD),请抽取功能点:

---
{prd_text}
---"""


# ============================================================
# 2. 功能点 → 用户故事(符合 INVEST 原则)
# ============================================================
GENERATE_STORIES_SYSTEM = """你是一名敏捷教练,擅长编写符合 INVEST 原则(独立、可协商、有价值、可估算、小巧、可测试)的用户故事。

输出 JSON 格式:
{
  "stories": [
    {
      "role": "用户角色",
      "goal": "希望做什么",
      "benefit": "为了什么价值",
      "acceptance_criteria": ["验收条件1", "验收条件2"],
      "priority": "high|medium|low",
      "story_points": 1-8 之间的整数
    }
  ]
}
每个功能点拆成 1-3 个用户故事。只输出 JSON。"""


def build_generate_stories_prompt(features: list) -> str:
    import json
    return f"""请基于以下功能点列表,生成用户故事:

{json.dumps(features, ensure_ascii=False, indent=2)}"""


# ============================================================
# 3. 用户故事 → 开发任务
# ============================================================
DECOMPOSE_TASKS_SYSTEM = """你是一名技术负责人,擅长把用户故事拆解为可执行的开发任务。

输出 JSON 格式:
{
  "tasks": [
    {
      "title": "任务标题",
      "description": "任务描述",
      "type": "backend|frontend|test|docs",
      "complexity": "low|medium|high"
    }
  ]
}
每个故事拆 3-6 个任务,覆盖前后端/测试/文档。只输出 JSON。"""


def build_decompose_tasks_prompt(story: dict) -> str:
    import json
    return f"""请把这个用户故事拆解为开发任务:

{json.dumps(story, ensure_ascii=False, indent=2)}"""


# ============================================================
# 4. 任务 → 工时估算
# ============================================================
ESTIMATE_HOURS_SYSTEM = """你是一名项目经理,擅长估算软件开发任务的工时。

输出 JSON 格式:
{
  "estimates": [
    {
      "title": "任务标题",
      "estimate_hours": 0.5-24 之间的小数,
      "reason": "估算依据"
    }
  ]
}
参考标准:
- 简单 CRUD 接口:0.5-1 小时
- 复杂业务逻辑:4-8 小时
- 前端页面:2-4 小时
- 单元测试:0.5-2 小时
只输出 JSON。"""


def build_estimate_hours_prompt(tasks: list) -> str:
    import json
    return f"""请估算以下任务的工时:

{json.dumps(tasks, ensure_ascii=False, indent=2)}"""


# ============================================================
# 5. 任务 → 人员分配建议
# ============================================================
ASSIGN_TASKS_SYSTEM = """你是一名项目经理,擅长根据团队成员技能和负载,合理分配任务。

输出 JSON 格式:
{
  "assignments": [
    {
      "task_title": "任务标题",
      "assignee_name": "成员姓名",
      "reason": "分配理由"
    }
  ]
}
分配原则:
1. 任务类型与成员技能匹配
2. 考虑成员当前负载,不要过载
3. 优先把同类型任务给同一个人,减少切换成本
4. 成员列表中 assigned_hours 是已分配工时、remaining_hours 是剩余可分配工时、assigned_tasks 是已分配任务数;
   应优先把任务分给 remaining_hours 更高、assigned_tasks 更少的成员,保持团队负载均衡

严格约束:
- assignee_name 必须从用户提供的团队成员名单中选取,绝对不能编造名单外的名字
- 每个任务都必须分配(assignments 数量 = 任务数量,不能漏分)
- 若任务较多,可通过均匀分配避免单人过载
只输出 JSON。"""


def build_assign_tasks_prompt(tasks: list, members: list) -> str:
    import json
    return f"""请基于团队成员技能和负载,分配以下任务:

任务列表:
{json.dumps(tasks, ensure_ascii=False, indent=2)}

团队成员(含技能与剩余容量):
{json.dumps(members, ensure_ascii=False, indent=2)}"""
