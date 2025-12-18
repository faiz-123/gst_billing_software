# Assets Directory Structure

This directory contains all static assets used by the GST Billing Software application.

## Directory Structure

```
assets/
├── icons/          # UI icons (buttons, actions, etc.)
├── images/         # General images and graphics
├── logos/          # Company logos and branding
└── fonts/          # Custom fonts (if any)
```

## Current Assets

### Icons (`icons/`)
- `eye.png` - Show password icon
- `eye-off.png` - Hide password icon  
- `eye.svg` - Show password icon (vector)
- `eye-off.svg` - Hide password icon (vector)
- `down-arrow.png` - Dropdown arrow icon
- `setting.png` - Settings icon

### Images (`images/`)
- *Currently empty - add general application images here*

### Logos (`logos/`)
- *Currently empty - add company logos here*

### Fonts (`fonts/`)
- *Currently empty - add custom fonts here*

## Usage in Code

When referencing assets in code, use relative paths from the project root:

```python
# Correct way to reference icons
icon = QtGui.QIcon("assets/icons/eye.png")

# Correct way to reference images  
pixmap = QPixmap("assets/images/logo.png")
```

## Adding New Assets

1. **Icons**: Place in `assets/icons/` - use for UI elements
2. **Images**: Place in `assets/images/` - use for graphics and photos
3. **Logos**: Place in `assets/logos/` - use for company branding
4. **Fonts**: Place in `assets/fonts/` - use for custom typography

## Best Practices

- Use PNG for icons with transparency
- Use SVG for scalable vector icons
- Use JPG for photos/complex images
- Keep file names descriptive and lowercase
- Use hyphens for multi-word names (e.g., `eye-off.png`)
