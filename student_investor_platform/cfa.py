CFA_CONCEPTS = {
    'Financial Statement Analysis': {
        'summary': 'Use financial ratios, trend analysis, and common-size statements to evaluate company health.',
        'formula': ['Current Ratio = Current Assets / Current Liabilities', 'ROE = Net Income / Shareholders Equity'],
        'example': 'Compare cash flow to net income to assess earnings quality.',
        'visual': 'Analyze a balance sheet, income statement, and cash flow statement side by side.'
    },
    'Time Value of Money': {
        'summary': 'Money available now is worth more than the same amount in the future.',
        'formula': ['PV = FV / (1+r)^n', 'FV = PV * (1+r)^n'],
        'example': 'A discount bond worth $1,000 in 5 years is worth less today depending on interest rate.',
        'visual': 'Show the growth curve of invested capital over time.'
    },
    'Portfolio Management': {
        'summary': 'Diversification and risk management are key to constructing resilient portfolios.',
        'formula': ['Portfolio Return = w1*r1 + w2*r2', 'Portfolio Variance = w^T Σ w'],
        'example': 'Combine stocks and bonds to reduce volatility while targeting returns.',
        'visual': 'Display asset allocation pie chart and risk/return scatter plot.'
    },
    'Equity Investments': {
        'summary': 'Analyze companies using valuation, quality, and growth drivers.',
        'formula': ['P/E = Price / Earnings', 'ROIC = NOPAT / Invested Capital'],
        'example': 'Use relative valuation to compare comparable companies in the same sector.',
        'visual': 'Display valuation metrics and earnings growth charts.'
    },
    'Fixed Income': {
        'summary': 'Fixed income focuses on bonds, yield curves, duration and credit risk.',
        'formula': ['Current Yield = Coupon / Price', 'Duration = weighted average time to cash flows'],
        'example': 'Rising rates reduce bond prices and increase yields.',
        'visual': 'Show a yield curve and bond price sensitivity chart.'
    },
    'Derivatives': {
        'summary': 'Derivatives derive value from underlying assets and are used for hedging.',
        'formula': ['Call Option Value = S*N(d1) - K*e^-rt*N(d2)'],
        'example': 'Use options to hedge downside risk on a stock position.',
        'visual': 'Display payoff diagrams for calls and puts.'
    },
    'Economics': {
        'summary': 'Understand macro factors like GDP, inflation, unemployment and monetary policy.',
        'formula': ['GDP = C + I + G + (X - M)', 'Real GDP = Nominal GDP / Price Index'],
        'example': 'Central bank rate hikes can cool inflation but slow growth.',
        'visual': 'Show economic cycle stages and indicator trends.'
    },
    'Ethics': {
        'summary': 'Ethics ensures trust, transparency and professional conduct in finance.',
        'formula': ['Apply the CFA Code of Ethics and Standards of Professional Conduct.'],
        'example': 'Avoid conflicts of interest and preserve client confidentiality.',
        'visual': 'Highlight ethical decision-making frameworks.'
    },
    'Quantitative Methods': {
        'summary': 'Quant tools help price assets, measure risk, and forecast returns.',
        'formula': ['Mean = Σx/n', 'Variance = Σ(x-μ)^2 / (n-1)'],
        'example': 'Use regression analysis to model expected returns.',
        'visual': 'Display distribution and trend charts.'
    }
}

def search_concepts(query):
    query = query.lower()
    results = {}
    for topic, data in CFA_CONCEPTS.items():
        if query in topic.lower() or query in data['summary'].lower():
            results[topic] = data
    return results
