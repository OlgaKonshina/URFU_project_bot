import telebot
import whisper
import os
import requests
import subprocess
import TGBot_config as config
import pytz

bot = telebot.TeleBot(config.token);
p_timezone = pytz.timezone(config.timezone)
timezone_common_name = config.timezone_common_name


@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, 'Привет ✌️ ,  отправь аудио сообщение!')


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
        doc = requests.get('https://api.telegram.org/file/bot{0}/{1}'.format(config.token,
                                                                             file_info.file_path))  # Получаем и сохраняем присланную голосвуху
        with open(fname + '.oga', 'wb') as f:
            f.write(doc.content)  # вот именно тут и сохраняется сама аудио-мессага
        subprocess.run(['ffmpeg', '-i', fname + '.oga', fname + '.wav'])
        model = whisper.load_model('small')
        # print('model = ', model)
        bot.send_message(message.from_user.id, 'Загрузили модель')
        result = model.transcribe(fname + '.wav', fp16=False)  # добавляем аудио для обработки
        # print(result('text'))
        bot.send_message(message.from_user.id, "Finish recognition...")
        bot.send_message(message.from_user.id, result['text'])
    except Exception as e:
        bot.send_message(message.from_user.id,
                         "Что-то пошло не так, но наши смелые инженеры уже трудятся над решением... \nДа ладно, никто эту ошибку исправлять не будет, она просто потеряется в логах.")
    finally:
        os.remove(fname + '.oga')
        os.remove(fname + '.wav')


@bot.message_handler(commands=['help'])
def help_command(message):
    bot.send_message(message.from_user.id, "Это модель распознования голосовых сообщений")



bot.polling(none_stop=True, interval=0)

