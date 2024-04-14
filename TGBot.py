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
    bot.send_message(message.chat.id, 'Привет ✌️ ,  отправь аудио сообщение или видеосообщение в кружке!\nHi ✌️, send me a voice message or video-note!')


@bot.message_handler(commands=['help'])
def help_message(message):
    bot.send_message(message.chat.id, 'Этот бот переводит голосовые сообщения или видео сообщения в кружке в текст\nБот создан в учебных '
                                      'целях\n\nThis bot translates voice messages or video-note into text\nThe bot was created for'
                                      ' educational purposes.')


@bot.message_handler(commands=['model'])


@bot.message_handler(commands=['lang'])
def help_message(message):
    bot.send_message(message.chat.id, 'Бот понимает сообщения на многих языках,\nно пока не на всех\nВыберете язык\nBot can understand many languages\nChoose languages.')

    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.row(
        telebot.types.InlineKeyboardButton('Русский / Russian', callback_data='lang-rus')
    )
    keyboard.row(
        telebot.types.InlineKeyboardButton('Английский / English', callback_data='lang-eng')
    )
    keyboard.row(
        telebot.types.InlineKeyboardButton('Хинди / Hindi', callback_data='lang-hin')
    )
    bot.send_message(
        message.chat.id,
        'Выберите язык / Choose the language:',
        reply_markup=keyboard
    )



@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    # Если сообщение из чата с ботом
    if call.message:
        if call.data == "lang-rus":
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Вы выбрали Русский язык сообщения")
        elif call.data == "lang-eng":
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="You've chose English message language")
        elif call.data == "lang-hin":
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="आपने अंग्रेजी संदेश भाषा चुनी है")
        else:
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Я не знаю такой язык")

@bot.message_handler(
    content_types=['audio', 'photo', 'video', 'document', 'text', 'location', 'contact', 'sticker'])
def exceptions(message):
    bot.send_message(message.from_user.id,
                     "Ничего не понятно, но очень интересно!😳\nПопробуйте команду /help\n\nNothing is clear, "
                     "but it is very interesting!😳 \nTry the /help command😳")


@bot.message_handler(content_types=['voice', 'video_note'])
def get_media_messages(message):
    bot.send_message(message.from_user.id, "Started recognition...")
    try:
        bot.send_message(message.from_user.id, "Continue recognition...")
        file_id = message.voice.file_id if message.content_type == 'voice' else message.video_note.file_id
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
