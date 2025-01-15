from dataclasses import dataclass
from typing import Dict, Tuple, Optional, List
from functools import cached_property
import logging
import pandas as pd
from .swaps import Party, InterestRateSwap

logger = logging.getLogger(__name__)

@dataclass
class ComparativeAnalysis:
    type: str
    rate: float

@dataclass
class PartyComparatives:
    fixed: float
    floating: float

@dataclass
class SwapAnalysisResult:
    """Contains all analysis results for a party in the swap."""
    party: Party
    comparative_advantage: ComparativeAnalysis
    net_benefit: float
    paying_position: str
    receiving_position: str
    market_improvement: float
    total_cost: float

@dataclass
class SwapSummary:
    """Overall swap analysis summary."""
    total_arbitrage: float
    fixed_rate: float
    floating_rate: float
    party_a_analysis: SwapAnalysisResult
    party_b_analysis: SwapAnalysisResult

class InterestRateSwapAnalyzer:
    """
    Analyzes interest rate swaps to determine comparative advantages and optimal positions.
    
    Attributes:
        party_a: First party in the swap
        party_b: Second party in the swap
        interest_rate_swap: The swap being analyzed
    """
    
    def __init__(self, party_a: Party, party_b: Party, interest_rate_swap: InterestRateSwap):
        if not all([party_a, party_b, interest_rate_swap]):
            raise ValueError("All parameters must be provided")
        
        self.party_a = party_a
        self.party_b = party_b
        self.interest_rate_swap = interest_rate_swap
        logger.info(f"Initializing swap analysis between {party_a} and {party_b}")

    def analyze(self) -> SwapSummary:
        """Perform complete analysis of the swap and return structured results."""
        try:
            party_a_analysis = self._analyze_party(self.party_a)
            party_b_analysis = self._analyze_party(self.party_b)
            
            return SwapSummary(
                total_arbitrage=self.calculate_total_arbitrage_available(),
                fixed_rate=self.interest_rate_swap.fixed_rate.rate,
                floating_rate=self.interest_rate_swap.floating_rate_delta.rate,
                party_a_analysis=party_a_analysis,
                party_b_analysis=party_b_analysis
            )
        except Exception as e:
            logger.error(f"Error analyzing swap: {str(e)}")
            raise

    def _analyze_party(self, party: Party) -> SwapAnalysisResult:
        """Analyze swap impact for a specific party."""
        try:
            paying_position = self.interest_rate_swap.get_paying_position_for_party(party)
            receiving_position = self.interest_rate_swap.get_receiving_position_for_party(party)
            net_benefit = self.get_net_benefit(party)
            
            return SwapAnalysisResult(
                party=party,
                comparative_advantage=self.comparative_advantages[party],
                net_benefit=net_benefit,
                paying_position=paying_position,
                receiving_position=receiving_position,
                market_improvement=self._calculate_market_improvement(party),
                total_cost=self._calculate_total_cost(party)
            )
        except Exception as e:
            logger.error(f"Error analyzing party {party}: {str(e)}")
            raise

    def _calculate_market_improvement(self, party: Party) -> float:
        """Calculate how much better the swap is compared to market rates."""
        try:
            return (
                party.get_rate(self.comparative_disadvantages[party].type).rate -
                (self.interest_rate_swap.get_rate(
                    self.interest_rate_swap.get_paying_position_for_party(party)
                ).rate + self.get_net_benefit(party))
            )
        except Exception as e:
            logger.error(f"Error calculating market improvement: {str(e)}")
            raise

    def _calculate_total_cost(self, party: Party) -> float:
        """Calculate total cost for party including swap payments."""
        try:
            return (
                self.interest_rate_swap.get_rate(
                    self.interest_rate_swap.get_paying_position_for_party(party)
                ).rate + self.get_net_benefit(party)
            )
        except Exception as e:
            logger.error(f"Error calculating total cost: {str(e)}")
            raise

    @cached_property
    def comparatives(self) -> Dict[Party, PartyComparatives]:
        return {
            party: PartyComparatives(**self.comparatives_for_party(party))
            for party in [self.party_a, self.party_b]
        }

    @cached_property
    def comparative_advantages(self) -> Dict[Party, ComparativeAnalysis]:
        return {
            party: ComparativeAnalysis(**self.determine_comparative_advantage_for_party(party))
            for party in [self.party_a, self.party_b]
        }

    @cached_property
    def comparative_disadvantages(self) -> Dict[Party, ComparativeAnalysis]:
        return {
            party: ComparativeAnalysis(**self.determine_comparative_disadvantage_for_party(party))
            for party in [self.party_a, self.party_b]
        }

    def print_absolute_advantages(self):
        print("Absolute Advantages:")

        adv = {
            "type": ["Fixed", "Floating"],
            "party": [self.party_a, self.party_b]
        }

        fixed = "None"
        if self.party_a.fixed_rate < self.party_b.fixed_rate:
            fixed = self.party_a
        elif self.party_a.fixed_rate > self.party_b.fixed_rate:
            fixed = self.party_b

        # Note: Assuming LIBOR is the benchmark floating rate
        floating = "None"
        if self.party_a.floating_rate_delta < self.party_b.floating_rate_delta:
            floating = self.party_a
        elif self.party_a.floating_rate_delta > self.party_b.floating_rate_delta:
            floating = self.party_b

        print(pd.DataFrame({"Type": ["Fixed", "Floating"], "Party": [fixed, floating]}))

    def print_comparative_advantages(self):
        print(pd.DataFrame(
            {"Party": [self.party_a, self.party_b], 
             "Fixed Comparative": [self.comparatives[self.party_a].fixed, self.comparatives[self.party_b].fixed], 
             "Floating Comparative": [self.comparatives[self.party_a].floating, self.comparatives[self.party_b].floating]}
        ))

        print("Comparative Advantages: (Smaller is better)")
        for party in [self.party_a, self.party_b]:
            print(f"  {party.name} has a comparative advantage in the {self.comparative_advantages[party].type} market")


    def determine_comparative_advantage_for_party(self, party: Party) -> Dict[str, float]:
        if self.comparatives[party].fixed < self.comparatives[party].floating:
            return {"type": "fixed", "rate": self.comparatives[party].fixed}
        elif self.comparatives[party].floating < self.comparatives[party].fixed:
            return {"type": "floating", "rate": self.comparatives[party].floating}
        else:
            return {"type": "none", "rate": 0}
            
    def determine_comparative_disadvantage_for_party(self, party: Party) -> Dict[str, float]:
        if self.comparatives[party].fixed > self.comparatives[party].floating:
            return {"type": "fixed", "rate": self.comparatives[party].fixed}
        elif self.comparatives[party].floating > self.comparatives[party].fixed:
            return {"type": "floating", "rate": self.comparatives[party].floating}
        else:
            return {"type": "none", "rate": 0}

    def comparatives_for_party(self, party: Party) -> Dict[str, float]:
        counterparty = self.party_b if party == self.party_a else self.party_a
        fixed_rate_difference = party.fixed_rate - counterparty.fixed_rate
        floating_rate_difference = party.floating_rate_delta - counterparty.floating_rate_delta

        return {"fixed": fixed_rate_difference.rate, "floating": floating_rate_difference.rate}

    def get_net_benefit(self, party: Party) -> float:
        """Calculate the net benefit for a party in the swap."""
        try:
            return party.get_rate(self.comparative_advantages[party].type) - \
                   self.interest_rate_swap.get_rate(self.interest_rate_swap.get_receiving_position_for_party(party))
        except Exception as e:
            raise ValueError(f"Could not calculate net benefit for {party}: {str(e)}")

    def calculate_total_arbitrage_available(self) -> float:
        return self.comparative_advantages[self.party_a].rate + self.comparative_advantages[self.party_b].rate
    
    def print_arbitrage_analysis(self):
        print()
        print(f"Total arbitrage available: {self.calculate_total_arbitrage_available():.2%}")

    def print_swap_details(self):
        print()
        print("Swap details")
        print(f" Fixed leg rate: {self.interest_rate_swap.fixed_rate}")
        print(f" Floating leg rate: {self.interest_rate_swap.floating_rate_delta}")

    def print_analysis(self):
        """Print a full analysis of the swap from each party's perspective."""
        for party in [self.party_a, self.party_b]:
            print()
            print(f"Actions for {party}")
            print(f"* borrow from {self.comparative_advantages[party].type} rate market at {party.get_rate(self.comparative_advantages[party].type)}")
            print(f"* receives {self.interest_rate_swap.get_receiving_position_for_party(party)} rate of {self.interest_rate_swap.get_rate(self.interest_rate_swap.get_receiving_position_for_party(party))} from swap")
            print(f"* this is a net benefit of {self.get_net_benefit(party)}")
            print(f"* has {self.interest_rate_swap.get_paying_position_for_party(party)} rate position in swap paying { self.interest_rate_swap.get_rate(self.interest_rate_swap.get_paying_position_for_party(party))}")
            print(f"* net position is {self.interest_rate_swap.get_rate(self.interest_rate_swap.get_paying_position_for_party(party))} + {self.get_net_benefit(party)} = {self.interest_rate_swap.get_rate(self.interest_rate_swap.get_paying_position_for_party(party)) + self.get_net_benefit(party)}")
            print(f"* ({party.get_rate(self.comparative_disadvantages[party].type) - (self.interest_rate_swap.get_rate(self.interest_rate_swap.get_paying_position_for_party(party)) + self.get_net_benefit(party))} better than the {party.get_rate(self.comparative_disadvantages[party].type)} avialable on the open market) ")

    def print_party_details(self):
        print()
        print(pd.DataFrame({"Party": [self.party_a, self.party_b], "Fixed Rate": [self.party_a.fixed_rate, self.party_b.fixed_rate], "Floating Rate Delta": [self.party_a.floating_rate_delta, self.party_b.floating_rate_delta]}))

    def print_all(self):
        self.print_party_details()

        self.print_absolute_advantages()

        self.print_comparative_advantages() 

        self.print_arbitrage_analysis()

        self.print_swap_details()

        self.print_analysis()

    def format_analysis_report(self, summary: SwapSummary) -> str:
        """Generate formatted analysis report."""
        report = []
        report.append("=== Swap Analysis Report ===")
        report.append(f"Total arbitrage available: {summary.total_arbitrage:.2%}")
        report.append(f"\nFixed rate: {summary.fixed_rate:.2%}")
        report.append(f"Floating rate: {summary.floating_rate:.2%}")
        
        for party_analysis in [summary.party_a_analysis, summary.party_b_analysis]:
            report.append(f"\nAnalysis for {party_analysis.party}")
            report.append(f"Comparative advantage: {party_analysis.comparative_advantage.type}")
            report.append(f"Net benefit: {party_analysis.net_benefit:.2%}")
            report.append(f"Market improvement: {party_analysis.market_improvement:.2%}")
            
        return "\n".join(report)

    def to_dataframe(self, summary: SwapSummary) -> pd.DataFrame:
        """Convert analysis results to a pandas DataFrame."""
        return pd.DataFrame({
            'Party': [summary.party_a_analysis.party, summary.party_b_analysis.party],
            'Comparative Advantage': [
                summary.party_a_analysis.comparative_advantage.type,
                summary.party_b_analysis.comparative_advantage.type
            ],
            'Net Benefit': [
                summary.party_a_analysis.net_benefit,
                summary.party_b_analysis.net_benefit
            ],
            'Market Improvement': [
                summary.party_a_analysis.market_improvement,
                summary.party_b_analysis.market_improvement
            ]
        })
