import os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext
from loadmovies import load_movies
from deletemessages import delete_message_later
import asyncio

REQUEST_GROUP_LINK = os.environ.get("REQUEST_GROUP_LINK")
RENDER_URL = os.environ.get("RENDER_URL")

async def handle_movie_request(update: Update, context: CallbackContext):
    if update.message:
        movie_name = update.message.text.lower()
        context.user_data["movie_name"] = movie_name
        context.user_data["page"] = 0
    else:
        movie_name = context.user_data.get("movie_name", "")
        if not movie_name:
            return

    movies = load_movies()
    matched_movies = [key for key in movies if movie_name in key.lower()]
    
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

    items_per_page = 10
    page = context.user_data.get("page", 0)
    total_pages = (len(matched_movies) + items_per_page - 1) // items_per_page
    page = max(0, min(page, total_pages - 1))
    context.user_data["page"] = page

    start = page * items_per_page
    end = start + items_per_page
    movie_buttons = []

    for key in matched_movies[start:end]:
        file = movies[key]
        btn_text = f"{file['file_size']} | {file['file_name']}"
        movie_buttons.append([InlineKeyboardButton(btn_text, callback_data=key)])

    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("⬅️ Previous", callback_data="prev_page"))
    nav_buttons.append(InlineKeyboardButton(f"📄 {page + 1}/{total_pages}", callback_data="page_info"))
    if page < total_pages - 1:
        nav_buttons.append(InlineKeyboardButton("Next ➡️", callback_data="next_page"))

    movie_buttons.append(nav_buttons)
    reply_markup = InlineKeyboardMarkup(movie_buttons)

    sent = await update.effective_message.reply_text(
        "🎞️ 𝗦𝗲𝗹𝗲𝗰𝘁 𝗬𝗼𝘂𝗿 𝗙𝗶𝗹𝗺\n⏳ This message disappears in 5 minutes",
        reply_markup=reply_markup
    )

    asyncio.create_task(delete_message_later(sent, 300))
    if update.message:
        asyncio.create_task(delete_message_later(update.message, 300))

async def button_click(update: Update, context: CallbackContext):
    query = update.callback_query
    data = query.data

    if data == "next_page":
        context.user_data["page"] = context.user_data.get("page", 0) + 1
        await query.message.delete()
        await handle_movie_request(update, context)
    elif data == "prev_page":
        context.user_data["page"] = context.user_data.get("page", 0) - 1
        await query.message.delete()
        await handle_movie_request(update, context)
    elif data == "page_info":
        await query.answer("You are on the current page.")
    else:
        # Pass to sendmovies
        context.user_data["selected_movie"] = data
        await query.answer()
        await send_movie(update, context)  # defined below or in sendmovies.py
