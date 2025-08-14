# Changelog

All notable changes to this project will be documented in this file.

## [0.2.0] - 2025-08-14
### Added
- Feature flags: `NEW_ENGINE` (switch to new architecture) and `DRY_RUN` (deterministic test mode).
- New domain/core layer: `core/interfaces.py`, `core/store.py`, `core/evaluator.py`, `core/runner.py` for pure, testable orchestration logic.
- Service adapters: `core/services.py` with Dry-Run and AutoGen-backed `WriterService` / `ValidatorService` plus `FeedbackParserAdapter`.
- New concurrent engine: `core/runner_engine.py` for feature-flag enabled multi-section execution.
- Extensive test suite reaching ~95% coverage including: section runner, new engine path, service adapters, PDF preprocessing, utilities (sync & async), store implementations, orchestrator and main control-flow (success + failure paths), and entry-point exception handling.
- Additional utility tests for parsing, sanitisation, termination detection, docx generation (mocked), and error branches.

### Changed
- `main.py` refactored to delegate via feature flag and produce structured run summary logs.
- Improved dynamic environment handling for Ollama vs Azure; config now supports local OpenAI-compatible endpoints.
- `build_services` now evaluates `DRY_RUN` at call time allowing per-test toggling without module reload.

### Fixed
- Multiple indentation / syntax issues during service adapter integration.
- Test flakiness due to network calls by isolating AutoGen interactions behind mocks in tests.
- Merge path and revision prompt handling made deterministic in dry-run mode.

### Removed / Deprecated
- Legacy orchestrator retained (`orchestrator.py`) but marked for future deprecation once confidence in new engine is complete.

### Internal / Tooling
- Added comprehensive logging (full + loop trace) and ensured graceful cleanup on exceptions / interrupts.
- Added specialized tests covering error handling in `main.__main__` entry block.

## [0.1.0] - 2025-08-13
### Added
- Initial multi-agent EHCP document generation pipeline with writer and validator teams.
- PDF preprocessing, section drafting/validation loop, merging, and Word document generation.
- Base utilities and configuration system.

## [0.0.1] - Initial
- Project scaffold.

