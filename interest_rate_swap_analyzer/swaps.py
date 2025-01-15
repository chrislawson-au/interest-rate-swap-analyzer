from datetime import date
from dataclasses import dataclass
from typing import Literal, Union, Optional
import pandas as pd

@dataclass
class InterestRate:
    """Represents an interest rate, either fixed or floating, with operator overloads."""
    rate: float
    rate_type: Literal["fixed", "floating"]

    def __post_init__(self):
        if not isinstance(self.rate, (int, float)):
            raise ValueError("Rate must be a number")
        if self.rate_type not in ["fixed", "floating"]:
            raise ValueError("Rate type must be 'fixed' or 'floating'")

    @property
    def is_floating(self) -> bool:
        return self.rate_type == "floating"

    def __add__(self, other):
        if isinstance(other, (int, float)):
            return InterestRate(self.rate + other, self.rate_type)
        elif isinstance(other, InterestRate):
            if self.is_floating or other.is_floating:
                return InterestRate(self.rate + other.rate, "floating")
            else:
                return InterestRate(self.rate + other.rate, "fixed")
        else:
            raise TypeError("Unsupported operand type for +")

    def __sub__(self, other):
        if isinstance(other, (int, float)):
            return InterestRate(self.rate - other, self.rate_type)
        elif isinstance(other, InterestRate):
            if self.is_floating or other.is_floating:
                return InterestRate(self.rate - other.rate, "floating")
            else:
                return InterestRate(self.rate - other.rate, "fixed")
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
    def __init__(
        self, 
        name: str,
        fixed_rate: float,
        floating_rate_delta: float,
        preference: Literal["fixed", "floating"]
    ):
        self.name = name
        self._fixed_rate = InterestRate(fixed_rate, "fixed")
        self._floating_rate_delta = InterestRate(floating_rate_delta, "floating")
        if preference not in ["fixed", "floating"]:
            raise ValueError("Preference must be 'fixed' or 'floating'")
        self.preference = preference

    @property
    def fixed_rate(self) -> InterestRate:
        return self._fixed_rate

    @property
    def floating_rate_delta(self) -> InterestRate:
        return self._floating_rate_delta

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
        if notional <= 0:
            raise ValueError("Notional must be positive")
        if start_date >= end_date:
            raise ValueError("Start date must be before end date")

        self._fixed_rate = InterestRate(fixed_rate, "fixed")
        self._floating_rate_delta = InterestRate(floating_rate_delta, "floating")
        self.notional = notional
        self.fixed_rate_payer = fixed_rate_payer
        self.floating_rate_payer = floating_rate_payer
        self.start_date = start_date
        self.end_date = end_date

    @property
    def fixed_rate(self) -> InterestRate:
        return self._fixed_rate

    @property
    def floating_rate_delta(self) -> InterestRate:
        return self._floating_rate_delta

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

