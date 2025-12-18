"""In-memory database stub used when running UI-only mode.

This lightweight stub implements the `db` API used across the app but
keeps everything in-memory. It's intended for UI-only runs and tests.
"""

from typing import List, Dict, Optional


class Database:
    def __init__(self):
        self._next_id = 1
        self.parties: List[Dict] = []
        self.products: List[Dict] = []
        self.invoices: List[Dict] = []
        self.payments: List[Dict] = []
        self.companies: List[Dict] = []
        self.create_sample_data()

    def _alloc_id(self):
        i = self._next_id
        self._next_id += 1
        return i

    def create_tables(self):
        # no-op for in-memory stub
        return

    def create_sample_data(self):
        self.parties = [
            {'id': self._alloc_id(), 'name': 'Demo Customer', 'phone': '9999999999', 'email': 'demo@example.com', 'type': 'Customer', 'gst_number': '', 'opening_balance': 0},
            {'id': self._alloc_id(), 'name': 'Sample Supplier', 'phone': '8888888888', 'email': 'supplier@example.com', 'type': 'Supplier', 'gst_number': '', 'opening_balance': 0},
        ]
        self.products = [
            {'id': self._alloc_id(), 'name': 'Sample Product', 'hsn_code': '', 'sales_rate': 100.0, 'stock_quantity': 10},
        ]

    # Companies
    def add_company(self, name, gstin=None, mobile=None, email=None, address=None):
        company = {'id': self._alloc_id(), 'name': name, 'gstin': gstin, 'mobile': mobile, 'email': email, 'address': address}
        self.companies.append(company)
        return company['id']

    def get_companies(self):
        return list(self.companies)

    # Parties
    def add_party(self, name, mobile=None, email=None, gstin=None, pan=None, address=None, city=None, party_type='Customer'):
        p = {'id': self._alloc_id(), 'name': name, 'phone': mobile or '', 'email': email or '', 'type': party_type, 'gst_number': gstin or '', 'opening_balance': 0}
        self.parties.append(p)
        return p['id']

    def get_parties(self):
        return list(self.parties)

    def search_parties(self, search_term: str):
        s = search_term.lower()
        return [p for p in self.parties if s in p.get('name', '').lower() or s in p.get('gst_number', '').lower()]

    def delete_party(self, party_id: int):
        self.parties = [p for p in self.parties if p.get('id') != party_id]

    # Products
    def add_product(self, name, hsn_code=None, barcode=None, unit='PCS', sales_rate=0, purchase_rate=0, discount_percent=0, mrp=0, stock_quantity=0, product_type='Goods'):
        prod = {'id': self._alloc_id(), 'name': name, 'hsn_code': hsn_code or '', 'sales_rate': sales_rate, 'stock_quantity': stock_quantity}
        self.products.append(prod)
        return prod['id']

    def update_product(self, product_data: Dict):
        for i, p in enumerate(self.products):
            if p['id'] == product_data.get('id'):
                self.products[i].update(product_data)
                return True
        return False

    def get_products(self):
        return list(self.products)

    def delete_product(self, product_id: int):
        self.products = [p for p in self.products if p.get('id') != product_id]

    # Invoices (minimal)
    def add_invoice(self, invoice_no, date, party_id, invoice_type='GST', subtotal=0, cgst=0, sgst=0, igst=0, round_off=0, grand_total=0):
        inv = {'id': self._alloc_id(), 'invoice_no': invoice_no, 'date': date, 'party_id': party_id, 'grand_total': grand_total}
        self.invoices.append(inv)
        return inv['id']

    def get_invoices(self):
        return list(self.invoices)

    def update_invoice(self, invoice_data: Dict):
        for i, inv in enumerate(self.invoices):
            if inv['id'] == invoice_data.get('id'):
                self.invoices[i].update(invoice_data)
                return True
        return False

    def delete_invoice(self, invoice_id: int):
        self.invoices = [inv for inv in self.invoices if inv.get('id') != invoice_id]

    # Payments (minimal)
    def add_payment(self, payment_id, party_id, amount, date, mode='Cash', invoice_id=None, notes=None):
        pay = {'id': self._alloc_id(), 'payment_id': payment_id, 'party_id': party_id, 'amount': amount, 'date': date}
        self.payments.append(pay)
        return pay['id']

    def get_payments(self):
        return list(self.payments)

    def update_payment(self, payment_data: Dict):
        for i, p in enumerate(self.payments):
            if p['id'] == payment_data.get('id'):
                self.payments[i].update(payment_data)
                return True
        return False

    def delete_payment(self, payment_id: int):
        self.payments = [p for p in self.payments if p.get('id') != payment_id]


# single global instance used by the app
db = Database()
