import yfinance as yf
import requests
import os
import pandas as pd

TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

def get_kod_report():
    print("Fetching data for Kodal Minerals...")
    ticker = yf.Ticker("KOD.L")
    
    # Get current info
    data = ticker.info
    price = data.get('regularMarketPrice') or data.get('currentPrice') or 0
    prev_close = data.get('previousClose') or 0
    vol_today = data.get('regularMarketVolume') or 0
    
    # Get 10-day history for average volume
    hist = ticker.history(period="15d") # Get 15 days to ensure we have 10 trading days
    avg_vol_10d = hist['Volume'].tail(10).mean()
    
    # Calculate Volume Trend
    vol_ratio = (vol_today / avg_vol_10d) if avg_vol_10d > 0 else 0
    if vol_ratio > 1.5:
        vol_trend = "High"
    elif vol_ratio < 0.5:
        vol_trend = "Low"
    else:
        vol_trend = "Normal"

    # Price Change
    change_pct = ((price - prev_close) / prev_close) * 100 if prev_close else 0
    emoji = "🟢" if change_pct >= 0 else "🔴"
    
    # Monetary Value (Price in p, so divide by 100 for £)
    total_value_gbp = (vol_today * price) / 100

    # Handle Market Cap safely
    mkt_cap_raw = data.get('marketCap') or 0
    mkt_cap = f"{mkt_cap_raw:,}" if isinstance(mkt_cap_raw, int) else "N/A"

    report = (
        f" *Kodal Minerals - Market Close Report*\n"
        f"-----------\n"
        f"{emoji} *Price:* {price}p ({change_pct:+.2f}%)\n"
        f"📈 *Today's Volume:* {vol_today:,}\n"
        f"📊 *10D Avg Vol:* {int(avg_vol_10d):,}\n"
        f"-----------\n"
        f"🔘 *Volume Level:* {vol_trend}\n"
        f"💰 *Total Value Traded:* £{total_value_gbp:,.2f}\n"
        f"-----------\n"
        f"↕️ *Day Range:* {data.get('dayLow')}p - {data.get('dayHigh')}p\n"
        f"🏢 *Market Cap:* £{mkt_cap}\n"
    )
    return report

def send_telegram_msg(text):
    if not TOKEN or not CHAT_ID:
        print("Missing Credentials")
        return
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"}
    r = requests.post(url, data=payload)
    print(f"Status: {r.status_code}")

if __name__ == "__main__":
    try:
        msg = get_kod_report()
        send_telegram_msg(msg)
    except Exception as e:
        print(f"Error: {e}")
