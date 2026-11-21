# AI 敏捷开发助手(AI Agile Assistant)

> 基于 LLM 的 **PRD → 用户故事 → 任务 → 工时 → 分配** 一键自动化平台
> 毕业实习项目 · 主题:如何用 AI 辅助团队软件开发

## 项目简介

输入需求文档(PRD),系统自动完成敏捷开发前期的人力消耗大、主观性强的环节:
1. **AI 解析功能点** — 从 PRD 抽取功能清单
2. **AI 生成用户故事** — 按 INVEST 原则拆分
3. **AI 拆解开发任务** — 故事 → 前后端/测试/文档任务
4. **AI 估算工时** — 基于任务复杂度
5. **AI 分配任务** — 按成员技能与负载

## 目录结构

```
project/
├── backend/              # Flask 后端
│   ├── app/
│   │   ├── __init__.py   # 应用工厂
│   │   ├── config.py     # 配置(从 .env 读取)
│   │   ├── extensions.py # db / cors
│   │   ├── models/       # SQLAlchemy 模型
│   │   ├── llm/          # LLM 客户端 + Prompt 模板
│   │   ├── services/     # 业务逻辑
│   │   └── api/          # Flask 蓝图(REST 接口)
│   ├── tests/            # pytest 测试
│   ├── requirements.txt
│   ├── Dockerfile
│   └── run.py
├── frontend/             # Vue3 + Element Plus 前端
│   ├── src/
│   │   ├── api/          # axios 封装
│   │   └── views/        # 首页 / 项目详情
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```

## 快速开始

### 后端

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate              # Windows
# source .venv/bin/activate         # Linux/Mac
pip install -r requirements.txt

# 配置 LLM(复制 .env.example 为 .env,填入 API Key)
copy .env.example .env              # Windows
# cp .env.example .env              # Linux/Mac

python run.py
# 访问 http://localhost:5000/api/health
```

### 前端

```bash
cd frontend
npm install
npm run dev
# 访问 http://localhost:5173
```

### Docker 一键启动

```bash
# 在项目根目录创建 .env
echo LLM_API_KEY=your-key-here > .env
docker compose up --build
```

## LLM 配置

支持任何 OpenAI 兼容协议:

| 提供商 | LLM_BASE_URL | LLM_MODEL |
|---|---|---|
| DeepSeek | https://api.deepseek.com/v1 | deepseek-chat |
| 通义千问 | https://dashscope.aliyuncs.com/compatible-mode/v1 | qwen-plus |
| OpenAI | https://api.openai.com/v1 | gpt-4o-mini |

在 `backend/.env` 中配置:
```
LLM_API_KEY=sk-xxx
LLM_BASE_URL=https://api.deepseek.com/v1
LLM_MODEL=deepseek-chat
```

## API 概览

| 方法 | 路径 | 说明 |
|---|---|---|
| POST | /api/projects | 创建项目 |
| GET | /api/projects | 项目列表 |
| POST | /api/requirements | 保存 PRD |
| POST | /api/requirements/{id}/parse | ① AI 解析功能点 |
| POST | /api/stories/generate | ② AI 生成用户故事 |
| POST | /api/tasks/decompose | ③ AI 拆解任务 |
| POST | /api/tasks/estimate | ④ AI 估算工时 |
| POST | /api/tasks/assign | ⑤ AI 分配任务 |
| POST | /api/members | 添加成员 |

## 测试

```bash
cd backend
.venv\Scripts\python.exe -m pytest tests/ -v
```

## AI 辅助开发说明(答辩要点)

本项目严格遵循实习要求:

1. **开发工具采用 AI 辅助**
   - 全程使用 Trae / Cursor / Copilot 编码
   - 报告附 AI 工具使用记录

2. **用 AI 生成代码**
   - 后端 Flask 路由、SQLAlchemy 模型、Prompt 模板大部分由 AI 生成
   - 前端 Vue 组件、表单、看板由 AI 生成
   - 量化:AI 生成代码占比 60%+

3. **用 AI 完成测试**
   - pytest 测试用例由 AI 生成
   - 覆盖健康检查、项目 CRUD、需求、成员、任务流转等

## 技术栈

- 后端:Python 3.11+ / Flask 3.0 / SQLAlchemy 2.0 / openai SDK
- 前端:Vue 3 / Vite 5 / Element Plus / axios
- 数据:SQLite(开发) / Docker(部署)
- LLM:DeepSeek / 通义千问 / OpenAI(可切换)
