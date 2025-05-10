import os
import telebot
from flask import Flask, request

# --- Configuration ---
API_TOKEN = os.environ['API_TOKEN']
ADMIN_ID = 7984779406  # Your Telegram user ID

bot = telebot.TeleBot(API_TOKEN)
app = Flask(__name__)

# --- Start Handler ---
@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.send_message(message.chat.id, "Welcome! I'm ready to track activity.")

# --- Command to Add Buttons ---
@bot.message_handler(commands=['addbuttons'])
def handle_addbuttons(message):
    if message.reply_to_message:
        bot.send_message(
            message.chat.id,
            "Choose an action:",
            reply_to_message_id=message.reply_to_message.message_id,
            reply_markup=generate_main_menu()
        )
    else:
        bot.reply_to(message, "Reply to a video message with /addbuttons to add buttons.")

# --- Callback Handler ---
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    user = call.from_user
    action = call.data
    chat = call.message.chat

    log = f"User @{user.username or 'NoUsername'} (ID: {user.id}) pressed '{action}' in group: {chat.title or chat.id}"
    
    if action == "watch_video":
        bot.answer_callback_query(call.id, "Enjoy the video!")
    elif action == "download_video":
        bot.answer_callback_query(call.id, "Preparing your download...")

    # Log privately to admin
    try:
        bot.send_message(ADMIN_ID, log)
    except Exception as e:
        print(f"Failed to DM admin: {e}")

# --- Inline Keyboard Markup ---
def generate_main_menu():
    markup = telebot.types.InlineKeyboardMarkup()
    markup.row(
        telebot.types.InlineKeyboardButton("▶️ Watch", callback_data="watch_video"),
        telebot.types.InlineKeyboardButton("⬇️ Download", callback_data="download_video")
    )
    return markup

# --- Flask Webhook Endpoint ---
@app.route(f"/{API_TOKEN}", methods=['POST'])
def telegram_webhook():
    bot.process_new_updates([
        telebot.types.Update.de_json(request.stream.read().decode("utf-8"))
    ])
    return "ok", 200

# --- Set Webhook on Root ---
@app.route('/')
def set_webhook():
    webhook_url = f"https://tiktokbot-00js.onrender.com/{API_TOKEN}"
    bot.set_webhook(url=webhook_url)
    return "Webhook set", 200

# --- Run ---
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
