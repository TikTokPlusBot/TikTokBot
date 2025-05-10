import os
import telebot
from flask import Flask, request

# === Configuration ===
API_TOKEN = os.environ['API_TOKEN']
ADMIN_ID = 7984779406  # Your Telegram ID
TARGET_CHAT_ID = -1002613048185  # Your group/channel ID

bot = telebot.TeleBot(API_TOKEN)
app = Flask(__name__)

# === Start ===
@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.reply_to(message, "Hello! I'm ready to serve, baby.")

# === /postvideo Command ===
@bot.message_handler(commands=['postvideo'])
def handle_post_video(message):
    if message.reply_to_message and message.reply_to_message.video:
        video = message.reply_to_message.video.file_id
        caption = message.reply_to_message.caption or "Enjoy the video!"
        msg = bot.send_video(
            chat_id=TARGET_CHAT_ID,
            video=video,
            caption=caption,
            reply_markup=generate_main_menu()
        )
        bot.reply_to(message, f"Posted to group with buttons under it.")
    else:
        bot.reply_to(message, "Reply to a video message with /postvideo.")

# === /addbuttons for Manual Use ===
@bot.message_handler(commands=['addbuttons'])
def handle_add_buttons(message):
    if message.reply_to_message:
        bot.send_message(
            message.chat.id,
            "Choose an action:",
            reply_to_message_id=message.reply_to_message.message_id,
            reply_markup=generate_main_menu()
        )
    else:
        bot.reply_to(message, "Reply to a message with /addbuttons.")

# === Inline Buttons Callback ===
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    user = call.from_user
    action = call.data
    chat = call.message.chat

    if action == "watch_video":
        bot.answer_callback_query(call.id, "Enjoy the video!")
    elif action == "download_video":
        bot.answer_callback_query(call.id, "Preparing your download...")

    # DM admin
    try:
        log = (
            f"User @{user.username or 'NoUsername'} (ID: {user.id}) "
            f"pressed '{action}' in {chat.title or 'private chat'}"
        )
        bot.send_message(ADMIN_ID, log)
    except Exception as e:
        print(f"Failed to DM admin: {e}")

# === Button Generator ===
def generate_main_menu():
    markup = telebot.types.InlineKeyboardMarkup()
    markup.row(
        telebot.types.InlineKeyboardButton("▶️ Watch", callback_data="watch_video"),
        telebot.types.InlineKeyboardButton("⬇️ Download", callback_data="download_video")
    )
    return markup

# === Flask Webhook ===
@app.route(f"/{API_TOKEN}", methods=['POST'])
def webhook():
    bot.process_new_updates([
        telebot.types.Update.de_json(request.stream.read().decode("utf-8"))
    ])
    return "ok", 200

@app.route('/')
def index():
    bot.set_webhook(url=f"https://tiktokbot-00js.onrender.com/{API_TOKEN}")
    return "Webhook set", 200

# === Run App ===
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
