import os
import telebot
from flask import Flask, request
from io import BytesIO
import requests

# --- Configuration ---
API_TOKEN = os.environ['API_TOKEN']
ADMIN_ID = 7984779406  # Your Telegram user ID

bot = telebot.TeleBot(API_TOKEN)
app = Flask(__name__)

# Dictionary to store video file IDs (in-memory)
video_storage = {}

# --- Start Handler ---
@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.send_message(message.chat.id, "Welcome! Send me a video to store.")

# --- Video Handler to Store Video File ID ---
@bot.message_handler(content_types=['video'])
def handle_video(message):
    file_id = message.video.file_id
    video_storage[message.chat.id] = file_id
    bot.send_message(message.chat.id, "Video stored successfully!")

# --- Command to Add Buttons with Thumbnail ---
@bot.message_handler(commands=['addbuttons'])
def handle_addbuttons(message):
    if message.reply_to_message and message.reply_to_message.video:
        video_file_id = video_storage.get(message.chat.id)
        
        # Fetch thumbnail from video or use a static image if needed
        # For simplicity, using a static thumbnail
        thumbnail = "https://path.to/your/thumbnail.jpg"  # Replace with your image
        
        # Send Thumbnail with Buttons
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(
            telebot.types.InlineKeyboardButton("▶️ Watch", callback_data="watch_video")
        )
        bot.send_photo(message.chat.id, thumbnail, "Click to watch the video.", reply_markup=markup)
    else:
        bot.reply_to(message, "Please reply to a video with /addbuttons.")

# --- Callback Query Handler ---
@bot.callback_query_handler(func=lambda call: call.data == "watch_video")
def handle_video_callback(call):
    user = call.from_user
    chat_id = call.message.chat.id

    # Retrieve video by file ID from stored videos
    video_file_id = video_storage.get(chat_id)
    
    if video_file_id:
        bot.send_video(call.message.chat.id, video_file_id)
        bot.answer_callback_query(call.id, "Enjoy the video!")
        
        # Log activity to admin
        log = f"User @{user.username or 'NoUsername'} (ID: {user.id}) watched the video."
        bot.send_message(ADMIN_ID, log)
    else:
        bot.answer_callback_query(call.id, "No video available.")

# --- Flask Webhook Endpoint ---
@app.route(f"/{API_TOKEN}", methods=['POST'])
def telegram_webhook():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "ok", 200

# --- Set Webhook on Root ---
@app.route('/')
def set_webhook():
    webhook_url = f"https://yourdomain.com/{API_TOKEN}"  # Replace with your actual domain
    bot.set_webhook(url=webhook_url)
    return "Webhook set", 200

# --- Run ---
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
