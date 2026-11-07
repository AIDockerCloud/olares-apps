# Olares 平台事实卡与提交规定 (OLARES.md)

本文件是 Olares 应用开发的约束速查。**它不是 PCMP 标准文件，而是本项目定制的领域事实层**：可整篇删除重建，重建依据是文末「信息源」。

## 标注体系

| 标注 | 含义 | 违反后果 |
| :--- | :--- | :--- |
| `[事实]` | 官方文档或真实仓库佐证 | 认知错误，可能导致配置无效 |
| `[规定]` | 本项目强制规定，源自 GitBot 实际拦截行为与提交经验 | PR 被驳回或自动校验失败 |
| `[建议]` | 工程实践，可被人类否决 | 无强制后果 |
| `[未决]` | 存在冲突或尚未核实 | 需先澄清再动手 |

---

## 1. 应用包结构 (OAC)

`[事实]` Olares Application Chart 基于 Helm Chart 扩展。可分发结构：

```text
<foldername>/
├── Chart.yaml                # 必选：Helm 元数据
├── OlaresManifest.yaml       # 必选：Olares 应用配置
├── values.yaml               # 必选：默认参数
├── templates/                # 必选：K8s 资源模板
├── i18n/                     # 必选：国际化清单
│   ├── en-US/OlaresManifest.yaml
│   └── zh-CN/OlaresManifest.yaml
├── owners                    # 必选：无后缀，列 GitHub 账号
├── .helmignore               # 必选：打包排除规则
├── LICENSE                   # 可选
└── README.md                 # 可选
```

`[规定]` `i18n/zh-CN` 与 `i18n/en-US` 必须齐全，内容为可覆盖的 `OlaresManifest.yaml` 片段（通常含 `metadata.description`、`spec.fullDescription`、`spec.upgradeDescription`）。`owners` 与 `.helmignore` 不可省略。

`[事实]` 分发控制文件放在 OAC 根目录，为**空文件**：`.suspend` 暂停分发，`.remove` 从市场移除。

---

## 2. 目录与元数据对齐

`[规定]` 以下四项必须完全一致（全小写、无特殊字符）：

```text
应用目录名 (FolderName) == Chart.yaml:name == metadata.name == metadata.appid
```

`[规定]` 版本号成组对齐，禁止只改一处：

| Chart.yaml | OlaresManifest.yaml |
| :--- | :--- |
| `name` | `metadata.name` |
| `version` | `metadata.version` |
| `appVersion` | `spec.versionName` |

`[规定]` `values.yaml` 的 `image.tag` 严禁 `latest`，必须锁定上游具体版本号，并与 `spec.versionName` 保持一致。

`[事实]` `metadata.name` 须匹配 `^[a-z][a-z0-9]{0,29}$`。
`[事实]` `appid` 只存在于 `metadata`，Chart.yaml 中无此字段。

---

## 3. OlaresManifest.yaml 顶层结构

`[事实]` 顶层键（顺序不敏感，建议按此组织）：

```text
olaresManifest.version   # 规范版本，如 '0.12.0'
olaresManifest.type      # app | recommend | middleware
apiVersion               # 规范大版本，见 §13 漂移说明
workloadReplicas         # 各 Deployment 的副本数（文档未收录，真实应用已用）
metadata                 # name/appid/version/title/description/icon/categories/tags
entrances                # 入口列表，1~10 个：name/host/port/title/authLevel/icon
sharedEntrances          # 可选：供集群内其他应用调用
ports                    # 可选：udp/tcp
permission               # 可选：appData/appCache/userData/provider
spec                     # 必填：展示信息 + 资源配额
middleware               # 可选：postgres/redis/mongo/minio/rabbitmq/mariadb/mysql
options                  # 可选：dependencies/conflicts/apiTimeout/allowedOutboundPorts/oidc
envs                     # 可选：安装时可配置的环境变量（需 OS ≥ 1.12.2）
provider                 # 可选：向其他应用开放接口
tailscale                # 可选：Tailscale ACL 开放端口
```

`[事实]` `authLevel` 三档：

- `public`：互联网任意访问，无鉴权；
- `private`：内外网均需授权（默认值）；
- `internal`：外网需授权，内网免鉴权。

`[事实]` `permission.userData` 是**目录列表**（如 `- Home`），不是布尔值。
`[事实]` 依赖声明在 `options.dependencies`，每项含 `name`/`version`/`type`/`mandatory`；`type: system` 表示对 Olares 系统本体的版本要求。

