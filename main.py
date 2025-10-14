# bot_check_buttons.py
import os
import sqlite3
import asyncio
from typing import Tuple

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputFile,
)
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

DB_PATH = "items.db"
TOKEN = os.environ.get("TELEGRAM_TOKEN")  # set this in your environment

# ---------- Simple DB helpers ----------
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY,
        name TEXT,
        price_cents INTEGER,
        available INTEGER  -- 1 or 0
    )
    """)
    # sample data (id=1)
    cur.execute("INSERT OR IGNORE INTO items (id, name, price_cents, available) VALUES (1, 'Cool Widget', 1999, 1)")
    cur.execute("INSERT OR IGNORE INTO items (id, name, price_cents, available) VALUES (2, 'Sold Out Thing', 2599, 0)")
    conn.commit()
    conn.close()

def get_item(item_id: int) -> Tuple[int, str, int, int] | None:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id, name, price_cents, available FROM items WHERE id = ?", (item_id,))
    row = cur.fetchone()
    conn.close()
    return row  # None or tuple

# ---------- Bot handlers ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a photo (or product) with buttons to check availability/price."""
    chat_id = update.effective_chat.id

    # We'll show item id 1 as example
    item_id = 1
    item = get_item(item_id)
    if not item:
        await context.bot.send_message(chat_id, "No item found in DB.")
        return

    _, name, price_cents, available = item
    caption = f"{name}\n\nTap a button to check availability or price."

    # Inline keyboard with callback data containing the item id
    keyboard = [
        [
            InlineKeyboardButton("Check if available", callback_data=f"avail:{item_id}"),
            InlineKeyboardButton("Check price", callback_data=f"price:{item_id}"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Send a sample photo. Replace with your image path or URL.
    # For a local file:
    # await context.bot.send_photo(chat_id=chat_id, photo=open("product1.jpg", "rb"), caption=caption, reply_markup=reply_markup)
    # For a URL:
    photo_url = "https://telegra.ph/file/2a7a6f2b3b5f6e3d1f1e2.jpg"  # replace with your photo or file
    await context.bot.send_photo(chat_id=chat_id, photo=photo_url, caption=caption, reply_markup=reply_markup)

async def callback_query_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()  # Acknowledge callback quickly to remove spinner on client

    data = query.data  # e.g., "avail:1" or "price:1"
    if not data:
        await query.edit_message_text("Invalid action.")
        return

    try:
        action, sid = data.split(":")
        item_id = int(sid)
    except Exception:
        await query.edit_message_text("Malformed callback data.")
        return

    item = get_item(item_id)
    if not item:
        await query.edit_message_text("Item not found.")
        return

    _, name, price_cents, available = item

    if action == "avail":
        # Example: check availability (here from DB). Replace with external API if needed.
        msg = f"✅ *{name}* is available now." if available else f"❌ *{name}* is currently out of stock."
        # You can either edit the original message or send a new one:
        await query.message.reply_markdown(msg)
    elif action == "price":
        # Format price nicely
        price = price_cents / 100.0
        msg = f"💲 Price for *{name}*: `{price:.2f}` (USD assumed)."
        await query.message.reply_markdown(msg)
    else:
        await query.edit_message_text("Unknown action.")

# ---------- main ----------
def main():
    init_db()
    if TOKEN is None:
        raise RuntimeError("Please set TELEGRAM_TOKEN environment variable.")

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(callback_query_handler))

    # Use long polling for development. For production consider webhooks.
    print("Bot started (polling). Press Ctrl+C to stop.")
    app.run_polling()

if __name__ == "__main__":
    main()
