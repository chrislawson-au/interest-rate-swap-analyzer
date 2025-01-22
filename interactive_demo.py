import streamlit as st
from datetime import date
from interest_rate_swap_analyzer.swaps import Party, InterestRateSwap
from interest_rate_swap_analyzer.analyzer import InterestRateSwapAnalyzer

st.title("Interest Rate Swap Analysis")

st.sidebar.header("Party A (Available from market)")
a_fixed = st.sidebar.number_input("Fixed Rate (%)", value=10.5)
a_float_delta = st.sidebar.number_input("Floating Rate Delta (%)", value=0.75)

st.sidebar.header("Party B (Available from market)")
b_fixed = st.sidebar.number_input("Fixed Rate (%) ", value=9.5)
b_float_delta = st.sidebar.number_input("Floating Rate Delta (%)", value=0.25)

st.sidebar.header("Swap Settings")
notional = st.sidebar.number_input("Notional", value=1_000_000.0)
fixed_payer = st.sidebar.selectbox("Fixed Rate Payer", ["Party A", "Party B"])
start = st.sidebar.date_input("Start Date", value=date.today())
end = st.sidebar.date_input("End Date", value=date(2030, 1, 1))
swap_fixed_rate = st.sidebar.number_input("Swap Fixed Rate (%)", value=9.5)
swap_floating_rate = st.sidebar.number_input("Swap Floating Rate Delta (%)", value=0.0)

# Build party objects
party_a = Party("Party A", a_fixed / 100, a_float_delta / 100, preference="fixed")
party_b = Party("Party B", b_fixed / 100, b_float_delta / 100, preference="floating")

# Determine which party is the fixed rate payer
if fixed_payer == "Party A":
    swap = InterestRateSwap(swap_fixed_rate / 100, swap_floating_rate / 100, notional, party_a, party_b, start, end)
else:
    swap = InterestRateSwap(swap_fixed_rate / 100, swap_floating_rate / 100, notional, party_b, party_a, start, end)

analyzer = InterestRateSwapAnalyzer(party_a, party_b, swap)
summary = analyzer.analyze()

st.subheader("Market Rates")
st.table(analyzer.to_market_rates_dataframe().set_index('Party', drop=True))

st.subheader("Opportunity Analysis")
st.table(analyzer.to_opportunity_analysis_dataframe(summary).assign(dummy='').set_index('dummy', drop=True))

st.subheader("Swap Details")
st.table(analyzer.to_swap_details_dataframe(summary).assign(dummy='').set_index('dummy', drop=True))

st.subheader("Party Positions")
st.table(analyzer.to_party_positions_dataframe(summary).set_index('Party', drop=True))