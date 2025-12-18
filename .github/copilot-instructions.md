This repository: GST Billing (PyQt5) — quick AI helper guide

Purpose
- Desktop GST billing application built with PyQt5. UI screens under `screens/`, small shared widgets in `widgets.py`, theming in `theme.py`, and persistence via `database.py`.

Big picture
- Entry points: `run.py` / `main.py` and `app_with_auth.py` (app bootstrapping). The UI composes `BaseScreen` subclasses from `screens/` into a main window.
- Screens folder contains per-feature screens: `parties.py`, `products.py`, `dashboard.py`, `invoices.py`, etc. Each screen builds its own layouts and uses `widgets.CustomTable` for tabular data.
- Persistence: `database.db` module exposes `db` object with helpers like `get_parties()`, `add_party()`, etc. Code defensively checks for attributes before calling.

Developer workflows
- Run UI: `python3 main.py` (or `./run_ui.sh` if added) — starts the PyQt5 desktop app.
- Run import checks: quick import test:
  python3 - << 'PY'
  try:
      import importlib
      m = importlib.import_module('screens.parties')
      importlib.reload(m)
      print('IMPORT OK')
  except Exception:
      import traceback; traceback.print_exc()
  PY
- Install dependencies: `pip install -r requirements.txt`.

Project-specific conventions
- UI patterns: screens use layouts and helper styled widgets. Prefer `create_label/create_input` style where present for consistent look.
- Use defensive db access: always check `hasattr(db, 'method')` before calling (database may be optional in dev environment).
- Minimal external services: app is local; optional PDF/export features use `pandas`/`reportlab`.

Key files and examples
- `screens/parties.py`: Party management UI and `PartyDialog` (form fields: name, phone, email, gst, pan, company, state, address, opening_balance, balance_type). Use this as reference for form layouts and db calls.
- `screens/products.py`: ProductDialog shows product-style form helpers `label()`, `input()`, and `input_style()` — mirror this when standardizing other dialogs.
- `widgets.py`: shared helpers such as `CustomTable` and `CustomButton` (search here when building table rows or buttons).
- `theme.py`: color and style tokens used across app — import values from here to maintain consistent styles.
- `database.py`: db access object `db` — check function names and signatures before calling.

When coding
- Keep UI-only changes isolated to `screens/` and `widgets.py`.
- Preserve `theme.py` tokens; reuse them in stylesheets.
- For new dialogs prefer the `ProductDialog` pattern: label + input stacked via grid rows and `create_label/create_input` helpers.

If unsure
- Run the import-check snippet above; if it fails, inspect the traceback for IndentationError or NameError from stray code fragments.

Deliverable
- After editing, run `python3 main.py` to visually confirm UI changes.

If you want, I can expand this doc with explicit edit guidelines, test commands, or additional examples from `screens/` files.
