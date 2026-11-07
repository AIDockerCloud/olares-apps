# AIDockerCloud owner 应用清单 (INVENTORY.md)

> `[事实]` 本文件由 `scripts/owned_apps.py` 从工作区扫描生成，**请勿手工编辑**。
> 唯一判定依据：`<app>/owners` 的列表中包含 `AIDockerCloud`。
> 刷新：`python3 scripts/owned_apps.py --write`；核对：`python3 scripts/owned_apps.py --check`。
> 权威基线：`upstream/main`（remote `upstream` = https://github.com/beclab/apps）。

- 在册应用数：**8**
- 扫描范围：仓库一级子目录下全部 `<app>/owners`
- 「镜像版本」列取 `values.yaml` 的 `image.tag` 或 `image.version`（多镜像取第一个业务镜像）
- `CHECK` 行表示版本字段存在差异，需人工对照同类应用核实（不一定是错误）

| 应用 | chart 版本 | metadata.version | appVersion | versionName | 镜像版本 | 一致性 | 最近提交 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| fastnotesync | 1.0.2 | 1.0.2 | 3.5.1 | 3.5.1 | 3.5.1 | OK | `a641ae8a` |
| mindwtr | 1.1.6 | 1.1.6 | 1.3.7 | 1.3.7 | 1.3.7-r2 | OK | `607d24ae` |
| neodb | 1.0.7 | 1.0.7 | 0.19.6.3 | 0.19.6.3 | 0.19.6.3 | OK | `352a61c3` |
| opentodo | 1.0.1 | 1.0.1 | 0.22.0 | 0.22.0 | 0.22.0 | OK | `db41592d` |
| syncthing | 1.0.2 | 1.0.2 | 2.1.1 | 2.1.1 | 2.1.1 | OK | `35e0da12` |
| triliumnext | 1.0.3 | 1.0.3 | 0.105.0 | 0.105.0 | 0.105.0 | OK | `bf864a84` |
| udctl | 1.0.1 | 1.0.1 | 0.162.0 | 0.162.0 | 0.162.0 | OK | `3692e296` |
| vaultwarden | 1.0.3 | 1.0.3 | 1.36.0 | 1.36.0 | 1.36.0 | OK | `03428a86` |

## 判定与维护规则

1. `[规定]` 应用范围只看 `owners` 文件；本清单之外的应用一律视为只读基线。
2. `[规定]` upstream 合并了 `Add AIDockerCloud to owners list` 或版本更新提交后，
   同步 `develop` 并重跑 `--write`，再执行 `--check` 确认清单与实物一致。
3. `[规定]` 交付 PR 一次只涉及本清单中的一个应用目录，且不携带治理层文件。
4. `[事实]` 版本更新至少涉及 5 个文件（见 [../DEVELOP.md](../DEVELOP.md) §5）；镜像版本字段有 `image.tag` 与 `image.version` 两种写法，
   且部分应用把镜像版本硬编码在 `templates/`，改版本前用 `grep -rn "<旧版本>" <app>/` 全目录检索。
5. `[建议]` `CHECK` 表示版本字段存在差异，动字段前先在本仓库找同类应用对照，不要凭记忆补值。
