from telegram import Update
from telegram.ext import CallbackContext
from loadmovies import load_movies
import os

OWNER_ID = int(os.getenv("OWNER_ID", "0"))  # Default to 0 if not set 

async def list_movies(update: Update, context: CallbackContext):
    if update.message.from_user.id != OWNER_ID:
        await update.message.reply_text("🚫 You are not authorized to use this command.")
        return

    movies = load_movies()
    if movies:
        movie_list = "\n".join([f"{i+1}. {name}" for i, name in enumerate(movies.keys())])
        await update.message.reply_text(f"📜 **Movies List:**\n\n{movie_list}")
    else:
        await update.message.reply_text("❌ No movies available.")
