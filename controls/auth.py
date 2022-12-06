import json
import shutil
import threading
import telebot
import re
import requests
from telebot import types
import urllib3

# Объект бота
bot = telebot.TeleBot(token="5688425165:AAHkyGJxmoMejLxzkj7ArReY5GxPZBFvjmk")
bot2 = telebot.TeleBot(token="5669270484:AAFfvWZN14zRdKKiMohMfzVZmfWGPFyqu4o")
name = None
all_chat_id = []
server_url = 'https://c0b2-2a09-5302-ffff-00-1ce6.eu.ngrok.io/'

@bot.message_handler(commands=['start'])
def start_message(message):
    mesg = bot.send_message(message.chat.id,
                            "Напишите мне свои фамилию имя и отчество, чтобы мы загрузили информацию по спортзалу и вашим сотрудникам сами")
    bot.register_next_step_handler(mesg, get_text_messages)


@bot2.message_handler(commands=['start'])
def start_message(message):
    bot2.send_message(message.chat.id, "Здравствуйте! Этот бот для администратора, и для вас доступны всего два "
                                       "действия: получить отчёт за этот месяц и напомнить всем про спортзал")
    admin_menu(message)


@bot2.message_handler()
def no_text(message):
    if message.text == 'Получить отчёт':
        get_report(message)
    elif message.text == 'Напомнить про спортзал':
        remind(message)
    else:
        bot2.send_message(message.chat.id, 'dunno')


# def get_report(message):
#     with open("отчёт.xlsx", "rb") as report:
#         file = report.read()
#     bot2.send_document(message.chat.id, file, visible_file_name='отчёт.xlsx')


def get_report(message):
    report = requests.get(server_url + 'get_report').content
    bot2.send_document(message.chat.id, report, visible_file_name='отчёт.xlsx')


def remind(message):
    global all_chat_id
    for id in all_chat_id:
        bot.send_message(id[0], 'Напоминаем, что необходимо проверить списки сотрудников, посещающих спортзал')


@bot.message_handler(commands=['help'])
def help_message(message):
    bot.send_message(message.chat.id, 'текст')


@bot.message_handler(commands=['out'])
def help_message(message):
    bot.send_message(message.chat.id, 'До свидания!')
    #удаление из бд чат id


# def get_text_messages2(message):
#     if bool(re.match('^[А-Я][а-я]+\s+[А-Я][а-я]+\s+[А-Я][а-я]+', message.text)):
#         # body = requests.get(ip,endpoint api).json() //отправляем запрос по фамилии, по ФИ, по Фамилии И.О.?
#         with open("responsible_true.json", "r") as read_file:  # заменить на requests?
#             data = json.loads(read_file.read())
#             if data['result'] is None or data['result']['full_name'] != message.text:
#                 reply = types.InlineKeyboardMarkup()
#                 trymore = types.InlineKeyboardButton(text='Попробую ещё раз', callback_data='trymore')
#                 nottry = types.InlineKeyboardButton(text='Я уверен в правильности введенных данных',
#                                                     callback_data='nottry')
#                 reply.add(trymore, nottry)
#                 bot.send_message(message.chat.id,
#                                  "Вашего имени нет в базе данных, может, вы что-то не так ввели",
#                                  reply_markup=reply)
#             else:
#                 bot.send_message(message.chat.id, "Здравствуйте, " + data['result']['full_name'] +
#                                  '. У вас снизу кнопка, открывающая окно с сотрудниками и их статусом занятий',
#                                  reply_markup=web_app_keyboard())
#
#     else:
#         mesg = bot.send_message(message.chat.id, "Введите ещё раз в формате \"Фамилия Имя Отчество\"")
#         bot.register_next_step_handler(mesg, get_text_messages)

def get_text_messages(message):
    if bool(re.match('^[А-Я][а-я]+\s+[А-Я][а-я]+\s+[А-Я][а-я]+', message.text)):
        data = get_proper_user_json(message.text)
        if data is None:
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
                                 reply_markup=web_app_keyboard(data))
            global all_chat_id
            all_chat_id.append([message.chat.id, data])
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

#TODO
def web_app_keyboard(file):  # создание клавиатуры с webapp кнопкой
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)  # создаем клавиатуру
    webAppTest = types.WebAppInfo(
        "https://famous-tarsier-114ae1.netlify.app/?id=" + get_user_departament(file))  # создаем webappinfo - формат хранения url
    one_butt = types.KeyboardButton(text="Список сотрудников", web_app=webAppTest)  # создаем кнопку типа webapp
    keyboard.add(one_butt)  # добавляем кнопки в клавиатуру

    return keyboard  # возвращаем клавиатуру


def admin_menu(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.InlineKeyboardButton('Получить отчёт')
    item2 = types.InlineKeyboardButton('Напомнить про спортзал')
    markup.add(item1)
    markup.add(item2)
    bot2.send_message(message.chat.id, 'Теперь у вас есть панель с опциями', reply_markup=markup)


def get_user_departament(user_json):
    return str(user_json['result']['responsible_for_the_department_id'])


def get_proper_user_json(username):
    json_list = [get_user_json(username)]
    split = username.split(' ')
    json_list.append(get_user_json(split[0]))
    json_list.append(get_user_json(split[0]+' ' + split[1][0] + ' ' + split[2][0]))
    json_list.append(get_user_json(split[0]+' ' + split[1][0] + '. ' + split[2][0] + '.'))
    for t in json_list:
        if t['result'] is not None:
            print(t)
            return t
    return None


def get_user_json(username):
    data = requests.get(server_url + 'verification/?name_responsible=' + username).json() #ищем как написал пользователь
    if data['result'] == 'null':
        return None
    else:
        return data


threading.Thread(target=bot2.polling).start()
bot.polling()
