import telebot
from telebot import types
from flask import Flask
import threading
import os

# -------------------------------
# Telegram Bot Setup
# -------------------------------
TOKEN = os.environ.get("TELEGRAM_TOKEN")  # Use Render Secret
bot = telebot.TeleBot(TOKEN)

# -------------------------------
# Local image-based clothes database
# -------------------------------
clothes = {
    "1": {
        "name": "ቀሚስ",
        "price": "1800",
        "available": True,
        "photo_path": "images/(1).jpg"
    },
    "2": {
        "name": "ጋውን",
        "price": "2200",
        "available": False
        "photo_path": "images/(2).jpg"
    },
    "3": {
        "name": "ጋውን",
        "price": "1800",
        "available": True,
        "photo_path": "images/(3).jpg"
    },
    "4": {
        "name": "ጋውን",
        "price": "2000",
        "available": False,
        "photo_path": "images/(4).jpg"
    },
    "5": {
        "name": "ጋውን",
        "price": "2000",
        "available": False,
        "photo_path": "images/(5).jpg"
    },
    "6": {
        "name": "ቀሚስ",
        "price": "1700",
        "available": True,
        "photo_path": "images/(6).jpg"
    },
    "7": {
        "name": "ቀሚስ",
        "price": "1800",
        "available": True,
        "photo_path": "images/(7).jpg"
    },
    "8": {
        "name": "ቀሚስ",
        "price": "2200",
        "available": True,
        "photo_path": "images/(8).jpg"
    },
    "9": {
        "name": "ሻርፕ",
        "price": "1500",
        "available": True,
        "photo_path": "images/(9).jpg"
    },
    "10": {
        "name": "ሻርፕ",
        "price": "1500",
        "available": True,
        "photo_path": "images/(10).jpg"
    },
    "11": {
        "name": "ሻርፕ",
        "price": "1500",
        "available": False,
        "photo_path": "images/(11).jpg"
    },
    "12": {
        "name": "ሻርፕ",
        "price": "1500",
        "available": False,
        "photo_path": "images/(12).jpg"
    },
    "13": {
        "name": "ሻርፕ",
        "price": "1500",
        "available": False,
        "photo_path": "images/(13).jpg"
    },
    "14": {
        "name": "ሻርፕ",
        "price": "1500",
        "available": True,
        "photo_path": "images/(14).jpg"
    },
    "15": {
        "name": "ጃኬት",
        "price": "2000",
        "available": False,
        "photo_path": "images/(15).jpg"
    },
    "16": {
        "name": "ጋውን",
        "price": "2000",
        "available": True,
        "photo_path": "images/(16).jpg"
    },
    "17": {
        "name": "ካፖርት",
        "price": "2000",
        "available": True,
        "photo_path": "images/(17).jpg"
    },
    "18": {
        "name": "ቀሚስ",
        "price": "2200",
        "available": True,
        "photo_path": "images/(18).jpg"
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

        try:
            # ✅ Open local image each time (Render-safe)
            with open(item["photo_path"], "rb") as photo_file:
                bot.send_photo(
                    message.chat.id,
                    photo_file,
                    caption=caption,
                    parse_mode="Markdown",
                    reply_markup=markup
                )
        except FileNotFoundError:
            bot.send_message(
                message.chat.id,
                f"⚠️ Image not found for {item['name']} (path: {item['photo_path']})"
            )

# -------------------------------
# Handle Button Clicks
# -------------------------------
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    try:
        action, item_key = call.data.split("_", 1)
        item = clothes.get(item_key)

        if not item:
            bot.answer_callback_query(call.id, "❌ Item not found!")
            return

        if action == "price":
            bot.answer_callback_query(call.id, f"The price of {item['name']} is {item['price']} ETB")
        elif action == "avail":
            status = "✅ Available" if item["available"] else "❌ Out of stock"
            bot.answer_callback_query(call.id, f"{item['name']} is {status}")

    except Exception as e:
        print("Callback error:", e)
        bot.answer_callback_query(call.id, "⚠️ Something went wrong!")

# -------------------------------
# Flask web server (for Render)
# -------------------------------
app = Flask(__name__)

@app.route('/')
def home():
    return "🤖 Telegram Clothes Bot is running!"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

# -------------------------------
# Run bot and webserver together
# -------------------------------
def run_bot():
    print("🤖 Bot is online and polling for updates...")
    bot.infinity_polling()

if __name__ == "__main__":
    threading.Thread(target=run_web).start()
    run_bot()
