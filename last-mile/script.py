import yfinance as yf
import json

# Logistical Tickers: UPS (Standard), FDX (Air/Ground), EXPD (Global Logistics), AMZN (Infrastructure)
tickers = ["UPS", "FDX", "EXPD", "AMZN"]
df = yf.download(tickers, period="2y", interval="1mo")['Adj Close'].dropna()

data_dict = {t: [{"date": d.strftime('%Y-%m'), "price": round(v, 2)} 
             for d, v in df[t].items()] for t in tickers}

with open('last-mile/data.json', 'w') as f:
    json.dump(data_dict, f)
