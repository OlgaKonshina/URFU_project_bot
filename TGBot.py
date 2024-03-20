import telebot;
#from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
import TGBot_config as config
import pytz
#from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton #Инлайн кнопки

bot = telebot.TeleBot(config.token);
p_timezone = pytz.timezone(config.timezone)
timezone_common_name = config.timezone_common_name


@bot.message_handler(commands=['help'])
def help_command(message):
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.add(
        telebot.types.InlineKeyboardButton(
            'Message the developer', url='telegram.me/DS_Shabanov'
  )
    )
    bot.send_message(
        message.chat.id,
        '1) To receive a list of available currencies press /exchange.\n' +
        '2) Click on the currency you are interested in.\n' +
        '3) You will receive a message containing information regarding the source and the target currencies, ' +
        'buying rates and selling rates.\n' +
        '4) Click “Update” to receive the current information regarding the request. ' +
        'The bot will also show the difference between the previous and the current exchange rates.\n' +
        '5) The bot supports inline. Type @<botusername> in any chat and the first letters of a currency.',
        reply_markup=keyboard
    )

#Инлайн кнопки
#InlineKeyboardMarkup пригодится для инициализации инлайн-кнопок, а InlineKeyboardButton — для их создания.

@bot.message_handler(commands=['start'])
def start_command(message):
    bot.send_message(message.from_user.id,
                     "Это Бот - помощник по математике. Используй команды, чтобы получить нужную помощь.")
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.row(
        telebot.types.InlineKeyboardButton('Таблица умножения', callback_data='get-table')
    )
    keyboard.row(
        telebot.types.InlineKeyboardButton('Решение уравнений', callback_data='get-equals')
    )
    bot.send_message(
        message.chat.id,
        'Выберете что вам нужно:',
        reply_markup=keyboard
    )

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    # Если сообщение из чата с ботом
    if call.message:
        if call.data == "get-table":
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Посчитаем произведение 2-х чисел")
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text="Введите 1-й множитель:")

            bot.register_next_step_handler(call.message, table_multiply_num1)

            # bot.send_message(chat_id=call.message.chat.id, text="Введите первый множитель:")
            # a1 = int(call.message.text)
            # bot.send_message(chat_id=call.message.chat.id, text="Введите второй множитель:")
            # a2 = int(call.message.text)
            # a3 = str('Произведение чисел: ', a1, ' * ', a2, ' = ', a1 * a2)
            # bot.send_message(chat_id=call.message.chat.id, text = a3 )
    # Если сообщение из инлайн-режима
    #elif call.inline_message_id:
        if call.data == "get-equals":
            bot.edit_message_text(inline_message_id=call.inline_message_id, text="Решим уравнение")

@bot.message_handler(content_types=['text'])
def table_multiply_num1 (message):
    global num1
    num1 = message.text
    bot.send_message(chat_id=message.chat.id, text="Введите 2-й множитель:")
    bot.register_next_step_handler(message, table_multiply_num2)

def table_multiply_num2(message):
    global num2
    num2 = message.text
    num_multiply = float(num1) * float(num2)
    num_multiply_str = 'Произведение этих чисел = ' + str(num_multiply)
    bot.send_message(chat_id=message.chat.id, text=num_multiply_str)






# def iq_callback(query):
#     data = query.data
#     #print(data.startswith)
#     if data.startswith('get-table'):
#         print(data.startswith('get-table'))
#         #get_menu_callback(query)
#
#         query.answer()
#         query.edit_message_text(text="See you next time!")


# @bot.message_handler(content_types=['text'])
# def table_pifagore(message):
#     print('Таблица Пифагора')
#     #bot.send_message(message.from_user.id, "Введите первый множитель:")
#     bot.send_message(chat_id=message.from_user.id, text='USP-Python has started up!')
#


# def get_menu_callback(query):
#     bot.answer_callback_query(query.id)
#     bot.send_message(query.message, 'Получили - ')
#     #send_exchange_result(query.message, query.data[4:])
#
# def send_result(message):
#     bot.send_message(message.chat.id, 'Получили - ')

# def get_ex_callback(query):
#     bot.answer_callback_query(query.id)
#     send_exchange_result(query.message, query.data[4:])

# def send_exchange_result(message, ex_code):
#     bot.send_chat_action(message.chat.id, 'typing')
#     ex = pb.get_exchange(ex_code)
#     bot.send_message(
#         message.chat.id, serialize_ex(ex),
#         reply_markup=get_update_keyboard(ex),
# 	parse_mode='HTML'
#     )


#
# name = ''
# surname = ''
# age = 0
# @bot.message_handler(content_types=['text'])
# def start(message):
#     if message.text == '/reg':
#         bot.send_message(message.from_user.id, "Как тебя зовут?")
#         bot.register_next_step_handler(message, get_name) #следующий шаг – функция get_name
#     else:
#         bot.send_message(message.from_user.id, 'Напиши /reg')
#
# def get_name(message): #получаем фамилию
#     global name
#     name = message.text
#     bot.send_message(message.from_user.id, 'Какая у тебя фамилия?')
#     bot.register_next_step_handler(message, get_surname)
#
# def get_surname(message):
#     global surname
#     surname = message.text
#     bot.send_message(message.from_user.id, 'Сколько тебе лет?')
#     bot.register_next_step_handler(message, get_age)
#
# def get_age(message):
#     global age
#     while age == 0: #проверяем что возраст изменился
#         try:
#              age = int(message.text) #проверяем, что возраст введен корректно
#         except Exception:
#              bot.send_message(message.from_user.id, 'Цифрами, пожалуйста')
#     bot.send_message(message.from_user.id, 'Тебе '+str(age)+' лет, тебя зовут '+name+' '+surname+'?')




bot.polling(none_stop=True, interval=2)

