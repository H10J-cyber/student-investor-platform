import yfinance as yf
import pandas as pd
import plotly.express as px


def get_stock_info(ticker):
    t = yf.Ticker(ticker)
    hist = t.history(period='5d')
    price = None
    try:
        price = hist['Close'].iloc[-1]
    except Exception:
        price = None
    info = {"ticker": ticker, "last_price": price}
    return info


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
