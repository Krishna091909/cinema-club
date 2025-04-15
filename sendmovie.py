import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from loadmovies import load_movies
from deletemessages import delete_message_later

import os

FILMSTREAM_BOT_USERNAME = os.getenv("FILMSTREAM_BOT_USERNAME")


async def send_movie(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    movie_name = query.data
    movies = load_movies()
    movie_data = movies.get(movie_name)

    if movie_data:
        user_id = query.from_user.id  
        file_id = movie_data["file_id"]
        file_size = movie_data["file_size"]
        file_name = movie_data["file_name"]

        # Create button to open Filestream bot
        keyboard = [
            [InlineKeyboardButton("🚀 Open Fast Download Bot", url=f"https://t.me/{FILMSTREAM_BOT_USERNAME}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # Send movie document with instruction and button
        await context.bot.send_document(
            chat_id=user_id,
            document=file_id,
            caption=(
                f"🎬 *{file_name}*\n\n"
                f"📦 *Size:* {file_size}\n\n"
                f"🤖 𝐅𝐨𝐫𝐰𝐚𝐫𝐝 𝐭𝐡𝐢𝐬 𝐟𝐢𝐥𝐞 𝐭𝐨 @{FILMSTREAM_BOT_USERNAME} 𝐭𝐨 𝐠𝐞𝐭 𝐅𝐚𝐬𝐭 𝐃𝐨𝐰𝐧𝐥𝐨𝐚𝐝"
            ),
            parse_mode="Markdown",
            reply_markup=reply_markup
        )

        # Delete inline button message after 5 minutes
        user_message = query.message  
        asyncio.create_task(delete_message_later(user_message, 300))

        # Delete user's search message after 5 minutes
        search_message = context.user_data.get("last_search_message")
        if search_message:
            asyncio.create_task(delete_message_later(search_message, 300))
            context.user_data["last_search_message"] = None

    else:
        error_msg = await query.message.reply_text("❌ Movie not found.")
        await asyncio.sleep(5)
        asyncio.create_task(delete_message_later(error_msg, 300))
