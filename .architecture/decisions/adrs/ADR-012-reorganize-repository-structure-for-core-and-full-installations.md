# ADR-012: Reorganize Repository Structure using Split Directories for Core and Full Installations

## Status

Proposed

## Context

The `opl` library has grown to include many tools and modules, some of which require heavy or environment-specific dependencies (e.g., `psycopg2-binary`, `kafka-python`, `locust`). However, many consumers of this repository only need a small "core" subset of tools (e.g., `junit_cli.py`, `cluster_read.py`) that run with a minimal dependency footprint. 

Historically, this was solved by maintaining a separate copy of the core Python modules inside the `core/opl/` directory, with its own `core/setup.py`. This leads to code duplication, increased maintenance burden, and the risk of the core and full modules drifting out of sync. We need a way to maintain a single source of truth for the codebase while continuing to support both a full installation and a lightweight core installation directly from the git repository using `pip`.

An initial proposal involved pointing `core/setup.py` back to the root `opl/` directory to share files. However, this relies on non-standard packaging paths (`../`) and fails to enforce a hard boundary preventing developers from accidentally adding heavy dependencies to core modules.

## Decision Drivers

* Code duplication between `opl/` and `core/opl/` increases maintenance burden and risk of bugs.
* Consumers need to be able to install just the core functionality without pulling in heavy dependencies.
* The installation commands for consumers (using `pip install git+https...`) are established and should ideally remain the same, specifically utilizing the `--subdirectory=core` feature of pip for the core installation.
* We want to physically enforce a hard boundary between core functionality and tools that require heavy dependencies.
* Python packaging constraints should be respected, avoiding hacks like referencing parent directories in `setup.py`.

## Decision

We will reorganize the repository structure into a **Split Directories** pattern, creating a workspace/monorepo style layout using Python's implicit namespace packages (PEP 420).

**Architectural Components Affected:**
* **Directory Structure:** The existing `opl/` directory will be split into two physically separate directories: `core/opl/` and `extras/opl/`.
* **Namespace Packaging:** `opl/__init__.py` files will be removed or converted to namespace packages to allow `import opl.*` to resolve across both physical directories seamlessly.
* **Packaging Configuration:**
    * `core/setup.py`: Standard setup file specifying only minimal dependencies.
    * `extras/setup.py`: Standard setup file specifying heavy dependencies.
    * Root `setup.py`: Acts as a "meta-package" that installs both `core` and `extras` via local file references (`install_requires=[f"opl-core @ file://{os.path.abspath('core')}", ...]`).

This architecture completely eliminates duplication while physically isolating core modules from heavy dependencies.

## Consequences

### Positive

* Single source of truth for all code: bug fixes and features only need to be implemented once.
* Hard physical boundaries: It is impossible to accidentally import a heavy dependency into a core module.
* Clean Packaging: `core/setup.py` doesn't need to use any `../` hacks.
* True Modularity: Aligns perfectly with modern Python workspace/monorepo patterns.
* Preserves Install Commands: Both `pip install git+https://...` and `pip install git+https://...#subdirectory=core` will continue to function seamlessly.

### Negative

* Initial Refactor Effort: Requires identifying every file currently in `opl/` and explicitly sorting them into either `core/opl/` or `extras/opl/`.
* Testing complexity: pytest configuration might need tweaking to discover tests across multiple source directories or ensure the implicit namespace package is correctly loaded during test runs.

### Neutral

* The root directory no longer contains source code directly; it merely orchestrates the sub-packages.

## Implementation Strategy

> **Note**: This section externalizes the "senior thinking" about HOW and WHEN to implement this decision, not just WHAT to implement.

### Blast Radius

**Impact Scope**: Local development environments, CI pipelines, and external consumers relying on git-based pip installs.

**Affected Components**:
- Packaging configuration (Root `setup.py`, `core/setup.py`, `extras/setup.py`)
- Python module structure (`opl/` -> `core/opl/` & `extras/opl/`)
- CI testing scripts (pytest configurations)

**Affected Teams**:
- All teams consuming the `opl` repository via pip.

**User Impact**: Users installing via pip from the git URL should experience no change in functionality, but the core installation will now correctly reflect the unified code. Imports like `from opl.module import foo` will continue working exactly as before thanks to namespace packaging.

**Risk Mitigation**:
- Exhaustively test `pip install` commands locally and in a clean container before merging.
- Verify that `pytest` can successfully discover and run tests for all modules.
- Ensure that the entry points defined in `core/setup.py` and the root `setup.py` still function correctly.

### Reversibility

**Reversibility Level**: High

**Rollback Feasibility**:
- Very easy to rollback by simply reverting the git commit if issues are discovered post-merge.

**Migration Paths**:
- **Forward Migration**: Split the `opl/` files into `core/opl/` and `extras/opl/`. Setup the meta-package `setup.py` in the root. Verify installation and tests.
- **Rollback Migration**: Revert the commit.
- **Evolution Path**: If the implicit namespace package proves too brittle across varying Python environments, we can investigate explicit `pkgutil` style namespace declarations.

