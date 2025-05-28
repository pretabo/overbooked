import random
import math
import logging
from datetime import datetime, timedelta
from src.db.business_db_manager import BusinessDBManager

# Initialize the business database manager
business_db = BusinessDBManager()

def generate_merch_stats():
    """Generate random merchandise quality stats"""
    design_quality = random.randint(1, 5)  # Changed to 1-5 star rating
    material_quality = random.randint(1, 5)  # Changed to 1-5 star rating
    uniqueness = random.randint(1, 5)  # Changed to 1-5 star rating
    fan_appeal = random.randint(1, 5)  # Changed to 1-5 star rating
    
    # Calculate overall quality as a weighted average (still 1-5 scale)
    overall_quality = round(design_quality * 0.35 + material_quality * 0.25 + 
                         uniqueness * 0.2 + fan_appeal * 0.2)
    
    return {
        'design_quality': design_quality,
        'material_quality': material_quality,
        'uniqueness': uniqueness, 
        'fan_appeal': fan_appeal,
        'overall_quality': overall_quality
    }

def create_merchandise_item(wrestler_id, name, merch_type, base_price=None, production_cost=None):
    """Create a new merchandise item for a wrestler with random stats"""
    # Get default price and cost based on type if not provided
    if base_price is None or production_cost is None:
        default_prices = {
            'T-Shirt': (3, 1),  # Changed to star rating (price stars, cost stars)
            'Premium T-Shirt': (4, 2),
            'Hat': (2, 1),
            'Poster': (2, 1),
            'Action Figure': (4, 2),
            'Championship Replica': (5, 3),
            'Mug': (2, 1),
            'Wristband': (1, 1)
        }
        
        if merch_type in default_prices:
            base_price = base_price or default_prices[merch_type][0]
            production_cost = production_cost or default_prices[merch_type][1]
        else:
            base_price = base_price or 2  # Default to 2 stars for price
            production_cost = production_cost or 1  # Default to 1 star for cost
    
    # Generate random stats
    stats = generate_merch_stats()
    
    # Create the merchandise item
    item_id = business_db.create_merchandise_item(
        wrestler_id=wrestler_id,
        name=name,
        merch_type=merch_type,
        base_price=base_price,
        production_cost=production_cost,
        design_quality=stats['design_quality'],
        material_quality=stats['material_quality'],
        uniqueness=stats['uniqueness'],
        fan_appeal=stats['fan_appeal'],
        overall_quality=stats['overall_quality']
    )
    
    return item_id

def calculate_daily_sales(merch_item, wrestler_popularity):
    """Calculate daily sales for a merchandise item"""
    # Base sales is related to wrestler popularity but merchandise quality matters too
    quality_factor = merch_item['overall_quality'] / 100.0
    popularity_factor = wrestler_popularity / 100.0
    
    # Base expected daily sales (very rough estimate)
    base_sales = 0.5  # 0.5 items per day for an average item and wrestler
    
    # Adjust by popularity and quality
    adjusted_sales = base_sales * (0.5 * popularity_factor + 0.5 * quality_factor)
    
    # Add some randomness (sales can vary by ±30%)
    randomness = random.uniform(0.7, 1.3)
    final_sales = adjusted_sales * randomness
    
    # Different merch types have different sales volumes
    type_multipliers = {
        'T-Shirt': 1.0,
        'Premium T-Shirt': 0.7,
        'Hat': 0.6,
        'Poster': 0.5,
        'Action Figure': 0.3,
        'Championship Replica': 0.05,  # Rare, expensive item
        'Mug': 0.4,
        'Wristband': 0.8
    }
    
    multiplier = type_multipliers.get(merch_item['type'], 1.0)
    final_sales *= multiplier
    
    # Always return at least 0
    quantity = max(0, round(final_sales))
    
    return quantity

