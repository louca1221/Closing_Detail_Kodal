import yfinance as yf
import requests
import os
import pandas as pd
from datetime import datetime

TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('CHAT_ID') 
MS_KEY = os.getenv('MARKETSTACK_KEY')

def get_marketstack_price():
    """Fetches the official EOD closing price using the working symbol KOD.L"""
    if not MS_KEY:
        return None
    try:
        # Reverted back to KOD.L based on your testing
        url = f"http://api.marketstack.com/v2/intraday?access_key={MS_KEY}&symbols=KOD.L"
        response = requests.get(url)
        data_json = response.json()
        
        if 'data' in data_json and len(data_json['data']) > 0:
            item = data_json['data'][0]
            ms_price = item['close']
            # Get the date of the price to verify it's today's data
            raw_date = item['date'][:10] # Gets YYYY-MM-DD
            print(f"✅ Marketstack (KOD.L) Price: {ms_price} from {raw_date}")
            return ms_price, raw_date
        return None, None
    except Exception as e:
        print(f"⚠️ Marketstack Error: {e}")
        return None, None

def get_kod_report():
    print("Gathering data...")
    ticker = yf.Ticker("KOD.L")
    
    # 1. Get Marketstack Price and Date
    ms_price, ms_date = get_marketstack_price()
    
    # 2. Get Yahoo Data for analysis
    y_data = ticker.info
    
    # Determine which price to use
    # If Marketstack provides a price, we use it. Otherwise, Yahoo is our safety.
    price = ms_price if ms_price else (y_data.get('regularMarketPrice') or y_data.get('currentPrice') or 0)
    price_source = "Yahoo Finance" if ms_price else "Yahoo Finance"
    
    prev_close = y_data.get('previousClose') or 0
    vol_today = y_data.get('regularMarketVolume') or 0
    
    # Volume Trend
    hist = ticker.history(period="15d")
    avg_vol_10d = hist['Volume'].tail(10).mean()
    vol_ratio = (vol_today / avg_vol_10d) if avg_vol_10d > 0 else 0
    vol_trend = "High" if vol_ratio > 1.5 else "Low" if vol_ratio < 0.5 else "Good"

    change_pct = ((price - prev_close) / prev_close) * 100 if prev_close else 0
    emoji = "🟢" if change_pct >= 0 else "🔴"
    total_value_gbp = (vol_today * price) / 100
    mkt_cap = f"{y_data.get('marketCap', 0):,}"

    # Use today's date for the header
    today_str = datetime.now().strftime('%d %b %Y')

    report = (
        f"*Kodal Minerals - Market Close Report*\n"
        f"{today_str}\n"
        f"-----------\n"
        f"{emoji} *Price:* {price}p ({change_pct:+.2f}%)\n"
        f"*Source:* {price_source} ({ms_date if ms_date else 'Live'})\n"
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
        print("Credentials missing")
        return
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"}
    r = requests.post(url, data=payload)
    if r.status_code != 200:
        print(f"❌ Telegram Error: {r.text}")
    else:
        print("✅ Success!")

if __name__ == "__main__":
    try:
        msg = get_kod_report()
        send_telegram_msg(msg)
    except Exception as e:
        print(f"Crash: {e}")
