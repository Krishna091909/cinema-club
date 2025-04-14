import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from WebStreamer.utils.file_properties import get_file_info, pack_file, get_short_hash
from WebStreamer.vars import Var
from WebStreamer.bot import client  # Telethon client
from loadmovies import load_movies  # Function to load movies from sheet

async def send_movie(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    movie_name = query.data
    movies = load_movies()  # Load movie data from Google Sheet
    movie_data = movies.get(movie_name)

    if movie_data:
        user_id = query.from_user.id
        file_id = movie_data["file_id"]
        file_size = movie_data["file_size"]
        file_name = movie_data["file_name"]

        try:
            # Step 1: Get file information (no forwarding)
            file_info = get_file_info(file_id)

            # Step 2: Generate stream link and hash
            full_hash = pack_file(file_info.file_name, file_info.file_size, file_info.mime_type, file_info.id)
            file_hash = get_short_hash(full_hash)
            stream_link = f"{Var.URL}stream/{file_info.id}?hash={file_hash}"

        except Exception as e:
            await query.message.reply_text(f"❌ Error generating download link: {e}")
            return

        # Step 3: Prepare download and stream buttons
        keyboard = [
            [InlineKeyboardButton("📥 Download", url=stream_link)],
            [InlineKeyboardButton("🎬 Join Channel", url="https://t.me/YOUR_CHANNEL_LINK")]  # Optional
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # Step 4: Send movie file with download button
        await context.bot.send_document(
            chat_id=user_id,
            document=file_id,
            caption=(
                f"🎬 *{file_name}*\n\n"
                f"📦 *Size:* {round(file_size / (1024 * 1024), 2)} MB\n\n"
                f"🔗 𝗖𝗹𝗶𝗰𝗸 𝗕𝗲𝗹𝗼𝘄 𝘁𝗼 𝗗𝗼𝘄𝗻𝗹𝗼𝗮𝗱 𝗳𝗮𝘀𝘁!"
            ),
            parse_mode="Markdown",
            reply_markup=reply_markup
        )

        # Step 5: Clean up old messages after 5 minutes
        user_message = query.message
        asyncio.create_task(delete_message_later(user_message, 300))

    else:
        error_msg = await query.message.reply_text("❌ Movie not found.")
        await asyncio.sleep(5)
        asyncio.create_task(delete_message_later(error_msg, 300))
