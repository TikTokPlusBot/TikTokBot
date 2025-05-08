import os
import telebot
from flask import Flask, request

API_TOKEN = os.environ['API_TOKEN']  # Replace with your actual bot token

bot = telebot.TeleBot(API_TOKEN)
app = Flask(__name__)

# --- Interaction Tracker ---
@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.send_message(message.chat.id, "Welcome! Choose an action:",
                     reply_markup=generate_main_menu())

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    user = call.from_user
    action = call.data
    print(f"User @{user.username} ({user.id}) clicked: {action}")

    if action == "watch_video":
        bot.answer_callback_query(call.id, "Tracking started. Enjoy!")
        bot.send_message(call.message.chat.id, "Here's your video:")
        bot.send_video(call.message.chat.id, "https://www.example.com/your_video.mp4")
    elif action == "download_video":
        bot.answer_callback_query(call.id, "Logging download request...")
        bot.send_message(call.message.chat.id, "Your download will begin shortly.")
    elif action == "vip_only":
        bot.answer_callback_query(call.id, "VIP only! Access denied.")

# --- Inline Keyboard ---
def generate_main_menu():
    markup = telebot.types.InlineKeyboardMarkup()
    markup.row(
        telebot.types.InlineKeyboardButton("▶️ Watch", callback_data="watch_video"),
        telebot.types.InlineKeyboardButton("⬇️ Download", callback_data="download_video")
    )
    markup.add(telebot.types.InlineKeyboardButton("🔒 VIP Content", callback_data="vip_only"))
    return markup

# --- Flask Webhook Endpoint ---
@app.route(f"/{API_TOKEN}", methods=['POST'])
def telegram_webhook():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "ok", 200

# --- Set webhook ---
@app.route('/')
def set_webhook():
    webhook_url = f"[https://{os.environ['REPL_SLUG']}.{os.environ['REPL_OWNER']}.repl.co/{API_TOKEN}]https://{os.environ['REPL_SLUG']}.{os.environ['REPL_OWNER']}.repl.co/{API_TOKEN}"
    bot.set_webhook(url=webhook_url)
    return "Webhook set", 200

# --- Run Flask app ---
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
