import re
import telebot

bot = telebot.TeleBot('***REMOVED***')

with open('/Users/cndfr/Library/Mobile Documents/com~apple~CloudDocs/DEV/Podzemelya/base.txt', newline='') as source:
    pages = source.readlines()

# page restriction & exclusions


def get_moves(id, text):
    global players
    players[id]['moves'] = [int(move) for move in re.findall(r'\b\d+\b', text)]

# player


players = {}


def create_character(id):
    character = {
        'stats': 0,
        'items': 0,
        'spells': 0,
        'moves': 0,
    }
    global players
    players[id] = character

# items

# fights


def generate_answer(message):
    if message.text.isnumeric():
        reqpage = int(message.text)
        if reqpage > 0 and reqpage <= 617:
            if reqpage in players[message.from_user.id]['moves']:
                text = pages[reqpage].replace('/', '\r\n')       # remove this
                get_moves(message.from_user.id, text)
                return f'{text}'
            else:
                return 'Вы не можете сюда попасть'
        else:
            return 'Такой страницы нет'
    else:
        return 'Введите номер страницы'


@bot.message_handler(commands=['start'])
def start(message):
    create_character(message.from_user.id)
    get_moves(message.from_user.id, pages[1])
    text = pages[1].replace('/', '\r\n')                         # remove this
    bot.send_message(
        message.chat.id, text, parse_mode='Markdown')


@bot.message_handler(commands=['debug'])
def debug(message):
    bot.send_message(
        message.chat.id, f'Players: {players}', parse_mode='Markdown')


@bot.message_handler()
def get_user_text(message):
    bot.send_message(
        message.chat.id, generate_answer(message), parse_mode='Markdown')


bot.polling(non_stop=True)
