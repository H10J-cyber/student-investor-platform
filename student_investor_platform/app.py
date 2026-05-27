import os
from datetime import datetime

import pandas as pd
import plotly.express as px
import streamlit as st

from finance import get_stock_info, plot_stock_history, compare_stocks, simulate_portfolio
from economics import (
    get_indicator_series,
    plot_indicator,
    build_heatmap_data,
    get_country_summary,
    get_available_countries,
    get_comparison_data,
    HEATMAP_INDICATORS,
)
from screener import DEFAULT_TICKERS, load_screener_data
from calculators import compound_interest, dcf, ddm, emi, sip_value
from cfa import CFA_CONCEPTS, search_concepts

try:
    from streamlit_option_menu import option_menu
except ImportError:
    option_menu = None

st.set_page_config(page_title="Finance Simulator", layout="wide", page_icon="💼")

PAGE_STYLE = """
<style>
html, body, [data-testid="stAppViewContainer"], [data-testid="stSidebar"], .css-18e3th9, .css-1outpf7, .css-1d391kg, .css-10trblm, .css-8kagpq {
  background: radial-gradient(circle at top left, #0bbd88 0%, #0b4f6c 38%, #041b2b 100%) !important;
  color: #ffffff !important;
}
[aria-label="Main content"] {
  background: transparent !important;
}
.sidebar .sidebar-content, .css-1d391kg {
  background: linear-gradient(180deg, #062b35 0%, #083d59 45%, #031b2b 100%) !important;
  border-right: 1px solid rgba(56, 189, 248, 0.18) !important;
}
.stButton>button, .stTextInput>div, .stSelectbox>div, .stTextArea>div, .stRadio>div, .stSlider>div {
  border-radius: 16px !important;
  border: 1px solid rgba(56, 189, 248, 0.22) !important;
  background: rgba(3, 22, 41, 0.92) !important;
  color: #ffffff !important;
}
div.block-container, .reportview-container .main {
  padding-top: 1.6rem !important;
  padding-left: 2rem !important;
  padding-right: 2rem !important;
  background: transparent !important;
}
.css-1lsmgbg.egzxvld2, .css-1v0mbdj, .css-1bivwz3 {
  background-color: transparent !important;
}
* {
  color: #ffffff !important;
}
.stAlert {
  border-radius: 16px !important;
  background: rgba(14, 79, 109, 0.92) !important;
  border: 1px solid rgba(37, 99, 235, 0.24) !important;
}
.card {
  background: rgba(6, 28, 44, 0.92);
  border: 1px solid rgba(34, 197, 94, 0.24);
  border-radius: 24px;
  padding: 1.6rem;
  box-shadow: 0 28px 70px rgba(3, 18, 35, 0.35);
}
.stDataFrame table {
  border-radius: 16px;
  overflow: hidden;
}
.stDataFrame th {
  background: rgba(10, 49, 68, 0.95) !important;
  color: #ffffff !important;
}
.stDataFrame td {
  background: rgba(6, 24, 40, 0.92) !important;
  color: #ffffff !important;
}
.css-1avcm0n.e1fqkh3o9 {
  background: rgba(14, 79, 109, 0.85) !important;
}
</style>
"""

st.markdown(PAGE_STYLE, unsafe_allow_html=True)

MAIN_MENU = [
    "Market Intelligence",
    "Economics Lab",
    "Stock Screener",
    "Valuation Tools",
    "CFA Learning",
    "Market Heatmaps",
]

MENU_ICONS = [
    "bar-chart-line",
    "globe2",
    "search",
    "calculator",
    "book",
    "graph-up",
]

if option_menu:
    selected = option_menu(
        "Finance Simulator",
        MAIN_MENU,
        icons=MENU_ICONS,
        menu_icon="speedometer",
        default_index=0,
        orientation="vertical",
        styles={
            "container": {"padding": "0!important", "background-color": "#0a2f3c"},
            "icon": {"color": "#5eead4", "font-size": "18px"},
            "nav-link": {
                "font-size": "14px",
                "text-align": "left",
                "margin": "0px",
                "color": "#d8f8ff",
                "padding": "12px 16px",
                "border-radius": "12px",
            },
            "nav-link-selected": {"background-color": "rgba(56, 189, 248, 0.18)", "color": "#a5f3fc"},
            "nav-link-hover": {"background-color": "rgba(14, 116, 144, 0.16)", "color": "#e0f2fe"},
        },
    )
