import os
import asyncio
import requests
import time
from flask import Flask, send_file
from threading import Thread
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler, 
    ConversationHandler, CallbackContext, filters
)
from addmovie import (
    start_add_movie, movie_name_handler, file_id_handler, 
    file_size_handler, file_name_handler, cancel, 
    MOVIE_NAME, FILE_ID, FILE_SIZE, FILE_NAME
)
from removemovie import remove_movie_command
from getfile import file_info
from listmovies import list_movies
from loadmovies import load_movies
from help import help_command
from sendmovie import send_movie
from movierequest import handle_movie_request  # Removed pagination import

CHANNEL_LINK = os.environ.get("CHANNEL_LINK")
REQUEST_GROUP_LINK = os.environ.get("REQUEST_GROUP_LINK")

# Fetch bot token from environment variable
BOT_TOKEN = os.environ.get("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable is missing! Set it before running the script.")

# Flask app for keeping the bot alive
app = Flask(__name__)

@app.route('/')
def home():
    return send_file("index.html")

def run_flask():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    url = os.environ.get("RENDER_URL")
    if not url:
        raise ValueError("RENDER_URL environment variable is missing! Set it before running the script.")

    while True:
        try:
            response = requests.get(url)
            print(f"Keep-alive ping sent! Status: {response.status_code}")
        except Exception as e:
            print(f"Keep-alive request failed: {e}")
        time.sleep(49)

# START COMMAND
async def start(update: Update, context: CallbackContext):
    user = update.message.from_user
    name = user.first_name if user.first_name else user.username

    CHANNEL_LINK = os.environ.get("CHANNEL_LINK")
    REQUEST_GROUP_LINK = os.environ.get("REQUEST_GROUP_LINK")

    keyboard = [
        [InlineKeyboardButton("📢 Join Movie Channel", url=CHANNEL_LINK)],
        [InlineKeyboardButton("💬 Join Movie Group", url=REQUEST_GROUP_LINK)]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"🎬 𝐇𝐞𝐥𝐥𝐨 {name}, 𝐖𝐞𝐥𝐜𝐨𝐦𝐞 𝐭𝐨 𝐭𝐡𝐞 𝐌𝐨𝐯𝐢𝐞 𝐁𝐨𝐭! 🍿\n\n"
        "👨‍💻 𝐓𝐡𝐢𝐬 𝐁𝐨𝐭 𝐖𝐚𝐬 𝐃𝐞𝐯𝐞𝐥𝐨𝐩𝐞𝐝 𝐁𝐲 👉 [@ItsKing000](https://t.me/ItsKing000)\n\n"
        "🔍 𝐏𝐥𝐞𝐚𝐬𝐞 𝐒𝐞𝐚𝐫𝐜𝐡 𝐭𝐡𝐞 𝐌𝐨𝐯𝐢𝐞 𝐍𝐚𝐦𝐞, 𝐈'𝐥𝐥 𝐒𝐞𝐧𝐝 𝐘𝐨𝐮 𝐭𝐡𝐞 𝐅𝐢𝐥𝐞 🎥\n\n"
        "🔹 𝐉𝐨𝐢𝐧 𝐨𝐮𝐫 𝐂𝐡𝐚𝐧𝐧𝐞𝐥 & 𝐆𝐫𝐨𝐮𝐩 𝐟𝐨𝐫 𝐭𝐡𝐞 𝐋𝐚𝐭𝐞𝐬𝐭 𝐌𝐨𝐯𝐢𝐞𝐬! 💥",
        parse_mode="Markdown",
        reply_markup=reply_markup
    )


def main():
    Thread(target=run_flask, daemon=True).start()
    Thread(target=keep_alive, daemon=True).start()

    tg_app = Application.builder().token(BOT_TOKEN).build()

    tg_app.add_handler(CommandHandler("start", start))
    tg_app.add_handler(CommandHandler("help", help_command))
    tg_app.add_handler(MessageHandler(filters.Document.ALL, file_info))
    tg_app.add_handler(CommandHandler("removemovie", remove_movie_command))
    tg_app.add_handler(CommandHandler("listmovies", list_movies))

    tg_app.add_handler(ConversationHandler(
        entry_points=[CommandHandler("addmovie", start_add_movie)],
        states={
            MOVIE_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, movie_name_handler)],
            FILE_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, file_id_handler)],
            FILE_SIZE: [MessageHandler(filters.TEXT & ~filters.COMMAND, file_size_handler)],
            FILE_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, file_name_handler)]
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    ))

    tg_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_movie_request))
    tg_app.add_handler(CallbackQueryHandler(send_movie))  # handles movie selection

    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_movie_request))
    application.add_handler(CallbackQueryHandler(button_click))


    

    print("Bot is running...")
    tg_app.run_polling()

if __name__ == "__main__":
    main()
