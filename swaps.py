from datetime import date
import pandas as pd

class InterestRate:
    """Represents an interest rate, either fixed or floating, with operator overloads."""
    def __init__(self, rate: float, rate_type: str):
        self.rate = rate
        self.rate_type = rate_type

    def __add__(self, other):
        if isinstance(other, (int, float)):
            return InterestRate(self.rate + other, self.rate_type)
        elif isinstance(other, InterestRate):
            if self.rate_type == "floating" or other.rate_type == "floating":
                return InterestRate(self.rate + other.rate, "floating")
            else:
                return InterestRate(self.rate + other.rate, "fixed")
        else:
            raise TypeError("Unsupported operand type for +")

    def __sub__(self, other):
        if isinstance(other, (int, float)):
            return InterestRate(self.rate - other, self.rate_type)
        elif isinstance(other, InterestRate):
            if self.rate_type != other.rate_type:
                return InterestRate(self.rate - other.rate, "floating") 
            return InterestRate(self.rate - other.rate, "fixed") # Always return a fixed rate. fixed - fixed = fixed, floating - floating = fixed (i.e., the difference in the floating rates)
        else:
            raise TypeError("Unsupported operand type for -")

    def __lt__(self, other):
        if isinstance(other, (int, float)):
            return self.rate < other
        elif isinstance(other, InterestRate):
            if self.rate_type != other.rate_type:
                raise ValueError("Cannot compare rates of different types")
            return self.rate < other.rate
        else:
            raise TypeError("Unsupported operand type for <")

    def __le__(self, other):
        if isinstance(other, (int, float)):
            return self.rate <= other
        elif isinstance(other, InterestRate):
            if self.rate_type != other.rate_type:
                raise ValueError("Cannot compare rates of different types")
            return self.rate <= other.rate
        else:
            raise TypeError("Unsupported operand type for <=")

    def __eq__(self, other):
        if isinstance(other, (int, float)):
            return self.rate == other
        elif isinstance(other, InterestRate):
            if self.rate_type != other.rate_type:
                raise ValueError("Cannot compare rates of different types")
            return self.rate == other.rate
        else:
            raise TypeError("Unsupported operand type for ==")

    def __ne__(self, other):
        if isinstance(other, (int, float)):
            return self.rate != other
        elif isinstance(other, InterestRate):
            if self.rate_type != other.rate_type:
                raise ValueError("Cannot compare rates of different types")
            return self.rate != other.rate
        else:
            raise TypeError("Unsupported operand type for !=")

    def __gt__(self, other):
        if isinstance(other, (int, float)):
            return self.rate > other
        elif isinstance(other, InterestRate):
            if self.rate_type != other.rate_type:
                raise ValueError("Cannot compare rates of different types")
            return self.rate > other.rate
        else:
            raise TypeError("Unsupported operand type for >")

    def __ge__(self, other):
        if isinstance(other, (int, float)):
            return self.rate >= other
        elif isinstance(other, InterestRate):
            if self.rate_type != other.rate_type:
                raise ValueError("Cannot compare rates of different types")
            return self.rate >= other.rate
        else:
            raise TypeError("Unsupported operand type for >=")

    def __str__(self):
        if self.rate_type == "fixed":
            return f"{self.rate:.2%}"
        elif self.rate_type == "floating":
            return f"S{'+' if self.rate >= 0 else '-'}{abs(int(self.rate*10_000))}"
        else:
            raise ValueError("Invalid rate type")

class Party:
    """Represents a party with preferences for fixed or floating rates."""
    def __init__(self, name, fixed_rate, floating_rate_delta, preference):
        self.name = name
        self.fixed_rate = InterestRate(fixed_rate, "fixed")
        self.floating_rate_delta = InterestRate(floating_rate_delta, "floating")  # Delta over a benchmark rate
        self.preference = preference  # "fixed" or "floating"

    def get_floating_rate(self, benchmark_rate):
        return benchmark_rate + self.floating_rate_delta.rate
    
    def get_rate(self, type):
        if type == "fixed":
            return self.fixed_rate
        else:
            return self.floating_rate_delta

    def __str__(self):
        return self.name


