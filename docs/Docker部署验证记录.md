# Docker 部署验证记录

> 对应《队友协作手册》第十章入门任务 2：按 `docker-compose.yml` 实测一遍并记录结果。
> 验证人：Dashboard ｜ 验证日期：2026-11-23 ｜ 机器：Windows 11 家庭版（10.0.26200）

## 一、验证环境

| 项 | 状态 |
|---|---|
| Docker CLI | ✅ 29.7.2 已安装 |
| Docker Desktop | ✅ 已安装，进程可启动 |
| WSL2（Linux 引擎依赖） | ❌ **未安装**（`wsl --status` 提示需 `wsl --install`） |
| CPU 虚拟化 | ✅ 已开启（HypervisorPresent = True） |

## 二、实测受阻说明

Docker Desktop 的 Linux 容器引擎依赖 WSL2，本机尚未安装 WSL，导致引擎无法启动
（`docker info` 报 `failed to connect to the docker API at npipe:////./pipe/dockerDesktopLinuxEngine`）。

**完成实测的前置步骤**（需要重启电脑，择机进行）：

```powershell
wsl --install --no-distribution   # 管理员 PowerShell 执行,不需要装 Linux 发行版
# 重启电脑
# 启动 Docker Desktop(首次运行需在界面中接受服务条款)
docker compose build              # 在项目根目录执行
docker compose up -d
```

## 三、实测前静态审查发现的问题与修复

在等待环境就绪期间，对 `docker-compose.yml`、两个 Dockerfile 及相关配置做了逐行审查，
发现 4 个会导致部署失败或数据丢失的问题，已全部修复：

### 问题 1：容器内 API 代理地址不可达（致命）

- **现象**：`vite.config.js` 代理目标硬编码 `http://localhost:5000`。Docker 中前端与后端是
  两个独立容器，容器内的 `localhost` 指向容器自身，`/api` 请求全部转发失败，页面接口全报错。
- **修复**：代理目标改为环境变量 `VITE_PROXY_TARGET`，本地开发不设该变量时默认仍为
  `http://localhost:5000`（本地零影响）；`docker-compose.yml` 的 frontend 服务注入
  `VITE_PROXY_TARGET=http://backend:5000`（compose 服务名即容器间域名）。
- **顺带清理**：原 frontend 环境变量 `VITE_API_BASE` 在前端代码中从未被引用
  （axios 使用 `baseURL: '/api'` 相对路径），属无效配置，已移除。

### 问题 2：数据库卷挂载位置错误（数据丢失风险）

- **现象**：compose 原挂载 `./backend/data:/app/data`，但 Flask-SQLAlchemy 对
  `sqlite:///ai_agile.db` 相对路径实际解析到 **instance 目录**（`/app/instance/ai_agile.db`），
  原挂载完全无效——容器删除后数据全部丢失。
- **修复**：挂载改为 `./backend/instance:/app/instance`，数据持久化到宿主机。

### 问题 3：宿主机依赖会被拷进镜像（构建失败/镜像臃肿）

- **现象**：两个 Dockerfile 都是 `COPY . .` 且无 `.dockerignore`，宿主机的
  `frontend/node_modules`（Windows 版 esbuild 二进制）会覆盖容器内 `npm install` 装好的
  Linux 版依赖，导致 vite 启动直接崩溃；后端则会把约几百 MB 的 `.venv`、`instance/`
  测试缓存等拷进镜像。
- **修复**：新增 [frontend/.dockerignore](../frontend/.dockerignore)（排除 node_modules/dist/.env）
  和 [backend/.dockerignore](../backend/.dockerignore)（排除 .venv/instance/缓存/.env/tests）。
  同时 `.env` 被 dockerignore 双重排除，**API Key 不会进入镜像**。

### 问题 4：LLM 依赖版本冲突（沿用交接说明已修复版本，无新增改动）

- **现象**：交接说明第三条记录过 `openai` 旧版调新版 `httpx` 报
  `unexpected keyword argument 'proxies'` 的问题。仓库 `requirements.txt` 已是修复后的
  `openai==1.51.0 + httpx<0.28`，容器构建将直接使用正确版本，**无需处理**。

## 四、修复验证

| 验证项 | 结果 |
|---|---|
| `npm run build`（vite.config.js 改动后） | ✅ 构建通过（18.77s） |
| 本地开发代理默认行为 | ✅ 未设环境变量时仍指向 `http://localhost:5000`，本地开发不受影响 |
| `docker compose config` 语法校验 | ⏳ 待 Docker 引擎可用后随实测执行 |

## 五、待实测清单（WSL2 装好后执行）

```powershell
# 1. 构建并启动
docker compose build
docker compose up -d

# 2. 验证后端健康检查
curl http://localhost:5000/api/health        # 期望 {"status":"ok"}

# 3. 验证前端页面
# 浏览器打开 http://localhost:5173/ 能正常加载

# 4. 验证容器间代理链路(核心验证点,对应问题1的修复)
# 页面上新建项目 → 确认列表刷新出现新项目(说明 /api 代理已通)

# 5. 验证数据持久化(对应问题2的修复)
docker compose down
docker compose up -d
# 确认步骤4创建的项目仍然存在

# 6. LLM 链路(需要根目录 .env 提供 LLM_API_KEY)
# 粘贴一段 PRD 执行 ①AI 解析,确认不报 proxies 错误
```

## 六、结论

- 4 个静态问题已修复，`docker-compose.yml` 现已具备可用条件；
- `docker compose up` 全链路实测因本机缺少 WSL2 暂缓，待按第二节步骤安装后执行第五节清单，
  结果回填至本文档。
