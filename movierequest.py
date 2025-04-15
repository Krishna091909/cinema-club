import os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext
from loadmovies import load_movies
from deletemessages import delete_message_later
import asyncio

# Fetch from environment variables
REQUEST_GROUP_LINK = os.environ.get("REQUEST_GROUP_LINK")
RENDER_URL = os.environ.get("RENDER_URL")

async def handle_movie_request(update: Update, context: CallbackContext):
    if not update.message or not update.message.text:
        return

    movies = load_movies()
    movie_name = update.message.text.lower()
    matched_movies = [key for key in movies if movie_name in key.lower()]

    # Store user message to delete later
    context.user_data["last_search_message"] = update.message

    if matched_movies:
        keyboard = [
            [InlineKeyboardButton(f"{movies[name]['file_size']} | {movies[name]['file_name']}", callback_data=name)]
            for name in matched_movies
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        sent_msg = await update.message.reply_text(
            "\n🎞️ 𝗦𝗲𝗹𝗲𝗰𝘁 𝗬𝗼𝘂𝗿 𝗙𝗶𝗹𝗺\n⏳This message disappears in 5 minutes\n",
            reply_markup=reply_markup
        )
    else:
        keyboard = [
            [InlineKeyboardButton("📬 Join Request Group", url=REQUEST_GROUP_LINK)],
            [InlineKeyboardButton("✅ Check Available Movies", url=RENDER_URL)]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        sent_msg = await update.message.reply_text(
            "❌ 𝐌𝐨𝐯𝐢𝐞 𝐍𝐨𝐭 𝐅𝐨𝐮𝐧𝐝!\n\n🔎 𝐏𝐥𝐞𝐚𝐬𝐞 𝐂𝐡𝐞𝐜𝐤 𝐭𝐡𝐞 𝐒𝐩𝐞𝐥𝐥𝐢𝐧𝐠\n\n ",
            reply_markup=reply_markup
        )

        # Schedule auto-delete for bot's reply and user's message
    delete_delay = 30 if not matched_movies else 300
    asyncio.create_task(delete_message_later(sent_msg, delete_delay))
    asyncio.create_task(delete_message_later(update.message, 300))

