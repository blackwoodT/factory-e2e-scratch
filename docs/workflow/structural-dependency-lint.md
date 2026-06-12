# Structural Dependency Lint

Purpose: make project-specific architecture boundaries mechanically checkable after a downstream project has generated its own architecture contract.

This is a template scaffold, not a universal architecture. Downstream projects choose their own boundary names, path globs, dependency extraction patterns, allowed edges, forbidden edges, and narrow ignores.

## Relationship to the architecture contract

`docs/design-docs/architecture-contract.md` is the human-readable project contract generated during bootstrap. A project-specific structural dependency config is the machine-readable enforcement projection of the contract's dependency-boundary rules.

Recommended generated config path:

```text
docs/design-docs/architecture-boundaries.json
```

Use `docs/design-docs/architecture-boundaries-template.json` as a starting point only. The template file must not be used as active policy; it is marked `template_only: true`, and the checker refuses to run with template-only configs.

## Bootstrap expectations

During initial downstream bootstrap, the architect/orchestrator should:

1. Generate `docs/design-docs/architecture-contract.md` from `docs/design-docs/architecture-contract-template.md`.
2. Identify which dependency-boundary rules are ready for mechanical enforcement.
3. Create `docs/design-docs/architecture-boundaries.json` from the template config.
4. Replace every example boundary, path glob, dependency pattern, allowed edge, forbidden edge, remediation, and ignore with project-specific values.
5. Set `template_only` to `false` only after the config reflects real project policy.
6. Record in the architecture contract which rules are linted, manually reviewed, docs-only, or intentionally deferred.

If the project has no enforceable structural dependency model yet, leave the checker unconfigured and record boundary-lint validation as skipped with reason and residual risk when a ticket touches dependency boundaries.

## Checker command

Default command:

```bash
python scripts/architecture/check_dependencies.py
```

Explicit config/root command:

```bash
python scripts/architecture/check_dependencies.py --config docs/design-docs/architecture-boundaries.json --root .
```

The checker is intentionally stack-neutral. It reads configured path globs and dependency extraction regexes; it does not assume a programming language, import syntax, framework, package manager, module resolver, or source-root convention.

## Config model

A project-specific config should include:

- `schema_version`: config schema version.
- `template_only`: must be `false` for active downstream policy.
- `source_contract`: path to the generated architecture contract.
- `coverage_notes`: what is mechanically enforced and what remains manual/docs-only.
- `boundaries`: project-specific boundary IDs and path globs.
- `dependency_patterns`: regex patterns with a named `(?P<target>...)` group.
- `allowed_edges`: dependency edges allowed by the generated contract.
- `forbidden_edges`: dependency edges forbidden by the generated contract.
- `ignored_dependencies`: narrow, reasoned exceptions for generated code or approved temporary cases.

Prefer small configs. Promote new rules only when they are reviewable and useful.

## Failure behavior

The checker fails closed when:

- no config exists at the selected path,
- the config is invalid JSON,
- the selected config is still marked `template_only: true`,
- required config lists are missing,
- a dependency pattern lacks the required named `target` group.

The checker exits with:

- `0` when no configured violations are found,
- `1` when forbidden or not-allowed configured edges are found,
- `2` when configuration is missing or invalid.

## Agent-legible findings

Violation output should explain:

- the file and line where the dependency was found,
- the source boundary,
- the dependency target,
- the resolved target boundary,
- the forbidden edge,
- the rule/config entry that produced the finding,
- why the rule exists,
- how an agent should remediate or update the architecture contract/config.

If a dependency is intentional, update the generated architecture contract first, then update the config with a new allowed edge or a narrow ignored dependency entry with a reason.

## Validation evidence

When a ticket touches dependency boundaries and a project-specific config exists, the orchestrator should include the structural checker in the validation contract. The implementer should record the exact command, result, and any findings/remediation in `implement.md` and optional `state.json.validation.evidence` when useful.

When the checker is not configured, record a skip with reason and residual risk rather than treating missing enforcement as a pass.

## Template self-test fixture

The template includes a fixture under `scripts/architecture/fixtures/structural-dependencies/`. The fixture uses a generic `depends-on:` marker so it can prove forbidden-edge detection without assuming one language or folder layout.

Run the self-test with:

```bash
python scripts/architecture/check_dependencies.py --config scripts/architecture/fixtures/structural-dependencies/architecture-boundaries.fixture.json --root scripts/architecture/fixtures/structural-dependencies --expect-violation
```

This command should pass by detecting the intentional fixture violation.

## Future optional adapters

Language-specific import resolvers, package/module graph adapters, or framework-specific rules may be added later as optional examples. They should plug into the same project-specific config model and must be clearly marked as examples, not universal policy.
