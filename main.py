import telebot
import re

bot = telebot.TeleBot('***REMOVED***')

with open('/Users/cndfr/Library/Mobile Documents/com~apple~CloudDocs/DEV/Podzemelya/base.txt', newline='') as source:
    pages = source.readlines()

# page restriction & exclusions
moves = []


def get_moves(text):
    global moves
    moves = [int(move) for move in re.findall(r'\b\d+\b', text)]


# player
players = []


def create_character(id):
    character = {
        'id': id,
        'stats': 0,
        'items': 0,
        'spells': 0,
        'moves': 0,
    }
    global players
    players.append(character)

# items

# fights


def generate_answer(message):
    if message.text.isnumeric():
        reqpage = int(message.text)
        if reqpage > 0 and reqpage <= 617:
            text = pages[reqpage].replace('/', '\r\n')
            if reqpage in moves:
                global players
                players[message.from_user.id] = get_moves(text)
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
    get_moves(pages[1])
    bot.send_message(
        message.chat.id, f'{pages[1]} Players: {players}', parse_mode='Markdown')


@bot.message_handler()
def get_user_text(message):
    bot.send_message(
        message.chat.id, f'{generate_answer(message)}', parse_mode='Markdown')


bot.polling(non_stop=True)
