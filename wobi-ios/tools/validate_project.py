"""静态校验 Wobi.xcodeproj 和资源文件。

在没有 Mac 的 Windows 上，无法真正跑 xcodebuild，所以用这个脚本兜底检查：
  - project.pbxproj 的 OpenStep plist 语法
  - 所有对象引用是否指向存在的 ID
  - 文件引用是否和磁盘上的文件一致
  - Info.plist / PrivacyInfo.xcprivacy / Assets / scheme 是否合法
  - Swift 源文件的括号与字符串是否基本平衡

用法：
    python tools/validate_project.py
"""

from __future__ import annotations

import json
import plistlib
import re
import sys
from pathlib import Path
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parent.parent
PROJECT_DIR = ROOT / "Wobi.xcodeproj"
PBXPROJ = PROJECT_DIR / "project.pbxproj"
SCHEME = PROJECT_DIR / "xcshareddata" / "xcschemes" / "Wobi.xcscheme"
SOURCE_DIR = ROOT / "Wobi" / "Sources"

errors: list[str] = []
warnings: list[str] = []


def fail(message: str) -> None:
    errors.append(message)


# ---------------------------------------------------------------------------
# OpenStep plist 解析（pbxproj 用的格式）
# ---------------------------------------------------------------------------


class OpenStepParser:
    def __init__(self, text: str) -> None:
        self.text = text
        self.pos = 0

    def parse(self):
        self.skip()
        value = self.parse_value()
        self.skip()
        if self.pos != len(self.text):
            line = self.text.count("\n", 0, self.pos) + 1
            raise ValueError(f"解析结束后还有多余内容（第 {line} 行）")
        return value

    def skip(self) -> None:
        while self.pos < len(self.text):
            char = self.text[self.pos]
            if char in " \t\r\n":
                self.pos += 1
            elif self.text.startswith("//", self.pos):
                end = self.text.find("\n", self.pos)
                self.pos = len(self.text) if end == -1 else end + 1
            elif self.text.startswith("/*", self.pos):
                end = self.text.find("*/", self.pos)
                if end == -1:
                    raise ValueError("注释没有闭合")
                self.pos = end + 2
            else:
                return

    def parse_value(self):
        self.skip()
        if self.pos >= len(self.text):
            raise ValueError("意外结束")
        char = self.text[self.pos]
        if char == "{":
            return self.parse_dict()
        if char == "(":
            return self.parse_array()
        if char == '"':
            return self.parse_quoted()
        return self.parse_bare()

    def parse_dict(self):
        result = {}
        self.pos += 1  # {
        while True:
            self.skip()
            if self.pos >= len(self.text):
                raise ValueError("字典没有闭合")
            if self.text[self.pos] == "}":
                self.pos += 1
                return result
            key = self.parse_quoted() if self.text[self.pos] == '"' else self.parse_bare()
            self.skip()
            if self.text[self.pos] != "=":
                raise ValueError(f"字典键 {key!r} 后缺少 =")
            self.pos += 1
            value = self.parse_value()
            result[key] = value
            self.skip()
            if self.pos < len(self.text) and self.text[self.pos] == ";":
                self.pos += 1

    def parse_array(self):
        result = []
        self.pos += 1  # (
        while True:
            self.skip()
            if self.pos >= len(self.text):
                raise ValueError("数组没有闭合")
            if self.text[self.pos] == ")":
                self.pos += 1
                return result
            result.append(self.parse_value())
            self.skip()
            if self.pos < len(self.text) and self.text[self.pos] == ",":
                self.pos += 1

    def parse_quoted(self) -> str:
        self.pos += 1
        out = []
        while self.pos < len(self.text):
            char = self.text[self.pos]
            if char == '"':
                self.pos += 1
                return "".join(out)
            if char == "\\":
                self.pos += 1
                if self.pos >= len(self.text):
                    break
                escape = self.text[self.pos]
                mapping = {"n": "\n", "t": "\t", "r": "\r", '"': '"', "\\": "\\"}
                if escape in mapping:
                    out.append(mapping[escape])
                    self.pos += 1
                elif escape == "U":
                    code = self.text[self.pos + 1 : self.pos + 5]
                    out.append(chr(int(code, 16)))
                    self.pos += 5
                else:
                    out.append(escape)
                    self.pos += 1
            else:
                out.append(char)
                self.pos += 1
        raise ValueError("字符串没有闭合")

    def parse_bare(self) -> str:
        start = self.pos
        while self.pos < len(self.text):
            char = self.text[self.pos]
            if char in " \t\r\n,;=(){}":
                break
            if self.text.startswith("//", self.pos) or self.text.startswith("/*", self.pos):
                break
            self.pos += 1
        if start == self.pos:
            line = self.text.count("\n", 0, self.pos) + 1
            raise ValueError(f"空 token（第 {line} 行）")
        return self.text[start : self.pos]


