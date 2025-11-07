# Changelog

All notable changes to this project will be documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.0] - 2025-10-24

### Added

- Run auditing & archiving system copying source, outputs, and logs into timestamped folders in `run-archive`.
- Modular `src/ehcp_autogen` package structure; dedicated `templates/` and `documentation/` asset folders.
- Professional project docs: `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`, plus expanded README.

### Changed

- Deployment model aligned to Azure Container App Jobs for cost‑efficient batch processing.
- Full Azure Blob Storage integration for all file I/O.
- Refactored blocking I/O to async (executor + native aio libs) to eliminate startup deadlocks.

### Fixed

- Deadlock on startup due to synchronous file/blob I/O.
- Orchestrator robustness for unexpected agent reply types.

### Removed

- Legacy local-only assumptions; project now fully cloud-native.

## [0.2.0] - 2025-08-14

### Added

- Feature flags: `NEW_ENGINE` (alternate concurrency architecture) and `DRY_RUN` (deterministic test mode).
- Domain/core layer: `core/interfaces.py`, `core/store.py`, `core/evaluator.py`, `core/runner.py` for pure, testable orchestration logic.
- Service adapters: `core/services.py` (Dry-Run + AutoGen-backed `WriterService` / `ValidatorService` + `FeedbackParserAdapter`).
- Concurrent engine: `core/runner_engine.py` (feature-flag path for multi-section execution).
- Extensive test suite (~95% coverage) including: section runner, new engine path, service adapters, PDF preprocessing, utilities (sync & async), stores, orchestrator & main control-flow (success/failure), entry-point exception handling.
- Utility tests for parsing, sanitisation, termination detection, docx generation (mocked), error branches.

### Changed

- `main.py` delegates via feature flag and emits structured run summary logs.
- Dynamic environment handling for Ollama vs Azure; config supports OpenAI-compatible local endpoints.
- `build_services` evaluates `DRY_RUN` at call time for per-test toggling without module reload.

### Fixed

- Indentation / syntax issues during adapter integration.
- Test flakiness via isolating AutoGen interactions behind mocks.
- Deterministic merge path & revision prompt handling in dry-run mode.

### Deprecated

- Legacy orchestrator (`orchestrator.py`) retained but slated for removal after confidence in new engine.

### Internal / Tooling

- Comprehensive logging (full + loop trace) and graceful cleanup on exceptions/interrupts.
- Specialized tests for error handling in `main.__main__` entry block.

## [0.1.0] - 2025-08-13

### Added

- Initial multi-agent EHCP document generation pipeline with writer & validator teams.
- PDF preprocessing, section drafting/validation loop, merging, Word document generation.
- Base utilities and configuration system.

## [0.0.1] - Initial

- Project scaffold.
