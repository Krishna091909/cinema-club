from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler
from telegram.ext import CommandHandler, MessageHandler, filters
from loadmovies import save_movie
from deletemessages import delete_message_later
import asyncio
import os

# Define conversation states
MOVIE_NAME, FILE_ID, FILE_SIZE, FILE_NAME = range(4)

OWNER_ID = int(os.getenv("OWNER_ID", "0"))  # Default to 0 if not set

async def start_add_movie(update: Update, context: CallbackContext):
    if update.message.from_user.id != OWNER_ID:
        reply = await update.message.reply_text("🚫 You are not authorized to use this command.")
        asyncio.create_task(delete_message_later(reply, 300))
        asyncio.create_task(delete_message_later(update.message, 300))
        return ConversationHandler.END

    reply = await update.message.reply_text("🎬 Please enter the **Movie Name**:")
    asyncio.create_task(delete_message_later(reply, 300))
    asyncio.create_task(delete_message_later(update.message, 300))
    return MOVIE_NAME

async def movie_name_handler(update: Update, context: CallbackContext):
    context.user_data["movie_name"] = update.message.text
    reply = await update.message.reply_text("📂 Now, please enter the **File ID**:")
    asyncio.create_task(delete_message_later(reply, 300))
    asyncio.create_task(delete_message_later(update.message, 300))
    return FILE_ID

async def file_id_handler(update: Update, context: CallbackContext):
    context.user_data["file_id"] = update.message.text
    reply = await update.message.reply_text("📏 Now, please enter the **File Size** (e.g., 541.92MB):")
    asyncio.create_task(delete_message_later(reply, 300))
    asyncio.create_task(delete_message_later(update.message, 300))
    return FILE_SIZE

async def file_size_handler(update: Update, context: CallbackContext):
    context.user_data["file_size"] = update.message.text
    reply = await update.message.reply_text("📄 Finally, please enter the **File Name** (e.g., movie.mkv):")
    asyncio.create_task(delete_message_later(reply, 300))
    asyncio.create_task(delete_message_later(update.message, 300))
    return FILE_NAME

async def file_name_handler(update: Update, context: CallbackContext):
    context.user_data["file_name"] = update.message.text

    # Save to Google Sheet
    save_movie(
        context.user_data["movie_name"],
        context.user_data["file_id"],
        context.user_data["file_size"],
        context.user_data["file_name"]
    )

    reply = await update.message.reply_text(f"✅ Movie '{context.user_data['movie_name']}' added successfully!")
    asyncio.create_task(delete_message_later(reply, 300))
    asyncio.create_task(delete_message_later(update.message, 300))
    return ConversationHandler.END

async def cancel(update: Update, context: CallbackContext):
    reply = await update.message.reply_text("❌ Movie addition cancelled.")
    asyncio.create_task(delete_message_later(reply, 300))
    asyncio.create_task(delete_message_later(update.message, 300))
    return ConversationHandler.END
