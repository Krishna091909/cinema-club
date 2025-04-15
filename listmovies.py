from telegram import Update
from telegram.ext import CallbackContext
from loadmovies import load_movies
from deletemessages import delete_message_later
import os
import asyncio

OWNER_ID = int(os.getenv("OWNER_ID", "0"))  # Default to 0 if not set 

async def list_movies(update: Update, context: CallbackContext):
    if update.message.from_user.id != OWNER_ID:
        msg = await update.message.reply_text("🚫 You are not authorized to use this command.")
        asyncio.create_task(delete_message_later(update.message, 300))
        asyncio.create_task(delete_message_later(msg, 300))
        return

    movies = load_movies()
    if movies:
        movie_list = "\n".join([f"{i+1}. {name}" for i, name in enumerate(movies.keys())])
        msg = await update.message.reply_text(f"📜 **Movies List:**\n\n{movie_list}", parse_mode="Markdown")
    else:
        msg = await update.message.reply_text("❌ No movies available.")

    # Auto-delete both user and bot messages after 5 minutes
    asyncio.create_task(delete_message_later(update.message, 300))
    asyncio.create_task(delete_message_later(msg, 300))
