#!/usr/bin/env python3
"""Test bill-to-bill invoice selection in receipt dialog."""

import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt, QTimer

def test_bill_to_bill():
    app = QApplication(sys.argv)
    
    from ui.receipts.receipt_form_dialog import ReceiptDialog
    
    print("\n" + "="*70)
    print("RECEIPT DIALOG - BILL-TO-BILL INVOICE SELECTION TEST")
    print("="*70 + "\n")
    
    # Create dialog
    dialog = ReceiptDialog()
    
    print("TEST 1: Dialog Initialization")
    print("-" * 70)
    assert hasattr(dialog, 'parties'), "parties not loaded"
    assert hasattr(dialog, 'invoices'), "invoices not loaded"
    print(f"✓ Loaded {len(dialog.parties)} parties")
    print(f"✓ Loaded {len(dialog.invoices)} invoices")
    
    # Find a party with outstanding invoices
    print("\nTEST 2: Finding Party with Outstanding Invoices")
    print("-" * 70)
    
    party_with_invoices = None
    for party in dialog.parties:
        party_id = party.get('id')
        invoices = [inv for inv in dialog.invoices 
                   if inv.get('party_id') == party_id 
                   and inv.get('due_amount', inv.get('grand_total', 0)) > 0]
        if invoices:
            party_with_invoices = party
            print(f"✓ Found party: {party.get('name')}")
            print(f"✓ Has {len(invoices)} outstanding invoices")
            break
    
    if not party_with_invoices:
        print("✗ No party with outstanding invoices found")
        dialog.close()
        return 1
    
    # Select party
    print("\nTEST 3: Selecting Party")
    print("-" * 70)
    party_name = party_with_invoices.get('name')
    dialog.party_search.lineEdit().setText(party_name)
    app.processEvents()
    print(f"✓ Set party to: {party_name}")
    
    # Trigger party selection
    dialog._on_party_text_edited(party_name)
    app.processEvents()
    print("✓ Party selection triggered")
    
    # Switch to bill-to-bill mode
    print("\nTEST 4: Switching to Bill-to-Bill Mode")
    print("-" * 70)
    try:
        dialog.btn_bill_to_bill.click()
        app.processEvents()
        print("✓ Bill-to-bill mode activated")
    except Exception as e:
        print(f"✗ Error switching to bill-to-bill: {e}")
        dialog.close()
        return 1
    
    # Check if invoice cards are created
    print("\nTEST 5: Invoice Cards Display")
    print("-" * 70)
    if hasattr(dialog, 'invoice_cards'):
        card_count = len(dialog.invoice_cards)
        if card_count > 0:
            print(f"✓ Created {card_count} invoice cards")
        else:
            print("✗ No invoice cards created")
            dialog.close()
            return 1
    else:
        print("✗ invoice_cards attribute not found")
        dialog.close()
        return 1
    
    # Test clicking first invoice
    print("\nTEST 6: Simulating Invoice Selection Click")
    print("-" * 70)
    try:
        if dialog.invoice_cards:
            first_card = dialog.invoice_cards[0]
            print(f"✓ First invoice card found")
            
            # Get invoice data from card
            invoice = first_card.property("invoice")
            if invoice:
                inv_no = invoice.get('invoice_no', 'N/A')
                due = invoice.get('due_amount', invoice.get('grand_total', 0))
                print(f"✓ Invoice: {inv_no}, Due: ₹{due:,.2f}")
                
                # Simulate click
                from PySide6.QtGui import QMouseEvent
                from PySide6.QtCore import QPoint
                mouse_event = QMouseEvent(QMouseEvent.MouseButtonPress, QPoint(100, 18), 
                                         Qt.LeftButton, Qt.LeftButton, Qt.NoModifier)
                first_card.mousePressEvent(mouse_event)
                app.processEvents()
                
                # Check if selection was stored
                if hasattr(dialog, 'selected_invoice') and dialog.selected_invoice:
                    selected_no = dialog.selected_invoice.get('invoice_no', 'N/A')
                    print(f"✓ Selected invoice stored: {selected_no}")
                else:
                    print("✗ selected_invoice not stored after click")
            else:
                print("✗ Could not get invoice data from card")
    except Exception as e:
        print(f"✗ Error during invoice selection: {e}")
        import traceback
        traceback.print_exc()
        dialog.close()
        return 1
    
    print("\n" + "="*70)
    print("RESULT: Bill-to-Bill Invoice Selection Test Complete")
    print("="*70 + "\n")
    
    dialog.close()
    return 0

if __name__ == "__main__":
    sys.exit(test_bill_to_bill())
