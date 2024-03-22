import sys
import telebot
import cv2
import psycopg2
from pyzbar.pyzbar import decode
from telebot import types


db_name = sys.argv[1]
db_user = sys.argv[2]
db_password = sys.argv[3]

BUTTONS = (
    "Сканировать QR-код книги",
    "Добавить книгу",
    "Удалить книгу"
)

bot = telebot.TeleBot("6385036893:AAHsvWGsVlCnpMyTy7QaNZbIVxnwz2eJS2M")

button_1 = types.KeyboardButton(
    text="Сканировать QR-код книги"
)

button_2 = types.KeyboardButton(
    text="Добавить книгу"
)

button_3 = types.KeyboardButton(
    text="Удалить книгу"
)

button_4 = types.KeyboardButton(
    text="Поиск книги"
)

keyboard = types.ReplyKeyboardMarkup()
keyboard.add(button_1, button_2, button_3, button_4)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Добро пожаловать!", reply_markup=keyboard)


@bot.message_handler(commands=['create'])
def handle_create(message):
    if len(message.text.split()) != 5:
        bot.reply_to(message, (
            "Не хватает данных для создания записи. "
            "Пожалуйста, используйте формат: "
            "/create Название_книги Автор_книги Жанр Год_публикации"
            )
        )
        return

    (command, title, author,
     genre, publication_year) = message.text.split(maxsplit=4)

    conn = psycopg2.connect(
        dbname=db_name,
        user=db_user,
        password=db_password,
        host="localhost"
    )
    cursor = conn.cursor()

    try:
        cursor.execute((
            "INSERT INTO books (title, author, genre, publication_year) "
            "VALUES (%s, %s, %s, %s)"
            ),
            (title, author, genre, publication_year)
        )
        conn.commit()
        bot.reply_to(
            message,
            "Данные успешно добавлены",
            reply_markup=keyboard
        )
    except Exception as e:
        bot.reply_to(message, f"Произошла ошибка: {e}", reply_markup=keyboard)

    cursor.close()
    conn.close()


def handle_create_2(message):
    if len(message.text.split()) != 4:
        bot.reply_to(message, (
            "Не хватает данных для создания записи. "
            "Пожалуйста, используйте формат: "
            "Название_книги Автор_книги Жанр Год_публикации"
            ),
            reply_markup=keyboard
        )
        return

    (title, author,
     genre, publication_year) = message.text.split(maxsplit=4)

    conn = psycopg2.connect(
        dbname=db_name,
        user=db_user,
        password=db_password,
        host="localhost"
    )
    cursor = conn.cursor()

    try:
        cursor.execute((
            "INSERT INTO books (title, author, genre, publication_year) "
            "VALUES (%s, %s, %s, %s)"
            ),
            (title, author, genre, publication_year)
        )
        conn.commit()
        bot.reply_to(
            message,
            "Данные успешно добавлены",
            reply_markup=keyboard
        )
    except Exception as e:
        bot.reply_to(message, f"Произошла ошибка: {e}", reply_markup=keyboard)

    cursor.close()
    conn.close()


@bot.message_handler(commands=['delete'])
def handle_delete(message):
    if len(message.text.split()) < 2:
        bot.reply_to(message, (
            "Необходимо указать параметр для удаления книги. "
            "Пожалуйста, используйте формат: /delete Название_книги"
            )
        )
        return

    command, title = message.text.split(maxsplit=1)

    conn = psycopg2.connect(
        dbname=db_name,
        user=db_user,
        password=db_password,
        host="localhost"
    )
    cursor = conn.cursor()

    try:
        cursor.execute("DELETE FROM books WHERE title = %s", (title,))
        conn.commit()

        if cursor.rowcount > 0:
            bot.reply_to(message, (
                f"Книга с названием '{title}' успешно удалена из базы данных."
                ),
                reply_markup=keyboard
            )
        else:
            bot.reply_to(message, (
                f"Книга с названием '{title}' не найдена в базе данных."
                ),
                reply_markup=keyboard
            )

    except Exception as e:
        bot.reply_to(message, (
            f"Произошла ошибка при удалении книги из базы данных: {e}"
            ),
            reply_markup=keyboard
        )

    cursor.close()
    conn.close()


