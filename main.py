import calendar
import calendar
import datetime

from telegram import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton, Update
from telegram.ext import Updater, MessageHandler, Filters, ConversationHandler, CallbackContext, CallbackQueryHandler

from data import db_session
from data.API_from_SKGMI import getSession, getUserName, genarateCodeAndSendOnEmail, getRating, getLessonsForStudent, \
    ValidateCode, getSkgmiIdFIO, addRecord
from data.user import User

diplom_name = "diplom.png"
dic_semestrs = {1: "Первый семестр", 2: "Второй семестр", 3: "Третий семестр", 4: "Четвёртый семестр",
                5: "Пятый семестр", 6: "Шестой семестр", 7: "Седьмой семестр", 8: "Восьмой семестр",
                9: "Девятый семестр"}

# TOKEN = "5192554941:AAHxw_cR7O7rG1feNC7kRCxhFfKMMjKAdqY"
TOKEN = "5202082113:AAGXyFL-I9Q1j-Nne1YRY7mawvKCdKlDIqY"
from telegram.ext import CommandHandler

text_commands = [["/getId", "/getFIO", "/timetable", "/add_ach"],
                 ["/sess", "/rating", "/logout"],
                 ["/help", "/myId", "/start"]]
commands = ReplyKeyboardMarkup(text_commands)


def help(update, context):
    update.message.reply_text(
        "Здравствуйте я ваш ассистент по расписанию в вашем ВУЗЕ.\n"
        "Вот список моих команд:\n"
        "/logout - выйти из аккаунта\n"
        "/watch - просмотреть расписание\n"
        "/find_id - просмотр SKGMI.ID по ФИО\n"
        "/rating - просмотр рейтинга(для студентов)\n"
        "/add_ach - добавить достижение\n"
        "/reg - войти в аккаунт", reply_markup=commands)


def start_new_reg(update, context):
    t = check_on_registration_in_bot(update, context)
    if not t:
        update.message.reply_text("Введите свой SKGMI.ID")
        update.message.reply_text("(Чтобы отменить введите команду /cancel)")
        return 1
    else:
        update.message.reply_text("Ву уже вошли в аккаунт, чтобы выйти из него нужно использовать команду /logout")
        return ConversationHandler.END


def myId(update, context):
    t = check_on_registration_in_bot(update, context)
    if t:

        user = getID(update, context)
        update.message.reply_text("Ваш SKGMI.ID - " + user.skgmi_id)
    else:
        update.message.reply_text("Вы не зарегитрированы")
        update.message.reply_text("Для регистрации используйте /reg")


def watch_lessons(update, context):
    t = check_on_registration_in_bot(update, context)
    if t:
        dt_obj = datetime.datetime.now()
        year = dt_obj.strftime("%Y")
        number_month = dt_obj.strftime("%m")
        context.user_data["number_month"] = int(number_month)
        context.user_data["year"] = int(year)
        calendar_days = creat_inlinekeyboard(year, number_month)

        update.message.reply_text("Выберите день",
                                  reply_markup=InlineKeyboardMarkup(calendar_days))
    else:
        update.message.reply_text("Вы не вошли в аккаунт")
        update.message.reply_text("Чтобы войти в аккаунт нужно использовать команду /reg")


yes_or_no_logout_keyboard = [
    [InlineKeyboardButton("Да", callback_data="LOGOUT YES"),
     InlineKeyboardButton("Нет", callback_data="LOGOUT NOT")]]
yes_or_no_logout_markup = InlineKeyboardMarkup(yes_or_no_logout_keyboard)


def logout(update, context):
    result = check_on_registration_in_bot(update, context)
    if result:
        update.message.reply_text("Вы точно хотите выйти из аккаунта.",
                                  reply_markup=yes_or_no_logout_markup)
    else:
        update.message.reply_text("Чтобы выйти из аккаунта нужно войти в аккаунт")


def start(update, context):
    update.message.reply_text(
        "Здравствуйте я ваш помощник с расписанием.\n"
        "Чтобы начать работать вы должны зарегистрироваться через команду - /reg\n"
        "Если нужна помощь с командами к вашим услугам команда /help",
    reply_markup=commands)


