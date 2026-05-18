#!/usr/bin/env python3
"""Sync vendored skills from their upstream repositories."""

from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess
import tempfile


ROOT = Path(__file__).resolve().parents[1]
SOURCES = ROOT / "skills.sources.json"
SKILLS = ROOT / "skills"
TEXT_SUFFIXES = {
    ".json",
    ".md",
    ".mbt",
    ".py",
    ".sh",
    ".toml",
    ".txt",
    ".yaml",
    ".yml",
}


def run(args: list[str]) -> None:
    subprocess.run(args, check=True)


def copy_skill(src: Path, dest: Path) -> None:
    if not (src / "SKILL.md").is_file():
        raise SystemExit(f"SKILL.md not found in upstream path: {src}")

    if dest.exists():
        shutil.rmtree(dest)

    def ignore(directory: str, names: list[str]) -> set[str]:
        ignored = {".git"}
        if Path(directory) == src:
            ignored.add(".github")
        return ignored.intersection(names)

    shutil.copytree(src, dest, ignore=ignore)
    strip_trailing_whitespace(dest)


def strip_trailing_whitespace(path: Path) -> None:
    for file_path in path.rglob("*"):
        if not file_path.is_file() or file_path.suffix not in TEXT_SUFFIXES:
            continue
        original = file_path.read_bytes()
        try:
            text = original.decode("utf-8")
        except UnicodeDecodeError:
            continue
        normalized = "\n".join(line.rstrip(" \t") for line in text.split("\n"))
        if normalized.encode("utf-8") != original:
            file_path.write_text(normalized)


def main() -> None:
    sources = json.loads(SOURCES.read_text())

    with tempfile.TemporaryDirectory(prefix="moonbit-skills-sync-") as tmp:
        tmp_root = Path(tmp)
        clones: dict[tuple[str, str], Path] = {}

        for skill_name, source in sources.items():
            repo = source["repo"]
            ref = source.get("ref", "main")
            key = (repo, ref)

            if key not in clones:
                clone_dir = tmp_root / f"repo-{len(clones)}"
                run([
                    "git",
                    "clone",
                    "--depth",
                    "1",
                    "--branch",
                    ref,
                    repo,
                    str(clone_dir),
                ])
                clones[key] = clone_dir

            upstream_path = clones[key] / source["path"]
            dest = SKILLS / skill_name
            print(f"sync {skill_name}: {repo}@{ref}:{source['path']}")
            copy_skill(upstream_path, dest)


if __name__ == "__main__":
    main()
