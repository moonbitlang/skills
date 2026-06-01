#!/usr/bin/env python3
"""Template vendoring script for MoonBit native C bindings.

Copy this file to scripts/prepare.py in the target binding repository, then
replace the CONFIG block. The script downloads a pinned upstream archive,
copies selected C/header files into the MoonBit package directory, optionally
flattens nested paths, rewrites quoted includes for flattened files, and
refreshes the native-stub block in moon.pkg.
"""

from __future__ import annotations

import hashlib
import re
import shutil
import tarfile
import urllib.request
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]

# CONFIG: replace these values for the target library.
PACKAGE_DIR = REPO_ROOT / "src"
CACHE_DIR = REPO_ROOT / ".prepare"
UPSTREAM_URL = "https://example.com/library-1.2.3.tar.gz"
UPSTREAM_SHA256 = "replace-with-archive-sha256"
ARCHIVE_ROOT = "library-1.2.3"
SOURCE_PREFIX = "upstream"

# Paths are relative to ARCHIVE_ROOT.
FILES_TO_VENDOR = [
    "include/library.h",
    "src/library.c",
]

# Files listed here are copied without include rewriting.
NO_REWRITE = {
    "include/library.h",
}

NATIVE_STUB_MANAGED_BEGIN = "# BEGIN managed-native-stub"
NATIVE_STUB_MANAGED_END = "# END managed-native-stub"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def download_archive() -> Path:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    archive = CACHE_DIR / Path(UPSTREAM_URL).name
    if not archive.exists():
        urllib.request.urlretrieve(UPSTREAM_URL, archive)
    actual = sha256_file(archive)
    if actual != UPSTREAM_SHA256:
        raise SystemExit(
            f"sha256 mismatch for {archive}: expected {UPSTREAM_SHA256}, got {actual}"
        )
    return archive


def extract_archive(archive: Path) -> Path:
    out_dir = CACHE_DIR / "src"
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True)
    with tarfile.open(archive) as tar:
        tar.extractall(out_dir)
    root = out_dir / ARCHIVE_ROOT
    if not root.exists():
        raise SystemExit(f"archive root not found: {root}")
    return root


def flat_name(relative_path: str) -> str:
    return SOURCE_PREFIX + "#" + relative_path.replace("/", "#")


def include_map() -> dict[str, str]:
    mapping: dict[str, str] = {}
    for rel in FILES_TO_VENDOR:
        mapping[Path(rel).name] = flat_name(rel)
        mapping[rel] = flat_name(rel)
    return mapping


INCLUDE_RE = re.compile(r'(^\s*#\s*include\s+")([^"]+)(")', re.MULTILINE)


def rewrite_includes(text: str, mapping: dict[str, str]) -> str:
    def replace(match: re.Match[str]) -> str:
        include = match.group(2)
        rewritten = mapping.get(include)
        if rewritten is None:
            rewritten = mapping.get(Path(include).name)
        if rewritten is None:
            return match.group(0)
        return f"{match.group(1)}{rewritten}{match.group(3)}"

    return INCLUDE_RE.sub(replace, text)


def clean_old_vendor_files() -> None:
    for path in PACKAGE_DIR.glob(f"{SOURCE_PREFIX}#*"):
        if path.is_file():
            path.unlink()


def vendor_files(upstream_root: Path) -> list[str]:
    PACKAGE_DIR.mkdir(parents=True, exist_ok=True)
    clean_old_vendor_files()
    mapping = include_map()
    vendored: list[str] = []
    for rel in FILES_TO_VENDOR:
        src = upstream_root / rel
        if not src.exists():
            raise SystemExit(f"missing upstream file: {src}")
        dest_name = flat_name(rel)
        dest = PACKAGE_DIR / dest_name
        text = src.read_text()
        if rel not in NO_REWRITE:
            text = rewrite_includes(text, mapping)
        dest.write_text(text)
        vendored.append(dest_name)
    return sorted(vendored)


def update_moon_pkg(vendored: list[str]) -> None:
    moon_pkg = PACKAGE_DIR / "moon.pkg"
    text = moon_pkg.read_text()
    block = "\n".join(
        [
            NATIVE_STUB_MANAGED_BEGIN,
            *[f'    "{name}",' for name in vendored if name.endswith(".c")],
            NATIVE_STUB_MANAGED_END,
        ]
    )
    pattern = re.compile(
        re.escape(NATIVE_STUB_MANAGED_BEGIN)
        + r".*?"
        + re.escape(NATIVE_STUB_MANAGED_END),
        re.DOTALL,
    )
    if not pattern.search(text):
        raise SystemExit(
            "moon.pkg is missing managed native-stub markers; add them before rerunning"
        )
    moon_pkg.write_text(pattern.sub(block, text))


def main() -> None:
    archive = download_archive()
    upstream_root = extract_archive(archive)
    vendored = vendor_files(upstream_root)
    update_moon_pkg(vendored)


if __name__ == "__main__":
    main()
