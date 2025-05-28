def run_promo_tests(num_promos: int = 5) -> None:
    """Run comprehensive promo tests with real wrestler data."""
    results = defaultdict(list)
    
    print(f"\nRunning {num_promos} promos for each wrestler...")
    
    # Test different combinations of tones and themes
    test_styles = [
        ("boast", "legacy"),
        ("boast", "dominance"),
        ("insult", "betrayal"),
        ("insult", "power"),
        ("callout", "comeback"),
        ("callout", "legacy")
    ]
    
    for wrestler in TEST_WRESTLERS[:5]:  # Test first 5 wrestlers
        name = wrestler["name"]
        stats = extract_promo_relevant_stats(wrestler)
        print(f"\nTesting {name}")
        print("Stats:", json.dumps(stats, indent=2))
        
        # Convert wrestler to expected format
        engine_wrestler = convert_wrestler_format(wrestler)
        
        for tone, theme in test_styles:
            print(f"\nTesting {tone.title()} - {theme.title()} style:")
            for i in range(num_promos):
                engine = PromoEngine(engine_wrestler, tone=tone, theme=theme)
                result = engine.simulate()
                
                analysis = analyze_promo_performance(result["beats"])
                analysis["final_rating"] = result["final_rating"]
                analysis["tone"] = tone
                analysis["theme"] = theme
                results[name].append(analysis)
            
            # Calculate and display averages for this style
            style_results = [r for r in results[name] if r["tone"] == tone and r["theme"] == theme]
            avg_results = {
                "final_ratings": [],
                "confidence_avg": [],
                "momentum_avg": [],
                "score_avg": [],
                "recoveries": [],
                "cash_ins": []
            }
            
            for run in style_results:
                avg_results["final_ratings"].append(run["final_rating"])
                avg_results["confidence_avg"].append(run["confidence"]["avg"])
                avg_results["momentum_avg"].append(run["momentum"]["avg"])
                avg_results["score_avg"].append(run["scores"]["avg"])
                avg_results["recoveries"].append(run["confidence"]["recoveries"])
                avg_results["cash_ins"].append(run["momentum"]["cash_ins"])
            
            print(f"\n{tone.title()} - {theme.title()} Results:")
            print(f"Final Rating: {sum(avg_results['final_ratings']) / len(avg_results['final_ratings']):.2f}")
            print(f"Avg Confidence: {sum(avg_results['confidence_avg']) / len(avg_results['confidence_avg']):.2f}")
            print(f"Avg Momentum: {sum(avg_results['momentum_avg']) / len(avg_results['momentum_avg']):.2f}")
            print(f"Avg Score: {sum(avg_results['score_avg']) / len(avg_results['score_avg']):.2f}")
            print(f"Avg Recoveries: {sum(avg_results['recoveries']) / len(avg_results['recoveries']):.2f}")
            print(f"Avg Cash-ins: {sum(avg_results['cash_ins']) / len(avg_results['cash_ins']):.2f}") 