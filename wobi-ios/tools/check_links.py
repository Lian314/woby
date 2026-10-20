"""校验文档链接、YAML 工作流、plist 和 JSON。

用法：
    python tools/check_links.py
需要 PyYAML（pip install pyyaml）。
"""

from __future__ import annotations

import json
import plistlib
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ERRORS: list[str] = []

LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")


def check_markdown() -> int:
    count = 0
    for md in ROOT.rglob("*.md"):
        if ".git" in md.parts:
            continue
        text = md.read_text(encoding="utf-8")
        for match in LINK_RE.finditer(text):
            target = match.group(1)
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            clean = target.split("#", 1)[0]
            if not clean:
                continue
            path = (md.parent / clean).resolve()
            count += 1
            if not path.exists():
                line = text.count("\n", 0, match.start()) + 1
                ERRORS.append(f"{md.relative_to(ROOT)}:{line} 链接不存在：{target}")
    return count


def check_yaml() -> int:
    try:
        import yaml  # type: ignore
    except ImportError:
        print("跳过 YAML：未安装 PyYAML")
        return 0
    count = 0
    for path in (ROOT / ".github" / "workflows").glob("*.yml"):
        try:
            yaml.safe_load(path.read_text(encoding="utf-8"))
            count += 1
        except Exception as exc:  # noqa: BLE001
            ERRORS.append(f"{path.relative_to(ROOT)} YAML 解析失败：{exc}")
    return count


def check_plists_and_json() -> int:
    count = 0
    for path in ROOT.rglob("*"):
        if ".git" in path.parts or not path.is_file():
            continue
        try:
            if path.suffix in (".plist", ".xcprivacy"):
                with path.open("rb") as handle:
                    plistlib.load(handle)
                count += 1
            elif path.suffix == ".json" and "Assets.xcassets" in path.parts:
                json.loads(path.read_text(encoding="utf-8"))
                count += 1
        except Exception as exc:  # noqa: BLE001
            ERRORS.append(f"{path.relative_to(ROOT)} 解析失败：{exc}")
    return count


def main() -> int:
    links = check_markdown()
    yaml_count = check_yaml()
    structured = check_plists_and_json()

    if ERRORS:
        print("发现问题：")
        for error in ERRORS:
            print(f"  - {error}")
        return 1
    print(f"通过：{links} 个本地链接，{yaml_count} 个 workflow，{structured} 个 plist/JSON")
    return 0


if __name__ == "__main__":
    sys.exit(main())
