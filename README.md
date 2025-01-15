# Interest Rate Swap Analyzer

A Python package for analyzing interest rate swaps, comparing advantages between parties, and visualizing swap outcomes.

## Installation

```bash
pip install interest-rate-swap-analyzer
```

## Features

- Calculate comparative advantages in interest rate swaps
- Analyze arbitrage opportunities
- Visualize swap cash flows
- Command-line interface for quick analysis
- Detailed reporting capabilities

## Quick Start

```python
from interest_rate_swap_analyzer import Party, InterestRateSwap, InterestRateSwapAnalyzer
from datetime import date

# Create parties
party_a = Party("Company A", fixed_rate=0.05, floating_rate_delta=0.02, preference="fixed")
party_b = Party("Bank B", fixed_rate=0.06, floating_rate_delta=0.01, preference="floating")

# Create swap
swap = InterestRateSwap(
    fixed_rate=0.055,
    floating_rate_delta=0.015,
    notional=1000000,
    fixed_rate_payer=party_a,
    floating_rate_payer=party_b,
    start_date=date(2023, 1, 1),
    end_date=date(2024, 1, 1)
)

# Analyze swap
analyzer = InterestRateSwapAnalyzer(party_a, party_b, swap)
results = analyzer.analyze()

# Get formatted report
print(analyzer.format_analysis_report(results))

# Or get results as DataFrame
df = analyzer.to_dataframe(results)
print(df)
```

## Development

Setup development environment:

```bash
pip install -e ".[dev]"
pytest
```

## License

MIT License
