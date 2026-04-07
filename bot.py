import telebot
import os
import google.generativeai as genai
from telebot import types
import time

# --- လူကြီးမင်းပေးထားသော Key များ ---
API_TOKEN = '8656360830:AAH7V6Hhb1AqIytZdyY984YGnBIDPPfwTfc'
GEMINI_API_KEY = 'AIzaSyB9od09ydz7pVRYzwkB1NduWa6yOT1RFPs'
# ----------------------------------

bot = telebot.TeleBot(API_TOKEN)
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

user_data = {}

@bot.message_handler(commands=['start'])
def start(message):
    user_data[message.chat.id] = {}
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton("🎬 Video to Script", callback_data="mode_video")
    btn2 = types.InlineKeyboardButton("🎙 Text to Voice", callback_data="mode_voice")
    markup.add(btn1, btn2)
    bot.send_message(message.chat.id, "မင်္ဂလာပါ! Movie Recap ဆရာကြီး Bot မှ ကြိုဆိုပါတယ်။\nဘာလုပ်ပေးရမလဲခင်ဗျာ?", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    chat_id = call.message.chat.id
    if call.data == "mode_video":
        markup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton("၁။ အသေးစိတ်ဘာသာပြန် (Detail)", callback_data="script_detail")
        btn2 = types.InlineKeyboardButton("၂။ ကြည့်ရှုသူပြန်ပြောပြပုံ (Narrator)", callback_data="script_viewer")
        btn3 = types.InlineKeyboardButton("၃။ ဇာတ်ကောင်ကိုယ်တိုင်ပြောပုံ (POV)", callback_data="script_character")
        markup.add(btn1, btn2, btn3)
        bot.edit_message_text("ဘယ်လို Script ပုံစံမျိုး ထုတ်ပေးရမလဲခင်ဗျာ?", chat_id, call.message.message_id, reply_markup=markup)

    elif call.data.startswith("script_"):
        user_data[chat_id]['script_type'] = call.data
        bot.send_message(chat_id, "အိုကေ! Recap လုပ်မယ့် Video ဖိုင်ကို ပို့ပေးပါ။ (AI မှ စစ်ဆေးပေးပါမည်)")

    elif call.data == "mode_voice":
        markup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton("ဦးသီဟ (Male)", callback_data="voice_thiha")
        btn2 = types.InlineKeyboardButton("မနီလာ (Female)", callback_data="voice_nila")
        markup.add(btn1, btn2)
        bot.edit_message_text("ဘယ်သူ့အသံနဲ့ ပြောင်းလဲပေးရမလဲ?", chat_id, call.message.message_id, reply_markup=markup)

@bot.message_handler(content_types=['video'])
def handle_video(message):
    chat_id = message.chat.id
    if 'script_type' not in user_data.get(chat_id, {}):
        bot.reply_to(message, "အရင်ဆုံး /start ကိုနှိပ်ပြီး ပုံစံရွေးပေးပါဦး။")
        return

    wait_msg = bot.reply_to(message, "Video ကို AI က ဖတ်နေပါတယ်။ ခဏလေး စောင့်ပေးပါ...")
    
    try:
        file_info = bot.get_file(message.video.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        video_path = f"video_{chat_id}.mp4"
        
        with open(video_path, 'wb') as f:
            f.write(downloaded_file)

        script_type = user_data[chat_id]['script_type']
        
        prompts = {
            "script_detail": "Write a professional Burmese movie recap script. Explain every scene in detail like a movie translator.",
            "script_viewer": "Write a funny and engaging Burmese movie recap. Narrate like you are explaining to a friend.",
            "script_character": "Write a movie recap in Burmese from the first-person perspective (POV) of the main character."
        }
        
        selected_prompt = prompts.get(script_type, prompts["script_detail"])
        video_file = genai.upload_file(path=video_path)
        
        while video_file.state.name == "PROCESSING":
            time.sleep(2)
            video_file = genai.get_file(video_file.name)

        response = model.generate_content([selected_prompt, video_file])
        bot.send_message(chat_id, f"📝 **သင့်အတွက် Script ရပါပြီ:**\n\n{response.text}")
        
        os.remove(video_path)
        genai.delete_file(video_file.name)

    except Exception as e:
        bot.send_message(chat_id, f"Error ဖြစ်သွားပါတယ်- {str(e)}")
    
    bot.delete_message(chat_id, wait_msg.message_id)

bot.infinity_polling()
