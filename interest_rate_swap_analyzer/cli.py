import argparse
from datetime import datetime
from .swaps import Party, InterestRateSwap
from .analyzer import InterestRateSwapAnalyzer

def parse_date(date_str):
    return datetime.strptime(date_str, '%Y-%m-%d').date()

def main():
    parser = argparse.ArgumentParser(description='Analyze interest rate swaps')
    parser.add_argument('--party-a-name', required=True)
    parser.add_argument('--party-a-fixed-rate', type=float, required=True)
    parser.add_argument('--party-a-floating-delta', type=float, required=True)
    parser.add_argument('--party-b-name', required=True)
    parser.add_argument('--party-b-fixed-rate', type=float, required=True)
    parser.add_argument('--party-b-floating-delta', type=float, required=True)
    parser.add_argument('--swap-fixed-rate', type=float, required=True)
    parser.add_argument('--swap-floating-delta', type=float, required=True)
    parser.add_argument('--notional', type=float, required=True)
    parser.add_argument('--start-date', type=parse_date, required=True)
    parser.add_argument('--end-date', type=parse_date, required=True)
    
    args = parser.parse_args()
    
    party_a = Party(args.party_a_name, args.party_a_fixed_rate, 
                    args.party_a_floating_delta, "fixed")
    party_b = Party(args.party_b_name, args.party_b_fixed_rate, 
                    args.party_b_floating_delta, "floating")
    
    swap = InterestRateSwap(
        args.swap_fixed_rate,
        args.swap_floating_delta,
        args.notional,
        party_a,
        party_b,
        args.start_date,
        args.end_date
    )
    
    analyzer = InterestRateSwapAnalyzer(party_a, party_b, swap)
    analyzer.print_all()

if __name__ == '__main__':
    main()
