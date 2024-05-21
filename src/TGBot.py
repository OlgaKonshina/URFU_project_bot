import telebot
import whisper
import os
import requests
import subprocess
import pytz
import yaml
import logging


logging.basicConfig(
    level=logging.INFO,
    filename="logfile.log",
    filemode="w",
    encoding='utf-8',
    format="%(name)s %(asctime)s %(levelname)s %(message)s",
)


try:
    with open(r"src/TGBot_config.yaml", "r") as f:
        config = yaml.safe_load(f)
    logging.info("Конфигурационный файл успешно загружен.")
except Exception as e:
    logging.critical(
        f"Конфигурационный файл не был загружен. Ошибка {e}", exc_info=True
    )


try:
    token = config["token"]
    bot = telebot.TeleBot(token)
    p_timezone = pytz.timezone(config["timezone"])
    timezone_common_name = config["timezone_common_name"]
    logging.info("Конфигурации успешно загружены")
except Exception as e:
    logging.critical(f"Конфигерации не загружены. Ошибка {e}", exc_info=True)


@bot.message_handler(commands=["start"])
def start_message(message):
    try:
        bot.send_message(
            message.chat.id,
            "Привет ✌️ ,  отправь аудио/видео сообщение!\n"
            "Hi ✌️, send me a voice/video message!",
        )
        logging.info("Отправлено приветственное сообщение.")
    except Exception as e:
        logging.error(
            f"Приветственное сообщение не отправлено. Ошибка: {e}",
            exc_info=True
        )


@bot.message_handler(commands=["help"])
def help_message(message):

    try:
        bot.send_message(
            message.chat.id,
            "Этот бот переводит голосовые/видео сообщения в текст\n"
            "Бот создан в учебных целях\n\n"
            "This bot translates voice/video messages into text\n"
            "The bot was created for educational purposes",
        )
        logging.info("Отправлено информационное сообщение")
    except Exception as e:
        logging.error(
            f"Произошла ошибка, инфоонмационное сообщение не отправлено. {e}",
            exc_info=True,
        )


@bot.message_handler(commands=["model"])
@bot.message_handler(commands=["lang"])
def help_message(message):
    try:
        bot.send_message(
            message.chat.id,
            "Бот понимает сообщения на многих языках,\nно пока не на всех\nВыберете язык\nBot can understand many languages\nChoose languages.",
        )

        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.row(
            telebot.types.InlineKeyboardButton(
                "Русский / Russian", callback_data="lang-rus"
            )
        )
        keyboard.row(
            telebot.types.InlineKeyboardButton(
                "Английский / English", callback_data="lang-eng"
            )
        )
        keyboard.row(
            telebot.types.InlineKeyboardButton(
                "Хинди / Hindi", callback_data="lang-hin"
            )
        )
        bot.send_message(
            message.chat.id,
            "Выберите язык / Choose the language:",
            reply_markup=keyboard,
        )
        logging.info("Отправлено информационное сообщение о выборе языка")
    except Exception as e:
        logging.error(
            f"Сообщение о выборе языка не было отправлено. Ошибка {e}", exc_info=True
        )


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    # Если сообщение из чата с ботом
    try:
        if call.message:
            if call.data == "lang-rus":
                bot.edit_message_text(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    text="Вы выбрали Русский язык сообщения",
                )
                logging.info("Выбран язык: русский")
            elif call.data == "lang-eng":
                bot.edit_message_text(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    text="You've chose English message language",
                )
                logging.info("Выбран язык: английский")
            elif call.data == "lang-hin":
                bot.edit_message_text(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    text="आपने अंग्रेजी संदेश भाषा चुनी है",
                )
                logging.info("Выбран язык: хинди")
            else:
                bot.edit_message_text(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    text="Я не знаю такой язык",
                )
                logging.warning("Неизвестный язык")
    except Exception as e:
        logging.error(f"Произошла неизвестная ошибка: {e}", exc_info=True)


