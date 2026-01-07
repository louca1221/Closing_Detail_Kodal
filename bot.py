import yfinance as yf
import requests
import os
import pandas as pd
from datetime import datetime

# GitHub Secrets
TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

def get_kod_report():
    print("Gathering data from Yahoo Finance...")
    ticker = yf.Ticker("KOD.L")
    
    # 1. Get current data
    y_data = ticker.info
    
    # Fetch price (tries regularMarketPrice first, then currentPrice)
    price = y_data.get('regularMarketPrice') or y_data.get('currentPrice') or 0
    prev_close = y_data.get('previousClose') or 0
    vol_today = y_data.get('regularMarketVolume') or 0
    
    # 2. Volume Trend Analysis
    # Get 15 days of history to calculate a reliable 10-day average
    hist = ticker.history(period="15d")
    avg_vol_10d = hist['Volume'].tail(10).mean()
    vol_ratio = (vol_today / avg_vol_10d) if avg_vol_10d > 0 else 0
    
    if vol_ratio > 1.5:
        vol_trend = "High"
    elif vol_ratio < 0.5:
        vol_trend = "Low"
    else:
        vol_trend = "Normal"

    # 3. Calculations
    change_pct = ((price - prev_close) / prev_close) * 100 if prev_close else 0
    emoji = "🟢" if change_pct >= 0 else "🔴"
    total_value_gbp = (vol_today * price) / 100
    mkt_cap = f"{y_data.get('marketCap', 0):,}"
    
    # Header Date
    today_str = datetime.now().strftime('%d %b %Y')

    report = (
        f"*Kodal Minerals Market Report - {today_str}*\n"
        f"-----------\n"
        f"{emoji} *Price:* {price}p ({change_pct:+.2f}%)\n"
        f"*Source:* Yahoo Finance\n"
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
        print("Error: TOKEN or CHAT_ID is missing.")
        return
        
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID, 
        "text": text, 
        "parse_mode": "Markdown"
    }
    
    r = requests.post(url, data=payload)
    if r.status_code != 200:
        print(f"❌ Telegram Error: {r.text}")
    else:
        print("✅ Message sent successfully!")

if __name__ == "__main__":
    try:
        msg = get_kod_report()
        send_telegram_msg(msg)
    except Exception as e:
        print(f"System Crash: {e}")
