#Импортирование библиотек
import telebot
import qrcode
from telebot import types
from config import bot_token
import cv2
import os


#Cоздание бота
bot = telebot.TeleBot(bot_token)


qr = qrcode.QRCode()
qr_file_name = 'ready_qr.png'


#Создание клавиатуры
markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
generate_qr_button = types.KeyboardButton('/Сгенерировать_qr')
read_qr_button = types.KeyboardButton('/Прочитать_qr')
FAQ_qr_button = types.KeyboardButton('/FAQ')
markup.add(generate_qr_button, read_qr_button, FAQ_qr_button)


#Приветствие пользователя при команде /start
@bot.message_handler(commands=['start'])
def meet_user(message):
    bot.send_message(message.from_user.id, f"Привет, {message.chat.username}!", reply_markup=markup)


#Начало генерации qr, по команде /Сгенерировать qr
@bot.message_handler(commands=['Сгенерировать_qr'])
#Обращениек пользователю, с целью получить данные для генерации qr
def qr_command_reaction(message):
    msg = bot.send_message(message.chat.id, "Введи текст, url", reply_markup=markup)
    bot.register_next_step_handler(msg, generate_qr)


#Создание qr по введёным данным
def generate_qr(message):
    text = message.text
    qr.add_data(text)
    image = qr.make_image()
    image.save('ready_qr.jpg', "JPEG")
    qr.clear()
    bot.send_message(message.chat.id, f"QRcode cо следующими данными:\n{text}", reply_markup=markup)
    p = open('ready_qr.jpg', 'rb')
    bot.send_photo(message.chat.id, p, reply_markup=markup)


#Выдача пользователю справочной информации
@bot.message_handler(commands=['FAQ'])
def help_for_user(message):
    bot.send_message(message.chat.id, "Я QRcode_bot!\nЯ призван помочь людям. Могу создавать qrcode, а в будущем смогу их распозновать.")


#Считывание qr с фото
@bot.message_handler(commands=['Прочитать_qr'])
def ask_qr_image(message):
    msg = bot.send_message(message.chat.id, "Отправь сообщение с qr кодом\n\n!Важно!\nВ данный момент считываются только qr-коды с изображений, а не с фотографий")
    bot.register_next_step_handler(msg, get_qr_message)

def get_qr_message(message):
    try:
        qr_to_read = bot.get_file(message.photo[0].file_id)
        filename, file_extension = os.path.splitext(qr_to_read.file_path)

        downloaded_file_photo = bot.download_file(qr_to_read.file_path)
        src = '/photos' + qr_to_read.file_id + file_extension
        with open(src, 'wb') as new_file:
            new_file.write(downloaded_file_photo)

        img = cv2.imread(src)

        detector = cv2.QRCodeDetector()
        data, bbox, clear_qr = detector.detectAndDecode(img)
        print(data)
        bot.send_message(message.chat.id, f"Содержимое qrcode: \n{data}")
    except:
        bot.send_message(message.chat.id, """Полученное сообщение не является изображением.\n""")








if __name__ == '__main__':
    bot.polling()
