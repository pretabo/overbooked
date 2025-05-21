import random
import time
from match_engine import simulate_match, load_wrestler_by_id, get_all_wrestlers

def run_matches_with_config(num_matches, disable_delays=False, fast_mode=False):
    """Run matches with optional performance improvements"""
    
    # Save original functions
    originals = {}
    if disable_delays:
        # Disable UI delays
        from PyQt5.QtCore import QThread
        originals['msleep'] = QThread.msleep
        QThread.msleep = lambda x: None
        
        from PyQt5.QtWidgets import QApplication
        originals['processEvents'] = QApplication.processEvents
        QApplication.processEvents = lambda: None
        
        print("UI delays disabled")
    
    # Get wrestlers
    all_wrestlers = get_all_wrestlers()
    if not all_wrestlers:
        print("No wrestlers found in database")
        return
    
    # Track timing
    start_time = time.time()
    match_times = []
    match_turns = []
    
    for i in range(num_matches):
        # Select random wrestlers
        w1_id, w1_name = random.choice(all_wrestlers)
        w2_id, w2_name = random.choice(all_wrestlers)
        
        # Load wrestler data
        wrestler1 = load_wrestler_by_id(w1_id)
        wrestler2 = load_wrestler_by_id(w2_id)
        
        if not wrestler1 or not wrestler2:
            continue
        
        print(f"\nMatch {i+1}: {wrestler1['name']} vs {wrestler2['name']}")
        match_start = time.time()
        
        # Run the match
        result = simulate_match(
            wrestler1,
            wrestler2,
            log_function=lambda x: None,  # Disable logging
            update_callback=None,         # Disable UI updates
            colour_callback=None,         # Disable commentary
            stats_callback=None,          # Disable stats
            fast_mode=fast_mode           # Fast mode setting
        )
        
        match_time = time.time() - match_start
        match_times.append(match_time)
        match_turns.append(result.get('turns', 0))
        
        print(f"  Winner: {result.get('winner', 'None')} by {result.get('win_type', 'unknown')}")
        print(f"  Match quality: {result.get('quality', 0):.2f}")
        print(f"  Turns: {result.get('turns', 0)}")
        print(f"  Time: {match_time:.3f} seconds")
    
    # Calculate statistics
    total_time = time.time() - start_time
    avg_time = sum(match_times) / len(match_times) if match_times else 0
    avg_turns = sum(match_turns) / len(match_turns) if match_turns else 0
    
    # Print results
    print("\n=== Results ===")
    print(f"Config: disable_delays={disable_delays}, fast_mode={fast_mode}")
    print(f"Total time for {num_matches} matches: {total_time:.3f} seconds")
    print(f"Average time per match: {avg_time:.3f} seconds")
    print(f"Average turns per match: {avg_turns:.1f}")
    print(f"Average time per turn: {(avg_time / avg_turns if avg_turns else 0):.3f} seconds")
    
    # Restore original functions
    if disable_delays:
        if 'msleep' in originals:
            QThread.msleep = originals['msleep']
        if 'processEvents' in originals:
            QApplication.processEvents = originals['processEvents']
    
    return {
        'total_time': total_time,
        'avg_time': avg_time,
        'avg_turns': avg_turns,
        'time_per_turn': avg_time / avg_turns if avg_turns else 0
    }

if __name__ == "__main__":
    num_matches = 5
    print(f"Running {num_matches} test matches with different configurations")
    
    # Test 1: Normal mode with delays
    print("\n=== TEST 1: Normal mode with UI delays ===")
    normal_results = run_matches_with_config(num_matches, disable_delays=False, fast_mode=False)
    
    # Test 2: Normal mode without delays
    print("\n=== TEST 2: Normal mode WITHOUT UI delays ===")
    nodelay_results = run_matches_with_config(num_matches, disable_delays=True, fast_mode=False)
    
    # Test 3: Fast mode with delays disabled
    print("\n=== TEST 3: Fast mode WITHOUT UI delays ===")
    fast_results = run_matches_with_config(num_matches, disable_delays=True, fast_mode=True)
    
    # Compare results
    print("\n=== COMPARISON ===")
    if normal_results and nodelay_results:
        speedup = normal_results['avg_time'] / nodelay_results['avg_time'] if nodelay_results['avg_time'] > 0 else 0
        print(f"Disabling UI delays makes matches {speedup:.1f}x faster")
    
    if nodelay_results and fast_results:
        speedup = nodelay_results['avg_time'] / fast_results['avg_time'] if fast_results['avg_time'] > 0 else 0
        print(f"Fast mode makes matches {speedup:.1f}x faster than just disabling delays")
    
    if normal_results and fast_results:
        speedup = normal_results['avg_time'] / fast_results['avg_time'] if fast_results['avg_time'] > 0 else 0
        print(f"Combined optimizations make matches {speedup:.1f}x faster than normal mode") 