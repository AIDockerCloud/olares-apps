---
pcmp_version: "2.2"
revision: 1
updated: 2026-11-07
---

# 架构与技术决策记录 (DECISIONS.md - Lite)

> 未经人类确认的方案一律标 `Proposed`。状态变更须提出新 DEC 并注明 `Supersedes`，不得隐式推翻。

## DEC-001 — 采用 PCMP v2.2 Lite + Olares App 定制档初始化 develop 分支
日期: 2026-11-07 | 状态: Accepted
- 确认来源: inverstar 于 2026-11-07 会话中明确要求「从 main 开 develop 分支，利用 Inverstar/PCMP 的 olares-app-develop 分支进行初始化，用于 AIDockerCloud owner 项目的版本更新或 bugfix」
- Supersedes: 无
- Superseded-by: 无
- 复审触发条件 (Review Trigger): PCMP 协议主版本升级，或维护场景从「版本更新 / bugfix」扩展到新增应用 / 团队协作时复审
- 背景 (Context): 该 fork 需长期维护多个应用的版本迭代，跨会话容易丢失范围判定、字段写法与提交规范；PCMP 的 olares-app 分支正好提供 Olares 平台红线与提交规定。
- 决策 (Decision): 引入 PCMP v2.2 协议原版（中英双语）+ Lite 四件套 + `ai/OLARES.md` 平台事实卡 + 可选工具（`scripts/pcmp_index.py`、`skills/pcmp/`），并按 fork / monorepo 场景改写 `AGENTS.md`、`ai/PROJECT.md`；治理层作为新增文件只落在 `develop`。
- 理由 (Reason): 维护期单人场景无需 Full 档位的 TASK/PLAN/sessions，Lite 已足够；Olares App 定制档把 19 条可判定红线固化为硬约束，可避免 AI 凭记忆生成 manifest 字段导致 GitBot 驳回。
- 备选方案 (Alternatives): PCMP Full（治理通胀，维护期收益低）；只写一份 README（AI 不会主动读，约束力弱）；直接照搬模板不改（模板假设单应用单仓库，与本 fork 结构冲突）。
- 影响 (Consequences): 仓库根目录多出治理文件，须严格与 upstream PR 隔离；`ai/OLARES.md` 属外部事实层，Olares 大版本更新后需复核。

## DEC-002 — develop 以 main 为起点并快进到 upstream/main 作为权威基线
日期: 2026-11-07 | 状态: Proposed
- 确认来源: 待 inverstar 确认（2026-11-07 会话中由 AI 提议，尚未批准）
- Supersedes: 无
- Superseded-by: 无
- 复审触发条件 (Review Trigger): fork 的 main 与 upstream/main 长期保持同步，或维护流程改为直接从 upstream/main 切分支时复审
- 背景 (Context): 初始化时 fork 的 `main` 停在 `db41592d`，只有 1 个应用把 AIDockerCloud 列入 owners；`upstream/main`(`0e96ff72`) 已有 8 个，且 main 是其祖先（0 ahead / 9 behind）。
- 决策 (Decision): `develop` 从 `main` 开出后执行 `git merge --ff-only upstream/main`，以完整 8 个应用作为首次盘点基线；`main` 分支保持不动。
- 理由 (Reason): 不同步则清单残缺，无法开展「对项目进行版本更新」这一用途；ff 无冲突、无历史改写、可完全回退。
- 备选方案 (Alternatives): 严格只基于旧 main（清单只有 1 个应用，需后续手工补 7 个提交）；先把 main 也快进（改动用户未要求的分支，风险更高）。
- 影响 (Consequences): `develop` 领先 fork `main` 9 个上游提交；推送 `develop` 到 origin 时会一并带上这些同步提交，需用户知悉。

## DEC-003 — 治理文件与 upstream PR 分支严格隔离
日期: 2026-11-07 | 状态: Proposed
- 确认来源: 待 inverstar 确认（2026-11-07 会话中由 AI 提议，尚未批准）
- Supersedes: 无
- Superseded-by: 无
- 复审触发条件 (Review Trigger): GitBot 校验规则调整，或确认治理文件不影响单应用 PR 审核时复审
- 背景 (Context): PCMP §12 与模板禁区要求「与 upstream/main 只差 1 个 Commit、不夹带其他应用变更」。本仓库的治理层是跨应用的仓库级文件，一旦进入 PR 分支即破坏该约束。
- 决策 (Decision): `AGENTS.md`、`DEVELOP.md`、`ai/`、`PROJECT_CONTEXT*.md`、`skills/`、`scripts/` 只存在于 `develop`；所有交付 PR 从干净的 `upstream/main` 切 `feature/<app>-v<version>`，单应用、单提交、无 Merge。
- 理由 (Reason): 把「集成分支」与「交付分支」职责分开，既保留长期上下文，又保证分发侧审核可预期。
- 备选方案 (Alternatives): 治理文件不纳入 git（跨机器不可用、无法审计）；把治理文件一起提 PR（大概率被 GitBot 驳回）。
- 影响 (Consequences): 每次交付需在两分支间切换；`develop` 允许 merge commit，PR 分支严禁 merge commit，须写入 `AGENTS.md` 与 `DEVELOP.md` 反复约束。

## DEC-004 — 应用范围以 owners 文件判定，清单由脚本核对
日期: 2026-11-07 | 状态: Proposed
- 确认来源: 待 inverstar 确认（2026-11-07 会话中由 AI 提议，尚未批准）
- Supersedes: 无
- Superseded-by: 无
- 复审触发条件 (Review Trigger): owners 文件格式变更、新增批量归属调整，或清单规模超过人工可核对范围时复审
- 背景 (Context): 「owner 含有 AIDockerCloud 的项目」需要一个可机器判定的定义；人工维护清单会随 upstream 合并漂移。
- 决策 (Decision): 以 `<app>/owners` 是否包含 `AIDockerCloud` 为唯一判定依据，`scripts/owned_apps.py` 扫描生成 `ai/INVENTORY.md`，`--check` 校验清单与实物一致；脚本仅用 Python 3 标准库。
- 理由 (Reason): owners 是 GitBot 认可的分发控制文件，语义明确；清单可随时重建，符合 PCMP「Markdown 权威、派生可重建」原则。
- 备选方案 (Alternatives): 按镜像仓库或 PR 作者判定（边界模糊、无法自动核对）；纯手工维护清单（易漂移）。
- 影响 (Consequences): upstream 每次新增/移除 owner 后都需重跑脚本刷新清单；脚本解析为轻量文本扫描，若 YAML 写法大幅变化需同步调整。