def handle_delete_2(message):

    title = message.text

    conn = psycopg2.connect(
        dbname=db_name,
        user=db_user,
        password=db_password,
        host="localhost"
    )
    cursor = conn.cursor()

    try:
        cursor.execute("DELETE FROM books WHERE title = %s", (title,))
        conn.commit()

        if cursor.rowcount > 0:
            bot.reply_to(message, (
                f"Книга с названием '{title}' успешно удалена из базы данных."
                ),
                reply_markup=keyboard
            )
        else:
            bot.reply_to(message, (
                f"Книга с названием '{title}' не найдена в базе данных."
                ),
                reply_markup=keyboard
            )

    except Exception as e:
        bot.reply_to(message, (
            f"Произошла ошибка при удалении книги из базы данных: {e}"
            ),
            reply_markup=keyboard
        )

    cursor.close()
    conn.close()


@bot.message_handler(func=lambda message: message.text == "Удалить книгу")
def delete_button(message):
    mesg = bot.send_message(message.chat.id, 'Введите название книги')
    bot.register_next_step_handler(mesg, handle_delete_2)


@bot.message_handler(func=lambda message: message.text == "Поиск книги")
def find_button(message):
    mesg = bot.send_message(message.chat.id, 'Введите название книги')
    bot.register_next_step_handler(mesg, handle_search_text)


@bot.message_handler(func=lambda message: message.text == "Добавить книгу")
def add_button(message):
    mesg = bot.send_message(message.chat.id, (
        "Пожалуйста, используйте формат: "
        "Название_книги Автор_книги Жанр Год_публикации"
        )
    )
    bot.register_next_step_handler(mesg, handle_create_2)


@bot.message_handler(func=lambda message: message.text == "Сканировать QR-код книги")
@bot.message_handler(commands=['scan'])
def scan_qr(message):
    bot.send_message(message.chat.id, "Отправляй фото", reply_markup=keyboard)


@bot.message_handler(func=lambda message: True)
def handle_text_or_photo(message):
    if message.text:
        bot.send_message(message.chat.id, "Интерфейс", reply_markup=keyboard)
    elif message.photo:
        handle_search_photo(message)


@bot.message_handler(content_types=['photo'])
def handle_search_photo(message):
    photo_id = message.photo[-1].file_id
    file_info = bot.get_file(photo_id)
    downloaded_file = bot.download_file(file_info.file_path)
    with open("qr_code.jpg", 'wb') as new_file:
        new_file.write(downloaded_file)
    decoded_objects = decode(cv2.imread("qr_code.jpg"))
    if decoded_objects:
        qr_data = decoded_objects[0].data.decode('utf-8')

        conn = psycopg2.connect(
            dbname=db_name,
            user=db_user,
            password=db_password,
            host="localhost"
        )
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT * FROM books WHERE title = %s", (qr_data,))
            rows = cursor.fetchall()

            if len(rows) > 0:
                response = (
                    f"Найдены следующие книги с названием '{qr_data}':\n"
                )
                for row in rows:
                    response += (
                        f"Название: {row[1]}, Автор: {row[2]}, "
                        f"Жанр: {row[3]}, Год публикации: {row[4]}\n"
                    )
                bot.reply_to(message, response, reply_markup=keyboard)
            else:
                bot.reply_to(message, (
                    f"Книга с названием '{qr_data}' не найдена в базе данных."
                    ),
                    reply_markup=keyboard
                )

        except Exception as e:
            bot.reply_to(message, (
                f"Произошла ошибка при поиске книги в базе данных: {e}"
                ),
                reply_markup=keyboard
            )

        cursor.close()
        conn.close()
    else:
        bot.reply_to(
            message,
            "QR код не найден на фото",
            reply_markup=keyboard
        )


def handle_search_text(message):

    qr_data = message.text

    conn = psycopg2.connect(
        dbname=db_name,
        user=db_user,
        password=db_password,
        host="localhost"
    )
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT * FROM books WHERE title = %s", (qr_data,))
        rows = cursor.fetchall()

        if len(rows) > 0:
            response = f"Найдены следующие книги с названием '{qr_data}':\n"
            for row in rows:
                response += (
                    f"Название: {row[1]}, Автор: {row[2]}, "
                    f"Жанр: {row[3]}, Год публикации: {row[4]}\n"
                )
            bot.reply_to(message, response, reply_markup=keyboard)
        else:
            bot.reply_to(message, (
                f"Книга с названием '{qr_data}' не найдена в базе данных."
                ),
                reply_markup=keyboard
            )

    except Exception as e:
        bot.reply_to(message, (
            f"Произошла ошибка при поиске книги в базе данных: {e}"
            ),
            reply_markup=keyboard
        )

    cursor.close()
    conn.close()


bot.polling()