else:
    selected = st.sidebar.radio("Navigation", MAIN_MENU)

st.sidebar.markdown("---")
st.sidebar.markdown("**Workspace**: professional fintech analytics with portfolio, valuations, macro models, and AI.")

def format_metric(value, precision=2):
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return "N/A"
    if isinstance(value, (int, float)):
        return f"{value:,.{precision}f}"
    return str(value)

@st.cache_data(show_spinner=False)
def cached_screener_data():
    return load_screener_data()

@st.cache_data(show_spinner=False)
def cached_heatmap_data(indicator):
    return build_heatmap_data(indicator)

@st.cache_data(show_spinner=False)
def cached_indicator_series(country, indicator):
    return get_indicator_series(country, indicator)


def show_market_intelligence():
    st.header("Market Intelligence")
    st.write("A professional market dashboard for stock analysis, comparative performance, and portfolio simulation.")

    ticker = st.text_input("Ticker", value="AAPL", max_chars=10).upper()
    if ticker:
        info = get_stock_info(ticker)
        price = format_metric(info.get("last_price"))

        col1, col2, col3 = st.columns(3)
        col1.metric("Ticker", ticker)
        col2.metric("Latest Price", price)
        col3.metric("As of", datetime.now().strftime("%Y-%m-%d"))

        with st.expander("Key stock overview"):
            st.json(info)

        st.subheader("Price history")
        fig = plot_stock_history(ticker)
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Compare multiple symbols")
    tickers = st.text_input("Compare tickers (comma-separated)", value="AAPL,MSFT,GOOGL")
    if tickers:
        symbol_list = [x.strip().upper() for x in tickers.split(",") if x.strip()]
        if len(symbol_list) > 1:
            st.plotly_chart(compare_stocks(symbol_list), use_container_width=True)
        else:
            st.info("Enter at least two tickers to compare.")

    st.subheader("Portfolio simulator")
    with st.expander("Build a simple position simulation"):
        default_holdings = {"AAPL": 50, "MSFT": 30, "GOOGL": 20}
        holdings_input = st.text_area(
            "Holdings (ticker:shares)", value="AAPL:50\nMSFT:30\nGOOGL:20",
            help="Enter one ticker per line as TICKER:SHARES"
        )
        start_date = st.date_input("Start date", value=datetime(2023, 1, 1))
        if st.button("Simulate portfolio"):
            try:
                positions = {
                    line.split(":")[0].strip().upper(): float(line.split(":")[1].strip())
                    for line in holdings_input.splitlines()
                    if ":" in line
                }
                if positions:
                    portfolio_df = simulate_portfolio(positions, start_date=start_date.strftime("%Y-%m-%d"))
                    st.line_chart(portfolio_df['portfolio_value'])
                    st.write(portfolio_df.tail(5))
                else:
                    st.warning("Provide ticker and share quantity with the format TICKER:SHARES.")
            except Exception as exc:
                st.error(f"Portfolio simulation failed: {exc}")


def show_economics_lab():
    st.header("Economics Lab")
    st.write("Live macro and country research tools for GDP, inflation, unemployment, and central bank trends.")

    country = st.selectbox("Country", get_available_countries(), index=0)
    indicator = st.selectbox("Indicator", list(HEATMAP_INDICATORS.values()), index=1)
    series = cached_indicator_series(country, indicator)

    st.subheader(f"{indicator} — {country}")
    if series.empty:
        st.warning("No indicator series available for this country and indicator.")
    else:
        st.plotly_chart(plot_indicator(series, title=f"{indicator} — {country}"), use_container_width=True)

    with st.expander("Country summary metrics"):
        country_summary = get_country_summary(country)
        metric_columns = st.columns(3)
        for idx, (label, value) in enumerate({
            "GDP (USD)": country_summary.get("GDP"),
            "GDP Growth (%)": country_summary.get("GDP Growth"),
            "Inflation (%)": country_summary.get("Inflation"),
            "Unemployment (%)": country_summary.get("Unemployment"),
            "Interest Rate (%)": country_summary.get("Interest Rate"),
        }.items()):
            metric_columns[idx % 3].metric(label, format_metric(value))
        st.markdown(country_summary.get("Economic Summary", "No summary available."))