# ---------------------------------------------------------------------------
# 检查工具
# ---------------------------------------------------------------------------


def check_object_references(objects: dict) -> None:
    id_pattern = re.compile(r"^[0-9A-F]{24}$")
    single_ref_keys = {
        "fileRef",
        "productReference",
        "buildConfigurationList",
        "mainGroup",
        "productRefGroup",
        "target",
    }
    list_ref_keys = {
        "children",
        "files",
        "buildPhases",
        "buildConfigurations",
        "targets",
        "dependencies",
        "buildRules",
    }

    for identifier, obj in objects.items():
        if not isinstance(obj, dict):
            fail(f"{identifier} 不是字典对象")
            continue
        if "isa" not in obj:
            fail(f"{identifier} 缺少 isa")

        for key in single_ref_keys:
            value = obj.get(key)
            if isinstance(value, str):
                if not id_pattern.match(value):
                    fail(f"{identifier}.{key} 不是 24 位十六进制 ID：{value}")
                elif value not in objects:
                    fail(f"{identifier}.{key} 指向不存在的对象 {value}")

        for key in list_ref_keys:
            values = obj.get(key)
            if not isinstance(values, list):
                continue
            for ref in values:
                if not isinstance(ref, str):
                    fail(f"{identifier}.{key} 中有非字符串引用")
                elif ref not in objects:
                    fail(f"{identifier}.{key} 指向不存在的对象 {ref}")

        target_attributes = obj.get("TargetAttributes")
        if isinstance(target_attributes, dict):
            for target_id in target_attributes:
                if target_id not in objects:
                    fail(f"TargetAttributes 指向不存在的 target {target_id}")


def check_build_files(objects: dict) -> None:
    for identifier, obj in objects.items():
        if obj.get("isa") != "PBXBuildFile":
            continue
        file_ref = obj.get("fileRef")
        if file_ref not in objects:
            fail(f"{identifier} 的 fileRef {file_ref} 不存在")
        elif objects[file_ref].get("isa") != "PBXFileReference":
            fail(f"{identifier} 的 fileRef 不是 PBXFileReference")


def resolve_paths(objects: dict, main_group_id: str) -> dict[str, Path]:
    """把 group 树里的文件引用解析成磁盘路径。"""
    result: dict[str, Path] = {}

    def walk(group_id: str, base: Path) -> None:
        group = objects.get(group_id)
        if not isinstance(group, dict) or group.get("isa") != "PBXGroup":
            return
        path = group.get("path")
        current = base / path if path else base
        for child_id in group.get("children", []):
            child = objects.get(child_id)
            if not isinstance(child, dict):
                continue
            isa = child.get("isa")
            if isa == "PBXGroup":
                walk(child_id, current)
            elif isa == "PBXFileReference":
                source_tree = child.get("sourceTree")
                if source_tree != "<group>":
                    continue
                child_path = child.get("path")
                if child_path:
                    result[child_id] = (current / child_path).resolve()

    walk(main_group_id, ROOT)
    return result


def check_file_paths(objects: dict, paths: dict[str, Path]) -> None:
    for identifier, path in paths.items():
        name = objects[identifier].get("path", identifier)
        if not path.exists():
            fail(f"文件引用在磁盘上不存在：{name} -> {path}")
    on_disk = {p.resolve() for p in SOURCE_DIR.glob("*.swift")}
    referenced = {path for path in paths.values() if path.parent == SOURCE_DIR.resolve()}
    missing = on_disk - referenced
    extra = referenced - on_disk
    if missing:
        fail(f"磁盘上有未被工程引用的 Swift 文件：{sorted(p.name for p in missing)}")
    if extra:
        fail(f"工程引用了不存在的 Swift 文件：{sorted(p.name for p in extra)}")


