import os
import telebot
from telebot import types
import time
import google.generativeai as genai

# Render Environment Variables ကနေ Key တွေကို ဖတ်ခြင်း
API_TOKEN = os.environ.get('BOT_TOKEN')
GEMINI_API_KEY = os.environ.get('GOOGLE_API_KEY')

# Bot နှင့် Gemini ကို ချိတ်ဆက်ခြင်း
bot = telebot.TeleBot(API_TOKEN)
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

user_data = {}

@bot.message_handler(commands=['start'])
def start(message):
    user_data[message.chat.id] = {'mode': None}
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton("🎬 Video to Script", callback_data="mode_video")
    btn2 = types.InlineKeyboardButton("🎙️ Text to Voice", callback_data="mode_voice")
    markup.add(btn1, btn2)
    bot.send_message(message.chat.id, "မင်္ဂလာပါ! Movie Recap ဆရာကြီး Bot မှ ကြိုဆိုပါတယ်။ ဘာလုပ်ပေးရမလဲခင်ဗျာ?", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    chat_id = call.message.chat.id
    if call.data == "mode_video":
        user_data[chat_id]['mode'] = 'video'
        bot.answer_callback_query(call.id) # ခလုတ်နှိပ်လိုက်ရင် တုံ့ပြန်မှုပေးရန်
        bot.send_message(chat_id, "🎬 ဗီဒီယိုဖိုင် ပို့ပေးပါ။ ကျွန်တော် Script ရေးပေးပါ့မယ်။")
    elif call.data == "mode_voice":
        user_data[chat_id]['mode'] = 'voice'
        bot.answer_callback_query(call.id)
        bot.send_message(chat_id, "🎙️ စာသားပို့ပေးပါ။ ကျွန်တော် အသံပြောင်းပေးပါ့မယ်။")

@bot.message_handler(content_types=['video'])
def handle_video(message):
    chat_id = message.chat.id
    if chat_id in user_data and user_data[chat_id].get('mode') == 'video':
        processing_msg = bot.send_message(chat_id, "⏳ ဗီဒီယိုကို စစ်ဆေးနေပါတယ်။ ခဏစောင့်ပေးပါ...")
        
        try:
            file_info = bot.get_file(message.video.file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            
            with open("temp_video.mp4", "wb") as f:
                f.write(downloaded_file)
            
            video_file = genai.upload_file(path="temp_video.mp4")
            
            while video_file.state.name == "PROCESSING":
                time.sleep(2)
                video_file = genai.get_file(video_file.name)
            
            prompt = "ဤဗီဒီယိုကို ကြည့်ပြီး မြန်မာလို စိတ်လှုပ်ရှားစရာကောင်းသော Movie Recap script တစ်ခု ရေးပေးပါ။"
            response = model.generate_content([prompt, video_file])
            
            bot.edit_message_text(response.text, chat_id, processing_msg.message_id)
            os.remove("temp_video.mp4")
            
        except Exception as e:
            bot.send_message(chat_id, f"❌ အမှားတစ်ခု ဖြစ်သွားပါတယ်: {str(e)}")

if __name__ == "__main__":
    print("Bot is starting...")
    bot.infinity_polling()
