import yfinance as yf
import json
import os
import pandas as pd
from datetime import datetime

# CONFIGURATION
tickers = ["UPS", "FDX", "EXPD", "AMZN", "DPSTF"]
folder_name = "last-mile" 

data_dict = {}
current_year = datetime.now().year

for t in tickers:
    try:
        print(f"Syncing {t}...")
        tk = yf.Ticker(t)
        df = tk.history(period="2y", interval="1mo")
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        if df.empty: continue

        prices = [{"date": d.strftime("%Y-%m"), "price": round(float(v), 2)} 
                  for d, v in df["Close"].items()]

        # YTD Logic: Find price from Jan of current year
        ytd_start_price = next((p["price"] for p in prices if p["date"] == f"{current_year}-01"), prices[0]["price"])
        current_price = prices[-1]["price"]
        ytd_growth = round(((current_price - ytd_start_price) / ytd_start_price) * 100, 2)
        total_return = round(((current_price - prices[0]["price"]) / prices[0]["price"]) * 100, 2)

        info = tk.info
        is_etf = info.get("quoteType") == "ETF"
        
        # CLEAN NUMERIC METRIC (Crucial for Weighted Math)
        raw_valuation = info.get("totalAssets") if is_etf else info.get("marketCap")
        
        data_dict[t] = {
            "metadata": {
                "name": info.get("longName", t),
                "summary": info.get("longBusinessSummary", "No summary available."),
                "valuation": raw_valuation if raw_valuation else 0,
                "total_return": f"{total_return}%",
                "ytd_growth": f"{ytd_growth}%",
                "holdings": "Unavailable",
                "type": "ETF" if is_etf else "Stock"
            },
            "prices": prices
        }

        if is_etf:
            try:
                h_df = tk.funds_data.top_holdings
                if h_df is not None and not h_df.empty:
                    data_dict[t]["metadata"]["holdings"] = h_df.index.tolist()[:5]
            except: pass

    except Exception as e:
        print(f"Error on {t}: {e}")

os.makedirs(folder_name, exist_ok=True)
with open(f"{folder_name}/data.json", "w") as f:
    json.dump(data_dict, f, indent=2)
