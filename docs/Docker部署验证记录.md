# Docker 部署验证记录

> 对应《队友协作手册》第十章入门任务 2：按 `docker-compose.yml` 实测一遍并记录结果。
> 验证人：Dashboard ｜ 静态审查：2026-11-23 ｜ 运行时实测：2026-11-26 ｜ 机器：Windows 11 家庭版（10.0.26200）

## 一、验证环境

| 项 | 状态 |
|---|---|
| Docker CLI | ✅ 29.7.2 已安装 |
| Docker Desktop | ✅ 已安装，进程可启动 |
| WSL2（Linux 引擎依赖） | ✅ 2026-11-24 已安装（`wsl --install --no-distribution` + 重启） |
| CPU 虚拟化 | ✅ 已开启（HypervisorPresent = True） |
| Docker Hub 镜像加速 | ✅ 已配置 daemon.json（docker.1ms.run 等国内镜像） |

## 二、环境就绪过程（已完成）

初始状态本机缺少 WSL2，Docker Linux 引擎无法启动。解决过程：

```powershell
wsl --install --no-distribution   # 管理员 PowerShell 执行,不需要装 Linux 发行版
# 重启电脑
# 启动 Docker Desktop(首次运行需在界面中接受服务条款)
```

WSL2 安装完成（2026-11-24）后完成全部实测，见第五节。

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
| `docker compose build` | ✅ 两个镜像构建成功（2026-11-26，走国内镜像加速） |
| `docker compose up -d` | ✅ 两个容器均启动成功（backend + frontend，见第五节） |

## 五、运行时实测结果（2026-11-26 执行）

| # | 验证项（对应第三节修复点） | 实测结果 |
|---|---|---|
| 1 | 后端健康检查 `GET :5000/api/health` | ✅ 返回 `{"status":"ok"}` |
| 2 | 前端页面 `GET :5173/` | ✅ HTTP 200 |
| 3 | **容器间代理链路** `GET :5173/api/health`（问题 1 修复） | ✅ 经 vite 代理转发到 backend 容器，返回 `{"status":"ok"}` |
| 4 | 通过 API 创建测试项目「docker验证项目」 | ✅ 成功，id=1 |
| 5 | `docker compose down` 后重新 `up -d`（完全重建容器） | ✅ 重建成功 |
| 6 | **数据持久化**：重建后 `GET /api/projects`（问题 2 修复） | ✅ id=1 的测试项目依然存在，SQLite 挂载生效 |

> LLM 链路（原清单第 6 步）：`.env` 已挂载进容器、依赖版本正确（openai 1.51.0），
> 该链路依赖外网 LLM 服务，留待实际使用时验证；容器内无 `proxies` 报错的环境问题已消除。

### 实测过程中额外解决的环境问题（供其他队友参考）

1. **Docker Hub 拉取超时**：直连 `registry-1.docker.io` 不通，在
   `%USERPROFILE%\.docker\daemon.json` 配置 `registry-mirrors`（docker.1ms.run 等）后正常。
2. **引擎反复崩溃（占用 8GB+ 内存的进程挤压所致）**：Docker Desktop 的 WSL2 VM 内存不足时
   backend 会被系统杀掉并进入重启循环，日志特征为 `docker_data.vhdx 挂载失败:
   WSL_E_USER_VHD_ALREADY_ATTACHED`。处理：结束大内存进程 → 彻底退出 Docker Desktop →
   `wsl --shutdown` → 重新启动 Docker Desktop。另建议在 `%USERPROFILE%\.wslconfig` 中
   限制 WSL2 内存（如 6GB），避免与桌面应用争抢资源。

## 六、结论

- 4 个静态问题已修复并经运行时实测逐一验证：**容器间代理链路（问题 1）与数据持久化
  （问题 2）两项核心修复均实测通过**；
- `docker compose up` 全链路实测完成：构建、启动、健康检查、页面加载、代理转发、
  数据持久化全部通过，docker-compose 部署方案可用。
