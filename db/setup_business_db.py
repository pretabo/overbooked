import sys
import os

# Add the src directory to the path so we can import from src.db
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.db.business_schema import create_business_tables, initialize_business_data

def setup_business_db():
    """Set up the business database tables and initialize data"""
    print("Creating business database tables...")
    create_business_tables()
    
    print("Initializing business data...")
    initialize_business_data()
    
    print("✅ Business database setup complete!")

if __name__ == "__main__":
    setup_business_db() 