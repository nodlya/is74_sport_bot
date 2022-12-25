import json
import shutil
import threading
import traceback

import telebot
import re
import requests
from telebot import types

# Объект бота
bot = telebot.TeleBot(token="5688425165:AAHkyGJxmoMejLxzkj7ArReY5GxPZBFvjmk")
bot2 = telebot.TeleBot(token="5669270484:AAFfvWZN14zRdKKiMohMfzVZmfWGPFyqu4o")
name = None
all_chat_id = []
server_url = 'https://5582-2a09-5302-ffff-00-1ce6.eu.ngrok.io/'


@bot.message_handler(commands=['start'])
def start_message(message):
    mesg = bot.send_message(message.chat.id,
                            "Напишите мне свои фамилию, чтобы мы загрузили информацию по спортзалу и вашим сотрудникам сами"
                            # , reply_markup=web_app_keyboard())
                            )
    bot.register_next_step_handler(mesg, get_text_messages)


@bot2.message_handler(commands=['start'])
def start_message(message):
    bot2.send_message(message.chat.id, "Здравствуйте! Этот бот для администратора, и для вас доступны всего два "
                                       "действия: получить отчёт за этот месяц и напомнить всем про спортзал")
    admin_menu(message)


@bot2.message_handler()
def no_text(message):
    if message.text == 'Получить отчёт активных':
        get_report_active(message)
    elif message.text == 'Получить отчёт неактивных':
        get_report_not_active(message)
    elif message.text == 'Добавить ответственного человека':
        mesg = bot2.send_message(message.chat.id, "Введите фамилию ответственного и через пробел название его отдела")
        bot2.register_next_step_handler(mesg, add_responsible)
    elif message.text == 'Изменить ответственного':
        mesg = bot2.send_message(message.chat.id, "Введите фамилию ответственного, чтобы изменить")
        bot2.register_next_step_handler(mesg, read_update_responsible)
    elif message.text == 'Удалить ответственного':
        mesg = bot2.send_message(message.chat.id, "Введите фамилию ответственного, чтобы удалить")
        bot2.register_next_step_handler(mesg, delete_responsible)
    elif message.text == 'Напомнить про спортзал':
        remind(message)
    else:
        print('none')


def add_responsible(message):
    try:
        surname = message.text[0:message.text.index(' ')]
        dep = message.text[message.text.index(' ') + 1:]
    except:
        bot2.send_message(message.chat.id,
                          'Проверьте, всё ли вы ввели, и ещё раз нажмите "Добавить ответственного", а затем напишите фамилию и отдел ответственного')

    dep_id = -1
    list = requests.get(server_url + 'get_all_departament').json()
    resp = ''
    for i in list['result']:
        if i['departament_name'] == dep:
            dep_id = i['id']
            resp = i
    if dep_id == -1:
        bot2.send_message(message.chat.id, all_dep_list())
    else:
        result = requests.post(
            server_url + 'create_responsible?last_name_responsible=' + surname + '&id_departaments=' + str(
                i['id'])).json()
        print(result)
        try:
            if result['result'] != 'none':
                bot2.send_message(message.chat.id, 'Ответственный добавлен!')
        except:
            bot2.send_message(message.chat.id, 'Что-то пошло не так... Попробуйте ещё раз')


def read_update_responsible(message):
    surname = message.text
    list = requests.get(server_url + 'verification?name_responsible=' + surname).json()
    try:
        print(list)
        t = list['result']
        mesg = bot2.send_message(message.chat.id, 'А теперь введите новые актуальные данные - фамилию и название отдела')
        bot2.register_next_step_handler(mesg, update_responsible, t)
    except:
        bot2.send_message(message.chat.id,
                          'Проверьте, есть ли такой ответственный и нажмите изменение ответственного ещё раз')


def update_responsible(message, user_json):
    try:
        surname = message.text[0:message.text.index(' ')]
        dep = message.text[message.text.index(' ') + 1:].split(', ')
        dep_id = ''
        for i in dep:
            print(i)
            t = requests.get(server_url + 'get_departament_id/?departamet_name=' + i)
            print(t)
            if t.status_code != 400 && t.status_code != 404:
                dep_id += t['result'] + ','
            else:
                bot2.send_message(message.chat.id, all_dep_list())
        else:
            print(dep_id)
            result = requests.patch(
            server_url + 'change_responsible?id_responsible=' + str(user_json['id'])
            + '&last_name=' + surname + '&id_departaments=' + dep_id[:-1]).json()
            print(result)
            try:
                if result['result'] != 'none':
                    bot2.send_message(message.chat.id, 'Ответственный изменен!')
            except:
                bot2.send_message(message.chat.id, 'Что-то пошло не так... Попробуйте ещё раз')
    except:
        print(traceback.format_exc())
        bot2.send_message(message.chat.id,
                      'Проверьте, всё ли вы ввели, и ещё раз нажмите "Изменить ответственного", а затем напишите фамилию и отдел ответственного')


def delete_responsible(message):
    surname = message.text
    list = requests.get(server_url + 'verification?name_responsible=' + surname).json()
    try:
        print(list)
        t = list['result']
        result = requests.delete(server_url + 'delete_responsible?id_responsible=' + str(list['result']['id'])).json()
        try:
            if result['result'] != 'null':
                bot2.send_message(message.chat.id, 'Ответственный удалён!')
        except:
            bot2.send_message(message.chat.id, 'Что-то пошло не так....')
    except:
        print(traceback.format_exc())
        bot2.send_message(message.chat.id, 'Проверьте, есть ли такой ответственный и выберите удаление ещё раз')


