"""
PHASE 2 INTEGRATION EXAMPLES

This file shows how to integrate Phase 2 error handling components
throughout the application.
"""

# ═══════════════════════════════════════════════════════════════════════════
# EXAMPLE 1: Using Error Handler in Controllers
# ═══════════════════════════════════════════════════════════════════════════

"""
from controllers.invoice_controller import InvoiceController
from core.error_handler import ErrorHandler
from core.exceptions import InvoiceException

controller = InvoiceController()

# Method 1: Using @handle_errors decorator
@handle_errors("Create Invoice")
def create_invoice(data):
    return controller._service.create_invoice(data)

# Method 2: Try-except with specific exceptions
def delete_invoice(invoice_id):
    try:
        return controller.delete_invoice(invoice_id)
    except InvoiceException as e:
        error_msg = e.to_user_message()
        # Display to user or return error
        return False, error_msg

# Method 3: Manual exception handling
def get_invoice_details(invoice_id):
    try:
        invoice = controller.get_invoice_with_items(invoice_id)
        if not invoice:
            raise InvoiceNotFound("Invoice not found")
        return invoice
    except InvoiceException as e:
        logger.error(f"Business error: {e.error_code}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        raise InvoiceException(f"Failed to fetch invoice: {str(e)}")
"""

# ═══════════════════════════════════════════════════════════════════════════
# EXAMPLE 2: Using Exception Validators in Forms
# ═══════════════════════════════════════════════════════════════════════════

"""
from core.exception_validators import ValidatorWithException
from ui.error_handler import UIErrorHandler, FormValidator

class PartyFormDialog:
    def validate_and_save(self):
        validator = FormValidator("Party Form")
        
        # Get form values
        party_name = self.party_name_input.text()
        gstin = self.gstin_input.text()
        pan = self.pan_input.text()
        mobile = self.mobile_input.text()
        email = self.email_input.text()
        
        # Validate required fields
        validator.validate_required("party_name", party_name, "Party Name")
        validator.validate_required("gstin", gstin, "GSTIN")
        
        # Validate formats using exception validators
        try:
            if gstin:
                ValidatorWithException.validate_gstin(gstin, raise_exception=True)
        except InvalidGSTIN as e:
            validator.add_error("gstin", e.to_user_message())
        
        try:
            if pan:
                ValidatorWithException.validate_pan(pan, raise_exception=True)
        except InvalidPAN as e:
            validator.add_error("pan", e.to_user_message())
        
        try:
            if mobile:
                ValidatorWithException.validate_mobile(mobile, raise_exception=True)
        except InvalidPhoneException as e:
            validator.add_error("mobile", e.to_user_message())
        
        try:
            if email:
                ValidatorWithException.validate_email(email, raise_exception=True)
        except InvalidEmailException as e:
            validator.add_error("email", e.to_user_message())
        
        # Show errors if any
        if validator.has_errors:
            validator.show_errors()
            return False
        
        # Save the party
        return self.save_party()
"""

# ═══════════════════════════════════════════════════════════════════════════
# EXAMPLE 3: Using Error Dialog in UI Operations
# ═══════════════════════════════════════════════════════════════════════════

"""
from ui.error_handler import UIErrorHandler, handle_ui_errors

class InvoiceListScreen:
    
    @handle_ui_errors("Delete Invoice")
    def on_delete_button_clicked(self):
        # Get selected invoice
        selected_invoice = self.get_selected_invoice()
        if not selected_invoice:
            UIErrorHandler.show_warning("No Selection", "Please select an invoice to delete")
            return
        
        # Ask for confirmation
        if not UIErrorHandler.ask_confirmation(
            "Confirm Delete",
            f"Are you sure you want to delete invoice {selected_invoice['invoice_no']}?"
        ):
            return
        
        # Delete the invoice
        success, message = self.controller.delete_invoice(selected_invoice['id'])
        
        if success:
            UIErrorHandler.show_success("Success", message)
            self.refresh_invoice_list()
        else:
            UIErrorHandler.show_error("Delete Failed", message)
"""

# ═══════════════════════════════════════════════════════════════════════════
# EXAMPLE 4: Using Transaction Manager for Multi-Step Operations
# ═══════════════════════════════════════════════════════════════════════════

"""
from core.error_handler import TransactionManager
from core.exceptions import InvoiceException

class InvoiceController:
    def create_invoice_with_items(self, invoice_data, items_data):
        # Use transaction manager for multi-step operation
        with TransactionManager(self.db) as txn:
            try:
                # Create invoice
                invoice_id = self.db.create_invoice(invoice_data)
                
                # Create invoice items
                for item in items_data:
                    item['invoice_id'] = invoice_id
                    self.db.create_invoice_item(item)
                
                # Update party balance
                party_id = invoice_data['party_id']
                amount = invoice_data['amount']
                self.db.update_party_balance(party_id, amount)
                
                # All successful, commit automatically
                return invoice_id
                
            except InvoiceException as e:
                # Rollback happens automatically on exception
                logger.error(f"Invoice creation failed: {e.error_code}")
                raise
"""

# ═══════════════════════════════════════════════════════════════════════════
# EXAMPLE 5: Exception Hierarchy Usage
# ═══════════════════════════════════════════════════════════════════════════

