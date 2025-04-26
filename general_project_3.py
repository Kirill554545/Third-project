import telebot
import time
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
import psycopg2
import re
import os

conn = psycopg2.connect(
    dbname="projectdb",
    user="postgres",
    password="1234",
    host="localhost",
    port="5432"
)

cur = conn.cursor()

# Создаем бота с вашим токеном
bot = telebot.TeleBot("7611122835:AAGaBz-4CLeVhn6j_QY3S7JwHmsnaiVrzoc")

click_count = {}

admin = [1078189371]

SAVE_DIR = 'data'
os.makedirs(SAVE_DIR, exist_ok=True)
type_message = 0
type_message_2 = 0
message_handler_active = False
profile_message_data = {}
add_bouqets_message_data = {}
wait_message = False
wait_message_add = False
download_photo = False
user_info = {}
current_bouqet_id = 0

back_to_start_button = InlineKeyboardButton("Назад", callback_data="back_to_start")
# back_to_changes_button = InlineKeyboardButton('Назад', callback_data='back_to_change')
delete_bouqet_button = InlineKeyboardButton("Удалить букет", callback_data='delete_bouqet')
p_keyboard = []
profile_button_texts = ['Изменить имя', 'Изменить номер телефона', 'Изменить электронную почту',
                        'Изменить адрес доставки']
sql_request = ['username', 'user_phone_number', 'email', 'delivery_address']
answer = ['Ваше имя успешно изменено', 'Ваш номер телефона успешно изменен', 'Ваша электронная почта успешно изменена',
          'Адрес доставки успешно изменен']
request_text = ['Ваше имя', 'Ваш номер телефона', 'Вашу электронную почту', 'адрес доставки']

b_keyboard = []
add_bouqet_button_text = ['Изменить название букета', 'Изменить фото букета', 'Изменить описание букета',
                          'Изменить цену букета', 'Сохранить']
sql_request_b = ['bouqet_name', 'bouqet_photo', 'bouqet_description', 'bouqet_price']
answer_b = ['Название букета успешно изменено', 'Фото букета успешно изменено', 'Описание букета успешно изменено',
            'Цена букета успешно изменена']
request_b = ['название букета', 'фото букета', 'описание букета', 'цену букета']
order_button = InlineKeyboardButton("Заказать", callback_data="send_order")
message_types = [
    "text",
    "document",
    "photo",
    "audio",
    "video",
    "voice",
    "video_note",
    "sticker",
    "location",
    "contact",
    "animation",
    "invoice",
    "chat_invite_link",
    "shipping_query",
    "pre_checkout_query"
]

# СОЗДАНИЕ КЛАВИАТУР
for i in profile_button_texts:
    button = InlineKeyboardButton(i, callback_data=i)
    p_keyboard.append([button])
p_keyboard.append([back_to_start_button])
profile_keyboard = InlineKeyboardMarkup(p_keyboard)

for i in add_bouqet_button_text:
    button = InlineKeyboardButton(i, callback_data=i)
    b_keyboard.append([button])
b_keyboard.append([back_to_start_button])
bouqets_keyboard = InlineKeyboardMarkup(b_keyboard)

forward = InlineKeyboardButton("->", callback_data='forward')
back = InlineKeyboardButton("<-", callback_data='back')
choose = InlineKeyboardButton("В корзину", callback_data="choose")


# bck_to_start = InlineKeyboardButton("Назад", callback_data='back_to_start')


# ПРОВЕРКА ВАЛИДНОСТИ
def is_valid_email(email):
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return re.match(pattern, email) is not None


def is_valid_name(name):
    if re.match("^[а-яА-ЯёЁa-zA-Z]+$", name) and 1 <= len(name) <= 50:
        return True
    return False


def is_valid_phone_number(phone_number):
    pattern = r'^(?:\+7|8)[0-9]{10}$'
    return bool(re.match(pattern, phone_number))


def return_bouqet_text(spisok):
    return f"""Новый букет\nНазвание: {spisok['bouqet_name']}\nФото: {len(spisok['bouqet_photo']) if spisok['bouqet_photo'][0][-3:] == 'jpg' else 0}/1\nОписание: {spisok['bouqet_description']}\nЦена: {spisok['bouqet_price']} {'' if spisok['bouqet_price'] == 'Не указана' else 'р.'}"""


def create_new_bouqet():
    return {'bouqet_name': 'Не указано', 'bouqet_photo': ['Не добавлено'], 'bouqet_description': 'Не указано',
            'bouqet_price': 'Не указана', 'ready': True}


