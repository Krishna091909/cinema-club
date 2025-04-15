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
    # Check if it's a new search (from message) or pagination (from button)
    if update.message and update.message.text:
        # New search
        movie_name = update.message.text.lower()
        context.user_data["movie_name"] = movie_name
        context.user_data["page"] = 0
        context.user_data["last_search_message"] = update.message
    else:
        # Pagination button click
        movie_name = context.user_data.get("movie_name", "")
        if not movie_name:
            return  # No previous search data, stop here

    movies = load_movies()
    matched_movies = [key for key in movies if movie_name in key.lower()]

    # If no matches found, show not found message
    if not matched_movies:
        keyboard = [
            [InlineKeyboardButton("📬 Join Request Group", url=REQUEST_GROUP_LINK)],
            [InlineKeyboardButton("✅ Check Available Movies", url=RENDER_URL)]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        sent_msg = await update.effective_message.reply_text(
            "❌ 𝐌𝐨𝐯𝐢𝐞 𝐍𝐨𝐭 𝐅𝐨𝐮𝐧𝐝!\n\n🔎 𝐏𝐥𝐞𝐚𝐬𝐞 𝐂𝐡𝐞𝐜𝐤 𝐭𝐡𝐞 𝐒𝐩𝐞𝐥𝐥𝐢𝐧𝐠\n\n ",
            reply_markup=reply_markup
        )
        asyncio.create_task(delete_message_later(sent_msg, 30))
        return

    # Pagination setup
    items_per_page = 10
    total_pages = (len(matched_movies) + items_per_page - 1) // items_per_page

    # Clamp page number within bounds
    current_page = context.user_data.get("page", 0)
    current_page = max(0, min(current_page, total_pages - 1))
    context.user_data["page"] = current_page

    start_index = current_page * items_per_page
    end_index = start_index + items_per_page
    movies_to_display = matched_movies[start_index:end_index]

    # Create keyboard with movie buttons
    keyboard = [
        [InlineKeyboardButton(f"{movies[name]['file_size']} | {movies[name]['file_name']}", callback_data=name)]
        for name in movies_to_display
    ]

    # Navigation buttons
    nav_buttons = []
    if current_page > 0:
        nav_buttons.append(InlineKeyboardButton("⬅️ Previous", callback_data="previous_page"))
    if current_page < total_pages - 1:
        nav_buttons.append(InlineKeyboardButton("Next ➡️", callback_data="next_page"))

    # Add page info
    keyboard.append([InlineKeyboardButton(f"📄 Page {current_page + 1}/{total_pages}", callback_data="no_action")])
    if nav_buttons:
        keyboard.append(nav_buttons)

    reply_markup = InlineKeyboardMarkup(keyboard)

    sent_msg = await update.effective_message.reply_text(
        f"🎞️ 𝗦𝗲𝗹𝗲𝗰𝘁 𝗬𝗼𝘂𝗿 𝗙𝗶𝗹𝗺\n⏳This message disappears in 5 minutes\n📄 Page {current_page + 1}/{total_pages}",
        reply_markup=reply_markup
    )

    # Delete message later
    asyncio.create_task(delete_message_later(sent_msg, 300))
    if update.message:
        asyncio.create_task(delete_message_later(update.message, 300))

async def button_click(update: Update, context: CallbackContext):
    query = update.callback_query
    data = query.data

    # Handle pagination
    if data == "previous_page":
        context.user_data["page"] = context.user_data.get("page", 0) - 1
    elif data == "next_page":
        context.user_data["page"] = context.user_data.get("page", 0) + 1

    # Reuse existing movie name and refresh results
    await handle_movie_request(update, context)
    await query.answer()