def calculate_event_sales(merch_item, wrestler_popularity, is_on_card, attendance):
    """Calculate merchandise sales during an event"""
    # Base calculation is similar to daily sales
    quality_factor = merch_item['overall_quality'] / 100.0
    popularity_factor = wrestler_popularity / 100.0
    
    # Base expected sales (percentage of attendance)
    base_percentage = 0.01  # 1% of attendees might buy merch for an average wrestler
    
    # If wrestler is on the card, bigger boost
    if is_on_card:
        base_percentage *= 3  # Triple the sales for wrestlers on the card
    
    # Adjust by popularity and quality
    adjusted_percentage = base_percentage * (0.6 * popularity_factor + 0.4 * quality_factor)
    
    # Expected sales based on attendance
    expected_sales = attendance * adjusted_percentage
    
    # Add some randomness (sales can vary by ±25%)
    randomness = random.uniform(0.75, 1.25)
    final_sales = expected_sales * randomness
    
    # Different merch types have different sales volumes
    type_multipliers = {
        'T-Shirt': 1.0,
        'Premium T-Shirt': 0.7,
        'Hat': 0.8,  # Hats sell better at events
        'Poster': 0.4,
        'Action Figure': 0.5,  # Action figures sell better at events
        'Championship Replica': 0.1,
        'Mug': 0.3,
        'Wristband': 1.2  # Wristbands sell very well at events
    }
    
    multiplier = type_multipliers.get(merch_item['type'], 1.0)
    final_sales *= multiplier
    
    # Always return at least 0
    quantity = max(0, round(final_sales))
    
    return quantity

def record_merchandise_sale(merch_item, wrestler_id, quantity, show_id=None, sales_type="daily"):
    """Record a merchandise sale in the database"""
    # Calculate financials
    total_amount = quantity * merch_item['base_price']
    production_cost = quantity * merch_item['production_cost']
    profit = total_amount - production_cost
    
    # Calculate profit split
    company_split = merch_item['company_split'] / 100.0
    wrestler_split = merch_item['wrestler_split'] / 100.0
    
    company_profit = profit * company_split
    wrestler_profit = profit * wrestler_split
    
    # Record the sale
    sale_id = business_db.record_merchandise_sale(
        wrestler_id=wrestler_id,
        merchandise_item_id=merch_item['id'],
        show_id=show_id,
        quantity=quantity,
        price=merch_item['base_price'],
        total_amount=total_amount,
        production_cost=production_cost,
        profit=profit,
        company_profit=company_profit,
        wrestler_profit=wrestler_profit,
        sales_type=sales_type
    )
    
    # Record company income in financial transactions
    if company_profit > 0:
        business_db.record_transaction(
            amount=company_profit,
            category="merchandise_sales",
            description=f"Merchandise sales: {quantity} x {merch_item['name']}",
            transaction_type="income",
            wrestler_id=wrestler_id,
            show_id=show_id
        )
    
    # Record production cost expense
    business_db.record_transaction(
        amount=-production_cost,
        category="merchandise_production",
        description=f"Production cost: {quantity} x {merch_item['name']}",
        transaction_type="expense",
        wrestler_id=wrestler_id,
        show_id=show_id
    )
    
    # Record wrestler royalty payment
    if wrestler_profit > 0:
        business_db.record_transaction(
            amount=-wrestler_profit,
            category="wrestler_royalties",
            description=f"Royalty payment for {merch_item['name']} sales",
            transaction_type="expense",
            wrestler_id=wrestler_id,
            show_id=show_id
        )
    
    return sale_id

def process_daily_merchandise_sales():
    """Process daily merchandise sales for all active items"""
    # Get all active merchandise items
    items = business_db.get_all_active_merchandise()
    
    total_items_sold = 0
    total_revenue = 0
    
    for item in items:
        # Get wrestler's popularity
        wrestler = business_db.get_wrestler(item['wrestler_id'])
        if not wrestler:
            continue
            
        popularity = wrestler.get('popularity', 50)
        
        # Calculate daily sales quantity
        quantity = calculate_daily_sales(item, popularity)
        
        if quantity > 0:
            # Record the sale
            record_merchandise_sale(item, item['wrestler_id'], quantity)
            
            total_items_sold += quantity
            total_revenue += quantity * item['base_price']
    
    logging.info(f"Daily merchandise sales processed: {total_items_sold} items sold for ${total_revenue:.2f}")
    return total_items_sold, total_revenue