def return_text_about_bouqet(sp):
    text = f'''Название букета: {sp[1]}\n\nОписание букета: {sp[3]}\n\nСтоимость букета: {sp[4]} р.'''
    photo = 'data/' + sp[2]
    return [text, photo]


def return_first(a):
    return a[0]


def bouqet_id(a):
    return a[1]


def basket_text(sp):
    text_for_basket = '🛒Корзина\n\n🌷Букеты:\n\n'
    bouqets_ids = list(map(bouqet_id, sp))
    cur.execute(f"""SELECT * FROM bouqets WHERE id IN %s""", (tuple(bouqets_ids),))
    bouqets_ids = cur.fetchall()
    counter = 1
    summa = 0
    for el in bouqets_ids:
        summa += int(el[4])
        pr = len(str(counter)) + 3
        el_txt = list(el[1:2] + el[3:])
        text_for_basket += f'''{counter}. Название букета: {el_txt[0]}\n{' ' * pr}Описание букета: {el_txt[1]}\n{' ' * pr}Стоимость букета: {el_txt[2]} р. \n\n'''
        counter += 1
    text_for_basket += f'Итого: {summa}'
    return text_for_basket


def order_text(sp, username):
    text = f'''Новый заказ!\n\nПользователь: @{username}\n\nЗаказ:\n\n'''
    bouqets_ids = list(map(bouqet_id, sp))
    cur.execute(f"""SELECT * FROM bouqets WHERE id IN %s""", (tuple(bouqets_ids),))
    bouqets_ids = cur.fetchall()
    summa = 0
    counter = 1
    for el in bouqets_ids:
        summa += int(el[4])
        pr = len(str(counter)) + 3
        el_txt = list(el[1:2] + el[3:])
        text += f'''{counter}. Название букета: {el_txt[0]}\n{' ' * pr}Описание букета: {el_txt[1]}\n{' ' * pr}Стоимость букета: {el_txt[2]} р. \n\n'''
        counter += 1
    text += f'Итого: {summa}'
    return text


# НАЧАЛЬНОЕ СООБЩЕНИЕ
@bot.message_handler(commands=['start'])
def start(message):
    cur.execute(f"""INSERT INTO users (user_id) VALUES ({message.chat.id}) ON CONFLICT (user_id) DO NOTHING;""")
    cur.execute('''SELECT role FROM users WHERE user_id = %s''', (message.chat.id,))
    role = cur.fetchone()[0]
    print(message.chat.id)
    button1 = InlineKeyboardButton("Готовые букеты", callback_data='bouquets')
    button2 = InlineKeyboardButton("Корзина", callback_data='basket')
    button3 = InlineKeyboardButton("Профиль", callback_data='profile')
    button4 = InlineKeyboardButton("Добавить букет", callback_data='add_bouqet')
    keyboard = [[button1], [button2], [button3]]
    if role in [2, 3]:
        keyboard.append([button4])
    # Создаем раскладку клавиатуры
    keyboard = InlineKeyboardMarkup(keyboard)
    bot.send_message(message.chat.id, 'Выберите кнопку:', reply_markup=keyboard)
    conn.commit()


# ОТКРЫТИЕ ВИТРИНЫ С БУКЕТАМИ
@bot.callback_query_handler(func=lambda call: call.data in ['bouquets'])
def handle_first_buttons(call):
    global bouqets, role, current_bouqet_id
    cur.execute('''SELECT role FROM users WHERE user_id = %s''', (call.message.chat.id,))
    role = cur.fetchone()[0]
    cur.execute('''SELECT * FROM bouqets''')
    bouqets = cur.fetchall()
    bot.delete_message(call.message.chat.id, call.message.message_id)
    click_count[call.message.chat.id] = 0
    if bouqets:
        info = return_text_about_bouqet(bouqets[click_count[call.message.chat.id]])
        current_bouqet_id = bouqets[click_count[call.message.chat.id]][0]
        # pages_info_button = InlineKeyboardButton(f"{click_count[call.message.chat.id] + 1}/{len(bouqets)}",
        #                                          callback_data='stranica')
        showcase_keyboard = [[back, choose, forward], [back_to_start_button]]
        if role in [2, 3]:
            showcase_keyboard.append([delete_bouqet_button])
        new_keyboard = InlineKeyboardMarkup(showcase_keyboard)
        with open(info[1], 'rb') as photo:
            bot.send_photo(call.message.chat.id, caption=info[0], photo=photo, reply_markup=new_keyboard)
    else:
        keyboard = InlineKeyboardMarkup([[back_to_start_button]])
        bot.send_message(chat_id=call.message.chat.id, text='Витрина пока что пуста, приходите позже :)',
                         reply_markup=keyboard)


