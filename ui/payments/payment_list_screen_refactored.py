"""
Payment List Screen (Refactored) - Uses FilterWidget for consistent filter management
"""

from PySide6.QtWidgets import QTableWidgetItem, QDialog, QMessageBox
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QColor

from theme import (
    PRIMARY, TEXT_PRIMARY, TEXT_SECONDARY, SUCCESS, DANGER, WARNING,
    FONT_SIZE_SMALL, get_normal_font, get_bold_font
)

from widgets import (
    StatCard, ListTable, TableFrame, TableActionButton,
    ListHeader, StatsContainer, FilterWidget
)

from ui.base import BaseScreen, PaginationWidget
from controllers.payment_controller import payment_controller
from ui.error_handler import UIErrorHandler
from core.core_utils import format_currency
from core.logger import get_logger
from ui.payments.payment_form_dialog import SupplierPaymentDialog

logger = get_logger(__name__)


class PaymentsScreen(BaseScreen):
    """Payment List Screen - Refactored with FilterWidget"""
    
    payment_updated = Signal()
    ITEMS_PER_PAGE = 49
    DEBOUNCE_DELAY = 500
    
    def __init__(self, parent=None):
        super().__init__(title="Payments", parent=parent)
        self.setObjectName("PaymentsScreen")
        logger.debug("Initializing PaymentsScreen")
        
        self._controller = payment_controller
        self._all_payments = []
        self._filtered_payments = []
        self._is_loading = False
        self.pagination_widget = None
        
        self._search_debounce_timer = QTimer()
        self._search_debounce_timer.setSingleShot(True)
        self._search_debounce_timer.timeout.connect(self._on_search_debounce)
        
        self._setup_ui()
        self._load_payments()
    
    def _setup_ui(self):
        self.title_label.hide()
        self.content_frame.hide()
        self.main_layout.setContentsMargins(24, 24, 24, 24)
        self.main_layout.setSpacing(20)
        
        self.main_layout.addWidget(self._create_header())
        self.main_layout.addWidget(self._create_stats_section())
        self.main_layout.addWidget(self._create_filters_section())
        self.main_layout.addWidget(self._create_table_section(), 1)
        self.main_layout.addWidget(self._create_pagination_controls())
    
    def _create_header(self):
        header = ListHeader("Payments", "+ New Payment")
        header.add_clicked.connect(self._on_add_clicked)
        header.export_clicked.connect(self._on_export_clicked)
        return header
    
    def _create_stats_section(self):
        self._total_card = StatCard("💳", "Total Payments", "0", PRIMARY)
        self._amount_card = StatCard("💰", "Total Amount", "₹0", SUCCESS)
        self._pending_card = StatCard("⏳", "Pending", "0", WARNING)
        self._cleared_card = StatCard("✅", "Cleared", "0", "#10B981")
        
        return StatsContainer([
            self._total_card,
            self._amount_card,
            self._pending_card,
            self._cleared_card
        ])
    
    def _create_filters_section(self):
        filter_widget = FilterWidget()
        filter_widget.add_search_filter("Search by party name, payment ref...")
        filter_widget.search_changed.connect(self._on_search_changed)
        
        status_options = {"All": "All", "Pending": "Pending", "Cleared": "Cleared", "Failed": "Failed", "Cancelled": "Cancelled"}
        self._status_combo = filter_widget.add_combo_filter("status", "Status:", status_options)
        
        period_options = {
            "All Time": "All Time",
            "Today": "Today",
            "This Week": "This Week",
            "This Month": "This Month",
            "This Year": "This Year"
        }
        self._period_combo = filter_widget.add_combo_filter("period", "Period:", period_options)
        
        self._party_combo = filter_widget.add_combo_filter("party", "Party:", {"All Parties": "All Parties"})
        self._party_combo.setMinimumWidth(150)
        
        filter_widget.add_stretch()
        filter_widget.add_refresh_button(lambda: self._load_payments(reset_page=True))
        filter_widget.filters_changed.connect(self._on_filter_changed)
        
        return filter_widget
    
    def _create_table_section(self):
        table_frame = TableFrame()
        self._table = ListTable(headers=["#", "Date", "Party", "Amount", "Method", "Status", "Edit", "Delete"])
        self._table.configure_columns([
            {"width": 50, "resize": "fixed"},
            {"width": 100, "resize": "fixed"},
            {"resize": "stretch"},
            {"width": 120, "resize": "fixed"},
            {"width": 100, "resize": "fixed"},
            {"width": 100, "resize": "fixed"},
            {"width": 70, "resize": "fixed"},
            {"width": 70, "resize": "fixed"},
        ])
        table_frame.set_table(self._table)
        return table_frame
    
    def _create_pagination_controls(self):
        self.pagination_widget = PaginationWidget(items_per_page=self.ITEMS_PER_PAGE, entity_name="payment")
        self.pagination_widget.page_changed.connect(self._on_pagination_page_changed)
        return self.pagination_widget
    
    def _load_payments(self, reset_page: bool = False):
        if self._is_loading:
            return
        try:
            self._is_loading = True
            self._all_payments = self._controller.get_all_payments()
            logger.debug(f"Loaded {len(self._all_payments)} payments")
            self._update_party_filter()
            if reset_page and self.pagination_widget:
                self.pagination_widget.reset_to_page_one()
            self._apply_filters()
        except Exception as e:
            logger.error(f"Failed to load payments: {str(e)}")
            UIErrorHandler.show_error("Load Error", f"Failed to load payments: {str(e)}")
        finally:
            self._is_loading = False
    
    def _apply_filters(self):
        try:
            search_text = ""
            status = self._status_combo.currentData() if hasattr(self, '_status_combo') else "All"
            period = self._period_combo.currentData() if hasattr(self, '_period_combo') else "All Time"
            party = self._party_combo.currentData() if hasattr(self, '_party_combo') else "All Parties"
            
            self._filtered_payments = self._controller.filter_payments(
                payments=self._all_payments,
                search_text=search_text,
                status=status,
                period=period,
                party=party
            )
            
            if self.pagination_widget:
                total_items = len(self._filtered_payments)
                items_per_page = self.pagination_widget.get_items_per_page()
                total_pages = (total_items + items_per_page - 1) // items_per_page
                self.pagination_widget.set_pagination_state(1, total_pages, total_items)
            
            self._update_stats()
            self._populate_table()
            logger.debug(f"Filters applied: {len(self._filtered_payments)} payments shown")
        except Exception as e:
            logger.error(f"Failed to apply filters: {str(e)}")
            UIErrorHandler.show_error("Filter Error", f"Failed to apply filters: {str(e)}")
    
    def _update_party_filter(self):
        try:
            parties = self._controller.get_unique_parties(self._all_payments)
            current = self._party_combo.currentData()
            self._party_combo.blockSignals(True)
            self._party_combo.clear()
            self._party_combo.addItem("All Parties", "All Parties")
            for party in parties:
                self._party_combo.addItem(party.get('name', ''), party.get('name', ''))
            idx = self._party_combo.findData(current)
            if idx >= 0:
                self._party_combo.setCurrentIndex(idx)
            self._party_combo.blockSignals(False)
        except Exception as e:
            logger.error(f"Failed to update party filter: {str(e)}")
    
    def _update_stats(self):
        try:
            stats = self._controller.calculate_payment_stats(self._all_payments)
            self._total_card.set_value(str(stats.get('total', 0)))
            self._amount_card.set_value(format_currency(stats.get('total_amount', 0)))
            self._pending_card.set_value(str(stats.get('pending_count', 0)))
            self._cleared_card.set_value(str(stats.get('cleared_count', 0)))
        except Exception as e:
            logger.error(f"Failed to update stats: {str(e)}")
    
    def _populate_table(self):
        try:
            self._table.setRowCount(0)
            if not self.pagination_widget:
                return
            current_page = self.pagination_widget.get_current_page()
            items_per_page = self.pagination_widget.get_items_per_page()
            start_idx = (current_page - 1) * items_per_page
            end_idx = start_idx + items_per_page
            page_payments = self._filtered_payments[start_idx:end_idx]
            for idx, payment in enumerate(page_payments):
                self._add_table_row(start_idx + idx, payment)
        except Exception as e:
            logger.error(f"Failed to populate table: {str(e)}")
            UIErrorHandler.show_error("Table Error", f"Failed to populate table: {str(e)}")
    
    def _add_table_row(self, idx: int, payment: dict):
        try:
            row = self._table.rowCount()
            self._table.insertRow(row)
            self._table.setRowHeight(row, 50)
            
            num_item = QTableWidgetItem(str(idx + 1))
            num_item.setTextAlignment(Qt.AlignCenter)
            num_item.setForeground(QColor(TEXT_SECONDARY))
            self._table.setItem(row, 0, num_item)
            
            date_item = QTableWidgetItem(payment.get('date', ''))
            date_item.setFont(get_normal_font())
            date_item.setTextAlignment(Qt.AlignCenter)
            self._table.setItem(row, 1, date_item)
            
            party_item = QTableWidgetItem(payment.get('party_name', ''))
            party_item.setFont(get_normal_font())
            self._table.setItem(row, 2, party_item)
            
            amount = float(payment.get('amount', 0) or 0)
            amount_item = QTableWidgetItem(format_currency(amount))
            amount_item.setFont(get_bold_font(FONT_SIZE_SMALL))
            amount_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self._table.setItem(row, 3, amount_item)
            
            method_item = QTableWidgetItem(payment.get('payment_method', ''))
            method_item.setFont(get_normal_font())
            method_item.setTextAlignment(Qt.AlignCenter)
            self._table.setItem(row, 4, method_item)
            
            status = payment.get('status', 'Pending')
            status_item = QTableWidgetItem(status)
            status_item.setTextAlignment(Qt.AlignCenter)
            if status == 'Cleared':
                status_item.setForeground(QColor(SUCCESS))
            elif status == 'Failed':
                status_item.setForeground(QColor(DANGER))
            self._table.setItem(row, 5, status_item)
            
            edit_btn = TableActionButton(text="Edit", tooltip="Edit Payment", bg_color="#EEF2FF", hover_color=PRIMARY, size=(60, 32))
            edit_btn.clicked.connect(lambda checked, pmt=payment: self._on_edit_clicked(pmt))
            self._table.setCellWidget(row, 6, edit_btn)
            
            delete_btn = TableActionButton(text="Del", tooltip="Delete Payment", bg_color="#FEE2E2", hover_color=DANGER, size=(60, 32))
            delete_btn.clicked.connect(lambda checked, pmt=payment: self._on_delete_clicked(pmt))
            self._table.setCellWidget(row, 7, delete_btn)
        except Exception as e:
            logger.error(f"Failed to add table row: {str(e)}")
    
    def _on_search_changed(self, text: str):
        self._search_debounce_timer.stop()
        self._search_debounce_timer.start(self.DEBOUNCE_DELAY)
    
    def _on_search_debounce(self):
        self._apply_filters()
    
    def _on_filter_changed(self):
        self._apply_filters()
    
    def _on_pagination_page_changed(self, page: int):
        self._populate_table()
    
    def _on_add_clicked(self):
        dialog = SupplierPaymentDialog(parent=self)
        if dialog.exec() == QDialog.Accepted:
            self._load_payments()
            self.payment_updated.emit()
    
    def _on_edit_clicked(self, payment: dict):
        dialog = SupplierPaymentDialog(payment_data=payment, parent=self)
        if dialog.exec() == QDialog.Accepted:
            self._load_payments()
            self.payment_updated.emit()
    
    def _on_delete_clicked(self, payment: dict):
        payment_id = payment.get('id')
        if not UIErrorHandler.ask_confirmation("Confirm Delete", "Delete this payment?"):
            return
        try:
            success, message = self._controller.delete_payment(payment_id)
            if success:
                UIErrorHandler.show_success("Success", "Payment deleted successfully!")
                self._load_payments()
                self.payment_updated.emit()
            else:
                UIErrorHandler.show_error("Error", message)
        except Exception as e:
            logger.error(f"Failed to delete payment: {str(e)}")
            UIErrorHandler.show_error("Error", f"Failed to delete payment: {str(e)}")
    
    def _on_export_clicked(self):
        QMessageBox.information(self, "Export", "📤 Export functionality coming soon!")
    
    def refresh(self):
        self._load_payments()
    
    def showEvent(self, event):
        super().showEvent(event)
        if not self._all_payments:
            self._load_payments()