"""
from core.exceptions import (
    BillingException, InvoiceException, InvoiceAlreadyExistsException,
    PaymentException, InvalidPaymentAmount, PartyException,
    ProductException, InsufficientStock
)

try:
    # Try to create invoice
    invoice = create_invoice(data)
except InvoiceAlreadyExistsException as e:
    # Handle duplicate invoice
    logger.error(f"Duplicate invoice: {e.error_code}")
    show_error("Duplicate Invoice", e.to_user_message())
except InvoiceException as e:
    # Handle any invoice error
    logger.error(f"Invoice error: {e.error_code}")
    show_error("Invoice Error", e.to_user_message())
except PaymentException as e:
    # Handle payment errors
    logger.error(f"Payment error: {e.error_code}")
except PartyException as e:
    # Handle party errors
    logger.error(f"Party error: {e.error_code}")
except ProductException as e:
    # Handle product errors
    logger.error(f"Product error: {e.error_code}")
    if isinstance(e, InsufficientStock):
        show_warning("Stock Alert", e.to_user_message())
except BillingException as e:
    # Handle any billing error
    logger.error(f"Billing error: {e.error_code}")
    show_error("Error", e.to_user_message())
except Exception as e:
    # Handle unexpected errors
    logger.error(f"Unexpected error: {str(e)}", exc_info=True)
    show_error("Error", "An unexpected error occurred. Please try again.")
"""

# ═══════════════════════════════════════════════════════════════════════════
# EXAMPLE 6: Complete Form Integration
# ═══════════════════════════════════════════════════════════════════════════

"""
from core.exception_validators import validate_gstin_field, validate_email_field
from ui.error_handler import UIErrorHandler

class ProductFormDialog:
    def on_gstin_field_changed(self):
        gstin_text = self.gstin_input.text()
        if gstin_text:  # Only validate if user entered something
            is_valid, error_msg = validate_gstin_field(gstin_text)
            
            if not is_valid:
                # Show error in red
                self.gstin_error_label.setText(error_msg)
                self.gstin_error_label.setStyleSheet("color: red;")
            else:
                # Clear error
                self.gstin_error_label.setText("")
    
    def on_email_field_changed(self):
        email_text = self.email_input.text()
        if email_text:
            is_valid, error_msg = validate_email_field(email_text)
            
            if not is_valid:
                self.email_error_label.setText(error_msg)
                self.email_error_label.setStyleSheet("color: red;")
            else:
                self.email_error_label.setText("")
    
    def on_save_clicked(self):
        # Validate all fields
        validator = FormValidator("Product Form")
        
        # ... validation code ...
        
        if validator.has_errors:
            validator.show_errors()
            return
        
        # Try to save
        try:
            product_id = self.save_product()
            UIErrorHandler.show_success("Success", f"Product saved successfully!")
            self.close()
        except Exception as e:
            UIErrorHandler.handle_form_error(e, "Save Product")
"""

# ═══════════════════════════════════════════════════════════════════════════
# EXAMPLE 7: Service Layer Exception Raising
# ═══════════════════════════════════════════════════════════════════════════

"""
from core.exceptions import (
    InvoiceAlreadyExistsException, PaymentException,
    InvalidPaymentAmount, PartyException
)

class InvoiceService:
    def create_invoice(self, invoice_data):
        # Check for duplicate
        existing = self.db.get_invoice_by_number(invoice_data['invoice_no'])
        if existing:
            raise InvoiceAlreadyExistsException(invoice_data['invoice_no'])
        
        # Create the invoice
        return self.db.create_invoice(invoice_data)

class PaymentService:
    def create_payment(self, payment_data):
        # Validate amount
        amount = payment_data['amount']
        if amount <= 0:
            raise InvalidPaymentAmount(amount, 0)
        
        # Check invoice amount
        invoice = self.db.get_invoice_by_id(payment_data['invoice_id'])
        if amount > invoice['total']:
            raise InvalidPaymentAmount(
                amount=amount,
                min_amount=invoice['total']
            )
        
        # Create the payment
        return self.db.create_payment(payment_data)

class PartyService:
    def create_party(self, party_data):
        # Check for duplicate GSTIN
        if party_data.get('gstin'):
            existing = self.db.get_party_by_gstin(party_data['gstin'])
            if existing:
                raise PartyAlreadyExists(f"GSTIN: {party_data['gstin']}")
        
        # Create the party
        return self.db.create_party(party_data)
"""

# ═══════════════════════════════════════════════════════════════════════════
# INTEGRATION CHECKLIST
# ═══════════════════════════════════════════════════════════════════════════

"""
Phase 2 Integration Checklist:

CONTROLLERS:
  ✅ Added @handle_errors decorator to delete methods
  ✅ Added exception imports
  ✅ Added specific exception catching
  ✅ Updated error handling to return proper tuples

SERVICES:
  ✅ Added exception imports
  ✅ Added exception raising on validation failures
  ✅ Added logging for service operations
  ⏳ Add more specific exception raising throughout

FORMS:
  ⏳ Import UIErrorHandler and FormValidator
  ⏳ Add field validation with format checking
  ⏳ Show validation errors in real-time
  ⏳ Ask confirmation before delete/save

UI SCREENS:
  ⏳ Import UIErrorHandler and handle_ui_errors
  ⏳ Handle exceptions from controller calls
  ⏳ Show error dialogs on failures
  ⏳ Show confirmation dialogs for destructive actions
  ⏳ Show success messages after operations

TESTING:
  ✅ Test suite created (test_error_handling.py)
  ⏳ Run tests to verify functionality
  ⏳ Test each exception type
  ⏳ Test error dialogs
  ⏳ Test form validation

DOCUMENTATION:
  ✅ Code docstrings added
  ✅ Usage examples documented
  ✅ Integration examples provided
  ✅ Exception hierarchy documented
"""
