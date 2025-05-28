from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QTableWidget, QTableWidgetItem,
    QComboBox, QSpinBox, QDoubleSpinBox, QDateEdit,
    QTabWidget, QGroupBox, QFormLayout, QDialog, QLineEdit
)
from PyQt5.QtCore import Qt, QDate
from datetime import datetime, timedelta
import logging
from src.db.business_db_manager import BusinessDBManager

# Create a business database manager instance
business_db = BusinessDBManager()

class BusinessDashboard(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        """Initialize the UI components"""
        layout = QVBoxLayout()
        
        # Create tab widget
        tabs = QTabWidget()
        
        # Financial Overview Tab
        financial_tab = QWidget()
        financial_layout = QVBoxLayout()
        
        # Financial Summary
        summary_group = QGroupBox("Financial Summary")
        summary_layout = QFormLayout()
        
        self.revenue_label = QLabel("$0")
        self.expenses_label = QLabel("$0")
        self.profit_label = QLabel("$0")
        
        summary_layout.addRow("Total Revenue:", self.revenue_label)
        summary_layout.addRow("Total Expenses:", self.expenses_label)
        summary_layout.addRow("Net Profit:", self.profit_label)
        
        summary_group.setLayout(summary_layout)
        financial_layout.addWidget(summary_group)
        
        # Recent Transactions
        transactions_group = QGroupBox("Recent Transactions")
        transactions_layout = QVBoxLayout()
        
        self.transactions_table = QTableWidget()
        self.transactions_table.setColumnCount(5)
        self.transactions_table.setHorizontalHeaderLabels([
            "Date", "Type", "Category", "Amount", "Description"
        ])
        
        transactions_layout.addWidget(self.transactions_table)
        transactions_group.setLayout(transactions_layout)
        financial_layout.addWidget(transactions_group)
        
        financial_tab.setLayout(financial_layout)
        tabs.addTab(financial_tab, "Financial Overview")
        
        # Shows Tab
        shows_tab = QWidget()
        shows_layout = QVBoxLayout()
        
        # Upcoming Shows
        upcoming_group = QGroupBox("Upcoming Shows")
        upcoming_layout = QVBoxLayout()
        
        self.shows_table = QTableWidget()
        self.shows_table.setColumnCount(6)
        self.shows_table.setHorizontalHeaderLabels([
            "Date", "Name", "Type", "Venue", "Budget", "Status"
        ])
        
        upcoming_layout.addWidget(self.shows_table)
        upcoming_group.setLayout(upcoming_layout)
        shows_layout.addWidget(upcoming_group)
        
        # Add Show Button
        add_show_btn = QPushButton("Add New Show")
        add_show_btn.clicked.connect(self.show_add_show_dialog)
        shows_layout.addWidget(add_show_btn)
        
        shows_tab.setLayout(shows_layout)
        tabs.addTab(shows_tab, "Shows")
        
        # Venues Tab
        venues_tab = QWidget()
        venues_layout = QVBoxLayout()
        
        # Venues List
        venues_group = QGroupBox("Available Venues")
        venues_layout_inner = QVBoxLayout()
        
        self.venues_table = QTableWidget()
        self.venues_table.setColumnCount(5)
        self.venues_table.setHorizontalHeaderLabels([
            "Name", "Capacity", "Base Cost", "Location", "Prestige"
        ])
        
        venues_layout_inner.addWidget(self.venues_table)
        venues_group.setLayout(venues_layout_inner)
        venues_layout.addWidget(venues_group)
        
        venues_tab.setLayout(venues_layout)
        tabs.addTab(venues_tab, "Venues")
        
        # Contracts Tab
        contracts_tab = QWidget()
        contracts_layout = QVBoxLayout()
        
        # Active Contracts
        contracts_group = QGroupBox("Active Contracts")
        contracts_table_layout = QVBoxLayout()
        
        self.contracts_table = QTableWidget()
        self.contracts_table.setColumnCount(5)
        self.contracts_table.setHorizontalHeaderLabels([
            "Wrestler", "Start Date", "End Date", "Salary", "Status"
        ])
        
        contracts_table_layout.addWidget(self.contracts_table)
        contracts_group.setLayout(contracts_table_layout)
        contracts_layout.addWidget(contracts_group)
        
        # TV Deals
        tv_deals_group = QGroupBox("TV Deals")
        tv_deals_layout = QVBoxLayout()
        
        self.tv_deals_table = QTableWidget()
        self.tv_deals_table.setColumnCount(5)
        self.tv_deals_table.setHorizontalHeaderLabels([
            "Network", "Show", "Payment", "Start Date", "End Date"
        ])
        
        tv_deals_layout.addWidget(self.tv_deals_table)
        
        # Add TV Deal Button
        add_tv_deal_btn = QPushButton("Add New TV Deal")
        add_tv_deal_btn.clicked.connect(self.show_add_tv_deal_dialog)
        tv_deals_layout.addWidget(add_tv_deal_btn)
        
        tv_deals_group.setLayout(tv_deals_layout)
        contracts_layout.addWidget(tv_deals_group)
        
        contracts_tab.setLayout(contracts_layout)
        tabs.addTab(contracts_tab, "Contracts")
        
        layout.addWidget(tabs)
        self.setLayout(layout)
        
        # Initial data load
        self.refresh_data()

    def refresh_data(self):
        """Refresh all data in the dashboard"""
        self.refresh_financial_summary()
        self.refresh_transactions()
        self.refresh_shows()
        self.refresh_venues()
        self.refresh_contracts()
        self.refresh_tv_deals()

    def refresh_financial_summary(self):
        """Update financial summary information"""
        try:
            # Get current month's data
            today = datetime.now()
            start_date = datetime(today.year, today.month, 1)
            end_date = (start_date + timedelta(days=32)).replace(day=1) - timedelta(days=1)
            
            summary = business_db.get_financial_summary(start_date, end_date)
            
            total_revenue = sum(item['total'] for item in summary if item['transaction_type'] == 'income')
            total_expenses = sum(abs(item['total']) for item in summary if item['transaction_type'] == 'expense')
            
            self.revenue_label.setText(f"${total_revenue:,.2f}")
            self.expenses_label.setText(f"${total_expenses:,.2f}")
            self.profit_label.setText(f"${total_revenue - total_expenses:,.2f}")
        except Exception as e:
            logging.error(f"Error refreshing financial summary: {e}")

    def refresh_transactions(self):
        """Update transactions table"""
        try:
            # Get recent transactions
            transactions = business_db.get_recent_transactions(limit=50)
            
            self.transactions_table.setRowCount(len(transactions))
            for i, trans in enumerate(transactions):
                self.transactions_table.setItem(i, 0, QTableWidgetItem(str(trans['transaction_date'])))
                self.transactions_table.setItem(i, 1, QTableWidgetItem(trans['transaction_type']))
                self.transactions_table.setItem(i, 2, QTableWidgetItem(trans['category']))
                self.transactions_table.setItem(i, 3, QTableWidgetItem(f"${trans['amount']:,.2f}"))
                self.transactions_table.setItem(i, 4, QTableWidgetItem(trans['description']))
        except Exception as e:
            logging.error(f"Error refreshing transactions: {e}")

    def refresh_shows(self):
        """Update shows table"""
        try:
            # Get upcoming shows
            shows = business_db.get_upcoming_shows(limit=50)
            
            self.shows_table.setRowCount(len(shows))
            for i, show in enumerate(shows):
                self.shows_table.setItem(i, 0, QTableWidgetItem(str(show['date'])))
                self.shows_table.setItem(i, 1, QTableWidgetItem(show['name']))
                self.shows_table.setItem(i, 2, QTableWidgetItem(show['show_type']))
                self.shows_table.setItem(i, 3, QTableWidgetItem(show['venue_name']))
                self.shows_table.setItem(i, 4, QTableWidgetItem(f"${show['budget']:,.2f}"))
                self.shows_table.setItem(i, 5, QTableWidgetItem(show['status']))
        except Exception as e:
            logging.error(f"Error refreshing shows: {e}")

    def refresh_venues(self):
        """Update venues table"""
        try:
            # Get all venues
            venues = business_db.get_all_venues()
            
            self.venues_table.setRowCount(len(venues))
            for i, venue in enumerate(venues):
                self.venues_table.setItem(i, 0, QTableWidgetItem(venue['name']))
                self.venues_table.setItem(i, 1, QTableWidgetItem(str(venue['capacity'])))
                self.venues_table.setItem(i, 2, QTableWidgetItem(f"${venue['base_cost']:,.2f}"))
                self.venues_table.setItem(i, 3, QTableWidgetItem(venue['location']))
                self.venues_table.setItem(i, 4, QTableWidgetItem(str(venue['prestige'])))
        except Exception as e:
            logging.error(f"Error refreshing venues: {e}")

    def refresh_contracts(self):
        """Update contracts table"""
        try:
            # Get active contracts
            contracts = business_db.get_active_contracts()
            
            self.contracts_table.setRowCount(len(contracts))
            for i, contract in enumerate(contracts):
                self.contracts_table.setItem(i, 0, QTableWidgetItem(contract['wrestler_name']))
                self.contracts_table.setItem(i, 1, QTableWidgetItem(str(contract['start_date'])))
                self.contracts_table.setItem(i, 2, QTableWidgetItem(str(contract['end_date'])))
                self.contracts_table.setItem(i, 3, QTableWidgetItem(f"${contract['base_salary']:,.2f}"))
                self.contracts_table.setItem(i, 4, QTableWidgetItem(contract['status']))
        except Exception as e:
            logging.error(f"Error refreshing contracts: {e}")

    def refresh_tv_deals(self):
        """Update TV deals table"""
        try:
            # Get active TV deals
            deals = business_db.get_active_tv_deals()
            
            self.tv_deals_table.setRowCount(len(deals))
            for i, deal in enumerate(deals):
                self.tv_deals_table.setItem(i, 0, QTableWidgetItem(deal['network_name']))
                self.tv_deals_table.setItem(i, 1, QTableWidgetItem(deal['show_name']))
                self.tv_deals_table.setItem(i, 2, QTableWidgetItem(f"${deal['weekly_payment']:,.2f}/week"))
                self.tv_deals_table.setItem(i, 3, QTableWidgetItem(str(deal['start_date'])))
                self.tv_deals_table.setItem(i, 4, QTableWidgetItem(str(deal['end_date'])))
        except Exception as e:
            logging.error(f"Error refreshing TV deals: {e}")

    def show_add_show_dialog(self):
        """Show dialog to add a new show"""
        dialog = AddShowDialog(self)
        if dialog.exec_():
            self.refresh_shows()

    def show_add_tv_deal_dialog(self):
        """Show dialog to add a new TV deal"""
        dialog = AddTVDealDialog(self)
        if dialog.exec_():
            self.refresh_tv_deals()


class AddShowDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.venues = business_db.get_all_venues()
        self.init_ui()

    def init_ui(self):
        """Initialize the dialog UI"""
        self.setWindowTitle("Add New Show")
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout()
        
        # Show details form
        form_layout = QFormLayout()
        
        # Name
        self.name_edit = QLineEdit()
        form_layout.addRow("Show Name:", self.name_edit)
        
        # Type
        self.type_combo = QComboBox()
        self.type_combo.addItems(["weekly", "ppv", "special"])
        self.type_combo.currentIndexChanged.connect(self.update_budget_estimate)
        form_layout.addRow("Show Type:", self.type_combo)
        
        # Date
        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.currentDate().addDays(7))  # Default to 1 week from now
        self.date_edit.setCalendarPopup(True)
        form_layout.addRow("Show Date:", self.date_edit)
        
        # Venue
        self.venue_combo = QComboBox()
        for venue in self.venues:
            self.venue_combo.addItem(venue['name'], venue['id'])
        self.venue_combo.currentIndexChanged.connect(self.update_budget_estimate)
        form_layout.addRow("Venue:", self.venue_combo)
        
        # Production Level
        self.production_level = QSpinBox()
        self.production_level.setMinimum(1)
        self.production_level.setMaximum(10)
        self.production_level.setValue(5)
        self.production_level.valueChanged.connect(self.update_budget_estimate)
        form_layout.addRow("Production Level (1-10):", self.production_level)
        
        # Budget (read-only, calculated)
        self.budget_label = QLabel("$0")
        form_layout.addRow("Estimated Budget:", self.budget_label)
        
        # Expected attendance
        self.attendance_label = QLabel("0")
        form_layout.addRow("Expected Attendance:", self.attendance_label)
        
        # Estimated revenue
        self.revenue_label = QLabel("$0")
        form_layout.addRow("Estimated Revenue:", self.revenue_label)
        
        # Estimated profit
        self.profit_label = QLabel("$0")
        form_layout.addRow("Estimated Profit:", self.profit_label)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        create_btn = QPushButton("Create Show")
        create_btn.clicked.connect(self.create_show)
        button_layout.addWidget(create_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # Initial calculation
        self.update_budget_estimate()

    def update_budget_estimate(self):
        """Update the budget estimate based on current selections"""
        try:
            # Get selected venue
            venue_id = self.venue_combo.currentData()
            venue = next((v for v in self.venues if v['id'] == venue_id), None)
            
            if not venue:
                return
            
            # Get show type and production level
            show_type = self.type_combo.currentText()
            production_level = self.production_level.value()
            
            # Calculate venue cost
            venue_cost = calculate_venue_cost(venue, show_type)
            
            # Calculate budget
            from src.core.business_utils import calculate_show_budget
            budget = calculate_show_budget(show_type, venue_cost, production_level)
            
            # Update budget label
            self.budget_label.setText(f"${budget:,.2f}")
            
            # Calculate expected attendance and revenue
            wrestler_popularity = 50  # Assume average popularity for now
            
            # Get estimated profit
            profit_estimate = estimate_show_profit(show_type, venue, wrestler_popularity, production_level)
            
            # Update labels
            expected_attendance = calculate_expected_attendance(venue, show_type, wrestler_popularity)
            self.attendance_label.setText(f"{expected_attendance:,}")
            self.revenue_label.setText(f"${profit_estimate['revenue']:,.2f}")
            self.profit_label.setText(f"${profit_estimate['profit']:,.2f}")
            
        except Exception as e:
            logging.error(f"Error updating budget estimate: {e}")

    def create_show(self):
        """Create a new show based on form data"""
        name = self.name_edit.text()
        show_type = self.type_combo.currentText()
        date = self.date_edit.date().toString("yyyy-MM-dd")
        venue_id = self.venue_combo.currentData()
        budget = float(self.budget_label.text().replace('$', '').replace(',', ''))
        
        try:
            # Create the show
            show_id = business_db.create_show(name, show_type, date, venue_id, budget)
            
            if show_id:
                # Record the initial expense
                business_db.record_transaction(
                    amount=-budget,
                    category="show_budget",
                    description=f"Budget allocation for {name}",
                    transaction_type="expense",
                    show_id=show_id
                )
                
                # Initialize event financial impact record
                business_db.create_event_financial_impact(
                    show_id=show_id,
                    production_costs=budget  # Initial budget as production costs
                )
                
                logging.info(f"Created new show: {name} on {date}")
                self.accept()
            else:
                logging.error("Failed to create show: no ID returned")
        except Exception as e:
            logging.error(f"Error creating show: {e}")


class AddTVDealDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        """Initialize the dialog UI"""
        self.setWindowTitle("Add New TV Deal")
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout()
        
        # TV deal form
        form_layout = QFormLayout()
        
        # Network name
        self.network_edit = QLineEdit()
        form_layout.addRow("Network Name:", self.network_edit)
        
        # Show name
        self.show_edit = QLineEdit()
        form_layout.addRow("Show Name:", self.show_edit)
        
        # Weekly payment
        self.payment_spin = QDoubleSpinBox()
        self.payment_spin.setMinimum(10000)
        self.payment_spin.setMaximum(1000000)
        self.payment_spin.setValue(50000)
        self.payment_spin.setSingleStep(5000)
        self.payment_spin.setPrefix("$")
        self.payment_spin.setSuffix(" /week")
        form_layout.addRow("Weekly Payment:", self.payment_spin)
        
        # Rating bonus
        self.bonus_spin = QDoubleSpinBox()
        self.bonus_spin.setMinimum(0)
        self.bonus_spin.setMaximum(100000)
        self.bonus_spin.setValue(5000)
        self.bonus_spin.setSingleStep(1000)
        self.bonus_spin.setPrefix("$")
        self.bonus_spin.setSuffix(" per 0.1 rating")
        form_layout.addRow("Rating Bonus:", self.bonus_spin)
        
        # Start date
        self.start_date_edit = QDateEdit()
        self.start_date_edit.setDate(QDate.currentDate())
        self.start_date_edit.setCalendarPopup(True)
        form_layout.addRow("Start Date:", self.start_date_edit)
        
        # End date
        self.end_date_edit = QDateEdit()
        self.end_date_edit.setDate(QDate.currentDate().addYears(1))
        self.end_date_edit.setCalendarPopup(True)
        form_layout.addRow("End Date:", self.end_date_edit)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        create_btn = QPushButton("Create TV Deal")
        create_btn.clicked.connect(self.create_tv_deal)
        button_layout.addWidget(create_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)

    def create_tv_deal(self):
        """Create a new TV deal"""
        network_name = self.network_edit.text()
        show_name = self.show_edit.text()
        start_date = self.start_date_edit.date().toString("yyyy-MM-dd")
        end_date = self.end_date_edit.date().toString("yyyy-MM-dd")
        weekly_payment = self.payment_spin.value()
        rating_bonus = self.bonus_spin.value()
        
        try:
            # Create the TV deal
            deal_id = business_db.create_tv_deal(
                network_name, show_name, start_date, end_date, weekly_payment, rating_bonus
            )
            
            if deal_id:
                logging.info(f"Created TV deal with {network_name} for {show_name}")
                self.accept()
            else:
                logging.error("Failed to create TV deal")
        except Exception as e:
            logging.error(f"Error creating TV deal: {e}") 