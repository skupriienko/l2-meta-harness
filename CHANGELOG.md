# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html)
with secondary CalVer release tracking (`YYYY.MM.DD.N`).

## [1.1.0] - 2026-11-03 (CalVer: 2026.11.03.1)

### Changed
- Refactored `MetaHarness` with typed dataclasses (`OversizedSkill`, `EvalResult`).
- Added bounded memory streaming for rule files up to 500KB.
- Stress benchmarked across 100 skills and 50 rules.

## [1.0.0] - 2026-11-02 (CalVer: 2026.11.02.1)

### Added
- Initial public open-source release of `l2-meta-harness` (Level-2 Recursive Meta-Harness & Drift Evaluator (Harness²)).
- Harness² evaluator auditing agent instruction health and behavioral drift.
- Enforces 24KB agent skill limits and 20,000-token rules budget ceilings.
- Detects circular references, broken metadata, and hook budget exhaustion.
- Zero-dependency Python standard library architecture.
- Full PEP 517/621 packaging (`pyproject.toml`, `setup.py`, `MANIFEST.in`, `src/*/py.typed`).
- Native Kilo Code / Kilo integration (`.kilo/kilo.jsonc`, `.kilo/rules/`, `.kilocoderules`).
- Developer tooling: Ruff linter, Mypy strict typing, pre-commit hooks, GitHub Actions CI matrix (Python 3.10–3.13).
- Comprehensive stress benchmarks under extreme concurrency (`tests/test_stress.py`).
- One-line deployment script (`install.sh`).
- Permissive MIT License.
