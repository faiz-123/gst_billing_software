"""
Invoice Preview Utility - Common print preview functionality
Used by both InvoicesScreen and InvoiceDialog
"""

import tempfile
import os
import webbrowser

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QFrame, QMessageBox, QFileDialog
)
from PyQt5.QtCore import Qt

from theme import PRIMARY, WHITE, BORDER


def show_invoice_preview(parent, invoice_id):
    """
    Show HTML preview dialog for an invoice.
    This is the main entry point for showing invoice previews.
    
    Args:
        parent: Parent widget (QWidget)
        invoice_id: ID of the invoice to preview
    """
    try:
        # Generate HTML content
        html_content = generate_invoice_html(parent, invoice_id)
        if not html_content:
            return
        
        # Show HTML preview dialog
        show_html_preview_dialog(parent, html_content, invoice_id)
        
    except Exception as e:
        QMessageBox.critical(parent, "Preview Error", f"Failed to show print preview: {str(e)}")


def generate_invoice_html(parent, invoice_id):
    """Generate HTML content for the invoice"""
    try:
        from ui.print.invoice_pdf_generator import InvoicePDFGenerator
        generator = InvoicePDFGenerator()
        
        # Get invoice data
        invoice_data = generator.get_invoice_data(invoice_id)
        if not invoice_data:
            QMessageBox.warning(parent, "Error", "Could not load invoice data")
            return None
        
        # Get invoice type and set appropriate template
        invoice_type = invoice_data['invoice'].get('tax_type', 'GST')
        generator.template_path = generator.get_template_path(invoice_type)
        
        # Prepare template data based on invoice type
        if invoice_type and invoice_type.upper() in ['NON-GST', 'NON GST', 'NONGST']:
            template_data = generator.prepare_non_gst_template_data(invoice_data)
        else:
            template_data = generator.prepare_template_data(invoice_data)
        
        html_content = generator.render_html_template(template_data, invoice_type)
        
        return html_content
            
    except Exception as e:
        QMessageBox.critical(parent, "HTML Generation Error", 
                           f"Failed to generate HTML: {str(e)}")
        return None


