import csv
import sqlite3
import os
import sys
import random
from datetime import datetime, timedelta
import pandas as pd

# Add the parent directory to the path so we can import from the db module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db.utils import db_path

# Function to safely convert to int with default
def safe_int(value, default=10):
    if value is None or value == '':
        return default
    try:
        return int(value)
    except (ValueError, TypeError):
        return default

# Function to format wrestler data
def format_wrestler(row):
    # Extract the name from the correct column
    name = row.get('name', '')
    if pd.isna(name) or name == '':
        # Try alternate name column
        alt_name = row.get('name.1', '')
        if not pd.isna(alt_name) and alt_name != '':
            name = alt_name
    
    # If still no name, return None to skip this wrestler
    if pd.isna(name) or name.strip() == '':
        print("Skipping wrestler with no name")
        return None
        
    # Ensure name is a string
    name = str(name).strip()
    
    # Extract attributes as a list in the correct order
    attributes = [
        safe_int(row.get('powerlifting', 10)),
        safe_int(row.get('grapple_control', 10)),
        safe_int(row.get('grip_strength', 10)),
        safe_int(row.get('agility', 10)),
        safe_int(row.get('balance', 10)),
        safe_int(row.get('flexibility', 10)),
        safe_int(row.get('recovery_rate', 10)),
        safe_int(row.get('conditioning', 10)),
        safe_int(row.get('chain_wrestling', 10)),
        safe_int(row.get('mat_transitions', 10)),
        safe_int(row.get('submission_technique', 10)),
        safe_int(row.get('strike_accuracy', 10)),
        safe_int(row.get('brawling_technique', 10)),
        safe_int(row.get('aerial_precision', 10)),
        safe_int(row.get('counter_timing', 10)),
        safe_int(row.get('pressure_handling', 10)),
        safe_int(row.get('promo_delivery', 10)),
        safe_int(row.get('fan_engagement', 10)),
        safe_int(row.get('entrance_presence', 10)),
        safe_int(row.get('presence_under_fire', 10)),
        safe_int(row.get('confidence', 10)),
        safe_int(row.get('focus', 10)),
        safe_int(row.get('resilience', 10)),
        safe_int(row.get('adaptability', 10)),
        safe_int(row.get('risk_assessment', 10)),
        safe_int(row.get('loyalty', 10)),
        safe_int(row.get('political_instinct', 10)),
        safe_int(row.get('determination', 10))
    ]
    
    # Extract signatures from the correct column
    signatures_str = row.get('signatures', '')
    if not pd.isna(signatures_str) and isinstance(signatures_str, str):
        signatures = [s.strip() for s in signatures_str.split(',') if s.strip()]
    else:
        signatures = []
    
    # Get finisher name, defaulting to a generated one if none exists
    finisher = row.get('finisher', '')
    if pd.isna(finisher) or finisher == '':
        finisher = f"{name}'s Finisher" if name else "Special Finisher"
    
    # Generate a random contract expiry date 2-4 years in the future
    current_date = datetime.now()
    expiry_date = current_date + timedelta(days=random.randint(730, 1460))  # 2-4 years
    contract_expiry = expiry_date.strftime('%Y-%m-%d')
    
    # Default reputation
    reputation = safe_int(row.get('reputation', 50), 50)
    
    # Fill in missing values with defaults
    return {
        'name': name,
        'attributes': attributes,
        'condition': safe_int(row.get('condition', 100), 100),
        'finisher': finisher,
        'reputation': reputation,
        'fan_popularity': 'High' if reputation > 70 else 'Moderate',
        'marketability': 'High' if reputation > 70 else 'Moderate',
        'merchandise_sales': 'Excellent' if reputation > 70 else 'Average',
        'contract_type': 'Full-Time',
        'contract_expiry': contract_expiry,
        'contract_value': 500000 + (reputation * 10000),
        'contract_promises': '',
        'contract_company': 'WWE',
        'locker_room_impact': 'Positive' if random.random() > 0.5 else 'Negative',
        'loyalty_level': row.get('loyalty_level', row.get('ambition', 'Moderate')),
        'ambition': row.get('ambition', 'Moderate'),
        'injury': '',
        'height': safe_int(row.get('height', 72), 72),
        'weight': safe_int(row.get('weight', 240), 240),
        'signatures': signatures
    }

