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
        # Create table for companies
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
        # Create table for parties
        self._execute(
            """
            CREATE TABLE IF NOT EXISTS parties (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                mobile TEXT,
                email TEXT,
                party_type TEXT NOT NULL,
                gst_number TEXT,
                pan TEXT,
                address TEXT,
                city TEXT,
                state TEXT,
                pincode TEXT,
                opening_balance REAL DEFAULT 0,
                balance_type TEXT DEFAULT 'dr'
            )
            """
        )
        # Create table for products
        self._execute(
            """
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                hsn_code TEXT,
                barcode TEXT,
                unit TEXT,
                sales_rate REAL DEFAULT 0,
                purchase_rate REAL DEFAULT 0,
                discount_percent REAL DEFAULT 0,
                mrp REAL DEFAULT 0,
                tax_rate REAL DEFAULT 18,
                sgst_rate REAL DEFAULT 9,
                cgst_rate REAL DEFAULT 9,
                opening_stock REAL DEFAULT 0,
                low_stock REAL DEFAULT 0,
                product_type TEXT,
                category TEXT,
                description TEXT
            )
            """
        )
        # Create table for invoices
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
        
        # Create table for invoice items (line items)
        self._execute(
            """
            CREATE TABLE IF NOT EXISTS invoice_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_id INTEGER NOT NULL,
                product_id INTEGER,
                product_name TEXT NOT NULL,
                hsn_code TEXT,
                quantity REAL NOT NULL DEFAULT 0,
                unit TEXT DEFAULT 'Piece',
                rate REAL NOT NULL DEFAULT 0,
                discount_percent REAL DEFAULT 0,
                discount_amount REAL DEFAULT 0,
                tax_percent REAL DEFAULT 0,
                tax_amount REAL DEFAULT 0,
                amount REAL NOT NULL DEFAULT 0,
                FOREIGN KEY(invoice_id) REFERENCES invoices(id),
                FOREIGN KEY(product_id) REFERENCES products(id)
            )
            """
        )
        
        # Create table for payments
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
            self.add_party('DEMO CUSTOMER', mobile='9999999999', email='demo@example.com', gstin='', pan=None, address=None, city=None, party_type='Customer')
            self.add_party('SAMPLE SUPPLIER', mobile='8888888888', email='supplier@example.com', gstin='', pan=None, address=None, city=None, party_type='Supplier')
        if not self._query("SELECT id FROM products LIMIT 1"):
            self.add_product('SAMPLE PRODUCT', hsn_code='', sales_rate=100.0)

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
            ("mobile", "TEXT"),
            ("email", "TEXT"),
            ("party_type", "TEXT"),
            ("gst_number", "TEXT"),
            ("pan", "TEXT"),
            ("address", "TEXT"),
            ("city", "TEXT"),
            ("state", "TEXT"),
            ("pincode", "TEXT"),
            ("opening_balance", "REAL DEFAULT 0"),
            ("balance_type", "TEXT DEFAULT 'dr'"),
        ]:
            try:
                self._ensure_column("parties", col, decl)
            except Exception:
                pass
        # Products
        for col, decl in [
            ("hsn_code", "TEXT"),
            ("barcode", "TEXT"),
            ("unit", "TEXT"),
            ("sales_rate", "REAL DEFAULT 0"),
            ("purchase_rate", "REAL DEFAULT 0"),
            ("discount_percent", "REAL DEFAULT 0"),
            ("mrp", "REAL DEFAULT 0"),
            ("tax_rate", "REAL DEFAULT 18"),
            ("sgst_rate", "REAL DEFAULT 9"),
            ("cgst_rate", "REAL DEFAULT 9"),
            ("opening_stock", "REAL DEFAULT 0"),
            ("low_stock", "REAL DEFAULT 0"),
            ("product_type", "TEXT"),
            ("category", "TEXT"),
            ("description", "TEXT"),
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
            ("status", "TEXT DEFAULT 'Draft'"),
            ("type", "TEXT DEFAULT 'GST'"),  # GST or Non-GST
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
        # Invoice items table schema updates
        for col, decl in [
            ("unit", "TEXT DEFAULT 'Piece'"),
            ("rate", "REAL DEFAULT 0"),
            ("discount_percent", "REAL DEFAULT 0"),
            ("discount_amount", "REAL DEFAULT 0"),
            ("tax_percent", "REAL DEFAULT 0"),
            ("tax_amount", "REAL DEFAULT 0"),
            ("amount", "REAL DEFAULT 0"),
        ]:
            try:
                self._ensure_column("invoice_items", col, decl)
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
    
    def get_company_by_id(self, company_id):
        """Get a single company by ID"""
        result = self._query("SELECT * FROM companies WHERE id = ?", (company_id,))
        return result[0] if result else None
    
    def update_company(self, company_id, name, gstin=None, mobile=None, email=None, address=None):
        """Update an existing company"""
        self._execute(
            "UPDATE companies SET name=?, gstin=?, mobile=?, email=?, address=? WHERE id=?",
            (name, gstin, mobile, email, address, company_id),
        )
        return company_id
    
    def delete_company(self, company_id):
        """Delete a company by ID"""
        self._execute("DELETE FROM companies WHERE id = ?", (company_id,))
        return True

    # --- parties ---
    def add_party(self, *args, **kwargs):
        """Supports both dict input and positional params to match existing callers.

        Dict keys: name, phone/mobile, email, gst_number/gstin, pan, address, city, state, pincode, opening_balance, balance_type, is_gst_registered, party_type
        Positional signature: (name, phone=None, email=None, gstin=None, pan=None, address=None, city=None, state=None, pincode=None, opening_balance=0, balance_type='dr', is_gst_registered=0, party_type='Customer')
        """
        if args and isinstance(args[0], dict):
            d = args[0]
            name = d.get('name')
            phone = d.get('phone') or d.get('mobile')
            email = d.get('email')
            gst = d.get('gst_number') or d.get('gstin')
            pan = d.get('pan')
            address = d.get('address')
            city = d.get('city')
            state = d.get('state')
            pincode = d.get('pincode')
            opening = d.get('opening_balance', 0) or 0
            bal_type = d.get('balance_type', 'dr')
            is_gst = d.get('is_gst_registered', 1 if gst else 0)
            party_type = d.get('type') or d.get('party_type', 'Customer')
        else:
            # Map legacy positional args
            name = args[0] if args else kwargs.get('name')
            phone = kwargs.get('phone') or kwargs.get('mobile')
            email = kwargs.get('email')
            gst = kwargs.get('gstin')
            pan = kwargs.get('pan')
            address = kwargs.get('address')
            city = kwargs.get('city')
            state = kwargs.get('state')
            pincode = kwargs.get('pincode')
            opening = kwargs.get('opening_balance', 0) or 0
            bal_type = kwargs.get('balance_type', 'dr')
            is_gst = kwargs.get('is_gst_registered', 0)
            party_type = kwargs.get('party_type', 'Customer')

        cur = self._execute(
            """
            INSERT INTO parties(name, mobile, email, party_type, gst_number, pan, address, city, state, pincode, opening_balance, balance_type)
            VALUES(?,?,?,?,?,?,?,?,?,?,?,?)
            """,
            (name, phone, email, party_type, gst, pan, address, city, state, pincode, float(opening or 0), bal_type),
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
    def add_product(self, name, hsn_code=None, barcode=None, unit='PCS', sales_rate=0, purchase_rate=0, discount_percent=0, mrp=0, opening_stock=0, low_stock=0, product_type='Goods', category=None, description=None):
        cur = self._execute(
            "INSERT INTO products(name, hsn_code, barcode, unit, sales_rate, purchase_rate, discount_percent, mrp, opening_stock, low_stock, product_type, category, description) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (name, hsn_code, barcode, unit, float(sales_rate or 0), float(purchase_rate or 0), float(discount_percent or 0), float(mrp or 0), float(opening_stock or 0), float(low_stock or 0), product_type, category, description),
        )
        return cur.lastrowid

    def update_product(self, product_data: Dict):
        pid = product_data.get('id')
        if not pid:
            return False
        self._execute(
            """
            UPDATE products SET
            name = ?, hsn_code = ?, barcode = ?, unit = ?,
            sales_rate = ?, purchase_rate = ?, discount_percent = ?, mrp = ?,
            tax_rate = ?, sgst_rate = ?, cgst_rate = ?,
            opening_stock = ?, low_stock = ?, product_type = ?, category = ?, description = ?
            WHERE id = ?
            """,
            (
            product_data.get('name'),
            product_data.get('hsn_code'),
            product_data.get('barcode'),
            product_data.get('unit'),
            float(product_data.get('sales_rate') or 0),
            float(product_data.get('purchase_rate') or 0),
            float(product_data.get('discount_percent') or 0),
            float(product_data.get('mrp') or 0),
            float(product_data.get('tax_rate') or 0),
            float(product_data.get('sgst_rate') or 0),
            float(product_data.get('cgst_rate') or 0),
            float(product_data.get('opening_stock') or 0),
            float(product_data.get('low_stock') or 0),
            product_data.get('product_type'),
            product_data.get('category'),
            product_data.get('description'),
            pid,
            ),
        )
        return True

    def get_products(self):
        return self._query("SELECT * FROM products ORDER BY id DESC")

    def delete_product(self, product_id: int):
        self._execute("DELETE FROM products WHERE id = ?", (product_id,))

    # --- invoices (minimal) ---
    def add_invoice(self, invoice_no, date, party_id, invoice_type='GST', subtotal=0, cgst=0, sgst=0, igst=0, round_off=0, grand_total=0, status='Draft'):
        cur = self._execute(
            "INSERT INTO invoices(invoice_no, date, party_id, grand_total, status, type) VALUES(?,?,?,?,?,?)",
            (invoice_no, date, party_id, float(grand_total or 0), status, invoice_type),
        )
        return cur.lastrowid

    def get_invoices(self):
        return self._query("SELECT * FROM invoices ORDER BY id DESC")

    def update_invoice(self, invoice_data: Dict):
        iid = invoice_data.get('id')
        if not iid:
            return False
        self._execute(
            "UPDATE invoices SET invoice_no = ?, date = ?, party_id = ?, grand_total = ?, status = ?, type = ? WHERE id = ?",
            (
                invoice_data.get('invoice_no'),
                invoice_data.get('date'),
                invoice_data.get('party_id'),
                float(invoice_data.get('grand_total') or 0),
                invoice_data.get('status', 'Draft'),
                invoice_data.get('type', 'GST'),
                iid,
            ),
        )
        return True

    def delete_invoice(self, invoice_id: int):
        # Delete invoice items first (foreign key constraint)
        self._execute("DELETE FROM invoice_items WHERE invoice_id = ?", (invoice_id,))
        # Then delete the invoice
        self._execute("DELETE FROM invoices WHERE id = ?", (invoice_id,))

    def get_invoice_by_number(self, invoice_no: str):
        """Get invoice by invoice number"""
        invoices = self._query("SELECT * FROM invoices WHERE invoice_no = ? LIMIT 1", (invoice_no,))
        return invoices[0] if invoices else None
        
    def get_invoice_by_id(self, invoice_id: int):
        """Get invoice by ID"""
        invoices = self._query("SELECT * FROM invoices WHERE id = ? LIMIT 1", (invoice_id,))
        return invoices[0] if invoices else None
    
    def invoice_no_exists(self, invoice_no: str):
        """Check if invoice number already exists"""
        result = self._query("SELECT COUNT(*) as count FROM invoices WHERE invoice_no = ?", (invoice_no,))
        return result[0]['count'] > 0 if result else False

    # --- invoice items ---
    def add_invoice_item(self, invoice_id: int, product_id: int, product_name: str, 
                        hsn_code: str = None, quantity: float = 0, unit: str = 'Piece',
                        rate: float = 0, discount_percent: float = 0, discount_amount: float = 0,
                        tax_percent: float = 0, tax_amount: float = 0, amount: float = 0):
        """Add a line item to an invoice"""
        cur = self._execute(
            """
            INSERT INTO invoice_items(invoice_id, product_id, product_name, hsn_code, 
                                    quantity, unit, rate, discount_percent, discount_amount,
                                    tax_percent, tax_amount, amount) 
            VALUES(?,?,?,?,?,?,?,?,?,?,?,?)
            """,
            (invoice_id, product_id, product_name, hsn_code, float(quantity), unit,
             float(rate), float(discount_percent), float(discount_amount),
             float(tax_percent), float(tax_amount), float(amount))
        )
        return cur.lastrowid

    def get_invoice_items(self, invoice_id: int):
        """Get all line items for an invoice"""
        return self._query("SELECT * FROM invoice_items WHERE invoice_id = ? ORDER BY id", (invoice_id,))
    
    def delete_invoice_items(self, invoice_id: int):
        """Delete all line items for an invoice"""
        self._execute("DELETE FROM invoice_items WHERE invoice_id = ?", (invoice_id,))
    
    def get_invoice_with_items(self, invoice_no: str):
        """Get complete invoice with line items"""
        invoice = self.get_invoice_by_number(invoice_no)
        if not invoice:
            return None
        
        # Get party details
        party = None
        if invoice['party_id']:
            parties = self._query("SELECT * FROM parties WHERE id = ?", (invoice['party_id'],))
            party = parties[0] if parties else None
        
        # Get line items
        items = self.get_invoice_items(invoice['id'])
        
        return {
            'invoice': invoice,
            'party': party,
            'items': items
        }

    def get_invoice_with_items_by_id(self, invoice_id: int):
        """Get complete invoice with line items by invoice ID"""
        invoice = self.get_invoice_by_id(invoice_id)
        if not invoice:
            return None
        
        # Get party details
        party = None
        if invoice.get('party_id'):
            parties = self._query("SELECT * FROM parties WHERE id = ?", (invoice['party_id'],))
            party = parties[0] if parties else None
        
        # Get line items
        items = self.get_invoice_items(invoice['id'])
        
        return {
            'invoice': invoice,
            'party': party,
            'items': items
        }

    # --- payments (minimal) ---
    def add_payment(self, payment_id, party_id, amount, date, mode='Cash', invoice_id=None, notes=None):
        cur = self._execute(
            "INSERT INTO payments(payment_id, party_id, amount, date, mode, invoice_id, notes) VALUES(?,?,?,?,?,?,?)",
            (payment_id, party_id, float(amount or 0), date, mode, invoice_id, notes),
        )
        return cur.lastrowid

    def get_payments(self):
        return self._query("""
            SELECT p.*, pa.name as party_name
            FROM payments p 
            LEFT JOIN parties pa ON p.party_id = pa.id 
            ORDER BY p.id DESC
        """)

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