def check_plists_and_assets(objects: dict, paths: dict[str, Path]) -> None:
    info = ROOT / "Wobi" / "Info.plist"
    privacy = ROOT / "Wobi" / "PrivacyInfo.xcprivacy"
    for file in (info, privacy):
        try:
            with file.open("rb") as handle:
                value = plistlib.load(handle)
            if not isinstance(value, dict):
                fail(f"{file.name} 不是字典")
        except Exception as exc:  # noqa: BLE001
            fail(f"{file.name} 解析失败：{exc}")

    try:
        with info.open("rb") as handle:
            info_data = plistlib.load(handle)
        for key in ("CFBundleDisplayName", "CFBundleIdentifier", "ITSAppUsesNonExemptEncryption"):
            if key not in info_data:
                fail(f"Info.plist 缺少 {key}")
        if info_data.get("CFBundleDisplayName") != "卧笔":
            fail("Info.plist 的 CFBundleDisplayName 不是“卧笔”")
    except Exception:
        pass

    asset_root = ROOT / "Wobi" / "Assets.xcassets"
    try:
        json.loads((asset_root / "Contents.json").read_text(encoding="utf-8"))
        icon_contents = json.loads(
            (asset_root / "AppIcon.appiconset" / "Contents.json").read_text(encoding="utf-8")
        )
        json.loads(
            (asset_root / "AccentColor.colorset" / "Contents.json").read_text(encoding="utf-8")
        )
        icon_name = icon_contents["images"][0]["filename"]
        icon_path = asset_root / "AppIcon.appiconset" / icon_name
        if not icon_path.exists():
            fail(f"App 图标缺失：{icon_path}")
        else:
            try:
                from PIL import Image  # type: ignore

                with Image.open(icon_path) as image:
                    if image.size != (1024, 1024):
                        fail(f"App 图标尺寸不是 1024x1024：{image.size}")
                    if image.mode not in ("RGB", "L"):
                        fail(f"App 图标带透明通道（{image.mode}），App Store 会拒绝")
            except ImportError:
                warnings.append("未安装 Pillow，跳过图标尺寸/透明通道检查")
    except Exception as exc:  # noqa: BLE001
        fail(f"Assets.xcassets 解析失败：{exc}")


def check_scheme(objects: dict) -> None:
    try:
        tree = ElementTree.parse(SCHEME)
    except Exception as exc:  # noqa: BLE001
        fail(f"scheme 解析失败：{exc}")
        return
    identifiers = {
        element.get("BlueprintIdentifier")
        for element in tree.iter("BuildableReference")
        if element.get("BlueprintIdentifier")
    }
    for identifier in identifiers:
        if identifier not in objects:
            fail(f"scheme 里的 BlueprintIdentifier {identifier} 不存在")
    if not identifiers:
        fail("scheme 里没有 BuildableReference")


SWIFT_TOKEN_RE = re.compile(
    r'"""(?:.|\n)*?"""|"(?:\\.|[^"\\])*"|//[^\n]*|/\*(?:.|\n)*?\*/',
    re.MULTILINE,
)


def check_swift_balance() -> None:
    pairs = {")": "(", "]": "[", "}": "{"}
    for path in sorted(SOURCE_DIR.glob("*.swift")):
        text = path.read_text(encoding="utf-8")
        stripped = SWIFT_TOKEN_RE.sub("", text)
        stack: list[tuple[str, int]] = []
        for index, char in enumerate(stripped):
            if char in "([{":
                stack.append((char, index))
            elif char in ")]}":
                if not stack or stack[-1][0] != pairs[char]:
                    fail(f"{path.name} 括号不匹配：第 {stripped.count(chr(10), 0, index) + 1} 行")
                    break
                stack.pop()
        else:
            if stack:
                fail(f"{path.name} 有未闭合的 {stack[-1][0]}")


def main() -> int:
    try:
        text = PBXPROJ.read_text(encoding="utf-8")
    except Exception as exc:  # noqa: BLE001
        print(f"无法读取 project.pbxproj：{exc}")
        return 1

    try:
        document = OpenStepParser(text).parse()
    except Exception as exc:  # noqa: BLE001
        print(f"project.pbxproj 语法错误：{exc}")
        return 1

    if not isinstance(document, dict):
        print("project.pbxproj 顶层不是字典")
        return 1

    objects = document.get("objects")
    if not isinstance(objects, dict):
        print("project.pbxproj 缺少 objects")
        return 1

    if document.get("rootObject") not in objects:
        fail("rootObject 指向不存在的对象")
    elif objects[document["rootObject"]].get("isa") != "PBXProject":
        fail("rootObject 不是 PBXProject")

    check_object_references(objects)
    check_build_files(objects)

    project = objects.get(document.get("rootObject"), {})
    paths = resolve_paths(objects, project.get("mainGroup"))
    check_file_paths(objects, paths)
    check_plists_and_assets(objects, paths)
    check_scheme(objects)
    check_swift_balance()

    if warnings:
        print("警告：")
        for warning in warnings:
            print(f"  - {warning}")
    if errors:
        print("发现错误：")
        for error in errors:
            print(f"  - {error}")
        return 1

    print(f"通过：{len(objects)} 个工程对象，{len(paths)} 个文件引用，{len(list(SOURCE_DIR.glob('*.swift')))} 个 Swift 文件")
    return 0


if __name__ == "__main__":
    sys.exit(main())
