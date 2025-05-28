from datetime import datetime, timedelta
import math

def calculate_venue_cost(venue, show_type):
    """Calculate venue cost based on type and show type"""
    base_cost = venue['base_cost']
    multipliers = {
        'weekly': 1.0,
        'ppv': 2.5,
        'special': 1.5
    }
    return base_cost * multipliers.get(show_type, 1.0)

def calculate_production_cost(show_type, production_level):
    """Calculate production costs for a show"""
    base_costs = {
        'weekly': 10000,
        'ppv': 50000,
        'special': 25000
    }
    return base_costs.get(show_type, 10000) * (1 + (production_level / 10))

def calculate_ticket_price(venue, show_type, wrestler_popularity):
    """Calculate appropriate ticket price"""
    base_prices = {
        'weekly': 20,
        'ppv': 50,
        'special': 35
    }
    
    base_price = base_prices.get(show_type, 20)
    venue_multiplier = 1 + (venue['prestige'] / 100)
    popularity_multiplier = 1 + (wrestler_popularity / 100)
    
    return base_price * venue_multiplier * popularity_multiplier

def calculate_expected_attendance(venue, show_type, wrestler_popularity):
    """Calculate expected attendance for a show"""
    base_attendance = venue['capacity'] * 0.7  # Start at 70% capacity
    
    # Adjust for show type
    type_multipliers = {
        'weekly': 0.8,
        'ppv': 1.0,
        'special': 0.9
    }
    
    # Adjust for wrestler popularity
    popularity_multiplier = 1 + (wrestler_popularity / 100)
    
    return math.floor(base_attendance * type_multipliers.get(show_type, 0.8) * popularity_multiplier)

def calculate_merchandise_sales(attendance, wrestler_popularity):
    """Calculate expected merchandise sales"""
    base_buyers = attendance * 0.1  # 10% of attendees
    popularity_multiplier = 1 + (wrestler_popularity / 100)
    
    return math.floor(base_buyers * popularity_multiplier)

def calculate_tv_ratings(show_type, wrestler_popularity, match_quality):
    """Calculate expected TV ratings"""
    base_ratings = {
        'weekly': 1.0,
        'ppv': 2.0,
        'special': 1.5
    }
    
    base = base_ratings.get(show_type, 1.0)
    popularity_multiplier = 1 + (wrestler_popularity / 100)
    quality_multiplier = 1 + (match_quality / 100)
    
    return base * popularity_multiplier * quality_multiplier

def calculate_sponsorship_value(show_type, expected_attendance, tv_ratings):
    """Calculate sponsorship value for a show"""
    base_values = {
        'weekly': 10000,
        'ppv': 50000,
        'special': 25000
    }
    
    base = base_values.get(show_type, 10000)
    attendance_multiplier = 1 + (expected_attendance / 10000)
    ratings_multiplier = 1 + (tv_ratings / 2)
    
    return base * attendance_multiplier * ratings_multiplier

def calculate_wrestler_salary(wrestler_value, contract_length, bonus_structure):
    """Calculate appropriate salary for a wrestler"""
    base_salary = wrestler_value / 12  # Monthly value
    
    # Adjust for contract length
    length_multiplier = 1 + (contract_length / 365) * 0.1  # 10% bonus per year
    
    # Add bonus structure value
    bonus_value = sum(bonus_structure.values()) if isinstance(bonus_structure, dict) else 0
    
    return base_salary * length_multiplier + bonus_value

def calculate_show_roi(revenue, costs):
    """Calculate return on investment for a show"""
    if costs == 0:
        return 0
    return (revenue - costs) / costs

def calculate_financial_health(cash, monthly_revenue, monthly_expenses):
    """Calculate financial health score (0-100)"""
    if monthly_expenses == 0:
        return 100
    
    if monthly_revenue == 0:
        return 0
        
    # Calculate basic metrics
    profit_margin = (monthly_revenue - monthly_expenses) / monthly_revenue
    cash_ratio = cash / monthly_expenses
    
    # Weight the metrics
    margin_weight = 0.6
    cash_weight = 0.4
    
    # Calculate score
    score = (
        (profit_margin * 100 * margin_weight) +
        (min(cash_ratio * 20, 100) * cash_weight)
    )
    
    return max(0, min(100, score))

def calculate_show_budget(show_type, venue_cost, production_level):
    """Calculate budget for a show"""
    base_budgets = {
        "weekly": 50000,
        "ppv": 200000,
        "special": 100000
    }
    
    base_budget = base_budgets.get(show_type, 50000)
    production_cost = production_level * 1000
    
    return base_budget + venue_cost + production_cost

def calculate_match_payout(match_quality, wrestler_popularity, is_title_match=False, is_main_event=False):
    """Calculate payout for a match"""
    base_payout = 1000 + (wrestler_popularity * 20)
    
    # Adjust for match quality
    quality_multiplier = 1 + (match_quality / 100)
    
    # Adjust for match type
    if is_title_match:
        base_payout *= 2
    
    if is_main_event:
        base_payout *= 1.5
    
    return base_payout * quality_multiplier

def get_fiscal_period(date=None):
    """Get fiscal year and month"""
    if date is None:
        date = datetime.now()
    return date.year, date.month

def calculate_contract_value(wrestler, duration_days):
    """Calculate the total value of a contract for budgeting"""
    monthly_salary = wrestler.get('base_salary', 5000)
    num_months = duration_days / 30
    return monthly_salary * num_months

def estimate_show_profit(show_type, venue, wrestler_popularity, production_level):
    """Estimate the profit for a show based on parameters"""
    venue_cost = calculate_venue_cost(venue, show_type)
    production_cost = calculate_production_cost(show_type, production_level)
    total_cost = venue_cost + production_cost
    
    expected_attendance = calculate_expected_attendance(venue, show_type, wrestler_popularity)
    ticket_price = calculate_ticket_price(venue, show_type, wrestler_popularity)
    ticket_revenue = expected_attendance * ticket_price
    
    merch_sales = calculate_merchandise_sales(expected_attendance, wrestler_popularity)
    merch_revenue = merch_sales * 20  # $20 per item
    
    tv_ratings = calculate_tv_ratings(show_type, wrestler_popularity, 70)  # Assume 70% match quality
    sponsorship_revenue = calculate_sponsorship_value(show_type, expected_attendance, tv_ratings)
    
    total_revenue = ticket_revenue + merch_revenue + sponsorship_revenue
    profit = total_revenue - total_cost
    
    return {
        'revenue': total_revenue,
        'costs': total_cost,
        'profit': profit,
        'roi': calculate_show_roi(total_revenue, total_cost)
    } 