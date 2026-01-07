import yfinance as yf
import requests
import os
import pandas as pd

TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('CHAT_ID') 
MS_KEY = os.getenv('MARKETSTACK_KEY')

def get_marketstack_price():
    """Fetches the official EOD closing price from Marketstack"""
    if not MS_KEY:
        print("Marketstack Key missing.")
        return None
    try:
        # Use XLON for London Stock Exchange & http for Free Plan compatibility
        url = f"http://api.marketstack.com/v1/eod/latest?access_key={MS_KEY}&symbols=KOD.XLON"
        response = requests.get(url)
        data_json = response.json()
        
        if 'data' in data_json and len(data_json['data']) > 0:
            ms_price = data_json['data'][0]['close']
            print(f"✅ Marketstack Price Found: {ms_price}")
            return ms_price
        else:
            print(f"❌ Marketstack API Error: {data_json.get('error', 'No data returned')}")
            return None
    except Exception as e:
        print(f"⚠️ Marketstack Connection Error: {e}")
        return None

def get_kod_report():
    print("Fetching data...")
    ticker = yf.Ticker("KOD.L")
    
    ms_price = get_marketstack_price()
    y_data = ticker.info
    
    # Logic: Use Marketstack price if available, otherwise use Yahoo
    price_source = "Marketstack" if ms_price else "Yahoo Finance"
    price = ms_price if ms_price else (y_data.get('regularMarketPrice') or y_data.get('currentPrice') or 0)
    
    prev_close = y_data.get('previousClose') or 0
    vol_today = y_data.get('regularMarketVolume') or 0
    
    # Volume Trend (Yahoo)
    hist = ticker.history(period="15d")
    avg_vol_10d = hist['Volume'].tail(10).mean()
    vol_ratio = (vol_today / avg_vol_10d) if avg_vol_10d > 0 else 0
    vol_trend = "High 🔥" if vol_ratio > 1.5 else "Low 💤" if vol_ratio < 0.5 else "Normal ✅"

    change_pct = ((price - prev_close) / prev_close) * 100 if prev_close else 0
    emoji = "🟢" if change_pct >= 0 else "🔴"
    total_value_gbp = (vol_today * price) / 100
    mkt_cap = f"{y_data.get('marketCap', 0):,}"

    # FIXED: Corrected the unclosed asterisk/parenthesis on the volume trend line
    report = (
        f"*Kodal Minerals (KOD.L) Report*\n"
        f"-----------\n"
        f"{emoji} *Price:* {price}p ({change_pct:+.2f}%)\n"
        f"*Source:* {price_source}\n"
        f"-----------\n"
        f"◽️ *Today's Volume:* {vol_today:,}\n"
        f"◽️ *10D Avg:* {int(avg_vol_10d):,}\n"
        f"◽️ *Activity:* {vol_trend}\n"
        f"◽️ *Market Cap:* £{mkt_cap}\n"
        f"-----------\n"
        f"◽️ *Value Traded:* £{total_value_gbp:,.2f}\n"
        f"◽️ *Day Range:* {y_data.get('dayLow')}p - {y_data.get('dayHigh')}p\n"
        f"-----------\n"
    )
    return report

def send_telegram_msg(text):
    if not TOKEN or not CHAT_ID:
        print("Missing Credentials")
        return
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"}
    r = requests.post(url, data=payload)
    
    # This will print the exact reason if Telegram rejects the message again
    if r.status_code != 200:
        print(f"❌ Telegram Error {r.status_code}: {r.text}")
    else:
        print("✅ Message sent successfully!")

if __name__ == "__main__":
    try:
        msg = get_kod_report()
        send_telegram_msg(msg)
    except Exception as e:
        print(f"Global Error: {e}")
