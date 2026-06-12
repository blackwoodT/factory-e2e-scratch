# Security Review Policy

Security review is risk-based by default. The normal two-pass review remains the baseline, but the orchestrator must add a security implementation sub-ticket, an independent security review gate, or both when a slice touches security-sensitive scope.

## Role split
- `$sec-specialist` is the implementation specialist for security-focused code, configuration, dependency, or infrastructure changes. It follows the implementer state machine and writes `implement.md`.
- `$sec-reviewer` is the independent security review gate. It follows reviewer-style behavior, reviews and comments on the GitHub PR, writes the security gate record to `review.md`, and does not implement fixes during the gate unless explicitly rerouted by the human.

## When security review is required
Require a `$sec-reviewer` security review gate, a `$sec-specialist` implementation sub-ticket, or both when a slice touches:
- authentication, authorization, sessions, roles, or permissions
- secrets, credentials, certificates, tokens, or key material
- personally identifiable information or sensitive student/staff data
- payments, financial records, or regulated/compliance-sensitive workflows
- network exposure, CORS, CSP, headers, file upload/download, or external webhooks
- database access patterns that could create injection, leakage, or tenancy risks
- dependency, container, CI/CD, infrastructure, or cloud permission changes

## Third pass guidance
Do not make every ticket a mandatory three-pass review by default. A universal third pass increases latency and can train agents to treat security as a checkbox. Prefer:
1. baseline two-pass review for ordinary low-risk slices
2. required `$sec-reviewer` security review gate for security-sensitive slices that need independent review
3. required `$sec-specialist` implementation sub-ticket when security-focused implementation work is separable from the parent slice
4. optional mandatory third pass for projects with high compliance or threat exposure

## Security review output
Security review should check for code flaws and broader best-practice risks, including:
- threat model fit for the feature
- least privilege and data minimization
- secure defaults and failure modes
- audit/logging requirements without leaking secrets
- dependency and deployment risk

The `$sec-reviewer` final answer must use the security review gate final-answer template in `workflow-reference.md` and `.roles/sec-reviewer.md`.

The `$sec-reviewer` must also leave a GitHub PR comment or review comment for accepted gates that states the pass id, tool/role, current head SHA, and acceptance result. For blocking findings, it should submit a `REQUEST_CHANGES` review with line-level comments when possible.

Findings that repeat should be promoted into docs, custom lints, structural tests, or validation contracts.