def check_on_registration_in_bot(update, context):
    chat = getID(update, context)
    if chat:
        return True
    else:
        return False


def start_reg(update, context):
    result = check_on_registration_in_bot(update, context)
    if result:
        update.message.reply_text("Вы уже зарегистрированы")
        update.message.reply_text("Если хотите Выйти из аккаунта то вам поможет команда /logout")
    else:
        update.message.reply_text("Регистрация")
        update.message.reply_text("Если хотите отменить регистрацию то напишите 'cancel'")
        update.message.reply_text("Введите логин")
        return 1


def cancel(update, context):
    update.message.reply_text("Отмена")


def creat_inlinekeyboard(year, number_month):
    string_month = calendar.month_name[int(number_month)]
    days_week = ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]
    matrix = [[InlineKeyboardButton(f"{string_month} {year}", callback_data="No")],
              []]
    for i in days_week:
        matrix[1].append(InlineKeyboardButton(i, callback_data="No"))
    calendar_obj = calendar.Calendar()
    calendar_days = calendar_obj.monthdayscalendar(int(year), int(number_month))
    for i in range(len(calendar_days)):
        for j in range(len(calendar_days[i])):
            if calendar_days[i][j]:
                calendar_days[i][j] = InlineKeyboardButton(str(calendar_days[i][j]),
                                                           callback_data=f"watch_lessons {calendar_days[i][j]}")
            else:
                calendar_days[i][j] = InlineKeyboardButton(" ", callback_data="No")
    matrix.extend(calendar_days)
    matrix.append([InlineKeyboardButton("<=", callback_data="left"),
                   InlineKeyboardButton(" ", callback_data="No"),
                   InlineKeyboardButton("=>", callback_data="right")])

    matrix.append([InlineKeyboardButton("Отмена", callback_data="cancel")])
    return matrix




def str_to_date(date_time_str):
    date_time_str = date_time_str.split("-")
    date_time_obj = datetime.date(year=int(date_time_str[0]), day=int(date_time_str[2]), month=int(date_time_str[1]))
    return date_time_obj


def getID(update, context):
    if "user" in context.user_data:
        return context.user_data["user"]
    else:
        chat_id = update.message.chat_id
        sess = db_session.create_session()
        # answer_id =
        skgmi_id = sess.query(User).filter(User.id == chat_id).first()
        context.user_data["user"] = skgmi_id
        return skgmi_id


