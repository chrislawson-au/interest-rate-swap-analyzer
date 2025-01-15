import pytest
from datetime import date
from interest_rate_swap_analyzer.swaps import Party, InterestRateSwap, InterestRate

def test_interest_rate_creation():
    rate = InterestRate(0.05, "fixed")
    assert rate.rate == 0.05
    assert rate.rate_type == "fixed"

def test_party_creation():
    party = Party("Test Corp", 0.05, 0.02, "fixed")
    assert party.name == "Test Corp"
    assert party.fixed_rate.rate == 0.05
    assert party.floating_rate_delta.rate == 0.02

def test_swap_creation():
    party_a = Party("A", 0.05, 0.02, "fixed")
    party_b = Party("B", 0.06, 0.01, "floating")
    
    swap = InterestRateSwap(
        0.055,
        0.015,
        1000000,
        party_a,
        party_b,
        date(2023, 1, 1),
        date(2024, 1, 1)
    )
    
    assert swap.notional == 1000000
    assert swap.fixed_rate.rate == 0.055
    assert swap.floating_rate_delta.rate == 0.015

def test_interest_rate_comparison():
    rate1 = InterestRate(0.05, "fixed")
    rate2 = InterestRate(0.06, "fixed")
    
    assert rate1 < rate2
    assert rate2 > rate1
    assert rate1 != rate2

def test_swap_calculations():
    party_a = Party("A", 0.05, 0.02, "fixed")
    party_b = Party("B", 0.06, 0.01, "floating")
    
    swap = InterestRateSwap(
        0.055,
        0.015,
        1000000,
        party_a,
        party_b,
        date(2023, 1, 1),
        date(2024, 1, 1)
    )
    
    fixed_payment = swap.calculate_fixed_leg_payment()
    assert fixed_payment == 27500  # 1000000 * 0.055 / 2
