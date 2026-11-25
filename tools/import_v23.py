#!/usr/bin/env python3
"""Import a BakeryProduction v23 release ZIP without changing relative resource paths."""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
import zipfile
from pathlib import Path

PREFIX = "Bakery_v23_FINAL/"
EXPECTED_ALP = {
    "Bakery_v23_MAIN.alp",
    "Bakery_v23_BOTTLENECK.alp",
    "Bakery_v23_IMPROVED.alp",
    "Bakery_v22_BACKUP.alp",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path, help="Bakery_v23_FINAL_COMPLETE.zip")
    parser.add_argument(
        "--destination",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "releases" / "v23",
        help="Output directory for models and their colocated image resources",
    )
    args = parser.parse_args()
    archive = args.archive.expanduser().resolve()
    if not archive.is_file():
        parser.error(f"Archive not found: {archive}")

    dest = args.destination.expanduser().resolve()
    if any(p.is_symlink() for p in [dest, *dest.parents]):
        parser.error("Symlinked destination is not supported")
    dest.mkdir(parents=True, exist_ok=True)
    manifest = {}

    with zipfile.ZipFile(archive) as zf:
        members = [item for item in zf.infolist() if not item.is_dir()]
        names = {Path(item.filename).name for item in members}
        missing = EXPECTED_ALP - names
        if missing:
            parser.error("Missing models in release: " + ", ".join(sorted(missing)))
        if len(members) < 40:
            parser.error(f"Unexpected file count: {len(members)} (expected at least 40)")
        if any(not item.filename.startswith(PREFIX) for item in members):
            parser.error("Unexpected archive structure; refusing to extract")

        for item in members:
            rel = item.filename.removeprefix(PREFIX)
            relpath = Path(rel)
            if not rel or relpath.is_absolute() or ".." in relpath.parts:
                parser.error(f"Unsafe archive entry: {item.filename}")
            target = (dest / relpath).resolve()
            if not target.is_relative_to(dest):
                parser.error(f"Archive path escapes destination: {item.filename}")
            target.parent.mkdir(parents=True, exist_ok=True)
            with zf.open(item) as source, target.open("wb") as output:
                shutil.copyfileobj(source, output)
            manifest[relpath.as_posix()] = {
                "sha256": sha256(target),
                "bytes": target.stat().st_size,
            }

    manifest_path = dest / "IMPORT_MANIFEST.json"
    manifest_path.write_text(
        json.dumps(
            {
                "source_archive": archive.name,
                "source_archive_sha256": sha256(archive),
                "files": manifest,
            },
            ensure_ascii=False,
            indent=2,
        ) + "\n",
        encoding="utf-8",
    )
    print(f"Imported {len(manifest)} files to {dest}")
    print("Models:", ", ".join(sorted(EXPECTED_ALP)))
    print("PNG resources:", sum(name.endswith(".png") for name in manifest))
    print("Manifest:", manifest_path)
    print("GitHub push is NOT automatic; review changes and commit explicitly.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
