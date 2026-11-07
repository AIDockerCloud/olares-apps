# 工程智能体规范 (AGENTS.md — AIDockerCloud/olares-apps · develop)

> 本文件只对 `develop` 本地集成分支生效。向 `beclab/apps` 提交 PR 时，PR 分支**不得**包含本文件及本仓库其余治理文件。

## 项目定位

本仓库是 Olares Market 官方应用仓库 `beclab/apps` 的 fork，单仓库内含约 400 个 OAC 应用包。
`develop` 分支的用途**仅限**：对 `owners` 文件中包含 `AIDockerCloud` 的应用做**版本更新**与 **bugfix**。
上下文按 **PCMP v2.2 Lite + PCMP for Olares App** 档位管理。

## 关键路径

| 用途 | 路径 |
| :--- | :--- |
| 协议原版 | `PROJECT_CONTEXT_ZH.md` / `PROJECT_CONTEXT.md` |
| 项目硬约束（动工前必读） | [ai/PROJECT.md](ai/PROJECT.md) |
| Olares 平台事实卡与提交规定 | [ai/OLARES.md](ai/OLARES.md)（§14 已登记参考仓库路径） |
| 状态与唯一活动任务 | [ai/STATE.md](ai/STATE.md) |
| 决策真源（ADR） | [ai/DECISIONS.md](ai/DECISIONS.md) |
| 在册应用清单 | [ai/INVENTORY.md](ai/INVENTORY.md)（脚本生成/核对） |
| 人类操作手册与 SOP | [DEVELOP.md](DEVELOP.md) |
| 可选工具 | `scripts/owned_apps.py`、`scripts/pcmp_index.py`、`skills/pcmp/` |

## 接管必读顺序

`PROJECT_CONTEXT_ZH.md` → `ai/PROJECT.md` → `ai/STATE.md` → `ai/DECISIONS.md`（Accepted 项）→ `ai/INVENTORY.md`。
Lite 档位不建 `ai/TASK.md`，当前唯一活动任务合并维护在 `ai/STATE.md`。

## 智能体协作守则

1. **先读再动**：按接管必读顺序建立上下文，严禁仅凭状态摘要推测硬约束，严禁通读全部历史会话反推现状；
2. **先同步基线**：动手前 `git fetch upstream`，以最新 `upstream/main` 为字段与结构基线；所有 manifest/template 写法一律从本仓库同类应用对照得出；
3. **先定范围**：只改 `ai/INVENTORY.md` 列出的应用目录；判定依据是 `<app>/owners` 是否含 `AIDockerCloud`，用 `python3 scripts/owned_apps.py --check` 复核清单未漂移；
4. **改配置先查事实卡**：任何 `OlaresManifest.yaml`、`Chart.yaml`、`templates/` 的改动，先对照 `ai/OLARES.md` 对应章节；
5. **成组修改**：版本更新固定涉及 5 个文件（`Chart.yaml`、`OlaresManifest.yaml`、`i18n/en-US/OlaresManifest.yaml`、`i18n/zh-CN/OlaresManifest.yaml`、`values.yaml`），字段清单见 `DEVELOP.md`，禁止只改一处；
6. **提交隔离**：PR 分支必须从干净的 `upstream/main` 切 `feature/<app>-v<chart版本>`（`<chart版本>` 是 `Chart.yaml:version` 小版本 +1，**不是上游软件版本**），与 upstream 只差 1 个 Commit，不带治理文件、不带其他应用、不引入 Merge 提交；一次性临时分支，PR 合并后删除；
7. **版本与说明同步**：`[UPDATE][<folder>][<chart-version>]<Title>`；bugfix 递增 chart 小版本号并同步中英双语 `upgradeDescription`；
8. **决策留痕**：权限范围、鉴权级别、镜像来源、分类选择、规范版本基线等变更，须在 `ai/DECISIONS.md` 追加 ADR 并附确认来源，未经确认标 `Proposed`；
9. **收尾**：跑 `python3 scripts/pcmp_index.py --check` 与 `python3 scripts/owned_apps.py --check`，递增 `ai/STATE.md` 的 `revision`，更新完成项与即时下一步；
10. **外部动作需授权**：不推送远端、不直接向 upstream 提 PR、不代执行需要 sudo 的命令，除非人类明确授权。

## 动作禁区

以下操作未经人类明确授权一律不做：

1. **不无参考地写配置**：不凭「官方应该是这样」补全任何未核实的字段或目录结构；
2. **不改 `owners` 文件**：它是应用范围的判定依据，且属 GitBot 关注的分发控制文件；
3. **不扩大安全边界**：不把 `authLevel` 改为 `public`，不扩大 `permission` 申请范围，不加 `privileged`；
4. **不碰分发控制文件**：不创建或提交 `.suspend`、`.remove`；
5. **不猜规范版本**：`olaresManifest.version` 与 `apiVersion` 未核实前先报 `[未决]`；
6. **不顺手「修正」无关字段**：存量应用存在旧分类取值等历史写法，非本次任务范围不得改动；
7. **不使用不合格图标**：不接受非 256×256 或超过 512 KB 的图标，不引用临时图床；
8. **不硬编码注入值**：用户名、域名、存储路径、中间件凭据一律引用 `.Values.*` 注入；
9. **不用浮动镜像标签**：不引入 `latest` 或未固定 digest 的镜像；改 tag 时同步 digest；
10. **不为改配置重建镜像**：上游缺陷优先用 `/patch` + `sitecustomize.py` 运行时 Hook；
11. **不污染 PR 分支**：不夹带其他应用变更、不引入 Merge 提交、不携带 `AGENTS.md` / `DEVELOP.md` / `ai/` / `PROJECT_CONTEXT*.md` / `skills/` / `scripts/`；
12. **不改清单之外的应用目录**：清单外应用一律视为只读基线；
13. **不扩大审阅范围**：不主动扫描或批量审阅清单外的工程目录。

## 遇到冲突时

官方文档与真实应用仓库不一致时（典型如 `olaresManifest.version`、`apiVersion`、`categories`），以 `ai/OLARES.md` §13 处理：以目标 OS 版本可安装的真实应用为基线，并向人类报告差异，不自行二选一。
