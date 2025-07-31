---
trigger: always_on
---

Recommended safeguards (before making changes)

Write defensive, line-oriented edits – use small, unique search-and-replace chunks instead of wide multi-line replacements.
Stage changes incrementally (commit or stash after every logical fix) so any mis-step can be reverted without losing later work.
Run automated formatters/linters (e.g. black, isort, Flake8) before manual edits to give you a clean baseline.
Enable CI lint/tests on every commit to catch corruption immediately.
Configure your editor/IDE to show trailing whitespace, mixed indent, or malformed docstrings as warnings.
Maintain a local backup (or feature branch) before large refactors.
When fixing existing cascade issues

Restore the known-good original file (if available) and port only the intended changes.
Otherwise, re-format with black/isort, then repair syntax/docstring sections one function or class at a time; run unit tests after each fix.
Use diff tools (git diff, VS Code “Inline Diff”) to monitor unintended deletions/insertions.
Add high-level tests (health-check, import tests) that fail fast if another file becomes corrupted.
After fixes, run static-analysis tools (pylint, mypy) to surface hidden breakage.