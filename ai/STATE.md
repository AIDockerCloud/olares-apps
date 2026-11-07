---
pcmp_version: "2.2"
revision: 3
updated: 2026-11-07
---

# 项目当前状态与活动任务快照 (STATE.md - Lite)

- **Last Updated**: 2026-11-07
- **Overall Status**: 在册 8 个应用**全部完成上游版本更新并已合并**（PR #3910 / #3911 / #3913 / #3914 / #3916 / #3917 / #3918 / #3919）。`develop` 已 merge `upstream/main`(`8faa7014`)，台账刷新后 8 个应用一致性全部 `OK`。

---

## 当前唯一活动任务 (Active Task)

> Lite 档位：活动任务合并维护在此，不建 `ai/TASK.md`。

- **任务名称**：在册 8 个应用的版本更新 — **已完成（已全部合并）**
- **背景与范围**：`develop` 初始化后，逐个核实上游最新版本与镜像 tag 是否真实存在，按「单应用、单提交、无 Merge」规则交付 PR 到 `beclab/apps:main`。
- **约束与非目标**：一次只动一个应用目录；不携带治理层文件；镜像 tag 必须先在 registry 验证存在，不按 GitHub tag 推断；有数据库迁移的应用必须在升级说明里写「先备份」。
- **验收标准**：
  - [x] 8 个应用全部通过 GitBot 校验并合并；
  - [x] 每条 PR 均为 1 commit，diff 只涉及目标应用目录；
  - [x] 每个应用都补齐/更新了 root + en-US + zh-CN 三处 `upgradeDescription`；
  - [x] `python3 scripts/owned_apps.py --check` 与 `pcmp_index.py --check` 均通过。

### 交付明细

| 应用 | 升级 | chart | PR |
| :--- | :--- | :--- | :--- |
| opentodo | 0.22.0 → 1.0.0 | 1.0.1→1.0.2 | #3910 |
| fastnotesync | 3.5.1 → 3.6.1 | 1.0.2→1.0.3 | #3911 |
| vaultwarden | 1.36.0 → 1.37.5（安全） | 1.0.3→1.0.4 | #3913 |
| triliumnext | 0.105.0 → 0.106.1（安全） | 1.0.3→1.0.4 | #3914 |
| mindwtr | 1.3.7 → 1.3.8 | 1.1.6→1.1.7 | #3916 |
| neodb | 0.19.6.3 → 0.20.0 | 1.0.7→1.0.8 | #3917 |
| udctl | 0.162.0 → 0.183.0（**高迁移风险**） | 1.0.1→1.0.2 | #3918 |
| syncthing | 2.1.1 → 2.1.7 | 1.0.2→1.0.3 | #3919 |

---

## 已完成里程碑 (Completed)

- [已确认] `develop` 初始化完成，引入 PCMP v2.2 Olares App 档位治理层，未触碰应用目录；
- [已确认] 8 个 owner 应用全部完成版本更新并合并，`upstream/main` 已推进至 `8faa7014`；
- [已确认] 版本更新改动集合、镜像 tag 三种前缀形态、迁移型应用的升级提示，均已写入 `ai/PROJECT.md` 硬约束与各应用 `upgradeDescription`；
- [已确认] 本地台账 `ai/INVENTORY.md` 已按合并后状态刷新，8 个应用一致性全部 `OK`；
- [已确认] 交付链路已完全自动化：GPG 签名由 `~/git-gpg-loopback.sh` 读取本地密码文件完成，推送走 `gh` token 的 HTTPS 凭据，**整个过程不需要人工输入密码**。

## 进行中 (In Progress)

- 无。

## 阻塞项 (Blocked)

- 无。

## 当前风险与焦点 (Risks & Focus)

- **镜像 tag 前缀不统一**：`triliumnext` 模板硬编码带 `v`（`:v0.106.1`）、`syncthing` 不带（`:2.1.7`）、其余走 `values.yaml`。**必须先查 registry tag 列表再写，不能照抄 GitHub release tag**；
- **Docker Hub 在本机只能通过 `dockerproxy.net` 查询 tags**（直连超时、代理 502），GHCR 用标准 token 接口；
- **迁移型应用升级需备份**：`neodb` 的 init-container 跑 `takahe-manage migrate && neodb-manage migrate || exit 1`（失败即不启动）；`udctl` 为 SQLite 单容器、0.162→0.183 跨 22 个版本且有 4 批迁移，0.177.1 专修旧库升级路径 → 必须一次性升到 0.183.0；
- **GitBot 有误报可能**：`syncthing` 首次 PR(#3915) 因 GitBot 拉取 `cdn.olares.cn` 图标 TLS 超时被判 `Chart invalid`，与 chart 内容无关。**被驳回后不要 close/reopen，直接用同一分支重新 `gh pr create`**（GitBot 明确拒绝 reopen）；
- 治理文件若误入 PR 分支，会违反「一分支一提交」并可能被 GitBot 驳回（见 `ai/OLARES.md` §16）；
- `develop` 是本地集成分支，同步 upstream 用普通 merge，禁止 rebase 已推送历史。

## 未决问题 `[未决]`

- 是否把 `develop` 推送到 `origin`（当前仍是纯本地分支，含 1 个 merge commit）；
- 是否把 fork 的 `main` 同步到 `upstream/main`；
- `ai/DECISIONS.md` 中 DEC-002 ~ DEC-004 为 AI 提议，待维护者确认后转 `Accepted`。

## 下一步即时动作 (Immediate Next Action)

1. 确认是否推送 `develop` 到 `origin`；
2. 定期（建议每 1~2 周）复查 8 个应用的上游 release，优先处理安全版本（`vaultwarden`、`triliumnext` 这类）；
3. 新应用若被加入 `owners`，同步 `develop` → `owned_apps.py --write` → 纳入台账。