def process_event_merchandise_sales(show_id):
    """Process merchandise sales for an event"""
    # Get show details
    show = business_db.get_show_details(show_id)
    if not show:
        logging.error(f"Cannot process event merchandise: Show {show_id} not found")
        return 0, 0
    
    # Get attendance
    attendance = show.get('attendance', 0)
    if attendance <= 0:
        logging.info(f"No merchandise sales: Show {show_id} had no attendance")
        return 0, 0
    
    # Get wrestlers on the card
    wrestlers_on_card = set()
    for match in show.get('matches', []):
        wrestlers_on_card.add(match['wrestler1_id'])
        wrestlers_on_card.add(match['wrestler2_id'])
    
    # Get all active merchandise items
    items = business_db.get_all_active_merchandise()
    
    total_items_sold = 0
    total_revenue = 0
    
    for item in items:
        # Get wrestler's popularity
        wrestler = business_db.get_wrestler(item['wrestler_id'])
        if not wrestler:
            continue
            
        popularity = wrestler.get('popularity', 50)
        
        # Check if wrestler is on the card
        is_on_card = item['wrestler_id'] in wrestlers_on_card
        
        # Calculate event sales quantity
        quantity = calculate_event_sales(item, popularity, is_on_card, attendance)
        
        if quantity > 0:
            # Record the sale
            record_merchandise_sale(
                item, 
                item['wrestler_id'], 
                quantity, 
                show_id=show_id, 
                sales_type="event"
            )
            
            total_items_sold += quantity
            total_revenue += quantity * item['base_price']
    
    # Update event financial impact
    business_db.update_event_financial_impact(
        show_id=show_id,
        merchandise_sales=total_revenue
    )
    
    logging.info(f"Event merchandise sales processed: {total_items_sold} items sold for ${total_revenue:.2f}")
    return total_items_sold, total_revenue

def auto_manage_merchandise(wrestler_id=None):
    """Auto-generate merchandise for a wrestler or all wrestlers"""
    if wrestler_id:
        # Get wrestler details
        wrestler = business_db.get_wrestler(wrestler_id)
        if not wrestler:
            logging.error(f"Cannot auto-manage merchandise: Wrestler {wrestler_id} not found")
            return False
            
        popularity = wrestler.get('popularity', 50)
        
        # Get existing merchandise for this wrestler
        existing_items = business_db.get_wrestler_merchandise(wrestler_id)
        
        # Determine how many items based on popularity
        if popularity >= 80:  # Main eventer
            target_item_count = 4
        elif popularity >= 60:  # Midcarder
            target_item_count = 3
        elif popularity >= 40:  # Undercarder
            target_item_count = 2
        else:  # Jobber
            target_item_count = 1
            
        # Create items if needed
        current_count = len(existing_items)
        
        if current_count < target_item_count:
            # Choose item types based on popularity
            available_types = [
                'T-Shirt',
                'Hat',
                'Poster'
            ]
            
            if popularity >= 60:
                available_types.extend(['Premium T-Shirt', 'Mug', 'Wristband'])
                
            if popularity >= 80:
                available_types.extend(['Action Figure', 'Championship Replica'])
            
            # Check what types already exist
            existing_types = [item['type'] for item in existing_items]
            
            # First, ensure they have a T-Shirt
            if 'T-Shirt' not in existing_types and 'T-Shirt' in available_types:
                name = f"{wrestler['name']} T-Shirt"
                create_merchandise_item(wrestler_id, name, 'T-Shirt')
                current_count += 1
            
            # Add more items up to the target count
            while current_count < target_item_count:
                # Filter out types they already have
                remaining_types = [t for t in available_types if t not in existing_types]
                
                if not remaining_types:
                    # If all types are used, duplicate a T-Shirt with a different design
                    if current_count < target_item_count:
                        name = f"{wrestler['name']} Special T-Shirt"
                        create_merchandise_item(wrestler_id, name, 'T-Shirt')
                        current_count += 1
                    break
                
                # Choose a random type
                chosen_type = random.choice(remaining_types)
                
                # Create a name for the item
                name = f"{wrestler['name']} {chosen_type}"
                
                # Create the item
                create_merchandise_item(wrestler_id, name, chosen_type)
                
                # Update counters
                current_count += 1
                existing_types.append(chosen_type)
            
        return True
    else:
        # Auto-manage for all wrestlers
        wrestlers = business_db.get_all_wrestlers()
        success_count = 0
        
        for wrestler in wrestlers:
            if auto_manage_merchandise(wrestler['id']):
                success_count += 1
                
        logging.info(f"Auto-managed merchandise for {success_count} wrestlers")
        return success_count > 0 