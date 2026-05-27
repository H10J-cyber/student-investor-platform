import numpy as np
import pandas as pd
import yfinance as yf

DEFAULT_TICKERS = [
    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'JPM', 'V', 'MA', 'PYPL',
    'META', 'NFLX', 'DIS', 'XOM', 'CVX', 'BA', 'WMT', 'KO', 'PEP', 'INTC'
]


def compute_rsi(close, period=14):
    delta = close.diff()
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)
    avg_gain = gain.rolling(period, min_periods=period).mean()
    avg_loss = loss.rolling(period, min_periods=period).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - 100 / (1 + rs)
    return rsi


def load_screener_data(tickers=None):
    if tickers is None:
        tickers = DEFAULT_TICKERS
    rows = []
    for ticker in tickers:
        try:
            t = yf.Ticker(ticker)
            info = t.info
            hist = t.history(period='3mo', interval='1d')
            if hist.empty:
                continue
            close = hist['Close']
            rsi = compute_rsi(close).iloc[-1] if len(close) >= 14 else None
            rows.append({
                'Ticker': ticker,
                'Name': info.get('shortName') or info.get('longName'),
                'Sector': info.get('sector'),
                'Market Cap': info.get('marketCap'),
                'PE Ratio': info.get('trailingPE'),
                'Dividend Yield': info.get('dividendYield'),
                'Revenue Growth': info.get('revenueGrowth'),
                'Beta': info.get('beta'),
                'Volume': info.get('averageVolume'),
                'Price': info.get('regularMarketPrice') or info.get('previousClose'),
                'Price Change %': info.get('regularMarketChangePercent'),
                'RSI': rsi,
            })
        except Exception:
            continue
    df = pd.DataFrame(rows)
    if df.empty:
        return df
    df['Price Change %'] = pd.to_numeric(df['Price Change %'], errors='coerce')
    df['Market Cap'] = pd.to_numeric(df['Market Cap'], errors='coerce')
    df['Revenue Growth'] = pd.to_numeric(df['Revenue Growth'], errors='coerce')
    df['Dividend Yield'] = pd.to_numeric(df['Dividend Yield'], errors='coerce')
    df['PE Ratio'] = pd.to_numeric(df['PE Ratio'], errors='coerce')
    df['Beta'] = pd.to_numeric(df['Beta'], errors='coerce')
    df['RSI'] = pd.to_numeric(df['RSI'], errors='coerce')
    return df
