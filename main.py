# Импортируем необходимые классы.

from telegram import ReplyKeyboardMarkup
from telegram.ext import Updater, MessageHandler, Filters, ConversationHandler
import sqlalchemy

from data import db_session

TOKEN = "5202082113:AAGXyFL-I9Q1j-Nne1YRY7mawvKCdKlDIqY"
# Добавим необходимый объект из модуля telegram.ext
from telegram.ext import CommandHandler
reply_keyboard = []
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
t = True



def help(update, context):
    update.message.reply_text(
        "Здравствуйте я ваш ассистент по расписанию в вашем ВУЗЕ. Чем могу быть полезен?")


def start(update, context):
    update.message.reply_text(
        "Привет. Пройдите небольшой опрос, пожалуйста!\n"
        "Вы можете прервать опрос, послав команду /stop.\n"
        "В каком городе вы живёте?")

    # Число-ключ в словаре states —
    # втором параметре ConversationHandler'а.
    return 1
    # Оно указывает, что дальше на сообщения от этого пользователя
    # должен отвечать обработчик states[1].
    # До этого момента обработчиков текстовых сообщений
    # для этого пользователя не существовало,
    # поэтому текстовые сообщения игнорировались.


def first_response(update, context):
    # Это ответ на первый вопрос.
    # Мы можем использовать его во втором вопросе.
    locality = update.message.text
    update.message.reply_text(
        f"Какая погода в городе {locality}?")
    # Следующее текстовое сообщение будет обработано
    # обработчиком states[2]
    return 2
def logout():
    pass

def second_response(update, context):
    # Ответ на второй вопрос.
    # Мы можем его сохранить в базе данных или переслать куда-либо.
    weather = update.message.text
    update.message.reply_text("Спасибо за участие в опросе! Всего доброго!")
    return ConversationHandler.END  # Константа, означающая конец диалога.
    # Все обработчики из states и fallbacks становятся неактивными.


# def start(update, context):
#     update.message.reply_text(
#         "Я ассистент по распианию. И вот мои команды:\n",
#         reply_markup=markup
#     )


def replace(update, context):
    print(context)
def start_reg(update, context):
    update.message.reply_text("Регистрация на сайте !Название сайта!")

# Определяем функцию-обработчик сообщений.
# У неё два параметра, сам бот и класс updater, принявший сообщение.
# def echo(update, context):
#     У объекта класса Updater есть поле message,
#     являющееся объектом сообщения.
#     У message есть поле text, содержащее текст полученного сообщения,
#     а также метод reply_text(str),
#     отсылающий ответ пользователю, от которого получено сообщение.
    # text = update.message.text
    # update.message.reply_text("Неопознанная команда чтобы узнать о всех командах бота напишите команду /help")
def cancel(update, context):
    update.message.reply_text("Дайте немного времени мы проверим ваши данные.")


def main():
    # Создаём объект updater.
    # Вместо слова "TOKEN" надо разместить полученный от @BotFather токен
    updater = Updater(TOKEN, use_context=True)

    # Получаем из него диспетчер сообщений.
    dp = updater.dispatcher

    # Создаём обработчик сообщений типа Filters.text
    # из описанной выше функции echo()
    # После регистрации обработчика в диспетчере
    # эта функция будет вызываться при получении сообщения
    # с типом "текст", т. е. текстовых сообщений.
    # text_handler = MessageHandler(Filters.text, echo)
    # Зарегистрируем их в диспетчере рядом
    # с регистрацией обработчиков текстовых сообщений.
    # Первым параметром конструктора CommandHandler я
    # вляется название команды.
    # dp.add_handler(CommandHandler("help", help))
    # dp.add_handler(CommandHandler("replace", replace))
    registration = ConversationHandler(
        # Точка входа в диалог.
        # В данном случае — команда /start. Она задаёт первый вопрос.
        entry_points=[CommandHandler('reg', start_reg)],

        # Состояние внутри диалога.
        # Вариант с двумя обработчиками, фильтрующими текстовые сообщения.
        states={
            # Функция читает ответ на первый вопрос и задаёт второй.
            1: [MessageHandler(Filters.text, first_response)],
            # Функция читает ответ на второй вопрос и завершает диалог.
            2: [MessageHandler(Filters.text, second_response)]
        },

        # Точка прерывания диалога. В данном случае — команда /stop.
        fallbacks=[CommandHandler('stop', cancel)]
    )
    dp.add_handler(registration)
    # Регистрируем обработчик в диспетчере.
    # dp.add_handler(text_handler)
    # Запускаем цикл приема и обработки сообщений.
    updater.start_polling()

    # Ждём завершения приложения.
    # (например, получения сигнала SIG_TERM при нажатии клавиш Ctrl+C)
    updater.idle()


# Запускаем функцию main() в случае запуска скрипта.
if __name__ == '__main__':
    db_session.global_init("db/blogs.db")
    main()
