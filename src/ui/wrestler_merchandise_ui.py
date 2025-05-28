from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QTableWidget, QTableWidgetItem,
    QMessageBox, QDialog, QFormLayout, QLineEdit,
    QComboBox, QSpinBox, QHeaderView, QApplication,
    QDoubleSpinBox
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor, QFont
import logging
from datetime import datetime
from src.db.business_db_manager import BusinessDBManager

# Create a business database manager instance
business_db = BusinessDBManager()

class MerchandiseItemDialog(QDialog):
    """Dialog for creating or editing a merchandise item"""
    def __init__(self, wrestler_id, wrestler_name, item=None, parent=None):
        super().__init__(parent)
        self.wrestler_id = wrestler_id
        self.wrestler_name = wrestler_name
        self.item = item
        
        self.setWindowTitle("Merchandise Item" if item else "New Merchandise Item")
        self.setMinimumWidth(400)
        
        self.init_ui()
        
    def init_ui(self):
        layout = QFormLayout()
        
        # Name field
        self.name_edit = QLineEdit()
        if self.item:
            self.name_edit.setText(self.item['name'])
        else:
            self.name_edit.setText(f"{self.wrestler_name} ")
        layout.addRow("Name:", self.name_edit)
        
        # Type selector
        self.type_combo = QComboBox()
        self.type_combo.addItems([
            "T-Shirt",
            "Premium T-Shirt",
            "Hat",
            "Poster",
            "Action Figure", 
            "Championship Replica",
            "Mug",
            "Wristband"
        ])
        
        if self.item:
            index = self.type_combo.findText(self.item['type'])
            if index >= 0:
                self.type_combo.setCurrentIndex(index)
        layout.addRow("Type:", self.type_combo)
        
        # Price field
        self.price_spin = QDoubleSpinBox()
        self.price_spin.setRange(0.99, 499.99)
        self.price_spin.setDecimals(2)
        self.price_spin.setSingleStep(0.99)
        self.price_spin.setPrefix("$")
        
        if self.item:
            self.price_spin.setValue(self.item['base_price'])
        else:
            # Default price based on type
            self.type_combo.currentIndexChanged.connect(self.update_default_price)
            self.update_default_price()
            
        layout.addRow("Price:", self.price_spin)
        
        # If editing an existing item, show the stats
        if self.item:
            # Design quality
            design_label = QLabel(f"{self.item['design_quality']}/100")
            layout.addRow("Design Quality:", design_label)
            
            # Material quality
            material_label = QLabel(f"{self.item['material_quality']}/100")
            layout.addRow("Material Quality:", material_label)
            
            # Uniqueness
            uniqueness_label = QLabel(f"{self.item['uniqueness']}/100")
            layout.addRow("Uniqueness:", uniqueness_label)
            
            # Fan appeal
            appeal_label = QLabel(f"{self.item['fan_appeal']}/100")
            layout.addRow("Fan Appeal:", appeal_label)
            
            # Overall quality
            overall_label = QLabel(f"{self.item['overall_quality']}/100")
            font = overall_label.font()
            font.setBold(True)
            overall_label.setFont(font)
            layout.addRow("Overall Quality:", overall_label)
            
            # Revenue split
            self.company_split = QSpinBox()
            self.company_split.setRange(50, 100)
            self.company_split.setSingleStep(5)
            self.company_split.setSuffix("%")
            self.company_split.setValue(int(self.item['company_split']))
            self.company_split.valueChanged.connect(self.update_wrestler_split)
            layout.addRow("Company Split:", self.company_split)
            
            self.wrestler_split = QSpinBox()
            self.wrestler_split.setRange(0, 50)
            self.wrestler_split.setSingleStep(5)
            self.wrestler_split.setSuffix("%")
            self.wrestler_split.setValue(int(self.item['wrestler_split']))
            self.wrestler_split.valueChanged.connect(self.update_company_split)
            layout.addRow("Wrestler Split:", self.wrestler_split)
            
            # Status selector
            self.status_combo = QComboBox()
            self.status_combo.addItems(["active", "discontinued"])
            index = self.status_combo.findText(self.item['status'])
            if index >= 0:
                self.status_combo.setCurrentIndex(index)
            layout.addRow("Status:", self.status_combo)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)
        
        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(self.accept)
        self.save_btn.setDefault(True)
        button_layout.addWidget(self.save_btn)
        
        layout.addRow("", button_layout)
        
        self.setLayout(layout)
    
    def update_default_price(self):
        """Update the default price based on the selected type"""
        merch_type = self.type_combo.currentText()
        
        default_prices = {
            'T-Shirt': 24.99,
            'Premium T-Shirt': 29.99,
            'Hat': 19.99,
            'Poster': 14.99,
            'Action Figure': 29.99,
            'Championship Replica': 299.99,
            'Mug': 12.99,
            'Wristband': 9.99
        }
        
        if merch_type in default_prices:
            self.price_spin.setValue(default_prices[merch_type])
        else:
            self.price_spin.setValue(19.99)
    
    def update_wrestler_split(self, value):
        """Update wrestler split when company split changes"""
        if hasattr(self, 'wrestler_split'):
            self.wrestler_split.setValue(100 - value)
    
    def update_company_split(self, value):
        """Update company split when wrestler split changes"""
        if hasattr(self, 'company_split'):
            self.company_split.setValue(100 - value)
    
    def get_values(self):
        """Get the values entered in the dialog"""
        result = {
            'name': self.name_edit.text(),
            'type': self.type_combo.currentText(),
            'base_price': self.price_spin.value()
        }
        
        if self.item:
            result['status'] = self.status_combo.currentText()
            result['company_split'] = self.company_split.value()
            result['wrestler_split'] = self.wrestler_split.value()
        
        return result

