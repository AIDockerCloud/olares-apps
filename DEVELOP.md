# develop 分支使用说明

> 面向人类维护者的操作手册。本文件只存在于 `develop`，**禁止进入向 `beclab/apps` 提交的 PR 分支**。
> AI 接管请读 [AGENTS.md](AGENTS.md)；硬约束见 [ai/PROJECT.md](ai/PROJECT.md)；平台事实见 [ai/OLARES.md](ai/OLARES.md)。

## 1. 这条分支是干什么的

`AIDockerCloud/olares-apps` 是 `beclab/apps` 的 fork。`develop` 是**本地集成分支**，只用来维护 `owners` 中含 `AIDockerCloud` 的应用：跟随上游发版、修 OAC 配置缺陷，并把成果以单应用 PR 交付到 `beclab/apps:main`。

治理层（`AGENTS.md`、`DEVELOP.md`、`ai/`、`PROJECT_CONTEXT*.md`、`skills/`、`scripts/`）只在这条分支上，版本更新本身**不产生**在这些文件里。

## 2. 分支拓扑

```text
upstream/main  ───────────────►  feature/<app>-v<chart版本>  （交付分支：单应用、1 Commit、PR 源）
      │                                    │
      │ merge（允许 merge commit）           │ PR → beclab/apps:main
      ▼                                    │
develop  （本地集成：治理层 + 清单 + 多提交） ◄── 合并后同步结果
main     （fork 镜像，本次未改动；落后 upstream 9 个提交）
```

要点：**交付分支永远从干净的 `upstream/main` 切，不从 `develop` 切**。`develop` 允许 merge commit，PR 分支严禁 merge commit。8 个应用不需要 8 条长期分支 —— 每条 feature 分支都是一次性的临时分支，PR 合并后即删。

## 3. 常用命令

```bash
git fetch upstream
git checkout develop
git merge upstream/main
python3 scripts/owned_apps.py
python3 scripts/owned_apps.py --check
python3 scripts/pcmp_index.py --check
```

`owned_apps.py --check` 校验清单与实物是否漂移；`pcmp_index.py --check` 校验 Frontmatter、ADR、双语协议与脚本镜像。两者都应在提交前通过。

## 4. 版本更新 SOP

**分支命名规则（最容易踩坑）**：格式 `feature/<应用名>-v<chart版本>`，`<chart版本>` = `Chart.yaml:version` = `metadata.version`，**不是上游软件版本号**。

- 例：agentj 上游发 0.28.2 → chart 版本定 0.2.20 → 分支 `feature/agentj-v0.2.20`，提交 `[UPDATE][agentj][0.2.20] Agent J 0.28.2`；
- 上游软件版本只写进 `appVersion` / `spec.versionName` / `image.tag`，不进分支名；
- chart 版本取「当前 `Chart.yaml:version` 的小版本 +1」，与上游版本号没有换算关系。

1. `git fetch upstream`
2. `git checkout -b feature/neodb-v1.0.8 upstream/main`（`v1.0.8` 为 chart 版本）
3. 按 §5 成组修改**且只修改**该应用的 5 个文件
4. `helm template <app>` 确认可渲染
5. `git add <app>` 然后单条提交：`git commit -m "[UPDATE][neodb][1.0.8] Upgrade to upstream x.y.z"`
6. `git rev-list --count upstream/main..HEAD` 必须为 `1`
7. `git diff --stat upstream/main...HEAD` 必须只含该应用目录
8. 推送并提 PR（**需人工授权**，AI 不代为执行）
9. PR 合并后同步：`git checkout develop`、`git fetch upstream`、`git merge upstream/main`
10. 刷新清单：`python3 scripts/owned_apps.py --write`，更新 `ai/STATE.md` 并递增 `revision`

**bugfix** 走同一流程：chart 小版本号递增，中英双语 `upgradeDescription` 写明修复项，提交信息仍用 `[UPDATE]`。

### 4.1 多个应用怎么排期

