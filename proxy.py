import os
import re
import time
import random
import requests
import telebot
import threading
import concurrent.futures
from flask import Flask
from telebot import types

# --- CONFIG ---
TOKEN = "8624293703:AAESXSXWeZ8TRVY6kyfWBUKRYJfk-M3ZAVI"
PORT = int(os.environ.get("PORT", 8080)) # Порт для хостинга

# --- KEEP-ALIVE SERVER ---
app = Flask('')

@app.route('/')
def home():
    return "Code-01 System is Online"

def run_web():
    app.run(host='0.0.0.0', port=PORT)

# --- PROXY ENGINE ---
class CloudBypass:
    def __init__(self):
        self.sources = [
            "https://api.proxyscrape.com/v2/?request=getproxies&proxytype=socks5",
            "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks5.txt",
            "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/socks5.txt"
        ]

    def fetch(self):
        proxies = set()
        for url in self.sources:
            try:
                r = requests.get(url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
                if r.status_code == 200:
                    found = re.findall(r'(\d{1,3}(?:\.\d{1,3}){3}):(\d{2,5})', r.text)
                    for ip, port in found:
                        proxies.add(f"{ip}:{port}")
            except: continue
        return list(proxies)

    def verify(self, proxy):
        px = {'http': f'socks5://{proxy}', 'https': f'socks5://{proxy}'}
        try:
            # Короткий таймаут для бесплатного хостинга
            start = time.time()
            r = requests.get("http://cp.cloudflare.com/generate_204", proxies=px, timeout=3)
            if r.status_code == 204:
                return (proxy, int((time.time() - start) * 1000))
        except: return None

# --- BOT ---
bot = telebot.TeleBot(TOKEN)
engine = CloudBypass()

@bot.message_handler(commands=['start'])
def start(message):
    kb = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("⚡️ ТОП-4 FAST", callback_data="go"))
    bot.send_message(message.chat.id, "<b>Code-01 Cloud Mode</b>\nСистема адаптирована под Free Tier.", parse_mode="HTML", reply_markup=kb)

@bot.callback_query_handler(func=lambda call: call.data == "go")
def run(call):
    bot.answer_callback_query(call.id, "Checking...")
    raw = engine.fetch()
    # Берем случайную выборку 50 шт, чтобы не перегружать CPU
    to_test = random.sample(raw, min(len(raw), 50))
    
    valid = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as ex:
        results = list(ex.map(engine.verify, to_test))
        valid = [r for r in results if r]
    
    valid.sort(key=lambda x: x[1])
    top_4 = valid[:4]
    
    if not top_4:
        bot.send_message(call.message.chat.id, "❌ Нет живых прокси. Повторите.")
        return

    res = "<b>🚀 ТОП-4 SOCKS5 (Free Tier):</b>\n\n"
    for p, ms in top_4:
        ip, port = p.split(':')
        res += f"🔹 <code>{p}</code> [<b>{ms}ms</b>]\n┗ <a href='https://t.me/socks?server={ip}&port={port}'>Connect</a>\n\n"
    bot.send_message(call.message.chat.id, res, parse_mode="HTML", disable_web_page_preview=True)

if __name__ == "__main__":
    # Запуск веб-сервера в отдельном потоке
    threading.Thread(target=run_web).start()
    print("Web Server Started. Starting Bot...")
    bot.infinity_polling()

