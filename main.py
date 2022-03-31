import schedule
import time
import calendar
import datetime
from pprint import pprint

from telegram import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton, Update
from telegram.ext import Updater, MessageHandler, Filters, ConversationHandler, CallbackContext, CallbackQueryHandler

from data import db_session
from data.chat_id import Chat_id
from data.substitution import Substitution
from data.user import User

TOKEN = "5202082113:AAGXyFL-I9Q1j-Nne1YRY7mawvKCdKlDIqY"
from telegram.ext import CommandHandler

name = [['Первая кнопка!']]
# inline_btn_1 = InlineKeyboardButton('Первая кнопка!', callback_data='button1')
inline_kb1 = ReplyKeyboardMarkup(name)


def help(update, context):
    update.message.reply_text(
        "Здравствуйте я ваш ассистент по расписанию в вашем ВУЗЕ.\n"
        "Вот список моих команд:\n"
        "/replace - поставить замещение\n"
        "/logout - выйти из аккаунта портала Table Master\n"
        # "/logout - выйти из аккаунта портала Table Master\n"
        "/reg - войти в аккаунт портала Table Master", reply_markup=inline_kb1)


def reminder():
    pass


def sign_up(update, context):
    answer = update.message.text
    if update.message.text == "cancel":
        update.message.reply_text("Регистрация отменена")
        return ConversationHandler.END
    else:
        if "login" not in context.user_data:
            context.user_data["login"] = answer
            update.message.reply_text("Введите пароль")
            return 1
    login = context.user_data["login"]
    password = update.message.text
    update.message.reply_text("Идёт проверка....")
    is_provered = 1
    if is_provered:
        sess = db_session.create_session()
        user = sess.query(User).filter(User.login.like(login), User.password.like(password)).first()
        if not user:
            user = User()
            user.login = login
            user.password = password
            sess.add(user)
            sess.commit()
        chat_id = update.message.chat_id
        chat = sess.query(Chat_id).filter(Chat_id.chat_id == chat_id).first()
        if not chat:
            chat = Chat_id()
            chat.chat_id = chat_id
            chat.user = user.id
            sess.add(chat)
            sess.commit()
        else:
            chat.user = user.id
        update.message.reply_text("Вы успешно вошли")
    else:
        update.message.reply_text("Неправильный логин или пароль")
        update.message.reply_text("Чтобы повторить попытку введите команду /reg")
    return ConversationHandler.END


def logout(update, context):
    result = proverka(update, context)
    if result:
        sess = db_session.create_session()
        chat = sess.query(Chat_id).filter(Chat_id.chat_id == update.message.chat_id).first()
        sess.query(User).filter(User.id == chat.user).delete()
        sess.query(Chat_id).filter(Chat_id.chat_id == update.message.chat_id).delete()
        sess.commit()
        update.message.reply_text("Вы успешно вышли из аккаунта")
    else:
        update.message.reply_text("Чтобы выйти из аккаунта нужно войти в аккаунт")


def start(update, context):
    update.message.reply_text(
        "Здравствуйте я ваш помощник с расписанием.\n"
        "Чтобы начать работать вы должны зарегистрироваться через команду - /reg\n"
        "Если нужна помощь с командами к вашим услугам команда /help"
    )


def proverka(update, context):
    sess = db_session.create_session()
    chat = sess.query(Chat_id).filter(Chat_id.chat_id == update.message.chat_id).first()
    if chat:
        return True
    else:
        return False


def start_reg(update, context):
    result = proverka(update, context)
    if result:
        update.message.reply_text("Вы уже зарегистрированы")
        update.message.reply_text("Если хотите Выйти из аккаунта то вам поможет команда /logout")
    else:
        update.message.reply_text("Регистрация на портале Table Master")
        update.message.reply_text("Если хотите отменить регистрацию то напишите 'cancel'")
        update.message.reply_text("Введите логин")
        return 1


def cancel(update, context):
    update.message.reply_text("Регистрация отменена")


def creat_inlinekeyboard(year, number_month):
    string_month = calendar.month_name[int(number_month)]
    days_week = ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]
    matrix = [[InlineKeyboardButton(f"{string_month} {year}", callback_data="No")],
              []]
    for i in days_week:
        matrix[1].append(InlineKeyboardButton(i, callback_data="No"))
    # matrix = []
    calendar_obj = calendar.Calendar()
    calendar_days = calendar_obj.monthdayscalendar(int(year), int(number_month))
    # matrix.extend(list(map(lambda x: list(map(str, x)), calendar_obj.monthdayscalendar(int(year), int(number_month)))))
    for i in range(len(calendar_days)):
        for j in range(len(calendar_days[i])):
            if calendar_days[i][j]:
                calendar_days[i][j] = InlineKeyboardButton(str(calendar_days[i][j]),
                                                           callback_data=str(calendar_days[i][j]))
            else:
                calendar_days[i][j] = InlineKeyboardButton(" ", callback_data="No")
    matrix.extend(calendar_days)
    matrix.append([InlineKeyboardButton("<=", callback_data="left"),
                   InlineKeyboardButton(" ", callback_data="No"),
                   InlineKeyboardButton("=>", callback_data="right")])
    matrix.append([InlineKeyboardButton("Отмена", callback_data="cancel")])
    return matrix