---

## 4. 图标规范

`[规定]` 图标同时用于 `metadata.icon` 与 `entrances[*].icon`，两项都必须合规：

| 项 | 要求 |
| :--- | :--- |
| 分辨率 | **精确 256×256 像素**，正方形。512×512、1024×1024 或非正方形一律不合格 |
| 体积 | **≤ 524,288 字节（512 KB）** |
| 格式 | PNG / WEBP |
| 地址 | 可公网访问的稳定直链，推荐仓库 raw 链接：`https://raw.githubusercontent.com/<org>/<repo>/main/icon-256.png` |

`[规定]` 图标文件随应用源码仓库维护，不放第三方图床，避免链接失效导致市场展示空白。

---

## 5. 应用分类白名单

`[规定]` `metadata.categories` 严禁自定义名称，只能从以下 5 个已注册分类中选：

```text
agents | developer | homelab | models | workspace
```

`[规定]` 违反即被拦截。`Entertainment`、`Tools`、`Utilities`、`Productivity` 等旧取值不得用于新提交。

`[未决]` 仓库存量应用仍大量使用旧分类（`AI` 117 个、`Productivity_v112` 86 个、`Utilities_v112` 82 个），且部分已合入（如 `udctl` 用 `Productivity_v112 + workspace`）。推断旧分类在过渡期仍被接受，但**新提交一律走白名单**。此判断待 GitBot 规则更新后复核。

---

## 6. 系统注入变量（禁硬编码清单）

`[事实]` 以下变量由 Olares 安装时注入模板，**在 values.yaml 中重复定义会被系统覆盖**，写死无意义且误导维护：

| 用途 | 变量 |
| :--- | :--- |
| 用户名 / 用户域名 | `.Values.bfl.username`、`.Values.user.zone` |
| 入口地址映射 | `.Values.domainMap`（入口名 → URL） |
| 存储路径 | `.Values.userspace.appData`、`.Values.userspace.appCache`、`.Values.userspace.userData` |
| 集群架构 | `.Values.cluster.arch` |
| 应用依赖地址 | `.Values.deps`、`.Values.svcs` |
| PostgreSQL | `.Values.postgres.host` / `.port` / `.username` / `.password` / `.databases.<name>` |
| MongoDB | `.Values.mongo.host` / `.port` / `.username` / `.password` / `.databases.<name>` |
| Redis | `.Values.redis.host` / `.port` / `.password` / `.namespaces.<name>` |

`[事实]` 目前不支持 AMD64 与 ARM 混合集群。
`[事实]` 中间件凭据由系统生成注入，`middleware` 块里填的 `username`/`password` 是申请参数，不是最终凭据——运行时一律读 `.Values.<mw>.*`。

---

## 7. 安全策略与权限

`[规定]` **第三方镜像严禁 Root 特权**。非 `beclab` 镜像绝对禁止配置 `securityContext.runAsUser: 0`，GitBot 会直接阻断报错。第三方镜像统一以 UID 1000 运行：

```yaml
securityContext:
  runAsNonRoot: true
  runAsUser: 1000
```

`[规定]` 数据目录或持久化卷需要修复属主时，**不得给业务容器提权**，改用官方白名单镜像作为 `initContainers`（`beclab` 镜像允许 root）：

```yaml
initContainers:
  - name: fix-permissions
    image: docker.io/beclab/aboveos-busybox:1.37.0
    command:
      - sh
      - -c
      - |
        mkdir -p /data/app /data/cache
        chown -R 1000:1000 /data/app /data/cache
        chmod -R 775 /data/app /data/cache
    volumeMounts:
      - name: app-data
        mountPath: /data
```

`[建议]` `chmod 775` 与 `chown 1000:1000` 成对使用；只 chown 不 chmod 时，若上游镜像以组权限写文件仍可能失败。

---

## 8. Nginx 非 root 运行时

`[规定]` Pod 内用 Nginx 做反代或前后端入口，且以 UID 1000 运行时，以下挂载缺一不可，否则启动即失败：

| 挂载点 | 类型 | 用途 | 缺失后果 |
| :--- | :--- | :--- | :--- |
| `/etc/nginx/conf.d` | emptyDir | 启动时用 `envsubst` 生成反代配置 | 配置不可写 |
| `/var/lib/nginx` | emptyDir | 需预建 `body` `proxy` `fastcgi` `scgi` `uwsgi` 子目录 | 上传或反代大响应报 `mkdir() failed (13: Permission denied)` |
| `/var/log/nginx` | emptyDir | 访问与错误日志 | 日志写入失败 |
| `/run` | emptyDir | 写 `nginx.pid` | 无法写 pid |
| `/etc/nginx/sites-enabled` | **emptyDir（空目录遮蔽）** | 遮蔽发行版自带的 80 端口站点 | `bind() to 0.0.0.0:80 failed (13: Permission denied)` |

