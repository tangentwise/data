import yfinance as yf
import json
import os
import pandas as pd
from datetime import datetime

# CONFIGURATION: Add as many sectors as you want here.
sector_map = {
    "battery-index": ["LIT", "LITP", "ION", "GSG"],
    "last-mile": ["UPS", "FDX", "AMZN", "EXPD", "DPSTF"],
    "mro-dist": ["AIT", "DXP", "GWW", "FAST", "MSM", "WCC"],
    "gig-economy": ["UBER", "DASH", "LYFT", "TOST"],
    "robotics-smid": ["TER", "IRBT", "RKDA", "ROBO", "BOTZ"] # Teradyne, iRobot, etc.
}

def sync_sector(folder, ticker_list):
    data_dict = {}
    current_year = datetime.now().year
    print(f"--- Syncing {folder} ---")

    for t in ticker_list:
        try:
            tk = yf.Ticker(t)
            # Use 'max' or '2y' to ensure we have Jan 1st for YTD
            df = tk.history(period="2y", interval="1mo")
            if df.empty: continue
            
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

            prices = [{"date": d.strftime("%Y-%m"), "price": round(float(v), 2)} 
                      for d, v in df["Close"].items()]

            # Safety check: find the first entry of the current year for YTD
            ytd_entry = next((p for p in prices if p["date"].startswith(str(current_year))), prices[0])
            ytd_start_price = ytd_entry["price"]
            cur_price = prices[-1]["price"]
            
            info = tk.info
            is_etf = info.get("quoteType") == "ETF"
            val = info.get("totalAssets") if is_etf else info.get("marketCap")

            data_dict[t] = {
                "metadata": {
                    "name": info.get("longName", t),
                    "summary": info.get("longBusinessSummary", "N/A"),
                    "valuation": val or 0,
                    "ytd_growth": f"{round(((cur_price - ytd_start_price)/ytd_start_price)*100, 2)}%",
                    "total_return": f"{round(((cur_price - prices[0]['price'])/prices[0]['price'])*100, 2)}%",
                    "type": "ETF" if is_etf else "Stock",
                    "holdings": "N/A"
                },
                "prices": prices
            }
            
            # Fetch ETF holdings if available
            if is_etf:
                try:
                    h_df = tk.funds_data.top_holdings
                    if h_df is not None:
                        data_dict[t]["metadata"]["holdings"] = h_df.index.tolist()[:5]
                except: pass

            print(f"  Success: {t}")
        except Exception as e:
            print(f"  Error {t}: {e}")

    os.makedirs(folder, exist_ok=True)
    with open(f"{folder}/data.json", "w") as f:
        json.dump(data_dict, f, indent=2)

for folder, tickers in sector_map.items():
    sync_sector(folder, tickers)
