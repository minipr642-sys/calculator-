import os
from flask import Flask, request
import telebot
from telebot import types

app = Flask(__name__)
TOKEN = "8482581885:AAFZieNXTVZKHLQOjgXeyMysBTIebSOoiSE"  # Your API key
bot = telebot.TeleBot(TOKEN)
URL = f"https://{os.environ.get('RENDER_EXTERNAL_HOSTNAME', 'your-app.onrender.com')}/{TOKEN}"

def calculate(operation, a, b):
    if operation == "add": return a + b
    if operation == "subtract": return a - b
    if operation == "multiply": return a * b
    if operation == "divide": return a / b if b != 0 else "Error: Division by zero!"
    return "Invalid operation"

@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return 'OK', 200

@app.route('/')
def index():
    bot.remove_webhook()
    bot.set_webhook(url=URL)
    return 'Webhook set!'

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Add", callback_data="add"),
               types.InlineKeyboardButton("Subtract", callback_data="subtract"))
    markup.add(types.InlineKeyboardButton("Multiply", callback_data="multiply"),
               types.InlineKeyboardButton("Divide", callback_data="divide"))
    bot.reply_to(message, "Choose an operation:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    bot.answer_callback_query(call.id)
    msg = bot.send_message(call.message.chat.id, "Enter first number:")
    bot.register_next_step_handler(msg, process_first_number, call.data)

def process_first_number(message, operation):
    try:
        a = float(message.text)
        msg = bot.send_message(message.chat.id, "Enter second number:")
        bot.register_next_step_handler(msg, process_second_number, operation, a)
    except ValueError:
        bot.reply_to(message, "Please enter a valid number!")

def process_second_number(message, operation, a):
    try:
        b = float(message.text)
        result = calculate(operation, a, b)
        bot.reply_to(message, f"Result: {result}")
    except ValueError:
        bot.reply_to(message, "Please enter a valid number!")
    except Exception as e:
        bot.reply_to(message, str(e))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