`[规定]` `/var/lib/nginx` 的子目录必须在 Nginx 启动前创建，写在启动脚本里：

```sh
mkdir -p /var/lib/nginx/body /var/lib/nginx/proxy /var/lib/nginx/fastcgi \
         /var/lib/nginx/scgi /var/lib/nginx/uwsgi
exec nginx -g 'daemon off;'
```

`[规定]` 业务端口必须是**非特权端口**（如 8000、8080），不得使用 80/443。Debian/Ubuntu 系镜像默认带 `/etc/nginx/sites-enabled/default` 监听 80，仅靠改自定义配置不够，必须用空 emptyDir 遮蔽整个目录。

---

## 9. 架构与前后端协同

`[规定]` 项目同时有 Web 前端与 Server/Cloud 后端两个镜像时，**优先作为单应用统一交付**：单 Pod 多容器 + 内置 Nginx 反代同域转发。

`[规定]` 必须保证 Same-Origin 同域访问，不靠 CORS 解决跨域，使 Web 版与手机/桌面客户端开箱即用。

`[规定]` 端口链路三处一致：

```text
容器 containerPort == Service targetPort == Service port == entrances[*].port
```

`[建议]` Service 名称与 `entrances[*].host` 保持一致，系统据此把入口流量路由到该 Service。

---

## 10. 运行时 Hook 机制

`[规定]` 上游开源镜像存在环境变量解析缺陷（典型：队列/Worker 未读取 Redis 密码）时，**优先用非侵入式运行时 Hook**，不重新构建推送镜像。

做法：ConfigMap 挂载到 `/patch`，设置 `PYTHONPATH=/patch`，用 `sitecustomize.py` 在 Python 启动时动态重写配置模块：

```yaml
env:
  - name: PYTHONPATH
    value: /patch
volumeMounts:
  - name: patch
    mountPath: /patch
```

`[建议]` `sitecustomize.py` 只做最小补丁（补齐缺失环境变量、修正配置读取顺序），不改业务逻辑；Hook 必须能在上游修复后直接删除而不留残留。

---

## 11. 资源与兼容声明

`[事实]` `spec` 资源字段：`requiredMemory` / `requiredDisk` / `requiredCpu` 与 `limitedMemory` / `limitedDisk` / `limitedCpu`，超限时系统可暂停应用。
`[事实]` `supportArch` 取值 `amd64`、`arm64`，需与实际镜像构建架构一致。
`[事实]` `spec.runAsUser: true` 强制以 UID 1000 非 root 运行。
`[事实]` `spec.onlyAdmin: true` 限制仅管理员可安装。

---

## 12. 分发与 PR 规范

`[事实]` 发布走 PR 到官方索引仓库，Terminus-Gitbot 自动校验文件范围、所有权、版本规则，通过后自动合并。

`[规定]` 分支与提交：

1. 基于最新 `upstream/main` 拉独立特性分支，命名 `feature/<app-name>-v<version>`；
2. 特性分支与 `upstream/main` 对比**只能有 1 个 Commit**，严禁夹带其他应用变更或 Merge 提交；
3. Commit 信息与 PR 标题同格式：

| 场景 | 格式 | 示例 |
| :--- | :--- | :--- |
| 新增应用 | `[NEW][<foldername>][<version>]<Title>` | `[NEW][mindwtr][1.0.0]Add Mindwtr application` |
| 迭代修复 | `[UPDATE][<foldername>][<version>]<Title>` | `[UPDATE][neodb][1.0.3]Disable default port 80 listener for non-root Nginx` |

4. Bugfix 重新提 PR 必须递增小版本号（`1.0.1` → `1.0.2`），并同步更新中英文 `upgradeDescription`。

`[事实]` `owners` 文件格式：

```yaml
owners:
- <github-username>
- <collaborator-username>
```

---

## 13. 已知规范漂移 `[未决]`

官方文档与真实应用仓库存在不一致，**不得只信文档**：

