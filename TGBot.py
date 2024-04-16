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

    bot.send_message(message.chat.id, 'Привет ✌️ ,  отправь аудио/видео сообщение!\n'
                                      'Hi ✌️, send me a voice/video message!')
#для сбора обратной связи
users = {}
administrators = (1088564774,)

#функция сбора обратной связи
@bot.message_handler(commands=['feedback'])
def feedback_message(message):
    chat_id = message.chat.id
    keyboard = telebot.types.ReplyKeyboardMarkup()
    button_save = telebot.types.InlineKeyboardButton(
        text="Написать в поддержку")
    keyboard.add(button_save)
    bot.send_message(chat_id,
                     'Здесь вы можете поделиться обратной связью',
                     reply_markup=keyboard)
    with open('feedback.jpg', 'rb') as file:
        photo = file.read()
    bot.send_photo(chat_id, photo)

#кнопка или вызов команды текстом
@bot.message_handler(
    func=lambda message: message.text == 'Написать в поддержку')
def write_to_support(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, 'Введите своё имя')
    users[chat_id] = {}
    bot.register_next_step_handler(message, save_username)

#сбор данных
def save_username(message):
    chat_id = message.chat.id
    name = message.text
    users[chat_id]['name'] = name
    bot.send_message(chat_id, f'Отлично, {name}. Теперь укажи свою фамилию')
    bot.register_next_step_handler(message, save_surname)

#функция сохранения/изменения данных пользователя
def save_surname(message):
    chat_id = message.chat.id
    surname = message.text
    users[chat_id]['surname'] = surname
    keyboard = telebot.types.InlineKeyboardMarkup()
    button_save = telebot.types.InlineKeyboardButton(text="Сохранить",
                                                     callback_data='save_data')
    button_change = telebot.types.InlineKeyboardButton(text="Изменить",
                                                       callback_data='change_data')
    keyboard.add(button_save, button_change)

    bot.send_message(chat_id, f'Сохранить данные?', reply_markup=keyboard)

#функция проверки данных пользователя
@bot.message_handler(commands=['who_i'])
def who_i(message):
    chat_id = message.chat.id
    name = users[chat_id]['name']
    surname = users[chat_id]['surname']
    bot.send_message(chat_id, f'Вы: {name} {surname}')

#функция сбора текста
@bot.callback_query_handler(func=lambda call: call.data == 'save_data')
def save_btn(call):
    message = call.message
    chat_id = message.chat.id
    message_id = message.message_id
    bot.answer_callback_query(call.id, text="Данные сохранены")
    bot.delete_message(chat_id=chat_id, message_id=message_id)
    bot.send_message(chat_id, 'Введите текст отзыва: ')
    bot.register_next_step_handler(message, send_feedback_administrators)

#функция отправки сообщения админу
def send_feedback_administrators(message):
    feedback = message.text
    user = users[message.chat.id]
    name = user['name']
    surname = user['surname']
    for admin_chat_id in administrators:
        bot.send_message(admin_chat_id,
                         f'{surname} {name} оставил отзыв: {feedback}')


@bot.callback_query_handler(func=lambda call: call.data == 'change_data')
def save_btn(call):
    message = call.message
    chat_id = message.chat.id
    message_id = message.message_id
    bot.edit_message_text(chat_id=chat_id, message_id=message_id,
                          text='Изменение данных!')
    write_to_support(message)


@bot.message_handler(commands=['help'])
def help_message(message):

    bot.send_message(message.chat.id, 'Этот бот переводит голосовые/видео сообщения в текст\n'
                                      'Бот создан в учебных целях\n\n'
                                      'This bot translates voice/video messages into text\n'
                                      'The bot was created for educational purposes')


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

    content_types=['audio', 'photo', 'document', 'text', 'location', 'contact', 'sticker'])
def exceptions(message):
    bot.send_message(message.from_user.id,
                     "Ничего не понятно, но очень интересно!😳\nПопробуйте команду /help😳\n\n"
                     "Nothing is clear, but it is very interesting!😳 \nTry the /help command😳")


@bot.message_handler(content_types=['voice', 'video', 'video_note'])


def get_media_messages(message):
    bot.send_message(message.from_user.id, "Started recognition...")
    try:
        bot.send_message(message.from_user.id, "Continue recognition...")

        if message.content_type == 'voice':
            file_id = message.voice.file_id
        elif message.content_type == 'video_note':
            file_id = message.video_note.file_id
        elif message.content_type == 'video':
            file_id = message.video.file_id
        else:
            bot.send_message(message.from_user.id, 'Такой формат я не знаю😳')
            return


        file_info = bot.get_file(file_id)
        path = file_info.file_path
        fname = os.path.basename(path)
        doc = requests.get('https://api.telegram.org/file/bot{0}/{1}'.format(token, file_info.file_path))
        with open(fname, 'wb') as f:
            f.write(doc.content)


        try:
            subprocess.run(['ffmpeg', '-i', fname, fname[:-4] + '.wav'], check=True)
        except subprocess.CalledProcessError as e:
            bot.send_message(message.from_user.id,
                             "c конвертацией файла что-то пошло не так... 😣")
            os.remove(fname)
            return


        model = whisper.load_model('small')
        bot.send_message(message.from_user.id, 'Model loaded')

        try:
            result = model.transcribe(fname[:-4] + '.wav', fp16=False)  # распознаем аудио и переводим в текст
        except Exception as e:
           bot.send_message(message.from_user.id,"Что-то пошло не так c распознованием😣")
           os.remove(fname)
           os.remove(fname[:-4] + '.wav')
           return

        bot.send_message(message.from_user.id, "Finish recognition...")

        if result['text'] == '':
            bot.send_message(message.from_user.id,"Ничего не удалось распознать 😣")
        else:
            bot.send_message(message.from_user.id, result['text'])

    except Exception as e:
        bot.send_message(message.from_user.id,
                         "Что-то пошло не так, но наши смелые инженеры уже трудятся над решением... 😣  \n"
                         "Something went wrong, but our brave engineers are already working on a solution... 😣")

    finally:
        os.remove(fname)
        os.remove(fname[:-4] + '.wav')


bot.polling(none_stop=True, interval=0)
