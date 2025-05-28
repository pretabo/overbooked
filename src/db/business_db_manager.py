import sqlite3
from datetime import datetime
import json
import logging
from db.utils import db_path

class BusinessDBManager:
    def __init__(self):
        self.db_path = db_path("business.db")
        self._ensure_tables_exist()

    def _ensure_tables_exist(self):
        """Ensure all business tables exist"""
        from src.db.business_schema import create_business_tables
        create_business_tables()

    def _get_connection(self):
        """Get a database connection"""
        return sqlite3.connect(self.db_path)

    # Show Management Methods
    def create_show(self, name, show_type, date, venue_id, budget):
        """Create a new show"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO shows (name, show_type, date, venue_id, budget, status)
                VALUES (?, ?, ?, ?, ?, 'scheduled')
            """, (name, show_type, date, venue_id, budget))
            
            show_id = cursor.lastrowid
            conn.commit()
            return show_id
        except Exception as e:
            logging.error(f"Error creating show: {e}")
            return None
        finally:
            conn.close()

    def get_upcoming_shows(self, limit=10):
        """Get upcoming shows"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT s.*, v.name as venue_name, v.capacity
                FROM shows s
                JOIN venues v ON s.venue_id = v.id
                WHERE s.date > datetime('now')
                AND s.status = 'scheduled'
                ORDER BY s.date
                LIMIT ?
            """, (limit,))
            
            columns = [desc[0] for desc in cursor.description]
            shows = [dict(zip(columns, row)) for row in cursor.fetchall()]
            return shows
        except Exception as e:
            logging.error(f"Error getting upcoming shows: {e}")
            return []
        finally:
            conn.close()

    def get_show_details(self, show_id):
        """Get detailed information about a show"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT s.*, v.name as venue_name, v.capacity, v.prestige
                FROM shows s
                JOIN venues v ON s.venue_id = v.id
                WHERE s.id = ?
            """, (show_id,))
            
            columns = [desc[0] for desc in cursor.description]
            show = dict(zip(columns, cursor.fetchone()))
            
            # Get matches for this show
            cursor.execute("""
                SELECT m.*, w1.name as wrestler1_name, w2.name as wrestler2_name, 
                       winner.name as winner_name
                FROM show_matches m
                JOIN wrestlers w1 ON m.wrestler1_id = w1.id
                JOIN wrestlers w2 ON m.wrestler2_id = w2.id
                LEFT JOIN wrestlers winner ON m.winner_id = winner.id
                WHERE m.show_id = ?
                ORDER BY m.match_number
            """, (show_id,))
            
            match_columns = [desc[0] for desc in cursor.description]
            matches = [dict(zip(match_columns, row)) for row in cursor.fetchall()]
            
            show['matches'] = matches
            return show
        except Exception as e:
            logging.error(f"Error getting show details: {e}")
            return None
        finally:
            conn.close()

    def add_match_to_show(self, show_id, match_number, match_type, wrestler1_id, wrestler2_id):
        """Add a match to a show"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO show_matches 
                (show_id, match_number, match_type, wrestler1_id, wrestler2_id)
                VALUES (?, ?, ?, ?, ?)
            """, (show_id, match_number, match_type, wrestler1_id, wrestler2_id))
            
            match_id = cursor.lastrowid
            conn.commit()
            return match_id
        except Exception as e:
            logging.error(f"Error adding match to show: {e}")
            return None
        finally:
            conn.close()

    def update_show_status(self, show_id, status, attendance=None, ticket_price=None, 
                         total_revenue=None, total_expenses=None):
        """Update the status of a show"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            query = "UPDATE shows SET status = ?"
            params = [status]
            
            if attendance is not None:
                query += ", attendance = ?"
                params.append(attendance)
                
            if ticket_price is not None:
                query += ", ticket_price = ?"
                params.append(ticket_price)
                
            if total_revenue is not None:
                query += ", total_revenue = ?"
                params.append(total_revenue)
                
            if total_expenses is not None:
                query += ", total_expenses = ?"
                params.append(total_expenses)
                
            if total_revenue is not None and total_expenses is not None:
                query += ", net_profit = ?"
                params.append(total_revenue - total_expenses)
                
            query += " WHERE id = ?"
            params.append(show_id)
            
            cursor.execute(query, params)
            conn.commit()
            return True
        except Exception as e:
            logging.error(f"Error updating show status: {e}")
            return False
        finally:
            conn.close()

    # Financial Methods
    def record_transaction(self, amount, category, description, transaction_type, show_id=None, wrestler_id=None):
        """Record a financial transaction"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO financial_transactions 
                (amount, category, description, transaction_type, show_id, wrestler_id)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (amount, category, description, transaction_type, show_id, wrestler_id))
            
            conn.commit()
            return cursor.lastrowid
        except Exception as e:
            logging.error(f"Error recording transaction: {e}")
            return None
        finally:
            conn.close()

    def get_financial_summary(self, start_date, end_date):
        """Get financial summary for a date range"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    transaction_type,
                    category,
                    SUM(amount) as total
                FROM financial_transactions
                WHERE transaction_date BETWEEN ? AND ?
                GROUP BY transaction_type, category
            """, (start_date, end_date))
            
            columns = [desc[0] for desc in cursor.description]
            summary = [dict(zip(columns, row)) for row in cursor.fetchall()]
            return summary
        except Exception as e:
            logging.error(f"Error getting financial summary: {e}")
            return []
        finally:
            conn.close()

    def get_recent_transactions(self, limit=50):
        """Get recent financial transactions"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    id, amount, category, description, transaction_date, 
                    transaction_type, show_id, wrestler_id
                FROM financial_transactions
                ORDER BY transaction_date DESC
                LIMIT ?
            """, (limit,))
            
            columns = [desc[0] for desc in cursor.description]
            transactions = [dict(zip(columns, row)) for row in cursor.fetchall()]
            return transactions
        except Exception as e:
            logging.error(f"Error getting recent transactions: {e}")
            return []
        finally:
            conn.close()

    # Contract Methods
    def create_contract(self, wrestler_id, start_date, end_date, base_salary, bonus_structure=None):
        """Create a new wrestler contract"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            if bonus_structure:
                bonus_structure = json.dumps(bonus_structure)
            
            cursor.execute("""
                INSERT INTO contracts 
                (wrestler_id, start_date, end_date, base_salary, bonus_structure, status)
                VALUES (?, ?, ?, ?, ?, 'active')
            """, (wrestler_id, start_date, end_date, base_salary, bonus_structure))
            
            contract_id = cursor.lastrowid
            conn.commit()
            return contract_id
        except Exception as e:
            logging.error(f"Error creating contract: {e}")
            return None
        finally:
            conn.close()

    def get_active_contracts(self):
        """Get all active contracts"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT c.*, w.name as wrestler_name
                FROM contracts c
                JOIN wrestlers w ON c.wrestler_id = w.id
                WHERE c.status = 'active'
                AND c.end_date > date('now')
            """)
            
            columns = [desc[0] for desc in cursor.description]
            contracts = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            # Parse bonus structure JSON
            for contract in contracts:
                if contract['bonus_structure']:
                    contract['bonus_structure'] = json.loads(contract['bonus_structure'])
            
            return contracts
        except Exception as e:
            logging.error(f"Error getting active contracts: {e}")
            return []
        finally:
            conn.close()

    def terminate_contract(self, contract_id):
        """Terminate a contract"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE contracts
                SET status = 'terminated'
                WHERE id = ?
            """, (contract_id,))
            
            conn.commit()
            return True
        except Exception as e:
            logging.error(f"Error terminating contract: {e}")
            return False
        finally:
            conn.close()

    # Venue Methods
    def get_all_venues(self):
        """Get all venues"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, name, capacity, base_cost, location, prestige
                FROM venues
                ORDER BY capacity
            """)
            
            columns = [desc[0] for desc in cursor.description]
            venues = [dict(zip(columns, row)) for row in cursor.fetchall()]
            return venues
        except Exception as e:
            logging.error(f"Error getting venues: {e}")
            return []
        finally:
            conn.close()

    def get_venue(self, venue_id):
        """Get a venue by ID"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, name, capacity, base_cost, location, prestige
                FROM venues
                WHERE id = ?
            """, (venue_id,))
            
            columns = [desc[0] for desc in cursor.description]
            venue = dict(zip(columns, cursor.fetchone()))
            return venue
        except Exception as e:
            logging.error(f"Error getting venue: {e}")
            return None
        finally:
            conn.close()

    # TV Deal Methods
    def create_tv_deal(self, network_name, show_name, start_date, end_date, weekly_payment, rating_bonus=0):
        """Create a new TV deal"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO tv_deals
                (network_name, show_name, start_date, end_date, weekly_payment, rating_bonus, status)
                VALUES (?, ?, ?, ?, ?, ?, 'active')
            """, (network_name, show_name, start_date, end_date, weekly_payment, rating_bonus))
            
            deal_id = cursor.lastrowid
            conn.commit()
            return deal_id
        except Exception as e:
            logging.error(f"Error creating TV deal: {e}")
            return None
        finally:
            conn.close()

    def get_active_tv_deals(self):
        """Get all active TV deals"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT *
                FROM tv_deals
                WHERE status = 'active'
                AND end_date > date('now')
            """)
            
            columns = [desc[0] for desc in cursor.description]
            deals = [dict(zip(columns, row)) for row in cursor.fetchall()]
            return deals
        except Exception as e:
            logging.error(f"Error getting TV deals: {e}")
            return []
        finally:
            conn.close()

    # Budget Methods
    def update_budget_allocation(self, category, percentage, amount, fiscal_year, fiscal_month):
        """Update budget allocation for a category"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO budget_allocations 
                (category, percentage, amount, fiscal_year, fiscal_month)
                VALUES (?, ?, ?, ?, ?)
            """, (category, percentage, amount, fiscal_year, fiscal_month))
            
            conn.commit()
            return True
        except Exception as e:
            logging.error(f"Error updating budget: {e}")
            return False
        finally:
            conn.close()

    def get_current_budget(self):
        """Get current budget allocations"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            current_year = datetime.now().year
            current_month = datetime.now().month
            
            cursor.execute("""
                SELECT category, percentage, amount
                FROM budget_allocations
                WHERE fiscal_year = ? AND fiscal_month = ?
            """, (current_year, current_month))
            
            columns = [desc[0] for desc in cursor.description]
            budget = [dict(zip(columns, row)) for row in cursor.fetchall()]
            return budget
        except Exception as e:
            logging.error(f"Error getting budget: {e}")
            return []
        finally:
            conn.close()

    # Integration with other databases
    def get_wrestler_relationships(self, wrestler_id):
        """Get all relationships for a wrestler from relationships.db"""
        try:
            conn = sqlite3.connect(db_path("relationships.db"))
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT wrestler2_id, relationship_value
                FROM relationships
                WHERE wrestler1_id = ?
            """, (wrestler_id,))
            
            relationships = cursor.fetchall()
            return relationships
        except Exception as e:
            logging.error(f"Error getting wrestler relationships: {e}")
            return []
        finally:
            conn.close()

    def save_business_state(self):
        """Save business state to save_state.db"""
        try:
            conn = sqlite3.connect(db_path("save_state.db"))
            cursor = conn.cursor()
            
            # Ensure table exists
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS game_state (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
            """)
            
            # Save current budget
            budget = json.dumps(self.get_current_budget())
            cursor.execute("""
                INSERT OR REPLACE INTO game_state
                (key, value)
                VALUES ('current_budget', ?)
            """, (budget,))
            
            # Save active contracts
            contracts = json.dumps(self.get_active_contracts())
            cursor.execute("""
                INSERT OR REPLACE INTO game_state
                (key, value)
                VALUES ('active_contracts', ?)
            """, (contracts,))
            
            # Save upcoming shows
            shows = json.dumps(self.get_upcoming_shows(limit=20))
            cursor.execute("""
                INSERT OR REPLACE INTO game_state
                (key, value)
                VALUES ('upcoming_shows', ?)
            """, (shows,))
            
            conn.commit()
            return True
        except Exception as e:
            logging.error(f"Error saving business state: {e}")
            return False
        finally:
            conn.close()

    def load_business_state(self):
        """Load business state from save_state.db"""
        try:
            conn = sqlite3.connect(db_path("save_state.db"))
            cursor = conn.cursor()
            
            # Check if table exists
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='game_state'
            """)
            if not cursor.fetchone():
                return {}
            
            # Load all state data
            cursor.execute("SELECT key, value FROM game_state")
            state = {}
            for key, value in cursor.fetchall():
                state[key] = json.loads(value)
            
            return state
        except Exception as e:
            logging.error(f"Error loading business state: {e}")
            return {}
        finally:
            conn.close()

    # Merchandise Methods
    def create_merchandise_item(self, wrestler_id, name, merch_type, base_price,
                            production_cost=None, design_quality=None, material_quality=None,
                            uniqueness=None, fan_appeal=None):
        """Create a new merchandise item"""
        try:
            conn = sqlite3.connect(db_path("business.db"))
            cursor = conn.cursor()
            
            # Generate reasonable defaults for optional parameters
            if production_cost is None:
                production_cost = int(base_price * 0.5)  # 50% of base price
                
            import random
            if design_quality is None:
                design_quality = random.randint(1, 5)
            if material_quality is None:
                material_quality = random.randint(1, 5)
            if uniqueness is None:
                uniqueness = random.randint(1, 5)
            if fan_appeal is None:
                fan_appeal = random.randint(1, 5)
                
            # Calculate overall quality
            overall_quality = (design_quality + material_quality + uniqueness + fan_appeal) // 4
            
            # Revenue splits (wrestler gets 10-30% based on item quality)
            wrestler_split = min(30, max(10, overall_quality * 5))
            company_split = 100 - wrestler_split
            
            # Create the item
            cursor.execute("""
                INSERT INTO merchandise_items (
                    wrestler_id, name, type, base_price, production_cost,
                    design_quality, material_quality, uniqueness, fan_appeal,
                    overall_quality, company_split, wrestler_split, status, 
                    creation_date
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, date('now'))
            """, (
                wrestler_id, name, merch_type, base_price, production_cost,
                design_quality, material_quality, uniqueness, fan_appeal,
                overall_quality, company_split, wrestler_split, "active"
            ))
            
            item_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return item_id
        except Exception as e:
            print(f"Error creating merchandise item: {e}")
            return None

    def get_wrestler_merchandise(self, wrestler_id):
        """Get merchandise items for a specific wrestler"""
        try:
            conn = sqlite3.connect(db_path("business.db"))
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT m.id, m.name, m.type, m.base_price, m.production_cost,
                       m.design_quality, m.material_quality, m.uniqueness, m.fan_appeal,
                       m.overall_quality, m.company_split, m.wrestler_split, m.status,
                       m.creation_date, w.name as wrestler_name
                FROM merchandise_items m
                LEFT JOIN wrestlers w ON w.id = m.wrestler_id
                WHERE m.wrestler_id = ?
                ORDER BY m.creation_date DESC
            """, (wrestler_id,))
            
            columns = [desc[0] for desc in cursor.description]
            items = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            conn.close()
            return items
        except Exception as e:
            print(f"Error getting wrestler merchandise: {e}")
            return []

    def get_all_active_merchandise(self):
        """Get all active merchandise items"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT mi.*, w.name as wrestler_name
                FROM merchandise_items mi
                JOIN wrestlers w ON mi.wrestler_id = w.id
                WHERE mi.status = 'active'
            """)
            
            columns = [desc[0] for desc in cursor.description]
            items = [dict(zip(columns, row)) for row in cursor.fetchall()]
            return items
        except Exception as e:
            logging.error(f"Error getting active merchandise: {e}")
            return []
        finally:
            conn.close()
            
    def get_merchandise_item(self, item_id):
        """Get a specific merchandise item"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT mi.*, w.name as wrestler_name
                FROM merchandise_items mi
                JOIN wrestlers w ON mi.wrestler_id = w.id
                WHERE mi.id = ?
            """, (item_id,))
            
            columns = [desc[0] for desc in cursor.description]
            row = cursor.fetchone()
            
            if not row:
                return None
                
            return dict(zip(columns, row))
        except Exception as e:
            logging.error(f"Error getting merchandise item: {e}")
            return None
        finally:
            conn.close()

    def update_merchandise_item(self, item_id, name=None, base_price=None, status=None,
                              company_split=None, wrestler_split=None):
        """Update a merchandise item"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            updates = []
            params = []
            
            if name is not None:
                updates.append("name = ?")
                params.append(name)
                
            if base_price is not None:
                updates.append("base_price = ?")
                params.append(base_price)
                
            if status is not None:
                updates.append("status = ?")
                params.append(status)
                
            if company_split is not None:
                updates.append("company_split = ?")
                params.append(company_split)
                
            if wrestler_split is not None:
                updates.append("wrestler_split = ?")
                params.append(wrestler_split)
                
            if not updates:
                return False
                
            query = f"UPDATE merchandise_items SET {', '.join(updates)} WHERE id = ?"
            params.append(item_id)
            
            cursor.execute(query, params)
            conn.commit()
            
            return cursor.rowcount > 0
        except Exception as e:
            logging.error(f"Error updating merchandise item: {e}")
            return False
        finally:
            conn.close()

    def record_merchandise_sale(self, wrestler_id, merchandise_item_id, quantity, price,
                             total_amount, production_cost, profit, company_profit, wrestler_profit,
                             show_id=None, sales_type="daily"):
        """Record a merchandise sale"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO merchandise_sales 
                (wrestler_id, merchandise_item_id, show_id, quantity, price, 
                 total_amount, production_cost, profit, company_profit, wrestler_profit, sales_type)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (wrestler_id, merchandise_item_id, show_id, quantity, price, 
                  total_amount, production_cost, profit, company_profit, wrestler_profit, sales_type))
            
            sale_id = cursor.lastrowid
            conn.commit()
            return sale_id
        except Exception as e:
            logging.error(f"Error recording merchandise sale: {e}")
            return None
        finally:
            conn.close()

    def get_merchandise_sales(self, start_date=None, end_date=None, wrestler_id=None, show_id=None):
        """Get merchandise sales for a date range"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            query = """
                SELECT ms.*, mi.name as item_name, mi.type as item_type, w.name as wrestler_name
                FROM merchandise_sales ms
                JOIN merchandise_items mi ON ms.merchandise_item_id = mi.id
                JOIN wrestlers w ON ms.wrestler_id = w.id
                WHERE 1=1
            """
            params = []
            
            if start_date:
                query += " AND ms.sale_date >= ?"
                params.append(start_date)
                
            if end_date:
                query += " AND ms.sale_date <= ?"
                params.append(end_date)
                
            if wrestler_id:
                query += " AND ms.wrestler_id = ?"
                params.append(wrestler_id)
                
            if show_id:
                query += " AND ms.show_id = ?"
                params.append(show_id)
                
            query += " ORDER BY ms.sale_date DESC"
            
            cursor.execute(query, params)
            
            columns = [desc[0] for desc in cursor.description]
            sales = [dict(zip(columns, row)) for row in cursor.fetchall()]
            return sales
        except Exception as e:
            logging.error(f"Error getting merchandise sales: {e}")
            return []
        finally:
            conn.close()
            
    def get_merchandise_sales_summary(self, start_date=None, end_date=None):
        """Get a summary of merchandise sales"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            query = """
                SELECT 
                    COUNT(*) as total_transactions,
                    SUM(quantity) as total_items_sold,
                    SUM(total_amount) as total_revenue,
                    SUM(production_cost) as total_production_cost,
                    SUM(profit) as total_profit,
                    SUM(company_profit) as total_company_profit,
                    SUM(wrestler_profit) as total_wrestler_profit,
                    AVG(profit) as average_profit_per_transaction
                FROM merchandise_sales
                WHERE 1=1
            """
            params = []
            
            if start_date:
                query += " AND sale_date >= ?"
                params.append(start_date)
                
            if end_date:
                query += " AND sale_date <= ?"
                params.append(end_date)
                
            cursor.execute(query, params)
            
            columns = [desc[0] for desc in cursor.description]
            summary = dict(zip(columns, cursor.fetchone()))
            
            # Get top selling items
            cursor.execute("""
                SELECT 
                    mi.id, mi.name, mi.type,
                    w.id as wrestler_id, w.name as wrestler_name,
                    SUM(ms.quantity) as total_sold,
                    SUM(ms.total_amount) as total_revenue,
                    SUM(ms.profit) as total_profit
                FROM merchandise_sales ms
                JOIN merchandise_items mi ON ms.merchandise_item_id = mi.id
                JOIN wrestlers w ON ms.wrestler_id = w.id
                WHERE 1=1
            """ + (" AND ms.sale_date >= ?" if start_date else "") + 
                  (" AND ms.sale_date <= ?" if end_date else "") + """
                GROUP BY mi.id
                ORDER BY total_sold DESC
                LIMIT 10
            """, params)
            
            top_item_columns = [desc[0] for desc in cursor.description]
            summary['top_selling_items'] = [dict(zip(top_item_columns, row)) for row in cursor.fetchall()]
            
            # Get top selling wrestlers
            cursor.execute("""
                SELECT 
                    w.id as wrestler_id, w.name as wrestler_name,
                    SUM(ms.quantity) as total_sold,
                    SUM(ms.total_amount) as total_revenue,
                    SUM(ms.profit) as total_profit
                FROM merchandise_sales ms
                JOIN wrestlers w ON ms.wrestler_id = w.id
                WHERE 1=1
            """ + (" AND ms.sale_date >= ?" if start_date else "") + 
                  (" AND ms.sale_date <= ?" if end_date else "") + """
                GROUP BY w.id
                ORDER BY total_sold DESC
                LIMIT 10
            """, params)
            
            top_wrestler_columns = [desc[0] for desc in cursor.description]
            summary['top_selling_wrestlers'] = [dict(zip(top_wrestler_columns, row)) for row in cursor.fetchall()]
            
            return summary
        except Exception as e:
            logging.error(f"Error getting merchandise sales summary: {e}")
            return {}
        finally:
            conn.close()

    # Event Financial Impact Methods
    def create_event_financial_impact(self, show_id, ticket_sales=0, merchandise_sales=0, 
                                   concession_sales=0, sponsorship_revenue=0, ppv_revenue=0,
                                   production_costs=0, talent_costs=0, marketing_costs=0, 
                                   venue_costs=0, other_costs=0):
        """Create a new event financial impact record"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            total_revenue = ticket_sales + merchandise_sales + concession_sales + sponsorship_revenue + ppv_revenue
            total_costs = production_costs + talent_costs + marketing_costs + venue_costs + other_costs
            net_profit = total_revenue - total_costs
            
            cursor.execute("""
                INSERT INTO event_financial_impact 
                (show_id, ticket_sales, merchandise_sales, concession_sales, sponsorship_revenue, 
                 ppv_revenue, production_costs, talent_costs, marketing_costs, venue_costs, 
                 other_costs, total_revenue, total_costs, net_profit)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (show_id, ticket_sales, merchandise_sales, concession_sales, sponsorship_revenue, 
                 ppv_revenue, production_costs, talent_costs, marketing_costs, venue_costs, 
                 other_costs, total_revenue, total_costs, net_profit))
            
            impact_id = cursor.lastrowid
            conn.commit()
            return impact_id
        except Exception as e:
            logging.error(f"Error creating event financial impact: {e}")
            return None
        finally:
            conn.close()

    def update_event_financial_impact(self, show_id, ticket_sales=None, merchandise_sales=None, 
                                    concession_sales=None, sponsorship_revenue=None, ppv_revenue=None,
                                    production_costs=None, talent_costs=None, marketing_costs=None, 
                                    venue_costs=None, other_costs=None):
        """Update an event financial impact record"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Check if record exists
            cursor.execute("""
                SELECT id, total_revenue, total_costs FROM event_financial_impact
                WHERE show_id = ?
            """, (show_id,))
            
            row = cursor.fetchone()
            if not row:
                # Create new record if it doesn't exist
                return self.create_event_financial_impact(
                    show_id, ticket_sales or 0, merchandise_sales or 0, 
                    concession_sales or 0, sponsorship_revenue or 0, ppv_revenue or 0,
                    production_costs or 0, talent_costs or 0, marketing_costs or 0, 
                    venue_costs or 0, other_costs or 0
                )
            
            impact_id, current_revenue, current_costs = row
            
            updates = []
            params = []
            
            # For each field, update only if provided
            fields = {
                'ticket_sales': ticket_sales,
                'merchandise_sales': merchandise_sales,
                'concession_sales': concession_sales,
                'sponsorship_revenue': sponsorship_revenue,
                'ppv_revenue': ppv_revenue,
                'production_costs': production_costs,
                'talent_costs': talent_costs,
                'marketing_costs': marketing_costs,
                'venue_costs': venue_costs,
                'other_costs': other_costs
            }
            
            for field, value in fields.items():
                if value is not None:
                    updates.append(f"{field} = ?")
                    params.append(value)
            
            if not updates:
                return impact_id
            
            # Get current values for recalculating totals
            cursor.execute("""
                SELECT 
                    ticket_sales, merchandise_sales, concession_sales, 
                    sponsorship_revenue, ppv_revenue, production_costs, 
                    talent_costs, marketing_costs, venue_costs, other_costs
                FROM event_financial_impact
                WHERE id = ?
            """, (impact_id,))
            
            current = dict(zip([
                'ticket_sales', 'merchandise_sales', 'concession_sales', 
                'sponsorship_revenue', 'ppv_revenue', 'production_costs', 
                'talent_costs', 'marketing_costs', 'venue_costs', 'other_costs'
            ], cursor.fetchone()))
            
            # Update current values with new ones
            for field, value in fields.items():
                if value is not None:
                    current[field] = value
            
            # Calculate new totals
            total_revenue = (
                current['ticket_sales'] + 
                current['merchandise_sales'] + 
                current['concession_sales'] + 
                current['sponsorship_revenue'] + 
                current['ppv_revenue']
            )
            
            total_costs = (
                current['production_costs'] + 
                current['talent_costs'] + 
                current['marketing_costs'] + 
                current['venue_costs'] + 
                current['other_costs']
            )
            
            net_profit = total_revenue - total_costs
            
            # Add total fields to updates
            updates.append("total_revenue = ?")
            params.append(total_revenue)
            
            updates.append("total_costs = ?")
            params.append(total_costs)
            
            updates.append("net_profit = ?")
            params.append(net_profit)
            
            # Execute update
            query = f"UPDATE event_financial_impact SET {', '.join(updates)} WHERE id = ?"
            params.append(impact_id)
            
            cursor.execute(query, params)
            conn.commit()
            
            return impact_id
        except Exception as e:
            logging.error(f"Error updating event financial impact: {e}")
            return None
        finally:
            conn.close()

    def get_event_financial_impact(self, show_id):
        """Get financial impact for an event"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM event_financial_impact
                WHERE show_id = ?
            """, (show_id,))
            
            columns = [desc[0] for desc in cursor.description]
            row = cursor.fetchone()
            
            if not row:
                return None
                
            return dict(zip(columns, row))
        except Exception as e:
            logging.error(f"Error getting event financial impact: {e}")
            return None
        finally:
            conn.close()
            
    def get_all_event_financials(self, limit=20):
        """Get financial summary for all events"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    efi.*, 
                    s.name as show_name, 
                    s.show_type,
                    s.date as show_date,
                    v.name as venue_name
                FROM event_financial_impact efi
                JOIN shows s ON efi.show_id = s.id
                JOIN venues v ON s.venue_id = v.id
                ORDER BY s.date DESC
                LIMIT ?
            """, (limit,))
            
            columns = [desc[0] for desc in cursor.description]
            events = [dict(zip(columns, row)) for row in cursor.fetchall()]
            return events
        except Exception as e:
            logging.error(f"Error getting all event financials: {e}")
            return []
        finally:
            conn.close()
            
    def get_wrestler(self, wrestler_id):
        """Get wrestler details"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM wrestlers
                WHERE id = ?
            """, (wrestler_id,))
            
            columns = [desc[0] for desc in cursor.description]
            row = cursor.fetchone()
            
            if not row:
                return None
                
            return dict(zip(columns, row))
        except Exception as e:
            logging.error(f"Error getting wrestler: {e}")
            return None
        finally:
            conn.close()
            
    def get_all_wrestlers(self):
        """Get all wrestlers"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, name, gender, popularity, charisma 
                FROM wrestlers
                ORDER BY popularity DESC
            """)
            
            columns = [desc[0] for desc in cursor.description]
            wrestlers = [dict(zip(columns, row)) for row in cursor.fetchall()]
            return wrestlers
        except Exception as e:
            logging.error(f"Error getting all wrestlers: {e}")
            return []
        finally:
            conn.close()

    def calculate_financial_health(self, cash_balance, monthly_income, monthly_expenses):
        """Calculate the financial health score (0-100)"""
        score = 50  # Start at neutral
        
        # Cash balance factor (0-30 points)
        if cash_balance > 1000000:  # Over $1M
            score += 30
        elif cash_balance > 500000:  # $500K-$1M
            score += 25
        elif cash_balance > 250000:  # $250K-$500K
            score += 20
        elif cash_balance > 100000:  # $100K-$250K
            score += 15
        elif cash_balance > 50000:   # $50K-$100K
            score += 10
        elif cash_balance > 10000:   # $10K-$50K
            score += 5
        elif cash_balance < 0:       # Negative cash
            score -= min(30, abs(cash_balance) // 10000)  # Lose points based on debt
        
        # Profit margin factor (0-40 points)
        if monthly_expenses > 0:
            profit_ratio = (monthly_income - monthly_expenses) / monthly_expenses
            
            if profit_ratio > 0.5:    # >50% profit margin
                score += 40
            elif profit_ratio > 0.3:  # 30-50% profit margin
                score += 30
            elif profit_ratio > 0.2:  # 20-30% profit margin
                score += 25
            elif profit_ratio > 0.1:  # 10-20% profit margin
                score += 20
            elif profit_ratio > 0:    # 0-10% profit margin
                score += 10
            elif profit_ratio > -0.1: # 0-10% loss
                score -= 5
            elif profit_ratio > -0.2: # 10-20% loss
                score -= 10
            elif profit_ratio > -0.3: # 20-30% loss
                score -= 20
            else:                    # >30% loss
                score -= 30
        
        # Growth factor (0-30 points)
        # Would need historical data to calculate
        
        # Ensure score is within bounds
        return max(0, min(100, score))

    def auto_manage_merchandise(self, wrestler_id=None):
        """
        Auto-generate merchandise items for a wrestler based on their popularity.
        If wrestler_id is None, generate for all wrestlers.
        """
        try:
            if wrestler_id:
                # Get a single wrestler
                conn = sqlite3.connect(db_path("wrestlers.db"))
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT id, name, reputation, fan_popularity
                    FROM wrestlers
                    WHERE id = ?
                """, (wrestler_id,))
                
                wrestler = cursor.fetchone()
                conn.close()
                
                if wrestler:
                    return self._create_merchandise_for_wrestler(wrestler[0], wrestler[1], wrestler[2], wrestler[3])
                return False
            else:
                # Get all wrestlers
                conn = sqlite3.connect(db_path("wrestlers.db"))
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT id, name, reputation, fan_popularity
                    FROM wrestlers
                """)
                
                wrestlers = cursor.fetchall()
                conn.close()
                
                success = True
                for wrestler in wrestlers:
                    result = self._create_merchandise_for_wrestler(wrestler[0], wrestler[1], wrestler[2], wrestler[3])
                    if not result:
                        success = False
                
                return success
        except Exception as e:
            print(f"Error auto-managing merchandise: {e}")
            return False
    
    def _create_merchandise_for_wrestler(self, wrestler_id, name, reputation, popularity):
        """Create merchandise items for a wrestler based on their popularity"""
        try:
            # Determine how many items to create based on popularity
            # Convert string popularity to numeric value if needed
            if isinstance(popularity, str):
                popularity_map = {
                    "Very Low": 1,
                    "Low": 2,
                    "Moderate": 3,
                    "High": 4,
                    "Very High": 5
                }
                popularity_value = popularity_map.get(popularity, 3)
            else:
                popularity_value = min(5, max(1, int(popularity / 20)))  # Scale 0-100 to 1-5
            
            # Number of items to create
            num_items = popularity_value
            
            # Types of merchandise based on popularity
            merch_types = ["T-Shirt"]
            
            if popularity_value >= 2:
                merch_types.append("Hat")
            if popularity_value >= 3:
                merch_types.append("Poster")
            if popularity_value >= 4:
                merch_types.append("Action Figure")
            if popularity_value >= 5:
                merch_types.append("Premium T-Shirt")
                merch_types.append("Championship Replica")
            
            # Create up to num_items merchandise items
            created = 0
            for i in range(min(num_items, len(merch_types))):
                # Basic item data
                merch_type = merch_types[i]
                item_name = f"{name} {merch_type}"
                
                # Base price depends on type
                base_prices = {
                    "T-Shirt": 25,
                    "Premium T-Shirt": 35,
                    "Hat": 20,
                    "Poster": 15,
                    "Action Figure": 30,
                    "Championship Replica": 100,
                    "Mug": 15,
                    "Wristband": 10
                }
                
                base_price = base_prices.get(merch_type, 20)
                
                # Production cost is typically 40-60% of base price
                import random
                production_cost = int(base_price * (0.4 + (random.random() * 0.2)))
                
                # Generate quality ratings (1-5 stars)
                design_quality = min(5, max(1, random.randint(1, 5) + int((reputation / 100) * 2)))
                material_quality = min(5, max(1, random.randint(1, 5)))
                uniqueness = min(5, max(1, random.randint(1, 5)))
                fan_appeal = min(5, max(1, random.randint(1, 5) + int((popularity_value / 5) * 2)))
                
                # Create the item
                self.create_merchandise_item(
                    wrestler_id=wrestler_id,
                    name=item_name,
                    merch_type=merch_type,
                    base_price=base_price,
                    production_cost=production_cost,
                    design_quality=design_quality,
                    material_quality=material_quality,
                    uniqueness=uniqueness,
                    fan_appeal=fan_appeal
                )
                
                created += 1
            
            return created > 0
            
        except Exception as e:
            print(f"Error creating merchandise for wrestler {wrestler_id}: {e}")
            return False 