| 项 | 官方文档 | 真实仓库（beclab/apps） |
| :--- | :--- | :--- |
| `olaresManifest.version` | 最新 0.11.0 | affine 用 `'0.12.0'`，alist 用 `'0.10.0'` |
| `apiVersion` | 有效值 `v1`/`v2` | affine 用 `'v3'` |
| `workloadReplicas` | 文档未收录 | affine 已使用 |
| `categories` | 分代取值（`Utilities` / `Utilities_v112`） | 新规范为 5 类白名单，存量新旧混用 |

`[建议]` 处理规则：以目标 Olares 版本能实际安装的真实应用为基线，复制其 manifest 骨架再改；兼容范围用 `options.dependencies` 中 `olares` 的 `version` 约束表达，而不是猜规范版本号。

---

## 14. 参考基线仓库

`[规定]` 开工前必须确认一份**本地可读的 `beclab/apps` 仓库路径**（官方仓库或自己的 fork 均可），由人类提供，登记在本节。AI 不得凭记忆写 manifest 字段、目录结构或运行时配置。

```text
参考仓库本地路径：/home/inverstar/ai/github.com/AIDockerCloud/olares-apps
参考仓库来源：    beclab/apps 的个人 fork（AIDockerCloud/olares-apps），remote `upstream` 指向官方仓库
核对日期：        2026-11-07
```

`[规定]` 路径缺失时，AI 必须先向人类索取，再动手写配置；不得以"我记得官方是这样"为由跳过。

`[规定]` 用法固定为「找同类应用对照」，而不是通读全仓：

| 场景 | 做法 |
| :--- | :--- |
| 新增应用 | 找 2~3 个功能相近的应用，对照其 `OlaresManifest.yaml`、`templates/`、`i18n/` 结构 |
| 报错修复 | 在参考仓库中检索相同报错涉及的关键字（如 `sites-enabled`、`initContainers`、`runAsUser`），看同类应用如何规避 |
| 规范版本存疑 | 优先信参考仓库里能正常安装的应用，其次才是官方文档（见 §13） |

`[规定]` 参考仓库是**只读基线**。不得直接修改参考仓库中的其他应用，也不得把其文件整目录复制进本项目而不做适配。

---

## 15. 信息源

- 官方开发指南：<https://docs.olares.cn/zh/developer/develop/>
- OAC 结构：`/developer/develop/package/chart.html`
- Manifest 字段：`/developer/develop/package/manifest.html`
- Helm 扩展与注入变量：`/developer/develop/package/extension.html`
- 分发规则：`/developer/develop/distribute-index.html`
- 真实应用仓库：<https://github.com/beclab/apps>（本地路径见 §14）

`[建议]` 本文件信息超过一个 Olares 大版本未复核时视为过期，需重新核对后再引用。

---

## 16. 本仓库适配：fork / monorepo 场景

PCMP for Olares App 模板默认假设「单应用单仓库」。本仓库是 `beclab/apps` 的 fork，单仓库内含约 400 个 OAC 应用包，故登记以下项目定制；其余章节规则原样适用。

1. `[事实]` **参考基线即本仓库自身**：`/home/inverstar/ai/github.com/AIDockerCloud/olares-apps` 既是工作区也是参考仓库；remote `upstream` 指向官方 `beclab/apps`，`upstream/main` 是字段与结构的权威基线。找同类应用时在本仓库内检索，无需另找外部仓库。
2. `[规定]` **§12「一分支一提交」只约束向 upstream 提交的 PR 分支**：PR 分支必须从干净的 `upstream/main` 切出，禁止携带 `develop` 分支的 `AGENTS.md`、`DEVELOP.md`、`ai/`、`PROJECT_CONTEXT*.md`、`skills/`、`scripts/` 等治理文件。`develop` 只是本地集成分支，允许多个提交与 merge commit；两类分支不得混用。
3. `[事实]` **版本更新的实际改动集合**（实证：提交 `0e96ff72` / agentj 0.28.2）：`Chart.yaml`、`OlaresManifest.yaml`、`i18n/en-US/OlaresManifest.yaml`、`i18n/zh-CN/OlaresManifest.yaml`、`values.yaml`。但镜像版本写法不统一：`agentj` / `neodb` 用 `values.yaml:image.tag`，`fastnotesync` / `vaultwarden` 用 `image.version` 且把版本硬编码在 `templates/*.yaml`。改版本前须 `grep -rn` 检索旧版本号，以目标应用真实结构为准。字段逐项清单见 [DEVELOP.md](../DEVELOP.md) §5。

核对日期：2026-11-07
