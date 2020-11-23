import telebot

from hash_sum_checker import check_hash_sum

bot = telebot.TeleBot('1408332480:AAGiZrfqhIXzCemZ30ZvrmwSOeJnee5Zyb0')


@bot.message_handler(commands=['start'])
def send_message(message):
    bot.send_message(message.chat.id, 'Enter URL for check hashsum of HTML tags')


@bot.message_handler()
def send_message(message):
    if message.text.startswith('http'):
        bot.send_message(message.chat.id, check_hash_sum(message.text))
    else:
        bot.send_message(message.chat.id, 'Invalid URL')


bot.polling(none_stop=True)
