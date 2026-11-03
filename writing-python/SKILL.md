---
name: writing-python
description: >-
  Conventions for writing and refactoring Python: SRP classes/files, strategy
  and gateway/service layout, package __init__ exports, no stubs or lazy
  export helpers, clean import DAGs, tests stay out of production. Use whenever
  creating, editing, moving, or reviewing Python code (.py files, packages,
  refactors).
---

# Writing Python

Apply these rules whenever you write or restructure Python.

## Structure

- **Class-first:** put behavior on classes with a small public surface. Prefer almost no module-level functions (tiny pure helpers / `@dataclass` field types are fine).
- **SRP classes:** one reason to change per class. Split god-objects; prefer compose over mixins of unrelated concerns. SRP classes stay **DRY** and expose **declarative** method names (say what they do in domain or transport terms, not a dump of steps).
- **SRP files:** prefer **one class per file**. Multiple classes in one module are a smell unless tightly coupled and tiny.
- **Method size:** keep methods/functions ≤ ~20 body lines; longer bodies delegate to private helpers with declarative names.
- **File size:** aim ~200 lines; treat 300+ as a split signal.
- **Packages for clusters:** when a concern has a main type plus helpers, use a package directory with the main module and helpers inside — not a flat pile of sibling utility modules.
- **Shared cross-cutting code** lives in a dedicated shared package so each app or service opts in explicitly.

## Strategy pattern (open/closed)

Prefer the **strategy** pattern when behavior varies by kind and you want to extend without editing a central switch.

Typical layout:

```text
something/
  something.py          # ABC / registry / wiring that stays stable
  strategies/
    strategy_a.py       # one concrete strategy per file
    strategy_b.py
```

- New behavior = new strategy module (+ register if needed), not growing `if/elif` in the core type.
- Concrete strategies implement a small shared ABC so callers stay open for extension and closed for modification.

## Gateway and service layers

When talking to an external system (HTTP, Docker, cloud API, DB driver, …), separate **gateway** from **service**:

| Layer | Role | Naming |
|-------|------|--------|
| **Gateway** | Raw, transport-level commands against the external surface | Short, protocol-shaped names (`get`, `post`, `put`, `delete`, `exec`, …). **No business vocabulary** in method names. |
| **Service** | Business use of that gateway | Declarative domain names; orchestrates gateway calls (sometimes a thin wrapper, usually real workflow logic). |

- Gateways stay free of product rules; services compose gateways and stay SRP.
- Prefer this split over one class that mixes “how we call the wire” with “what the product means.”

## Package exports

- Every package `__init__.py` defines the **public surface** via normal eager imports and `__all__`.
- Callers import public names from the package (e.g. `from package import PublicType`).
- Visibility is controlled by `__init__`, not by underscore-prefixing types that are merely “internal to the package” when the package decides the export list.
- **No lazy export helpers** (`__getattr__` / deferred import barrels). If eager `__init__` creates cycles, **fix the import DAG** (import from owning modules, slim package surfaces, split modules) — never paper over cycles.
- Implementation files import from **owning modules**, not through unrelated fat barrels that force-load the world.

## No stubs or shims

- Do **not** add thin functions that only forward to a class method. Call the class API at the use site.
- Do **not** add re-export functions that only exist for old paths. Update callers; use `git mv` for renames of tracked files.

## Imports

- All `import` / `from … import` at **module scope** (no function-local imports to hide cycles).
- Prefer relative imports inside a package tree when that is the project convention.
- **`from __future__ import annotations` is almost never needed** — do not add it at the top of every file. Only add it when there is a concrete, required reason.

## Tests vs production

- Tests serve the code, not the other way around.
- Do **not** put test-only helpers in the production package tree. Keep them under the test tree (e.g. shared test helpers).
- Production APIs must not exist solely to make tests convenient.

## Uniform plugin surfaces

- When several siblings are wired the same way (strategies, jobs, channels), give them a small **ABC** with a clear attach/run interface so the caller or wiring layer stays dumb and uniform.

## Checklist before finishing a Python change

- [ ] Classes/files are SRP; methods short and declarative; no new god-module
- [ ] Varying behavior uses strategies under `…/strategies/` when open/closed fits
- [ ] External I/O uses gateway (raw) + service (business) when applicable
- [ ] Package `__init__` exports are intentional and eager (no lazy barrels)
- [ ] Import graph stays a DAG; no stub wrappers
- [ ] No unnecessary `from __future__ import annotations`
- [ ] No test-only utilities left under production code