def show_html_preview_dialog(parent, html_content, invoice_id):
    """Show HTML preview directly in QWebEngineView"""
    try:
        from PyQt5.QtWebEngineWidgets import QWebEngineView
    except ImportError:
        QMessageBox.critical(parent, "Error", 
                           "PyQtWebEngine not installed.\n\nRun: pip3 install PyQtWebEngine")
        return
    
    try:
        # Get invoice number for title
        from ui.print.invoice_pdf_generator import InvoicePDFGenerator
        generator = InvoicePDFGenerator()
        invoice_data = generator.get_invoice_data(invoice_id)
        
        if not invoice_data:
            QMessageBox.warning(parent, "Error", "Could not load invoice data")
            return
        
        invoice_no = invoice_data['invoice']['invoice_no']
        
        # Create preview dialog
        preview_dialog = QDialog(parent)
        preview_dialog.setWindowTitle(f"📄 Invoice Preview - {invoice_no}")
        preview_dialog.setModal(True)
        preview_dialog.resize(900, 850)
        preview_dialog.setMinimumSize(800, 600)
        
        # Main layout
        layout = QVBoxLayout(preview_dialog)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Header bar with title and buttons
        header_frame = QFrame()
        header_frame.setFixedHeight(60)
        header_frame.setStyleSheet(f"""
            QFrame {{ 
                background: {PRIMARY}; 
                border-radius: 8px; 
            }}
        """)
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(15, 5, 15, 5)
        
        # Title
        title_label = QLabel(f"📄 Invoice: {invoice_no}")
        title_label.setStyleSheet(f"color: {WHITE}; font-size: 16px; font-weight: bold;")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Button style
        btn_style = f"""
            QPushButton {{
                background: {WHITE};
                color: {PRIMARY};
                border: none;
                border-radius: 6px;
                font-size: 13px;
                font-weight: bold;
                padding: 8px 15px;
                min-width: 100px;
            }}
            QPushButton:hover {{ background: #e0e7ff; }}
            QPushButton:pressed {{ background: #c7d2fe; }}
        """
        
        # Store references in dialog for callbacks
        preview_dialog.html_content = html_content
        preview_dialog.invoice_no = invoice_no
        
        # Save PDF button
        save_btn = QPushButton("💾 Save PDF")
        save_btn.setStyleSheet(btn_style)
        save_btn.clicked.connect(lambda: save_invoice_as_pdf(preview_dialog))
        header_layout.addWidget(save_btn)
        
        # Print button
        print_btn = QPushButton("🖨️ Print")
        print_btn.setStyleSheet(btn_style)
        print_btn.clicked.connect(lambda: print_invoice(preview_dialog))
        header_layout.addWidget(print_btn)
        
        # Open in Browser button
        browser_btn = QPushButton("🌐 Open in Browser")
        browser_btn.setStyleSheet(btn_style)
        browser_btn.clicked.connect(lambda: open_html_in_browser(html_content, invoice_no))
        header_layout.addWidget(browser_btn)
        
        # Close button
        close_btn = QPushButton("❌ Close")
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background: #ef4444;
                color: {WHITE};
                border: none;
                border-radius: 6px;
                font-size: 13px;
                font-weight: bold;
                padding: 8px 15px;
                min-width: 80px;
            }}
            QPushButton:hover {{ background: #dc2626; }}
            QPushButton:pressed {{ background: #b91c1c; }}
        """)
        close_btn.clicked.connect(preview_dialog.close)
        header_layout.addWidget(close_btn)
        
        layout.addWidget(header_frame)
        
        # HTML Viewer using QWebEngineView
        html_viewer = QWebEngineView()
        html_viewer.setStyleSheet(f"""
            QWebEngineView {{
                border: 1px solid {BORDER};
                border-radius: 8px;
                background: white;
            }}
        """)
        
        # Load HTML content
        html_viewer.setHtml(html_content)
        layout.addWidget(html_viewer)
        
        # Store viewer reference for printing
        preview_dialog.html_viewer = html_viewer
        
        # Show the dialog
        preview_dialog.exec_()
        
    except Exception as e:
        QMessageBox.critical(parent, "Preview Error", f"Failed to show preview: {str(e)}")


def open_html_in_browser(html_content, invoice_no):
    """Open HTML content in default browser"""
    try:
        # Save HTML to temp file
        temp_dir = tempfile.gettempdir()
        html_path = os.path.join(temp_dir, f"Invoice_{invoice_no}.html")
        
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        # Open in default browser
        webbrowser.open(f'file://{html_path}')
        
    except Exception as e:
        print(f"Error opening in browser: {str(e)}")


def save_invoice_as_pdf(preview_dialog):
    """Save invoice as PDF file"""
    try:
        from PyQt5.QtCore import QMarginsF, QSizeF
        from PyQt5.QtGui import QPageLayout, QPageSize
        
        invoice_no = preview_dialog.invoice_no
        
        # Ask user where to save
        file_path, _ = QFileDialog.getSaveFileName(
            preview_dialog,
            "Save Invoice as PDF",
            f"Invoice_{invoice_no}.pdf",
            "PDF Files (*.pdf)"
        )
        
        if not file_path:
            return
        
        # Get the web view
        html_viewer = preview_dialog.html_viewer
        
        # Create page layout for A4
        page_layout = QPageLayout(
            QPageSize(QPageSize.A4),
            QPageLayout.Portrait,
            QMarginsF(10, 10, 10, 10)
        )
        
        # Print to PDF
        html_viewer.page().printToPdf(file_path, page_layout)
        
        QMessageBox.information(preview_dialog, "Success", 
                               f"Invoice saved to:\n{file_path}")
        
    except Exception as e:
        QMessageBox.critical(preview_dialog, "Error", f"Failed to save PDF: {str(e)}")


def print_invoice(preview_dialog):
    """Print the invoice"""
    try:
        html_viewer = preview_dialog.html_viewer
        
        # Use browser's print dialog
        html_viewer.page().runJavaScript("window.print();")
        
    except Exception as e:
        QMessageBox.critical(preview_dialog, "Error", f"Failed to print: {str(e)}")
