import re
import telebot
import shelve
import pickle

bot = telebot.TeleBot('5752337489:AAGabYmTALazbxrgIVbkoyS2LFNSxHZjSf0')

with open('/Users/cndfr/Library/Mobile Documents/com~apple~CloudDocs/DEV/Podzemelya/base.txt', newline='') as source:
    pages = source.readlines()


# players


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

    # with open("/Users/cndfr/Library/Mobile Documents/com~apple~CloudDocs/DEV/Podzemelya/data.pickle", "wb") as userdata:
    #     pickle.dump(character, userdata, protocol=pickle.HIGHEST_PROTOCOL)
    # with shelve.open('/Users/cndfr/Library/Mobile Documents/com~apple~CloudDocs/DEV/Podzemelya/userdata.dat', 'w') as userdata:
    #     userdata[id] = character

# pages -------------- restriction ------------- add exclusions


# def create_page(i):
#     page = {
#         'items': '',
#         'fight': False,
#         'secmoves': '',
#         'text': 'Вы быстро идете вперед — 3.',
#     }
#     global pages
#     pages[i] = page


def get_moves(id, text):
    global players
    players[id]['moves'] = [int(move) for move in re.findall(r'\b\d+\b', text)]

# items

# fights


def generate_answer(message):
    if not message.text.isnumeric():
        return 'Введите номер страницы'
    reqpage = int(message.text)
    if not (reqpage > 0 and reqpage <= 617):
        return 'Такой страницы нет'
    if reqpage not in players[message.from_user.id]['moves']:
        return 'Вы не можете сюда попасть'

    text = pages[reqpage].replace('<br>', '\r\n')
    get_moves(message.from_user.id, text)
    return f'{text}'


@bot.message_handler(commands=['start'])
def start(message):
    create_character(message.from_user.id)
    get_moves(message.from_user.id, pages[1])
    text = pages[1].replace('<br>', '\r\n')
    bot.send_message(
        message.chat.id, text, parse_mode='Html')


@bot.message_handler(commands=['debug'])
def debug(message):
    bot.send_message(
        message.chat.id, f'Players: {players}', parse_mode='Html')


@bot.message_handler()
def get_user_text(message):
    bot.send_message(
        message.chat.id, generate_answer(message), parse_mode='Html')


bot.polling(non_stop=True)
