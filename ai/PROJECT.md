# 项目核心定义 (PROJECT.md)

> 硬约束文件。本仓库是 fork / monorepo，与 PCMP for Olares App 模板默认的「单应用单仓库」不同，下文第 1、2、15、16 条为项目定制。详细依据见 [OLARES.md](OLARES.md)，操作 SOP 见 [../DEVELOP.md](../DEVELOP.md)。

## 1. 项目定位与宗旨

- **仓库**：`AIDockerCloud/olares-apps`，官方 `beclab/apps` 的 fork，单仓库约 400 个 OAC 应用包；
- **分支**：`develop`（本地集成分支，唯一允许承载治理层与多提交的分支；`main` 只作 fork 镜像，不在此累加工作）；
- **用途**：对 `owners` 含 `AIDockerCloud` 的应用进行**版本更新**与 **bugfix**，产出可合入 `beclab/apps:main` 的单应用 PR；
- **治理**：PCMP v2.2 **Lite + Olares App 定制档**（`AGENTS.md` + `PROJECT.md` + `STATE.md` 含活动任务 + `DECISIONS.md` + `OLARES.md` 事实卡）；
- **目标运行环境**：Olares OS / Olares Market，OAC 打包分发。

## 2. 核心目标 (Scope)

- 维护 [INVENTORY.md](INVENTORY.md) 在册应用（截至 2026-11-07 为 8 个）；
- **版本更新**：跟随上游软件发版，成组修改版本字段、镜像 tag/digest 与中英双语升级说明；
- **bugfix**：修复 OAC 配置或运行时缺陷，递增 chart 小版本；
- 保证每个交付 PR 与 `upstream/main` 只差 1 个 Commit，符合 GitBot 校验。

## 3. 明确非目标 (Non-Goals)

- 不新增应用（`[NEW]` 不在本分支范围，除非人类明确授权）；
- 不改动 `owners` 不含 `AIDockerCloud` 的应用；
- 不做 Olares 系统级改造，不整目录复制其他应用而不做适配；
- 不把治理层文件带进 upstream PR，不把 `develop` 直接作为 PR 源分支；
- 不申请超出功能所需的用户目录与网络权限。

## 4. 不得违反的硬约束 (Hard Boundaries)

违反任一条即导致安装失败、GitBot 驳回、权限越界或 PR 被污染。

### 4.1 参考基线与范围

1. **先有基线再动手**：本地工作区 `/home/inverstar/ai/github.com/AIDockerCloud/olares-apps` 同时是参考仓库（登记见 [OLARES.md](OLARES.md) §14）；remote `upstream` 指向 `beclab/apps`，`upstream/main` 为字段与结构的权威基线。字段写法一律从本仓库同类应用对照得出，禁止凭记忆生成。
2. **范围由 owners 判定**：只处理 `<app>/owners` 含 `AIDockerCloud` 的应用；清单由 `scripts/owned_apps.py` 生成，改动前后用 `--check` 核对未漂移；一次 PR 只涉及一个应用目录。

### 4.2 元数据与结构对齐

3. **四名一致**：应用目录名 == `Chart.yaml:name` == `metadata.name` == `metadata.appid`。
4. **版本多处同步**：`Chart.yaml` 的 `version` ↔ `OlaresManifest.yaml` 的 `metadata.version` ↔ 提交信息中的 chart 版本；`Chart.yaml` 的 `appVersion` ↔ `spec.versionName` ↔ `values.yaml` 的 `image.tag`。
5. **镜像版本锁定**：`image.tag` 禁 `latest`，须为具体上游版本；带 `digest` 的应用改 tag 时必须同步 digest。**tag 必须先在 registry 验证存在，禁止用 GitHub release tag 推断镜像 tag** —— 两者前缀规则不同（实证：`syncthing` 的 GitHub tag 是 `v2.1.7`，镜像只有 `2.1.7`；`triliumnext` 反之，镜像 tag 是 `v0.106.1`）。`docker.io` 的 tag 列表在本机只能经 `https://dockerproxy.net/v2/<owner>/<repo>/tags/list` 获取（直连超时、走代理 502），GHCR 用标准 token 接口。
6. **必备文件齐全**：`i18n/zh-CN`、`i18n/en-US`、`owners`、`.helmignore` 缺一不可。

### 4.3 版本更新 / bugfix 的字段清单 `[事实]`

> 实证来源：upstream 提交 `0e96ff72`（`[UPDATE][agentj][0.2.20] Agent J 0.28.2`），共改 5 个文件。

7. **五文件基线，但以目标应用真实结构为准**：`Chart.yaml`、`OlaresManifest.yaml`、`i18n/en-US/OlaresManifest.yaml`、`i18n/zh-CN/OlaresManifest.yaml`、`values.yaml` 是提交 `0e96ff72` 的实际改动集合；**镜像版本写法不统一，实测存在三种形态**，改版本前必须 `grep -rn "<旧版本>" <app>/` 全目录检索，禁止照抄五文件清单漏改：

   | 形态 | 应用 | 镜像 tag 落在哪 |
   | :--- | :--- | :--- |
   | `image.tag`（无引号 / 带引号） | `syncthing`、`udctl`、`mindwtr`、`agentj` | `values.yaml`，模板引用 `.Values.image.tag` |
   | `image.version` | `fastnotesync`、`vaultwarden` | `values.yaml` **有该字段但模板不引用**，真实 tag 硬编码在 `templates/*.yaml` 的 `image:` 行，**两处都要改** |
   | 嵌套多镜像 | `neodb`（`image.neodb.tag`）、`triliumnext` | `values.yaml` 嵌套结构，模板引用 `.Values.image.<key>.tag`；边车镜像（typesense / busybox）不得顺手改动 |

   注意 `triliumnext` 模板硬编码的 tag **带 `v` 前缀**而 `values.yaml` 里的不带，两处各自沿用既有写法，不要"统一"成一种。