def keyboard_buttons_query(update: Update, context: CallbackContext):
    query = update.callback_query
    data = query.data
    if data.split()[0] == "LOGOUT":
        if data.split()[1] == "NOT":
            query.edit_message_text("Вы остались в аккаунте")
        else:
            sess = db_session.create_session()
            sess.query(User).filter(User.id == query.message.chat_id).delete()
            sess.commit()
            del context.user_data["user"]
            query.edit_message_text("Вы успешно вышли из аккаунта")
    elif data.split("_")[:2] == ["show", "semestrs"]:
        keyboard = []
        for i in dic_semestrs:
            keyboard.append([InlineKeyboardButton(dic_semestrs[i], callback_data=f"{i}_{data.split('_')[2]}_")])
        markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text("Все семестры", reply_markup=markup)
    elif len(data.split("_")) == 3:
        print(data)
        try:
            if data.split("_")[1] == "rating":
                print(data)
                semestr = int(data.split("_")[0])

                user = getID(query, context)
                response = getRating(user.skgmi_id)
                keyboard = [[InlineKeyboardButton(dic_semestrs[semestr], callback_data="show_semestrs_rating")],
                            [InlineKeyboardButton("<=", callback_data="left_rating"),
                             InlineKeyboardButton("=>", callback_data="right_rating")],
                            [InlineKeyboardButton("Предмет | Контроль | Рейтинг ", callback_data="No")]]
                for i in response:
                    if i["Term"] == dic_semestrs[semestr]:
                        keyboard.append([InlineKeyboardButton(
                            i["SubjectName"] + " | " + str(i["RatingControl_1"]) + " | " + str(i["CurrentControl_1"]),
                            callback_data="No")])
                context.user_data["semestr"] = semestr
                query.edit_message_text("Ваш рейтинг", reply_markup=InlineKeyboardMarkup(keyboard))
            elif data.split("_")[1] == "sess":
                semestr = int(data.split("_")[0])
                user = getID(query, context)
                response = getSession(user.skgmi_id)
                keyboard = [[InlineKeyboardButton(dic_semestrs[semestr], callback_data="show_semestrs_sess")],
                            [InlineKeyboardButton("<=", callback_data="left_sess"),
                             InlineKeyboardButton("=>", callback_data="right_sess")],
                            [InlineKeyboardButton("Предмет | Тип | Оценка", callback_data="No")]]
                for i in response:
                    if i["Term"] == dic_semestrs[semestr]:
                        button = InlineKeyboardButton(f"""{i["Subject"]}|{i["TypeOfTheControl"]}|{i["Mark"]}""",
                                                      callback_data="No")
                        keyboard.append([button])
                context.user_data["semestr"] = semestr
                query.edit_message_text("Ваши оценки за сессию", reply_markup=InlineKeyboardMarkup(keyboard))
        except IndexError:
            pass
    elif data == "right":
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
    elif data == "right_sess":
        semestr = context.user_data["semestr"]
        if semestr + 1 <= len(dic_semestrs):

            user = getID(query, context)
            response = getSession(user.skgmi_id)
            keyboard = [[InlineKeyboardButton(dic_semestrs[semestr + 1], callback_data="show_semestrs_sess")],
                        [InlineKeyboardButton("<=", callback_data="left_sess"),
                         InlineKeyboardButton("=>", callback_data="right_sess")],
                        [InlineKeyboardButton("Предмет | Тип | Оценка", callback_data="No")]]
            for i in response:
                if i["Term"] == dic_semestrs[semestr + 1]:
                    button = InlineKeyboardButton(f"""{i["Subject"]}|{i["TypeOfTheControl"]}|{i["Mark"]}""",
                                                  callback_data="No")
                    keyboard.append([button])
            context.user_data["semestr"] += 1
            query.edit_message_text("Ваши оценки за сессию", reply_markup=InlineKeyboardMarkup(keyboard))
    elif data == "left_sess":
        semestr = context.user_data["semestr"]
        if semestr - 1 >= 1:

            user = getID(query, context)
            response = getSession(user.skgmi_id)
            keyboard = [[InlineKeyboardButton(dic_semestrs[semestr - 1], callback_data="show_semestrs_sess")],
                        [InlineKeyboardButton("<=", callback_data="left_sess"),
                         InlineKeyboardButton("=>", callback_data="right_sess")],
                        [InlineKeyboardButton("Предмет | Тип | Оценка", callback_data="No")]]
            for i in response:
                if i["Term"] == dic_semestrs[semestr - 1]:
                    button = InlineKeyboardButton(f"""{i["Subject"]}|{i["TypeOfTheControl"]}|{i["Mark"]}""",
                                                  callback_data="No")
                    keyboard.append([button])
            context.user_data["semestr"] -= 1
            query.edit_message_text("Ваши оценки за сессию", reply_markup=InlineKeyboardMarkup(keyboard))
    elif data.split()[0] == "left":
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
        if len(data.split()) == 2:
            if data.split()[1] == "watching":
                days = InlineKeyboardMarkup(creat_inlinekeyboard(year, number_month))
        else:
            days = InlineKeyboardMarkup(creat_inlinekeyboard(year, number_month))
        query.edit_message_text("Выберите день",
                                reply_markup=days)
    elif data.split()[0] == "watch_lessons":
        role = "student"
        if role == "student":
            context.user_data["day"] = int(data.split()[1])
            lessons = getLessonsForStudent(getID(query, context).skgmi_id,
                                           day=context.user_data["day"],
                                           month=context.user_data["number_month"],
                                           year=context.user_data["year"])
            if not lessons:
                lessons.append([InlineKeyboardButton("(Нет пар)", callback_data="back_to_watch_calendar_days")])
                lessons.append([InlineKeyboardButton("Назад", callback_data="back_to_watch_calendar_days")])
                markup = InlineKeyboardMarkup(lessons)
                query.edit_message_text("Все пары", reply_markup=markup)
            else:
                for i in range(len(lessons)):
                    h = f"""8:30 | {lessons[i]["SubjectName"]} | Аудитория {lessons[i]["Building"]}-{lessons[i]["Classroom"].split()[-1]} | {lessons[i]["TeacherName"]}"""
                    lessons[i] = [InlineKeyboardButton(h, callback_data='No')]
                lessons.append([InlineKeyboardButton("Назад", callback_data="back_to_watch_calendar_days")])
                markup = InlineKeyboardMarkup(lessons)
                query.edit_message_text("Все пары", reply_markup=markup)
    elif data == "left_rating":
        semestr = context.user_data["semestr"]
        if semestr - 1 >= 1:

            user = getID(query, context)
            response = getRating(user.skgmi_id)
            keyboard = [[InlineKeyboardButton(dic_semestrs[semestr - 1], callback_data="show_semestrs_rating")],
                        [InlineKeyboardButton("<=", callback_data="left_rating"),
                         InlineKeyboardButton("=>", callback_data="right_rating")],
                        [InlineKeyboardButton("Предмет | Контроль | Рейтинг ", callback_data="No")]]
            for i in response:
                if i["Term"] == dic_semestrs[semestr - 1]:
                    keyboard.append([InlineKeyboardButton(
                        i["SubjectName"] + " | " + str(i["RatingControl_1"]) + " | " + str(i["CurrentControl_1"]),
                        callback_data="No")])
            context.user_data["semestr"] -= 1
            query.edit_message_text("Ваш рейтинг", reply_markup=InlineKeyboardMarkup(keyboard))
    elif data == "right_rating":
        semestr = context.user_data["semestr"]
        if semestr + 1 <= len(dic_semestrs):

            user = getID(query, context)
            response = getRating(user.skgmi_id)
            keyboard = [[InlineKeyboardButton(dic_semestrs[semestr + 1], callback_data="show_semestrs_rating")],
                        [InlineKeyboardButton("<=", callback_data="left_rating"),
                         InlineKeyboardButton("=>", callback_data="right_rating")],
                        [InlineKeyboardButton("Предмет | Контроль | Рейтинг ", callback_data="No")]]
            for i in response:
                if i["Term"] == dic_semestrs[semestr + 1]:
                    keyboard.append([InlineKeyboardButton(
                        i["SubjectName"] + " | " + str(i["RatingControl_1"]) + " | " + str(i["CurrentControl_1"]),
                        callback_data="No")])
            context.user_data["semestr"] += 1
            query.edit_message_text("Ваш рейтинг", reply_markup=InlineKeyboardMarkup(keyboard))
    elif data == "back_to_watch_calendar_days":
        query.delete_message()
        watch(query, context)
    elif data == "cancel":
        query.edit_message_text("Просмотр расписания отменён")

