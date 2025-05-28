from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QTableWidget, QTableWidgetItem,
    QComboBox, QSpinBox, QDoubleSpinBox, QDateEdit,
    QTabWidget, QGroupBox, QFormLayout, QDialog, QLineEdit,
    QSplitter, QFrame, QHeaderView, QGridLayout
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QColor, QPalette, QFont
from datetime import datetime, timedelta
import logging
from src.db.business_db_manager import BusinessDBManager

# Create a business database manager instance
business_db = BusinessDBManager()

class BusinessStatsUI(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        """Initialize the UI components"""
        layout = QVBoxLayout()
        layout.setSpacing(20)
        
        # Header
        header_label = QLabel("Business Performance Dashboard")
        header_font = QFont()
        header_font.setPointSize(18)
        header_font.setBold(True)
        header_label.setFont(header_font)
        header_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(header_label)
        
        # Key performance metrics
        metrics_layout = QGridLayout()
        
        # Get data for metrics
        self.load_data()
        
        # Add metric boxes
        metrics_layout.addWidget(self.create_metric_box("Financial Health", f"{self.financial_health:.1f}/100", 
                                self.get_health_color(self.financial_health)), 0, 0)
        metrics_layout.addWidget(self.create_metric_box("Cash Balance", f"${self.cash_balance:,.2f}", 
                                self.get_cash_color(self.cash_balance)), 0, 1)
        metrics_layout.addWidget(self.create_metric_box("Monthly Income", f"${self.current_month_revenue:,.2f}", 
                                self.get_income_color(self.current_month_revenue, self.current_month_expenses)), 0, 2)
        metrics_layout.addWidget(self.create_metric_box("Monthly Expenses", f"${self.current_month_expenses:,.2f}", 
                                self.get_expense_color(self.current_month_expenses, self.current_month_revenue)), 0, 3)
        metrics_layout.addWidget(self.create_metric_box("Upcoming Shows", str(len(self.upcoming_shows)), 
                                "#3498db"), 1, 0)
        metrics_layout.addWidget(self.create_metric_box("Active Contracts", str(len(self.active_contracts)), 
                                "#9b59b6"), 1, 1)
        metrics_layout.addWidget(self.create_metric_box("Venues", str(len(business_db.get_all_venues())), 
                                "#f39c12"), 1, 2)
        metrics_layout.addWidget(self.create_metric_box("YTD Revenue", f"${sum(item['total'] for item in self.ytd_data if item['transaction_type'] == 'income'):,.2f}", 
                                "#2ecc71"), 1, 3)
        
        layout.addLayout(metrics_layout)
        
        # Financial breakdown
        financial_group = QGroupBox("Financial Breakdown (Last 3 Months)")
        financial_layout = QVBoxLayout()
        
        # Create financial table
        self.financial_table = QTableWidget()
        self.financial_table.setColumnCount(4)
        self.financial_table.setHorizontalHeaderLabels([
            "Category", "Income", "Expenses", "Net"
        ])
        
        # Populate financial table
        self.populate_financial_table()
        
        financial_layout.addWidget(self.financial_table)
        financial_group.setLayout(financial_layout)
        layout.addWidget(financial_group)
        
        # Upcoming shows
        shows_group = QGroupBox("Upcoming Shows")
        shows_layout = QVBoxLayout()
        
        # Create shows table
        self.shows_table = QTableWidget()
        self.shows_table.setColumnCount(5)
        self.shows_table.setHorizontalHeaderLabels([
            "Date", "Name", "Type", "Venue", "Estimated Revenue"
        ])
        
        # Populate shows table
        self.populate_shows_table()
        
        shows_layout.addWidget(self.shows_table)
        shows_group.setLayout(shows_layout)
        layout.addWidget(shows_group)
        
        # Revenue projections
        projection_group = QGroupBox("Revenue Projections (Next 3 Months)")
        projection_layout = QVBoxLayout()
        
        # Monthly projected revenue/expenses
        projection_label = QLabel(self.get_projection_text())
        projection_layout.addWidget(projection_label)
        
        projection_group.setLayout(projection_layout)
        layout.addWidget(projection_group)
        
        # Actions section
        actions_layout = QHBoxLayout()
        
        # Open business dashboard button
        dashboard_btn = QPushButton("Open Business Dashboard")
        dashboard_btn.clicked.connect(self.open_business_dashboard)
        actions_layout.addWidget(dashboard_btn)
        
        # Refresh button
        refresh_btn = QPushButton("Refresh Data")
        refresh_btn.clicked.connect(self.refresh_data)
        actions_layout.addWidget(refresh_btn)
        
        layout.addLayout(actions_layout)
        
        self.setLayout(layout)

    def create_metric_box(self, title, value, color):
        """Create a metric box with title and value"""
        box = QGroupBox(title)
        box.setStyleSheet(f"QGroupBox {{ color: #333; background-color: {color}; border-radius: 5px; }}")
        
        layout = QVBoxLayout()
        
        value_label = QLabel(value)
        value_font = QFont()
        value_font.setPointSize(16)
        value_font.setBold(True)
        value_label.setFont(value_font)
        value_label.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(value_label)
        box.setLayout(layout)
        
        return box

    def load_data(self):
        """Load all business stats data"""
        # Get current month and previous month date ranges
        today = datetime.now()
        
        # Current month
        current_month_start = datetime(today.year, today.month, 1)
        next_month = current_month_start.replace(day=28) + timedelta(days=4)
        current_month_end = next_month - timedelta(days=next_month.day)
        
        # Previous month
        prev_month = (current_month_start - timedelta(days=1)).replace(day=1)
        prev_month_start = prev_month
        prev_month_end = current_month_start - timedelta(days=1)
        
        # Load financial data for current and previous month
        self.current_month_data = business_db.get_financial_summary(
            current_month_start, current_month_end
        )
        
        self.prev_month_data = business_db.get_financial_summary(
            prev_month_start, prev_month_end
        )
        
        # Calculate totals
        self.current_month_revenue = sum(
            item['total'] for item in self.current_month_data 
            if item['transaction_type'] == 'income'
        )
        
        self.current_month_expenses = sum(
            abs(item['total']) for item in self.current_month_data 
            if item['transaction_type'] == 'expense'
        )
        
        self.prev_month_revenue = sum(
            item['total'] for item in self.prev_month_data 
            if item['transaction_type'] == 'income'
        )
        
        self.prev_month_expenses = sum(
            abs(item['total']) for item in self.prev_month_data 
            if item['transaction_type'] == 'expense'
        )
        
        # Get upcoming shows
        self.upcoming_shows = business_db.get_upcoming_shows(limit=5)
        
        # Get active contracts
        self.active_contracts = business_db.get_active_contracts()
        
        # Get all-time financial data for YTD stats
        year_start = datetime(today.year, 1, 1)
        self.ytd_data = business_db.get_financial_summary(year_start, today)
        
        # Calculate cash balance from all transactions
        all_time_data = business_db.get_financial_summary(
            datetime(1990, 1, 1),  # Arbitrary past date
            today
        )
        
        self.cash_balance = sum(item['total'] for item in all_time_data)
        
        # Calculate financial health
        self.financial_health = business_db.calculate_financial_health(
            self.cash_balance,
            self.current_month_revenue,
            self.current_month_expenses
        )

    def get_health_color(self, health):
        """Get color based on financial health score"""
        if health >= 80:
            return "#2ecc71"  # Green
        elif health >= 60:
            return "#27ae60"  # Darker green
        elif health >= 40:
            return "#f39c12"  # Orange
        elif health >= 20:
            return "#e67e22"  # Darker orange
        else:
            return "#e74c3c"  # Red

    def get_cash_color(self, cash):
        """Get color based on cash balance"""
        if cash >= 1000000:
            return "#2ecc71"  # Green
        elif cash >= 500000:
            return "#27ae60"  # Darker green
        elif cash >= 100000:
            return "#f39c12"  # Orange
        elif cash >= 0:
            return "#e67e22"  # Darker orange
        else:
            return "#e74c3c"  # Red

    def get_income_color(self, income, expenses):
        """Get color based on income vs expenses"""
        if income >= expenses * 1.5:
            return "#2ecc71"  # Green
        elif income >= expenses:
            return "#27ae60"  # Darker green
        elif income >= expenses * 0.8:
            return "#f39c12"  # Orange
        elif income >= expenses * 0.5:
            return "#e67e22"  # Darker orange
        else:
            return "#e74c3c"  # Red

    def get_expense_color(self, expenses, income):
        """Get color based on expenses vs income"""
        if expenses <= income * 0.5:
            return "#2ecc71"  # Green
        elif expenses <= income * 0.8:
            return "#27ae60"  # Darker green
        elif expenses <= income:
            return "#f39c12"  # Orange
        elif expenses <= income * 1.5:
            return "#e67e22"  # Darker orange
        else:
            return "#e74c3c"  # Red

    def populate_financial_table(self):
        """Populate the financial summary table"""
        try:
            # Clear existing data
            self.financial_table.setRowCount(0)
            
            # Group data by category
            income_categories = {}
            expense_categories = {}
            
            for item in self.current_month_data:
                if item['transaction_type'] == 'income':
                    if item['category'] not in income_categories:
                        income_categories[item['category']] = 0
                    income_categories[item['category']] += item['total']
                else:
                    if item['category'] not in expense_categories:
                        expense_categories[item['category']] = 0
                    expense_categories[item['category']] += abs(item['total'])
            
            # Add income categories
            self.financial_table.setRowCount(len(income_categories) + len(expense_categories) + 2)  # +2 for headers
            
            # Income header
            income_header = QTableWidgetItem("INCOME")
            income_header.setBackground(QColor("#2ecc71"))
            income_header.setForeground(QColor("#fff"))
            self.financial_table.setItem(0, 0, income_header)
            self.financial_table.setItem(0, 1, QTableWidgetItem(""))
            
            row = 1
            for category, total in income_categories.items():
                self.financial_table.setItem(row, 0, QTableWidgetItem(category.replace('_', ' ').title()))
                amount = QTableWidgetItem(f"${total:,.2f}")
                amount.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.financial_table.setItem(row, 1, amount)
                row += 1
            
            # Expense header
            expense_header = QTableWidgetItem("EXPENSES")
            expense_header.setBackground(QColor("#e74c3c"))
            expense_header.setForeground(QColor("#fff"))
            self.financial_table.setItem(row, 0, expense_header)
            self.financial_table.setItem(row, 1, QTableWidgetItem(""))
            row += 1
            
            for category, total in expense_categories.items():
                self.financial_table.setItem(row, 0, QTableWidgetItem(category.replace('_', ' ').title()))
                amount = QTableWidgetItem(f"${total:,.2f}")
                amount.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.financial_table.setItem(row, 1, amount)
                row += 1
        
        except Exception as e:
            logging.error(f"Error populating financial table: {e}")

    def populate_shows_table(self):
        """Populate the upcoming shows table"""
        try:
            # Clear existing data
            self.shows_table.setRowCount(0)
            
            # Add upcoming shows
            self.shows_table.setRowCount(len(self.upcoming_shows))
            
            for i, show in enumerate(self.upcoming_shows):
                self.shows_table.setItem(i, 0, QTableWidgetItem(str(show['date'])))
                self.shows_table.setItem(i, 1, QTableWidgetItem(show['name']))
                self.shows_table.setItem(i, 2, QTableWidgetItem(show['venue_name']))
                
                budget_item = QTableWidgetItem(f"${show['budget']:,.2f}")
                budget_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.shows_table.setItem(i, 3, budget_item)
                
                self.shows_table.setItem(i, 4, QTableWidgetItem(show['status']))
        
        except Exception as e:
            logging.error(f"Error populating shows table: {e}")

    def get_projection_text(self):
        """Get text for revenue projections"""
        try:
            # Get current month's data
            today = datetime.now()
            start_date = datetime(today.year, today.month, 1)
            end_date = (start_date + timedelta(days=32)).replace(day=1) - timedelta(days=1)
            
            summary = get_financial_report(start_date, end_date)
            
            monthly_income = sum(item['total'] for item in summary if item['transaction_type'] == 'income')
            monthly_expenses = sum(abs(item['total']) for item in summary if item['transaction_type'] == 'expense')
            
            # Project for next 3 months (simple projection with growth)
            upcoming_shows = len(get_upcoming_shows())
            tv_deals = len(business_db.get_active_tv_deals())
            
            # Simple projection model
            month1_income = monthly_income * 1.05  # 5% growth
            month2_income = month1_income * 1.05
            month3_income = month2_income * 1.05
            
            month1_expenses = monthly_expenses * 1.02  # 2% growth
            month2_expenses = month1_expenses * 1.02
            month3_expenses = month2_expenses * 1.02
            
            html = f"""
            <p><b>Based on current performance and {upcoming_shows} upcoming shows:</b></p>
            <table>
                <tr>
                    <th>Month</th>
                    <th>Projected Income</th>
                    <th>Projected Expenses</th>
                    <th>Projected Profit</th>
                </tr>
                <tr>
                    <td>Month 1</td>
                    <td>${month1_income:,.2f}</td>
                    <td>${month1_expenses:,.2f}</td>
                    <td>${month1_income - month1_expenses:,.2f}</td>
                </tr>
                <tr>
                    <td>Month 2</td>
                    <td>${month2_income:,.2f}</td>
                    <td>${month2_expenses:,.2f}</td>
                    <td>${month2_income - month2_expenses:,.2f}</td>
                </tr>
                <tr>
                    <td>Month 3</td>
                    <td>${month3_income:,.2f}</td>
                    <td>${month3_expenses:,.2f}</td>
                    <td>${month3_income - month3_expenses:,.2f}</td>
                </tr>
            </table>
            <p><i>Note: Projections include {tv_deals} active TV deals and existing contracts.</i></p>
            """
            
            return html
        except Exception as e:
            logging.error(f"Error generating projection text: {e}")
            return "<p>No projection data available.</p>"

    def open_business_dashboard(self):
        """Open the business dashboard"""
        # This will be connected to the main app to open the business dashboard
        pass

    def refresh_data(self):
        """Refresh all data in the dashboard"""
        self.load_data()
        self.populate_financial_table()
        self.populate_shows_table() 