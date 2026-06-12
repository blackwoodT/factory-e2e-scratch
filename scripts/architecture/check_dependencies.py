#!/usr/bin/env python3
"""Config-driven structural dependency checker for template bootstraps.

This script is intentionally stack-neutral. It does not parse one language's import
syntax or resolve one package system. Downstream projects provide boundary globs,
dependency extraction patterns, and allowed/forbidden edges in JSON config.
"""
from __future__ import annotations

import argparse
import fnmatch
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

EXIT_OK = 0
EXIT_VIOLATION = 1
EXIT_CONFIG = 2


@dataclass(frozen=True)
class Boundary:
    id: str
    paths: tuple[str, ...]


@dataclass(frozen=True)
class DependencyPattern:
    id: str
    regex: re.Pattern[str]


@dataclass(frozen=True)
class EdgeRule:
    id: str
    source: str
    target: str
    reason: str
    remediation: str


@dataclass(frozen=True)
class Finding:
    file: str
    line: int
    source_boundary: str
    dependency: str
    target_boundary: str
    rule_id: str
    edge: str
    reason: str
    remediation: str
    pattern_id: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check configured architecture dependency boundaries."
    )
    parser.add_argument(
        "--config",
        default="docs/design-docs/architecture-boundaries.json",
        help="Path to project-specific JSON config. Defaults to docs/design-docs/architecture-boundaries.json.",
    )
    parser.add_argument(
        "--root",
        default=".",
        help="Repo/project root used for configured path globs. Defaults to current directory.",
    )
    parser.add_argument(
        "--expect-violation",
        action="store_true",
        help="Self-test mode: exit 0 only when at least one violation is found.",
    )
    return parser.parse_args()


def load_config(config_path: Path) -> dict[str, Any]:
    if not config_path.exists():
        print(
            "Structural dependency config not found.\n"
            f"Expected: {config_path}\n\n"
            "Remediation for agents:\n"
            "- During downstream bootstrap, generate a project-specific config from "
            "docs/design-docs/architecture-contract.md.\n"
            "- Use docs/design-docs/architecture-boundaries-template.json as a starting point, "
            "replace all example domains/paths/rules, and set template_only to false.\n"
            "- If this ticket does not touch dependency boundaries or enforcement is not configured yet, "
            "record this check as skipped with reason and residual risk in the validation evidence.",
            file=sys.stderr,
        )
        sys.exit(EXIT_CONFIG)

    try:
        data = json.loads(config_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"Invalid structural dependency config JSON: {config_path}: {exc}", file=sys.stderr)
        sys.exit(EXIT_CONFIG)

    if data.get("template_only") is True:
        print(
            "Refusing to run structural dependency checks with a template-only config.\n"
            f"Config: {config_path}\n\n"
            "Remediation for agents:\n"
            "- Generate a downstream project-specific config from the generated architecture contract.\n"
            "- Replace example boundary names, path globs, dependency patterns, and edge rules.\n"
            "- Set template_only to false only after the config reflects real project policy.",
            file=sys.stderr,
        )
        sys.exit(EXIT_CONFIG)

    return data


def require_list(config: dict[str, Any], key: str) -> list[Any]:
    value = config.get(key)
    if not isinstance(value, list) or not value:
        print(f"Config must define a non-empty `{key}` list.", file=sys.stderr)
        sys.exit(EXIT_CONFIG)
    return value


def compile_boundaries(config: dict[str, Any]) -> list[Boundary]:
    boundaries: list[Boundary] = []
    for item in require_list(config, "boundaries"):
        if not isinstance(item, dict) or not isinstance(item.get("id"), str):
            print("Every boundary must be an object with string `id`.", file=sys.stderr)
            sys.exit(EXIT_CONFIG)
        paths = item.get("paths")
        if not isinstance(paths, list) or not paths or not all(isinstance(p, str) for p in paths):
            print(f"Boundary `{item.get('id')}` must define non-empty string `paths`.", file=sys.stderr)
            sys.exit(EXIT_CONFIG)
        boundaries.append(Boundary(item["id"], tuple(paths)))
    return boundaries


def compile_patterns(config: dict[str, Any]) -> list[DependencyPattern]:
    patterns: list[DependencyPattern] = []
    for item in require_list(config, "dependency_patterns"):
        if not isinstance(item, dict) or not isinstance(item.get("id"), str) or not isinstance(item.get("regex"), str):
            print("Every dependency pattern must define string `id` and `regex`.", file=sys.stderr)
            sys.exit(EXIT_CONFIG)
        try:
            compiled = re.compile(item["regex"])
        except re.error as exc:
            print(f"Invalid regex for dependency pattern `{item['id']}`: {exc}", file=sys.stderr)
            sys.exit(EXIT_CONFIG)
        if "target" not in compiled.groupindex:
            print(f"Dependency pattern `{item['id']}` must include a named (?P<target>...) group.", file=sys.stderr)
            sys.exit(EXIT_CONFIG)
        patterns.append(DependencyPattern(item["id"], compiled))
    return patterns


def compile_rules(config: dict[str, Any], key: str) -> list[EdgeRule]:
    rules: list[EdgeRule] = []
    for index, item in enumerate(config.get(key, [])):
        if not isinstance(item, dict):
            print(f"Every `{key}` entry must be an object.", file=sys.stderr)
            sys.exit(EXIT_CONFIG)
        source = item.get("from")
        target = item.get("to")
        if not isinstance(source, str) or not isinstance(target, str):
            print(f"Every `{key}` entry must define string `from` and `to`.", file=sys.stderr)
            sys.exit(EXIT_CONFIG)
        rules.append(
            EdgeRule(
                id=str(item.get("id") or f"{key}-{index + 1}"),
                source=source,
                target=target,
                reason=str(item.get("reason") or "Configured architecture boundary rule."),
                remediation=str(
                    item.get("remediation")
                    or "Move the dependency behind an allowed boundary, or update the architecture contract/config if the boundary policy changed."
                ),
            )
        )
    return rules


