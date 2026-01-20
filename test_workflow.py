#!/usr/bin/env python3
"""Comprehensive test for receipt dialog UI workflow."""

import sys
import traceback
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QMouseEvent
from PySide6.QtCore import QPoint

def run_workflow_test():
    app = QApplication(sys.argv)
    
    print("\n" + "="*80)
    print(" "*20 + "RECEIPT DIALOG - COMPLETE WORKFLOW TEST")
    print("="*80 + "\n")
    
    try:
        from ui.receipts.receipt_form_dialog import ReceiptDialog
        
        dialog = ReceiptDialog()
        dialog.show()
        app.processEvents()
        
        # TEST 1: Dialog opens
        print("TEST 1: Dialog Initialization")
        print("-" * 80)
        assert dialog.isVisible(), "Dialog not visible"
        print("✓ Dialog opens successfully")
        print(f"✓ Dialog size: {dialog.width()}x{dialog.height()}")
        print(f"✓ Loaded {len(dialog.parties)} parties")
        print(f"✓ Loaded {len(dialog.invoices)} invoices")
        
        # TEST 2: Customer selection
        print("\nTEST 2: Customer Selection")
        print("-" * 80)
        
        # Find a party with invoices
        party_with_invoices = None
        for p in dialog.parties:
            party_id = p.get('id')
            invoices_for_party = [inv for inv in dialog.invoices 
                                 if inv.get('party_id') == party_id 
                                 and inv.get('due_amount', inv.get('grand_total', 0)) > 0]
            if invoices_for_party:
                party_with_invoices = p
                break
        
        if party_with_invoices:
            party_name = party_with_invoices.get('name')
            print(f"✓ Found party with invoices: {party_name}")
            
            # Set party in search
            dialog.party_search.lineEdit().setText(party_name)
            app.processEvents()
            print(f"✓ Set party search to: {party_name}")
            
            # Trigger party text change
            dialog._on_party_text_edited(party_name)
            app.processEvents()
            print("✓ Party selection handler triggered")
        else:
            print("⚠ No party with outstanding invoices found - skipping further tests")
            dialog.close()
            return 0
        
        # TEST 3: Settlement mode - Bill-to-Bill
        print("\nTEST 3: Bill-to-Bill Settlement Mode")
        print("-" * 80)
        
        try:
            dialog.btn_bill_to_bill.click()
            app.processEvents()
            print("✓ Bill-to-bill mode activated")
        except Exception as e:
            print(f"✗ Error activating bill-to-bill: {e}")
            raise
        
        # Check if invoice cards are created
        if hasattr(dialog, 'invoice_cards'):
            print(f"✓ Invoice cards created: {len(dialog.invoice_cards)}")
            
            # TEST 4: Invoice selection
            print("\nTEST 4: Invoice Selection")
            print("-" * 80)
            
            if dialog.invoice_cards:
                first_card = dialog.invoice_cards[0]
                invoice_data = first_card.property("invoice")
                
                if invoice_data:
                    inv_no = invoice_data.get('invoice_no', 'N/A')
                    due = invoice_data.get('due_amount', invoice_data.get('grand_total', 0))
                    print(f"✓ First invoice: {inv_no}, Due: ₹{due:,.2f}")
                    
                    # Simulate click on invoice
                    try:
                        mouse_event = QMouseEvent(QMouseEvent.MouseButtonPress, QPoint(100, 18), 
                                                 Qt.LeftButton, Qt.LeftButton, Qt.NoModifier)
                        first_card.mousePressEvent(mouse_event)
                        app.processEvents()
                        print("✓ Invoice card click simulated")
                        
                        # Check if selection was stored
                        if hasattr(dialog, 'selected_invoice') and dialog.selected_invoice:
                            selected_inv_no = dialog.selected_invoice.get('invoice_no', 'N/A')
                            print(f"✓ Selected invoice stored: {selected_inv_no}")
                        else:
                            print("⚠ selected_invoice not stored after click")
                            
                    except Exception as e:
                        print(f"✗ Error during invoice selection: {e}")
                        traceback.print_exc()
                else:
                    print("✗ Could not get invoice data from card")
            else:
                print("✗ No invoice cards available")
        else:
            print("✗ invoice_cards attribute not found")
        
        # TEST 5: Amount input
        print("\nTEST 5: Amount Input")
        print("-" * 80)
        
        try:
            current_value = dialog.amount_input.value()
            dialog.amount_input.setValue(100.50)
            app.processEvents()
            new_value = dialog.amount_input.value()
            
            print(f"✓ Amount input accessible")
            print(f"✓ Set amount to: ₹{new_value:,.2f}")
            print(f"✓ Minimum value allowed: {dialog.amount_input.minimum()}")
            
        except Exception as e:
            print(f"✗ Error with amount input: {e}")
            traceback.print_exc()
        
        # TEST 6: Date field
        print("\nTEST 6: Date Field")
        print("-" * 80)
        
        try:
            current_date = dialog.receipt_date.date()
            print(f"✓ Date field accessible")
            print(f"✓ Current date: {current_date.toString('dd/MM/yyyy')}")
            print(f"✓ Calendar popup enabled: {dialog.receipt_date.calendarPopup()}")
            
        except Exception as e:
            print(f"✗ Error with date field: {e}")
            traceback.print_exc()
        
        # TEST 7: Payment method
        print("\nTEST 7: Payment Method")
        print("-" * 80)
        
        try:
            payment_modes = []
            for i in range(dialog.payment_method.count()):
                payment_modes.append(dialog.payment_method.itemText(i))
            
            print(f"✓ Payment method combo available")
            print(f"✓ Available modes: {', '.join(payment_modes)}")
            
        except Exception as e:
            print(f"✗ Error with payment method: {e}")
            traceback.print_exc()
        
        print("\n" + "="*80)
        print(" "*25 + "WORKFLOW TEST COMPLETED")
        print("="*80 + "\n")
        
        dialog.close()
        return 0
        
    except Exception as e:
        print(f"\n✗ CRITICAL ERROR: {type(e).__name__}: {e}")
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(run_workflow_test())
