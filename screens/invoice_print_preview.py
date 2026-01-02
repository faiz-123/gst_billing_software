""" 
Invoice Print Preview Dialog
Shows PDF preview with exactly 3 buttons: Print, Download PDF, Cancel
Professional, read-only interface for invoice printing
"""

import os
import shutil
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QScrollArea, QFrame, QFileDialog, QMessageBox, QSplitter, QWidget
)
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QPixmap, QFont

from theme import PRIMARY, SUCCESS, TEXT_SECONDARY, WHITE, BORDER, BACKGROUND

# Check for QWebEngineWidgets availability at module level
WEB_ENGINE_AVAILABLE = False
QWebEngineView = None

try:
    from PyQt5.QtWebEngineWidgets import QWebEngineView
    WEB_ENGINE_AVAILABLE = True
except ImportError:
    # Create a dummy class to prevent errors
    class QWebEngineView:
        pass


class InvoicePrintPreview(QDialog):
    """Professional print preview dialog with embedded PDF viewer and 3 action buttons"""
    
    def __init__(self, pdf_path, parent=None):
        super().__init__(parent)
        self.pdf_path = pdf_path
        self.setWindowTitle("Invoice Print Preview")
        self.setup_ui(parent)
        self.load_pdf()

    def setup_ui(self, parent):
        """Setup the user interface"""
        # Set dialog properties
        self.setModal(True)
        self.resize(900, 700)
        self.setMinimumSize(800, 600)
        

        try:
            if parent is not None:
                container = getattr(parent, 'content_frame', parent)
                pw = container.width() or container.size().width()
                ph = container.height() or container.size().height()
                target_w = max(600, int(pw * 0.9))
                target_h = max(480, int(ph * 0.9))
                self.resize(target_w, target_h)
                try:
                    top = parent.window() if hasattr(parent, 'window') else parent
                    px = top.x(); py = top.y(); pw_total = top.width(); ph_total = top.height()
                    dx = px + max(0, (pw_total - self.width()) // 2)
                    dy = py + max(0, (ph_total - self.height()) // 2)
                    self.move(dx, dy)
                except Exception:
                    pass
        except Exception:
            pass

        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Header section
        header = self.create_header()
        layout.addWidget(header)
        
        # PDF viewer section
        viewer = self.create_pdf_viewer()
        layout.addWidget(viewer, 1)  # Give it stretch factor
        
        # Action buttons section
        buttons = self.create_action_buttons()
        layout.addWidget(buttons)
        
        self.apply_styling()
    
    def create_header(self):
        """Create the header section"""
        header_frame = QFrame()
        header_frame.setFixedHeight(60)
        header_frame.setStyleSheet(f"""
            QFrame {{
                background: {WHITE};
                border-bottom: 2px solid {BORDER};
            }}
        """)
        
        layout = QHBoxLayout(header_frame)
        layout.setContentsMargins(20, 10, 20, 10)
        
        # Title and subtitle
        title_layout = QVBoxLayout()
        
        title = QLabel("📄 Invoice Print Preview")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setStyleSheet(f"color: {PRIMARY}; margin: 0; padding: 0;")
        
        subtitle = QLabel("Review your invoice before printing or downloading")
        subtitle.setFont(QFont("Arial", 11))
        subtitle.setStyleSheet(f"color: {TEXT_SECONDARY}; margin: 0; padding: 0;")
        
        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)
        title_layout.setSpacing(2)
        
        layout.addLayout(title_layout)
        layout.addStretch()
        
        return header_frame
    
    def create_pdf_viewer(self):
        """Create the PDF viewer section - single instance only"""
        viewer_frame = QFrame()
        viewer_frame.setObjectName("main_viewer_frame")  # Set identifier
        viewer_frame.setStyleSheet(f"""
            QFrame {{
                background: {BACKGROUND};
                border: none;
            }}
        """)
        
        self.viewer_layout = QVBoxLayout(viewer_frame)
        self.viewer_layout.setContentsMargins(10, 10, 10, 10)
        
        # Initialize viewer state
        self.pdf_viewer_created = False

        if WEB_ENGINE_AVAILABLE and QWebEngineView:
            try:
                # Try to use QWebEngineView for PDF display
                self.web_view = QWebEngineView()
                self.web_view.setStyleSheet(f"""
                    QWebEngineView {{
                        border: 2px solid {BORDER};
                        border-radius: 8px;
                        background: {WHITE};
                    }}
                """)
                
                self.viewer_layout.addWidget(self.web_view)
                self.pdf_viewer_created = True
                
            except Exception as e:
                print(f"Failed to create QWebEngineView: {e}")
                self.web_view = None
        else:
            # Mark that we'll use fallback viewer
            self.web_view = None
        
        return viewer_frame

    def create_action_buttons(self):
        """Create the action buttons section with exactly 3 buttons"""
        buttons_frame = QFrame()
        buttons_frame.setFixedHeight(80)
        buttons_frame.setStyleSheet(f"""
            QFrame {{
                background: {WHITE};
                border-top: 2px solid {BORDER};
            }}
        """)
        
        layout = QHBoxLayout(buttons_frame)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(15)
        
        # Left side - instruction text
        instruction = QLabel("Choose an action:")
        instruction.setFont(QFont("Arial", 11))
        instruction.setStyleSheet(f"color: {TEXT_SECONDARY};")
        
        layout.addWidget(instruction)
        layout.addStretch()
        
        # Right side - action buttons
        # 1. Print button (primary action)
        self.print_btn = self.create_action_button(
            "🖨️ Print", 
            PRIMARY, 
            self.print_pdf,
            "Send invoice to system printer"
        )
        layout.addWidget(self.print_btn)
        
        # 2. Download PDF button (secondary action)
        self.download_btn = self.create_action_button(
            "💾 Download PDF", 
            SUCCESS, 
            self.download_pdf,
            "Save PDF to your computer"
        )
        layout.addWidget(self.download_btn)
        
        # 3. Cancel button (neutral action)
        self.cancel_btn = self.create_action_button(
            "❌ Cancel", 
            TEXT_SECONDARY, 
            self.reject,
            "Close preview without action"
        )
        layout.addWidget(self.cancel_btn)
        
        return buttons_frame
    
    def create_action_button(self, text, color, callback, tooltip):
        """Create a styled action button"""
        button = QPushButton(text)
        button.setFixedHeight(45)
        button.setMinimumWidth(130)
        button.setToolTip(tooltip)
        button.setCursor(Qt.PointingHandCursor)
        button.setFont(QFont("Arial", 11, QFont.Bold))
        
        # Color variations for hover and press states
        hover_color = self.get_hover_color(color)
        pressed_color = self.get_pressed_color(color)
        
        button.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {color}, stop:1 {hover_color});
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {hover_color}, stop:1 {pressed_color});
            }}
            QPushButton:pressed {{
                background: {pressed_color};
            }}
            QPushButton:disabled {{
                background: #9CA3AF;
                color: #6B7280;
            }}
        """)
        
        button.clicked.connect(callback)
        return button
    
    def get_hover_color(self, base_color):
        """Get hover color for a base color"""
        color_map = {
            PRIMARY: "#1E40AF",
            SUCCESS: "#059669", 
            TEXT_SECONDARY: "#4B5563"
        }
        return color_map.get(base_color, "#4B5563")
    
    def get_pressed_color(self, base_color):
        """Get pressed color for a base color"""
        color_map = {
            PRIMARY: "#1D4ED8",
            SUCCESS: "#047857",
            TEXT_SECONDARY: "#374151"
        }
        return color_map.get(base_color, "#374151")
    
    def load_pdf(self):
        """Load and display the PDF/HTML with enhanced preview capabilities"""
        if not self.pdf_path or not os.path.exists(self.pdf_path):
            QMessageBox.warning(self, "File Error", "Invoice file not found!")
            return
        
        print(f"🔍 Loading invoice for preview: {self.pdf_path}")
        
        # Update window title
        filename = os.path.basename(self.pdf_path)
        self.setWindowTitle(f"Invoice Preview - {filename}")
        
        # Check if it's an HTML file (our current PDF generator outputs HTML)
        if self.pdf_path.lower().endswith('.html'):
            print("ℹ️ Loading HTML invoice file")
            self._load_html_preview()
        else:
            print("ℹ️ Loading PDF file")
            self._load_pdf_preview()
    
    def _load_html_preview(self):
        """Load HTML file in web view for preview"""
        if not self.pdf_viewer_created:
            print("ℹ️ Creating HTML preview viewer")
            self._create_html_viewer()
            self.pdf_viewer_created = True
    
    def _create_html_viewer(self):
        """Create HTML viewer using QWebEngineView"""
        try:
            # Clear any existing content first
            self._clear_viewer_layout()
            
            if WEB_ENGINE_AVAILABLE and QWebEngineView:
                # Use QWebEngineView for HTML display
                self.web_view = QWebEngineView()
                self.web_view.setStyleSheet(f"""
                    QWebEngineView {{
                        border: 2px solid {BORDER};
                        border-radius: 8px;
                        background: {WHITE};
                    }}
                """)
                
                # Load HTML file
                file_url = QUrl.fromLocalFile(os.path.abspath(self.pdf_path))
                self.web_view.load(file_url)
                
                self.viewer_layout.addWidget(self.web_view)
                print("✅ HTML loaded in QWebEngineView")
            else:
                # Fallback: Try to load HTML content directly
                print("⚠️ QWebEngineView not available, trying direct HTML display")
                self._create_direct_html_viewer()
                
        except Exception as e:
            print(f"❌ HTML viewer creation failed: {e}")
            self._create_direct_html_viewer()
    
    def _create_direct_html_viewer(self):
        """Direct HTML viewer using QLabel with HTML content"""
        try:
            # Read HTML content
            with open(self.pdf_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # Create scrollable area for HTML content
            scroll_area = QScrollArea()
            scroll_area.setWidgetResizable(True)
            scroll_area.setStyleSheet(f"""
                QScrollArea {{
                    border: 2px solid {BORDER};
                    border-radius: 8px;
                    background: {WHITE};
                }}
            """)
            
            # Create label to display HTML
            html_label = QLabel()
            html_label.setWordWrap(True)
            html_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
            html_label.setStyleSheet(f"""
                QLabel {{
                    background: {WHITE};
                    padding: 20px;
                    font-family: Arial, sans-serif;
                    font-size: 10px;
                    line-height: 1.2;
                }}
            """)
            
            # Process HTML content to make it suitable for QLabel
            processed_html = self._process_html_for_display(html_content)
            html_label.setText(processed_html)
            
            # Set the label as scroll area widget
            scroll_area.setWidget(html_label)
            
            # Add to layout
            self.viewer_layout.addWidget(scroll_area)
            print("✅ Direct HTML display created")
            
        except Exception as e:
            print(f"❌ Direct HTML viewer failed: {e}")
            self._create_html_fallback_viewer()
    
    def _process_html_for_display(self, html_content):
        """Process HTML content to make it suitable for QLabel display"""
        try:
            # Extract content between <body> tags or use full content
            import re
            
            # Find body content
            body_match = re.search(r'<body[^>]*>(.*?)</body>', html_content, re.DOTALL | re.IGNORECASE)
            if body_match:
                content = body_match.group(1)
            else:
                # If no body tags, look for main content
                content = html_content
            
            # Clean up the HTML for better QLabel display
            # Remove complex CSS and scripts
            content = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL | re.IGNORECASE)
            content = re.sub(r'<style[^>]*>.*?</style>', '', content, flags=re.DOTALL | re.IGNORECASE)
            
            # Simplify table styling for QLabel
            content = re.sub(r'<table[^>]*>', '<table border="1" style="border-collapse: collapse; width: 100%; margin: 10px 0;">', content)
            content = re.sub(r'<td[^>]*>', '<td style="padding: 8px; border: 1px solid #ccc; vertical-align: top;">', content)
            content = re.sub(r'<th[^>]*>', '<th style="padding: 8px; border: 1px solid #ccc; background: #f5f5f5; font-weight: bold;">', content)
            
            # Ensure proper text formatting
            content = re.sub(r'<div[^>]*>', '<div style="margin: 5px 0;">', content)
            content = re.sub(r'<p[^>]*>', '<p style="margin: 8px 0;">', content)
            content = re.sub(r'<h[1-6][^>]*>', '<h3 style="margin: 15px 0 10px 0; font-weight: bold; font-size: 14px;">', content)
            content = re.sub(r'</h[1-6]>', '</h3>', content)
            
            # Add some basic styling
            styled_content = f"""
            <div style="font-family: Arial, sans-serif; font-size: 10px; line-height: 1.4; color: #000;">
                {content}
            </div>
            """
            
            return styled_content
            
        except Exception as e:
            print(f"❌ HTML processing failed: {e}")
            return f"<p>Error processing HTML content: {str(e)}</p>"
    
    def _create_html_fallback_viewer(self):
        """Fallback HTML viewer when direct HTML display is not available"""
        try:
            # Create a container for preview and action buttons
            container = QFrame()
            container.setStyleSheet(f"""
                QFrame {{
                    background: {WHITE};
                    border: 2px solid {BORDER};
                    border-radius: 8px;
                }}
            """)
            
            layout = QVBoxLayout(container)
            layout.setContentsMargins(20, 20, 20, 20)
            layout.setSpacing(15)
            
            # Title
            title_label = QLabel("📄 Invoice Preview")
            title_label.setAlignment(Qt.AlignCenter)
            title_label.setStyleSheet(f"""
                QLabel {{
                    font-size: 18px;
                    font-weight: bold;
                    color: {PRIMARY};
                    margin-bottom: 10px;
                }}
            """)
            layout.addWidget(title_label)
            
            # Invoice info
            try:
                # Read HTML to extract basic invoice info
                with open(self.pdf_path, 'r', encoding='utf-8') as f:
                    html_content = f.read()
                
                # Extract some basic info from HTML
                import re
                
                # Try to extract invoice details
                invoice_no_match = re.search(r'INV[-_][^<\s]+|Invoice[^:]*:\s*([^<\n\s]+)', html_content, re.IGNORECASE)
                date_match = re.search(r'Date[^:]*:\s*([^<\n]+)|(\d{2}-\d{2}-\d{4})', html_content, re.IGNORECASE)
                company_match = re.search(r'<h[1-3][^>]*>([^<]*(?:COMPANY|CORP|LTD|PVT)[^<]*)</h[1-3]>', html_content, re.IGNORECASE)
                
                # Extract values with better handling
                if invoice_no_match:
                    if invoice_no_match.group(1):
                        invoice_no = invoice_no_match.group(1).strip()
                    else:
                        invoice_no = invoice_no_match.group(0).strip()
                else:
                    invoice_no = "N/A"
                
                if date_match:
                    if date_match.group(1):
                        invoice_date = date_match.group(1).strip()
                    elif date_match.group(2):
                        invoice_date = date_match.group(2).strip()
                    else:
                        invoice_date = date_match.group(0).strip()
                else:
                    invoice_date = "N/A"
                
                company_name = company_match.group(1).strip() if company_match else "Invoice"
                
                info_text = f"""
                <div style="background: #f8f9fa; padding: 15px; border-radius: 6px; border-left: 4px solid {PRIMARY};">
                    <p style="margin: 0 0 8px 0; font-size: 14px;"><strong>Company:</strong> {company_name}</p>
                    <p style="margin: 0 0 8px 0; font-size: 14px;"><strong>Invoice Number:</strong> {invoice_no}</p>
                    <p style="margin: 0 0 8px 0; font-size: 14px;"><strong>Date:</strong> {invoice_date}</p>
                    <p style="margin: 0; font-size: 14px;"><strong>File:</strong> {os.path.basename(self.pdf_path)}</p>
                </div>
                """
                
            except Exception:
                info_text = f"""
                <div style="background: #f8f9fa; padding: 15px; border-radius: 6px;">
                    <p style="margin: 0; font-size: 14px;"><strong>File:</strong> {os.path.basename(self.pdf_path)}</p>
                </div>
                """
            
            info_label = QLabel()
            info_label.setText(info_text)
            info_label.setWordWrap(True)
            layout.addWidget(info_label)
            
            # Preview button
            preview_button = QPushButton("🔍 Open Full Preview in Browser")
            preview_button.setStyleSheet(f"""
                QPushButton {{
                    background: {SUCCESS};
                    color: {WHITE};
                    border: none;
                    padding: 12px 24px;
                    border-radius: 8px;
                    font-size: 14px;
                    font-weight: bold;
                    margin: 10px 0;
                }}
                QPushButton:hover {{
                    background: #059669;
                }}
                QPushButton:pressed {{
                    background: #047857;
                }}
            """)
            preview_button.clicked.connect(self._open_full_preview)
            layout.addWidget(preview_button)
            
            # Instructions
            instructions_text = """
                <div style="background: #e3f2fd; padding: 15px; border-radius: 6px; border-left: 4px solid #2196f3;">
                    <h4 style="margin: 0 0 10px 0; color: #1976d2;">Quick Actions:</h4>
                    <ul style="margin: 0; padding-left: 20px;">
                        <li style="margin: 5px 0;">Click <strong>"Print"</strong> below to print the invoice</li>
                        <li style="margin: 5px 0;">Click <strong>"Download PDF"</strong> to save as PDF</li>
                        <li style="margin: 5px 0;">Click <strong>"Open Full Preview"</strong> to view in browser</li>
                    </ul>
                </div>
            """
            
            instructions_label = QLabel()
            instructions_label.setText(instructions_text)
            instructions_label.setWordWrap(True)
            layout.addWidget(instructions_label)
            
            # Add some stretch
            layout.addStretch()
            
            self.viewer_layout.addWidget(container)
            print("✅ HTML fallback viewer with preview option created")
            
        except Exception as e:
            print(f"❌ HTML fallback viewer failed: {e}")
            self._create_error_viewer()
    
    def _open_full_preview(self):
        """Open the invoice in browser for full preview"""
        try:
            import webbrowser
            file_url = 'file://' + os.path.abspath(self.pdf_path)
            webbrowser.open(file_url)
            print("✅ Invoice opened in browser for preview")
        except Exception as e:
            print(f"❌ Failed to open browser preview: {e}")
            QMessageBox.warning(self, "Preview Error", f"Failed to open browser preview:\n{str(e)}")
    
    def _load_pdf_preview(self):
        """Load PDF file preview (original functionality)"""
        # Always use our enhanced fallback viewer for better control and preview quality
        # Skip web engine to ensure consistent behavior across different systems
        print("ℹ️ Using enhanced PDF preview for better quality")
        
        # Use fallback viewer only if not already created
        if not self.pdf_viewer_created:
            print("ℹ️ Creating enhanced PDF viewer")
            self._create_single_fallback_viewer()
            self.pdf_viewer_created = True
        else:
            print("ℹ️ Enhanced viewer already exists")
    
    def _create_error_viewer(self):
        """Create error viewer when file cannot be loaded"""
        error_label = QLabel()
        error_label.setAlignment(Qt.AlignCenter)
        error_label.setStyleSheet(f"""
            QLabel {{
                background: #FEE2E2;
                border: 2px solid #F87171;
                border-radius: 8px;
                padding: 20px;
                font-size: 14px;
                color: #DC2626;
            }}
        """)
        error_label.setText("""
            ❌ Preview Error
            
            Unable to load the invoice file.
            Please try generating the invoice again.
        """)
        
        self.viewer_layout.addWidget(error_label)
        print("⚠️ Error viewer created")
    
    def _create_single_fallback_viewer(self):
        """Create a single fallback viewer to prevent duplicates"""
        try:
            # Clear any existing content first
            self._clear_viewer_layout()
            
            # Try multiple PDF rendering methods
            if self._render_pdf_with_pymupdf():
                print("✅ PDF rendered successfully with PyMuPDF")
                return
                
            if self._render_pdf_with_pdf2image():
                print("✅ PDF rendered successfully with pdf2image")
                return
                
            if self._render_pdf_with_wand():
                print("✅ PDF rendered successfully with Wand")
                return
            
            # If all rendering fails, try to auto-install PyMuPDF and try again
            if self._try_install_pymupdf():
                if self._render_pdf_with_pymupdf():
                    print("✅ PDF rendered successfully with auto-installed PyMuPDF")
                    return
            
            # Last resort: show a simple viewer that opens external PDF
            self._create_external_pdf_viewer()
            
        except Exception as e:
            print(f"❌ Single fallback viewer creation failed: {e}")
            self._create_external_pdf_viewer()
    
    def _clear_viewer_layout(self):
        """Clear the main viewer layout to prevent duplicates"""
        if hasattr(self, 'viewer_layout') and self.viewer_layout:
            while self.viewer_layout.count():
                child = self.viewer_layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
    
    def _render_pdf_with_pymupdf(self):
        """Render PDF using PyMuPDF for high-quality preview"""
        try:
            import fitz  # PyMuPDF
            
            print(f"🔍 PyMuPDF: Opening PDF: {self.pdf_path}")
            
            # Open PDF document
            doc = fitz.open(self.pdf_path)
            page = doc[0]  # Get first page
            
            # Render at high resolution for crisp display
            zoom_factor = 2.0  # Good balance between quality and performance
            mat = fitz.Matrix(zoom_factor, zoom_factor)
            pix = page.get_pixmap(matrix=mat)
            img_data = pix.tobytes("png")
            
            print(f"✅ PyMuPDF: Rendered PDF page as {pix.width}x{pix.height} pixels")
            
            # Create QPixmap
            pixmap = QPixmap()
            success = pixmap.loadFromData(img_data)
            
            if not success:
                print("❌ Failed to create QPixmap from PDF data")
                doc.close()
                return False
                
            print(f"✅ PyMuPDF: QPixmap created successfully {pixmap.width()}x{pixmap.height()}")
            
            # Add to the main viewer layout directly
            self._add_pixmap_to_viewer(pixmap)
            
            doc.close()
            return True
            
        except ImportError:
            print("❌ PyMuPDF not available for PDF rendering")
            return False
        except Exception as e:
            print(f"❌ PyMuPDF rendering failed: {e}")
            return False
            
    def _render_pdf_with_pdf2image(self):
        """Render PDF using pdf2image library"""
        try:
            from pdf2image import convert_from_path
            import tempfile
            
            print(f"🔍 pdf2image: Converting PDF: {self.pdf_path}")
            
            # Convert first page to image
            images = convert_from_path(self.pdf_path, first_page=1, last_page=1, dpi=200)
            
            if not images:
                return False
                
            # Save to temporary file
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
                images[0].save(temp_file.name, 'PNG')
                
                # Create QPixmap
                pixmap = QPixmap(temp_file.name)
                
                if pixmap.isNull():
                    os.unlink(temp_file.name)
                    return False
                
                # Add to viewer
                self._add_pixmap_to_viewer(pixmap)
                
                # Clean up
                os.unlink(temp_file.name)
                
                print("✅ pdf2image: PDF rendered successfully")
                return True
                
        except ImportError:
            print("❌ pdf2image not available")
            return False
        except Exception as e:
            print(f"❌ pdf2image rendering failed: {e}")
            return False
            
    def _render_pdf_with_wand(self):
        """Render PDF using Wand (ImageMagick) library"""
        try:
            from wand.image import Image as WandImage
            import tempfile
            
            print(f"🔍 Wand: Converting PDF: {self.pdf_path}")
            
            # Convert first page using Wand
            with WandImage(filename=f"{self.pdf_path}[0]", resolution=200) as img:
                img.format = 'png'
                
                with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
                    img.save(filename=temp_file.name)
                    
                    # Create QPixmap
                    pixmap = QPixmap(temp_file.name)
                    
                    if pixmap.isNull():
                        os.unlink(temp_file.name)
                        return False
                    
                    # Add to viewer
                    self._add_pixmap_to_viewer(pixmap)
                    
                    # Clean up
                    os.unlink(temp_file.name)
                    
                    print("✅ Wand: PDF rendered successfully")
                    return True
                    
        except ImportError:
            print("❌ Wand not available")
            return False
        except Exception as e:
            print(f"❌ Wand rendering failed: {e}")
            return False
            
    def _try_install_pymupdf(self):
        """Try to auto-install PyMuPDF"""
        try:
            import subprocess
            import sys
            
            print("🔄 Attempting to install PyMuPDF...")
            result = subprocess.run([sys.executable, '-m', 'pip', 'install', 'pymupdf'], 
                                  capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                print("✅ PyMuPDF installed successfully")
                return True
            else:
                print(f"❌ PyMuPDF installation failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Failed to install PyMuPDF: {e}")
            return False
            
    def _create_external_pdf_viewer(self):
        """Create a viewer that opens PDF in external application"""
        info_widget = QLabel()
        info_widget.setAlignment(Qt.AlignCenter)
        
        info_html = f"""
        <div style='text-align: center; padding: 60px 40px;'>
            <h1 style='color: {PRIMARY}; font-size: 24px; margin-bottom: 20px;'>
                📄 PDF Preview
            </h1>
            <p style='font-size: 16px; color: {TEXT_SECONDARY}; margin-bottom: 25px;'>
                Click the button below to view your invoice
            </p>
            <div style='background: {BACKGROUND}; padding: 20px; border-radius: 8px; margin: 20px 0;'>
                <p style='font-size: 14px; color: {TEXT_SECONDARY}; margin: 5px 0;'>
                    <strong>File:</strong> {os.path.basename(self.pdf_path)}
                </p>
            </div>
        </div>
        """
        
        info_widget.setText(info_html)
        info_widget.setStyleSheet(f"""
            QLabel {{
                background: {WHITE};
                border: 2px solid {BORDER};
                border-radius: 12px;
                margin: 10px;
            }}
        """)
        
        # Add open PDF button
        open_btn = QPushButton("📖 View PDF")
        open_btn.setFixedSize(200, 50)
        open_btn.setStyleSheet(f"""
            QPushButton {{
                background: {PRIMARY};
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background: #1d4ed8;
            }}
        """)
        open_btn.clicked.connect(self._open_external_pdf)
        
        # Add to layout
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.addWidget(info_widget)
        layout.addWidget(open_btn, 0, Qt.AlignCenter)
        
        self.viewer_layout.addWidget(container)
        
    def _open_external_pdf(self):
        """Open PDF in external application"""
        try:
            import platform
            import subprocess
            
            system = platform.system()
            if system == "Darwin":  # macOS
                subprocess.run(['open', self.pdf_path])
            elif system == "Windows":
                subprocess.run(['start', self.pdf_path], shell=True)
            else:  # Linux
                subprocess.run(['xdg-open', self.pdf_path])
                
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not open PDF: {e}")
    
    def _add_pixmap_to_viewer(self, pixmap):
        """Add the PDF pixmap to the main viewer layout"""
        try:
            # Create scroll area for PDF viewing
            scroll_area = QScrollArea()
            scroll_area.setWidgetResizable(True)
            scroll_area.setAlignment(Qt.AlignCenter)
            scroll_area.setStyleSheet(f"""
                QScrollArea {{
                    border: 2px solid {BORDER};
                    border-radius: 8px;
                    background: {WHITE};
                }}
                QScrollBar:vertical {{
                    border: none;
                    background: {BACKGROUND};
                    width: 12px;
                    border-radius: 6px;
                }}
                QScrollBar::handle:vertical {{
                    background: {PRIMARY};
                    border-radius: 6px;
                    min-height: 20px;
                }}
            """)
            
            # Create label to display PDF image
            pdf_label = QLabel()
            pdf_label.setPixmap(pixmap)
            pdf_label.setAlignment(Qt.AlignCenter)
            pdf_label.setScaledContents(False)  # Maintain aspect ratio
            pdf_label.setStyleSheet("""
                QLabel {
                    background: white;
                    padding: 20px;
                    border: 1px solid #e5e5e5;
                    border-radius: 4px;
                }
            """)
            
            scroll_area.setWidget(pdf_label)
            
            # Add to the main viewer layout
            self.viewer_layout.addWidget(scroll_area)
            
            # Store reference for future use
            self.pdf_image_label = pdf_label
            
            print("🎉 PDF preview added to viewer successfully!")
                    
        except Exception as e:
            print(f"❌ Failed to add pixmap to viewer: {e}")
    
    def _clear_layout(self, layout):
        """Clear all widgets from a layout"""
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
    
    def _render_pdf_with_other_methods(self):
        """Try alternative PDF rendering methods"""
        # This could include pdf2image, wand, etc.
        # For now, return False to use the info message
        return False
    
    def _show_pdf_ready_message(self):
        """Show a professional 'PDF Ready' message in the main viewer"""
        try:
            file_size = os.path.getsize(self.pdf_path)
            file_size_mb = file_size / (1024 * 1024)
            
            # Create professional info display
            info_widget = QLabel()
            info_widget.setAlignment(Qt.AlignCenter)
            
            info_html = f"""
            <div style='text-align: center; padding: 60px 40px;'>
                <h1 style='color: {PRIMARY}; font-size: 24px; margin-bottom: 20px;'>
                    📄 Invoice PDF Ready
                </h1>
                <p style='font-size: 16px; color: {TEXT_SECONDARY}; margin-bottom: 25px;'>
                    Your invoice has been generated successfully
                </p>
                <div style='background: {BACKGROUND}; padding: 20px; border-radius: 8px; margin: 20px 0;'>
                    <p style='font-size: 14px; color: {TEXT_SECONDARY}; margin: 5px 0;'>
                        <strong>File:</strong> {os.path.basename(self.pdf_path)}
                    </p>
                    <p style='font-size: 14px; color: {TEXT_SECONDARY}; margin: 5px 0;'>
                        <strong>Size:</strong> {file_size_mb:.2f} MB ({file_size:,} bytes)
                    </p>
                </div>
                <p style='font-size: 14px; color: {SUCCESS}; margin-top: 30px;'>
                    ✅ Ready to print or download
                </p>
            </div>
            """
            
            info_widget.setText(info_html)
            info_widget.setStyleSheet(f"""
                QLabel {{
                    background: {WHITE};
                    border: 2px solid {BORDER};
                    border-radius: 12px;
                    margin: 10px;
                }}
            """)
            
            # Add to the main viewer layout
            self.viewer_layout.addWidget(info_widget)
            print("✅ PDF ready message displayed in main viewer")
                    
        except Exception as e:
            print(f"❌ Failed to show PDF ready message: {e}")
            # Final fallback - show a simple message box
            QMessageBox.information(self, "PDF Ready", 
                                  f"Invoice PDF generated successfully:\n{os.path.basename(self.pdf_path)}")
    

    
    def print_pdf(self):
        """Print the invoice (handles both PDF and HTML files)"""
        print(f"🖨️ Print button clicked! File path: {self.pdf_path}")
        try:
            if not os.path.exists(self.pdf_path):
                print(f"❌ File not found: {self.pdf_path}")
                QMessageBox.warning(self, "Print Error", "Invoice file not found!")
                return
            
            print(f"✅ File exists: {os.path.getsize(self.pdf_path)} bytes")
            
            # Check if it's an HTML file
            if self.pdf_path.lower().endswith('.html'):
                print("🌐 Opening HTML invoice in browser for printing")
                self._open_html_for_printing()
            else:
                print("📄 Handling PDF file printing")
                self._handle_pdf_printing()
            
            print("🏁 Print function completed")
            
        except Exception as e:
            print(f"❌ Exception in print_pdf: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Print Error", 
                               f"Failed to open invoice for printing:\n{str(e)}\n\nPlease open the file manually.")
    
    def _open_html_for_printing(self):
        """Open HTML file in browser for printing"""
        try:
            import webbrowser
            
            # Open HTML file in browser
            file_url = 'file://' + os.path.abspath(self.pdf_path)
            webbrowser.open(file_url)
            
            # Show instruction message
            QMessageBox.information(self, "Print Instructions", 
                                  """✅ Invoice opened in your browser!

