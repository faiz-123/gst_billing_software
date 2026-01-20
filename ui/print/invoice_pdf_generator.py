"""
Simple HTML-based PDF invoice generator for GST Billing Software
Uses basic HTML generation and opens in browser for manual PDF saving
"""

import os
import sys
import tempfile
from datetime import datetime
import webbrowser

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from core.db.sqlite_db import db
from core.core_utils import number_to_words_indian, format_currency
from config import config


def _get_project_root():
    """Get the project root directory"""
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class InvoicePDFGenerator:
    """Professional GST invoice PDF generator using HTML/CSS templates"""
    
    def __init__(self):
        project_root = _get_project_root()
        self.gst_template_path = os.path.join(project_root, 'templates', 'invoice.html')
        self.non_gst_template_path = os.path.join(project_root, 'templates', 'invoice_non_gst.html')
        self.template_path = self.gst_template_path  # Default
    
    def get_template_path(self, invoice_type):
        """Get the appropriate template path based on invoice type"""
        if invoice_type and invoice_type.upper() in ['NON-GST', 'NON GST', 'NONGST']:
            return self.non_gst_template_path
        return self.gst_template_path
    
    def generate_invoice_pdf(self, invoice_id, auto_open_browser=True):
        """Generate PDF for the given invoice ID
        
        Since complex PDF libraries have dependencies issues,
        this method generates HTML and optionally opens it in browser for manual PDF save.
        
        Args:
            invoice_id (int): ID of the invoice to generate PDF for
            auto_open_browser (bool): Whether to automatically open in browser
            
        Returns:
            str: Path to the generated HTML file
        """
        try:
            # Get invoice data with items and party details
            invoice_data = self.get_invoice_data(invoice_id)
            if not invoice_data:
                raise Exception(f"Invoice with ID {invoice_id} not found")
            
            # Determine template based on invoice type
            invoice_type = invoice_data['invoice'].get('tax_type', 'GST')
            self.template_path = self.get_template_path(invoice_type)
            
            # Prepare template data based on invoice type
            if invoice_type and invoice_type.upper() in ['NON-GST', 'NON GST', 'NONGST']:
                template_data = self.prepare_non_gst_template_data(invoice_data)
            else:
                template_data = self.prepare_template_data(invoice_data)
            
            # Load and render HTML template
            html_content = self.render_html_template(template_data, invoice_type)
            
            # Create temporary HTML file
            temp_dir = tempfile.gettempdir()
            html_filename = f"invoice_{invoice_data['invoice']['invoice_no']}.html"
            html_path = os.path.join(temp_dir, html_filename)
            
            # Save HTML file
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            # Optionally open in browser for manual PDF save
            if auto_open_browser:
                webbrowser.open('file://' + html_path)
                print(f"Invoice HTML opened in browser: {html_path}")
                print("To save as PDF: Press Ctrl+P (or Cmd+P on Mac) and save as PDF")
            else:
                print(f"Invoice HTML generated: {html_path}")
            
            return html_path
            
        except Exception as e:
            print(f"Error generating PDF: {e}")
            return None
    
    def get_invoice_data(self, invoice_id):
        """Get complete invoice data including items and party details"""
        try:
            # Get invoice
            invoice = db.get_invoice_by_id(invoice_id)
            if not invoice:
                return None
            
            # Get party details
            party = None
            if invoice['party_id']:
                parties = db._query("SELECT * FROM parties WHERE id = ?", (invoice['party_id'],))
                party = parties[0] if parties else None
            
            # Get line items
            items = db.get_invoice_items(invoice_id)
            
            # Get company details from config
            company = self.get_company_details()
            
            return {
                'invoice': invoice,
                'party': party,
                'items': items,
                'company': company
            }
        except Exception as e:
            print(f"Error getting invoice data: {e}")
            return None
    
    def get_company_details(self):
        """Get company details from config or database"""
        try:
            # Try to get from config first
            if hasattr(config, 'data') and config.data:
                company_data = config.data.get('company', {})
                if company_data:
                    return company_data
            
            # Fallback: get from companies table
            companies = db._query("SELECT * FROM companies LIMIT 1")
            if companies:
                return companies[0]
            
            # Default company details if none found
            return {
                'name': 'SUPER POWER BATTERIES (INDIA)',
                'address': 'A-12, Gangotri Appartment, R. V. Desai Road, Vadodara - 390001 Gujarat',
                'phone': '0265-2423031, 8511597157',
                'email': '',
                'gstin': '24AADPP6173E1ZT',
                'terms': 'Subject to Vadodara - 390001 jurisdiction E.& O.E'
            }
        except:
            # Return default if anything fails
            return {
                'name': 'SUPER POWER BATTERIES (INDIA)',
                'address': 'A-12, Gangotri Appartment, R. V. Desai Road, Vadodara - 390001 Gujarat',
                'phone': '0265-2423031, 8511597157',
                'email': '',
                'gstin': '24AADPP6173E1ZT',
                'terms': 'Subject to Vadodara - 390001 jurisdiction E.& O.E'
            }
    
    def prepare_template_data(self, invoice_data):
        """Prepare data for HTML template rendering"""
        invoice = invoice_data['invoice']
        party = invoice_data['party'] or {}
        items = invoice_data['items']
        company = invoice_data['company']
        
        # Format the invoice date
        invoice_date = invoice.get('date', datetime.now().strftime('%Y-%m-%d'))
        try:
            date_obj = datetime.strptime(invoice_date, '%Y-%m-%d')
            formatted_date = date_obj.strftime('%d-%m-%Y')
        except:
            formatted_date = invoice_date
        
        # Calculate totals and prepare item data
        total_quantity = 0
        total_discount = 0
        subtotal_taxable = 0
        total_cgst = 0
        total_sgst = 0
        total_igst = 0
        gst_summary = {}
        
        processed_items = []
        
        for item in items:
            quantity = float(item.get('quantity', 0))
            rate = float(item.get('rate', 0))
            discount_percent = float(item.get('discount_percent', 0))
            tax_percent = float(item.get('tax_percent', 0))
            
            total_val = quantity * rate
            discount_amt = total_val * (discount_percent / 100)
            taxable_amt = total_val - discount_amt
            
            # GST calculation (assuming intra-state for CGST/SGST)
            total_tax = taxable_amt * (tax_percent / 100)
            cgst_rate = tax_percent / 2 if tax_percent > 0 else 0
            sgst_rate = tax_percent / 2 if tax_percent > 0 else 0
            cgst_amount = total_tax / 2 if total_tax > 0 else 0
            sgst_amount = total_tax / 2 if total_tax > 0 else 0
            igst_rate = 0  # For interstate transactions
            igst_amount = 0
            
            final_amount = taxable_amt + total_tax
            
            # Add to totals
            total_quantity += quantity
            total_discount += discount_amt
            subtotal_taxable += taxable_amt
            total_cgst += cgst_amount
            total_sgst += sgst_amount
            total_igst += igst_amount
            
            # GST summary
            if tax_percent not in gst_summary:
                gst_summary[tax_percent] = {
                    'rate': int(tax_percent),
                    'taxable_amt': 0,
                    'cgst_amt': 0,
                    'sgst_amt': 0,
                    'tax_amt': 0
                }
            
            gst_summary[tax_percent]['taxable_amt'] += taxable_amt
            gst_summary[tax_percent]['cgst_amt'] += cgst_amount
            gst_summary[tax_percent]['sgst_amt'] += sgst_amount
            gst_summary[tax_percent]['tax_amt'] += total_tax
            
            # Prepare item data for template
            processed_items.append({
                'description': item.get('product_name', ''),
                'hsn_code': item.get('hsn_code', ''),
                'mrp': f"{rate:.0f}" if rate > 0 else "0",
                'quantity': f"{quantity:.0f}",
                'rate': f"{rate:.2f}",
                'total_val': f"{total_val:.2f}",
                'discount_percent': f"{discount_percent:.2f}" if discount_percent > 0 else "0.00",
                'discount_amt': f"{discount_amt:.2f}" if discount_amt > 0 else "0.00",
                'taxable_amt': f"{taxable_amt:.2f}",
                'cgst_percent': f"{cgst_rate:.1f}" if cgst_rate > 0 else "0",
                'cgst_amt': f"{cgst_amount:.2f}" if cgst_amount > 0 else "0.00",
                'sgst_percent': f"{sgst_rate:.1f}" if sgst_rate > 0 else "0",
                'sgst_amt': f"{sgst_amount:.2f}" if sgst_amount > 0 else "0.00",
                'igst_percent': f"{igst_rate:.1f}" if igst_rate > 0 else "0",
                'igst_amt': f"{igst_amount:.2f}" if igst_amount > 0 else "0.00",
                'total': f"{final_amount:.2f}"
            })
        
        # Calculate final totals
        grand_total = float(invoice.get('grand_total', subtotal_taxable + total_cgst + total_sgst))
        total_tax_amount = total_cgst + total_sgst + total_igst
        total_after_tax = subtotal_taxable + total_tax_amount
        round_off = grand_total - total_after_tax
        
        # Amount in words
        amount_words = number_to_words_indian(grand_total)
        
        # Prepare GST summary for template
        gst_summary_list = []
        for rate, amounts in gst_summary.items():
            if amounts['taxable_amt'] > 0:
                gst_summary_list.append({
                    'rate': amounts['rate'],
                    'taxable_amt': f"{amounts['taxable_amt']:.2f}",
                    'sgst_amt': f"{amounts['sgst_amt']:.2f}",
                    'cgst_amt': f"{amounts['cgst_amt']:.2f}",
                    'tax_amt': f"{amounts['tax_amt']:.2f}"
                })
        
        # Prepare buyer location
        buyer_location_parts = []
        if party.get('city'):
            buyer_location_parts.append(party['city'])
        if party.get('state'):
            buyer_location_parts.append(party['state'])
        buyer_location = ' '.join(buyer_location_parts)
        
        return {
            # Company details
            'company_name': company.get('name', 'SUPER POWER BATTERIES (INDIA)'),
            'company_address': company.get('address', 'A-12, Gangotri Appartment, R. V. Desai Road, Vadodara - 390001 Gujarat'),
            'company_contact': f"Ph. : {company.get('phone', '0265-2423031, 8511597157')} E mail : {company.get('email', '')}",
            'company_gstin': company.get('gstin', '24AADPP6173E1ZT'),
            
            # Invoice details
            'invoice_no': invoice.get('invoice_no', ''),
            'invoice_date': formatted_date,
            'terms': invoice.get('bill_type', 'Credit'),
            'tax_type': invoice.get('tax_type', 'GST'),
            'ref_no': '',
            'vehicle_no': '',
            'transport': '',
            
            # Buyer details
            'buyer_name': party.get('name', 'Unknown Customer'),
            'buyer_address': party.get('address', ''),
            'buyer_location': buyer_location,
            'buyer_contact': party.get('mobile', ''),
            'buyer_gstin': party.get('gst_number', ''),
            
            # Items
            'items': processed_items,
            
            # Totals
            'total_quantity': f"{total_quantity:.0f}",
            'total_discount': f"{total_discount:.2f}",
            'subtotal_taxable': f"{subtotal_taxable:.2f}",
            'total_cgst': f"{total_cgst:.2f}",
            'total_sgst': f"{total_sgst:.2f}",
            'total_igst': f"{total_igst:.2f}",
            
            # GST Summary
            'gst_summary': gst_summary_list,
            
            # Bottom totals
            'total_before_tax': f"{subtotal_taxable:.2f}",
            'total_cgst_igst': f"{total_cgst:.2f}",
            'total_tax_amount': f"{total_tax_amount:.2f}",
            'total_after_tax': f"{total_after_tax:.2f}",
            'round_off': f"{round_off:.2f}",
            'net_amount': f"{grand_total:.2f}",
            'amount_in_words': amount_words,
            
            # Bank details
            'bank_name': 'BANK OF INDIA',
            'bank_account': 'A/C NO:00-250271000001287',
            'bank_ifsc': 'IFSC CODE: BKID0002503',
            
            # Terms
            'terms_conditions': company.get('terms', 'Subject to Vadodara - 390001 jurisdiction E.& O.E')
        }
    
    def prepare_non_gst_template_data(self, invoice_data):
        """Prepare data for Non-GST HTML template rendering (no tax fields)"""
        invoice = invoice_data['invoice']
        party = invoice_data['party'] or {}
        items = invoice_data['items']
        company = invoice_data['company']
        
        # Format the invoice date
        invoice_date = invoice.get('date', datetime.now().strftime('%Y-%m-%d'))
        try:
            date_obj = datetime.strptime(invoice_date, '%Y-%m-%d')
            formatted_date = date_obj.strftime('%d-%m-%Y')
        except:
            formatted_date = invoice_date
        
        # Calculate totals and prepare item data (no tax calculations)
        total_quantity = 0
        total_discount = 0
        subtotal_amount = 0
        
        processed_items = []
        
        for item in items:
            quantity = float(item.get('quantity', 0))
            rate = float(item.get('rate', 0))
            discount_percent = float(item.get('discount_percent', 0))
            
            total_val = quantity * rate
            discount_amt = total_val * (discount_percent / 100)
            final_amount = total_val - discount_amt
            
            # Add to totals
            total_quantity += quantity
            total_discount += discount_amt
            subtotal_amount += final_amount
            
            # Prepare item data for template (no tax columns)
            processed_items.append({
                'description': item.get('product_name', ''),
                'hsn_code': item.get('hsn_code', ''),
                'mrp': f"{rate:.0f}" if rate > 0 else "0",
                'quantity': f"{quantity:.0f}",
                'rate': f"{rate:.2f}",
                'total_val': f"{total_val:.2f}",
                'discount_percent': f"{discount_percent:.2f}" if discount_percent > 0 else "0.00",
                'discount_amt': f"{discount_amt:.2f}" if discount_amt > 0 else "0.00",
                'amount': f"{final_amount:.2f}"
            })
        
        # Calculate final totals
        grand_total = float(invoice.get('grand_total', subtotal_amount))
        round_off = grand_total - subtotal_amount
        
        # Amount in words
        amount_words = number_to_words_indian(grand_total)
        
        # Prepare buyer location
        buyer_location_parts = []
        if party.get('city'):
            buyer_location_parts.append(party['city'])
        if party.get('state'):
            buyer_location_parts.append(party['state'])
        buyer_location = ' '.join(buyer_location_parts)
        
        return {
            # Company details
            'company_name': company.get('name', 'SUPER POWER BATTERIES (INDIA)'),
            'company_address': company.get('address', 'A-12, Gangotri Appartment, R. V. Desai Road, Vadodara - 390001 Gujarat'),
            'company_contact': f"Ph. : {company.get('phone', '0265-2423031, 8511597157')} E mail : {company.get('email', '')}",
            
            # Invoice details
            'invoice_no': invoice.get('invoice_no', ''),
            'invoice_date': formatted_date,
            'terms': invoice.get('bill_type', 'Credit'),
            'ref_no': '',
            'vehicle_no': '',
            'transport': '',
            
            # Buyer details
            'buyer_name': party.get('name', 'Unknown Customer'),
            'buyer_address': party.get('address', ''),
            'buyer_location': buyer_location,
            'buyer_contact': party.get('mobile', ''),
            
            # Items
            'items': processed_items,
            
            # Totals
            'total_quantity': f"{total_quantity:.0f}",
            'total_discount': f"{total_discount:.2f}",
            'subtotal_amount': f"{subtotal_amount:.2f}",
            
            # Bottom totals
            'round_off': f"{round_off:.2f}",
            'net_amount': f"{grand_total:.2f}",
            'amount_in_words': amount_words,
            
            # Bank details
            'bank_name': company.get('bank_name', 'BANK OF INDIA'),
            'bank_account': company.get('bank_account', 'A/C NO:00-250271000001287'),
            'bank_ifsc': company.get('bank_ifsc', 'IFSC CODE: BKID0002503'),
            
            # Terms
            'terms_conditions': company.get('terms', 'Subject to Vadodara - 390001 jurisdiction E.& O.E')
        }
    
    def render_html_template(self, template_data, invoice_type='GST'):
        """Render HTML template with data using comprehensive string replacement"""
        try:
            # Read template file
            with open(self.template_path, 'r', encoding='utf-8') as f:
                template_content = f.read()
            
            # Replace basic template variables with {{ key }} format
            html_content = template_content
            
            # Replace simple variables
            for key, value in template_data.items():
                if not isinstance(value, (list, dict)):
                    placeholder = "{{ " + key + " }}"
                    html_content = html_content.replace(placeholder, str(value))
            
            # Check if this is a Non-GST invoice
            is_non_gst = invoice_type and invoice_type.upper() in ['Non-GST', 'NON-GST', 'NON GST', 'NONGST']

            # Handle items table - build complete tbody content
            items_html = ""
            for idx, item in enumerate(template_data['items'], 1):
                if is_non_gst:
                    # Non-GST row format (no tax columns)
                    row_html = f"""
                    <tr>
                        <td class="sr">{idx}</td>
                        <td class="description">{item['description']}</td>
                        <td>{item['hsn_code']}</td>
                        <td class="amount">{item['mrp']}</td>
                        <td>{item['quantity']}</td>
                        <td class="amount">{item['rate']}</td>
                        <td class="amount">{item['total_val']}</td>
                        <td>{item['discount_percent']}</td>
                        <td class="amount highlight-col">{item['discount_amt']}</td>
                        <td class="amount highlight-col">{item['amount']}</td>
                    </tr>
                """
                else:
                    # GST row format (with all tax columns)
                    row_html = f"""
                    <tr>
                        <td class="sr">{idx}</td>
                        <td class="description">{item['description']}</td>
                        <td>{item['hsn_code']}</td>
                        <td class="amount">{item['mrp']}</td>
                        <td>{item['quantity']}</td>
                        <td class="amount">{item['rate']}</td>
                        <td class="amount">{item['total_val']}</td>
                        <td>{item['discount_percent']}</td>
                        <td class="amount highlight-col">{item['discount_amt']}</td>
                        <td class="amount highlight-col">{item['taxable_amt']}</td>
                        <td>{item['cgst_percent']}</td>
                        <td class="amount">{item['cgst_amt']}</td>
                        <td>{item['sgst_percent']}</td>
                        <td class="amount">{item['sgst_amt']}</td>
                        <td>{item['igst_percent']}</td>
                        <td class="amount">{item['igst_amt']}</td>
                        <td class="amount">{item['total']}</td>
                    </tr>
                """
                items_html += row_html
            
            # Add empty rows for better layout
            empty_row_count = max(0, 8 - len(template_data['items']))
            for i in range(empty_row_count):
                if is_non_gst:
                    # Non-GST empty row (10 columns)
                    items_html += """
                    <tr>
                        <td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td>
                        <td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td>
                        <td class="highlight-col">&nbsp;</td><td class="highlight-col">&nbsp;</td>
                    </tr>
                """
                else:
                    # GST empty row (17 columns)
                    items_html += """
                    <tr>
                        <td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td>
                        <td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td>
                        <td class="highlight-col">&nbsp;</td><td class="highlight-col">&nbsp;</td>
                        <td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td>
                        <td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td>
                    </tr>
                """
            
            # Add subtotals row
            if is_non_gst:
                # Non-GST subtotals row
                subtotals_html = f"""
                <tr class="sub-totals">
                    <td></td>
                    <td style="text-align: right; padding-right: 5px;">Sub Totals ></td>
                    <td></td><td></td>
                    <td>{template_data['total_quantity']}</td>
                    <td></td><td></td><td></td>
                    <td class="amount highlight-col">{template_data['total_discount']}</td>
                    <td class="amount highlight-col">{template_data['subtotal_amount']}</td>
                </tr>
            """
            else:
                # GST subtotals row
                subtotals_html = f"""
                <tr class="sub-totals">
                    <td></td>
                    <td style="text-align: right; padding-right: 5px;">Sub Totals ></td>
                    <td></td><td></td>
                    <td>{template_data['total_quantity']}</td>
                    <td></td><td></td><td></td>
                    <td class="amount highlight-col">{template_data['total_discount']}</td>
                    <td class="amount highlight-col">{template_data['subtotal_taxable']}</td>
                    <td></td>
                    <td class="amount">{template_data['total_cgst']}</td>
                    <td></td>
                    <td class="amount">{template_data['total_sgst']}</td>
                    <td></td>
                    <td class="amount">{template_data['total_igst']}</td>
                    <td></td>
                </tr>
            """
            
            items_html += subtotals_html
            
            # Clean template control structures and replace items table
            # Remove Jinja2 for loops and template syntax
            template_cleanups = [
                ('{% for item in items %}', ''),
                ('{% endfor %}', ''),
                ('{{ loop.index }}', ''),
                ('{% for i in range(10 - items|length) %}', ''),
                ('{{ item.description }}', ''),
                ('{{ item.hsn_code }}', ''),
                ('{{ item.mrp }}', ''),
                ('{{ item.quantity }}', ''),
                ('{{ item.rate }}', ''),
                ('{{ item.total_val }}', ''),
                ('{{ item.discount_percent }}', ''),
                ('{{ item.discount_amt }}', ''),
                ('{{ item.amount }}', ''),  # For Non-GST
                ('{{ item.taxable_amt }}', ''),
                ('{{ item.cgst_percent }}', ''),
                ('{{ item.cgst_amt }}', ''),
                ('{{ item.sgst_percent }}', ''),
                ('{{ item.sgst_amt }}', ''),
                ('{{ item.igst_percent }}', ''),
                ('{{ item.igst_amt }}', ''),
                ('{{ item.total }}', '')
            ]
            
            for old_text, new_text in template_cleanups:
                html_content = html_content.replace(old_text, new_text)
            
            # Find and replace items table tbody
            tbody_start = html_content.find('<tbody>')
            tbody_end = html_content.find('</tbody>') + len('</tbody>')
            if tbody_start != -1 and tbody_end != -1:
                before_tbody = html_content[:tbody_start + len('<tbody>')]
                after_tbody = html_content[tbody_end - len('</tbody>'):]
                html_content = before_tbody + items_html + after_tbody
            
            # Handle GST summary table (only for GST invoices)
            if not is_non_gst and 'gst_summary' in template_data:
                gst_html = ""
                for gst_row in template_data['gst_summary']:
                    gst_html += f"""
                    <tr>
                        <td>{gst_row['rate']}%</td>
                        <td class="amount">{gst_row['taxable_amt']}</td>
                        <td class="amount">{gst_row['sgst_amt']}</td>
                        <td class="amount">{gst_row['cgst_amt']}</td>
                        <td class="amount">{gst_row['tax_amt']}</td>
                    </tr>
                """
            
                # Clean GST summary template syntax
                gst_cleanups = [
                    ('{% for gst_row in gst_summary %}', ''),
                    ('{{ gst_row.rate }}', ''),
                    ('{{ gst_row.taxable_amt }}', ''),
                    ('{{ gst_row.sgst_amt }}', ''),
                    ('{{ gst_row.cgst_amt }}', ''),
                    ('{{ gst_row.tax_amt }}', '')
                ]
                
                for old_gst, new_gst in gst_cleanups:
                    html_content = html_content.replace(old_gst, new_gst)
                
                # Find and replace GST table tbody (look for second tbody)
                gst_table_start = html_content.find('<table class="gst-table">')
                if gst_table_start != -1:
                    gst_tbody_start = html_content.find('<tbody>', gst_table_start)
                    gst_tbody_end = html_content.find('</tbody>', gst_tbody_start) + len('</tbody>')
                    if gst_tbody_start != -1 and gst_tbody_end != -1:
                        before_gst = html_content[:gst_tbody_start + len('<tbody>')]
                        after_gst = html_content[gst_tbody_end - len('</tbody>'):]
                        html_content = before_gst + gst_html + after_gst
            
            return html_content
            
        except Exception as e:
            print(f"Error rendering HTML template: {e}")
            import traceback
            traceback.print_exc()
            raise


# Convenience function for use in other modules
def generate_invoice_pdf(invoice_id, auto_open_browser=True):
    """Generate PDF for an invoice using HTML/CSS approach
    
    Args:
        invoice_id (int): ID of the invoice to generate PDF for
        auto_open_browser (bool): Whether to automatically open in browser
    Returns:
        str: Path to the generated HTML file
    """
    generator = InvoicePDFGenerator()
    return generator.generate_invoice_pdf(invoice_id, auto_open_browser)
