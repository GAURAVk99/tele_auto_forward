import asyncio
import logging
import threading
from telethon import TelegramClient, events
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# === TELETHON (Userbot) CONFIG ===
api_id = 20877162
api_hash = '6dfa90f0624d13f591753174e2c56e8a'
session_name = 'forwarder_session'

# === TELEGRAM BOT CONFIG ===
bot_token = '7681888610:AAFCqyElrXweC1R7vQcg53TS2YHih210wsc'
admin_user_id = 1013148420  # Your Telegram user ID

# === INITIAL SETTINGS ===
source_chats = [-1001234567890]
destination_chats = [-1009876543210]
forward_as_copy = True
keywords = ['python']
skip_media = True
custom_prefix = '[AutoFWD] '
custom_suffix = ' #bot'
delay_seconds = 2

client = TelegramClient(session_name, api_id, api_hash)

# === FORWARDING LOGIC ===
@client.on(events.NewMessage(chats=lambda e: source_chats))
async def forward_handler(event):
    message_text = event.raw_text.lower()

    if keywords and not any(k in message_text for k in keywords):
        return
    if skip_media and event.media:
        return

    if forward_as_copy:
        msg = custom_prefix + event.raw_text + custom_suffix
        for dest in destination_chats:
            await client.send_message(dest, msg)
            await asyncio.sleep(delay_seconds)
    else:
        for dest in destination_chats:
            await event.forward_to(dest)
            await asyncio.sleep(delay_seconds)

# === COMMAND BOT HANDLERS ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != admin_user_id:
        return
    await update.message.reply_text("✅ Auto Forwarder Command Bot is running!")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != admin_user_id:
        return
    status_text = (
        f"📊 **Bot Status**\n"
        f"🟢 Source: {source_chats}\n"
        f"📤 Destination: {destination_chats}\n"
        f"📄 Copy Mode: {'ON' if forward_as_copy else 'OFF'}\n"
        f"🔍 Keywords: {keywords}\n"
        f"🚫 Skip Media: {'YES' if skip_media else 'NO'}\n"
        f"⏱ Delay: {delay_seconds}s"
    )
    await update.message.reply_text(status_text, parse_mode="Markdown")

async def toggle_copy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global forward_as_copy
    if update.effective_user.id != admin_user_id:
        return
    forward_as_copy = not forward_as_copy
    await update.message.reply_text(f"📄 Forward as copy: {'ON' if forward_as_copy else 'OFF'}")

async def set_keywords(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global keywords
    if update.effective_user.id != admin_user_id:
        return
    keywords = context.args
    await update.message.reply_text(f"✅ Updated keywords: {keywords}")

async def add_source(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global source_chats
    if update.effective_user.id != admin_user_id:
        return
    try:
        chat_id = int(context.args[0])
        if chat_id not in source_chats:
            source_chats.append(chat_id)
            await update.message.reply_text(f"✅ Added source chat: {chat_id}")
        else:
            await update.message.reply_text("⚠️ Chat already in source list.")
    except:
        await update.message.reply_text("❌ Usage: /addsource <chat_id>")

async def remove_source(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global source_chats
    if update.effective_user.id != admin_user_id:
        return
    try:
        chat_id = int(context.args[0])
        if chat_id in source_chats:
            source_chats.remove(chat_id)
            await update.message.reply_text(f"✅ Removed source chat: {chat_id}")
        else:
            await update.message.reply_text("⚠️ Chat not found in source list.")
    except:
        await update.message.reply_text("❌ Usage: /removesource <chat_id>")

async def add_dest(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global destination_chats
    if update.effective_user.id != admin_user_id:
        return
    try:
        chat_id = int(context.args[0])
        if chat_id not in destination_chats:
            destination_chats.append(chat_id)
            await update.message.reply_text(f"✅ Added destination chat: {chat_id}")
        else:
            await update.message.reply_text("⚠️ Chat already in destination list.")
    except:
        await update.message.reply_text("❌ Usage: /adddest <chat_id>")

async def remove_dest(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global destination_chats
    if update.effective_user.id != admin_user_id:
        return
    try:
        chat_id = int(context.args[0])
        if chat_id in destination_chats:
            destination_chats.remove(chat_id)
            await update.message.reply_text(f"✅ Removed destination chat: {chat_id}")
        else:
            await update.message.reply_text("⚠️ Chat not found in destination list.")
    except:
        await update.message.reply_text("❌ Usage: /removedest <chat_id>")

# === UPDATED: /menu Command with Command Buttons ===
async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != admin_user_id:
        return

    keyboard = [
        ["/start", "/status"],
        ["/copy", "/keywords"],
        ["/addsource", "/removesource"],
        ["/adddest", "/removedest"],
    ]

    reply_markup = ReplyKeyboardMarkup(
        keyboard, resize_keyboard=True, one_time_keyboard=False
    )

    await update.message.reply_text(
        "📋 Choose a command from below:", reply_markup=reply_markup
    )

# === START COMMAND BOT ===
def start_command_bot():
    asyncio.set_event_loop(asyncio.new_event_loop())
    app = ApplicationBuilder().token(bot_token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("copy", toggle_copy))
    app.add_handler(CommandHandler("keywords", set_keywords))
    app.add_handler(CommandHandler("addsource", add_source))
    app.add_handler(CommandHandler("removesource", remove_source))
    app.add_handler(CommandHandler("adddest", add_dest))
    app.add_handler(CommandHandler("removedest", remove_dest))
    app.add_handler(CommandHandler("menu", menu))
    app.run_polling()

# === RUN BOT ===
def run_both():
    thread = threading.Thread(target=start_command_bot)
    thread.start()
    client.start()
    client.run_until_disconnected()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_both()
