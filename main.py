import os
import db

import config
import telebot

from telebot import types

bot = telebot.TeleBot(config.TOKEN)


def choose_action(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    check_balance_button = types.KeyboardButton("💰 Проверить баланс")
    add_income_button = types.KeyboardButton("➕ Добавить доходы")
    add_expenses_button = types.KeyboardButton("➖ Добавить расходы")
    get_history_button = types.KeyboardButton("💾 Получить отчёт")

    markup.row(check_balance_button)
    markup.row(add_income_button)
    markup.row(add_expenses_button)
    markup.row(get_history_button)

    bot.send_message(message.chat.id,
                     f"Выберите действие", parse_mode="markdown", reply_markup=markup)


@bot.message_handler(commands=['start'])
def start(message):
    database = db.Database()

    if database.is_registered(message.chat.id):
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
                         "💾 Просматривать историю\n"
                         "📱 И все это вы можете делать где угодно!", parse_mode="markdown", reply_markup=markup)


@bot.message_handler(content_types=['text'])
def message_handler(message):
    database = db.Database()

    if database.is_registered(message.chat.id):
        if database.get_income_in(message.chat.id):
            try:
                n = float(message.text.replace(",", "."))
                if n:
                    database.add_user_income(message.chat.id, n)

                else:
                    bot.send_message(message.chat.id, "Пожалуйста, вводите только числа, отличные от нуля")

            except ValueError:
                if message.text.lower().strip() == "end":
                    database.set_income_in(message.chat.id, False)
                    bot.send_message(message.chat.id, "Данные успешно записаны!")

                else:
                    bot.send_message(message.chat.id, "Пожалуйста, вводите только числа")

        elif database.get_expenses_in(message.chat.id):
            try:
                n = float(message.text.replace(",", "."))
                if n:
                    database.add_user_expenses(message.chat.id, n)

                else:
                    bot.send_message(message.chat.id, "Пожалуйста, вводите только числа, отличные от нуля")

            except ValueError:
                if message.text.lower().strip() == "end":
                    database.set_expenses_in(message.chat.id, False)
                    bot.send_message(message.chat.id, "Данные успешно записаны!")

                else:
                    bot.send_message(message.chat.id, "Пожалуйста, вводите только числа")

        elif message.chat.type == 'private':
            if message.text == '💰 Проверить баланс':
                balance = database.get_user_balance(message.chat.id)
                bot.send_message(message.chat.id, f"Ваш баланс: {balance}")

            elif message.text == '➕ Добавить доходы':
                bot.send_message(message.chat.id, "Для того, чтобы добавить доходы, необходимо перечислить их"
                                                  " отдельными сообщениями.\nКак только закончите, напишите *end*.",

                                 parse_mode="markdown")
                database.set_income_in(message.chat.id, True)

            elif message.text == '➖ Добавить расходы':
                bot.send_message(message.chat.id, "Для того, чтобы добавить расходы, необходимо перечислить их"
                                                  " отдельными сообщениями.\nКак только закончите, напишите *end*.",
                                 parse_mode="markdown")
                database.set_expenses_in(message.chat.id, True)

            elif message.text == "💾 Получить отчёт":
                filepath = f"histories/{message.chat.id}.txt"

                user_income = database.get_user_income(message.chat.id)
                user_expenses = database.get_user_expenses(message.chat.id)

                data = ["Информация о доходах:"]
                data += [f" +{i}" for i in user_income] if user_income else ["Нет данных о доходах."]
                data += ["\n", "Информация о расходах:"]
                data += [f" -{i}" for i in user_expenses] if user_expenses else ["Нет данных о расходах."]

                with open(filepath, "w", encoding="utf8") as history_file:
                    history_file.write("\n".join(data))

                with open(filepath, "rb") as history_file:
                    bot.send_document(message.chat.id, open(filepath, "rb"))

                os.remove(filepath)

            elif not any((database.get_income_in(message.chat.id), database.get_expenses_in(message.chat.id))):
                bot.send_message(message.chat.id, f"Такая команда не найдена!")
    else:
        bot.send_message(message.chat.id, f"Для начала зарегистрируйтесь. Перезапустите бот: /start")

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    database = db.Database()
    try:
        if call.message:
            if call.data == "signup":
                database.create_user(call.message.chat.id)
                bot.send_message(call.message.chat.id, "Вы успешно зарегистрированы! Поздравляем! 👌🏻")

                choose_action(call.message)

    except Exception as e:
        print(repr(e))


bot.polling(none_stop=True)