def inputSKGMIID(update, context):
    text = update.message.text
    response = genarateCodeAndSendOnEmail(update.message.text)
    if response == 200:
        is_provered = 1
        context.user_data["SKGMI.ID"] = update.message.text
    else:
        is_provered = 0
    if is_provered:
        update.message.reply_text("Вам на почту прислали код")
        update.message.reply_text("Впишите его")
        update.message.reply_text("Пример: 124515")
        return 2
    else:
        update.message.reply_text("Неправильный SKGMI.ID")
        update.message.reply_text("Регистрация отменена")
        return ConversationHandler.END

def reg(update, context):
    code = update.message.text
    message_about_searching = update.message.reply_text("Идёт проверка....")
    response = ValidateCode(context.user_data["SKGMI.ID"], code, update.message.chat_id)
    message_about_searching.delete()
    if response == 200:
        sess = db_session.create_session()
        new_user = User()
        new_user.id = update.message.chat_id
        new_user.skgmi_id = context.user_data["SKGMI.ID"]
        sess.add(new_user)
        sess.commit()
        context.user_data["user"] = new_user
        sess.expunge_all()
        sess.close()
        update.message.reply_text("Вы успешно зарегистрировались")

    else:
        update.message.reply_text("Неверный код")
        update.message.reply_text("Регистрация отменена")
    return ConversationHandler.END