**Options Preserved**:
- We can still extract core to a separate repository in the future if needed, and it would be significantly easier to do so since it is already physically isolated.

**Commitments Made**:
- We commit to organizing code into these logical groupings (`core` vs `extras`) and maintaining the namespace package structure.

### Sequencing & Timing

**Prerequisites**:
- [ ] Technical spike completed successfully to validate the meta-package approach with Git URL installs (Done).
- [ ] Identify which files in `opl/` belong in `core/` and which belong in `extras/`.

**System Readiness**:
- **Dependencies**: Consumers' environments are unaffected as long as the install command continues to work.

**Team Readiness**:
- **Understanding**: The team needs to understand the new directory layout and that all new modules must be placed in the appropriate sub-directory (`core` or `extras`).

**Sequencing Concerns**:
- None. This is an internal repository refactoring.

**Readiness Assessment**: Ready to implement.

### Social Cost

**Learning Curve**: Low
- Developers just need to remember to navigate into `core/opl/` or `extras/opl/` instead of a top-level `opl/` directory.

**Cognitive Load**:
- Reduced, as boundaries between lightweight and heavy tools are now physically enforced.

**Clarity Assessment**:
- **Will this help more than confuse?**: Yes. Duplication is inherently confusing, and clear physical boundaries prevent architectural degradation.
- **Explanation required**: A brief team announcement regarding the directory structure change.

**Documentation Needs**:
- [ ] Update any developer documentation that mentions the location of source files.

### Confidence Assessment

**Model Correctness Confidence**: High
- The approach leverages standard Python PEP 420 namespace packaging and standard pip install mechanisms.

**Assumptions**:
1. Python's implicit namespace packages (PEP 420) work consistently across all our supported Python versions (>=3.6). - **Validation**: Requires verifying behavior in Python 3.6+ environments, particularly regarding `__init__.py` files.

**Uncertainty Areas**:
- Ensuring all CI testing tools (like `pytest`, `flake8`, `mypy`) correctly handle the split directories and namespace packages without significant configuration changes.

**Validation Approach**:
- Run the full CI test suite against the new branch locally.

## Implementation

**Phase 1: Structure Preparation (Completed)**
* Create `extras/opl/` directory.
* Remove `opl/__init__.py` (if it doesn't contain vital code) to enable implicit namespace packaging, or convert it to a `pkgutil` style namespace declaration if needed for compatibility.

**Phase 2: Code Migration**
* Move heavy-dependency tools and modules from `opl/` into `extras/opl/`.
* Move the remaining lightweight core tools from `opl/` into `core/opl/`.
* Delete the now-empty root `opl/` directory.

**Phase 3: Packaging Update**
* Update `core/setup.py`.
* Create `extras/setup.py`.
* Update the root `setup.py` to act as the meta-package pulling in both local directories.

**Phase 4: Validation & Cleanup**
* Run tests to ensure imports resolve correctly.
* Update `tox.ini`, GitHub Actions, or any other CI configuration that hardcodes the `opl/` path.
* Open a Pull Request for review.

## Alternatives Considered

### Package Core and use Extras for Full

Move all code to a single package, and use `extras_require` for the heavy dependencies (e.g., `pip install .[full]`).

**Pros:**
* Standard Python packaging practice.
* Single `setup.py` file.

**Cons:**
* Breaks backwards compatibility with the existing `subdirectory=core` installation method.
* Users would have to change their CI/CD pipelines to update the pip install command.
* Doesn't physically enforce the boundary between core code and heavy code.

### Extract Core to a Separate Repository

Move the core tools to an entirely new repository (`opl-core`) and have the main `opl` repository depend on it.

**Pros:**
* Hardest boundary prevents accidental dependency leakage.
* Clean separation of concerns.

**Cons:**
* Significant overhead to create and maintain a new repository.
* Requires coordinating changes across two repositories.

### Single source of truth using `../` references

Point `core/setup.py` back to the root `opl/` directory (`package_dir={'': '..'}`).

**Pros:**
* Very simple change to `setup.py`.
* No need to split directories.

**Cons:**
* Relies on non-standard `../` references in packaging which can break certain build tools.
* Fails to physically separate core modules from heavy modules, relying purely on developer discipline to avoid bad imports.

## Validation

**Acceptance Criteria:**
- [ ] The `opl/` directory is successfully split into `core/opl/` and `extras/opl/`.
- [ ] No duplicated Python files exist in the repository.
- [ ] Running `python -m pip install git+https://github.com/redhat-performance/opl.git` succeeds, installs the full toolset (both core and extras), and imports work seamlessly.
- [ ] Running `python3 -m pip install --no-cache-dir -e "git+https://github.com/redhat-performance/opl.git#egg=opl-rhcloud-perf-team-core&subdirectory=core"` succeeds, installs only the core tools, and those tools are executable.
- [ ] All automated tests pass successfully.

**Testing Approach:**
* Use a clean Python virtual environment to test both installation commands sequentially.
* Run the existing `pytest` suite locally against the new directory structure.

## References

* [PEP 420 -- Implicit Namespace Packages](https://peps.python.org/pep-0420/)
* Setuptools Documentation on Package Discovery