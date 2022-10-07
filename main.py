import re
import telebot
import shelve
import random
import linecache
import json

bot = telebot.TeleBot('***REMOVED***')

# DICE


def roll(dices):
    result = 0
    for dice in range(dices):
        result += random.randint(1, 6)
    return result

# HEROES


def create_character(id):
    character = {
        'name': linecache.getline('names.txt', random.randint(0, 158)).replace("\n", ""),
        'skill': roll(1) + 6,
        'vigor': roll(2) + 12,
        'luck': roll(1) + 6,
        'gold': 15,
        'water': 2,
        'items': '0/7',
        'spells': 'левитации, огня, иллюзии, силы, слабости, копии, исцеления, плавания',
        'paragraph': 0,
        'moves': [1],
    }
    with shelve.open('userdata', 'w') as userdata:
        userdata[id] = character

# PAGES ------------- add exclusions


def generate_paragraph(reqpage):
    with open('base.txt', 'r') as book:
        lines = book.readlines()
        paragraph = json.loads(lines[reqpage])
    return paragraph


def uncode_text(paragraph):
    text = str(paragraph['id']) + '. ' + \
        paragraph['text'].replace('<br>', '\r\n').replace('<q>', '\"')
    return text


def set_moves(id, paragraph):
    with shelve.open('userdata', 'w') as userdata:
        character = userdata[id]
        character['moves'] = [int(move)
                              for move in re.findall(r'\b\d+\b', paragraph['text'])]
        character['paragraph'] = paragraph['id']
        userdata[id] = character

# ITEMS

# FIGHTS

# COMMANDS

# start - рестарт
# hero - герой


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id, f'<b>Старт игры</b> \r\nСоздание нового героя', parse_mode='Html')
    create_character(f'{message.from_user.id}')
    hero(message)

    paragraph = generate_paragraph(1)
    text = uncode_text(paragraph)

    set_moves(f'{message.from_user.id}', paragraph)
    bot.send_message(
        message.chat.id, text, parse_mode='Html')


@bot.message_handler(commands=['hero'])
def hero(message):
    char = 0
    with shelve.open('userdata', 'r') as userdata:
        char = userdata[f'{message.from_user.id}']
        name = char['name']
        skill = char['skill']
        vigor = char['vigor']
        luck = char['luck']
        gold = char['gold']
        water = char['water']
        items = char['items']
        spells = char['spells']
    bot.send_message(
        message.chat.id, f'<b>Ваш герой — {name}:</b> \r\n🗡 Мастерство: {skill} \r\n🫀 Выносливость: {vigor} \r\n☀️ Удача: {luck} \r\n💰 Деньги: {gold} \r\n💧 Вода: {water} \r\n📦 Вещи: {items} \r\n✨ Заклинания: {spells}', parse_mode='Html')


@bot.message_handler(commands=['debug'])
def debug(message):
    with shelve.open('userdata', 'r') as userdata:
        char = userdata[f'{message.from_user.id}']
    bot.send_message(
        message.chat.id, f'{message.from_user.id} \r\nUserdata: {char}', parse_mode='Html')

# MESSAGE


@bot.message_handler()
def get_user_text(message):
    if not message.text.isnumeric():
        return 'Введите номер страницы'
    reqpage = int(message.text)
    if not (reqpage > 0 and reqpage <= 617):
        return 'Такой страницы нет'
    with shelve.open('userdata', 'r') as userdata:
        character = userdata[f'{message.from_user.id}']
    if reqpage == character['paragraph']:
        return 'Вы сейчас здесь'
    if reqpage not in character['moves']:
        return 'Вы не можете сюда попасть'

    paragraph = generate_paragraph(reqpage)
    text = uncode_text(paragraph)
    set_moves(f'{message.from_user.id}', paragraph)

    bot.send_message(
        message.chat.id, text, parse_mode='Html')


bot.polling(non_stop=True)
