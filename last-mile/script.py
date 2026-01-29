import yfinance as yf
import json
import os
import pandas as pd

# Set your tickers here (Update this list for each folder's script)
tickers = ["UPS", "FDX", "EXPD", "AMZN"] 
folder_name = "battery-index" # Change to "last-mile" for the other folder

data_dict = {}

for t in tickers:
    try:
        print(f"Syncing {t}...")
        tk = yf.Ticker(t)
        
        # 1. Fetch History
        df = tk.history(period="2y", interval="1mo")
        if df.empty:
            print(f"No price data for {t}")
            continue

        prices = [{"date": d.strftime("%Y-%m"), "price": round(float(v), 2)} 
                  for d, v in df["Close"].items()]

        # 2. Calculate Returns for Badges
        start_price = prices[0]["price"]
        current_price = prices[-1]["price"]
        total_return = round(((current_price - start_price) / start_price) * 100, 2)

        # 12M Return calculation
        m12_price = prices[-13]["price"] if len(prices) >= 13 else start_price
        return_12m = round(((current_price - m12_price) / m12_price) * 100, 2)

        # 3. Fetch Metadata
        info = tk.info
        is_etf = info.get("quoteType") == "ETF"
        
        # Market Cap vs Net Assets
        metric_val = info.get("totalAssets") if is_etf else info.get("marketCap")
        if metric_val:
            metric_str = f"{'Net Assets' if is_etf else 'Market Cap'}: ${metric_val:,.0f}"
        else:
            metric_str = "Valuation: Unavailable"

        # ETF Holdings Logic
        holdings = "Unavailable"
        if is_etf:
            try:
                h_df = tk.funds_data.top_holdings
                if h_df is not None and not h_df.empty:
                    holdings = h_df.index.tolist()[:5] # Top 5 names
            except:
                pass

        # 4. Assemble Object
        data_dict[t] = {
            "metadata": {
                "name": info.get("longName", t),
                "summary": info.get("longBusinessSummary", "No summary available."),
                "metric": metric_str,
                "total_return": f"{total_return}%",
                "return_12m": f"{return_12m}%",
                "holdings": holdings,
                "type": "ETF" if is_etf else "Stock"
            },
            "prices": prices
        }
        print(f"Successfully processed {t}")

    except Exception as e:
        print(f"Error on {t}: {e}")

# Save to the specific folder
os.makedirs(folder_name, exist_ok=True)
with open(f"{folder_name}/data.json", "w") as f:
    json.dump(data_dict, f, indent=2)

print(f"Update complete for {folder_name}.")
