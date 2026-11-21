# 协作规范

本项目为 2 人团队协作开发，所有代码变更需通过分支 + Pull Request 流程合入 `main`。

## 分支命名

| 前缀 | 用途 | 示例 |
|---|---|---|
| `feature/` | 新功能 | `feature/task-kanban` |
| `fix/` | 修 Bug | `fix/estimate-truncation` |
| `docs/` | 文档 | `docs/update-readme` |
| `refactor/` | 重构 | `refactor/llm-client` |

格式：`<前缀>/<简短英文描述>`，分支名用小写和连字符。

## 提交信息规范

采用 Conventional Commits 格式：

```
<类型>: <一句话说明>
```

| 类型 | 说明 |
|---|---|
| `feat` | 新增功能 |
| `fix` | 修复问题 |
| `docs` | 文档变更 |
| `style` | 格式调整（不影响逻辑） |
| `refactor` | 重构 |
| `test` | 测试相关 |
| `chore` | 构建/配置/杂项 |

示例：

```
feat: 任务看板增加状态筛选
fix: 修复工时估算结果为空的问题
docs: 补充部署说明
test: 增加任务拆解接口的单元测试
```

要求：
- 一次提交只做一件事，避免"改了一大堆"的巨型提交
- 说明写清楚做了什么，不要写 `update`、`修改`、`111` 这类无意义信息

## 工作流程

```bash
# 1. 拉取最新代码
git checkout main
git pull origin main

# 2. 从 main 建自己的分支
git checkout -b feature/你的功能名

# 3. 开发并按功能点多次提交
git add <改动的文件>
git commit -m "feat: 具体做了什么"

# 4. 推送到远程
git push origin feature/你的功能名

# 5. 在 GitHub 上发起 Pull Request，由另一人 Review 后合并
```

## 注意事项

1. **绝对不要提交 `backend/.env`**：里面有真实的 API Key，`.gitignore` 已忽略，但 `git add -f` 等强制操作会绕过保护。
2. **不要提交 `node_modules/`、`.venv/`、`instance/`**：都是本地依赖或运行产物。
3. 队友本地首次运行，需按 `README.md` 的「快速开始」建环境，并从 `backend/.env.example` 复制出 `.env` 填自己的 Key。
4. 合并到 `main` 前确保后端 `pytest` 通过。
5. 一人负责的模块尽量集中提交，另一个人 Review 时便于理解。
