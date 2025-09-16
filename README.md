# lib_template

<!-- Badges -->
[![CI](https://github.com/bitranox/lib_template/actions/workflows/ci.yml/badge.svg)](https://github.com/bitranox/lib_template/actions/workflows/ci.yml)
[![CodeQL](https://github.com/bitranox/lib_template/actions/workflows/codeql.yml/badge.svg)](https://github.com/bitranox/lib_template/actions/workflows/codeql.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Jupyter](https://img.shields.io/badge/Jupyter-Launch-orange?logo=jupyter)](https://mybinder.org/v2/gh/bitranox/lib_template/HEAD?labpath=notebooks%2FQuickstart.ipynb)
[![PyPI](https://img.shields.io/pypi/v/lib_template.svg)](https://pypi.org/project/lib_template/)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/lib_template.svg)](https://pypi.org/project/lib_template/)
[![Code Style: Ruff](https://img.shields.io/badge/Code%20Style-Ruff-46A3FF?logo=ruff&labelColor=000)](https://docs.astral.sh/ruff/)
[![codecov](https://codecov.io/gh/bitranox/lib_template/graph/badge.svg?token=UFBaUDIgRk)](https://codecov.io/gh/bitranox/lib_template)
[![Maintainability](https://qlty.sh/badges/041ba2c1-37d6-40bb-85a0-ec5a8a0aca0c/maintainability.svg)](https://qlty.sh/gh/bitranox/projects/lib_template)
[![Known Vulnerabilities](https://snyk.io/test/github/bitranox/lib_template/badge.svg)](https://snyk.io/test/github/bitranox/lib_template)

Scaffold for Rich powered logging helpers:
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

## Development

Development workflow, make targets, and release details now live in [DEVELOPMENT.md](DEVELOPMENT.md).

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