def show_stock_screener():
    st.header("Stock Screener")
    st.write("Filter and compare high-quality equities using real-time YFinance fundamentals and technical signals.")

    df = cached_screener_data()
    if df.empty:
        st.warning("Screener data is not available right now. Try again later.")
        return

    sector_filter = st.multiselect("Filter sectors", sorted(df['Sector'].dropna().unique()), default=df['Sector'].dropna().unique().tolist())
    price_range = st.slider("Price range", min_value=0.0, max_value=float(df['Price'].max() or 1000), value=(0.0, float(df['Price'].max() or 1000)))
    rsi_range = st.slider("RSI range", min_value=0, max_value=100, value=(0, 100))

    filtered = df[
        (df['Sector'].isin(sector_filter)) &
        (df['Price'].between(price_range[0], price_range[1])) &
        (df['RSI'].between(rsi_range[0], rsi_range[1]))
    ]

    st.metric("Universe size", len(filtered))
    sort_order = st.selectbox("Sort by", ["Price Change %", "RSI", "Market Cap", "PE Ratio"], index=0)
    st.dataframe(filtered.sort_values(by=sort_order, ascending=False).reset_index(drop=True).style.format({
        'Price': '${:,.2f}',
        'Market Cap': '${:,.0f}',
        'Price Change %': '{:,.2f}%',
        'Dividend Yield': '{:.2%}',
        'Revenue Growth': '{:.2%}',
        'RSI': '{:,.1f}',
    }))

    st.subheader("Top gainers & screen highlights")
    cols = st.columns(2)
    with cols[0]:
        st.markdown("**Top movers**")
        st.dataframe(filtered.nlargest(5, 'Price Change %')[['Ticker', 'Name', 'Price Change %', 'Price']])
    with cols[1]:
        st.markdown("**Oversold / bullish candidates**")
        st.dataframe(filtered.nsmallest(5, 'RSI')[['Ticker', 'Name', 'RSI', 'PE Ratio']])

    ticker = st.text_input("Show chart for ticker", value=DEFAULT_TICKERS[0]).upper()
    if ticker:
        st.plotly_chart(plot_stock_history(ticker), use_container_width=True)


def show_valuation_tools():
    st.header("Valuation & Wealth Tools")
    tool = st.radio("Select calculator", ["Compound Interest", "SIP Planner", "EMI Calculator", "Dividend Discount Model", "Discounted Cash Flow"])

    if tool == "Compound Interest":
        principal = st.number_input("Principal", value=10000.0, min_value=0.0)
        rate = st.number_input("Annual rate (%)", value=7.0)
        years = st.number_input("Years", value=10, min_value=1)
        if st.button("Calculate"):
            total, timeline = compound_interest(principal, rate, years)
            st.metric("Future value", f"${total:,.2f}")
            st.plotly_chart(px.line(timeline, x='Year', y='Value', title='Compound growth'), use_container_width=True)

    elif tool == "SIP Planner":
        monthly = st.number_input("Monthly investment", value=500.0, min_value=0.0)
        rate = st.number_input("Expected annual return (%)", value=12.0)
        years = st.number_input("Years", value=15, min_value=1)
        if st.button("Calculate SIP"):
            future, timeline = sip_value(monthly, rate, years)
            st.metric("Total value", f"${future:,.2f}")
            st.plotly_chart(px.line(timeline, x='Month', y='Value', title='SIP accumulation'), use_container_width=True)

    elif tool == "EMI Calculator":
        principal = st.number_input("Loan amount", value=500000.0, min_value=0.0)
        rate = st.number_input("Annual interest rate (%)", value=8.5)
        years = st.number_input("Loan term (years)", value=15, min_value=1)
        if st.button("Compute EMI"):
            payment = emi(principal, rate, years)
            st.metric("Monthly EMI", f"${payment:,.2f}")

    elif tool == "Dividend Discount Model":
        dividend = st.number_input("Annual dividend per share", value=2.0, min_value=0.0)
        required_return = st.number_input("Required return (%)", value=8.0)
        growth = st.number_input("Growth rate (%)", value=4.0)
        if st.button("Value stock"):
            value = ddm(dividend, required_return, growth)
            if value is None:
                st.error("Required return must be greater than growth rate.")
            else:
                st.metric("Intrinsic value", f"${value:,.2f}")

    else:
        st.write("Discounted Cash Flow")
        cash_flow_text = st.text_area("Projected cash flows (comma separated)", value="10000,12000,14000,16000,18000")
        rate = st.number_input("Discount rate (%)", value=10.0)
        terminal_growth = st.number_input("Terminal growth rate (%)", value=2.0)
        if st.button("Calculate DCF"):
            try:
                flows = [float(x.strip()) for x in cash_flow_text.split(",") if x.strip()]
                value = dcf(flows, rate, terminal_growth / 100)
                st.metric("Present value", f"${value:,.2f}")
            except Exception as exc:
                st.error(f"Unable to compute DCF: {exc}")


