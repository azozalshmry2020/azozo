import requests
from telebot import TeleBot, types
import os
import yt_dlp

# Replace 'YOUR_TELEGRAM_BOT_TOKEN' with your actual bot token
bot_token = "6361320030:AAEFHZcizbWEdOClbBQIfcSsTLOPe2l_NVU"
bot = TeleBot(bot_token)

# Define the download buttons
sh_btn = types.InlineKeyboardButton(text='تحميل', callback_data='s1')
yt_btn = types.InlineKeyboardButton(text='تحميل من يوتيوب', callback_data='s2')

# Handle /start command
@bot.message_handler(commands=["start"])
def start(message):
    b = types.InlineKeyboardMarkup()
    b.row_width = 2
    b.add(sh_btn, yt_btn)

    bot.send_message(message.chat.id, f"""
    *مرحبًا بك {message.from_user.first_name} في بوت تحميل من تيك توك وإنستاجرام ويوتيوب. يقوم البوت بتحميل فيديو وصوت 💿*
    """, parse_mode='markdown', reply_markup=b)

# Handle callback queries
@bot.callback_query_handler(func=lambda call: True)
def sh(call):
    if call.data == 's1':
        msg = bot.send_message(call.message.chat.id, '- ارسل الرابط!')
        bot.register_next_step_handler(msg, process_url)
    elif call.data == 's2':
        msg = bot.send_message(call.message.chat.id, '- ارسل رابط الفيديو من يوتيوب!')
        bot.register_next_step_handler(msg, process_youtube_url)

# Handle URL messages for Instagram and TikTok
def process_url(message):
    bot.send_message(message.chat.id, "<strong>جاري التحميل، انتظر قليلا ...</strong>", parse_mode="html")
    msg = message.text

    if 'instagram.com/reel/' in msg or 'instagram.com/p/' in msg:
        download_instagram_content(msg, message.chat.id)
    elif 'tiktok.com' in msg:
        download_tiktok_content(msg, message.chat.id)
    else:
        bot.send_message(message.chat.id, "الرابط غير مدعوم. يرجى إرسال رابط تيك توك أو إنستاجرام.")

# Handle URL messages for YouTube
def process_youtube_url(message):
    bot.send_message(message.chat.id, "<strong>جاري التحميل، انتظر قليلا ...</strong>", parse_mode="html")
    url = message.text

    if 'youtube.com/watch' in url or 'youtu.be/' in url:
        download_youtube_content(url, message.chat.id)
    else:
        bot.send_message(message.chat.id, "الرابط غير مدعوم. يرجى إرسال رابط من يوتيوب.")

def download_instagram_content(url, chat_id):
    try:
        api_url = f'https://abarmizban.com/downloader/test.php?url={url}'
        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json()

        video_url = data.get('video', {}).get('medias', [{}])[0].get('url')
        if not video_url:
            raise ValueError("مفتاح 'url' غير موجود في استجابة API")

        video_data = requests.get(video_url).content
        video_path = f"instagram_video_{chat_id}.mp4"

        with open(video_path, "wb") as video_file:
            video_file.write(video_data)

        with open(video_path, "rb") as video:
            bot.send_video(chat_id, video, caption="📹 تم تحميل فيديو إنستاجرام")

        os.remove(video_path)

    except requests.RequestException as e:
        bot.send_message(chat_id, f"حدث خطأ أثناء الاتصال بـ API: {e}")
    except ValueError as e:
        bot.send_message(chat_id, f"خطأ في بيانات استجابة API: {e}")
    except Exception as e:
        bot.send_message(chat_id, f"حدث خطأ أثناء التنزيل من إنستاجرام: {e}")

def download_tiktok_content(url, chat_id):
    try:
        response = requests.get(f'https://www.tikwm.com/api?url={url}&hd=1')
        response.raise_for_status()
        data = response.json()

        hdplay_url = data['data']['hdplay']
        wmplay_url = data['data']['wmplay']

        video_data = requests.get(hdplay_url).content
        audio_data = requests.get(wmplay_url).content

        video_path = f"tiktok_video_{chat_id}.mp4"
        audio_path = f"tiktok_audio_{chat_id}.mp3"

        with open(video_path, "wb") as video_file:
            video_file.write(video_data)
        with open(audio_path, "wb") as audio_file:
            audio_file.write(audio_data)

        with open(video_path, "rb") as video:
            bot.send_video(chat_id, video, caption="📹 تم تحميل فيديو تيك توك")
        with open(audio_path, "rb") as audio:
            bot.send_audio(chat_id, audio, caption="🔊 تم تحميل الصوت")

        os.remove(video_path)
        os.remove(audio_path)

    except Exception as e:
        bot.send_message(chat_id, f"حدث خطأ أثناء التنزيل من تيك توك: {e}")

def download_youtube_content(url, chat_id):
    try:
        ydl_opts = {
            'format': 'best',
            'outtmpl': f'youtube_video_{chat_id}.%(ext)s',
            'noplaylist': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            video_path = ydl.prepare_filename(info_dict)

        with open(video_path, "rb") as video:
            bot.send_video(chat_id, video, caption="📹 تم تحميل فيديو يوتيوب")

        os.remove(video_path)

    except Exception as e:
        bot.send_message(chat_id, f"حدث خطأ أثناء التنزيل من يوتيوب: {e}")

print('البوت يعمل الآن...')
bot.infinity_polling()