def all_dep_list():
    result = 'Пожалуйста, сверьтесь со списком, нажмите ещё раз "Добавить ответственного", и введите отдел в точности как в списке:\n'
    list = requests.get(server_url + 'get_all_departament').json()
    for i in list['result']:
        result += i['departament_name'] + '\n'
    return result


@bot.message_handler()
def no_text(message):
    if message.text == 'Отчёт активных':
        dep = 0
        for i in range(0, len(all_chat_id)):
            print(i)
            if all_chat_id[i][0] == message.chat.id:
                dep = get_user_departament(all_chat_id[i][1]).replace(' ', '')[1:-1]
        print(dep)
        get_report_active_dep(message, dep)
    elif message.text == 'Отчёт неактивных':
        dep = 0
        for i in range(0, len(all_chat_id)):
            print(i)
            if all_chat_id[i][0] == message.chat.id:
                dep = get_user_departament(all_chat_id[i][1]).replace(' ', '')[1:-1]
        print(dep)
        get_report_not_active_dep(message, dep)
    else:
        bot2.send_message(message.chat.id, 'я такого не знаю, попробуйте понажимать на кнопочки')


def get_report_active(message):
    report = requests.get(server_url + 'get_report_activ_aboniment').content
    bot2.send_document(message.chat.id, report, visible_file_name='отчёт_активные.xlsx')


def get_report_not_active(message):
    report = requests.get(server_url + 'get_report_noactiv_aboniment').content
    bot2.send_document(message.chat.id, report, visible_file_name='отчёт_неактивные.xlsx')


def get_report_active_dep(message, dep):
    report = requests.get(server_url + 'get_report_activ_aboniment_in_departament/?id_departaments=' + str(dep)).content
    bot.send_document(message.chat.id, report, visible_file_name='отчёт_активные.xlsx')


def get_report_not_active_dep(message, dep):
    report = requests.get(server_url + 'get_report_noactiv_aboniment_in_departament/?id_departaments=' + dep).content
    bot.send_document(message.chat.id, report, visible_file_name='отчёт_неактивные.xlsx')


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
    # удаление из бд чат id


def get_text_messages(message):
    if bool(re.match('^[А-Я][а-я]+', message.text)):
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
            bot.send_message(message.chat.id,
                             "Здравствуйте! У вас появилась снизу кнопка, открывающая окно с сотрудниками и их статусом занятий",
                             reply_markup=web_app_keyboard(data))

            global all_chat_id
            all_chat_id.append([message.chat.id, data])
    else:
        mesg = bot.send_message(message.chat.id, "Что-то видимо не так, напишите фамилию ещё раз")
        bot.register_next_step_handler(mesg, get_text_messages)


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.data == 'trymore':
        mesg = bot.send_message(call.message.chat.id, "Введите ещё раз свою фамилию")
        bot.register_next_step_handler(mesg, get_text_messages)
    elif call.data == 'nottry':
        bot.send_message(call.message.chat.id, 'Напишите администратору, чтобы вас добавили в список ответственных')


def web_app_keyboard(file):  # создание клавиатуры с webapp кнопкой
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)  # создаем клавиатуру
    webAppTest = types.WebAppInfo(
        "https://famous-tarsier-114ae1.netlify.app/?id=" + get_user_departament(file).replace(' ', '')[
                                                           1:-1])  # создаем webappinfo - формат хранения url
    one_butt = types.KeyboardButton(text="Список сотрудников", web_app=webAppTest)
    butt2 = types.KeyboardButton(text="Отчёт активных")
    butt3 = types.KeyboardButton(text="Отчёт неактивных")  # создаем кнопку типа webapp
    keyboard.add(one_butt)  # добавляем кнопки в клавиатуру
    keyboard.add(butt2)
    keyboard.add(butt3)

    return keyboard  # возвращаем клавиатуру


def admin_menu(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.InlineKeyboardButton('Получить отчёт активных')
    item2 = types.InlineKeyboardButton('Получить отчёт неактивных')
    item3 = types.InlineKeyboardButton('Добавить ответственного человека')
    item4 = types.InlineKeyboardButton('Изменить ответственного')
    item5 = types.InlineKeyboardButton('Удалить ответственного')
    item6 = types.InlineKeyboardButton('Напомнить про спортзал')
    markup.add(item1)
    markup.add(item2)
    markup.add(item3)
    markup.add(item4)
    markup.add(item5)
    markup.add(item6)
    bot2.send_message(message.chat.id, 'Теперь у вас есть панель с опциями', reply_markup=markup)


def get_user_departament(user_json):
    return str(user_json['result']['responsible_for_the_department_id'])


def get_proper_user_json(username):
    json_list = [get_user_json(username)]
    # split = username.split(' ')
    # json_list.append(get_user_json(split[0]))
    # json_list.append(get_user_json(split[0]+' ' + split[1][0] + ' ' + split[2][0]))
    # json_list.append(get_user_json(split[0]+' ' + split[1][0] + '. ' + split[2][0] + '.'))
    for t in json_list:
        if t['result'] is not None:
            print(t)
            return t
    return None


def get_user_json(username):
    data = requests.get(
        server_url + 'verification/?name_responsible=' + username).json()  # ищем как написал пользователь
    if data['result'] == 'null':
        return None
    else:
        return data


threading.Thread(target=bot2.polling).start()
bot.polling()
