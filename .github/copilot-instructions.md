This repository: GST Billing (PyQt5) — AI coding agent guide

## Purpose
Desktop GST billing application with PyQt5. Core structure: `screens/` for UI modules, `widgets.py` for reusable components, `theme.py` for styling, `database.py` for SQLite persistence.

## Architecture overview
- **Entry points**: `main.py` (main app) and `app_with_auth.py` (with auth flow)
- **Screen system**: `BaseScreen` subclasses in `screens/` compose into sidebar navigation via `MainWindow`
- **Dialog pattern**: Separate dialog files (`*_dialogue.py`) handle complex forms (invoice, product, party creation)
- **Data flow**: `database.py` exposes singleton `db` object with methods like `get_parties()`, `add_invoice()`, etc.

## Critical patterns

### Dialog structure (follow `ProductDialog` in `screens/product_dialogue.py`)
```python
def label(self, text):
    # Standard label with theme colors
def input(self):
    # Styled QLineEdit with consistent appearance
def input_style():
    # Returns CSS string with theme colors
```
Use this pattern for all form dialogs - creates visual consistency.

### Uppercase input enforcement (common pattern)
```python
def force_upper(text):
    cursor_pos = self.input_field.cursorPosition()
    self.input_field.blockSignals(True)
    self.input_field.setText(text.upper())
    self.input_field.setCursorPosition(cursor_pos)
    self.input_field.blockSignals(False)
self.input_field.textChanged.connect(force_upper)
```
Applied to party names, product searches - maintains data consistency.

### Signal connections for reactive UI
- Invoice type changes update all item tax rates via `currentTextChanged.connect()`
- Product selection auto-populates HSN, rate, tax from product data
- Always use `blockSignals()` to prevent recursive updates during programmatic changes

## Key conventions
- **Theme consistency**: Import colors from `theme.py` - use `PRIMARY`, `WHITE`, `BORDER`, etc. in stylesheets
- **Database safety**: Check `hasattr(db, 'method_name')` before calling - db may be unavailable in dev
- **Tax logic**: GST invoices use product tax rates; Non-GST invoices set tax to 0 automatically
- **Read-only fields**: Use `setReadOnly(True)` + `BACKGROUND` color for calculated/auto-populated fields

## Essential files
- `screens/invoice_dialogue.py`: Complex dialog with item widgets, tax calculations, parent-child communication
- `widgets.py`: `CustomTable`, `CustomButton`, `CustomInput` - reuse these for consistency  
- `database.py`: SQLite wrapper with methods matching UI needs (`get_invoices_with_filters()`, etc.)
- `config.py`: JSON-based settings management via singleton `config` object

## Developer workflow
```bash
python3 main.py  # Start application
pip install -r requirements.txt  # Dependencies
```

### Quick validation
```python
# Test imports without full app startup
import importlib
m = importlib.import_module('screens.parties')
importlib.reload(m)
print('IMPORT OK')
```

## Common tasks
- **New screen**: Inherit from `BaseScreen`, add to `main.py` imports and navigation
- **Form validation**: Use Qt validators or custom `textChanged` handlers with visual feedback
- **Database changes**: Update schema in `database.py` `create_tables()`, add methods as needed
- **Styling**: Extend `theme.py` colors rather than hardcoding hex values in components

Always run `python3 main.py` after changes to verify UI behavior and catch runtime errors.
