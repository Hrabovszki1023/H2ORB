from __future__ import annotations

import argparse
import shutil
import sys
import tomllib
from collections import deque
from importlib import metadata
from pathlib import Path

from packaging.requirements import InvalidRequirement, Requirement
from packaging.utils import canonicalize_name

CLASSIFIER_LICENSES = {
    "License :: OSI Approved :: Apache Software License": "Apache-2.0",
    "License :: OSI Approved :: BSD License": "BSD License",
    "License :: OSI Approved :: ISC License (ISCL)": "ISC",
    "License :: OSI Approved :: MIT License": "MIT",
    "License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)": "MPL-2.0",
    "License :: OSI Approved :: Python Software Foundation License": "PSF-2.0",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check licenses of an installed dependency tree.")
    parser.add_argument("--root", default="h2orb", help="Installed root distribution to inspect")
    parser.add_argument(
        "--policy",
        type=Path,
        default=Path(__file__).with_name("license-policy.toml"),
    )
    parser.add_argument("--output", type=Path, help="Write a third-party notice summary")
    parser.add_argument("--license-dir", type=Path, help="Copy packaged license files here")
    return parser.parse_args()


def license_name(distribution: metadata.Distribution) -> str:
    package_metadata = distribution.metadata
    expression = package_metadata.get("License-Expression")
    if expression and expression.strip().upper() != "UNKNOWN":
        return expression.strip()

    declared = package_metadata.get("License")
    if declared and declared.strip().upper() != "UNKNOWN":
        return declared.strip()

    classifiers = package_metadata.get_all("Classifier", [])
    detected = [CLASSIFIER_LICENSES[item] for item in classifiers if item in CLASSIFIER_LICENSES]
    return " OR ".join(sorted(set(detected))) if detected else "UNKNOWN"


def dependency_tree(root: str) -> list[metadata.Distribution]:
    queue: deque[tuple[str, frozenset[str]]] = deque([(root, frozenset())])
    visited: dict[str, set[str]] = {}
    distributions: dict[str, metadata.Distribution] = {}

    while queue:
        requested_name, extras = queue.popleft()
        name = canonicalize_name(requested_name)
        seen_extras = visited.setdefault(name, set())
        if name in distributions and extras.issubset(seen_extras):
            continue

        try:
            distribution = metadata.distribution(requested_name)
        except metadata.PackageNotFoundError as error:
            message = f"Required distribution is not installed: {requested_name}"
            raise RuntimeError(message) from error

        distributions[name] = distribution
        seen_extras.update(extras)
        environments = [{"extra": ""}, *({"extra": extra} for extra in sorted(extras))]

        for raw_requirement in distribution.requires or []:
            try:
                requirement = Requirement(raw_requirement)
            except InvalidRequirement as error:
                package_name = distribution.metadata["Name"]
                message = f"Invalid requirement metadata in {package_name}: {raw_requirement}"
                raise RuntimeError(message) from error
            if requirement.marker and not any(
                requirement.marker.evaluate(environment) for environment in environments
            ):
                continue
            queue.append((requirement.name, frozenset(requirement.extras)))

    root_name = canonicalize_name(root)
    return [distributions[name] for name in sorted(distributions) if name != root_name]


def source_url(distribution: metadata.Distribution) -> str:
    for project_url in distribution.metadata.get_all("Project-URL", []):
        label, separator, url = project_url.partition(",")
        if separator and label.strip().lower() in {"homepage", "repository", "source"}:
            return url.strip()
    return distribution.metadata.get("Home-page") or "UNKNOWN"


def copy_license_files(distribution: metadata.Distribution, target_root: Path) -> list[Path]:
    copied: list[Path] = []
    package_name = canonicalize_name(distribution.metadata["Name"])
    for relative_path in distribution.files or []:
        parts = [part.lower() for part in relative_path.parts]
        filename = relative_path.name.lower()
        if not (
            "licenses" in parts
            or filename.startswith(("license", "licence", "copying", "notice", "copyright"))
        ):
            continue
        source = Path(distribution.locate_file(relative_path))
        if not source.is_file():
            continue
        destination = target_root / package_name / relative_path.name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, destination)
        copied.append(destination.relative_to(target_root.parent))
    return copied


def main() -> int:
    args = parse_args()
    policy = tomllib.loads(args.policy.read_text(encoding="utf-8"))
    allowed = set(policy.get("allowed", []))
    reviewed = policy.get("reviewed", {})
    rows: list[tuple[str, str, str, str, str]] = []
    failures: list[str] = []

    if args.license_dir:
        if args.license_dir.exists():
            shutil.rmtree(args.license_dir)
        args.license_dir.mkdir(parents=True)

    for distribution in dependency_tree(args.root):
        name = distribution.metadata["Name"]
        canonical_name = canonicalize_name(name)
        detected_license = license_name(distribution)
        review = reviewed.get(canonical_name, {})
        accepted = detected_license in allowed or detected_license in review.get("licenses", [])
        if detected_license in allowed:
            decision = "allowed"
        else:
            decision = "reviewed" if accepted else "blocked"
        if not accepted:
            failures.append(f"{name}=={distribution.version}: {detected_license}")

        license_files: list[Path] = []
        if args.license_dir:
            license_files = copy_license_files(distribution, args.license_dir)
        rows.append(
            (
                name,
                distribution.version,
                detected_license,
                decision,
                source_url(distribution),
            )
        )
        print(f"{decision:8} {name}=={distribution.version}: {detected_license}")
        if args.license_dir and not license_files:
            failures.append(f"{name}=={distribution.version}: no packaged license file found")

    if args.output:
        lines = [
            "# Third-party notices",
            "",
            "This file is generated from the exact installed H2ORB runtime dependency set.",
            "Full license and notice files are stored in `third-party-licenses/`.",
            "",
            "| Package | Version | License | Decision | Source |",
            "|---|---:|---|---|---|",
        ]
        lines.extend(
            f"| {name} | {version} | {license_value} | {decision} | {url} |"
            for name, version, license_value, decision, url in rows
        )
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text("\n".join(lines) + "\n", encoding="utf-8")

    if failures:
        print("\nLicense policy failed:", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1

    print(f"\nLicense policy passed for {len(rows)} runtime dependencies.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
