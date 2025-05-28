#!/usr/bin/env python3
"""
Demo script for the fixed promo formatting.
This script displays example beats with consistent formatting.
"""

def print_styled_beat(wrestler_name, promo_line, commentary, momentum, confidence):
    """Print a promo beat with consistent styling."""
    print(f"{wrestler_name}: ")
    print(f"'{promo_line}'. ")
    print(f"{commentary} ")
    print(f"⚡ {momentum:.1f} | 💪 {confidence:.1f} ")
    print()

def main():
    """Display example beats with consistent formatting."""
    print("\n========== PROMO CONSISTENCY DEMO ==========\n")
    
    # Example intro beat
    print("Edge and Grandmaster Sexay face off in the ring, microphones in hand.\n")
    
    # Example promo beats
    print_styled_beat(
        "Edge",
        "I'm not just going to beat you, Grandmaster Sexay. I'm going to make an example out of you.",
        "That was a devastating verbal assault!",
        34.6, 59.6
    )
    
    print_styled_beat(
        "Grandmaster Sexay",
        "I don't need to match your intensity, Edge. I just need to beat you.",
        "What a brilliant counter-point!",
        34.6, 59.6
    )
    
    print_styled_beat(
        "Edge",
        "The difference between us is simple: talent. I have it, you don't.",
        "The audience is going wild for that exchange!",
        44.7, 69.8
    )
    
    print_styled_beat(
        "Grandmaster Sexay",
        "You're nothing but a footnote in my career, Edge. A forgettable chapter at best.",
        "That's how you dominate a verbal confrontation!",
        54.5, 74.5
    )
    
    # Example summary beat
    print("Versus Promo Complete. Edge: 99.0 | Grandmaster Sexay: 92.2 | Edge won the verbal battle!\n")

if __name__ == "__main__":
    main() 