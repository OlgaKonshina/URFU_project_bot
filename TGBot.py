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
    bot.send_message(message.chat.id, 'Привет ✌️ ,  отправь аудио сообщение!\nHi ✌️, send me a voice message!')


@bot.message_handler(commands=['help'])
def help_message(message):
    bot.send_message(message.chat.id, 'Этот бот переводит голосовые сообщения в текст\nБот создан в учебных '
                                      'целях\n\nThis bot translates voice messages into text\nThe bot was created for'
                                      ' educational purposes.')


@bot.message_handler(
    content_types=['audio', 'photo', 'video', 'document', 'text', 'location', 'contact', 'sticker'])
def exceptions(message):
    bot.send_message(message.from_user.id,
                     "Ничего не понятно, но очень интересно!😳\nПопробуйте команду /help\n\nNothing is clear, "
                     "but it is very interesting!😳 \nTry the /help command😳")


@bot.message_handler(content_types=['voice'])
def get_audio_messages(message):
    bot.send_message(message.from_user.id, "Started recognition...")
    # Основная функция, принимает голосовое сообщение от пользователя
    try:
        bot.send_message(message.from_user.id, "Continue recognition...")
        # Ниже пытаемся вычленить имя файла, да и вообще берем данные с мессаги
        file_info = bot.get_file(message.voice.file_id)
        print('file_info = ', file_info)
        path = file_info.file_path  # Вот тут-то и полный путь до файла (например: voice/file_2.oga)
        fname = os.path.basename(path)  # Преобразуем путь в имя файла (например: file_2.oga)
        # print(fname)
        doc = requests.get('https://api.telegram.org/file/bot{0}/{1}'.format(token,
                                                                             file_info.file_path)) # Получаем и сохраняем
        with open(fname + '.oga', 'wb') as f:
            f.write(doc.content)  # вот именно тут и сохраняется само аудио
        subprocess.run(['ffmpeg', '-i', fname + '.oga', fname + '.wav'])
        model = whisper.load_model('small')
        # print('model = ', model)
        bot.send_message(message.from_user.id, 'Загрузили модель\nLoaded the model')
        result = model.transcribe(fname + '.wav', fp16=False)  # добавляем аудио для обработки
        # print(result('text'))
        bot.send_message(message.from_user.id, "Finish recognition...")
        bot.send_message(message.from_user.id, result['text'])
    except Exception as e:
        bot.send_message(message.from_user.id,
                         "Что-то пошло не так, но наши смелые инженеры уже трудятся над решением... 😣  \nSomething "
                         "went wrong, but our brave engineers are already working on a solution... 😣")
    finally:
        os.remove(fname + '.oga')
        os.remove(fname + '.wav')
        pass


@bot.message_handler(content_types=['video_note'])
def get_video_messages(message):
    bot.send_message(message.from_user.id, "Started recognition...")
    # Основная функция, принимает голосовое сообщение от пользователя
    try:
        bot.send_message(message.from_user.id, "Continue recognition...")
        # Ниже пытаемся вычленить имя файла, да и вообще берем данные с мессаги
        file_info = bot.get_file(message.video_note.file_id)
        print('file_info = ', file_info)
        path = file_info.file_path  # Вот тут-то и полный путь до файла (например: voice/file_2.oga)
        fname = os.path.basename(path)  # Преобразуем путь в имя файла (например: file_2.oga)
        # print(fname)
        doc = requests.get('https://api.telegram.org/file/bot{0}/{1}'.format(token,
                                                                             file_info.file_path))  # Получаем и сохраняем присланную голосвуху
        with open(fname, 'wb') as f:
            f.write(doc.content)  # вот именно тут и сохраняется сама аудио-мессага
        subprocess.run(['ffmpeg', '-i', fname, fname[:-4] + '.wav'])

        model = whisper.load_model('small')
        print('model = ', model)
        bot.send_message(message.from_user.id, 'Загрузили модель\nLoaded the model')

        result = model.transcribe(fname[:-4] + '.wav', fp16=False)  # добавляем аудио для обработки
        print(result['text'])
        bot.send_message(message.from_user.id, "Finish recognition...")
        (bot.send_message(message.from_user.id, result['text']))

    except Exception as e:
        bot.send_message(message.from_user.id,
                         "Что-то пошло не так, но наши смелые инженеры уже трудятся над решением... 😣 \nSomething "
                         "went wrong, but our brave engineers are already working on a solution... 😣")
    finally:
        os.remove(fname)
        os.remove(fname[:-4] + '.wav')
        pass


bot.polling(none_stop=True, interval=0)
