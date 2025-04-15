from loadmovies import remove_movie
from telegram import Update
from telegram.ext import CallbackContext
from deletemessages import delete_message_later
import os
import asyncio

OWNER_ID = int(os.getenv("OWNER_ID", "0"))  # Default to 0 if not set

async def remove_movie_command(update: Update, context: CallbackContext):
    # Delete user message after 5 mins
    asyncio.create_task(delete_message_later(update.message, 300))

    # Check if the user is authorized
    if update.message.from_user.id != OWNER_ID:
        msg = await update.message.reply_text("🚫 You are not authorized to use this command.")
        asyncio.create_task(delete_message_later(msg, 300))
        return

    # Ensure a movie name is provided
    if not context.args:
        msg = await update.message.reply_text("❌ Please provide a movie name to remove. Usage: /removemovie <movie_name>")
        asyncio.create_task(delete_message_later(msg, 300))
        return

    movie_name = " ".join(context.args)  # Combine all arguments into a single movie name
    if remove_movie(movie_name):  # Call the function that actually removes the movie
        msg = await update.message.reply_text(f"🗑️ Movie '{movie_name}' removed successfully!")
    else:
        msg = await update.message.reply_text("❌ Movie not found!")

    # Delete bot response after 5 mins
    asyncio.create_task(delete_message_later(msg, 300))