def show_cfa_learning():
    st.header("CFA Learning Hub")
    query = st.text_input("Search CFA concept", value="portfolio")
    results = search_concepts(query) if query else CFA_CONCEPTS

    for topic, data in (results or CFA_CONCEPTS).items():
        with st.expander(topic):
            st.write(data['summary'])
            st.markdown("**Core formulas**")
            for formula in data['formula']:
                st.write(f"- {formula}")
            st.markdown("**Example**")
            st.write(data['example'])


def show_market_heatmaps():
    st.header("Market Heatmaps")
    indicator = st.selectbox("Indicator", list(HEATMAP_INDICATORS.values()), index=0)
    heatmap_df = cached_heatmap_data(indicator)

    if heatmap_df.empty:
        st.warning("Heatmap data unavailable. Please refresh or try another indicator.")
        return

    fig = px.choropleth(
        heatmap_df,
        locations='iso3',
        color='value',
        hover_name='country',
        color_continuous_scale='Plasma',
        labels={'value': indicator},
        title=f"Global {indicator} Heatmap",
    )
    st.plotly_chart(fig, use_container_width=True)

    selected_country = st.selectbox("Inspect country", get_available_countries())
    if selected_country:
        summary = get_country_summary(selected_country)
        st.markdown(f"### {selected_country} snapshot")

        if summary:
            metric_columns = st.columns(3)
            country_metrics = [
                ("GDP (USD)", summary.get("GDP")),
                ("GDP Growth (%)", summary.get("GDP Growth")),
                ("Inflation (%)", summary.get("Inflation")),
                ("Unemployment (%)", summary.get("Unemployment")),
                ("Interest Rate (%)", summary.get("Interest Rate")),
                ("Exchange Rate (USD)", summary.get("Exchange Rate (USD)")),
            ]
            for idx, (label, value) in enumerate(country_metrics):
                metric_columns[idx % 3].metric(label, format_metric(value))

            fact_col1, fact_col2 = st.columns([2, 1])
            with fact_col1:
                st.markdown("**Country details**")
                st.write(f"**Region:** {summary.get('Region', 'N/A')}")
                st.write(f"**Subregion:** {summary.get('Subregion', 'N/A')}")
                st.write(f"**Currency:** {summary.get('Currency', 'N/A')}")
                st.write(f"**Population:** {format_metric(summary.get('Population'), precision=0)}")
            with fact_col2:
                st.markdown("**Economic summary**")
                st.write(summary.get("Economic Summary", "No summary available."))

        else:
            st.warning("No country data available for this selection.")

        series = cached_indicator_series(selected_country, indicator)
        if not series.empty:
            st.plotly_chart(plot_indicator(series, title=f"{indicator} trend for {selected_country}"), use_container_width=True)


def main():
    if selected == "Market Intelligence":
        show_market_intelligence()
    elif selected == "Economics Lab":
        show_economics_lab()
    elif selected == "Stock Screener":
        show_stock_screener()
    elif selected == "Valuation Tools":
        show_valuation_tools()
    elif selected == "CFA Learning":
        show_cfa_learning()
    elif selected == "Market Heatmaps":
        show_market_heatmaps()
    else:
        st.write("Select a section from the sidebar.")


if __name__ == '__main__':
    main()
