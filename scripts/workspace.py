#!/usr/bin/env python3
"""创建独立工作区、导入原件、校验摘要和准备分析副本。仅使用标准库。"""

import argparse
import hashlib
import json
import shutil
import stat
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NOTE_NAMES = (
    "SCOPE.md", "ARCHITECTURE.md", "findings.md", "renames.md",
    "open-questions.md", "HANDOFF.md",
)


def files_in(path):
    """拒绝软链接和特殊文件，避免把工作区外数据混入证据。"""
    if path.is_symlink():
        raise ValueError(f"不接受软链接：{path}")
    if path.is_file():
        return [path]
    if not path.is_dir():
        raise ValueError(f"需要普通文件或目录：{path}")
    files = []
    for item in sorted(path.rglob("*")):
        mode = item.lstat().st_mode
        if stat.S_ISLNK(mode) or not (stat.S_ISREG(mode) or stat.S_ISDIR(mode)):
            raise ValueError(f"不接受软链接或特殊文件：{item}")
        if stat.S_ISREG(mode):
            files.append(item)
    return files


def inventory(directory):
    result = {}
    for path in files_in(directory):
        relative = path.relative_to(directory).as_posix()
        if relative == ".gitkeep":
            continue
        with path.open("rb") as handle:
            digest = hashlib.file_digest(handle, "sha256").hexdigest()
        result[relative] = {"sha256": digest, "size": path.stat().st_size}
    return result


def import_target(root, source):
    if source.is_symlink():
        raise ValueError(f"不接受软链接：{source}")
    source = source.resolve()
    if source == root or source in root.parents or root in source.parents:
        raise ValueError("从工作区外导入样本，避免递归复制或混用分析产物")
    files = files_in(source)
    if not files:
        raise ValueError("样本目录为空")
    manifest = root / "notes/target-manifest.json"
    target = root / "target"
    if manifest.exists() or any(p.name != ".gitkeep" for p in target.iterdir()):
        raise ValueError("本工作区已有样本或基线；请为新目标创建独立工作区")
    destination = target / source.name
    if destination.name == ".gitkeep":
        raise ValueError(".gitkeep 是保留名称")
    if source.is_dir():
        shutil.copytree(source, destination)
    else:
        shutil.copyfile(source, destination)
    data = {
        "version": 1,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "files": inventory(target),
    }
    with manifest.open("x", encoding="utf-8") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    for path in files_in(destination):
        path.chmod(0o444)
    print(f"已导入 {len(data['files'])} 个文件；基线：{manifest}")


def verify(root):
    manifest = root / "notes/target-manifest.json"
    if not manifest.is_file():
        raise ValueError("尚未建立原件基线；先运行 import")
    data = json.loads(manifest.read_text(encoding="utf-8"))
    expected = data["files"]
    if data.get("version") != 1 or not expected:
        raise ValueError("基线格式不支持或没有记录文件")
    actual = inventory(root / "target")
    differences = []
    for name in sorted(expected.keys() | actual.keys()):
        if name not in expected:
            differences.append(f"新增：{name}")
        elif name not in actual:
            differences.append(f"丢失：{name}")
        elif actual[name] != expected[name]:
            differences.append(f"变化：{name}")
    if differences:
        raise ValueError("原件校验失败\n" + "\n".join(differences))
    print(f"原件校验通过：{len(expected)} 个文件")


def stage(root):
    verify(root)
    destination = root / "work/input"
    if destination.exists() or destination.is_symlink():
        raise ValueError("work/input 已存在，保留现有分析副本，不覆盖")
    target = root / "target"
    shutil.copytree(target, destination,
                    ignore=lambda directory, names: {".gitkeep"} if Path(directory) == target else set())
    for path in files_in(destination):
        path.chmod(0o600)
    print(f"分析副本：{destination}")


def new_workspace(destination):
    destination = destination.absolute()
    if destination.exists() or destination.is_symlink():
        raise ValueError("新工作区路径必须不存在")
    destination = destination.resolve()
    if ROOT == destination or ROOT in destination.parents:
        raise ValueError("新工作区应位于模板目录之外")
    destination.mkdir(parents=True)
    for name in ("README.md", "AGENTS.md", "CLAUDE.md", "Makefile", ".gitignore", ".mcp.json"):
        shutil.copyfile(ROOT / name, destination / name)
    for name in (".claude/settings.json", ".codex/config.toml"):
        (destination / name).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / name, destination / name)
    for name in ("scripts", "prompts", "tests", "docs"):
        shutil.copytree(ROOT / name, destination / name,
                        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "settings.local.json"))
    for name in ("target", "work", "notes/evidence"):
        (destination / name).mkdir(parents=True, exist_ok=True)
        (destination / name / ".gitkeep").touch()
    for name in NOTE_NAMES:
        shutil.copyfile(ROOT / "templates/notes" / name, destination / "notes" / name)
    shutil.copytree(ROOT / "templates", destination / "templates")
    print(f"已创建：{destination}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("new", help="复制模板到不存在的目录").add_argument("path", type=Path)
    commands.add_parser("import", help="导入工作区外的文件/目录").add_argument("path", type=Path)
    commands.add_parser("verify", help="校验原件，差异时返回非零退出码")
    commands.add_parser("stage", help="生成可写分析副本，不覆盖已有副本")
    args = parser.parse_args()
    try:
        if args.command == "new":
            new_workspace(args.path)
        elif args.command == "import":
            import_target(ROOT, args.path.absolute())
        elif args.command == "verify":
            verify(ROOT)
        else:
            stage(ROOT)
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f"错误：{error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
