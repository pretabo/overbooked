import random
import time
from match_engine import simulate_match, load_wrestler_by_id, get_all_wrestlers
import sys

# Override time.sleep to do nothing
original_sleep = time.sleep
time.sleep = lambda x: None

# Disable QThread.msleep by monkey patching - fix the patching
from PyQt5.QtCore import QThread
original_msleep = QThread.msleep
# Use the correct function signature for a static method
QThread.msleep = lambda ms: None

# Number of matches to run
NUM_MATCHES = 10
FAST_MODE = True

# Additional optimizations
def apply_performance_patches():
    """Apply additional performance patches to the match engine."""
    import types
    from PyQt5.QtWidgets import QApplication
    
    # Save original methods
    original_process_events = QApplication.processEvents
    
    # Replace processEvents with a no-op in fast mode
    def patched_process_events(self):
        pass
    
    # Apply the patches
    QApplication.processEvents = types.MethodType(patched_process_events, QApplication)
    
    print("Applied performance patches to disable UI updates")
    
    return {
        "process_events": original_process_events
    }

def restore_original_functions(originals):
    """Restore original function implementations."""
    from PyQt5.QtWidgets import QApplication
    
    # Restore original methods
    time.sleep = original_sleep
    QThread.msleep = original_msleep
    if "process_events" in originals:
        QApplication.processEvents = originals["process_events"]
    
    print("Restored original functions")

def main():
    print("=== Match Engine Speed Test ===")
    print(f"Running {NUM_MATCHES} matches with fast_mode={FAST_MODE}")
    
    # Apply performance patches
    originals = apply_performance_patches()
    
    # Get all wrestlers from database
    all_wrestlers = get_all_wrestlers()
    if not all_wrestlers:
        print("Error: No wrestlers found in database")
        restore_original_functions(originals)
        return
    
    print(f"Found {len(all_wrestlers)} wrestlers in database")
    
    # Track total time
    start_time = time.time()
    
    # Run matches
    for i in range(NUM_MATCHES):
        # Select two random wrestlers
        w1_id, w1_name = random.choice(all_wrestlers)
        w2_id, w2_name = random.choice(all_wrestlers)
        
        # Load wrestler data
        wrestler1 = load_wrestler_by_id(w1_id)
        wrestler2 = load_wrestler_by_id(w2_id)
        
        if not wrestler1 or not wrestler2:
            print(f"Error loading wrestlers for match {i+1}")
            continue
        
        print(f"\nMatch {i+1}: {wrestler1['name']} vs {wrestler2['name']}")
        match_start = time.time()
        
        # Run match with no UI updates and fast mode
        result = simulate_match(
            wrestler1, 
            wrestler2, 
            log_function=lambda x: None,  # Disable logging output
            update_callback=None,         # Disable UI updates
            colour_callback=None,         # Disable commentary
            stats_callback=None,          # Disable stats tracking
            fast_mode=FAST_MODE           # Enable fast mode
        )
        
        match_time = time.time() - match_start
        print(f"  Winner: {result['winner']} by {result['finish_type']}")
        print(f"  Match quality: {result['quality']:.2f}")
        print(f"  Turns: {result['turns']}")
        print(f"  Time taken: {match_time:.3f} seconds")
    
    # Calculate and display total time
    total_time = time.time() - start_time
    avg_time = total_time / NUM_MATCHES
    
    print("\n=== Results ===")
    print(f"Total time for {NUM_MATCHES} matches: {total_time:.3f} seconds")
    print(f"Average time per match: {avg_time:.3f} seconds")
    
    # Restore original functions
    restore_original_functions(originals)

if __name__ == "__main__":
    main() 