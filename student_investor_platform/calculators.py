import numpy as np
import pandas as pd


def compound_interest(principal, annual_rate, years, compounds_per_year=1):
    rate = annual_rate / 100
    periods = years * compounds_per_year
    value = principal * (1 + rate / compounds_per_year) ** periods
    timeline = np.linspace(0, years, periods + 1)
    values = principal * (1 + rate / compounds_per_year) ** (timeline * compounds_per_year)
    return float(value), pd.DataFrame({'Year': timeline, 'Value': values})


def sip_value(monthly_amount, annual_return, years):
    r = annual_return / 100 / 12
    n = years * 12
    future_value = monthly_amount * ((1 + r) ** n - 1) / r * (1 + r)
    timeline = np.arange(1, n + 1)
    values = monthly_amount * ((1 + r) ** timeline - 1) / r * (1 + r)
    return float(future_value), pd.DataFrame({'Month': timeline, 'Value': values})


def emi(principal, annual_rate, years):
    monthly_rate = annual_rate / 100 / 12
    n = years * 12
    if monthly_rate == 0:
        payment = principal / n
    else:
        payment = principal * monthly_rate * (1 + monthly_rate) ** n / ((1 + monthly_rate) ** n - 1)
    return float(payment)


def ddm(dividend, required_return, growth_rate):
    r = required_return / 100
    g = growth_rate / 100
    if r <= g:
        return None
    return float(dividend * (1 + g) / (r - g))


def dcf(cash_flows, discount_rate, terminal_growth=0.02):
    r = discount_rate / 100
    pv = 0.0
    for i, cf in enumerate(cash_flows, start=1):
        pv += cf / ((1 + r) ** i)
    terminal_value = cash_flows[-1] * (1 + terminal_growth) / (r - terminal_growth)
    pv += terminal_value / ((1 + r) ** len(cash_flows))
    return float(pv)
