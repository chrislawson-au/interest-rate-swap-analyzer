
import streamlit as st
from datetime import date
from interest_rate_swap_analyzer.swaps import Party, InterestRateSwap
from interest_rate_swap_analyzer.analyzer import InterestRateSwapAnalyzer

st.title("Interactive Interest Rate Swap Demo")

st.sidebar.header("Party A Settings")
a_fixed = st.sidebar.number_input("Party A Fixed Rate (%)", value=2.0)
a_float_delta = st.sidebar.number_input("Party A Floating Rate Delta (%)", value=0.5)

st.sidebar.header("Party B Settings")
b_fixed = st.sidebar.number_input("Party B Fixed Rate (%)", value=3.0)
b_float_delta = st.sidebar.number_input("Party B Floating Rate Delta (%)", value=1.0)

st.sidebar.header("Swap Settings")
notional = st.sidebar.number_input("Notional", value=1_000_000.0)
fixed_payer = st.sidebar.selectbox("Fixed Rate Payer", ["Party A", "Party B"])
start = st.sidebar.date_input("Start Date", value=date.today())
end = st.sidebar.date_input("End Date", value=date(2030, 1, 1))

if st.button("Analyze Swap"):
    # Build party objects
    party_a = Party("Party A", a_fixed / 100, a_float_delta / 100, preference="fixed")
    party_b = Party("Party B", b_fixed / 100, b_float_delta / 100, preference="floating")

    # Determine which party is the fixed rate payer
    if fixed_payer == "Party A":
        swap = InterestRateSwap(a_fixed / 100, a_float_delta / 100, notional, party_a, party_b, start, end)
    else:
        swap = InterestRateSwap(b_fixed / 100, b_float_delta / 100, notional, party_b, party_a, start, end)

    analyzer = InterestRateSwapAnalyzer(party_a, party_b, swap)
    summary = analyzer.analyze()

    st.subheader("Analysis Results")
    st.write(analyzer.format_analysis_report(summary))