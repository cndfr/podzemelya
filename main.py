import re
import telebot
import shelve

bot = telebot.TeleBot('***REMOVED***')

with open('base.txt', newline='') as source:
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
    with shelve.open('userdata', 'w') as userdata:
        userdata[f'{id}'] = character

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
    with shelve.open('userdata', 'w') as userdata:
        profile = userdata[f'{id}']
        profile['moves'] = [int(move) for move in re.findall(r'\b\d+\b', text)]
        userdata[f'{id}'] = profile

# items

# fights


def generate_answer(message):
    if not message.text.isnumeric():
        return 'Введите номер страницы'
    reqpage = int(message.text)
    if not (reqpage > 0 and reqpage <= 617):
        return 'Такой страницы нет'
    with shelve.open('userdata', 'r') as userdata:
        profile = userdata[f'{message.from_user.id}']
        moves = profile['moves']
    if reqpage not in moves:
        return 'Вы не можете сюда попасть'
    if reqpage == moves[0]:
        return 'Вы сейчас здесь'

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
    with shelve.open('userdata', 'r') as userdata:
        entry = userdata[f'{message.from_user.id}']
    bot.send_message(
        message.chat.id, f'{message.from_user.id} \r\nUserdata: {entry}', parse_mode='Html')


@bot.message_handler()
def get_user_text(message):
    bot.send_message(
        message.chat.id, generate_answer(message), parse_mode='Html')


bot.polling(non_stop=True)
