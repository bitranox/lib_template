# lib_template

<!-- Badges -->
[![CI](https://github.com/bitranox/lib_template/actions/workflows/ci.yml/badge.svg)](https://github.com/bitranox/lib_template/actions/workflows/ci.yml)
[![CodeQL](https://github.com/bitranox/lib_template/actions/workflows/codeql.yml/badge.svg)](https://github.com/bitranox/lib_template/actions/workflows/codeql.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Jupyter](https://img.shields.io/badge/Jupyter-Launch-orange?logo=jupyter)](https://mybinder.org/v2/gh/bitranox/lib_template/HEAD?labpath=notebooks%2FQuickstart.ipynb)
[![PyPI](https://img.shields.io/pypi/v/lib_template.svg)](https://pypi.org/project/lib_template/)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/lib_template.svg)](https://pypi.org/project/lib_template/)
[![Code Style: Ruff](https://img.shields.io/badge/Code%20Style-Ruff-46A3FF?logo=ruff&labelColor=000)](https://docs.astral.sh/ruff/)
[![codecov](https://codecov.io/gh/bitranox/lib_template/graph/badge.svg?token=z1D8JSjWEH)](https://codecov.io/gh/bitranox/lib_template)
[![Maintainability](https://qlty.sh/gh/bitranox/projects/lib_template/maintainability.svg)](https://qlty.sh/gh/bitranox/projects/lib_template)
[![Known Vulnerabilities](https://snyk.io/test/github/bitranox/lib_template/badge.svg)](https://snyk.io/test/github/bitranox/lib_template)

Scaffold for Rich-powered logging helpers:
- Colorful console logging primitives built on Rich
- Configurable themes and contextual data formatting
- CLI entry point to inspect configuration and experiment with output (coming soon)
- Exit-code and messaging helpers powered by lib_cli_exit_tools

## Install

Pick one of the options below. All methods register the `lib_template` and `lib-template` commands on your PATH.

### 1) Standard virtualenv (pip)

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -e .[dev]       # dev install
# or for runtime only:
pip install .
```

### 2) Per-user (no venv)

```bash
pip install --user .
```

Note: respects PEP 668; avoid on system Python if “externally managed”. Ensure `~/.local/bin` (POSIX) is on PATH.

### 3) pipx (isolated, recommended for end users)

```bash
pipx install .
pipx upgrade lib_template
# From Git tag/commit:
pipx install "git+https://github.com/bitranox/lib_template@v0.1.0"
```

### 4) uv (fast installer/runner)

```bash
uv pip install -e .[dev]
uv tool install .
uvx lib_template --help
```

### 5) From artifacts

```bash
python -m build
pip install dist/lib_template-*.whl
pip install dist/lib_template-*.tar.gz   # sdist
```

### 6) Poetry / PDM (project-managed envs)

```bash
# Poetry
poetry add lib_template     # as dependency
poetry install                    # for local dev

# PDM
pdm add lib_template
pdm install
```

### 7) From Git via pip (CI-friendly)

```bash
pip install "git+https://github.com/bitranox/lib_template@v0.1.0#egg=lib_template"
```

### 8) Conda/mamba (optional)

```bash
mamba create -n lib-template python=3.12 pip
mamba activate lib-template
pip install .
```

### 9) System package managers (optional distribution)

- Homebrew formula (macOS): `brew install lib_template` (if published)
- Nix: flake/package for reproducible installs
- Deb/RPM via `fpm` for OS-native packages

### Make Targets

| Target            | Description                                                                                |
|-------------------|--------------------------------------------------------------------------------------------|
| `help`            | Show help                                                                                  |
| `install`         | Install package editable                                                                   |
| `dev`             | Install package with dev extras                                                            |
| `test`            | Lint, type-check, run tests with coverage, upload to Codecov                               |
| `run`             | Run module CLI (requires dev install or src on PYTHONPATH)                                 |
| `version-current` | Print current version from pyproject.toml                                                  |
| `bump`            | Bump version (updates pyproject.toml and CHANGELOG.md)                                     |
| `bump-patch`      | Bump patch version (X.Y.Z -> X.Y.(Z+1))                                                    |
| `bump-minor`      | Bump minor version (X.Y.Z -> X.(Y+1).0)                                                    |
| `bump-major`      | Bump major version ((X+1).0.0)                                                             |
| `clean`           | Remove caches, build artifacts, and coverage                                               |
| `push`            | Commit all changes once and push to GitHub (no CI monitoring)                              |
| `build`           | Build wheel/sdist and attempt conda, brew, and nix builds (auto-installs tools if missing) |
| `menu`            | Interactive TUI to run targets and edit parameters (requires dev dep: textual)             |

#### Target Parameters (env vars)

- Global
  - `PY` (default: `python3`) — Python interpreter used to run scripts
  - `PIP` (default: `pip`) — pip executable used by bootstrap/install

- `install`
  - No specific parameters (respects `PY`, `PIP`).

- `dev`
  - No specific parameters (respects `PY`, `PIP`).

- `test`
  - `COVERAGE=on|auto|off` (default: `on`) — controls pytest coverage run and Codecov upload
  - `SKIP_BOOTSTRAP=1` — skip auto-install of dev tools if missing
  - `TEST_VERBOSE=1` — echo each command executed by the test harness
  - Also respects `CODECOV_TOKEN` when needed for uploads

- `run`
  - No parameters via `make` (always shows `--help`). For custom args: `python scripts/run_cli.py -- <args>`.

- `version-current`
  - No parameters

- `bump`
  - `VERSION=X.Y.Z` — explicit target version
  - `PART=major|minor|patch` — semantic part to bump (default if `VERSION` not set: `patch`)
  - Examples:
    - `make bump VERSION=1.0.2`
    - `make bump PART=minor`

- `bump-patch` / `bump-minor` / `bump-major`
  - No parameters; shorthand for `make bump PART=...`

- `clean`
  - No parameters

- `push`
  - `REMOTE=<name>` (default: `origin`) — git remote to push to

- `build`
  - No parameters via `make`. Advanced: use the script directly, e.g. `python scripts/build.py --no-conda --no-nix`.

- `release`
  - `REMOTE=<name>` (default: `origin`) — git remote to push to
  - Advanced (via script): `python scripts/release.py --retries 5 --retry-wait 3.0`

### Interactive Menu (Textual)

`make menu` launches a colorful terminal UI (powered by `textual`) to browse targets, edit parameters, and run them with live output.

Install dev extras if you haven’t:

```bash
pip install -e .[dev]
```

Run the menu:

```bash
make menu
```

#### Target Details

- `test`: single entry point for local CI — runs ruff lint + format check, pyright, pytest (including doctests) with coverage (enabled by default), and uploads coverage to Codecov if configured (reads `.env`).
- Auto‑bootstrap: `make test` will try to install dev tools (`pip install -e .[dev]`) if `ruff`/`pyright`/`pytest` are missing. Set `SKIP_BOOTSTRAP=1` to skip this behavior.
- `build`: convenient builder — creates Python wheel/sdist, then attempts Conda, Homebrew, and Nix builds. It auto‑installs missing tools (Miniforge, Homebrew, Nix) when needed.
- `install`/`dev`/`user-install`: common install flows for editable or per‑user installs.
- `version-current`: prints current version from `pyproject.toml`.
- `bump`: updates `pyproject.toml` version and inserts a new section in `CHANGELOG.md`. Use `VERSION=X.Y.Z make bump` or `make bump-minor`/`bump-major`/`bump-patch`.
- `pipx-*` and `uv-*`: isolated CLI installations for end users and fast developer tooling.
- `which-cmd`/`verify-install`: quick diagnostics to ensure the command is on PATH.

## Usage

The scaffold keeps a CLI entry point so you can validate packaging flows, but it
currently exposes a single informational command while logging features are
developed:

```bash
lib_template info
lib-template info
python -m lib_template info
```

For library use you gain a configurable dataclass and helper stubs that you can
extend:

```python
import lib_template

lib_template.configure(traceback=True, theme="monokai")
lib_template.print_exception_message("coming soon")  # no-op placeholder
lib_template.reset_defaults()
```

All public functions are intentionally lightweight so you can supply your own
Rich-powered logging behavior.

## Development

```bash
make test                 # ruff + pyright + pytest + coverage (default ON)
SKIP_BOOTSTRAP=1 make test  # skip auto-install of dev deps
COVERAGE=off make test       # disable coverage locally
COVERAGE=on make test        # force coverage and generate coverage.xml/codecov.xml
```

### Packaging sync (Conda/Brew/Nix)

- `make test` and `make push` automatically align the packaging skeletons in `packaging/` with the current `pyproject.toml`:
  - Conda: updates `{% set version = "X.Y.Z" %}` and both `python >=X.Y` constraints to match `requires-python`.
  - Homebrew: updates the source URL tag to `vX.Y.Z` and sets `depends_on "python@X.Y"` to match `requires-python`.
  - Nix: updates the package `version`, example `rev = "vX.Y.Z"`, and switches `pkgs.pythonXYZPackages` / `pkgs.pythonXYZ` to match the minimum Python version from `requires-python`.

- To run just the sync without bumping versions: `python scripts/bump_version.py --sync-packaging`.

- On release tags (`v*.*.*`), CI validates that packaging files are consistent with `pyproject.toml` and will fail if they drift.

## Versioning & Metadata

- Single source of truth for package metadata is `pyproject.toml` (`[project]`).
- The library reads its own installed metadata at runtime via `importlib.metadata` (see `src/lib_template/__init__conf__.py`).
- Do not duplicate the version in code; bump only `pyproject.toml` and update `CHANGELOG.md`.
- Console script name is discovered from entry points; defaults to `lib_template`.

## Packaging Skeletons

Starter files for package managers live under `packaging/`:

- Conda: `packaging/conda/recipe/meta.yaml` (update version + sha256)
- Homebrew: `packaging/brew/Formula/lib-template.rb` (fill sha256 and vendored resources)
- Nix: `packaging/nix/flake.nix` (use working tree or pin to GitHub rev with sha256)

These are templates; fill placeholders (e.g., sha256) before publishing. Version and Python constraints are auto-synced from `pyproject.toml` by `make test`/`make push` and during version bumps.

## CI & Publishing

GitHub Actions workflows are included:

- `.github/workflows/ci.yml` — lint/type/test, build wheel/sdist, verify pipx and uv installs, Nix and Conda builds (CI-only; no local install required).
- `.github/workflows/release.yml` — on tags `v*.*.*`, builds artifacts and publishes to PyPI when `PYPI_API_TOKEN` secret is set.

To publish a release:
1. Bump `pyproject.toml` version and update `CHANGELOG.md`.
2. Tag the commit (`git tag v0.1.1 && git push --tags`).
3. Ensure `PYPI_API_TOKEN` secret is configured in the repo.
4. Release workflow uploads wheel/sdist to PyPI.

Conda/Homebrew/Nix: use files in `packaging/` to submit to their ecosystems. CI also attempts builds to validate recipes, but does not publish automatically.

### Local Codecov uploads

- `make test` (with coverage enabled) generates `coverage.xml` and `codecov.xml`, then attempts to upload via the Codecov CLI or the bash uploader.
- For private repos, set `CODECOV_TOKEN` (see `.env.example`) or export it in your shell.
- For public repos, a token is typically not required.

## License

MIT