To print the invoice:
• Press Ctrl+P (or Cmd+P on Mac)
• Choose your printer
• Select 'Save as PDF' if you want to save as PDF
• Click Print

The browser print dialog will give you the best quality output.""")
            
        except Exception as e:
            print(f"❌ Failed to open HTML in browser: {e}")
            QMessageBox.critical(self, "Print Error", 
                               f"Failed to open invoice in browser:\n{str(e)}")
    
    def _handle_pdf_printing(self):
        """Handle PDF file printing (original functionality)"""
        # Instead of opening external app, show print options dialog
        from PyQt5.QtPrintSupport import QPrintDialog, QPrinter
        from PyQt5.QtGui import QPainter, QPixmap
        
        try:
            # Create printer object
            printer = QPrinter(QPrinter.HighResolution)
            printer.setPageSize(QPrinter.A4)
            
            # Show print dialog
            print_dialog = QPrintDialog(printer, self)
            print_dialog.setWindowTitle("Print Invoice")
            
            if print_dialog.exec_() == QPrintDialog.Accepted:
                # User clicked OK in print dialog
                print("✅ User confirmed printing")
                
                # Try to render PDF content for printing
                if self._print_pdf_content(printer):
                    QMessageBox.information(self, "Print Sent", 
                                          "Invoice has been sent to the printer successfully!")
                else:
                    # Fallback: open in external app if direct printing fails
                    self._fallback_external_print()
            else:
                print("ℹ️ User cancelled printing")
                
        except ImportError:
            print("❌ Qt Print Support not available, falling back to external print")
            self._fallback_external_print()
        except Exception as e:
            print(f"❌ Printing error: {e}")
            self._fallback_external_print()
    
    def _print_pdf_content(self, printer):
        """Try to print PDF content directly"""
        try:
            import fitz  # PyMuPDF
            from PyQt5.QtGui import QPainter, QPixmap
            
            # Open PDF document
            doc = fitz.open(self.pdf_path)
            painter = QPainter()
            
            if not painter.begin(printer):
                return False
                
            # Print each page
            for page_num in range(len(doc)):
                if page_num > 0:
                    printer.newPage()
                    
                page = doc[page_num]
                
                # Render page to image at high resolution
                mat = fitz.Matrix(3.0, 3.0)  # High resolution for printing
                pix = page.get_pixmap(matrix=mat)
                img_data = pix.tobytes("png")
                
                # Convert to QPixmap and draw
                pixmap = QPixmap()
                if pixmap.loadFromData(img_data):
                    # Scale to fit printer page
                    painter.drawPixmap(printer.pageRect(), pixmap)
                    
            painter.end()
            doc.close()
            return True
            
        except Exception as e:
            print(f"❌ Direct PDF printing failed: {e}")
            return False
    
    def _fallback_external_print(self):
        """Fallback to opening PDF in external application"""
        try:
            import platform
            import subprocess
            system = platform.system()
            
            if system == "Darwin":  # macOS
                subprocess.run(['open', '-a', 'Preview', self.pdf_path], check=True)
                QMessageBox.information(self, "Print Ready", 
                                      "PDF opened in Preview.\n\n" +
                                      "Press ⌘+P (Command+P) to print with full printer control.")
            elif system == "Windows":
                subprocess.run(['powershell', '-Command', f'Start-Process -FilePath "{self.pdf_path}" -Verb Print'], check=True)
            else:  # Linux
                subprocess.run(['xdg-open', self.pdf_path], check=True)
                QMessageBox.information(self, "Print Ready", 
                                      "PDF opened. Use Ctrl+P to print.")
                                      
        except Exception as e:
            QMessageBox.warning(self, "Print Error", 
                              f"Unable to open PDF for printing: {str(e)}")
            
        except Exception as e:
            print(f"❌ Exception in print_pdf: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Print Error", 
                               f"Failed to print PDF:\n{str(e)}\n\nPlease open the PDF manually and print.")
    
    def download_pdf(self):
        """Save invoice file to user-selected location (handles both PDF and HTML)"""
        try:
            if not os.path.exists(self.pdf_path):
                QMessageBox.warning(self, "Download Error", "Invoice file not found!")
                return
            
            # Check file type and handle accordingly
            if self.pdf_path.lower().endswith('.html'):
                self._download_html_as_pdf()
            else:
                self._download_pdf_directly()
        
        except Exception as e:
            QMessageBox.critical(self, "Download Error", 
                               f"Failed to save invoice:\n{str(e)}")
    
    def _download_html_as_pdf(self):
        """Handle downloading HTML invoice as PDF"""
        try:
            # Extract invoice number from filename for suggestion
            base_name = os.path.basename(self.pdf_path)
            invoice_name = base_name.replace('.html', '.pdf')
            
            # Open file save dialog
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Save Invoice as PDF",
                invoice_name,
                "PDF files (*.pdf);;HTML files (*.html);;All files (*.*)"
            )

            if file_path:
                if file_path.lower().endswith('.pdf'):
                    # User wants PDF - show instructions
                    self._show_pdf_save_instructions()
                else:
                    # User wants HTML - copy directly
                    shutil.copy2(self.pdf_path, file_path)
                    QMessageBox.information(self, "Download Successful", 
                                          f"Invoice HTML saved to:\n{file_path}\n\nYou can open this file in any browser and save as PDF using Ctrl+P → Save as PDF")
                    self.accept()

        except Exception as e:
            raise e
    
    def _show_pdf_save_instructions(self):
        """Show instructions for saving HTML as PDF"""
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Save as PDF Instructions")
        msg.setText("To save the invoice as PDF:")
        msg.setDetailedText("""1. The invoice will open in your browser
