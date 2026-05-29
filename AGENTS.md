# AGENTS.md

## Cursor Cloud specific instructions

This repository (`uds-mesh`) is a **schema/governance repository**, not a traditional application. There is no build step, no runtime server, and no `package.json`. The development workflow consists of:

### Lint

```sh
pre-commit run --all-files
```

> **Note:** You must first unset `core.hooksPath` if it is configured: `git config --unset-all core.hooksPath` before running `pre-commit install`.

### Test

```sh
bash schemas/spans/test_graph_spans.sh
```

This is the only automated test. It validates the OTEL span schema YAML (`schemas/spans/a11oy.graph.yaml`) using grep-based assertions (25 checks).

### Governance file validation (mirrors CI)

The CI workflow (`.github/workflows/ci.yml`) checks that these files exist: `README.md`, `LICENSE`, `SECURITY.md`, `CODE_OF_CONDUCT.md`, `CONTRIBUTING.md`, `CITATION.cff`, and verifies ORCID presence in `CITATION.cff` and existence of `uds-bundle.yaml`.

### Gotchas

- The `check-yaml` pre-commit hook fails on `schemas/spans/a11oy.graph.yaml` because that file uses non-standard YAML formatting (intentional schema notation). This is a known pre-existing condition in the repository.
- There is no `package.json` or Node.js code in this repo despite the devcontainer referencing Node 20. The actual TypeScript code lives in companion repos.
- DCO sign-off is required on all commits (`git commit -s`).
