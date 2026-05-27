import yfinance as yf
import pandas as pd
import plotly.express as px


def get_stock_info(ticker):
    t = yf.Ticker(ticker)
    hist = t.history(period='5d')
    price = None
    change = None
    if not hist.empty:
        price = hist['Close'].iloc[-1]
        if len(hist) >= 2:
            change = price - hist['Close'].iloc[-2]
    info = {
        "ticker": ticker,
        "last_price": price,
        "daily_change": change,
        "history_rows": len(hist),
    }
    return info


def get_stock_summary(ticker):
    t = yf.Ticker(ticker)
    info = t.info or {}
    summary = {
        "ticker": ticker,
        "name": info.get("shortName") or info.get("longName"),
        "sector": info.get("sector"),
        "industry": info.get("industry"),
        "market_cap": info.get("marketCap"),
        "pe_ratio": info.get("trailingPE"),
        "forward_pe": info.get("forwardPE"),
        "dividend_yield": info.get("dividendYield"),
        "beta": info.get("beta"),
        "current_price": info.get("regularMarketPrice"),
    }
    return summary


def plot_stock_history(ticker, period='1y'):
    t = yf.Ticker(ticker)
    hist = t.history(period=period)
    if hist.empty:
        return px.line()
    fig = px.line(hist, x=hist.index, y='Close', title=f'{ticker} Close Price')
    return fig


def compare_stocks(tickers, period='1y'):
    frames = []
    for tk in tickers:
        t = yf.Ticker(tk)
        h = t.history(period=period)[['Close']].rename(columns={'Close': tk})
        frames.append(h)
    if not frames:
        return px.line()
    df = pd.concat(frames, axis=1).ffill()
    df = df.pct_change().add(1).cumprod()
    fig = px.line(df, x=df.index, y=df.columns, title='Normalized Returns')
    return fig


def simulate_portfolio(holdings, start_date='2020-01-01'):
    # holdings: dict ticker -> shares
    frames = []
    for tk, shares in holdings.items():
        t = yf.Ticker(tk)
        h = t.history(start=start_date)[['Close']].rename(columns={'Close': tk})
        frames.append(h * shares)
    df = pd.concat(frames, axis=1).ffill()
    df['portfolio_value'] = df.sum(axis=1)
    return df