# УДАЛЕНИЕ БУКЕТА С ВИТРИНЫ

@bot.callback_query_handler(func=lambda call: call.data in ['delete_bouqet'])
def delete_bouqet_fn(call):
    bot.delete_message(call.message.chat.id, call.message.message_id)
    start(call.message)
    cur.execute(f"""SELECT bouqet_photo FROM bouqets WHERE id = {current_bouqet_id}""")
    file_name = str(map(return_first, cur.fetchone()))
    file_path = os.path.join('data', file_name + '.jpg')
    if os.path.isfile(file_path):
        os.remove(file_path)
    cur.execute(f"""DELETE FROM bouqets WHERE id = {current_bouqet_id}""")
    conn.commit()


# ОТКРЫТИЕ ПРОФИЛЯ ПОЛЬЗОВАТЕЛЯ

@bot.callback_query_handler(func=lambda call: call.data in ['profile'])
def profile_open(call):
    global profile_keyboard
    bot.delete_message(call.message.chat.id, call.message.message_id)
    cur.execute("""SELECT email, username, user_phone_number, delivery_address FROM users WHERE user_id = %s;""",
                (call.message.chat.id,))
    user_info = cur.fetchone()
    profile_text = f"""Профиль\n\nИмя: {user_info[1]}\n\nНомер телефона: {user_info[2]}\n\nЭлектронная почта: {user_info[0]}\n\nАдрес доставки: {user_info[3]}"""
    msg = bot.send_message(call.message.chat.id, profile_text, reply_markup=profile_keyboard)
    profile_message_data[call.message.chat.id] = []
    profile_message_data[call.message.chat.id].append(msg.message_id)


# ДОБАВЛЕНИЕ БУКЕТА В КОРЗИНУ
@bot.callback_query_handler(func=lambda call: call.data in ['choose'])
def add_to_basket(call):
    bouqet_id = bouqets[click_count[call.message.chat.id]][0]
    user_id = call.message.from_user.id
    cur.execute(f"""SELECT bouqet_id FROM basket WHERE user_id = '{user_id}'""")
    bouqets_id = list(map(return_first, cur.fetchall()))
    if bouqet_id not in bouqets_id:
        cur.execute(f"""INSERT INTO basket (bouqet_id, user_id) VALUES ({bouqet_id}, '{user_id}')""")
        conn.commit()
        msg = bot.send_message(call.message.chat.id, text='Букет успешно добавлен в корзину!')
        time.sleep(2)
        bot.delete_message(call.message.chat.id, message_id=msg.message_id)
    else:
        pass


# ФУНКЦИОНАЛ СМЕНЫ ЛИЧНЫХ ДАННЫХ

@bot.callback_query_handler(func=lambda call: call.data in profile_button_texts)
def change(call):
    global wait_message, profile_message_data, profile_button_texts, type_message
    wait_message = True
    bot.answer_callback_query(call.id)
    for el in range(1, len(profile_message_data[call.message.chat.id])):
        bot.delete_message(chat_id=call.message.chat.id, message_id=profile_message_data[call.message.chat.id][el])
    profile_message_data[call.message.chat.id] = [profile_message_data[call.message.chat.id][0]]
    bck_to_profile = InlineKeyboardButton("Назад", callback_data="back_to_profile")
    keyboard = [[bck_to_profile]]
    new_keyboard = InlineKeyboardMarkup(keyboard)
    msg_1 = bot.send_message(call.message.chat.id,
                             f"Теперь вы можете отправить {' '.join(call.json['data'].split()[1:])}",
                             reply_markup=new_keyboard)
    profile_message_data[call.message.chat.id].append(msg_1.message_id)
    bot.register_next_step_handler(call.message, chn)
    type_message = profile_button_texts.index(call.json['data'])