# Function to generate finisher style based on attributes
def determine_finisher_style(wrestler):
    attributes = wrestler['attributes']
    
    # Determine style based on highest relevant attribute
    powerlifting = attributes[0]
    agility = attributes[3]
    submission_technique = attributes[11]
    
    if powerlifting > agility and powerlifting > submission_technique:
        return "slam"
    elif agility > powerlifting and agility > submission_technique:
        return "strike"
    elif submission_technique > powerlifting and submission_technique > agility:
        return "submission"
    else:
        # Default to slam if all are equal
        return "slam"

# Function to generate signature moves for wrestlers without them
def generate_signature_moves(wrestler_name, finisher_style):
    # Define move types based on style preference
    move_types = {
        "slam": ["slam", "strike", "slam"],
        "strike": ["strike", "strike", "slam"],
        "submission": ["submission", "strike", "slam"],
        "aerial": ["aerial", "strike", "slam"]
    }
    
    # Use the same style for signature moves
    move_type = move_types.get(finisher_style, ["strike", "slam"])[0]
    
    # Generate a name based on wrestler's name
    first_name = wrestler_name.split(' ')[0] if wrestler_name else "Special"
    signature_name = f"{first_name}'s Special"
    
    return [{
        "name": signature_name,
        "type": move_type,
        "damage": 7,
        "difficulty": 6
    }]

