from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QTabWidget, QGroupBox, QFormLayout, QDateEdit, QMessageBox,
    QComboBox, QScrollArea, QFrame, QSplitter, QSpinBox, QDoubleSpinBox,
    QDialog, QLineEdit
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QColor, QFont
import logging
from datetime import datetime, timedelta
from src.db.business_db_manager import BusinessDBManager
from src.ui.wrestler_merchandise_ui import WrestlerMerchandiseUI

# Create a business database manager instance
business_db = BusinessDBManager()

class MerchandiseManagerUI(QWidget):
    """UI for managing all merchandise in the game"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle("Merchandise Manager")
        self.setMinimumSize(1000, 700)
        
        self.current_wrestler_window = None
        
        self.init_ui()
        self.load_sales_data()
        self.load_wrestlers()
    
    def init_ui(self):
        main_layout = QVBoxLayout()
        
        # Header
        header_layout = QHBoxLayout()
        
        title_label = QLabel("Merchandise Manager")
        title_font = title_label.font()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        self.auto_all_btn = QPushButton("Auto-Generate All")
        self.auto_all_btn.clicked.connect(self.auto_generate_all)
        header_layout.addWidget(self.auto_all_btn)
        
        main_layout.addLayout(header_layout)
        
        # Tab widget
        self.tab_widget = QTabWidget()
        
        # Sales tab
        sales_tab = QWidget()
        sales_layout = QVBoxLayout()
        
        # Date range selector
        date_range_box = QGroupBox("Date Range")
        date_form = QFormLayout()
        
        self.start_date = QDateEdit()
        self.start_date.setDate(QDate.currentDate().addMonths(-1))
        self.start_date.setCalendarPopup(True)
        date_form.addRow("Start Date:", self.start_date)
        
        self.end_date = QDateEdit()
        self.end_date.setDate(QDate.currentDate())
        self.end_date.setCalendarPopup(True)
        date_form.addRow("End Date:", self.end_date)
        
        date_btn_layout = QHBoxLayout()
        
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self.load_sales_data)
        date_btn_layout.addWidget(self.refresh_btn)
        
        self.last_30_btn = QPushButton("Last 30 Days")
        self.last_30_btn.clicked.connect(lambda: self.set_date_range(30))
        date_btn_layout.addWidget(self.last_30_btn)
        
        self.last_90_btn = QPushButton("Last 90 Days")
        self.last_90_btn.clicked.connect(lambda: self.set_date_range(90))
        date_btn_layout.addWidget(self.last_90_btn)
        
        self.all_time_btn = QPushButton("All Time")
        self.all_time_btn.clicked.connect(lambda: self.set_date_range(3650))  # ~10 years
        date_btn_layout.addWidget(self.all_time_btn)
        
        date_form.addRow("", date_btn_layout)
        date_range_box.setLayout(date_form)
        sales_layout.addWidget(date_range_box)
        
        # Summary section
        summary_box = QGroupBox("Sales Summary")
        summary_layout = QFormLayout()
        
        self.total_items_label = QLabel("0")
        summary_layout.addRow("Total Items Sold:", self.total_items_label)
        
        self.total_revenue_label = QLabel("$0.00")
        summary_layout.addRow("Total Revenue:", self.total_revenue_label)
        
        self.total_profit_label = QLabel("$0.00")
        summary_layout.addRow("Total Profit:", self.total_profit_label)
        
        self.company_profit_label = QLabel("$0.00")
        summary_layout.addRow("Company Profit:", self.company_profit_label)
        
        self.wrestler_profit_label = QLabel("$0.00")
        summary_layout.addRow("Wrestler Royalties:", self.wrestler_profit_label)
        
        summary_box.setLayout(summary_layout)
        sales_layout.addWidget(summary_box)
        
        # Top selling items
        items_box = QGroupBox("Top Selling Items")
        items_layout = QVBoxLayout()
        
        self.items_table = QTableWidget()
        self.items_table.setColumnCount(6)
        self.items_table.setHorizontalHeaderLabels([
            "Item", "Type", "Wrestler", "Total Sold", "Revenue", "Profit"
        ])
        self.items_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.items_table.verticalHeader().setVisible(False)
        self.items_table.setEditTriggers(QTableWidget.NoEditTriggers)
        items_layout.addWidget(self.items_table)
        
        items_box.setLayout(items_layout)
        sales_layout.addWidget(items_box)
        
        # Top selling wrestlers
        wrestlers_box = QGroupBox("Top Selling Wrestlers")
        wrestlers_layout = QVBoxLayout()
        
        self.wrestlers_table = QTableWidget()
        self.wrestlers_table.setColumnCount(4)
        self.wrestlers_table.setHorizontalHeaderLabels([
            "Wrestler", "Items Sold", "Revenue", "Profit"
        ])
        self.wrestlers_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.wrestlers_table.verticalHeader().setVisible(False)
        self.wrestlers_table.setEditTriggers(QTableWidget.NoEditTriggers)
        wrestlers_layout.addWidget(self.wrestlers_table)
        
        wrestlers_box.setLayout(wrestlers_layout)
        sales_layout.addWidget(wrestlers_box)
        
        sales_tab.setLayout(sales_layout)
        self.tab_widget.addTab(sales_tab, "Sales")
        
        # Roster tab
        roster_tab = QWidget()
        roster_layout = QVBoxLayout()
        
        # Filter
        filter_layout = QHBoxLayout()
        
        filter_layout.addWidget(QLabel("Filter:"))
        
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["All", "Has Merchandise", "No Merchandise"])
        self.filter_combo.currentIndexChanged.connect(self.apply_filter)
        filter_layout.addWidget(self.filter_combo)
        
        filter_layout.addStretch()
        
        roster_layout.addLayout(filter_layout)
        
        # Roster grid (scrollable)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        
        self.roster_widget = QWidget()
        self.roster_layout = QVBoxLayout()
        self.roster_widget.setLayout(self.roster_layout)
        
        scroll_area.setWidget(self.roster_widget)
        roster_layout.addWidget(scroll_area)
        
        roster_tab.setLayout(roster_layout)
        self.tab_widget.addTab(roster_tab, "Roster")
        
        main_layout.addWidget(self.tab_widget)
        
        # Bottom buttons
        button_layout = QHBoxLayout()
        
        button_layout.addStretch()
        
        self.close_btn = QPushButton("Close")
        self.close_btn.clicked.connect(self.close)
        button_layout.addWidget(self.close_btn)
        
        main_layout.addLayout(button_layout)
        
        self.setLayout(main_layout)
    
    def set_date_range(self, days):
        """Set the date range to last X days"""
        end_date = QDate.currentDate()
        start_date = end_date.addDays(-days)
        
        self.end_date.setDate(end_date)
        self.start_date.setDate(start_date)
        
        self.load_sales_data()
    
    def load_sales_data(self):
        """Load sales data for the selected date range"""
        start_date = self.start_date.date().toString("yyyy-MM-dd")
        end_date = self.end_date.date().toString("yyyy-MM-dd")
        
        # Get sales summary
        summary = get_merchandise_sales_summary(start_date, end_date)
        
        # Update summary labels
        self.total_items_label.setText(f"{summary.get('total_items_sold', 0):,}")
        self.total_revenue_label.setText(f"${summary.get('total_revenue', 0):,.2f}")
        self.total_profit_label.setText(f"${summary.get('total_profit', 0):,.2f}")
        self.company_profit_label.setText(f"${summary.get('total_company_profit', 0):,.2f}")
        self.wrestler_profit_label.setText(f"${summary.get('total_wrestler_profit', 0):,.2f}")
        
        # Update top items table
        items = summary.get('top_selling_items', [])
        self.items_table.setRowCount(len(items))
        
        for i, item in enumerate(items):
            # Item name
            name_item = QTableWidgetItem(item['name'])
            self.items_table.setItem(i, 0, name_item)
            
            # Type
            type_item = QTableWidgetItem(item['type'])
            self.items_table.setItem(i, 1, type_item)
            
            # Wrestler
            wrestler_item = QTableWidgetItem(item['wrestler_name'])
            self.items_table.setItem(i, 2, wrestler_item)
            
            # Total sold
            sold_item = QTableWidgetItem(f"{item['total_sold']:,}")
            sold_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.items_table.setItem(i, 3, sold_item)
            
            # Revenue
            revenue_item = QTableWidgetItem(f"${item['total_revenue']:,.2f}")
            revenue_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.items_table.setItem(i, 4, revenue_item)
            
            # Profit
            profit_item = QTableWidgetItem(f"${item['total_profit']:,.2f}")
            profit_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.items_table.setItem(i, 5, profit_item)
        
        # Update top wrestlers table
        wrestlers = summary.get('top_selling_wrestlers', [])
        self.wrestlers_table.setRowCount(len(wrestlers))
        
        for i, wrestler in enumerate(wrestlers):
            # Wrestler name
            name_item = QTableWidgetItem(wrestler['wrestler_name'])
            self.wrestlers_table.setItem(i, 0, name_item)
            
            # Total sold
            sold_item = QTableWidgetItem(f"{wrestler['total_sold']:,}")
            sold_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.wrestlers_table.setItem(i, 1, sold_item)
            
            # Revenue
            revenue_item = QTableWidgetItem(f"${wrestler['total_revenue']:,.2f}")
            revenue_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.wrestlers_table.setItem(i, 2, revenue_item)
            
            # Profit
            profit_item = QTableWidgetItem(f"${wrestler['total_profit']:,.2f}")
            profit_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.wrestlers_table.setItem(i, 3, profit_item)
    
    def load_wrestlers(self):
        """Load all wrestlers for the auto-generate dropdown"""
        try:
            # Get all wrestlers
            self.all_wrestlers = business_db.get_all_wrestlers()
            
            # Clear and re-populate wrestler dropdown
            self.wrestler_combo.clear()
            self.wrestler_combo.addItem("All Wrestlers", None)
            
            for wrestler in self.all_wrestlers:
                self.wrestler_combo.addItem(wrestler['name'], wrestler['id'])
                
        except Exception as e:
            logging.error(f"Error loading wrestlers: {e}")
    
    def apply_filter(self):
        """Apply the selected filter to the roster list"""
        # Clear existing widgets
        for i in reversed(range(self.roster_layout.count())):
            widget = self.roster_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        
        filter_type = self.filter_combo.currentText()
        
        # Create a frame for each wrestler
        for wrestler in self.all_wrestlers:
            # Apply filter
            if filter_type == "Has Merchandise" and not wrestler.get('has_merchandise', False):
                continue
            elif filter_type == "No Merchandise" and wrestler.get('has_merchandise', True):
                continue
            
            wrestler_frame = QFrame()
            wrestler_frame.setFrameShape(QFrame.StyledPanel)
            wrestler_frame.setFrameShadow(QFrame.Raised)
            
            frame_layout = QHBoxLayout()
            
            # Wrestler name
            name_label = QLabel(wrestler['name'])
            font = name_label.font()
            font.setBold(True)
            name_label.setFont(font)
            frame_layout.addWidget(name_label)
            
            # Popularity
            popularity_label = QLabel(f"Popularity: {wrestler.get('popularity', 'N/A')}")
            frame_layout.addWidget(popularity_label)
            
            frame_layout.addStretch()
            
            # View merch button
            view_btn = QPushButton("View Merchandise")
            view_btn.clicked.connect(lambda checked, w=wrestler: self.view_wrestler_merchandise(w))
            frame_layout.addWidget(view_btn)
            
            # Generate merch button
            gen_btn = QPushButton("Auto-Generate")
            gen_btn.clicked.connect(lambda checked, w=wrestler: self.auto_generate_for_wrestler(w))
            frame_layout.addWidget(gen_btn)
            
            wrestler_frame.setLayout(frame_layout)
            self.roster_layout.addWidget(wrestler_frame)
        
        # Add a stretch at the end
        self.roster_layout.addStretch()
    
    def view_wrestler_merchandise(self, wrestler):
        """Open the merchandise UI for a specific wrestler"""
        if self.current_wrestler_window:
            self.current_wrestler_window.close()
        
        self.current_wrestler_window = WrestlerMerchandiseUI(wrestler['id'], wrestler['name'])
        self.current_wrestler_window.closed.connect(self.load_wrestlers)
        self.current_wrestler_window.show()
    
    def auto_generate_for_wrestler(self):
        """Auto-generate merchandise for a specific wrestler"""
        try:
            # Get selected wrestler
            index = self.wrestler_combo.currentIndex()
            if index <= 0:  # "All wrestlers" is index 0
                return
                
            wrestler_id = self.wrestler_combo.itemData(index)
            wrestler_name = self.wrestler_combo.itemText(index)
            
            # Generate merchandise
            success = business_db.auto_manage_merchandise(wrestler_id)
            
            if success:
                QMessageBox.information(
                    self, 
                    "Success", 
                    f"Successfully auto-generated merchandise for {wrestler_name}"
                )
                self.load_sales_summary()
            else:
                QMessageBox.warning(
                    self, 
                    "Error", 
                    f"Failed to auto-generate merchandise for {wrestler_name}"
                )
                
        except Exception as e:
            logging.error(f"Error auto-generating merchandise: {e}")
            QMessageBox.critical(
                self, 
                "Error", 
                f"An error occurred: {str(e)}"
            )

    def auto_generate_for_all(self):
        """Auto-generate merchandise for all wrestlers"""
        try:
            # Generate merchandise for all
            success = business_db.auto_manage_merchandise()
            
            if success:
                QMessageBox.information(
                    self, 
                    "Success", 
                    "Successfully auto-generated merchandise for all wrestlers"
                )
                self.load_sales_summary()
            else:
                QMessageBox.warning(
                    self, 
                    "Error", 
                    "Failed to auto-generate merchandise"
                )
                
        except Exception as e:
            logging.error(f"Error auto-generating merchandise: {e}")
            QMessageBox.critical(
                self, 
                "Error", 
                f"An error occurred: {str(e)}"
            )

    def load_sales_summary(self):
        """Load merchandise sales summary"""
        try:
            # Get date range
            start_date = self.start_date.date().toPyDate()
            end_date = self.end_date.date().toPyDate()
            
            # Get sales summary
            sales_summary = business_db.get_merchandise_sales_summary(start_date, end_date)
            
            # Clear and set up table
            self.sales_table.setRowCount(len(sales_summary))
            
            for i, item in enumerate(sales_summary):
                self.sales_table.setItem(i, 0, QTableWidgetItem(item['name']))
                self.sales_table.setItem(i, 1, QTableWidgetItem(item['wrestler_name']))
                self.sales_table.setItem(i, 2, QTableWidgetItem(item['type']))
                
                quality_item = QTableWidgetItem(str(item['overall_quality']))
                quality_item.setTextAlignment(Qt.AlignCenter)
                self.sales_table.setItem(i, 3, quality_item)
                
                units_item = QTableWidgetItem(str(item['units_sold']))
                units_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.sales_table.setItem(i, 4, units_item)
                
                revenue_item = QTableWidgetItem(f"${item['total_revenue']:,.2f}")
                revenue_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.sales_table.setItem(i, 5, revenue_item)
                
                profit_item = QTableWidgetItem(f"${item['total_profit']:,.2f}")
                profit_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                profit_item.setForeground(QColor("#2ecc71"))  # Green
                self.sales_table.setItem(i, 6, profit_item)
                
                wrestler_revenue_item = QTableWidgetItem(f"${item['wrestler_revenue']:,.2f}")
                wrestler_revenue_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.sales_table.setItem(i, 7, wrestler_revenue_item)
            
        except Exception as e:
            logging.error(f"Error loading sales summary: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MerchandiseManagerUI()
    window.show()
    sys.exit(app.exec_()) 