def chn(message: telebot.types.Message):
    global profile_keyboard, wait_message, type_message, answer, sql_request
    access = False
    if message.chat.id in profile_message_data and wait_message:
        wait_message = False
        if type_message == 0:
            if is_valid_name(message.text):
                access = True
        elif type_message == 1:
            if is_valid_phone_number(message.text):
                access = True
        elif type_message == 2:
            if is_valid_email(message.text):
                access = True
        elif type_message == 3:
            access = True
        if access:
            ans = bot.send_message(message.chat.id, answer[type_message])
            cur.execute(f"""UPDATE users SET {sql_request[type_message]} = %s WHERE user_id = %s""",
                        (message.text, message.chat.id))
            conn.commit()
            cur.execute(
                """SELECT username, user_phone_number, email, delivery_address FROM users WHERE user_id = %s;""",
                (message.chat.id,))
            user_info = cur.fetchone()
            profile_text = f"""Профиль\n\nИмя: {user_info[0]}\n\nНомер телефона: {user_info[1]}\n\nЭлектронная почта: {user_info[2]}\n\nАдрес доставки: {user_info[3]}"""
            bot.edit_message_text(text=profile_text, chat_id=message.chat.id,
                                  message_id=profile_message_data[message.chat.id][0],
                                  reply_markup=profile_keyboard)
            wait_message = False
            access = False
        else:
            ans = bot.send_message(message.chat.id, "Неверный формат ввода.\nПопробуйте еще раз.")
            wait_message = False
        time.sleep(2)
        bot.delete_message(chat_id=message.chat.id, message_id=profile_message_data[message.chat.id][1])
        bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        bot.delete_message(chat_id=message.chat.id, message_id=ans.message_id)
        profile_message_data[message.chat.id] = [profile_message_data[message.chat.id][0]]


# ОСНОВНЫЕ ДЕЙСТВИЯ С КНОПКАМИ


# ВОЗВРАТ К ПЕРВОМУ СООБЩЕНИЮ
@bot.callback_query_handler(func=lambda call: call.data == 'back_to_start')
def handle_second_buttons(call):
    bot.delete_message(call.message.chat.id, call.message.message_id)
    start(call.message)


# ВОЗВРАТ К ПРОФИЛЮ
@bot.callback_query_handler(func=lambda call: call.data == 'back_to_profile')
def back_profile(call):
    profile_message_data[call.message.chat.id] = [profile_message_data[call.message.chat.id]]
    bot.delete_message(call.message.chat.id, call.message.message_id)
    profile_open(call)


# ВОЗВРАТ К СОЗДАНИЮ БУКЕТА
@bot.callback_query_handler(func=lambda call: call.data == 'back_to_change_list')
def back_change(call):
    global wait_message_add, download_photo, temporary_data
    if temporary_data:
        save_photo(*temporary_data)
    wait_message_add = False
    download_photo = False
    for message in add_bouqets_message_data[call.message.chat.id][1:]:
        bot.delete_message(call.message.chat.id, message)
    add_bouqets_message_data[call.message.chat.id] = [add_bouqets_message_data[call.message.chat.id][0]]


# СОХРАНЕНИЕ БУКЕТА
@bot.callback_query_handler(func=lambda call: call.data == 'Сохранить')
def save_bouqet(call):
    global new_bouqet, temporary_data
    cur.execute(
        f'''INSERT INTO bouqets (bouqet_name, bouqet_photo, bouqet_description, bouqet_price) 
        VALUES ('{new_bouqet['bouqet_name']}', '{str(new_bouqet['bouqet_photo'][0])}', '{new_bouqet['bouqet_description']}', 
        '{new_bouqet['bouqet_price']}')''')
    conn.commit()
    new_bouqet = create_new_bouqet()
    ans = bot.send_message(call.message.chat.id, 'Данные успешно сохранены')
    time.sleep(2)
    bot.delete_message(call.message.chat.id, ans.message_id)
    temporary_data = []
    text_bouqets = return_bouqet_text(new_bouqet)
    bot.edit_message_text(text_bouqets, chat_id=call.message.chat.id,
                          message_id=add_bouqets_message_data[call.message.chat.id][0],
                          reply_markup=bouqets_keyboard)


