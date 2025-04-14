import logging
from telethon import Button, errors
from telethon.events import NewMessage
from telethon.extensions import html
from WebStreamer.bot import StreamBot
from WebStreamer.utils.file_properties import get_file_info, pack_file, get_short_hash
from WebStreamer.vars import Var

# Enable logging
logging.basicConfig(level=logging.INFO)

@StreamBot.on(NewMessage(func=lambda e: True if e.message.file and e.is_private else False))
async def media_receive_handler(event):
    try:
        user = await event.get_sender()

        # Check if the user is allowed to use the bot
        if Var.ALLOWED_USERS and not ((str(user.id) in Var.ALLOWED_USERS) or (user.username in Var.ALLOWED_USERS)):
            return await event.reply(
                message="❌ You are not authorized to use this bot.",
                link_preview=False,
                parse_mode=html
            )

        # Forward the received file to the BIN_CHANNEL
        log_msg = await event.message.forward_to(Var.BIN_CHANNEL)
        file_info = get_file_info(log_msg)

        # Generate file hash and stream link
        full_hash = pack_file(
            file_info.file_name,
            file_info.file_size,
            file_info.mime_type,
            file_info.id
        )
        file_hash = get_short_hash(full_hash)
        stream_link = f"{Var.URL}stream/{log_msg.id}?hash={file_hash}"

        # Prepare the reply text
        reply_text = f"""
👋 𝗛𝗲𝗹𝗹𝗼 {html.escape(user.first_name)},

✅ 𝗬𝗼𝘂𝗿 𝗟𝗶𝗻𝗸 𝗛𝗮𝘀 𝗕𝗲𝗲𝗻 𝗚𝗲𝗻𝗲𝗿𝗮𝘁𝗲𝗱!

📂 <b>Fɪʟᴇ Nᴀᴍᴇ:</b> <code>{html.escape(file_info.file_name)}</code>

📦 <b>Fɪʟᴇ Sɪᴢᴇ:</b> <code>{round(file_info.file_size / (1024 * 1024), 2)} MB</code>

🎥 <b>𝙐𝙨𝙚 𝙑𝙇𝘾 𝙥𝙡𝙖𝙮𝙚𝙧</b> for better support of all video formats.
"""

        # Send the reply with buttons
        await event.reply(
            message=reply_text,
            link_preview=False,
            buttons=[
                [Button.url("📥 Download", url=stream_link)],
                [Button.url("🎬 Join Movie Updates Channel", url="https://t.me/+MhdyDUCdRR1lNGNl")]
            ],
            parse_mode="html"
        )

    except errors.FloodWaitError as e:
        logging.error(f"FloodWaitError: {e}")
        await event.reply("⚠️ You're sending too many requests. Please wait and try again.")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        await event.reply("⚠️ An unexpected error occurred. Please try again.")
