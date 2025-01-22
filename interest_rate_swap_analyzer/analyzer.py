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
    market_paying_vs_swap_receiving_benefit: float  # renamed from net_benefit
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
            benefit = self.get_market_paying_vs_swap_receiving_benefit(party)  # renamed from net_benefit
            
            return SwapAnalysisResult(
                party=party,
                comparative_advantage=self.comparative_advantages[party],
                market_paying_vs_swap_receiving_benefit=benefit,  # renamed
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
                party.get_rate(self.comparative_disadvantages[party].type).rate
                - (
                    self.interest_rate_swap.get_rate(
                        self.interest_rate_swap.get_paying_position_for_party(party)
                    ).rate
                    + self.get_market_paying_vs_swap_receiving_benefit(party)  # renamed
                )
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
                ).rate + self.get_market_paying_vs_swap_receiving_benefit(party)  # renamed
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

    def get_market_paying_vs_swap_receiving_benefit(self, party: Party) -> float:  # renamed from get_net_benefit
        """Calculate the benefit between market paying rate and swap receiving rate."""
        return -(
            party.get_rate(self.comparative_advantages[party].type).rate
            - self.interest_rate_swap.get_rate(
                self.interest_rate_swap.get_receiving_position_for_party(party)
            ).rate
        )

    def calculate_total_arbitrage_available(self) -> float:
        return self.comparative_advantages[self.party_a].rate + self.comparative_advantages[self.party_b].rate

    def to_dataframe(self, summary: SwapSummary) -> pd.DataFrame:
        """Convert analysis results to a pandas DataFrame."""
        return pd.DataFrame({
            'Party': [summary.party_a_analysis.party, summary.party_b_analysis.party],
            'Comparative Advantage': [
                summary.party_a_analysis.comparative_advantage.type,
                summary.party_b_analysis.comparative_advantage.type
            ],
            'Net Benefit': [
                summary.party_a_analysis.market_paying_vs_swap_receiving_benefit,  # renamed
                summary.party_b_analysis.market_paying_vs_swap_receiving_benefit  # renamed
            ],
            'Market Improvement': [
                summary.party_a_analysis.market_improvement,
                summary.party_b_analysis.market_improvement
            ]
        })

    def to_details_dataframe(self, summary: SwapSummary) -> pd.DataFrame:
        """Gather the original inputs and swap details in a user-friendly table."""
        return pd.DataFrame([{
            "Party A fixed (market)": f"{self.party_a.fixed_rate.rate:.2%}",
            "Party A floating (market)": f"{self.party_a.floating_rate_delta.rate:.2%}",
            "Party B fixed (market)": f"{self.party_b.fixed_rate.rate:.2%}",
            "Party B floating (market)": f"{self.party_b.floating_rate_delta.rate:.2%}",
            "Swap Notional": self.interest_rate_swap.notional,
            "Swap Start": self.interest_rate_swap.start_date,
            "Swap End": self.interest_rate_swap.end_date,
            "Swap Fixed Rate": f"{summary.fixed_rate:.2%}",
            "Swap Floating Rate": f"{summary.floating_rate:.2%}",
            "Total Arbitrage": f"{summary.total_arbitrage:.2%}"
        }])

    def to_market_rates_dataframe(self) -> pd.DataFrame:
        """Return market rates for Party A and Party B in a table, floating rates as 'S+...'."""
        return pd.DataFrame([
            {
                "Party": "Party A",
                "Fixed Rate (Market)": str(self.party_a.fixed_rate),
                "Floating Rate (Market)": str(self.party_a.floating_rate_delta),
            },
            {
                "Party": "Party B",
                "Fixed Rate (Market)": str(self.party_b.fixed_rate),
                "Floating Rate (Market)": str(self.party_b.floating_rate_delta),
            }
        ])

    def to_swap_details_dataframe(self, summary: SwapSummary) -> pd.DataFrame:
        """Return basic swap details in a table, using formatted rates from the swap object."""
        return pd.DataFrame([{
            "Swap Fixed Rate": str(self.interest_rate_swap.fixed_rate),
            "Swap Floating Rate": str(self.interest_rate_swap.floating_rate_delta),
            "Total Arbitrage": f"{summary.total_arbitrage:.2%}",
        }])

    def to_party_positions_dataframe(self, summary: SwapSummary) -> pd.DataFrame:
        """Show each party's paying position, paying rate, receiving position, receiving rate,
        position from the market, net position, and benefit, with floating rates as 'S+...'."""
        data = []
        for party_analysis in [summary.party_a_analysis, summary.party_b_analysis]:
            paying_rate = self.interest_rate_swap.get_rate(party_analysis.paying_position)
            receiving_rate = self.interest_rate_swap.get_rate(party_analysis.receiving_position)
            market_position_type = self.comparative_advantages[party_analysis.party].type
            market_rate = party_analysis.party.get_rate(market_position_type)
            
            # Get the opposite market rate (what they would have paid)
            opposite_market_position = "floating" if market_position_type == "fixed" else "fixed"
            opposite_market_rate = party_analysis.party.get_rate(opposite_market_position)
            
            net_position = paying_rate - self.get_market_paying_vs_swap_receiving_benefit(party_analysis.party)
            net_market_benefit = opposite_market_rate.rate - net_position.rate
            
            data.append({
                "Party": party_analysis.party,
                # "Swap Paying Position": party_analysis.paying_position,
                "Swap Paying Rate": str(paying_rate),
                # "Swap Receiving Position": party_analysis.receiving_position,
                "Swap Receiving Rate": str(receiving_rate), 
                "Market Position": str(market_rate),
                "Benefit": f"{self.get_market_paying_vs_swap_receiving_benefit(party_analysis.party):.2%}",
                "Net Position": str(net_position),
                "Net Market Benefit": f"{net_market_benefit:.2%}"
            })
        return pd.DataFrame(data)