@bot.message_handler(
    content_types=[
        "audio",
        "photo",
        "document",
        "text",
        "location",
        "contact",
        "sticker",
    ]
)
def exceptions(message):
    try:
        bot.send_message(
            message.from_user.id,
            "Ничего не понятно, но очень интересно!😳\nПопробуйте команду /help😳\n\n"
            "Nothing is clear, but it is very interesting!😳 \nTry the /help command😳",
        )
        logging.warning("Не удалось что-либо распознать")
    except Exception as e:
        logging.error("Неизвестная ошибка: {e}", exc_info=True)


@bot.message_handler(content_types=["voice", "video", "video_note"])
def get_media_messages(message):
    bot.send_message(message.from_user.id, "Started recognition...")
    try:
        bot.send_message(message.from_user.id, "Continue recognition...")
        logging.info("Отправили сообщение о процессе распознавания")

        if message.content_type == "voice":
            file_id = message.voice.file_id
            logging.info("Распознаём аудио сообщение")
        elif message.content_type == "video_note":
            file_id = message.video_note.file_id
            logging.info("Распознаем видеео сообщение")
        elif message.content_type == "video":
            file_id = message.video.file_id
            logging.info("Распоознаем видео сообщние")
        else:
            bot.send_message(message.from_user.id, "Такой формат я не знаю😳")
            logging.error(
                f"Не удалось распознать сообщение, неверный формат {message.content_type}"
            )
            return

        try:
            file_info = bot.get_file(file_id)
            path = file_info.file_path
            fname = os.path.basename(path)
            doc = requests.get(
                "https://api.telegram.org/file/bot{0}/{1}".format(
                    token, file_info.file_path
                )
            )
            with open(fname, "wb") as f:
                f.write(doc.content)
            logging.info("Файл для распознавания успешно открыт")
        except Exception as e:
            logging.critical(f"Не удалось открыть файл. Ошибка {e}", exc_info=True)

        try:
            subprocess.run(["ffmpeg", "-i", fname, fname[:-4] + ".wav"], check=True)
            logging.info("Конвертация произошла успешно")
        except subprocess.CalledProcessError as e:
            bot.send_message(
                message.from_user.id, "c конвертацией файла что-то пошло не так... 😣"
            )
            os.remove(fname)
            logging.critical(f"Ошибка в конвертации {e}", exc_info=True)
            return

        try:
            model = whisper.load_model("small")
            bot.send_message(message.from_user.id, "Model loaded")
            logging.info("Модель успешно загружена")
        except Exception as e:
            logging.critical(f"Модель не загружена. Ошибка: {e}", exc_info=True)

        try:
            result = model.transcribe(
                fname[:-4] + ".wav", fp16=False
            )  # распознаем аудио и переводим в текст
            logging.info("Распознали аудио и перевели его в текст")
        except Exception as e:
            bot.send_message(
                message.from_user.id, "Что-то пошло не так c распознованием😣"
            )
            os.remove(fname)
            os.remove(fname[:-4] + ".wav")
            logging.critical(
                f"Не удалось перевести аудио в текст. Ошибка: {e}", exc_info=True
            )
            return

        bot.send_message(message.from_user.id, "Finish recognition...")

        if result["text"] == "":
            bot.send_message(message.from_user.id, "Ничего не удалось распознать 😣")
            logging.warning("Не удалось распознаттть текст")
        else:
            bot.send_message(message.from_user.id, result["text"])
            logging.info("Сообщение распознано и переведенов текст")

    except Exception as e:
        bot.send_message(
            message.from_user.id,
            "Что-то пошло не так, но наши смелые инженеры уже трудятся над решением... 😣\n"
            "Something went wrong, but our brave engineers are already working on a solution... 😣",
        )
        logging.critical(f"Скрипт не отработал. Ошибка {e}", exc_info=True)

    finally:
        os.remove(fname)
        os.remove(fname[:-4] + ".wav")
        logging.info("Закончили выполнение скрипта")


bot.polling(none_stop=True, interval=0)
