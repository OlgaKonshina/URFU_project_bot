import telebot
import whisper
import os
import requests
import subprocess
import pytz
import yaml

with open(r'TGBot_config.yaml', 'r') as f:
    config = yaml.safe_load(f)

token = config['token']
bot = telebot.TeleBot(token)
p_timezone = pytz.timezone(config['timezone'])
timezone_common_name = config['timezone_common_name']


@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, 'Привет ✌️ ,  отправь аудио сообщение или видеосообщение в кружке или видео!\nHi ✌️, send me a voice message or video-note or video!')


@bot.message_handler(commands=['help'])
def help_message(message):
    bot.send_message(message.chat.id, 'Этот бот переводит голосовые сообщения или видео сообщения в кружке или видео в текст\nБот создан в учебных '
                                      'целях\n\nThis bot translates voice messages or video-note or video into text\nThe bot was created for'
                                      ' educational purposes.')


@bot.message_handler(
    content_types=['audio', 'photo', 'document', 'text', 'location', 'contact', 'sticker'])
def exceptions(message):
    bot.send_message(message.from_user.id,
                     "Ничего не понятно, но очень интересно!😳\nПопробуйте команду /help\n\nNothing is clear, "
                     "but it is very interesting!😳 \nTry the /help command😳")


@bot.message_handler(content_types=['voice', 'video_note','video'])
def get_media_messages(message):
    bot.send_message(message.from_user.id, "Started recognition...")
    try:
        bot.send_message(message.from_user.id, "Continue recognition...")
        file_id = ()
        if message.content_type == 'voice':
            file_id = (message.voice.file_id)
        elif message.content_type == 'video':
            file_id = (message.video.file_id)
        else:
            file_id =(message.video_note.file_id)
        file_info = bot.get_file(file_id)
        path = file_info.file_path
        fname = os.path.basename(path)
        doc = requests.get('https://api.telegram.org/file/bot{0}/{1}'.format(token, file_info.file_path))
        with open(fname, 'wb') as f:
            f.write(doc.content)
        subprocess.run(['ffmpeg', '-i', fname, fname[:-4] + '.wav'])

        model = whisper.load_model('small')
        bot.send_message(message.from_user.id, 'Model loaded')

        result = model.transcribe(fname[:-4] + '.wav', fp16=False)
        bot.send_message(message.from_user.id, "Finish recognition...")
        bot.send_message(message.from_user.id, result['text'])
    except Exception as e:
        bot.send_message(message.from_user.id,
                         "Something went wrong, but our brave engineers are already working on a solution...")
    finally:
        os.remove(fname)
        os.remove(fname[:-4] + '.wav')


bot.polling(none_stop=True, interval=0)