8. **chart 版本递增**：`Chart.yaml:version` 与 `metadata.version` 必须同时 +1（小版本），bugfix 亦然；`upgradeDescription` 三处（根 manifest + 双语 i18n）必须同步，中文不得留空或沿用旧文案。**若本次升级涉及数据库迁移、启动期配置校验变严或破坏性变更，必须在说明里写明「先备份」与「先升服务端再升客户端」**（实证：`neodb` 的 migration init-container 迁移失败即不启动；`udctl` 跨 22 个版本有 4 批迁移且 `0.177.1` 专修旧库升级路径；`vaultwarden 1.37.5` 起非法配置值会直接阻止启动）。
9. **应用自定义字段**：`values.yaml` 内的 `image.version`、应用自定义 `version` / `wheelSha256` 等派生字段，以及 `templates/` 中硬编码的镜像行，须与上游版本对齐，不可只改一处 tag。

### 4.4 展示元数据

10. **图标严格合规**：`metadata.icon` 与 `entrances[*].icon` 均须 256×256、≤ 512 KB 的 PNG/WEBP 公网直链。
11. **分类白名单**：新增取值只能取 `agents` / `developer` / `homelab` / `models` / `workspace`；存量旧取值属历史写法，非本次任务范围不得顺手改动。

### 4.5 安全与运行时

12. **第三方镜像禁 Root**：非 `beclab` 镜像禁止 `runAsUser: 0`，统一 UID 1000 + `runAsNonRoot: true`；权限修复只走 `beclab/aboveos-busybox` initContainer。
13. **禁止硬编码系统注入值**：用户名、域名、存储路径、中间件地址与凭据一律引用 `.Values.bfl.*` / `.Values.userspace.*` / `.Values.postgres.*`。
14. **Nginx 非 root 五挂载齐全**：`/etc/nginx/conf.d`、`/var/lib/nginx`（预建子目录）、`/var/log/nginx`、`/run`、`/etc/nginx/sites-enabled`（空 emptyDir 遮蔽 80 端口站点）；业务端口非特权，容器端口 == Service `port`/`targetPort` == `entrances[*].port`。
15. **权限与鉴权最小化**：`permission` 只声明实际需要的目录；`authLevel` 保持 `private` / `internal`，改 `public` 必须有 ADR。

### 4.6 分支与分发

16. **PR 分支干净且单一**：从最新 `upstream/main` 切 `feature/<app>-v<chart版本>`，与 `upstream/main` 只差 1 个 Commit，无 Merge 提交；提交信息 `[UPDATE][<folder>][<chart-version>]<Title>`。分支名与提交信息里的版本都是 **chart 版本**（`Chart.yaml:version` / `metadata.version`），小版本 +1，**不是上游软件版本**；上游版本只写进 `appVersion` / `spec.versionName` / `image.tag`。一次性临时分支，PR 合并后删除。
17. **治理文件与 PR 隔离**：`AGENTS.md`、`DEVELOP.md`、`ai/`、`PROJECT_CONTEXT*.md`、`skills/`、`scripts/` 只存在于 `develop`，禁止进入 PR 分支；`develop` 允许 merge commit，PR 分支不允许。
18. **规范版本不靠猜**：`olaresManifest.version` 与 `apiVersion` 以目标 OS 版本可安装的真实应用为基线，冲突按 [OLARES.md](OLARES.md) §13 处理。
19. **分发文件不得误动**：`owners` 变更须经维护者确认；严禁为调试提交 `.suspend` / `.remove`；不扩大审阅范围到清单外应用。
20. **GitBot 驳回后的处置**：先分辨是 chart 问题还是 bot 侧故障 —— GitBot 拉取 `metadata.icon` 等外链超时会被误报成 `Chart invalid ... safefetch: TLS handshake timeout`，此时用 `git diff -U0` 确认对应行未被修改、并在本地 `curl -I` 复测该 URL 即可排除。确认是误报后**不要 `close` + `reopen`**：GitBot 会回复 `Please create a new PR instead of reopening this PR.` 并把 PR 保持在 CLOSED；正确做法是**用同一分支重新 `gh pr create`**，检查会重跑且旧 PR 无需处理。实证：`syncthing` #3915 误报 → reopen 被拒 → 新建 #3919 一次通过。

## 5. 工作流摘要

`git fetch upstream` → 核对 [INVENTORY.md](INVENTORY.md) 选定单个应用 → 从 `upstream/main` 切 `feature/<app>-v<chart版本>` → 按 §4.3 成组改文件（以目标应用真实结构为准）→ `helm template <app>` → 单 Commit → PR 到 `beclab/apps:main` → 合并后同步回 `develop`、刷新清单与 `STATE.md` → 删除临时分支。多应用排期见 [../DEVELOP.md](../DEVELOP.md) §4.1。

## 6. 本地验证方式

| 检查 | 命令 | 期望 |
| :--- | :--- | :--- |
| 清单一致性 | `python3 scripts/owned_apps.py --check` | 退出码 0，`ai/INVENTORY.md` 与实物一致 |
| 上下文合规 | `python3 scripts/pcmp_index.py --check` | 0 errors（Frontmatter / ADR / 双语 / 脚本镜像） |
| 模板渲染 | `helm template <app>` | YAML 可渲染 |
| 分支洁净度 | `git diff --stat upstream/main...HEAD` | PR 分支只含 1 个应用目录的变更 |
| 提交数量 | `git rev-list --count upstream/main..HEAD` | `1` |
