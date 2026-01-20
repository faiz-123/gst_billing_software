# Unified Invoice Template Implementation

## Overview
Successfully merged GST and Non-GST invoice templates into a single unified template that handles both types with conditional rendering based on the `is_gst` flag.

## Changes Made

### 1. New Unified Template
**File**: `templates/invoice_unified.html`
- Single template for both GST and Non-GST invoices
- Uses Jinja2 `{% if is_gst %}...{% else %}...{% endif %}` syntax for conditional rendering
- Maintains all styling and layout for both invoice types
- A4 page format with proper dimensions and borders

### 2. GST Invoice Features (When `is_gst` = True)
- **Header**: "TAX INVOICE"
- **Items Table**: 17 columns including:
  - Sr, Description, HSN Code, MRP, Qty, Rate, Total Val
  - Discount %, Discount Amt, Taxable Amt
  - CGST %, CGST Amt, SGST %, SGST Amt, IGST %, IGST Amt, Total
- **GST Summary Section**: Breakdown by tax rate
- **Totals Section**: Sub-total, CGST/IGST, SGST, Total Tax, Total After Tax, Round Off
- **Fields**: Shows GSTIN, Tax Classification, Buyer GSTIN
- **Highlighted Columns**: Discount Amt and Taxable Amt (light blue background)

### 3. Non-GST Invoice Features (When `is_gst` = False)
- **Header**: "INVOICE"
- **Items Table**: Simplified 9 columns:
  - Sr, Description, HSN Code, Qty, Rate, Total Val
  - Discount %, Discount Amt, Amount
- **No Tax Fields**: All tax-related columns removed
- **No GST Summary**: Simplified bottom section
- **Fields**: No GSTIN or Buyer GSTIN displayed
- **Layout**: Cleaner, simpler table structure

### 4. Updated PDF Generator
**File**: `ui/print/invoice_pdf_generator.py`

**Changed Classes**:
```python
class InvoicePDFGenerator:
    def __init__(self):
        # Now uses unified template
        self.unified_template_path = os.path.join(project_root, 'templates', 'invoice_unified.html')
        self.template_path = self.unified_template_path
```

**Modified Methods**:

#### `prepare_template_data()` (GST)
- Added `'is_gst': True` flag
- Includes all GST-related fields:
  - `total_cgst`, `total_sgst`, `total_igst`
  - `gst_summary` list
  - `total_cgst_igst`, `total_tax_amount`, `total_after_tax`, `round_off`

#### `prepare_non_gst_template_data()` (Non-GST)
- Added `'is_gst': False` flag
- Includes only non-tax fields:
  - `subtotal_amount` instead of taxable totals
  - No tax-related calculations
  - `tax_type` set to 'NON-GST'

### 5. Template Data Structure

**Common Fields** (Both invoice types):
```python
{
    'is_gst': True/False,  # FLAG TO DIFFERENTIATE
    'company_name': str,
    'company_address': str,
    'company_contact': str,
    'company_gstin': str,
    'invoice_no': str,
    'invoice_date': str,
    'terms': str,
    'tax_type': 'GST' or 'NON-GST',
    'ref_no': str,
    'vehicle_no': str,
    'transport': str,
    'buyer_name': str,
    'buyer_address': str,
    'buyer_location': str,
    'buyer_contact': str,
    'buyer_gstin': str,  # Only for GST
    'items': list,
    'total_quantity': str,
    'total_discount': str,
    'net_amount': str,
    'amount_in_words': str,
    'bank_name': str,
    'bank_account': str,
    'bank_ifsc': str,
    'terms_conditions': str,
}
```

**GST-Specific Fields**:
```python
{
    'subtotal_taxable': str,
    'total_cgst': str,
    'total_sgst': str,
    'total_igst': str,
    'gst_summary': list,  # List of {rate, taxable_amt, sgst_amt, cgst_amt, tax_amt}
    'total_before_tax': str,
    'total_cgst_igst': str,
    'total_tax_amount': str,
    'total_after_tax': str,
    'round_off': str,
}
```

**Non-GST-Specific Fields**:
```python
{
    'subtotal_amount': str,
}
```

### 6. Item Data Structure

**GST Items**:
```python
{
    'description': str,
    'hsn_code': str,
    'mrp': str,
    'quantity': str,
    'rate': str,
    'total_val': str,
    'discount_percent': str,
    'discount_amt': str,
    'taxable_amt': str,
    'cgst_percent': str,
    'cgst_amt': str,
    'sgst_percent': str,
    'sgst_amt': str,
    'igst_percent': str,
    'igst_amt': str,
    'total': str,
}
```

**Non-GST Items**:
```python
{
    'description': str,
    'hsn_code': str,
    'quantity': str,
    'rate': str,
    'total_val': str,
    'discount_percent': str,
    'discount_amt': str,
    'total': str,
}
```

## Benefits

1. **Single Maintenance Point**: One template file to maintain instead of two
2. **Consistent Styling**: Both invoice types have identical layout and design
3. **Easy Updates**: Changes apply to both types automatically
4. **Clear Differentiation**: Template shows different content based on invoice type
5. **Flexible**: Easy to add more invoice types in the future with additional flags
6. **No Duplication**: Reduces code redundancy

## Backward Compatibility

- Old template files (`invoice.html`, `invoice_non_gst.html`) can be kept as backup
- PDF generator automatically switches to unified template
- No changes required in invoice dialog or preview screens
- All existing functionality preserved

## Future Enhancements

1. Add more invoice type flags (e.g., `'is_proforma'`, `'is_estimate'`)
2. Add optional sections (e.g., discount breakdown table)
3. Conditional bank details display
4. Customizable header templates per company

## Testing Checklist

- [ ] GST invoice preview displays correctly
- [ ] Non-GST invoice preview displays correctly
- [ ] GST invoice PDF export works
- [ ] Non-GST invoice PDF export works
- [ ] Printing from preview works for both types
- [ ] All calculations correct for both types
- [ ] Layout fills full A4 page for both types
- [ ] Border displays correctly for both types