# ПЕРЕЛИСТЫВАНИЕ ВИТРИНЫ (ВПЕРЕД/НАЗАД)
@bot.callback_query_handler(func=lambda call: call.data in ['forward', 'back'])
def forward_back_buttons(call):
    global bouqets, click_count, role, current_bouqet_id
    edit = False
    if call.data == 'forward' and click_count[call.message.chat.id] < len(bouqets) - 1:
        click_count[call.message.chat.id] += 1
        edit = True
    elif call.data == 'back' and click_count[call.message.chat.id] > 0:
        click_count[call.message.chat.id] -= 1
        edit = True
    if edit:
        # pages_info_button = InlineKeyboardButton(f"{click_count[call.message.chat.id] + 1}/{len(bouqets)}",
        #                                          callback_data='stranica')
        showcase_keyboard = [[back, choose, forward], [back_to_start_button]]
        if role in [2, 3]:
            showcase_keyboard.append([delete_bouqet_button])
        new_keyboard = InlineKeyboardMarkup(showcase_keyboard)
        info = return_text_about_bouqet(bouqets[click_count[call.message.chat.id]])
        current_bouqet_id = bouqets[click_count[call.message.chat.id]][0]
        with open(info[1], 'rb') as new_photo:
            bot.edit_message_media(media=InputMediaPhoto(new_photo, caption=info[0]), chat_id=call.message.chat.id,
                                   message_id=call.message.message_id, reply_markup=new_keyboard)
        edit = False


# ОТКРЫТИЕ КОРЗИНЫ
@bot.callback_query_handler(func=lambda call: call.data in ['basket'])
def open_basket(call):
    bot.delete_message(call.message.chat.id, call.message.message_id)
    keyboard = [[order_button], [back_to_start_button]]
    new_keyboard_1 = InlineKeyboardMarkup(keyboard)
    cur.execute(f"""SELECT * FROM basket WHERE user_id = '{call.message.from_user.id}'""")
    bouqs = cur.fetchall()
    profile_text = basket_text(bouqs)
    bot.send_message(call.message.chat.id, profile_text, reply_markup=new_keyboard_1)


@bot.callback_query_handler(func=lambda call: call.data in ['send_order'])
def send_order_function(call):
    cur.execute(f"""SELECT * FROM basket WHERE user_id = '{call.message.from_user.id}'""")
    bouqs = cur.fetchall()
    message_text = order_text(bouqs, call.message.chat.username)
    if bouqs:
        print(1)
        print(call)
        msg = bot.send_message(admin[0], 'У Вас новый заказ!')
        time.sleep(10)
        bot.delete_message(admin[0], message_id=msg.message_id)


# ДОБАВЛЕНИЕ НОВОГО БУКЕТА
@bot.callback_query_handler(func=lambda call: call.data in ['add_bouqet'])
def add_bouq(call):
    global bouqets_keyboard, new_bouqet, temporary_data
    temporary_data = []
    new_bouqet = create_new_bouqet()
    bot.delete_message(call.message.chat.id, call.message.message_id)
    text_bouqets = return_bouqet_text(new_bouqet)
    msg = bot.send_message(call.message.chat.id, text_bouqets, reply_markup=bouqets_keyboard)
    add_bouqets_message_data[call.message.chat.id] = []
    add_bouqets_message_data[call.message.chat.id].append(msg.message_id)


# ВЫБОР ПАРАМЕТРА ИЗМЕНЕНИЯ У БУКЕТА
@bot.callback_query_handler(func=lambda call: call.data in add_bouqet_button_text)
def change_1(call):
    global wait_message_add, add_bouqets_message_data, add_bouqet_button_text, type_message_2, download_photo
    bck_to_changes = InlineKeyboardButton("Назад", callback_data="back_to_change_list")
    new_keyboard_b = InlineKeyboardMarkup([[bck_to_changes]])
    msg_2 = bot.send_message(call.message.chat.id,
                             f"Теперь вы можете отправить {' '.join(call.json['data'].split()[1:])}",
                             reply_markup=new_keyboard_b)
    add_bouqets_message_data[call.message.chat.id].append(msg_2.message_id)
    type_message_2 = add_bouqet_button_text.index(call.json['data'])
    if type_message_2 in [0, 2, 3]:
        print('Обработка текстовых сообщений')
        wait_message_add = True
        bot.register_next_step_handler(call.message, text_changes)
    else:
        print('Обработка отправленных фотографий')
        if new_bouqet['ready'] is True:
            new_bouqet[sql_request_b[1]].clear()
            new_bouqet['ready'] = False
        download_photo = True
        bot.register_next_step_handler(call.message, handle_photo)


