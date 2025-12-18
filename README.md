# GST Billing Software

A comprehensive PyQt5-based GST billing and inventory management application with a modern, professional interface.

## Features

### 📊 Dashboard
- Real-time sales metrics and KPIs
- Recent invoices and payments overview
- Quick action buttons for common tasks
- Company and financial year management

### 👥 Parties Management
- Add and manage customers and suppliers
- GST registration details and PAN information
- Opening balance tracking
- Advanced search and filtering
- Export functionality

### 📦 Products & Services
- Comprehensive inventory management
- Product categorization and branding
- Tax rate and HSN/SAC code management
- Stock tracking with low-stock alerts
- Support for both goods and services
- Pricing with MRP, purchase, and selling prices

### 🧾 Invoicing
- Professional invoice creation
- Multi-item invoices with automatic calculations
- Tax calculations (GST/CGST/SGST)
- Discount management
- Due date tracking
- Invoice status management (Draft, Sent, Paid, Overdue)

### 💰 Payments
- Record payments received and made
- Multiple payment methods support
- Invoice linking for payment tracking
- Outstanding amount calculations
- Payment history and reporting

## Technical Features

### 🎨 Modern UI/UX
- Clean, professional interface design
- Consistent color scheme and typography
- Responsive layouts
- Custom widgets and components
- Icon-based navigation

### 🏗️ Architecture
- Modular design with separation of concerns
- Base classes for consistent screen structure
- Centralized theme and styling
- SQLite database for data persistence
- JSON configuration management

### 🔧 Database
- SQLite database with proper schema
- CRUD operations for all entities
- Data integrity and relationships
- Automatic database initialization

## Installation

### Prerequisites
- Python 3.7 or higher
- PyQt5

### Setup Instructions

1. **Clone or download the project**
   ```bash
   cd /path/to/gst_billing_software
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python run.py
   ```

   Or directly:
   ```bash
   python main.py
   ```

## Project Structure

```
gst_billing_software/
├── screens/                 # Application screens
│   ├── __init__.py
│   ├── dashboard.py        # Main dashboard
│   ├── parties.py          # Customer/supplier management
│   ├── products.py         # Product/service management
│   ├── invoices.py         # Invoice creation and management
│   └── payments.py         # Payment recording and tracking
├── assets/                 # Static assets (icons, images)
├── data/                   # Database and data files
│   └── config.json        # Application configuration
├── theme.py               # UI theme and styling
├── widgets.py             # Custom UI components
├── database.py            # Database operations
├── config.py              # Configuration management
├── base_screen.py         # Base screen class
├── main.py                # Main application window
├── run.py                 # Application launcher
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## Usage

### First Run
1. On first launch, the application will create a SQLite database
2. Configure your company information in settings
3. Start by adding parties (customers/suppliers)
4. Add your products and services
5. Create invoices and record payments

### Navigation
- Use the sidebar to navigate between different modules
- Dashboard provides an overview of your business
- Each module has search, filter, and export capabilities
- Quick action buttons for common operations

### Data Management
- All data is stored locally in SQLite database
- Configuration settings are saved in JSON format
- Regular backups recommended for important data

## Customization

### Themes
Edit `theme.py` to customize colors, fonts, and styling:
- Color constants for consistent theming
- Font definitions for typography
- Stylesheet templates for widgets

### Database Schema
The database schema is automatically created with tables for:
- Companies
- Parties (customers/suppliers)
- Products/services
- Invoices and invoice items
- Payments

### Adding New Features
1. Create new screen in `screens/` directory
2. Inherit from `BaseScreen` class
3. Add navigation in `main.py`
4. Update database schema if needed

## Development

### Code Structure
- **MVC Pattern**: Separation of UI, business logic, and data
- **Base Classes**: Consistent structure across screens
- **Custom Widgets**: Reusable UI components
- **Theme System**: Centralized styling

### Key Classes
- `BaseScreen`: Common functionality for all screens
- `CustomButton`, `CustomTable`, `CustomInput`: Styled widgets
- `Database`: SQLite operations wrapper
- `Config`: Configuration management

### Database Operations
All database operations are handled through the `db` instance:
```python
from database import db

# Add new party
party_data = {'name': 'ABC Corp', 'type': 'Customer'}
db.add_party(party_data)

# Get all products
products = db.get_products()
```

## Contributing

1. Follow the existing code structure and patterns
2. Use the base classes for new screens
3. Maintain consistent styling using the theme system
4. Add proper error handling and validation
5. Test thoroughly with sample data

## License

This project is developed for educational and business use. Feel free to modify and extend according to your needs.

## Support

For issues, feature requests, or questions:
1. Check the code comments and documentation
2. Review the database schema in `database.py`
3. Examine existing screens for implementation patterns

## Roadmap

Future enhancements could include:
- [ ] PDF generation for invoices
- [ ] Advanced reporting and analytics
- [ ] Backup and restore functionality
- [ ] Multi-company support
- [ ] API integration for accounting software
- [ ] Email integration for invoice sending
- [ ] Barcode scanning support
- [ ] Advanced inventory management
- [ ] Role-based access control
- [ ] Cloud synchronization

---

**Note**: This application is designed for Indian GST compliance but can be adapted for other tax systems by modifying the tax calculation logic and field labels.
