import yfinance as yf
import requests
import os

# Get secrets from GitHub Environment Variables
TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

def get_kod_report():
    ticker = yf.Ticker("KOD.L")
    data = ticker.info
    
    price = data.get('regularMarketPrice') or data.get('currentPrice')
    prev_close = data.get('previousClose')
    volume = data.get('regularMarketVolume', 0)
    
    report = (
        f"📊 *Kodal Minerals (KOD.L) Daily Report*\n"
        f"--- --- --- --- --- ---\n"
        f"💰 Close Price: {price}p\n"
        f"📉 Prev Close: {prev_close}p\n"
        f"📈 Volume: {volume:,}\n"
        f"🏢 Mkt Cap: £{data.get('marketCap', 0):,}\n"
    )
    return report

def send_telegram_msg(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"}
    requests.post(url, data=payload)

if __name__ == "__main__":
    report_text = get_kod_report()
    send_telegram_msg(report_text)