def find_id(update, context):
    update.message.reply_text("Введите ФИО через пробел\n"
                              "(Напишите /cancel для отмены)")
    return 1


def find_FIO(update, context):
    update.message.reply_text("Введите SKGMI.ID")
    update.message.reply_text("Чтобы отменить - /cancel")
    return 1


def backFIO(update, context):
    try:
        if update.message.text == "/cancel":
            update.message.reply_text("Отмена")
            return ConversationHandler.END
        skgmi_id = update.message.text
        response = getUserName(skgmi_id)
        message_about_searching = update.message.reply_text("Идёт поиск..")
        message_about_searching.delete()
        update.message.reply_text(response["DisplayName"])
        return ConversationHandler.END
    except Exception:
        update.message.reply_text("Такого пользователя не найдено")
        update.message.reply_text("Попробуйте снова")
        return 1


def backSKGMI(update, context):
    try:
        if update.message.text == "/cancel":
            update.message.reply_text("Отмена")
            return ConversationHandler.END
        fio = update.message.text
        response = getSkgmiIdFIO(fio)
        message_about_searching = update.message.reply_text("Идёт поиск..")
        update.message.reply_text(response["Username"])
        message_about_searching.delete()
        return ConversationHandler.END
    except Exception:
        update.message.reply_text("Такого пользователя не найдено")
        update.message.reply_text("Попробуйте снова")
        return 1


def myRating(update, context):
    t = check_on_registration_in_bot(update, context)
    if t:
        user = getID(update, context)
        this_user = getUserName(user.skgmi_id)
        if this_user["IsStudent"]:
            update.message.reply_text("Чтобы выбрать семестр из списка нажмите на кнопку показывающую индефикатор семестров")
            # if True:
            rating = getRating(user.skgmi_id)
            print(rating)
            keyboard = [[InlineKeyboardButton("Первый семестр", callback_data="show_semestrs_rating")],
                        [InlineKeyboardButton("<=", callback_data="left_rating"),
                         InlineKeyboardButton("=>", callback_data="right_rating")],
                        [InlineKeyboardButton("Предмет | Контроль | Рейтинг ", callback_data="No")]]
            context.user_data["semestr"] = 1
            for i in rating:
                if i["Term"] == "Первый семестр":
                    keyboard.append([InlineKeyboardButton(
                        i["SubjectName"] + " | " + str(i["RatingControl_1"]) + " | " + str(i["CurrentControl_1"]),
                        callback_data="No")])

            markup = InlineKeyboardMarkup(keyboard)
            update.message.reply_text("Ваш рейтинг", reply_markup=markup)
        else:
            update.message.reply_text("Вы не студент")
    else:
        update.message.reply_text("Вы не зарегистрированы")


def get_sess(update, context):
    t = check_on_registration_in_bot(update, context)
    if t:
        keyboard = [[InlineKeyboardButton("Первый семестр", callback_data="show_semestrs_sess")],
                    [InlineKeyboardButton("<=", callback_data="left_sess"),
                     InlineKeyboardButton("=>", callback_data="right_sess")],
                    [InlineKeyboardButton("Предмет | Тип | Оценка", callback_data="No")]]

        user = getID(update, context)
        this_user = getUserName(user.skgmi_id)
        t = update.message.reply_text("Получение данных...")
        if this_user["IsStudent"]:
            update.message.reply_text("Чтобы выбрать семестр из списка нажмите на кнопку показывающую индефикатор семестров")
            response = getSession(this_user["Username"])
            context.user_data["session"] = 1
            for i in response:
                if i["Term"] == "Первый семестр":
                    button = InlineKeyboardButton(f"""{i["Subject"]}|{i["TypeOfTheControl"]}|{i["Mark"]}""",
                                                  callback_data="No")
                    keyboard.append([button])
            markup = InlineKeyboardMarkup(keyboard)
            t.delete()
            context.user_data["semestr"] = 1
            update.message.reply_text("Оценки за сессию", reply_markup=markup)
        else:
            update.message.reply_text("Вы не студент")
    else:
        update.message.reply_text("Вы не зарегистрированы")


