import db

import config
import telebot

from telebot import types

user_id, username = int(), str()
income_in, expenses_in = False, False
income, expenses = list(), list()

bot = telebot.TeleBot(config.TOKEN)


def choose_action(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    check_balance_button = types.KeyboardButton("💰 Проверить баланс")
    add_income_button = types.KeyboardButton("➕ Добавить доходы")
    add_expenses_button = types.KeyboardButton("➖ Добавить расходы")

    markup.row(check_balance_button)
    markup.row(add_income_button)
    markup.row(add_expenses_button)

    bot.send_message(message.chat.id,
                     f"Выберите действие", parse_mode="markdown", reply_markup=markup)


@bot.message_handler(commands=['start'])
def start(message):
    global user_id, username
    user_id = message.chat.id
    username = message.from_user.username
    database = db.Database()

    if database.is_registered(user_id):
        bot.send_message(message.chat.id,
                         f"Здравствуйте, *{message.from_user.first_name} {message.from_user.last_name}*!", parse_mode="markdown")
        choose_action(message)

    else:
        markup = types.InlineKeyboardMarkup(row_width=1)
        signup_button = types.InlineKeyboardButton("Зарегистрироваться", callback_data="signup")
        markup.add(signup_button)

        bot.send_message(message.chat.id,
                         "Это бот *MCStudio*\nС его помощью вы можете:\n💰 Вести учёт своих денежных средств\n"
                         "✔ Проверять баланс\n"
                         "➕ Добавлять свои доходы\n"
                         "➖ Добавлять свои расходы\n"
                         "📱 И все это вы можете делать где угодно!", parse_mode="markdown", reply_markup=markup)


@bot.message_handler(content_types=['text'])
def message_handler(message):
    global income_in, expenses_in, income, expenses
    database = db.Database()

    if income_in:
        try:
            n = float(message.text.replace(",", "."))
            if n:
                income.append(n)

            else:
                bot.send_message(message.chat.id, "Пожалуйста, вводите только числа, отличные от нуля")

        except ValueError:
            if message.text.lower().strip() == "end":
                income_in = False
                database.add_user_income(user_id, *income)
                bot.send_message(message.chat.id, "Данные успешно записаны!" if income else "Данные не записаны!")
                income = list()

            else:
                bot.send_message(message.chat.id, "Пожалуйста, вводите только числа")

    elif expenses_in:
        try:
            n = float(message.text.replace(",", "."))
            if n:
                expenses.append(n)

            else:
                bot.send_message(message.chat.id, "Пожалуйста, вводите только числа, отличные от нуля")

        except ValueError:
            if message.text.lower().strip() == "end":
                expenses_in = False
                database.add_user_expenses(user_id, *expenses)
                bot.send_message(message.chat.id, "Данные успешно записаны!" if expenses else "Данные не записаны!")
                expenses = list()

            else:
                bot.send_message(message.chat.id, "Пожалуйста, вводите только числа")

    elif message.chat.type == 'private':
        if message.text == '💰 Проверить баланс':
            balance = database.get_user_balance(user_id)
            bot.send_message(message.chat.id, f"Ваш баланс: {balance}")

        elif message.text == '➕ Добавить доходы':
            bot.send_message(message.chat.id, "Для того, чтобы добавить доходы, необходимо перечислить их отдельными "
                                              "сообщениями.\nКак только закончите, напишите *end*.",
                             parse_mode="markdown")
            income_in = True

        elif message.text == '➖ Добавить расходы':
            bot.send_message(message.chat.id, "Для того, чтобы добавить расходы, необходимо перечислить их отдельными "
                                              "сообщениями.\nКак только закончите, напишите *end*.",
                             parse_mode="markdown")
            expenses_in = True

        elif not any((income_in, expenses_in)):
            bot.send_message(message.chat.id, f"Такая команда не найдена!")


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    database = db.Database()
    try:
        if call.message:
            if call.data == "signup":
                database.create_user(user_id, username)
                bot.send_message(call.message.chat.id, "Вы успешно зарегистрированы! Поздравляем! 👌🏻")

                choose_action(call.message)

    except Exception as e:
        print(repr(e))


bot.polling(none_stop=True)
