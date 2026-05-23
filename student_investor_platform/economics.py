import requests
import pandas as pd
from functools import lru_cache
import plotly.express as px

WORLD_BANK_BASE = "https://api.worldbank.org/v2"
RESTCOUNTRIES_ALL = "https://restcountries.com/v3.1/all"
RESTCOUNTRIES_NAME = "https://restcountries.com/v3.1/name"
EXCHANGE_RATE_URL = "https://api.exchangerate.host/latest"

INDICATOR_CODES = {
    "Inflation": "FP.CPI.TOTL.ZG",
    "GDP": "NY.GDP.MKTP.CD",
    "GDP Growth": "NY.GDP.MKTP.KD.ZG",
    "Unemployment": "SL.UEM.TOTL.ZS",
    "Interest Rate": "FR.INR.RINR",
    "Exports": "NE.EXP.GNFS.CD",
    "Imports": "NE.IMP.GNFS.CD"
}

HEATMAP_INDICATORS = {
    "Inflation": "Inflation",
    "GDP Growth": "GDP Growth",
    "Unemployment": "Unemployment",
    "Interest Rate": "Interest Rate",
    "Currency Strength": "Currency Strength",
    "Trade Balance": "Trade Balance"
}


@lru_cache(maxsize=None)
def fetch_world_bank_indicator(code, country="all", start_year=2015, end_year=2024):
    country_path = country if country == "all" else country
    url = f"{WORLD_BANK_BASE}/country/{country_path}/indicator/{code}?date={start_year}:{end_year}&format=json&per_page=20000"
    resp = requests.get(url, timeout=20)
    resp.raise_for_status()
    payload = resp.json()
    if not isinstance(payload, list) or len(payload) < 2:
        return pd.DataFrame()
    records = []
    for item in payload[1]:
        if item.get("value") is None:
            continue
        records.append({
            "iso3": item.get("countryiso3code"),
            "country": item.get("country", {}).get("value"),
            "year": int(item.get("date", 0)),
            "value": float(item.get("value"))
        })
    return pd.DataFrame(records)


@lru_cache(maxsize=None)
def fetch_country_info(country_name):
    params = {"fullText": "true"}
    resp = requests.get(f"{RESTCOUNTRIES_NAME}/{country_name}", params=params, timeout=20)
    if resp.status_code != 200:
        resp = requests.get(f"{RESTCOUNTRIES_NAME}/{country_name}", timeout=20)
    resp.raise_for_status()
    data = resp.json()
    if not data:
        raise ValueError(f"Country not found: {country_name}")
    item = data[0]
    currencies = item.get("currencies", {})
    currency_code = next(iter(currencies.keys()), None)
    currency_name = currencies.get(currency_code, {}).get("name") if currency_code else None
    return {
        "name": item.get("name", {}).get("common", country_name),
        "iso3": item.get("cca3"),
        "region": item.get("region"),
        "subregion": item.get("subregion"),
        "population": item.get("population"),
        "currency_code": currency_code,
        "currency_name": currency_name,
        "flag": item.get("flags", {}).get("emoji")
    }


@lru_cache(maxsize=None)
def fetch_exchange_rates(base="USD"):
    resp = requests.get(EXCHANGE_RATE_URL, params={"base": base}, timeout=20)
    resp.raise_for_status()
    return resp.json().get("rates", {})


@lru_cache(maxsize=None)
def get_currency_strength_data():
    countries = requests.get(RESTCOUNTRIES_ALL, timeout=30).json()
    rates = fetch_exchange_rates(base="USD")
    rows = []
    for country in countries:
        iso3 = country.get("cca3")
        currencies = country.get("currencies", {})
        if not iso3 or not currencies:
            continue
        currency_code = next(iter(currencies.keys()))
        rate = rates.get(currency_code)
        if rate is None or rate <= 0:
            continue
        strength = 1 / rate
        rows.append({
            "iso3": iso3,
            "country": country.get("name", {}).get("common"),
            "value": strength,
            "currency_code": currency_code
        })
    return pd.DataFrame(rows)


def get_latest_indicator_values(code):
    data = fetch_world_bank_indicator(code)
    if data.empty:
        return pd.DataFrame()
    return data.sort_values(["iso3", "year"]).groupby("iso3", as_index=False).last()


