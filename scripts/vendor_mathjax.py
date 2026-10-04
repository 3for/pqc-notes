#!/usr/bin/env python3
"""Reproduce the site's self-hosted MathJax files from pinned npm archives.

Uses only the Python standard library. No npm lifecycle scripts are executed.
Run from any directory: python3 scripts/vendor_mathjax.py
Use --archive-dir with previously downloaded tarballs for an offline rebuild.
"""

import argparse
import base64
import hashlib
import hmac
import io
import json
from pathlib import Path, PurePosixPath
import shutil
import tarfile
import tempfile
import urllib.request


ROOT = Path(__file__).resolve().parents[1]
DESTINATION = ROOT / "docs/assets/vendor"
PACKAGES = (
    {
        "name": "mathjax",
        "version": "4.1.3",
        "directory": "mathjax",
        "url": "https://registry.npmjs.org/mathjax/-/mathjax-4.1.3.tgz",
        "integrity": "sha512-BN/8Pkgn7G1pIDYJqd9md+JHsE/jydSYbyOZnSdSA0WziuVO8mRxdYiWFumkVVly/8U+hm9DpIIoWuvySverzw==",
    },
    {
        "name": "@mathjax/mathjax-newcm-font",
        "version": "4.1.3",
        "directory": "mathjax-newcm-font",
        "url": "https://registry.npmjs.org/@mathjax/mathjax-newcm-font/-/mathjax-newcm-font-4.1.3.tgz",
        "integrity": "sha512-gzAB3dFHilHX1l5x2xUqRL+1jDQt3Fyza1DkEMVXWC4E8SvsGdlgEza47HYi2WhVcgfkvf4zgUGzuhbq3Pjlew==",
    },
)


def fetch(package, archive_dir):
    """Verify the complete archive before parsing or writing any member."""
    filename = package["url"].rsplit("/", 1)[1]
    if archive_dir:
        data = (archive_dir / filename).read_bytes()
    else:
        request = urllib.request.Request(
            package["url"], headers={"User-Agent": "pqc-notes-vendor/1"}
        )
        with urllib.request.urlopen(request, timeout=60) as response:
            data = response.read()
    algorithm, expected = package["integrity"].split("-", 1)
    actual = base64.b64encode(hashlib.new(algorithm, data).digest()).decode()
    if not hmac.compare_digest(actual, expected):
        raise ValueError(f"Integrity mismatch for {package['name']}")
    return data


def keep_runtime_file(package, path):
    """Keep browser bundles and every dynamic runtime directory, not sources."""
    if path.name in {"LICENSE", "NOTICE", "COPYING", "package.json"}:
        return len(path.parts) == 1
    if path.suffix not in {".js", ".json", ".woff", ".woff2"}:
        return False
    if package["directory"] == "mathjax":
        if len(path.parts) == 1:
            # The site loads only this combined entry point. Keep the separate
            # loader/startup/core components, but not duplicate combinations.
            return path.name in {"tex-chtml.js", "core.js", "loader.js", "startup.js"}
        return path.parts[0] in {"a11y", "input", "output", "sre", "ui"}
    return path.parts[0] in {"chtml", "svg"} or str(path) in {"chtml.js", "svg.js"}


def extract(package, data, destination):
    count = 0
    with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as archive:
        metadata = json.load(archive.extractfile("package/package.json"))
        for key in ("name", "version"):
            if metadata[key] != package[key]:
                raise ValueError(f"Unexpected {key} in {package['name']}")
        if metadata.get("license") != "Apache-2.0":
            raise ValueError(f"Review changed license for {package['name']}")
        seen = set()
        for member in archive:
            raw_parts = member.name.split("/")
            if (
                member.name.startswith("/")
                or ".." in raw_parts
                or "\\" in member.name
                or raw_parts[0] != "package"
            ):
                raise ValueError(f"Unsafe archive path: {member.name}")
            if member.isdir():
                continue
            if not member.isfile():
                raise ValueError(f"Unsupported archive member: {member.name}")
            path = PurePosixPath(*raw_parts[1:])
            if not keep_runtime_file(package, path):
                continue
            if path in seen:
                raise ValueError(f"Duplicate archive member: {member.name}")
            seen.add(path)
            target = destination.joinpath(*path.parts)
            target.parent.mkdir(parents=True, exist_ok=True)
            with archive.extractfile(member) as source, target.open("wb") as output:
                shutil.copyfileobj(source, output)
            count += 1
    return count


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive-dir", type=Path, help="read pinned .tgz files here")
    args = parser.parse_args()
    archives = [(package, fetch(package, args.archive_dir)) for package in PACKAGES]
    DESTINATION.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".mathjax-", dir=DESTINATION.parent) as tmp:
        stage = Path(tmp)
        counts = {}
        for package, data in archives:
            counts[package["name"]] = extract(package, data, stage / package["directory"])

        # The font archive declares Apache-2.0 in package.json but omits a
        # LICENSE file. Include the unmodified license text shipped by MathJax.
        shutil.copyfile(stage / "mathjax/LICENSE", stage / "mathjax-newcm-font/LICENSE")
        readme = [
            "Self-hosted MathJax browser runtime and New Computer Modern fonts.",
            "Generated by: python3 scripts/vendor_mathjax.py",
            "Official registry: https://registry.npmjs.org/",
            "Hosting guide: https://docs.mathjax.org/en/latest/web/hosting.html",
            "",
        ]
        for package in PACKAGES:
            readme.extend([
                f"Package: {package['name']}@{package['version']}",
                f"Directory: {package['directory']}/",
                f"Source: {package['url']}",
                f"Integrity: {package['integrity']}",
                "License: Apache-2.0 (declared in the original package.json)",
                "",
            ])
        readme.extend([
            "The font npm archive omits LICENSE. Its LICENSE here is the unchanged",
            "Apache-2.0 license text supplied in the MathJax npm archive.",
            "JavaScript/font contents are unchanged. Browser runtime files, dynamic",
            "font ranges, speech data and package metadata are retained. Source maps,",
            "development sources, Node entry points, examples and docs are omitted.",
            "Only tex-chtml.js is retained as a combined top-level entry point.",
            "Separate SVG output/font data are retained for the MathJax renderer menu.",
            "MathJax and the font package must be served from these local directories;",
            "configure output.fontPath to point at mathjax-newcm-font/.",
            "",
        ])
        (stage / "README.txt").write_text("\n".join(readme), encoding="utf-8")
        manifest = {
            path.relative_to(stage).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in sorted(stage.rglob("*")) if path.is_file()
        }
        (stage / "manifest.json").write_text(
            json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )

        if DESTINATION.is_symlink():
            raise ValueError("Vendor destination must not be a symlink")
        DESTINATION.mkdir(parents=True, exist_ok=True)
        for package in PACKAGES:
            target = DESTINATION / package["directory"]
            if target.is_symlink():
                raise ValueError(f"Package destination must not be a symlink: {target}")
        for package in PACKAGES:
            target = DESTINATION / package["directory"]
            if target.exists():
                shutil.rmtree(target)
            shutil.move(str(stage / package["directory"]), target)
        for filename in ("README.txt", "manifest.json"):
            (stage / filename).replace(DESTINATION / filename)
        for name, count in counts.items():
            print(f"Vendored {name}: {count} verified runtime files")


if __name__ == "__main__":
    main()
