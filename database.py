"""SQLite-backed database used for persistence.

This module exposes a `db` object with the same API used by the UI
screens. Data is stored in a local SQLite file configured via
`data/config.json` under the key `database.path`.
"""

import json
import os
import sqlite3
from typing import List, Dict, Optional, Any


def _load_db_path() -> str:
    cfg_path = os.path.join(os.path.dirname(__file__), 'data', 'config.json')
    try:
        with open(cfg_path, 'r', encoding='utf-8') as f:
            cfg = json.load(f)
        db_path = cfg.get('database', {}).get('path') or 'data/gst_billing.db'
    except Exception:
        db_path = 'data/gst_billing.db'
    # Ensure directory exists
    abs_path = os.path.join(os.path.dirname(__file__), db_path)
    os.makedirs(os.path.dirname(abs_path), exist_ok=True)
    return abs_path


class Database:
    def __init__(self, path: Optional[str] = None):
        self.path = path or _load_db_path()
        self.conn = sqlite3.connect(self.path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.create_tables()
        self._ensure_schema()
        self.ensure_seed()

    # --- utilities ---
    def _execute(self, sql: str, params: tuple = ()):  # write ops
        cur = self.conn.cursor()
        cur.execute(sql, params)
        self.conn.commit()
        return cur

    def _query(self, sql: str, params: tuple = ()) -> List[Dict[str, Any]]:
        cur = self.conn.cursor()
        cur.execute(sql, params)
        rows = cur.fetchall()
        return [dict(r) for r in rows]

    # --- schema ---
    def create_tables(self):
        self._execute(
            """
            CREATE TABLE IF NOT EXISTS companies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                gstin TEXT,
                mobile TEXT,
                email TEXT,
                address TEXT
            )
            """
        )
        self._execute(
            """
            CREATE TABLE IF NOT EXISTS parties (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT,
                email TEXT,
                type TEXT,
                gst_number TEXT,
                pan TEXT,
                address TEXT,
                state TEXT,
                opening_balance REAL DEFAULT 0,
                balance_type TEXT DEFAULT 'dr',
                is_gst_registered INTEGER DEFAULT 0
            )
            """
        )
        self._execute(
            """
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                hsn_code TEXT,
                sales_rate REAL DEFAULT 0,
                stock_quantity REAL DEFAULT 0
            )
            """
        )
        self._execute(
            """
            CREATE TABLE IF NOT EXISTS invoices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_no TEXT,
                date TEXT,
                party_id INTEGER,
                grand_total REAL DEFAULT 0,
                FOREIGN KEY(party_id) REFERENCES parties(id)
            )
            """
        )
        self._execute(
            """
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                payment_id TEXT,
                party_id INTEGER,
                amount REAL,
                date TEXT,
                mode TEXT,
                invoice_id INTEGER,
                notes TEXT,
                FOREIGN KEY(party_id) REFERENCES parties(id),
                FOREIGN KEY(invoice_id) REFERENCES invoices(id)
            )
            """
        )

    def ensure_seed(self):
        # Seed a couple of rows if tables are empty
        if not self._query("SELECT id FROM parties LIMIT 1"):
            self.add_party('Demo Customer', mobile='9999999999', email='demo@example.com', gstin='', pan=None, address=None, city=None, party_type='Customer')
            self.add_party('Sample Supplier', mobile='8888888888', email='supplier@example.com', gstin='', pan=None, address=None, city=None, party_type='Supplier')
        if not self._query("SELECT id FROM products LIMIT 1"):
            self.add_product('Sample Product', hsn_code='', sales_rate=100.0, stock_quantity=10)

    # --- migrations / schema checks ---
    def _table_columns(self, table: str) -> List[str]:
        cur = self.conn.cursor()
        cur.execute(f"PRAGMA table_info({table})")
        return [r[1] for r in cur.fetchall()]

    def _ensure_column(self, table: str, name: str, decl: str):
        cols = set(self._table_columns(table))
        if name not in cols:
            self._execute(f"ALTER TABLE {table} ADD COLUMN {name} {decl}")

    def _ensure_schema(self):
        # Parties required columns
        for col, decl in [
            ("phone", "TEXT"),
            ("email", "TEXT"),
            ("type", "TEXT"),
            ("gst_number", "TEXT"),
            ("pan", "TEXT"),
            ("address", "TEXT"),
            ("state", "TEXT"),
            ("opening_balance", "REAL DEFAULT 0"),
            ("balance_type", "TEXT DEFAULT 'dr'"),
            ("is_gst_registered", "INTEGER DEFAULT 0"),
        ]:
            try:
                self._ensure_column("parties", col, decl)
            except Exception:
                pass
        # Products
        for col, decl in [
            ("hsn_code", "TEXT"),
            ("sales_rate", "REAL DEFAULT 0"),
            ("stock_quantity", "REAL DEFAULT 0"),
        ]:
            try:
                self._ensure_column("products", col, decl)
            except Exception:
                pass
        # Invoices
        for col, decl in [
            ("invoice_no", "TEXT"),
            ("date", "TEXT"),
            ("party_id", "INTEGER"),
            ("grand_total", "REAL DEFAULT 0"),
        ]:
            try:
                self._ensure_column("invoices", col, decl)
            except Exception:
                pass
        # Payments
        for col, decl in [
            ("payment_id", "TEXT"),
            ("party_id", "INTEGER"),
            ("amount", "REAL"),
            ("date", "TEXT"),
            ("mode", "TEXT"),
            ("invoice_id", "INTEGER"),
            ("notes", "TEXT"),
        ]:
            try:
                self._ensure_column("payments", col, decl)
            except Exception:
                pass
        # Companies
        for col, decl in [
            ("name", "TEXT"),
            ("gstin", "TEXT"),
            ("mobile", "TEXT"),
            ("email", "TEXT"),
            ("address", "TEXT"),
        ]:
            try:
                self._ensure_column("companies", col, decl)
            except Exception:
                pass

    # --- companies ---
    def add_company(self, name, gstin=None, mobile=None, email=None, address=None):
        cur = self._execute(
            "INSERT INTO companies(name, gstin, mobile, email, address) VALUES(?,?,?,?,?)",
            (name, gstin, mobile, email, address),
        )
        return cur.lastrowid

    def get_companies(self):
        return self._query("SELECT * FROM companies ORDER BY id DESC")

    # --- parties ---
    def add_party(self, *args, **kwargs):
        """Supports both dict input and positional params to match existing callers.

        Dict keys: name, phone/mobile, email, gst_number/gstin, pan, address, state, opening_balance, balance_type, is_gst_registered, type
        Positional signature: (name, mobile=None, email=None, gstin=None, pan=None, address=None, city=None, party_type='Customer')
        """
        if args and isinstance(args[0], dict):
            d = args[0]
            name = d.get('name')
            phone = d.get('phone') or d.get('mobile')
            email = d.get('email')
            gst = d.get('gst_number') or d.get('gstin')
            pan = d.get('pan')
            address = d.get('address')
            state = d.get('state')
            opening = d.get('opening_balance', 0) or 0
            bal_type = d.get('balance_type', 'dr')
            is_gst = d.get('is_gst_registered', 1 if gst else 0)
            ptype = d.get('type', 'Customer')
        else:
            # Map legacy positional args
            name = args[0] if args else kwargs.get('name')
            phone = kwargs.get('mobile')
            email = kwargs.get('email')
            gst = kwargs.get('gstin')
            pan = kwargs.get('pan')
            address = kwargs.get('address')
            state = kwargs.get('state') or kwargs.get('city')
            opening = 0
            bal_type = 'dr'
            is_gst = 1 if gst else 0
            ptype = kwargs.get('party_type', 'Customer')

        cur = self._execute(
            """
            INSERT INTO parties(name, phone, email, type, gst_number, pan, address, state, opening_balance, balance_type, is_gst_registered)
            VALUES(?,?,?,?,?,?,?,?,?,?,?)
            """,
            (name, phone, email, ptype, gst, pan, address, state, float(opening or 0), bal_type, int(1 if is_gst else 0)),
        )
        return cur.lastrowid

    def get_parties(self):
        return self._query("SELECT * FROM parties ORDER BY id DESC")

    def search_parties(self, search_term: str):
        like = f"%{search_term}%"
        return self._query(
            "SELECT * FROM parties WHERE name LIKE ? OR gst_number LIKE ? ORDER BY id DESC",
            (like, like),
        )

    def delete_party(self, party_id: int):
        self._execute("DELETE FROM parties WHERE id = ?", (party_id,))

    # --- products ---
    def add_product(self, name, hsn_code=None, barcode=None, unit='PCS', sales_rate=0, purchase_rate=0, discount_percent=0, mrp=0, stock_quantity=0, product_type='Goods'):
        cur = self._execute(
            "INSERT INTO products(name, hsn_code, sales_rate, stock_quantity) VALUES(?,?,?,?)",
            (name, hsn_code, float(sales_rate or 0), float(stock_quantity or 0)),
        )
        return cur.lastrowid

    def update_product(self, product_data: Dict):
        pid = product_data.get('id')
        if not pid:
            return False
        self._execute(
            "UPDATE products SET name = ?, hsn_code = ?, sales_rate = ?, stock_quantity = ? WHERE id = ?",
            (
                product_data.get('name'),
                product_data.get('hsn_code'),
                float(product_data.get('sales_rate') or 0),
                float(product_data.get('stock_quantity') or 0),
                pid,
            ),
        )
        return True

    def get_products(self):
        return self._query("SELECT * FROM products ORDER BY id DESC")

    def delete_product(self, product_id: int):
        self._execute("DELETE FROM products WHERE id = ?", (product_id,))

    # --- invoices (minimal) ---
    def add_invoice(self, invoice_no, date, party_id, invoice_type='GST', subtotal=0, cgst=0, sgst=0, igst=0, round_off=0, grand_total=0):
        cur = self._execute(
            "INSERT INTO invoices(invoice_no, date, party_id, grand_total) VALUES(?,?,?,?)",
            (invoice_no, date, party_id, float(grand_total or 0)),
        )
        return cur.lastrowid

    def get_invoices(self):
        return self._query("SELECT * FROM invoices ORDER BY id DESC")

    def update_invoice(self, invoice_data: Dict):
        iid = invoice_data.get('id')
        if not iid:
            return False
        self._execute(
            "UPDATE invoices SET invoice_no = ?, date = ?, party_id = ?, grand_total = ? WHERE id = ?",
            (
                invoice_data.get('invoice_no'),
                invoice_data.get('date'),
                invoice_data.get('party_id'),
                float(invoice_data.get('grand_total') or 0),
                iid,
            ),
        )
        return True

    def delete_invoice(self, invoice_id: int):
        self._execute("DELETE FROM invoices WHERE id = ?", (invoice_id,))

    # --- payments (minimal) ---
    def add_payment(self, payment_id, party_id, amount, date, mode='Cash', invoice_id=None, notes=None):
        cur = self._execute(
            "INSERT INTO payments(payment_id, party_id, amount, date, mode, invoice_id, notes) VALUES(?,?,?,?,?,?,?)",
            (payment_id, party_id, float(amount or 0), date, mode, invoice_id, notes),
        )
        return cur.lastrowid

    def get_payments(self):
        return self._query("SELECT * FROM payments ORDER BY id DESC")

    def update_payment(self, payment_data: Dict):
        pid = payment_data.get('id')
        if not pid:
            return False
        self._execute(
            "UPDATE payments SET payment_id = ?, party_id = ?, amount = ?, date = ?, mode = ?, invoice_id = ?, notes = ? WHERE id = ?",
            (
                payment_data.get('payment_id'),
                payment_data.get('party_id'),
                float(payment_data.get('amount') or 0),
                payment_data.get('date'),
                payment_data.get('mode'),
                payment_data.get('invoice_id'),
                payment_data.get('notes'),
                pid,
            ),
        )
        return True

    def delete_payment(self, payment_id: int):
        self._execute("DELETE FROM payments WHERE id = ?", (payment_id,))


# single global instance used by the app
db = Database()
