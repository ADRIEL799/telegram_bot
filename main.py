import telebot
from telebot import types

# Replace with your bot token
BOT_TOKEN = "8195063787:AAHvQ7JCUMH3FmSZQxrw4Qu6DDoPbIgNaiA"
bot = telebot.TeleBot(BOT_TOKEN)

# Example clothes database
clothes = {
    "shirt1": {"price": "$20", "available": True, "photo": "https://example.com/shirt.jpg"},
    "hoodie1": {"price": "$35", "available": False, "photo": "https://example.com/hoodie.jpg"},
}

# Command to show all clothes
@bot.message_handler(commands=["start", "shop"])
def show_shop(message):
    for item_name, item in clothes.items():
        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton("💰 Check Price", callback_data=f"price_{item_name}"),
            types.InlineKeyboardButton("📦 Check Availability", callback_data=f"avail_{item_name}")
        )
        bot.send_photo(message.chat.id, item["photo"], caption=f"👕 {item_name.capitalize()}", reply_markup=markup)

# Handle button presses
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    action, item_name = call.data.split("_", 1)
    item = clothes[item_name]

    if action == "price":
        bot.answer_callback_query(call.id, f"The price is {item['price']}")
    elif action == "avail":
        available_text = "✅ Available" if item["available"] else "❌ Out of stock"
        bot.answer_callback_query(call.id, available_text)

# Run the bot
print("🤖 Bot is running...")
bot.infinity_polling()
