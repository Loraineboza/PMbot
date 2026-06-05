import os
import threading
from flask import Flask
from your_bot_file import bot, dp  # замени на свои импорты

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

@app.route('/health')
def health():
    return "OK", 200

def run_bot():
    # Запуск твоего бота (polling)
    # Здесь код запуска твоего бота
    pass

if __name__ == '__main__':
    # Запускаем бота в отдельном потоке
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.start()
    
    # Запускаем Flask сервер (Render требует открытый порт)
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)