# ОБРАБОТКА ТЕКСТОВЫХ ПАРАМЕТРОВ У БУКЕТА
@bot.message_handler(content_types=['message'])
def text_changes(message: telebot.types.Message):
    global bouqets_keyboard, wait_message_add, answer_b, sql_request_b, type_message_2, new_bouqet, add_bouqets_message_data
    if wait_message_add:
        wait_message_add = False
        add_bouqets_message_data[message.chat.id].append(message.message_id)
        new_bouqet[sql_request_b[type_message_2]] = message.text
        text_bouqets = return_bouqet_text(new_bouqet)
        ans_b = bot.send_message(message.chat.id, answer_b[type_message_2])
        add_bouqets_message_data[message.chat.id].append(ans_b.message_id)
        bot.edit_message_text(text_bouqets, chat_id=message.chat.id,
                              message_id=add_bouqets_message_data[message.chat.id][0],
                              reply_markup=bouqets_keyboard)
        time.sleep(2)
        for el in add_bouqets_message_data[message.chat.id][1:]:
            bot.delete_message(message.chat.id, el)
        add_bouqets_message_data[message.chat.id] = [add_bouqets_message_data[message.chat.id][0]]


# ОБРАБОТКА ФОТОГРАФИЙ ДЛЯ БУКЕТА
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    global download_photo, new_bouqet, add_bouqets_message_data, temporary_data
    if download_photo:
        if len(temporary_data) < 1:
            temporary_data.append(message.photo[-1])
            add_bouqets_message_data[message.chat.id].append(message.message_id)
        if len(temporary_data) == 1:
            download_photo = False
            save_photo(*temporary_data[len(new_bouqet[sql_request_b[1]]):])
            temporary_data = []
            ans_b = bot.send_message(message.chat.id, answer_b[1])
            add_bouqets_message_data[message.chat.id].append(ans_b.message_id)
            for el in add_bouqets_message_data[message.chat.id][1:]:
                bot.delete_message(message.chat.id, el)
            add_bouqets_message_data[message.chat.id] = [add_bouqets_message_data[message.chat.id][0]]
        text_bouqets = return_bouqet_text(new_bouqet)
        bot.edit_message_text(text_bouqets, chat_id=message.chat.id,
                              message_id=add_bouqets_message_data[message.chat.id][0],
                              reply_markup=bouqets_keyboard)
    else:
        bot.delete_message(message.chat.id, message.message_id)


# СОХРАНЕНИЕ ФОТОГРАФИЙ В ПАПКУ data
def save_photo(*file_info):
    for files in file_info:
        file_count = len([f for f in os.listdir('data') if os.path.isfile(os.path.join('data', f))])
        file_id = files.file_id
        file = bot.get_file(file_id)
        file_path = os.path.join('data', f"photo_{file_count + 1}.jpg")
        downloaded_file = bot.download_file(file.file_path)
        with open(file_path, 'wb') as new_file:
            new_file.write(downloaded_file)
            new_bouqet[sql_request_b[1]].append(file_path.split('\\')[1])
        print(f"Фотография сохранена как {file_path}")


# УДАЛЕНИЕ ЛЮБЫХ СООБЩЕНИЙ, КОТОРЫЕ НЕ ЖДАЛ БОТ
@bot.message_handler(content_types=message_types)
def echo_message(message):
    print(message.message_id)
    global wait_message, download_photo
    if not wait_message and not download_photo:
        bot.delete_message(chat_id=message.chat.id, message_id=message.id)


# @bot.message_handler(content_types=['sticker'])
# def handle_stickers(message):
#     echo_message(message)


# @bot.message_handler(func=lambda message: True)  # Обрабатываем все типы сообщений
# def handle_all_messages(message):
#     # Отправляем ответ для подтверждения получения сообщения
#     bot.send_message(message.chat.id, "Ваше сообщение получено! Удаляю...")
#
#     # Удаляем сообщение пользователя
#     try:
#         bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
#     except Exception as e:
#         print(f"Ошибка при удалении сообщения: {e}")

# ОТПРАВКА СООБЩЕНИЙ АДМИНИСТРАТОРУ
@bot.message_handler(content_types=['document'])
def doc(message):
    if message.document:
        bot.send_document(admin[0], message.document.file_id, caption=f'Сдал отчет @{message.from_user.username}')


# @bot.message_handler(func=lambda call: call.data in ['order'])
# def send_order(call):
#     cur.execute(f"""SELECT * FROM basket WHERE user_id = '{call.message.from_user.id}'""")
#     bouqs = cur.fetchall()
#     message_text = order_text(bouqs, call.message.from_user.username)
#     print(1)
#     if bouqs:
#         bot.send_message(admin[0], message_text)

# Запускаем бота
if __name__ == '__main__':
    bot.polling(none_stop=True)
