import streamlit as st
import plotly.express as px
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

st.set_page_config(page_title="Student Investor", layout="wide")

st.title("Student Investor & Economics Analytics Platform")

section = st.sidebar.selectbox("Section", ["Finance", "Economics", "Economic Heatmap & Country Analysis"])

if section == "Finance":
    st.header("Finance Explorer")
    ticker = st.text_input("Enter ticker (e.g., AAPL)")
    col1, col2 = st.columns([2,1])
    if ticker:
        info = get_stock_info(ticker)
        col1.subheader(f"{ticker} — Price & Chart")
        col1.write(info)
        fig = plot_stock_history(ticker)
        col1.plotly_chart(fig, use_container_width=True)

    st.subheader("Compare tickers")
    tickers = st.text_input("Comma-separated tickers (e.g., AAPL,TSLA)")
    if tickers:
        fig = compare_stocks([t.strip().upper() for t in tickers.split(",")])
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Portfolio Simulator")
    if st.button("Simulate sample portfolio"):
        df = simulate_portfolio({"AAPL":100, "TSLA":50}, start_date='2022-01-01')
        st.line_chart(df['portfolio_value'])

elif section == "Economics":
    st.header("Economics Explorer")
    country = st.selectbox("Country", ["United States", "India", "China", "United Kingdom"])
    indicator = st.selectbox("Indicator", ["Inflation (CPI)", "GDP (current US$)", "Unemployment rate"])
    if st.button("Load indicator"):
        series = get_indicator_series(country, indicator)
        fig = plot_indicator(series, title=f"{indicator} — {country}")
        st.plotly_chart(fig, use_container_width=True)

else:
    st.header("Economic Heatmap & Country Analysis")
    heatmap_indicator = st.selectbox("Indicator for heatmap", list(HEATMAP_INDICATORS.values()))
    heatmap_df = build_heatmap_data(heatmap_indicator)
    if heatmap_df.empty:
        st.warning("Unable to load heatmap data. Please try again later.")
    else:
        fig = px.choropleth(
            heatmap_df,
            locations='iso3',
            color='value',
            hover_name='country',
            color_continuous_scale='Viridis',
            labels={'value': heatmap_indicator},
            title=f"World {heatmap_indicator} Heatmap"
        )
        st.write("Use the chart hover tooltips to inspect country values, then choose a country below for details.")
        st.plotly_chart(fig, use_container_width=True)
        country_list = get_available_countries()
        country_name = st.selectbox("Select a country", country_list, index=0)

        country_summary = get_country_summary(country_name)
        left, right = st.columns([2, 1])
        with left:
            st.subheader(f"{country_summary.get('Country')} — Key Economic Metrics")
            metrics = {
                "GDP (USD)": country_summary.get("GDP"),
                "GDP Growth (%)": country_summary.get("GDP Growth"),
                "Inflation (%)": country_summary.get("Inflation"),
                "Unemployment (%)": country_summary.get("Unemployment"),
                "Interest Rate (%)": country_summary.get("Interest Rate"),
                "Exchange Rate (USD)": country_summary.get("Exchange Rate (USD)"),
                "Trade Balance (USD)": country_summary.get("Trade Balance"),
                "Population": country_summary.get("Population"),
                "Currency": country_summary.get("Currency"),
            }
            for label, value in metrics.items():
                st.metric(label=label, value=f"{value:,.2f}" if isinstance(value, (int, float)) else value)

            st.markdown("### Economic Summary")
            st.write(country_summary.get("Economic Summary"))

        with right:
            st.subheader("Country Comparison")
            country_compare = st.multiselect(
                "Compare countries", get_available_countries(), default=[country_name] if country_name else []
            )
            if country_compare:
                compare_df = get_comparison_data(country_compare)
                st.dataframe(compare_df.set_index("Country"))
                if len(country_compare) >= 2:
                    compare_chart = px.bar(
                        compare_df.melt(id_vars=["Country"], value_vars=["GDP Growth", "Inflation", "Unemployment"]),
                        x="Country",
                        y="value",
                        color="variable",
                        barmode="group",
                        title="Economic Comparison"
                    )
                    st.plotly_chart(compare_chart, use_container_width=True)

        st.subheader("Recent Country Trends")
        trend_col1, trend_col2 = st.columns(2)
        with trend_col1:
            inflation_series = get_indicator_series(country_name, "Inflation")
            st.plotly_chart(plot_indicator(inflation_series, title=f"{country_name} Inflation Trend"), use_container_width=True)
        with trend_col2:
            gdp_series = get_indicator_series(country_name, "GDP Growth")
            st.plotly_chart(plot_indicator(gdp_series, title=f"{country_name} GDP Growth Trend"), use_container_width=True)
        trend_col3, trend_col4 = st.columns(2)
        with trend_col3:
            unemployment_series = get_indicator_series(country_name, "Unemployment")
            st.plotly_chart(plot_indicator(unemployment_series, title=f"{country_name} Unemployment Trend"), use_container_width=True)
        with trend_col4:
            interest_series = get_indicator_series(country_name, "Interest Rate")
            st.plotly_chart(plot_indicator(interest_series, title=f"{country_name} Interest Rate Trend"), use_container_width=True)
