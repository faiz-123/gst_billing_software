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
        self._current_company_id = None  # Track current company for data isolation
        self.create_tables()
        self._ensure_schema()
        self.ensure_seed()

    def set_current_company(self, company_id: int):
        """Set the current company for data isolation"""
        self._current_company_id = company_id

    def get_current_company_id(self) -> Optional[int]:
        """Get the current company ID"""
        return self._current_company_id

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
                address TEXT,
                website TEXT,
                tax_type TEXT,
                fy_start TEXT,
                fy_end TEXT,
                other_license TEXT,
                bank_name TEXT,
                account_name TEXT,
                account_number TEXT,
                ifsc_code TEXT,
                logo_path TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        # Create table for parties
        self._execute(
            """
            CREATE TABLE IF NOT EXISTS parties (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER,
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
                balance_type TEXT DEFAULT 'dr',
                FOREIGN KEY(company_id) REFERENCES companies(id)
            )
            """
        )
        # Create table for products
        self._execute(
            """
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER,
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
                description TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(company_id) REFERENCES companies(id)
            )
            """
        )
        # Create table for invoices
        self._execute(
            """
            CREATE TABLE IF NOT EXISTS invoices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER,
                invoice_no TEXT NOT NULL,
                date TEXT NOT NULL,
                party_id INTEGER,
                tax_type TEXT DEFAULT 'GST',
                internal_type TEXT,
                bill_type TEXT DEFAULT 'CASH',
                subtotal REAL DEFAULT 0,
                discount REAL DEFAULT 0,
                cgst REAL DEFAULT 0,
                sgst REAL DEFAULT 0,
                igst REAL DEFAULT 0,
                round_off REAL DEFAULT 0,
                grand_total REAL DEFAULT 0,
                balance_due REAL DEFAULT 0,
                status TEXT DEFAULT 'Draft',
                notes TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(company_id) REFERENCES companies(id),
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
                company_id INTEGER,
                payment_id TEXT,
                party_id INTEGER,
                amount REAL,
                date TEXT,
                mode TEXT,
                invoice_id INTEGER,
                notes TEXT,
                FOREIGN KEY(company_id) REFERENCES companies(id),
                FOREIGN KEY(party_id) REFERENCES parties(id),
                FOREIGN KEY(invoice_id) REFERENCES invoices(id)
            )
            """
        )
        
        # Create table for purchase invoices (separate from sales invoices)
        self._execute(
            """
            CREATE TABLE IF NOT EXISTS purchase_invoices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER,
                invoice_no TEXT,
                date TEXT,
                supplier_id INTEGER,
                supplier_invoice_no TEXT,
                grand_total REAL DEFAULT 0,
                status TEXT DEFAULT 'Unpaid',
                type TEXT DEFAULT 'GST',
                notes TEXT,
                FOREIGN KEY(company_id) REFERENCES companies(id),
                FOREIGN KEY(supplier_id) REFERENCES parties(id)
            )
            """
        )
        
        # Create table for purchase invoice items (line items)
        self._execute(
            """
            CREATE TABLE IF NOT EXISTS purchase_invoice_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                purchase_invoice_id INTEGER NOT NULL,
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
                FOREIGN KEY(purchase_invoice_id) REFERENCES purchase_invoices(id),
                FOREIGN KEY(product_id) REFERENCES products(id)
            )
            """
        )

    def ensure_seed(self):
        # Seed data is no longer global - each company should create their own data
        # Remove automatic seeding as data should belong to specific companies
        pass

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
        # Add company_id to all relevant tables for data isolation
        for table in ['parties', 'products', 'invoices', 'payments', 'purchase_invoices']:
            try:
                self._ensure_column(table, "company_id", "INTEGER")
            except Exception:
                pass
        
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
            ("warranty_months", "INTEGER DEFAULT 0"),
            ("has_serial_number", "INTEGER DEFAULT 0"),
            ("track_stock", "INTEGER DEFAULT 0"),
            ("is_gst_registered", "INTEGER DEFAULT 0"),
            ("current_stock", "REAL DEFAULT 0"),
            ("created_at", "TEXT"),  # Can't use CURRENT_TIMESTAMP in ALTER TABLE
        ]:
            try:
                self._ensure_column("products", col, decl)
            except Exception:
                pass
        # Invoices - ensure all required columns exist
        for col, decl in [
            ("invoice_no", "TEXT"),
            ("date", "TEXT"),
            ("party_id", "INTEGER"),
            ("tax_type", "TEXT DEFAULT 'GST'"),
            ("internal_type", "TEXT"),
            ("bill_type", "TEXT DEFAULT 'CASH'"),
            ("subtotal", "REAL DEFAULT 0"),
            ("discount", "REAL DEFAULT 0"),
            ("cgst", "REAL DEFAULT 0"),
            ("sgst", "REAL DEFAULT 0"),
            ("igst", "REAL DEFAULT 0"),
            ("round_off", "REAL DEFAULT 0"),
            ("grand_total", "REAL DEFAULT 0"),
            ("balance_due", "REAL DEFAULT 0"),
            ("status", "TEXT DEFAULT 'Draft'"),
            ("notes", "TEXT"),
            ("created_at", "TEXT"),
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
            ("website", "TEXT"),
            ("tax_type", "TEXT"),
            ("fy_start", "TEXT"),
            ("fy_end", "TEXT"),
            ("other_license", "TEXT"),
            ("bank_name", "TEXT"),
            ("account_name", "TEXT"),
            ("account_number", "TEXT"),
            ("ifsc_code", "TEXT"),
            ("logo_path", "TEXT"),
            ("created_at", "TEXT"),  # Can't use CURRENT_TIMESTAMP in ALTER TABLE
        ]:
            try:
                self._ensure_column("companies", col, decl)
            except Exception:
                pass

    # --- companies ---
    def add_company(self, name, gstin=None, mobile=None, email=None, address=None,
                    website=None, tax_type=None, fy_start=None, fy_end=None,
                    other_license=None, bank_name=None, account_name=None,
                    account_number=None, ifsc_code=None, logo_path=None):
        cur = self._execute(
            """INSERT INTO companies(name, gstin, mobile, email, address, website,
               tax_type, fy_start, fy_end, other_license, bank_name, account_name,
               account_number, ifsc_code, logo_path, created_at)
               VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,datetime('now'))""",
            (name, gstin, mobile, email, address, website, tax_type, fy_start,
             fy_end, other_license, bank_name, account_name, account_number,
             ifsc_code, logo_path),
        )
        return cur.lastrowid

    def get_companies(self):
        return self._query("SELECT * FROM companies ORDER BY id DESC")
    
    def get_company_by_id(self, company_id):
        """Get a single company by ID"""
        result = self._query("SELECT * FROM companies WHERE id = ?", (company_id,))
        return result[0] if result else None
    
    def get_company_by_name(self, name):
        """Get a company by its name"""
        result = self._query("SELECT * FROM companies WHERE name = ?", (name,))
        return result[0] if result else None
    
    def update_company(self, company_id, name, gstin=None, mobile=None, email=None, address=None,
                       website=None, tax_type=None, fy_start=None, fy_end=None,
                       other_license=None, bank_name=None, account_name=None,
                       account_number=None, ifsc_code=None, logo_path=None):
        """Update an existing company"""
        self._execute(
            """UPDATE companies SET name=?, gstin=?, mobile=?, email=?, address=?,
               website=?, tax_type=?, fy_start=?, fy_end=?, other_license=?,
               bank_name=?, account_name=?, account_number=?, ifsc_code=?, logo_path=?
               WHERE id=?""",
            (name, gstin, mobile, email, address, website, tax_type, fy_start,
             fy_end, other_license, bank_name, account_name, account_number,
             ifsc_code, logo_path, company_id),
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
            INSERT INTO parties(company_id, name, mobile, email, party_type, gst_number, pan, address, city, state, pincode, opening_balance, balance_type)
            VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)
            """,
            (self._current_company_id, name, phone, email, party_type, gst, pan, address, city, state, pincode, float(opening or 0), bal_type),
        )
        return cur.lastrowid

    def get_parties(self):
        if self._current_company_id:
            return self._query("SELECT * FROM parties WHERE company_id = ? ORDER BY id DESC", (self._current_company_id,))
        return self._query("SELECT * FROM parties ORDER BY id DESC")

    def search_parties(self, search_term: str):
        like = f"%{search_term}%"
        if self._current_company_id:
            return self._query(
                "SELECT * FROM parties WHERE company_id = ? AND (name LIKE ? OR gst_number LIKE ?) ORDER BY id DESC",
                (self._current_company_id, like, like),
            )
        return self._query(
            "SELECT * FROM parties WHERE name LIKE ? OR gst_number LIKE ? ORDER BY id DESC",
            (like, like),
        )

    def delete_party(self, party_id: int):
        self._execute("DELETE FROM parties WHERE id = ?", (party_id,))

    # --- products ---
    def add_product(self, name, hsn_code=None, barcode=None, unit='PCS', sales_rate=0, purchase_rate=0, discount_percent=0, mrp=0, tax_rate=18, sgst_rate=9, cgst_rate=9, opening_stock=0, low_stock=0, product_type='Goods', category=None, description=None, warranty_months=0, has_serial_number=0, track_stock=0, is_gst_registered=0):
        # current_stock starts with opening_stock value
        current_stock = float(opening_stock or 0)
        cur = self._execute(
            """INSERT INTO products(company_id, name, hsn_code, barcode, unit, sales_rate, purchase_rate, 
               discount_percent, mrp, tax_rate, sgst_rate, cgst_rate, opening_stock, low_stock, product_type, 
               category, description, warranty_months, has_serial_number, track_stock, is_gst_registered, 
               current_stock, created_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,datetime('now'))""",
            (self._current_company_id, name, hsn_code, barcode, unit, float(sales_rate or 0), float(purchase_rate or 0), float(discount_percent or 0), float(mrp or 0), float(tax_rate or 0), float(sgst_rate or 0), float(cgst_rate or 0), float(opening_stock or 0), float(low_stock or 0), product_type, category, description, int(warranty_months or 0), int(has_serial_number or 0), int(track_stock or 0), int(is_gst_registered or 0), current_stock),
        )
        return cur.lastrowid

    def update_product(self, data: dict):
        pid = data.get("id")
        if not pid:
            return
        
        # If opening_stock is being updated and track_stock is enabled, 
        # we need to adjust current_stock accordingly
        if 'opening_stock' in data and data.get('track_stock', 0):
            # Get existing product to check the difference
            existing = self.get_product_by_id(pid)
            if existing:
                old_opening = float(existing.get('opening_stock', 0) or 0)
                new_opening = float(data.get('opening_stock', 0) or 0)
                old_current = float(existing.get('current_stock', 0) or 0)
                
                # Adjust current_stock by the difference in opening_stock
                # current_stock = old_current + (new_opening - old_opening)
                difference = new_opening - old_opening
                data['current_stock'] = old_current + difference
        
        # Build dynamic update
        allowed = [
            "name", "hsn_code", "barcode", "unit", "sales_rate", "purchase_rate",
            "discount_percent", "mrp", "tax_rate", "sgst_rate", "cgst_rate", 
            "opening_stock", "low_stock", "product_type", "category", "description",
            "warranty_months", "has_serial_number", "track_stock", "is_gst_registered", "current_stock"
        ]
        parts, vals = [], []
        for k in allowed:
            if k in data:
                parts.append(f"{k}=?")
                vals.append(data[k])
        if not parts:
            return
        vals.append(pid)
        self._execute(f"UPDATE products SET {', '.join(parts)} WHERE id=?", tuple(vals))
        return True

    def get_products(self):
        if self._current_company_id:
            return self._query("SELECT * FROM products WHERE company_id = ? ORDER BY id DESC", (self._current_company_id,))
        return self._query("SELECT * FROM products ORDER BY id DESC")

    def get_product_by_id(self, product_id: int):
        """Get a single product by ID"""
        result = self._query("SELECT * FROM products WHERE id = ?", (product_id,))
        return result[0] if result else None

    def delete_product(self, product_id: int):
        self._execute("DELETE FROM products WHERE id = ?", (product_id,))

    # --- stock management ---
    def update_product_stock(self, product_id: int, quantity_change: float, operation: str = 'add'):
        """
        Update product stock based on operation.
        operation: 'add' for purchase (increase stock), 'subtract' for sales (decrease stock)
        Only updates if track_stock is enabled for the product.
        """
        product = self.get_product_by_id(product_id)
        if not product:
            return False
        
        # Check if track_stock is enabled
        if not product.get('track_stock', 0):
            return False  # Stock tracking not enabled for this product
        
        current_stock = float(product.get('current_stock', 0) or 0)
        
        if operation == 'add':
            new_stock = current_stock + float(quantity_change)
        elif operation == 'subtract':
            new_stock = current_stock - float(quantity_change)
            # Prevent negative stock
            if new_stock < 0:
                new_stock = 0
        else:
            return False
        
        self._execute("UPDATE products SET current_stock = ? WHERE id = ?", (new_stock, product_id))
        return True

    def update_stock_for_purchase_items(self, items: list):
        """
        Update stock for all items in a purchase invoice.
        items: list of dicts with 'product_id' and 'quantity'
        """
        for item in items:
            product_id = item.get('product_id')
            quantity = float(item.get('quantity', 0))
            if product_id and quantity > 0:
                self.update_product_stock(product_id, quantity, 'add')

    def update_stock_for_sales_items(self, items: list):
        """
        Update stock for all items in a sales invoice.
        items: list of dicts with 'product_id' and 'quantity'
        """
        print(f"DEBUG: update_stock_for_sales_items called with {len(items)} items")
        for item in items:
            product_id = item.get('product_id')
            quantity = float(item.get('quantity', 0))
            print(f"DEBUG: Processing item - product_id: {product_id}, quantity: {quantity}")
            if product_id and quantity > 0:
                result = self.update_product_stock(product_id, quantity, 'subtract')
                print(f"DEBUG: update_product_stock returned: {result}")

    # --- invoices ---
    def add_invoice(self, invoice_no, date, party_id, tax_type='GST', subtotal=0, cgst=0, sgst=0, igst=0, round_off=0, grand_total=0, status='Draft', internal_type=None, bill_type='CASH', discount=0, balance_due=0, notes=None):
        cur = self._execute(
            """INSERT INTO invoices(
                company_id, invoice_no, date, party_id, tax_type, internal_type, bill_type,
                subtotal, discount, cgst, sgst, igst, round_off, grand_total,
                balance_due, status, notes
            ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (
                self._current_company_id, invoice_no, date, party_id, tax_type, internal_type, bill_type,
                float(subtotal or 0), float(discount or 0), float(cgst or 0), float(sgst or 0), float(igst or 0),
                float(round_off or 0), float(grand_total or 0), float(balance_due or 0),
                status, notes
            ),
        )
        return cur.lastrowid

    def get_invoices(self):
        if self._current_company_id:
            return self._query("SELECT * FROM invoices WHERE company_id = ? ORDER BY id DESC", (self._current_company_id,))
        return self._query("SELECT * FROM invoices ORDER BY id DESC")

    def update_invoice(self, invoice_data: Dict):
        iid = invoice_data.get('id')
        if not iid:
            return False
        self._execute(
            """UPDATE invoices SET 
                invoice_no = ?, date = ?, party_id = ?, tax_type = ?, internal_type = ?, bill_type = ?,
                subtotal = ?, discount = ?, cgst = ?, sgst = ?, igst = ?, round_off = ?,
                grand_total = ?, balance_due = ?, status = ?, notes = ?
            WHERE id = ?""",
            (
                invoice_data.get('invoice_no'),
                invoice_data.get('date'),
                invoice_data.get('party_id'),
                invoice_data.get('tax_type', 'GST'),
                invoice_data.get('internal_type'),
                invoice_data.get('bill_type', 'CASH'),
                float(invoice_data.get('subtotal') or 0),
                float(invoice_data.get('discount') or 0),
                float(invoice_data.get('cgst') or 0),
                float(invoice_data.get('sgst') or 0),
                float(invoice_data.get('igst') or 0),
                float(invoice_data.get('round_off') or 0),
                float(invoice_data.get('grand_total') or 0),
                float(invoice_data.get('balance_due') or 0),
                invoice_data.get('status', 'Draft'),
                invoice_data.get('notes'),
                iid,
            )
        )
        return True

    def delete_invoice(self, invoice_id: int):
        # Delete invoice items first (foreign key constraint)
        self._execute("DELETE FROM invoice_items WHERE invoice_id = ?", (invoice_id,))
        # Then delete the invoice
        self._execute("DELETE FROM invoices WHERE id = ?", (invoice_id,))

    def get_invoice_by_number(self, invoice_no: str):
        """Get invoice by invoice number"""
        if self._current_company_id:
            invoices = self._query("SELECT * FROM invoices WHERE company_id = ? AND invoice_no = ? LIMIT 1", (self._current_company_id, invoice_no,))
        else:
            invoices = self._query("SELECT * FROM invoices WHERE invoice_no = ? LIMIT 1", (invoice_no,))
        return invoices[0] if invoices else None
        
    def get_invoice_by_id(self, invoice_id: int):
        """Get invoice by ID"""
        invoices = self._query("SELECT * FROM invoices WHERE id = ? LIMIT 1", (invoice_id,))
        return invoices[0] if invoices else None
    
    def invoice_no_exists(self, invoice_no: str):
        """Check if invoice number already exists for current company"""
        if self._current_company_id:
            result = self._query("SELECT COUNT(*) as count FROM invoices WHERE company_id = ? AND invoice_no = ?", (self._current_company_id, invoice_no,))
        else:
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
    def add_payment(self, payment_id, party_id, amount, date, mode='Cash', invoice_id=None, notes=None, payment_type=None):
        """Add a payment or receipt. payment_type should be 'PAYMENT' or 'RECEIPT'"""
        cur = self._execute(
            "INSERT INTO payments(company_id, payment_id, party_id, amount, date, mode, invoice_id, notes, type) VALUES(?,?,?,?,?,?,?,?,?)",
            (self._current_company_id, payment_id, party_id, float(amount or 0), date, mode, invoice_id, notes, payment_type),
        )
        return cur.lastrowid

    def get_payments(self, payment_type=None):
        """Get payments. Optionally filter by type ('PAYMENT' or 'RECEIPT')"""
        if self._current_company_id:
            if payment_type:
                return self._query("""
                    SELECT p.*, pa.name as party_name
                    FROM payments p 
                    LEFT JOIN parties pa ON p.party_id = pa.id 
                    WHERE p.company_id = ? AND p.type = ?
                    ORDER BY p.id DESC
                """, (self._current_company_id, payment_type))
            return self._query("""
                SELECT p.*, pa.name as party_name
                FROM payments p 
                LEFT JOIN parties pa ON p.party_id = pa.id 
                WHERE p.company_id = ?
                ORDER BY p.id DESC
            """, (self._current_company_id,))
        if payment_type:
            return self._query("""
                SELECT p.*, pa.name as party_name
                FROM payments p 
                LEFT JOIN parties pa ON p.party_id = pa.id 
                WHERE p.type = ?
                ORDER BY p.id DESC
            """, (payment_type,))
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
            "UPDATE payments SET payment_id = ?, party_id = ?, amount = ?, date = ?, mode = ?, invoice_id = ?, notes = ?, type = ? WHERE id = ?",
            (
                payment_data.get('payment_id'),
                payment_data.get('party_id'),
                float(payment_data.get('amount') or 0),
                payment_data.get('date'),
                payment_data.get('mode'),
                payment_data.get('invoice_id'),
                payment_data.get('notes'),
                payment_data.get('type'),
                pid,
            ),
        )
        return True

    def delete_payment(self, payment_id: int):
        self._execute("DELETE FROM payments WHERE id = ?", (payment_id,))

    # --- purchase invoices ---
    def add_purchase_invoice(self, invoice_no, date, supplier_id, supplier_invoice_no=None, 
                             invoice_type='GST', grand_total=0, status='Unpaid', notes=None):
        """Add a new purchase invoice"""
        cur = self._execute(
            """INSERT INTO purchase_invoices(company_id, invoice_no, date, supplier_id, supplier_invoice_no, 
               grand_total, status, type, notes) VALUES(?,?,?,?,?,?,?,?,?)""",
            (self._current_company_id, invoice_no, date, supplier_id, supplier_invoice_no, float(grand_total or 0), 
             status, invoice_type, notes),
        )
        return cur.lastrowid

    def get_purchase_invoices(self):
        """Get all purchase invoices for current company"""
        if self._current_company_id:
            return self._query("SELECT * FROM purchase_invoices WHERE company_id = ? ORDER BY id DESC", (self._current_company_id,))
        return self._query("SELECT * FROM purchase_invoices ORDER BY id DESC")

    def get_purchase_invoice_by_id(self, purchase_id: int):
        """Get purchase invoice by ID"""
        invoices = self._query("SELECT * FROM purchase_invoices WHERE id = ? LIMIT 1", (purchase_id,))
        return invoices[0] if invoices else None

    def get_purchase_invoice_by_number(self, invoice_no: str):
        """Get purchase invoice by invoice number"""
        if self._current_company_id:
            invoices = self._query("SELECT * FROM purchase_invoices WHERE company_id = ? AND invoice_no = ? LIMIT 1", (self._current_company_id, invoice_no,))
        else:
            invoices = self._query("SELECT * FROM purchase_invoices WHERE invoice_no = ? LIMIT 1", (invoice_no,))
        return invoices[0] if invoices else None

    def update_purchase_invoice(self, invoice_data: Dict):
        """Update an existing purchase invoice"""
        pid = invoice_data.get('id')
        if not pid:
            return False
        self._execute(
            """UPDATE purchase_invoices SET invoice_no = ?, date = ?, supplier_id = ?, 
               supplier_invoice_no = ?, grand_total = ?, status = ?, type = ?, notes = ? WHERE id = ?""",
            (
                invoice_data.get('invoice_no'),
                invoice_data.get('date'),
                invoice_data.get('supplier_id'),
                invoice_data.get('supplier_invoice_no'),
                float(invoice_data.get('grand_total') or 0),
                invoice_data.get('status', 'Unpaid'),
                invoice_data.get('type', 'GST'),
                invoice_data.get('notes'),
                pid,
            ),
        )
        return True

    def delete_purchase_invoice(self, purchase_id: int):
        """Delete a purchase invoice and its items"""
        self._execute("DELETE FROM purchase_invoice_items WHERE purchase_invoice_id = ?", (purchase_id,))
        self._execute("DELETE FROM purchase_invoices WHERE id = ?", (purchase_id,))

    def purchase_invoice_no_exists(self, invoice_no: str):
        """Check if purchase invoice number already exists for current company"""
        if self._current_company_id:
            result = self._query("SELECT COUNT(*) as count FROM purchase_invoices WHERE company_id = ? AND invoice_no = ?", (self._current_company_id, invoice_no,))
        else:
            result = self._query("SELECT COUNT(*) as count FROM purchase_invoices WHERE invoice_no = ?", (invoice_no,))
        return result[0]['count'] > 0 if result else False

    # --- purchase invoice items ---
    def add_purchase_invoice_item(self, purchase_invoice_id: int, product_id: int, product_name: str,
                                  hsn_code: str = None, quantity: float = 0, unit: str = 'Piece',
                                  rate: float = 0, discount_percent: float = 0, discount_amount: float = 0,
                                  tax_percent: float = 0, tax_amount: float = 0, amount: float = 0):
        """Add a line item to a purchase invoice"""
        cur = self._execute(
            """INSERT INTO purchase_invoice_items(purchase_invoice_id, product_id, product_name, hsn_code,
               quantity, unit, rate, discount_percent, discount_amount, tax_percent, tax_amount, amount)
               VALUES(?,?,?,?,?,?,?,?,?,?,?,?)""",
            (purchase_invoice_id, product_id, product_name, hsn_code, float(quantity), unit,
             float(rate), float(discount_percent), float(discount_amount),
             float(tax_percent), float(tax_amount), float(amount))
        )
        return cur.lastrowid

    def get_purchase_invoice_items(self, purchase_invoice_id: int):
        """Get all line items for a purchase invoice"""
        return self._query("SELECT * FROM purchase_invoice_items WHERE purchase_invoice_id = ? ORDER BY id", 
                          (purchase_invoice_id,))

    def delete_purchase_invoice_items(self, purchase_invoice_id: int):
        """Delete all line items for a purchase invoice"""
        self._execute("DELETE FROM purchase_invoice_items WHERE purchase_invoice_id = ?", (purchase_invoice_id,))

    def get_purchase_invoice_with_items(self, invoice_no: str):
        """Get complete purchase invoice with line items"""
        invoice = self.get_purchase_invoice_by_number(invoice_no)
        if not invoice:
            return None
        
        # Get supplier details
        supplier = None
        if invoice.get('supplier_id'):
            parties = self._query("SELECT * FROM parties WHERE id = ?", (invoice['supplier_id'],))
            supplier = parties[0] if parties else None
        
        # Get line items
        items = self.get_purchase_invoice_items(invoice['id'])
        
        return {
            'invoice': invoice,
            'party': supplier,
            'items': items
        }

    def get_purchase_invoice_with_items_by_id(self, purchase_id: int):
        """Get complete purchase invoice with line items by ID"""
        invoice = self.get_purchase_invoice_by_id(purchase_id)
        if not invoice:
            return None
        
        # Get supplier details
        supplier = None
        if invoice.get('supplier_id'):
            parties = self._query("SELECT * FROM parties WHERE id = ?", (invoice['supplier_id'],))
            supplier = parties[0] if parties else None
        
        # Get line items
        items = self.get_purchase_invoice_items(invoice['id'])
        
        return {
            'invoice': invoice,
            'party': supplier,
            'items': items
        }

    # --- data migration utilities ---
    def migrate_data_to_company(self, company_id: int):
        """
        Migrate all existing data (with NULL company_id) to a specific company.
        This is useful for one-time migration of legacy data.
        """
        tables = ['parties', 'products', 'invoices', 'payments', 'purchase_invoices']
        migrated = {}
        for table in tables:
            result = self._execute(
                f"UPDATE {table} SET company_id = ? WHERE company_id IS NULL",
                (company_id,)
            )
            migrated[table] = result.rowcount
        return migrated

    def get_unassigned_data_count(self):
        """
        Get count of records without a company_id assigned.
        Useful to check if migration is needed.
        """
        tables = ['parties', 'products', 'invoices', 'payments', 'purchase_invoices']
        counts = {}
        for table in tables:
            result = self._query(f"SELECT COUNT(*) as count FROM {table} WHERE company_id IS NULL")
            counts[table] = result[0]['count'] if result else 0
        return counts


# single global instance used by the app
db = Database()
