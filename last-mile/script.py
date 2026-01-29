import yfinance as yf
import json
import os

# 1. Logistics Tickers
tickers = ["UPS", "FDX", "EXPD", "AMZN"]

data_dict = {}

# 2. Process each ticker one by one (The Reliable Way)
for t in tickers:
    try:
        print(f"Syncing {t}...")
        # Get 2 years of monthly data
        df = yf.download(t, period="2y", interval="1mo")
        
        if not df.empty:
            # In the latest yfinance, 'Close' is the adjusted price by default
            # We use .iloc[:, 0] to grab the first column safely if names vary
            prices = df['Close'] 
            
            data_dict[t] = [
                {"date": d.strftime('%Y-%m'), "price": round(float(v), 2)}
                for d, v in prices.items()
            ]
            print(f"Successfully processed {t}")
        else:
            print(f"Warning: No data for {t}")
            
    except Exception as e:
        print(f"Error on {t}: {e}")

# 3. Ensure the last-mile directory exists
os.makedirs('last-mile', exist_ok=True)

with open('last-mile/data.json', 'w') as f:
    json.dump(data_dict, f)

print("Logistics Data Sync Complete.")
