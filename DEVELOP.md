# develop 分支使用说明

> 面向人类维护者的操作手册。本文件只存在于 `develop`，**禁止进入向 `beclab/apps` 提交的 PR 分支**。
> AI 接管请读 [AGENTS.md](AGENTS.md)；硬约束见 [ai/PROJECT.md](ai/PROJECT.md)；平台事实见 [ai/OLARES.md](ai/OLARES.md)。

## 1. 这条分支是干什么的

`AIDockerCloud/olares-apps` 是 `beclab/apps` 的 fork。`develop` 是**本地集成分支**，只用来维护 `owners` 中含 `AIDockerCloud` 的应用：跟随上游发版、修 OAC 配置缺陷，并把成果以单应用 PR 交付到 `beclab/apps:main`。

治理层（`AGENTS.md`、`DEVELOP.md`、`ai/`、`PROJECT_CONTEXT*.md`、`skills/`、`scripts/`）只在这条分支上，版本更新本身**不产生**在这些文件里。

## 2. 分支拓扑

```text
upstream/main  ───────────────►  feature/<app>-v<version>   （交付分支：单应用、1 Commit、PR 源）
      │                                    │
      │ merge（允许 merge commit）           │ PR → beclab/apps:main
      ▼                                    │
develop  （本地集成：治理层 + 清单 + 多提交） ◄── 合并后同步结果
main     （fork 镜像，本次未改动；落后 upstream 9 个提交）
```

要点：**交付分支永远从干净的 `upstream/main` 切，不从 `develop` 切**。`develop` 允许 merge commit，PR 分支严禁 merge commit。

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

1. `git fetch upstream`
2. `git checkout -b feature/neodb-v1.0.8 upstream/main`（按实际应用与版本命名）
3. 按 §5 成组修改**且只修改**该应用的 5 个文件
4. `helm template <app>` 确认可渲染
5. `git add <app>` 然后单条提交：`git commit -m "[UPDATE][neodb][1.0.8] Upgrade to upstream x.y.z"`
6. `git rev-list --count upstream/main..HEAD` 必须为 `1`
7. `git diff --stat upstream/main...HEAD` 必须只含该应用目录
8. 推送并提 PR（**需人工授权**，AI 不代为执行）
9. PR 合并后同步：`git checkout develop`、`git fetch upstream`、`git merge upstream/main`
10. 刷新清单：`python3 scripts/owned_apps.py --write`，更新 `ai/STATE.md` 并递增 `revision`

**bugfix** 走同一流程：chart 小版本号递增，中英双语 `upgradeDescription` 写明修复项，提交信息仍用 `[UPDATE]`。

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
