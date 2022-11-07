import json
import telebot
import re
import requests

from telebot import types

# Объект бота
bot = telebot.TeleBot(token="5688425165:AAHkyGJxmoMejLxzkj7ArReY5GxPZBFvjmk")
name = None


@bot.message_handler(commands=['start'])
def start_message(message):
    mesg = bot.send_message(message.chat.id,
                            "Напишите мне свои фамилию имя и отчество, чтобы мы загрузили информацию по спортзалу и вашим сотрудникам сами")
    bot.register_next_step_handler(mesg, get_text_messages)


@bot.message_handler(commands=['help'])
def help_message(message):
    bot.send_message(message.chat.id, 'текст')


@bot.message_handler(commands=['out'])
def help_message(message):
    bot.send_message(message.chat.id, 'До свидания!')
    #удаление из бд чат id


def get_text_messages(message):
    if bool(re.match('^[А-Я][а-я]+\s+[А-Я][а-я]+\s+[А-Я][а-я]+', message.text)):
        # body = requests.get(ip,endpoint api).json() //отправляем запрос по фамилии, по ФИ, по Фамилии И.О.?
        with open("responsible_true.json", "r") as read_file:  # заменить на requests?
            data = json.loads(read_file.read())
            if data['result'] is None or data['result']['full_name'] != message.text:
                reply = types.InlineKeyboardMarkup()
                trymore = types.InlineKeyboardButton(text='Попробую ещё раз', callback_data='trymore')
                nottry = types.InlineKeyboardButton(text='Я уверен в правильности введенных данных',
                                                    callback_data='nottry')
                reply.add(trymore, nottry)
                bot.send_message(message.chat.id,
                                 "Вашего имени нет в базе данных, может, вы что-то не так ввели",
                                 reply_markup=reply)
            else:
                bot.send_message(message.chat.id, "Здравствуйте, " + data['result']['full_name'] +
                                 '. У вас снизу кнопка, открывающая окно с сотрудниками и их статусом занятий',
                                 reply_markup=webAppKeyboard())

    else:
        mesg = bot.send_message(message.chat.id, "Введите ещё раз в формате \"Фамилия Имя Отчество\"")
        bot.register_next_step_handler(mesg, get_text_messages)


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.data == 'trymore':
        mesg = bot.send_message(call.message.chat.id, "Введите ещё раз в формате \"Фамилия Имя Отчество\"")
        bot.register_next_step_handler(mesg, get_text_messages)
    elif call.data == 'nottry':
        bot.send_message(call.message.chat.id, 'Напишите разработчикам, чтобы вас добавили в базу данных')


def webAppKeyboard():  # создание клавиатуры с webapp кнопкой
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)  # создаем клавиатуру
    webAppTest = types.WebAppInfo(
        "https://famous-tarsier-114ae1.netlify.app/")  # создаем webappinfo - формат хранения url
    one_butt = types.KeyboardButton(text="Список сотрудников", web_app=webAppTest)  # создаем кнопку типа webapp
    keyboard.add(one_butt)  # добавляем кнопки в клавиатуру

    return keyboard  # возвращаем клавиатуру


bot.polling()