def normalize(path: Path | str) -> str:
    return str(path).replace("\\", "/").lstrip("./")


def matches(pattern: str, value: str) -> bool:
    normalized = normalize(value)
    return fnmatch.fnmatch(normalized, pattern) or fnmatch.fnmatch(f"./{normalized}", pattern)


def boundary_for_path(rel_path: str, boundaries: Iterable[Boundary]) -> str | None:
    for boundary in boundaries:
        if any(matches(pattern, rel_path) for pattern in boundary.paths):
            return boundary.id
    return None


def iter_candidate_files(root: Path, boundaries: Iterable[Boundary]) -> Iterable[Path]:
    seen: set[Path] = set()
    for path in root.rglob("*"):
        if not path.is_file() or path in seen:
            continue
        rel_path = normalize(path.relative_to(root))
        if boundary_for_path(rel_path, boundaries) is not None:
            seen.add(path)
            yield path


def target_boundary_for_dependency(target: str, boundaries: Iterable[Boundary]) -> str | None:
    normalized_target = normalize(target)
    return boundary_for_path(normalized_target, boundaries)


def edge_matches(rule: EdgeRule, source: str, target: str) -> bool:
    return (rule.source == source or rule.source == "*") and (rule.target == target or rule.target == "*")


def ignored(source: str, target: str, dependency: str, config: dict[str, Any]) -> bool:
    for item in config.get("ignored_dependencies", []):
        if not isinstance(item, dict):
            continue
        source_match = item.get("from", source) in (source, "*")
        target_match = item.get("to", target) in (target, "*")
        dep_pattern = item.get("dependency")
        dep_match = not isinstance(dep_pattern, str) or matches(dep_pattern, dependency)
        if source_match and target_match and dep_match:
            return True
    return False


def check(config: dict[str, Any], root: Path) -> list[Finding]:
    boundaries = compile_boundaries(config)
    patterns = compile_patterns(config)
    allowed = compile_rules(config, "allowed_edges")
    forbidden = compile_rules(config, "forbidden_edges")
    findings: list[Finding] = []

    for file_path in iter_candidate_files(root, boundaries):
        rel_path = normalize(file_path.relative_to(root))
        source_boundary = boundary_for_path(rel_path, boundaries)
        if source_boundary is None:
            continue
        try:
            lines = file_path.read_text(encoding="utf-8").splitlines()
        except UnicodeDecodeError:
            continue
        for line_number, line in enumerate(lines, start=1):
            for pattern in patterns:
                match = pattern.regex.search(line)
                if not match:
                    continue
                dependency = normalize(match.group("target").strip().strip('"\''))
                target_boundary = target_boundary_for_dependency(dependency, boundaries)
                if target_boundary is None or target_boundary == source_boundary:
                    continue
                if ignored(source_boundary, target_boundary, dependency, config):
                    continue
                forbidden_rule = next((rule for rule in forbidden if edge_matches(rule, source_boundary, target_boundary)), None)
                allowed_rule = next((rule for rule in allowed if edge_matches(rule, source_boundary, target_boundary)), None)
                if forbidden_rule is not None:
                    rule = forbidden_rule
                elif allowed and allowed_rule is None:
                    rule = EdgeRule(
                        id="implicit-not-allowed",
                        source=source_boundary,
                        target=target_boundary,
                        reason="This dependency edge is not present in configured allowed_edges.",
                        remediation="Route the dependency through an allowed boundary, or update the architecture contract and structural config if the architecture changed.",
                    )
                else:
                    continue
                findings.append(
                    Finding(
                        file=rel_path,
                        line=line_number,
                        source_boundary=source_boundary,
                        dependency=dependency,
                        target_boundary=target_boundary,
                        rule_id=rule.id,
                        edge=f"{source_boundary} -> {target_boundary}",
                        reason=rule.reason,
                        remediation=rule.remediation,
                        pattern_id=pattern.id,
                    )
                )
    return findings


def print_findings(findings: list[Finding], config_path: Path) -> None:
    print("Structural dependency boundary violations found:")
    print(f"Config: {config_path}")
    for index, finding in enumerate(findings, start=1):
        print(f"\n{index}. Forbidden dependency edge: {finding.edge}")
        print(f"   Location: {finding.file}:{finding.line}")
        print(f"   Source boundary: {finding.source_boundary}")
        print(f"   Dependency target: {finding.dependency}")
        print(f"   Target boundary: {finding.target_boundary}")
        print(f"   Rule: {finding.rule_id}")
        print(f"   Dependency pattern: {finding.pattern_id}")
        print(f"   Why this failed: {finding.reason}")
        print(f"   Remediation for agents: {finding.remediation}")
    print(
        "\nIf this dependency is intentional, update the generated architecture contract first, "
        "then update the structural dependency config with the new allowed edge or a narrow ignored_dependency entry with a reason."
    )


def main() -> int:
    args = parse_args()
    root = Path(args.root).resolve()
    config_path = Path(args.config).resolve()
    config = load_config(config_path)
    findings = check(config, root)

    if args.expect_violation:
        if findings:
            print_findings(findings, config_path)
            print("\nSelf-test passed: expected violation was detected.")
            return EXIT_OK
        print("Self-test failed: expected at least one structural dependency violation.", file=sys.stderr)
        return EXIT_VIOLATION

    if findings:
        print_findings(findings, config_path)
        return EXIT_VIOLATION

    print("Structural dependency check passed: no forbidden configured edges found.")
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
