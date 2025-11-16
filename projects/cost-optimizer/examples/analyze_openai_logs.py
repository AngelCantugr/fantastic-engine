"""
Example: Analyzing OpenAI API Logs

This example demonstrates how to analyze OpenAI API logs
to find cost optimization opportunities.
"""

from cost_optimizer import CostAnalyzer
import os


def main():
    """Run cost analysis on sample OpenAI logs."""

    # Path to sample logs
    sample_log_path = os.path.join(
        os.path.dirname(__file__),
        "..",
        "data",
        "sample_logs",
        "openai_sample.json",
    )

    # Initialize analyzer for OpenAI
    analyzer = CostAnalyzer(
        provider="openai",
        similarity_threshold=0.85,
        min_savings=5.00,
    )

    print("🔍 Loading OpenAI API logs...")
    analyzer.load_logs(sample_log_path)

    print("📊 Analyzing costs and patterns...")
    results = analyzer.analyze()

    print("\n💡 Detecting optimization opportunities...")
    optimizations = analyzer.get_optimizations()

    print("\n💰 Calculating potential savings...")
    savings = analyzer.calculate_savings()

    print("\n📈 Generating report...")
    analyzer.generate_report(
        output_format="terminal",
        top_n=10,
        include_details=True,
    )

    # Example: Export to CSV for further analysis
    print("\n💾 Exporting results...")
    analyzer.generate_report(
        output_format="csv",
        output_path="./reports/cost_analysis.csv",
    )

    print("\n✅ Analysis complete!")
    print(f"   Total cost: ${results['total_cost']:.2f}")
    print(f"   Potential savings: ${savings['total']:.2f}")
    print(f"   Optimization opportunities: {len(optimizations)}")


if __name__ == "__main__":
    main()
