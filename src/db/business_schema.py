import sqlite3
from datetime import datetime
from db.utils import db_path

def create_business_tables():
    """Create all business-related database tables"""
    conn = sqlite3.connect(db_path("business.db"))
    cursor = conn.cursor()

    # Financial Transactions Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS financial_transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount DECIMAL(10,2) NOT NULL,
            category VARCHAR(50) NOT NULL,
            description TEXT,
            transaction_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            transaction_type VARCHAR(20) NOT NULL,  -- 'income' or 'expense'
            show_id INTEGER,  -- Optional reference to a show
            wrestler_id INTEGER,  -- Optional reference to a wrestler
            FOREIGN KEY (show_id) REFERENCES shows(id),
            FOREIGN KEY (wrestler_id) REFERENCES wrestlers(id)
        )
    """)

    # Shows Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS shows (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(100) NOT NULL,
            show_type VARCHAR(20) NOT NULL,  -- 'weekly', 'ppv', 'special'
            date DATETIME NOT NULL,
            venue_id INTEGER NOT NULL,
            budget DECIMAL(10,2) NOT NULL,
            status VARCHAR(20) NOT NULL,  -- 'scheduled', 'in_progress', 'completed'
            attendance INTEGER,
            ticket_price DECIMAL(10,2),
            total_revenue DECIMAL(10,2),
            total_expenses DECIMAL(10,2),
            net_profit DECIMAL(10,2),
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (venue_id) REFERENCES venues(id)
        )
    """)

    # Show Matches Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS show_matches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            show_id INTEGER NOT NULL,
            match_number INTEGER NOT NULL,
            match_type VARCHAR(50) NOT NULL,
            wrestler1_id INTEGER NOT NULL,
            wrestler2_id INTEGER NOT NULL,
            winner_id INTEGER,
            match_rating INTEGER,
            crowd_reaction INTEGER,
            duration INTEGER,  -- in seconds
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (show_id) REFERENCES shows(id),
            FOREIGN KEY (wrestler1_id) REFERENCES wrestlers(id),
            FOREIGN KEY (wrestler2_id) REFERENCES wrestlers(id),
            FOREIGN KEY (winner_id) REFERENCES wrestlers(id)
        )
    """)

    # Venues Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS venues (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(100) NOT NULL,
            capacity INTEGER NOT NULL,
            base_cost DECIMAL(10,2) NOT NULL,
            location VARCHAR(100) NOT NULL,
            prestige INTEGER DEFAULT 50,  -- 0-100 scale
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Contracts Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS contracts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            wrestler_id INTEGER NOT NULL,
            start_date DATE NOT NULL,
            end_date DATE NOT NULL,
            base_salary DECIMAL(10,2) NOT NULL,
            bonus_structure TEXT,  -- JSON string of bonus conditions
            status VARCHAR(20) NOT NULL,  -- 'active', 'expired', 'terminated'
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (wrestler_id) REFERENCES wrestlers(id)
        )
    """)

    # Budget Allocations Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS budget_allocations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category VARCHAR(50) NOT NULL,
            percentage DECIMAL(5,2) NOT NULL,  -- 0-100
            amount DECIMAL(10,2) NOT NULL,
            fiscal_year INTEGER NOT NULL,
            fiscal_month INTEGER NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(category, fiscal_year, fiscal_month)
        )
    """)

    # Merchandise Items Table (NEW)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS merchandise_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            wrestler_id INTEGER NOT NULL,
            name VARCHAR(100) NOT NULL,
            type VARCHAR(50) NOT NULL,  -- 't-shirt', 'hat', 'poster', etc.
            base_price INTEGER NOT NULL,  -- Changed to 1-5 star rating
            production_cost INTEGER NOT NULL,  -- Changed to 1-5 star rating
            design_quality INTEGER NOT NULL,  -- Changed to 1-5 star rating
            material_quality INTEGER NOT NULL,  -- Changed to 1-5 star rating
            uniqueness INTEGER NOT NULL,  -- Changed to 1-5 star rating
            fan_appeal INTEGER NOT NULL,  -- Changed to 1-5 star rating
            overall_quality INTEGER NOT NULL,  -- Changed to 1-5 star rating (calculated)
            release_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            status VARCHAR(20) NOT NULL DEFAULT 'active',  -- 'active', 'discontinued'
            company_split DECIMAL(5,2) NOT NULL DEFAULT 80.00,  -- Percentage the company receives
            wrestler_split DECIMAL(5,2) NOT NULL DEFAULT 20.00,  -- Percentage the wrestler receives
            FOREIGN KEY (wrestler_id) REFERENCES wrestlers(id)
        )
    """)

    # Merchandise Sales Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS merchandise_sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            wrestler_id INTEGER NOT NULL,
            merchandise_item_id INTEGER NOT NULL,
            show_id INTEGER,  -- Optional reference to a show if sold during an event
            quantity INTEGER NOT NULL,
            price DECIMAL(10,2) NOT NULL,
            total_amount DECIMAL(10,2) NOT NULL,
            production_cost DECIMAL(10,2) NOT NULL,
            profit DECIMAL(10,2) NOT NULL,
            company_profit DECIMAL(10,2) NOT NULL,
            wrestler_profit DECIMAL(10,2) NOT NULL,
            sales_type VARCHAR(20) NOT NULL,  -- 'daily', 'event'
            sale_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (wrestler_id) REFERENCES wrestlers(id),
            FOREIGN KEY (merchandise_item_id) REFERENCES merchandise_items(id),
            FOREIGN KEY (show_id) REFERENCES shows(id)
        )
    """)

    # Event Financial Impact Table (NEW)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS event_financial_impact (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            show_id INTEGER NOT NULL,
            ticket_sales DECIMAL(10,2) NOT NULL,
            merchandise_sales DECIMAL(10,2) NOT NULL,
            concession_sales DECIMAL(10,2) NOT NULL,
            sponsorship_revenue DECIMAL(10,2) NOT NULL,
            ppv_revenue DECIMAL(10,2) NOT NULL,
            production_costs DECIMAL(10,2) NOT NULL,
            talent_costs DECIMAL(10,2) NOT NULL,
            marketing_costs DECIMAL(10,2) NOT NULL,
            venue_costs DECIMAL(10,2) NOT NULL,
            other_costs DECIMAL(10,2) NOT NULL,
            total_revenue DECIMAL(10,2) NOT NULL,
            total_costs DECIMAL(10,2) NOT NULL,
            net_profit DECIMAL(10,2) NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (show_id) REFERENCES shows(id)
        )
    """)

    # TV Deals Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tv_deals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            network_name VARCHAR(100) NOT NULL,
            show_name VARCHAR(100) NOT NULL,
            start_date DATE NOT NULL,
            end_date DATE NOT NULL,
            weekly_payment DECIMAL(10,2) NOT NULL,
            rating_bonus DECIMAL(10,2),  -- Bonus per 0.1 rating point
            status VARCHAR(20) NOT NULL,  -- 'active', 'expired', 'cancelled'
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Create indexes for better query performance
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_transactions_date ON financial_transactions(transaction_date)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_shows_date ON shows(date)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_contracts_dates ON contracts(start_date, end_date)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_budget_fiscal ON budget_allocations(fiscal_year, fiscal_month)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_merch_items_wrestler ON merchandise_items(wrestler_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_merch_sales_date ON merchandise_sales(sale_date)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_event_financial_show ON event_financial_impact(show_id)")

    conn.commit()
    conn.close()

def initialize_business_data():
    """Initialize some basic business data"""
    conn = sqlite3.connect(db_path("business.db"))
    cursor = conn.cursor()

    # Check if venues table is empty
    cursor.execute("SELECT COUNT(*) FROM venues")
    venue_count = cursor.fetchone()[0]
    
    # Add some default venues if none exist
    if venue_count == 0:
        venues = [
            ("Local Arena", 2000, 5000.00, "Hometown", 50),
            ("Regional Stadium", 5000, 15000.00, "Major City", 70),
            ("National Arena", 10000, 50000.00, "Metropolitan", 90)
        ]
        cursor.executemany("""
            INSERT INTO venues (name, capacity, base_cost, location, prestige)
            VALUES (?, ?, ?, ?, ?)
        """, venues)
        print("Default venues created.")

    # Set up initial budget allocations
    current_year = datetime.now().year
    current_month = datetime.now().month
    
    # Check if budget allocations exist for current month
    cursor.execute("""
        SELECT COUNT(*) FROM budget_allocations 
        WHERE fiscal_year = ? AND fiscal_month = ?
    """, (current_year, current_month))
    
    allocation_count = cursor.fetchone()[0]
    
    if allocation_count == 0:
        allocations = [
            ("talent", 40.00, 400000.00, current_year, current_month),
            ("production", 20.00, 200000.00, current_year, current_month),
            ("marketing", 20.00, 200000.00, current_year, current_month),
            ("operations", 20.00, 200000.00, current_year, current_month)
        ]
        cursor.executemany("""
            INSERT INTO budget_allocations 
            (category, percentage, amount, fiscal_year, fiscal_month)
            VALUES (?, ?, ?, ?, ?)
        """, allocations)
        print("Budget allocations initialized.")
    
    # Define default merchandise types with price ranges
    merchandise_types = [
        ("T-Shirt", 24.99, 8.50),
        ("Premium T-Shirt", 29.99, 12.00),
        ("Hat", 19.99, 5.50),
        ("Poster", 14.99, 2.00),
        ("Action Figure", 29.99, 9.00),
        ("Championship Replica", 299.99, 120.00),
        ("Mug", 12.99, 3.50),
        ("Wristband", 9.99, 1.50)
    ]
    
    conn.commit()
    conn.close()
    
    print("Business database initialized successfully.")

if __name__ == "__main__":
    create_business_tables()
    initialize_business_data() 