class InterestRateSwap:
    """Holds the parameters of a swap, including rates, notional, parties, and dates."""
    def __init__(
        self,
        fixed_rate: float,
        floating_rate_delta: float,
        notional: float,
        fixed_rate_payer: Party,
        floating_rate_payer: Party,
        start_date: date,
        end_date: date
    ):
        self.fixed_rate = InterestRate(fixed_rate, "fixed")
        self.floating_rate_delta = InterestRate(floating_rate_delta, "floating")
        self.notional = notional
        self.fixed_rate_payer = fixed_rate_payer
        self.floating_rate_payer = floating_rate_payer
        self.start_date = start_date
        self.end_date = end_date

    # Semi-annual payments
    def calculate_fixed_leg_payment(self):
        return self.notional * self.fixed_rate.rate / 2
    
    # Semi-annual payments
    def calculate_floating_leg_payment(self, benchmark_rate):
        floating_rate = benchmark_rate + self.floating_rate_delta.rate
        return self.notional * floating_rate / 2


    def calculate_interest_payments(self, benchmark_rate):
        fixed_leg_payment = self.calculate_fixed_leg_payment()
        floating_leg_payment = self.calculate_floating_leg_payment(benchmark_rate)
        fixed_leg_net_payment = floating_leg_payment - fixed_leg_payment
        floating_leg_net_payment = fixed_leg_payment - floating_leg_payment

        return (fixed_leg_payment, floating_leg_payment, fixed_leg_net_payment, floating_leg_net_payment)
    
    def get_paying_position_for_party(self, party):
        if party == self.fixed_rate_payer:
            return "fixed"
        else:
            return "floating"

    def get_receiving_position_for_party(self, party):
        if party == self.fixed_rate_payer:
            return "floating"
        elif party == self.floating_rate_payer:
            return "fixed"
        else:
            return None

    
    def get_rate(self, type):
        if type == "fixed":
            return self.fixed_rate
        else:
            return self.floating_rate_delta
        

class InterestRateSwapAnalyzer:
    """Analyzes and prints details regarding parties' advantages in an interest rate swap."""
    def __init__(self, party_a: Party, party_b: Party, interest_rate_swap: InterestRateSwap):
        self.party_a = party_a
        self.party_b = party_b
        self.interest_rate_swap = interest_rate_swap

        self.comparatives = {party: self.comparatives_for_party(party) for party in [self.party_a, self.party_b]}
        self.comparative_advantages = {party: self.determine_comparative_advantage_for_party(party) for party in [self.party_a, self.party_b]}
        self.comparative_disadvantages = {party: self.determine_comparative_disadvantage_for_party(party) for party in [self.party_a, self.party_b]}

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
             "Fixed Comparative": [self.comparatives[self.party_a]['fixed'], self.comparatives[self.party_b]['fixed']], 
             "Floating Comparative": [self.comparatives[self.party_a]['floating'], self.comparatives[self.party_b]['floating']]}
        ))

        print("Comparative Advantages: (Smaller is better)")
        for party in [self.party_a, self.party_b]:
            print(f"  {party.name} has a comparative advantage in the {self.comparative_advantages[party]['type']} market")


    def determine_comparative_advantage_for_party(self, party):
        if self.comparatives[party]["fixed"] < self.comparatives[party]["floating"]:
            return {"type": "fixed", "rate": self.comparatives[party]["fixed"]}
        elif self.comparatives[party]["floating"] < self.comparatives[party]["fixed"]:
            return {"type": "floating", "rate": self.comparatives[party]["floating"]}
        else:
            return {"type": "none", "rate": 0}
            
    def determine_comparative_disadvantage_for_party(self, party):
        if self.comparatives[party]["fixed"] > self.comparatives[party]["floating"]:
            return {"type": "fixed", "rate": self.comparatives[party]["fixed"]}
        elif self.comparatives[party]["floating"] > self.comparatives[party]["fixed"]:
            return {"type": "floating", "rate": self.comparatives[party]["floating"]}
        else:
            return {"type": "none", "rate": 0}

    def comparatives_for_party(self, party):
        counterparty = self.party_b if party == self.party_a else self.party_a
        fixed_rate_difference = party.fixed_rate - counterparty.fixed_rate
        floating_rate_difference = party.floating_rate_delta - counterparty.floating_rate_delta

        return {"fixed": fixed_rate_difference.rate, "floating": floating_rate_difference.rate}

    def get_net_benefit(self, party):
        return party.get_rate(self.comparative_advantages[party]['type']) - self.interest_rate_swap.get_rate(self.interest_rate_swap.get_receiving_position_for_party(party))
        
    def calculate_total_arbitrage_available(self):
        return self.comparative_advantages[self.party_a]['rate'] + self.comparative_advantages[self.party_b]['rate']
    
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
            print(f"* borrow from {self.comparative_advantages[party]['type']} rate market at {party.get_rate(self.comparative_advantages[party]['type'])}")
            print(f"* receives {self.interest_rate_swap.get_receiving_position_for_party(party)} rate of {self.interest_rate_swap.get_rate(self.interest_rate_swap.get_receiving_position_for_party(party))} from swap")
            print(f"* this is a net benefit of {self.get_net_benefit(party)}")
            print(f"* has {self.interest_rate_swap.get_paying_position_for_party(party)} rate position in swap paying { self.interest_rate_swap.get_rate(self.interest_rate_swap.get_paying_position_for_party(party))}")
            print(f"* net position is {self.interest_rate_swap.get_rate(self.interest_rate_swap.get_paying_position_for_party(party))} + {self.get_net_benefit(party)} = {self.interest_rate_swap.get_rate(self.interest_rate_swap.get_paying_position_for_party(party)) + self.get_net_benefit(party)}")
            print(f"* ({party.get_rate(self.comparative_disadvantages[party]['type']) - (self.interest_rate_swap.get_rate(self.interest_rate_swap.get_paying_position_for_party(party)) + self.get_net_benefit(party))} better than the {party.get_rate(self.comparative_disadvantages[party]['type'])} avialable on the open market) ")

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

