#!/usr/bin/env python3
"""扫描 owners 文件，生成 / 核对 AIDockerCloud owner 应用清单。

零外部依赖（仅 Python 3 标准库）。用法：
  python3 scripts/owned_apps.py            打印清单 Markdown
  python3 scripts/owned_apps.py --write   写入 ai/INVENTORY.md
  python3 scripts/owned_apps.py --check   比对 ai/INVENTORY.md，漂移则退出码 1

判定依据：仓库一级子目录 <app>/owners 的列表中包含 AIDockerCloud。
"""

from __future__ import annotations

import argparse
import difflib
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INVENTORY = ROOT / "ai" / "INVENTORY.md"
OWNER = "AIDockerCloud"


def text(rel: str) -> str:
    path = ROOT / rel
    return path.read_text(encoding="utf-8") if path.is_file() else ""


def first(pattern: str, content: str, default: str = "-") -> str:
    match = re.search(pattern, content, re.MULTILINE)
    return match.group(1).strip().strip("'\"") if match else default


def owners(path: Path) -> list[str]:
    result = []
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped.startswith("-"):
            result.append(stripped[1:].strip().strip("'\""))
    return result


def last_commit(app: str) -> str:
    try:
        proc = subprocess.run(
            ["git", "log", "-1", "--format=%h", "--", app],
            cwd=ROOT, capture_output=True, text=True, check=True,
        )
        return proc.stdout.strip() or "-"
    except (OSError, subprocess.CalledProcessError):
        return "-"


def collect() -> list[dict[str, str]]:
    rows = []
    for owners_file in sorted(ROOT.glob("*/owners")):
        if OWNER not in owners(owners_file):
            continue
        app = owners_file.parent.name
        chart = text(f"{app}/Chart.yaml")
        manifest = text(f"{app}/OlaresManifest.yaml")
        values = text(f"{app}/values.yaml")

        chart_version = first(r"^version:\s*['\"]?([^\s'\"]+)", chart)
        app_version = first(r"^appVersion:\s*['\"]?([^\s'\"]+)", chart)
        meta_version = first(r"^  version:\s*['\"]?([^\s'\"]+)", manifest)
        version_name = first(r"^  versionName:\s*['\"]?([^\s'\"]+)", manifest)
        # 镜像版本字段有两种写法：image.tag（agentj/neodb/mindwtr）或
        # image.version（fastnotesync/vaultwarden）；多镜像应用取第一个业务镜像。
        image_tag = first(r"^\s+tag:\s*['\"]?([^\s'\"]+)", values)
        if image_tag == "-":
            image_tag = first(r"^\s+version:\s*['\"]?([^\s'\"]+)", values)

        issues = []
        if chart_version != meta_version:
            issues.append("chart/metadata 版本不一致")
        if app_version != version_name:
            issues.append("appVersion/versionName 不一致")
        if image_tag != "-" and not image_tag.startswith(app_version):
            issues.append("镜像版本与 appVersion 不同")

        rows.append({
            "app": app,
            "chart": chart_version,
            "meta": meta_version,
            "appver": app_version,
            "vname": version_name,
            "tag": image_tag,
            "consistency": "OK" if not issues else "CHECK: " + "；".join(issues),
            "commit": last_commit(app),
        })
    return rows


def render(rows: list[dict[str, str]]) -> str:
    lines = [
        "# AIDockerCloud owner 应用清单 (INVENTORY.md)",
        "",
        "> `[事实]` 本文件由 `scripts/owned_apps.py` 从工作区扫描生成，**请勿手工编辑**。",
        "> 唯一判定依据：`<app>/owners` 的列表中包含 `AIDockerCloud`。",
        "> 刷新：`python3 scripts/owned_apps.py --write`；核对：`python3 scripts/owned_apps.py --check`。",
        "> 权威基线：`upstream/main`（remote `upstream` = https://github.com/beclab/apps）。",
        "",
        f"- 在册应用数：**{len(rows)}**",
        "- 扫描范围：仓库一级子目录下全部 `<app>/owners`",
        "- 「镜像版本」列取 `values.yaml` 的 `image.tag` 或 `image.version`（多镜像取第一个业务镜像）",
        "- `CHECK` 行表示版本字段存在差异，需人工对照同类应用核实（不一定是错误）",
        "",
        "| 应用 | chart 版本 | metadata.version | appVersion | versionName | 镜像版本 | 一致性 | 最近提交 |",
        "| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |",
    ]
    for row in rows:
        lines.append(
            "| {app} | {chart} | {meta} | {appver} | {vname} | {tag} | {consistency} | `{commit}` |".format(**row)
        )
    lines += [
        "",
        "## 判定与维护规则",
        "",
        "1. `[规定]` 应用范围只看 `owners` 文件；本清单之外的应用一律视为只读基线。",
        "2. `[规定]` upstream 合并了 `Add AIDockerCloud to owners list` 或版本更新提交后，",
        "   同步 `develop` 并重跑 `--write`，再执行 `--check` 确认清单与实物一致。",
        "3. `[规定]` 交付 PR 一次只涉及本清单中的一个应用目录，且不携带治理层文件。",
        "4. `[事实]` 版本更新至少涉及 5 个文件（见 [../DEVELOP.md](../DEVELOP.md) §5）；镜像版本字段有 `image.tag` 与 `image.version` 两种写法，",
        "   且部分应用把镜像版本硬编码在 `templates/`，改版本前用 `grep -rn \"<旧版本>\" <app>/` 全目录检索。",
        "5. `[建议]` `CHECK` 表示版本字段存在差异，动字段前先在本仓库找同类应用对照，不要凭记忆补值。",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="生成/核对 AIDockerCloud owner 应用清单")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--write", action="store_true", help="写入 ai/INVENTORY.md")
    group.add_argument("--check", action="store_true", help="比对现有清单，漂移则退出码 1")
    args = parser.parse_args()

    expected = render(collect())

    if args.write:
        INVENTORY.parent.mkdir(parents=True, exist_ok=True)
        INVENTORY.write_text(expected, encoding="utf-8")
        print(f"已写入 {INVENTORY.relative_to(ROOT)}")
        return 0

    if args.check:
        if not INVENTORY.is_file():
            print(f"缺少清单：{INVENTORY.relative_to(ROOT)}（先执行 --write）", file=sys.stderr)
            return 1
        actual = INVENTORY.read_text(encoding="utf-8")
        if actual == expected:
            print("清单一致：ai/INVENTORY.md 与工作区扫描结果相符")
            return 0
        print("清单已漂移：ai/INVENTORY.md 与工作区扫描结果不一致", file=sys.stderr)
        diff = difflib.unified_diff(
            actual.splitlines(), expected.splitlines(),
            fromfile="ai/INVENTORY.md", tofile="scan-result", lineterm="",
        )
        for line in list(diff)[:60]:
            print(line, file=sys.stderr)
        print("修复：python3 scripts/owned_apps.py --write", file=sys.stderr)
        return 1

    print(expected, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
