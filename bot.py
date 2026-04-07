import os
import telebot
from telebot import types
import time
import google.generativeai as genai

# Render Environment Variables
API_TOKEN = os.environ.get('BOT_TOKEN')
GEMINI_API_KEY = os.environ.get('GOOGLE_API_KEY')

# Initialize Bot and Gemini
bot = telebot.TeleBot(API_TOKEN)
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# ---------------------------------------------------------
# ဒီအောက်ကနေစပြီး လူကြီးမင်းရဲ့ မူလ Bot Code တွေကို ဆက်ထားပေးပါ
# ---------------------------------------------------------

user_data = {}

@bot.message_handler(commands=['start'])
def start(message):
    user_data[message.chat.id] = {}
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton("🎬 Video to Script", callback_data="mode_video")
    btn2 = types.InlineKeyboardButton("🎙️ Text to Voice", callback_data="mode_voice")
    markup.add(btn1, btn2)
    bot.send_message(message.chat.id, "မင်္ဂလာပါ! Movie Recap ဆရာကြီး Bot မှ ကြိုဆိုပါတယ်။", reply_markup=markup)

# ... ကျန်ရှိသော Code များ ...

if __name__ == "__main__":
    print("Bot is starting...")
    bot.infinity_polling()