不用给 8 个应用各留一条长期分支，用「**台账驱动 + 一次性临时分支**」：

1. `develop` 上的 [ai/INVENTORY.md](ai/INVENTORY.md) 是唯一台账，先跑 `python3 scripts/owned_apps.py --check` 确认范围没漂移；
2. 从台账挑 **1 个**应用，按 SOP 走完 PR；合并后删掉该 feature 分支；
3. 回 `develop` 同步 upstream（`git merge upstream/main`），`python3 scripts/owned_apps.py --write` 刷新台账，再挑下一个；
4. 每个应用的上游版本各自查（GitHub Releases / 镜像仓库 tag），台账只记**当前**版本，不负责探测新版本。

**想并行也可以**：同时开多条 feature 分支、各提各的 PR，但每条都必须基于当时的最新 `upstream/main`、单应用、单提交。先合并的 PR 会让 upstream/main 前进，后合并的 PR 会显示 out-of-date，此时用 **rebase**（不要 merge，否则引入 Merge 提交违反规范）更新：

```bash
git fetch upstream
git rebase upstream/main
git push --force-with-lease
```

为避免反复 rebase，建议**串行**，或一次最多并行 2~3 个。

## 5. 版本更新要改的 5 个文件 `[事实]`

实证来源：upstream 提交 `0e96ff72`（agentj 0.28.2，5 files changed）。

| 文件 | 字段 | 说明 |
| :--- | :--- | :--- |
| `Chart.yaml` | `version`、`appVersion` | chart 版本 +1；`appVersion` 跟随上游软件版本 |
| `OlaresManifest.yaml` | `metadata.version`、`spec.versionName`、`spec.upgradeDescription` | 与 Chart 对齐；升级说明换成新版内容 |
| `i18n/en-US/OlaresManifest.yaml` | `spec.upgradeDescription` | 英文升级说明，与根 manifest 一致 |
| `i18n/zh-CN/OlaresManifest.yaml` | `spec.upgradeDescription` | 中文升级说明，不得留旧文案 |
| `values.yaml` | `image.tag` **或** `image.version`、`image.digest`、应用自定义 `version` 等 | tag 禁 `latest`；有 digest 必须同步更新 |
| `templates/*.yaml`（部分应用） | 硬编码的 `image: <repo>:<版本>` | fastnotesync / vaultwarden 属于此类，**不在 agentj 的 5 文件集合里** |

**改版本前先全目录检索旧版本号**，避免漏改：

```bash
grep -rn 0.28.2 agentj/
```

把版本号与目录名换成目标应用的实际值（示例为 agentj 当前版本）。清单 [ai/INVENTORY.md](ai/INVENTORY.md) 的「镜像版本」列同时兼容 `image.tag` 与 `image.version` 两种写法。

提交信息格式：`[UPDATE][<foldername>][<chart-version>]<Title>`（例：`[UPDATE][agentj][0.2.20] Agent J 0.28.2`）。

## 6. 红线速查

- 不修改 `owners`（它是范围判定依据，也属分发控制文件）；
- 不创建 `.suspend` / `.remove`；不顺手改无关字段（存量旧 `categories` 取值属历史写法）；
- 一次 PR 只碰一个应用目录，不夹带治理文件、不引入 Merge 提交；
- `olaresManifest.version` / `apiVersion` 以真实可安装应用为基线，不猜；
- 第三方镜像禁 `runAsUser: 0`；Nginx 非 root 五挂载齐全；端口三处一致；
- 改 manifest 前先在本仓库找同类应用对照，不凭记忆补字段。

## 7. 待人工确认 `[未决]`

- 是否把 `develop` 推送到 `origin`（`git push -u origin develop`，会一并带上同步的 9 个 upstream 提交）；
- 是否把 fork 的 `main` 也快进到 `upstream/main`（本次未动 `main`）；
- `ai/DECISIONS.md` 中 DEC-002 ~ DEC-004 为 AI 提议，确认后转 `Accepted`。