# Main function to import wrestlers
def import_wrestlers_from_csv(csv_path):
    print(f"Importing wrestlers from {csv_path}...")
    
    # Use pandas to read the CSV file
    try:
        df = pd.read_csv(csv_path)
        print(f"CSV columns: {df.columns.tolist()}")
        
        # Convert dataframe to list of dictionaries
        wrestlers_data = df.to_dict('records')
        print(f"Found {len(wrestlers_data)} wrestlers in CSV")
        
        # Debug first wrestler
        print("First wrestler data:")
        for key, value in wrestlers_data[0].items():
            print(f"  {key}: {value}")
        
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return
    
    formatted_wrestlers = []
    for w in wrestlers_data:
        formatted = format_wrestler(w)
        if formatted:  # Only add if not None (skipped due to no name)
            formatted_wrestlers.append(formatted)
    
    print(f"Formatted {len(formatted_wrestlers)} valid wrestlers")
    
    # Connect to the database
    conn = sqlite3.connect(db_path("wrestlers.db"))
    conn.execute(f"ATTACH DATABASE '{db_path('finishers.db')}' AS fdb")
    cursor = conn.cursor()
    
    # Store finisher and signature move IDs
    finisher_id_map = {}
    sig_id_map = {}
    
    # Load existing finishers
    cursor.execute("SELECT name, id FROM finishers")
    for name, id in cursor.fetchall():
        finisher_id_map[name] = id
    
    # Load existing signature moves
    cursor.execute("SELECT name, id FROM signature_moves")
    for name, id in cursor.fetchall():
        sig_id_map[name] = id
    
    # Count of successfully imported wrestlers
    imported_count = 0
    
    # Process each wrestler
    for wrestler in formatted_wrestlers:
        name = wrestler["name"]
        if not name:
            print("Skipping wrestler with no name")
            continue
            
        print(f"Processing {name}...")
        
        # Check if wrestler with same name already exists
        cursor.execute("SELECT id FROM wrestlers WHERE name = ?", (name,))
        if cursor.fetchone():
            print(f"Wrestler with name '{name}' already exists! Skipping.")
            continue
        
        # Handle finisher
        finisher_name = wrestler["finisher"]
        if not finisher_name or finisher_name.strip() == '':
            finisher_name = f"{name}'s Finisher"
        
        finisher_style = determine_finisher_style(wrestler)
        finisher_damage = 10  # Standard damage value
        finisher_difficulty = 8  # Standard difficulty
        
        # Check if finisher exists
        if finisher_name not in finisher_id_map:
            cursor.execute(
                "INSERT INTO finishers (name, style, damage, difficulty) VALUES (?, ?, ?, ?)",
                (finisher_name, finisher_style, finisher_damage, finisher_difficulty)
            )
            finisher_id_map[finisher_name] = cursor.lastrowid
        
        finisher_id = finisher_id_map[finisher_name]
        
        # Insert wrestler
        cursor.execute("""
            INSERT INTO wrestlers (
                name, reputation, condition, finisher_id,
                fan_popularity, marketability, merchandise_sales,
                contract_type, contract_expiry, contract_value,
                contract_promises, contract_company,
                locker_room_impact, loyalty_level, ambition, injury,
                height, weight
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            name, wrestler["reputation"], wrestler["condition"], finisher_id,
            wrestler["fan_popularity"], wrestler["marketability"], wrestler["merchandise_sales"],
            wrestler["contract_type"], wrestler["contract_expiry"], wrestler["contract_value"],
            wrestler["contract_promises"], wrestler["contract_company"],
            wrestler["locker_room_impact"], wrestler["loyalty_level"], wrestler["ambition"], wrestler["injury"],
            wrestler["height"], wrestler["weight"]
        ))
        
        wrestler_id = cursor.lastrowid
        
        # Insert attributes
        cursor.execute(f"""
            INSERT INTO wrestler_attributes (
                wrestler_id,
                powerlifting, grapple_control, grip_strength,
                agility, balance, flexibility, recovery_rate, conditioning,
                chain_wrestling, mat_transitions, submission_technique, strike_accuracy,
                brawling_technique, aerial_precision, counter_timing, pressure_handling,
                promo_delivery, fan_engagement, entrance_presence, presence_under_fire, confidence,
                focus, resilience, adaptability, risk_assessment,
                loyalty, political_instinct, determination
            ) VALUES ({','.join(['?'] * 29)})
        """, (wrestler_id, *wrestler["attributes"]))
        
        # Handle signature moves
        sig_names = wrestler["signatures"]
        if not sig_names:
            # Generate a signature move if none exists
            generated_sigs = generate_signature_moves(name, finisher_style)
            for sig in generated_sigs:
                sig_name = sig["name"]
                sig_type = sig["type"]
                sig_damage = sig["damage"]
                sig_difficulty = sig["difficulty"]
                
                # Insert signature move if it doesn't exist
                if sig_name not in sig_id_map:
                    cursor.execute(
                        "INSERT INTO signature_moves (name, type, damage, difficulty) VALUES (?, ?, ?, ?)",
                        (sig_name, sig_type, sig_damage, sig_difficulty)
                    )
                    sig_id_map[sig_name] = cursor.lastrowid
                
                # Link to wrestler
                cursor.execute(
                    "INSERT INTO wrestler_signature_moves (wrestler_id, signature_move_id) VALUES (?, ?)",
                    (wrestler_id, sig_id_map[sig_name])
                )
        else:
            for sig_name in sig_names:
                sig_name = sig_name.strip()
                if not sig_name:
                    continue
                
                # Default values
                sig_type = "strike"
                sig_damage = 7
                sig_difficulty = 6
                
                # Insert signature move if it doesn't exist
                if sig_name not in sig_id_map:
                    cursor.execute(
                        "INSERT INTO signature_moves (name, type, damage, difficulty) VALUES (?, ?, ?, ?)",
                        (sig_name, sig_type, sig_damage, sig_difficulty)
                    )
                    sig_id_map[sig_name] = cursor.lastrowid
                
                # Link to wrestler
                cursor.execute(
                    "INSERT INTO wrestler_signature_moves (wrestler_id, signature_move_id) VALUES (?, ?)",
                    (wrestler_id, sig_id_map[sig_name])
                )
                
        imported_count += 1
    
    # Commit changes
    conn.commit()
    conn.close()
    
    print(f"Successfully imported {imported_count} wrestlers into the database!")

if __name__ == "__main__":
    csv_path = db_path("data_input - wrestlersupdated.csv")
    import_wrestlers_from_csv(csv_path) 