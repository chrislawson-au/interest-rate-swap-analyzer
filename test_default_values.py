#!/usr/bin/env python3
"""Test script to verify calculations with default values from interactive_demo.py"""

from datetime import date
from interest_rate_swap_analyzer.swaps import Party, InterestRateSwap
from interest_rate_swap_analyzer.analyzer import InterestRateSwapAnalyzer, OpportunityAnalyzer

# Constants (from interactive_demo.py)
NOTIONAL = 1_000_000.0
START_DATE = date.today()
END_DATE = date(2030, 1, 1)

# Default values (from interactive_demo.py)
a_fixed = 10.45 / 100
a_float_delta = 0.75 / 100
b_fixed = 9.65 / 100
b_float_delta = 0.25 / 100
swap_fixed_rate = 9.6 / 100
swap_floating_rate = 0.10 / 100

# Build party objects
party_a = Party("Party A", a_fixed, a_float_delta, preference="fixed")
party_b = Party("Party B", b_fixed, b_float_delta, preference="floating")

# Create swap
opportunity_analyzer = OpportunityAnalyzer(party_a, party_b)
fixed_payer = opportunity_analyzer.find_fixed_rate_payer()
floating_payer = party_b if fixed_payer == party_a else party_a

swap = InterestRateSwap(
    swap_fixed_rate,
    swap_floating_rate,
    NOTIONAL,
    fixed_payer,
    floating_payer,
    START_DATE,
    END_DATE
)

# Analyze
analyzer = InterestRateSwapAnalyzer(party_a, party_b, swap)
summary = analyzer.analyze()

# Print results for verification
print("=" * 60)
print("INTEREST RATE SWAP ANALYSIS - DEFAULT VALUES")
print("=" * 60)
print()

print("INPUT VALUES:")
print(f"  Party A Fixed Rate: {a_fixed:.4f} ({a_fixed*100:.2f}%)")
print(f"  Party A Floating Delta: {a_float_delta:.4f} ({a_float_delta*100:.2f}%)")
print(f"  Party B Fixed Rate: {b_fixed:.4f} ({b_fixed*100:.2f}%)")
print(f"  Party B Floating Delta: {b_float_delta:.4f} ({b_float_delta*100:.2f}%)")
print(f"  Swap Fixed Rate: {swap_fixed_rate:.4f} ({swap_fixed_rate*100:.2f}%)")
print(f"  Swap Floating Delta: {swap_floating_rate:.4f} ({swap_floating_rate*100:.2f}%)")
print()

print("CALCULATED VALUES:")
print(f"  Total Arbitrage Available: {summary.total_arbitrage:.4f} ({summary.total_arbitrage*100:.2f}%)")
print(f"  Fixed Rate Payer: {fixed_payer.name}")
print(f"  Floating Rate Payer: {floating_payer.name}")
print()

print("PARTY A ANALYSIS:")
print(f"  Comparative Advantage: {summary.party_a_analysis.comparative_advantage.type}")
print(f"  Paying Position: {summary.party_a_analysis.paying_position}")
print(f"  Receiving Position: {summary.party_a_analysis.receiving_position}")
print(f"  Market Improvement: {summary.party_a_analysis.market_improvement:.4f} ({summary.party_a_analysis.market_improvement*100:.2f}%)")
print(f"  Total Cost: {summary.party_a_analysis.total_cost:.4f} ({summary.party_a_analysis.total_cost*100:.2f}%)")
print(f"  Benefit: {summary.party_a_analysis.market_paying_vs_swap_receiving_benefit:.4f} ({summary.party_a_analysis.market_paying_vs_swap_receiving_benefit*100:.2f}%)")
print()

print("PARTY B ANALYSIS:")
print(f"  Comparative Advantage: {summary.party_b_analysis.comparative_advantage.type}")
print(f"  Paying Position: {summary.party_b_analysis.paying_position}")
print(f"  Receiving Position: {summary.party_b_analysis.receiving_position}")
print(f"  Market Improvement: {summary.party_b_analysis.market_improvement:.4f} ({summary.party_b_analysis.market_improvement*100:.2f}%)")
print(f"  Total Cost: {summary.party_b_analysis.total_cost:.4f} ({summary.party_b_analysis.total_cost*100:.2f}%)")
print(f"  Benefit: {summary.party_b_analysis.market_paying_vs_swap_receiving_benefit:.4f} ({summary.party_b_analysis.market_paying_vs_swap_receiving_benefit*100:.2f}%)")
print()

print("FORMATTED RATES:")
print(f"  Party A Fixed Rate: {party_a.fixed_rate}")
print(f"  Party A Floating Rate: {party_a.floating_rate_delta}")
print(f"  Party B Fixed Rate: {party_b.fixed_rate}")
print(f"  Party B Floating Rate: {party_b.floating_rate_delta}")
print(f"  Swap Fixed Rate: {swap.fixed_rate}")
print(f"  Swap Floating Rate: {swap.floating_rate_delta}")
print()

print("=" * 60)
print("Use these values to verify JavaScript implementation")
print("=" * 60)