def replace(update, context):
    t = proverka(update, context)
    if t:
        dt_obj = datetime.datetime.now()
        year = dt_obj.strftime("%Y")
        number_month = dt_obj.strftime("%m")
        context.user_data["number_month"] = int(number_month)
        context.user_data["year"] = int(year)
        matrix = creat_inlinekeyboard(int(year), int(number_month))
        markup = InlineKeyboardMarkup(matrix)
        pprint(matrix)
        update.message.reply_text("Выберите день", reply_markup=markup)
    else:
        update.message.reply_text("Вы не вошли в аккаунт.")
        update.message.reply_text("Чтобы войти в аккаунт портала Table Master, наберите команду /reg")


def str_to_date(date_time_str):
    print(date_time_str)
    date_time_str = date_time_str.split("-")
    date_time_obj = datetime.date(year=int(date_time_str[0]), day=int(date_time_str[2]), month=int(date_time_str[1]))
    return date_time_obj


def keyboard_buttons_query(update: Update, context: CallbackContext):
    query = update.callback_query
    data = query.data
    if data == "right":
        number_month = context.user_data["number_month"]
        year = context.user_data["year"]
        if number_month == 12:
            context.user_data["year"] += 1
            year += 1
            number_month = 1
            context.user_data["number_month"] = 1
        else:
            number_month += 1
            context.user_data["number_month"] += 1
        days = InlineKeyboardMarkup(creat_inlinekeyboard(year, number_month))
        query.edit_message_text("Выберите день",
                                reply_markup=days)
    elif data == "left":
        number_month = context.user_data["number_month"]
        year = context.user_data["year"]
        if number_month == 1:
            context.user_data["year"] -= 1
            year -= 1
            number_month = 12
            context.user_data["number_month"] = 12
        else:
            number_month -= 1
            context.user_data["number_month"] -= 1
        days = InlineKeyboardMarkup(creat_inlinekeyboard(year, number_month))
        query.edit_message_text("Выберите день",
                                reply_markup=days)
    elif data.isdigit():
        keyboard_of_lessons = [
            [InlineKeyboardButton("Математика", callback_data="predmet Математика 1")],
            [InlineKeyboardButton("Английский язык", callback_data="predmet Английский язык 2")],
            [InlineKeyboardButton("Информатика", callback_data="predmet Информатика 3")],
            [InlineKeyboardButton("Физика", callback_data="predmet Физика 4")],
            [InlineKeyboardButton("Отмена", callback_data="cancel")]
        ]
        context.user_data["day"] = int(data)
        # query.edit_message_text("Выберите пару", reply_markup=InlineKeyboardMarkup(keyboard_of_lessons))
        markup = InlineKeyboardMarkup(keyboard_of_lessons)
        query.edit_message_text("Выберите пару", reply_markup=markup)
        print("chislo")
    elif data.split()[0] == "agree":
        sess = db_session.create_session()
        print(int(data.split()[1]))
        sess.query(Substitution).filter(Substitution.id == int(data.split()[1])).delete()
        sess.commit()
        query.edit_message_text("Вы приняли замещение")
    elif data == "cancel":
        query.edit_message_text("Постановка замещения отменена")
    elif data.split()[0] == "predmet":
        subject = " ".join(data.split()[1:-1])
        sess = db_session.create_session()
        chat_id = query.message.chat_id
        chat = sess.query(Chat_id).filter(Chat_id.chat_id == chat_id).first()
        substitution = Substitution()
        substitution.from_user = chat.user
        date = datetime.date(year=context.user_data["year"], day=context.user_data["day"],
                             month=context.user_data["number_month"])
        substitution.date = date
        substitution.number_para = int(query.data.split()[-1])
        sess.add(substitution)
        sess.commit()
        from_user = sess.query(User).filter(User.id == chat.user).first()
        chats = sess.query(Chat_id).filter(Chat_id.user != from_user.id)
        query.message.reply_text("Бот разослал всем пользоваетлям этого бота предложение об замещении")
        for i in chats:
            buttons = InlineKeyboardMarkup(
                [[InlineKeyboardButton("Принять", callback_data=f"agree {substitution.id}")]])
            context.bot.send_message(i.chat_id, f"Предложение на счёт замещения\n"
                                                f"Пользователь  {from_user.login} хочет чтобы кто-то его заместил\n"
                                                f"{date} на паре номер {substitution.number_para}\n",
                                     reply_markup=buttons)


# def job():
#     sess = db_session.create_session()
#     chats = sess.query(Chat_id).all()
    # for i in chats:

# def callback_minute(context):
#     my_time = datetime.time(minute=0, hour=8)
#     now_time = datetime.time
#     context.bot.send_message(chat_id=1288005934, text='One message every minute')
def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CallbackQueryHandler(callback=keyboard_buttons_query))
    registration = ConversationHandler(
        entry_points=[CommandHandler('reg', start_reg)],
        states={
            1: [MessageHandler(Filters.text, sign_up)]
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )
    dp.add_handler(CommandHandler("replace", replace))
    dp.add_handler(registration)
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("logout", logout))
    dp.add_handler(CommandHandler("start", start))
    updater.start_polling()
    # jq = updater.job_queue
    # job_minute = jq.run_repeating(callback_minute, interval=60*15)
    # schedule.every().day.at("18:27").do(job)
    #
    # while True:
    #     schedule.run_pending()
    updater.idle()


if __name__ == '__main__':
    db_session.global_init("db/blogs.db")
    main()