def handle_docs_photo(update, context):
    if update.message.text == "/cancel":
        update.message.reply_text("Отмена")
    if update.message.text == "/skip":
        response = addRecord(context.user_data["text"], context.user_data["head"], getID(update, context).skgmi_id,
                             using_file=False)
        update.message.reply_text("Достижение добавлено", reply_markup=commands)
        return ConversationHandler.END
    file_id = update.message.photo[-1].file_id
    newFile = context.bot.get_file(file_id)
    newFile.download('diplom.png')
    response = addRecord(context.user_data["text"], context.user_data["head"], getID(update, context).skgmi_id,
                         using_file=True)
    update.message.reply_text("Достижение добавлено", reply_markup=commands)
    return ConversationHandler.END


def diplom_start(update, context):
    t = check_on_registration_in_bot(update, context)
    if t:

        user = getID(update, context)
        this_user = getUserName(user.skgmi_id)
        # if this_user["IsStudent"]:
        if True:
            update.message.reply_text("Введите заголовок достижения")
            update.message.reply_text("Для отмены - /cancel")
            return 1
        else:
            update.message.reply_text("Вы не студент")
            return ConversationHandler.END
    else:
        update.message.reply_text("Вы не зарегистрированы")
        return ConversationHandler.END


def diplom_header(update, context):
    if update.message.text != "/cancel":
        context.user_data["head"] = update.message.text
        update.message.reply_text("Введите описание достижения")
        return 2
    else:

        update.message.reply_text("Отмена")


keyboard_with_skip = ReplyKeyboardMarkup([["/skip"]])


def diplom_text(update, context):
    context.user_data["text"] = update.message.text
    update.message.reply_text("Пришли фотографию достижения")
    update.message.reply_text("Для пропуска этого этапа - /skip")
    return 3


def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CallbackQueryHandler(callback=keyboard_buttons_query))
    registration = ConversationHandler(
        entry_points=[CommandHandler('reg', start_new_reg)],
        states={
            1: [MessageHandler(Filters.text, inputSKGMIID)],
            2: [MessageHandler(Filters.text, reg)]
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )
    find_skgmi_id_from_FIO = ConversationHandler(
        entry_points=[CommandHandler('getID', find_id)],
        states={
            1: [MessageHandler(Filters.text, backSKGMI)]
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )
    find_fio = ConversationHandler(
        entry_points=[CommandHandler('getFIO', find_FIO)],
        states={
            1: [MessageHandler(Filters.text, backFIO)]
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )
    file_proverka = ConversationHandler(
        entry_points=[CommandHandler('add_ach', diplom_start)],
        states={
            1: [MessageHandler(Filters.all, diplom_header)],
            2: [MessageHandler(Filters.all, diplom_text)],
            3: [MessageHandler(Filters.all, handle_docs_photo)]
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )
    dp.add_handler(registration)

    dp.add_handler(find_skgmi_id_from_FIO)
    dp.add_handler(find_fio)
    dp.add_handler(file_proverka)
    dp.add_handler(CommandHandler("timetable", watch_lessons))
    dp.add_handler(CommandHandler("sess", get_sess))
    dp.add_handler(CommandHandler("rating", myRating))
    dp.add_handler(CommandHandler("logout", logout))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("myId", myId))
    dp.add_handler(CommandHandler("start", start))

    updater.start_polling()
    updater.idle()


# @Тимур Добрый день, создали для вас пользователя в нашей системе управления проектами.
# Сайт - https://devops.expasys.online/DefaultCollection
# логин - EXPASYS\chatbot
# пароль - FL$pn*vn
# репозиторий - https://devops.expasys.online/DefaultCollection/_git/EIOS_ChatBot
# Репозиторий не инициализирован, чтобы вы могли сразу запушить существующий.
if __name__ == '__main__':
    db_session.global_init("db/blogs.db")
    main()
