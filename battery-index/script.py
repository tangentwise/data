import yfinance as yf
import json
import os

# 1. Define your Hard Asset basket
tickers = ["LIT", "LITP", "ION", "GSG"]

data_dict = {}

# 2. Process each ticker individually to avoid Multi-Index headaches
for t in tickers:
    try:
        print(f"Syncing {t}...")
        # Get 2 years of monthly data
        df = yf.download(t, period="2y", interval="1mo")
        
        if not df.empty:
            # Target the 'Close' column (yfinance v0.2.x standard)
            # We convert to float and round to 2 decimals for clean JSON
            close_col = 'Close' if 'Close' in df.columns else 'Adj Close'
            series = df[close_col]

            
            data_dict[t] = [
                {"date": d.strftime('%Y-%m'), "price": round(float(v), 2)}
                for d, v in series.items() 
            ]
            print(f"Successfully added {t}")
        else:
            print(f"No data found for {t}")
            
    except Exception as e:
        print(f"Error downloading {t}: {e}")

# 3. Ensure the directory exists before saving
# This matches your specific file path: battery-index/data.json
os.makedirs('battery-index', exist_ok=True)

with open('battery-index/data.json', 'w') as f:
    json.dump(data_dict, f)

print("Batch sync complete. JSON updated.")

