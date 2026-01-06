import yfinance as yf
import requests
import os

TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

def get_kod_report():
    print("Fetching data for Kodal Minerals...")
    ticker = yf.Ticker("KOD.L")
    data = ticker.info
    
    # Logic to handle missing data
    price = data.get('regularMarketPrice') or data.get('currentPrice') or "N/A"
    prev_close = data.get('previousClose', "N/A")
    volume = data.get('regularMarketVolume', 0)
    
    report = (
        f"📊 *Kodal Minerals (KOD.L) Update*\n"
        f"--- --- --- --- --- --- ---\n"
        f"💰 *Current Price:* {price}p\n"
        f"📉 *Prev Close:* {prev_close}p\n"
        f"↕️ *Day Range:* {day_low}p - {day_high}p\n"
        f"📈 *Volume:* {volume:,}\n"
        f"🏢 *Market Cap:* £{data.get('marketCap', 0):,}\n"
        f"--- --- --- --- --- --- ---\n"
        f"🕒 _Data from Yahoo Finance_"
    )
    return report

def send_telegram_msg(text):
    if not TOKEN or not CHAT_ID:
        print("ERROR: Missing TOKEN or CHAT_ID in GitHub Secrets!")
        return

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"}
    
    response = requests.post(url, data=payload)
    print(f"Telegram Response: {response.status_code} - {response.text}")

if __name__ == "__main__":
    report_text = get_kod_report()
    send_telegram_msg(report_text)