class WrestlerMerchandiseUI(QWidget):
    """UI for managing a wrestler's merchandise"""
    
    closed = pyqtSignal()
    
    def __init__(self, wrestler_id, wrestler_name, parent=None):
        super().__init__(parent)
        self.wrestler_id = wrestler_id
        self.wrestler_name = wrestler_name
        
        self.setWindowTitle(f"{wrestler_name} - Merchandise")
        self.setMinimumSize(800, 500)
        
        self.init_ui()
        self.load_merchandise()
    
    def init_ui(self):
        """Initialize the UI"""
        main_layout = QVBoxLayout()
        
        # Header
        header_layout = QHBoxLayout()
        title = QLabel(f"Merchandise for {self.wrestler_name}")
        title.setStyleSheet("font-size: 16pt; font-weight: bold;")
        header_layout.addWidget(title)
        
        # Summary section
        summary_layout = QHBoxLayout()
        self.sales_label = QLabel("Total Sales: 0 units")
        self.revenue_label = QLabel("Total Revenue: $0.00")
        self.wrestler_revenue_label = QLabel("Wrestler's Revenue: $0.00")
        
        summary_layout.addWidget(self.sales_label)
        summary_layout.addWidget(self.revenue_label)
        summary_layout.addWidget(self.wrestler_revenue_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        # Add item button
        add_btn = QPushButton("Add Item")
        add_btn.clicked.connect(self.add_merchandise)
        button_layout.addWidget(add_btn)
        
        # Auto-generate button
        auto_btn = QPushButton("Auto-Generate")
        auto_btn.clicked.connect(self.auto_generate)
        button_layout.addWidget(auto_btn)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        button_layout.addWidget(close_btn)
        
        # Table
        self.merch_table = QTableWidget()
        self.merch_table.setColumnCount(7)
        self.merch_table.setHorizontalHeaderLabels([
            "Name", "Type", "Quality", "Sales", "Revenue", "Wrestler's Cut", "Status"
        ])
        self.merch_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.merch_table.verticalHeader().setVisible(False)
        self.merch_table.setSelectionBehavior(QTableWidget.SelectRows)
        
        # Layout
        main_layout.addLayout(header_layout)
        main_layout.addLayout(summary_layout)
        main_layout.addWidget(self.merch_table)
        main_layout.addLayout(button_layout)
        
        self.setLayout(main_layout)
        self.resize(800, 500)
        
        # Load data
        self.load_merchandise()
    
    def load_merchandise(self):
        """Load the wrestler's merchandise items"""
        try:
            # Get the wrestler's merchandise
            items = business_db.get_wrestler_merchandise(self.wrestler_id)
            
            # Clear the table
            self.merch_table.setRowCount(0)
            
            # Add items to the table
            if items:
                self.merch_table.setRowCount(len(items))
                
                for i, item in enumerate(items):
                    # Item name
                    name_item = QTableWidgetItem(item['name'])
                    self.merch_table.setItem(i, 0, name_item)
                    
                    # Item type
                    type_item = QTableWidgetItem(item['type'])
                    self.merch_table.setItem(i, 1, type_item)
                    
                    # Quality rating (star-based)
                    quality_item = QTableWidgetItem(f"★ {item['overall_quality']}")
                    quality_item.setTextAlignment(Qt.AlignCenter)
                    quality_color = self.get_quality_color(item['overall_quality'])
                    quality_item.setForeground(QColor(quality_color))
                    self.merch_table.setItem(i, 2, quality_item)
                    
                    # Sales
                    sales_item = QTableWidgetItem(str(item.get('units_sold', 0)))
                    sales_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                    self.merch_table.setItem(i, 3, sales_item)
                    
                    # Revenue
                    revenue = item.get('total_revenue', 0)
                    revenue_item = QTableWidgetItem(f"${revenue:,.2f}")
                    revenue_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                    self.merch_table.setItem(i, 4, revenue_item)
                    
                    # Wrestler's cut
                    wrestler_revenue = item.get('wrestler_revenue', 0)
                    wrestler_revenue_item = QTableWidgetItem(f"${wrestler_revenue:,.2f}")
                    wrestler_revenue_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                    self.merch_table.setItem(i, 5, wrestler_revenue_item)
                    
                    # Status
                    status_item = QTableWidgetItem(item['status'])
                    status_item.setTextAlignment(Qt.AlignCenter)
                    self.merch_table.setItem(i, 6, status_item)
            
            # Update summary
            total_sales = sum(item.get('units_sold', 0) for item in items)
            total_revenue = sum(item.get('total_revenue', 0) for item in items)
            wrestler_revenue = sum(item.get('wrestler_revenue', 0) for item in items)
            
            self.sales_label.setText(f"Total Sales: {total_sales} units")
            self.revenue_label.setText(f"Total Revenue: ${total_revenue:,.2f}")
            self.wrestler_revenue_label.setText(f"Wrestler's Revenue: ${wrestler_revenue:,.2f}")
            
        except Exception as e:
            print(f"Error loading merchandise: {e}")
            logging.error(f"Error loading merchandise: {e}")
    
    def add_merchandise(self):
        """Show dialog to add a new merchandise item"""
        dialog = MerchandiseItemDialog(self.wrestler_id, self.wrestler_name)
        if dialog.exec_():
            # Create merchandise item
            data = dialog.get_values()
            try:
                business_db.create_merchandise_item(
                    wrestler_id=self.wrestler_id,
                    name=data['name'],
                    merch_type=data['type'],
                    base_price=data['base_price'],
                    production_cost=data['production_cost'],
                    design_quality=data['design_quality'],
                    material_quality=data['material_quality'],
                    uniqueness=data['uniqueness'],
                    fan_appeal=data['fan_appeal']
                )
                self.load_merchandise()
            except Exception as e:
                logging.error(f"Error creating merchandise: {e}")
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to create merchandise: {str(e)}"
                )
    
    def auto_generate(self):
        """Auto-generate merchandise for this wrestler"""
        reply = QMessageBox.question(
            self,
            "Confirm Auto-Generate",
            f"Auto-generate merchandise for {self.wrestler_name}? This will create new items based on their popularity level.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                success = business_db.auto_manage_merchandise(self.wrestler_id)
                
                if success:
                    QMessageBox.information(
                        self, 
                        "Success", 
                        f"Auto-generated merchandise for {self.wrestler_name}"
                    )
                    self.load_merchandise()
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
    
    def closeEvent(self, event):
        """Emit closed signal when the window is closed"""
        self.closed.emit()
        super().closeEvent(event)

    def get_quality_color(self, quality):
        """Get a color for a quality rating"""
        if quality >= 5:
            return "#2ecc71"  # Green
        elif quality >= 4:
            return "#27ae60"  # Darker green
        elif quality >= 3:
            return "#f39c12"  # Orange
        elif quality >= 2:
            return "#e67e22"  # Darker orange
        else:
            return "#e74c3c"  # Red

if __name__ == "__main__":
    app = QApplication(sys.argv)
    # Example usage with sample data
    window = WrestlerMerchandiseUI(1, "Test Wrestler")
    window.show()
    sys.exit(app.exec_()) 