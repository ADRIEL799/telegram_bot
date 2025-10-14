import telebot
from telebot import types
from flask import Flask
import threading
import os

# Replace this with your actual bot token
TOKEN = os.environ.get("TELEGRAM_TOKEN")
bot = telebot.TeleBot(TOKEN)

# -------------------------------
# Example clothes "database"
# -------------------------------
clothes = {
    "shirt1": {
        "name": "Jacket",
        "price": "1700",
        "available": True,
        "photo_path": "photo_3_2025-07-15_16-13-20.jpg"
    },
    "hoodie1": {
        "name": "Warm Hoodie",
        "price": "1500",
        "available": False,
        "photo_path": "clothes/warm_hoodie2.jpg"
    },
    "jeans1": {
        "name": "Slim Fit Jeans",
        "price": "2000",
        "available": True,
        "photo_path": "clothes/slim_jeans.jpg"
    }
}

# -------------------------------
# Telegram Bot Handlers
# -------------------------------
@bot.message_handler(commands=["start", "shop"])
def show_shop(message):
    bot.send_message(message.chat.id, "🛍️ Welcome to the Clothing Shop!\nBrowse the available items below:")
    for item_key, item in clothes.items():
        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton("💰 Check Price", callback_data=f"price_{item_key}"),
            types.InlineKeyboardButton("📦 Check Availability", callback_data=f"avail_{item_key}")
        )
        caption = f"👕 *{item['name']}*"
        bot.send_photo(message.chat.id, item["photo"], caption=caption, parse_mode="Markdown", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    try:
        action, item_key = call.data.split("_", 1)
        item = clothes.get(item_key)

        if not item:
            bot.answer_callback_query(call.id, "❌ Item not found!")
            return

        if action == "price":
            bot.answer_callback_query(call.id, f"The price of {item['name']} is {item['price']}")
        elif action == "avail":
            status = "✅ Available" if item["available"] else "❌ Out of stock"
            bot.answer_callback_query(call.id, f"{item['name']} is {status}")
    except Exception as e:
        print("Callback error:", e)
        bot.answer_callback_query(call.id, "⚠️ Something went wrong!")

# -------------------------------
# Flask web server (Render fix)
# -------------------------------
app = Flask(__name__)

@app.route('/')
def home():
    return "🤖 Telegram Clothes Bot is running!"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

# -------------------------------
# Start both bot & webserver
# -------------------------------
def run_bot():
    print("🤖 Bot is online and polling for updates...")
    bot.infinity_polling()

if __name__ == "__main__":
    threading.Thread(target=run_web).start()
    run_bot()
