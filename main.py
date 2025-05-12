import os
from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler
from yt_dlp import YoutubeDL
from dotenv import load_dotenv
import logging
import re

load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")

from telegram import Bot
bot = Bot(token=TOKEN)

app = Flask(__name__)
dispatcher = Dispatcher(bot, update_queue=None, use_context=True)

user_links = {}

def start(update: Update, context: CallbackContext):
    update.message.reply_text("Envía un nombre de video o un link de YouTube.")

import re

def handle_message(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    text = update.message.text.strip()

    # Verificar si es un enlace de YouTube
    is_link = re.match(r'^https?://(www\.)?(youtube\.com|youtu\.be)/', text)

    # Si no es link, usar ytsearch
    video_source = text if is_link else f"ytsearch1:{text}"

    user_links[chat_id] = video_source

    keyboard = [
        [InlineKeyboardButton("🎵 Audio", callback_data='audio'),
         InlineKeyboardButton("🎥 Video", callback_data='video')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("¿Qué formato quieres?", reply_markup=reply_markup)

def download_and_send(chat_id, choice):
    query = user_links.get(chat_id)
    if not query:
        bot.send_message(chat_id, "No se encontró la solicitud previa.")
        return

    ydl_opts = {
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'format': 'bestaudio/best' if choice == 'audio' else 'bestvideo+bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio' if choice == 'audio' else 'FFmpegVideoConvertor',
            'preferredcodec': 'mp3' if choice == 'audio' else 'mp4',
        }],
        'noplaylist': True,
    }

    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(query, download=True)
        filename = ydl.prepare_filename(info)
        if choice == 'audio':
            filename = filename.rsplit(".", 1)[0] + ".mp3"
        else:
            filename = filename.rsplit(".", 1)[0] + ".mp4"

    with open(filename, 'rb') as f:
        if choice == 'audio':
            bot.send_audio(chat_id, audio=f)
        else:
            bot.send_video(chat_id, video=f)

    os.remove(filename)
    user_links.pop(chat_id, None)
    bot.send_message(chat_id, "Puedes enviar otro video o link cuando quieras.")

def button(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    choice = query.data
    chat_id = query.message.chat_id

    bot.send_message(chat_id, "Descargando, por favor espera...")
    try:
        download_and_send(chat_id, choice)
    except Exception as e:
        bot.send_message(chat_id, f"Error: {e}")
        user_links.pop(chat_id, None)

dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
dispatcher.add_handler(CallbackQueryHandler(button))

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "ok"

@app.route('/')
def index():
    return "Bot de Telegram activo."

if __name__ == '__main__':
    app.run(port=5000)