2. Press Ctrl+P (or Cmd+P on Mac)
3. Choose 'Save as PDF' as the destination
4. Select your desired location and click Save

This method ensures the best quality PDF output with proper formatting.""")
        
        open_button = msg.addButton("Open in Browser", QMessageBox.AcceptRole)
        cancel_button = msg.addButton("Cancel", QMessageBox.RejectRole)
        
        msg.exec_()
        
        if msg.clickedButton() == open_button:
            # Open HTML in browser
            import webbrowser
            file_url = 'file://' + os.path.abspath(self.pdf_path)
            webbrowser.open(file_url)
            self.accept()
    
    def _download_pdf_directly(self):
        """Handle downloading actual PDF files"""
        # Extract invoice number from filename for suggestion
        base_name = os.path.basename(self.pdf_path)
        suggested_name = base_name if base_name.endswith('.pdf') else f"{base_name}.pdf"
        
        # Open file save dialog
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Invoice PDF",
            suggested_name,
            "PDF files (*.pdf);;All files (*.*)"
        )
        
        if file_path:
            # Copy PDF to selected location
            shutil.copy2(self.pdf_path, file_path)
            
            QMessageBox.information(self, "Download Successful", 
                                  f"PDF saved to:\n{file_path}")
            
            # Close dialog after successful download
            self.accept()
    
    def apply_styling(self):
        """Apply overall dialog styling"""
        self.setStyleSheet(f"""
            QDialog {{
                background: {BACKGROUND};
                border: 2px solid {BORDER};
                border-radius: 10px;
            }}
        """)
    
    def keyPressEvent(self, event):
        """Handle keyboard shortcuts"""
        if event.key() == Qt.Key_Escape:
            self.reject()
        elif event.key() == Qt.Key_P and event.modifiers() == Qt.ControlModifier:
            self.print_pdf()
        elif event.key() == Qt.Key_S and event.modifiers() == Qt.ControlModifier:
            self.download_pdf()
        else:
            super().keyPressEvent(event)
    
    def closeEvent(self, event):
        """Clean up when dialog is closed"""
        # Optionally clean up the temporary PDF file
        # For now, we'll leave it for manual cleanup
        super().closeEvent(event)
