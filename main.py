import re
import telebot
import shelve
import random

bot = telebot.TeleBot('5752337489:AAGabYmTALazbxrgIVbkoyS2LFNSxHZjSf0')

with open('base.txt', newline='') as source:
    pages = source.readlines()

# DICE


def roll(dices):
    result = 0
    for dice in range(dices):
        result += random.randint(1, 6)
    return result

# PLAYERS

# ['левитация', 'огонь', 'иллюзия', 'сила', 'слабость', 'копия', 'исцеление', 'плавание']


def create_character(id):
    character = {
        'skill': roll(1) + 6,
        'vigor': roll(2) + 12,
        'luck': roll(1) + 6,
        'gold': 15,
        'water': 2,
        'items': '0/7',
        'spells': ['левитации', 'огня', 'иллюзии', 'силы', 'слабости', 'копии', 'исцеления', 'плавания'],
        'moves': 0,
    }
    with shelve.open('userdata', 'w') as userdata:
        userdata[id] = character

# PAGES ------------- add exclusions

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
        character = userdata[id]
        character['moves'] = [int(move)
                              for move in re.findall(r'\b\d+\b', text)]
        userdata[id] = character

# ITEMS

# FIGHTS

# ANSWER


def generate_answer(message):
    if not message.text.isnumeric():
        return 'Введите номер страницы'
    reqpage = int(message.text)
    if not (reqpage > 0 and reqpage <= 617):
        return 'Такой страницы нет'
    with shelve.open('userdata', 'r') as userdata:
        character = userdata[f'{message.from_user.id}']
        moves = character['moves']
    if reqpage not in moves:
        return 'Вы не можете сюда попасть'
    if reqpage == moves[0]:
        return 'Вы сейчас здесь'

    text = pages[reqpage].replace('<br>', '\r\n')
    get_moves(f'{message.from_user.id}', text)
    return f'{text}'

# COMMANDS

# start - рестарт
# char - персонаж


@bot.message_handler(commands=['start'])
def start(message):
    create_character(f'{message.from_user.id}')
    bot.send_message(
        message.chat.id, f'<b>Старт игры</b> \r\nСоздание нового героя', parse_mode='Html')
    char(message)
    get_moves(f'{message.from_user.id}', pages[1])
    text = pages[1].replace('<br>', '\r\n')
    bot.send_message(
        message.chat.id, text, parse_mode='Html')


@bot.message_handler(commands=['char'])
def char(message):
    with shelve.open('userdata', 'r') as userdata:
        char = userdata[f'{message.from_user.id}']
        char = userdata[f'{message.from_user.id}']
        skill = char['skill']
        vigor = char['vigor']
        luck = char['luck']
        gold = char['gold']
        water = char['water']
        items = char['items']
        spells = char['spells']
    bot.send_message(
        message.chat.id, f'Ваш герой: \r\n🗡 Мастерство: {skill} \r\n🫀 Выносливость: {vigor} \r\n☀️ Удача: {luck} \r\n💰 Деньги: {gold} \r\n💧 Вода: {water} \r\n📦 Вещи: {items} \r\n✨ Заклинания: {spells}', parse_mode='Html')


@bot.message_handler(commands=['debug'])
def debug(message):
    with shelve.open('userdata', 'r') as userdata:
        char = userdata[f'{message.from_user.id}']
    bot.send_message(
        message.chat.id, f'{message.from_user.id} \r\nUserdata: {char}', parse_mode='Html')

# MESSAGE


@bot.message_handler()
def get_user_text(message):
    bot.send_message(
        message.chat.id, generate_answer(message), parse_mode='Html')


bot.polling(non_stop=True)