def build_heatmap_data(indicator_name):
    if indicator_name == "Currency Strength":
        df = get_currency_strength_data()
        df = df.dropna(subset=["value"])
        return df
    if indicator_name == "Trade Balance":
        exports = get_latest_indicator_values(INDICATOR_CODES["Exports"])
        imports = get_latest_indicator_values(INDICATOR_CODES["Imports"])
        if exports.empty or imports.empty:
            return pd.DataFrame()
        merged = exports.merge(imports, on=["iso3", "country"], suffixes=("_exp", "_imp"))
        merged["value"] = merged["value_exp"] - merged["value_imp"]
        return merged[["iso3", "country", "year_exp", "value"]].rename(columns={"year_exp": "year"})
    code = INDICATOR_CODES.get(indicator_name)
    if not code:
        return pd.DataFrame()
    return get_latest_indicator_values(code)


def get_country_indicator_series(country_name, indicator_name, years=15):
    info = fetch_country_info(country_name)
    code = INDICATOR_CODES.get(indicator_name)
    if not code or not info.get("iso3"):
        return pd.Series(dtype=float)
    df = fetch_world_bank_indicator(code, country=info["iso3"], start_year=2000, end_year=2024)
    if df.empty:
        return pd.Series(dtype=float)
    df = df.sort_values("year")
    return pd.Series(df["value"].values, index=df["year"].astype(int), name=indicator_name)


def get_indicator_series(country_name, indicator_name):
    mapping = {
        "Inflation (CPI)": "Inflation",
        "GDP (current US$)": "GDP",
        "Unemployment rate": "Unemployment",
        "GDP Growth": "GDP Growth",
        "Interest Rate": "Interest Rate",
        "Inflation": "Inflation",
        "Unemployment": "Unemployment",
    }
    mapped = mapping.get(indicator_name, indicator_name)
    return get_country_indicator_series(country_name, mapped)


def get_country_summary(country_name):
    info = fetch_country_info(country_name)
    summary = {
        "Country": info.get("name"),
        "Region": info.get("region"),
        "Subregion": info.get("subregion"),
        "Population": info.get("population"),
        "Currency": info.get("currency_name"),
        "Currency Code": info.get("currency_code"),
        "Exchange Rate (USD)": None,
        "GDP": None,
        "GDP Growth": None,
        "Inflation": None,
        "Unemployment": None,
        "Interest Rate": None,
        "Trade Balance": None,
        "Economic Summary": None,
        "Flag": info.get("flag")
    }
    if info.get("currency_code"):
        rates = fetch_exchange_rates(base="USD")
        currency = info["currency_code"]
        rate = rates.get(currency)
        summary["Exchange Rate (USD)"] = rate
    for label in ["GDP", "GDP Growth", "Inflation", "Unemployment", "Interest Rate"]:
        series = get_country_indicator_series(country_name, label)
        summary[label] = float(series.dropna().iloc[-1]) if not series.empty else None
    exports = fetch_world_bank_indicator(INDICATOR_CODES["Exports"], country=info["iso3"], start_year=2000, end_year=2024)
    imports = fetch_world_bank_indicator(INDICATOR_CODES["Imports"], country=info["iso3"], start_year=2000, end_year=2024)
    if not exports.empty and not imports.empty:
        exp_val = exports.sort_values("year").iloc[-1]["value"]
        imp_val = imports.sort_values("year").iloc[-1]["value"]
        summary["Trade Balance"] = float(exp_val - imp_val)
    summary["Economic Summary"] = (
        f"{summary['Country']} has a GDP of {summary['GDP']:,} USD with an inflation rate of {summary['Inflation']}% "
        f"and unemployment at {summary['Unemployment']}%. Recent GDP growth is {summary['GDP Growth']}%."
    )
    return summary


def get_available_countries():
    data = fetch_world_bank_indicator(INDICATOR_CODES["GDP"])
    if data.empty:
        return []
    return sorted(data["country"].dropna().unique())


def get_comparison_data(country_names):
    rows = []
    for country in country_names:
        summary = get_country_summary(country)
        rows.append({
            "Country": summary["Country"],
            "GDP": summary["GDP"],
            "GDP Growth": summary["GDP Growth"],
            "Inflation": summary["Inflation"],
            "Unemployment": summary["Unemployment"],
            "Interest Rate": summary["Interest Rate"],
            "Currency": summary["Currency"],
            "Exchange Rate (USD)": summary["Exchange Rate (USD)"]
        })
    return pd.DataFrame(rows)


def plot_indicator(series, title=None):
    if series.empty:
        return px.line(title=title)
    df = series.reset_index()
    df.columns = ["year", "value"]
    fig = px.line(df, x="year", y="value", title=title)
    return fig
