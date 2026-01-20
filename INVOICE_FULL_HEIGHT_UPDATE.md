# Invoice Full Height Layout Update

## Changes Made

### Files Modified
1. `templates/invoice.html`
2. `templates/invoice_non_gst.html`

### CSS Changes

#### 1. Invoice Container
**Changed from:** `min-height: 29.7cm;`
**Changed to:** `height: 29.7cm;` with flexbox layout
```css
.invoice-container {
    width: 21cm;
    height: 29.7cm;  /* Fixed height for full A4 page */
    display: flex;   /* Enable flexbox */
    flex-direction: column;  /* Stack items vertically */
}
```

**Benefits:**
- Invoice now uses the complete A4 page height (29.7cm)
- Content stretches to fill the entire page
- Footer stays at the bottom

#### 2. Items Section (the main content area)
**Changed from:** Static height
**Changed to:** Flexible height that grows
```css
.items-section {
    flex: 1;  /* Takes up all available space */
    overflow-y: auto;  /* Allows scrolling if needed */
    display: flex;
    flex-direction: column;
}
```

**Benefits:**
- Items table expands to fill available vertical space
- Automatically balances space between items and other sections
- Prevents content from being cramped

#### 3. Items Table Rows
**Changed from:** `padding: 3px 2px;` (invoice.html) / `padding: 4px 3px;` (non-gst)
**Changed to:** `padding: 5px 2px;` (invoice.html) / `padding: 5px 3px;` (non-gst)
**Added:** `height: auto;`

**Benefits:**
- More vertical padding makes items more readable
- Rows expand to fill available space
- Better visual balance on full-height pages

#### 4. Items Table
**Added:** `flex: 1;`
```css
.items-table {
    flex: 1;  /* Makes table grow with section */
}
```

**Benefits:**
- Table rows automatically space out evenly
- Full height utilization with proper spacing

## Result
- Invoice preview now displays on full A4 page height (29.7cm)
- Items are properly spaced throughout the page
- All content visible without unnecessary white space
- Print output maintains full page layout
- Professional appearance with content properly distributed

## Responsive Behavior
- **On screen:** Content fills the visible area with proper spacing
- **When printing:** Outputs full A4 page with all content properly positioned
- **With multiple items:** Rows expand evenly to fill available space
- **With few items:** Proper spacing prevents content from looking cramped

## Testing
To verify the changes:
1. Open invoice preview
2. Compare with screen - should use full height
3. Use Print preview - should show full A4 page
4. Try invoices with different numbers of items - spacing should adjust automatically
