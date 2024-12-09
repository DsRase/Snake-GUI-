import telebot

TOKEN = None

bot = telebot.TeleBot(TOKEN)

is_bot_working = True

@bot.message_handler(content_types=["text"])
def get_text_messages(message):
    global is_bot_working
    if message.text == "/stop":
        is_bot_working = False
    bot.send_message(message.from_user.id, "ИДИ НАХУЙ!")

bot.polling(none_stop=is_bot_working, interval=0)
