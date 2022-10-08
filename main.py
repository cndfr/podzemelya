import re
import telebot
import shelve
import random
import linecache
import json
import time

bot = telebot.TeleBot('5752337489:AAGabYmTALazbxrgIVbkoyS2LFNSxHZjSf0')

# DICE


def roll(dices):
    result = 0
    for dice in range(dices):
        dice = random.randint(1, 6)
        result += dice
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
    # str(paragraph['id']) + '. ' + paragraph['text'].replace('<br>', '\r\n').replace('<q>', '\"')
    text = str(paragraph['id']) + '. ' + \
        paragraph['text'].replace('<br>', '\r\n').replace('<q>', '\"')
    return text


def set_moves(id, paragraph):
    with shelve.open('userdata', 'w') as userdata:
        character = userdata[id]
        character['moves'] = paragraph['moves']
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
        message.chat.id, f'<b>Старт игры</b> \r\n⏳ Создание нового героя...', parse_mode='Html')
    create_character(f'{message.from_user.id}')

    # time.sleep(3)

    hero(message)

    # time.sleep(3)

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
        if vigor == 0:
            name = '💀 ' + char['name']
        luck = char['luck']
        gold = char['gold']
        water = char['water']
        items = char['items']
        spells = char['spells']
    bot.send_message(
        message.chat.id, f'<b>Ваш герой — {name}:</b> \r\n🗡 Мастерство: {skill} \r\n🫀 Выносливость: {vigor} \r\n☀️ Удача: {luck} \r\n✨ Заклинания: {spells}', parse_mode='Html')
    # \r\n💰 <i>Деньги: {gold} \r\n💧 Вода: {water} \r\n📦 Вещи: {items}</i>


@bot.message_handler(commands=['debug'])
def debug(message):
    with shelve.open('userdata', 'r') as userdata:
        char = userdata[f'{message.from_user.id}']
    paragraph = generate_paragraph(char['paragraph'])
    bot.send_message(
        message.chat.id, f'{message.from_user.id} \r\n✨ Userdata: {char} \r\n✨ Paragraph: {paragraph}')

# MESSAGE


@bot.message_handler()
def get_user_text(message):
    if not message.text.isnumeric():
        bot.send_message(message.chat.id, 'Введите номер страницы')
        return
    reqpage = int(message.text)
    if not (reqpage > 0 and reqpage <= 618):
        bot.send_message(message.chat.id, 'Такой страницы нет')
        return
    with shelve.open('userdata', 'r') as userdata:
        hero = userdata[f'{message.from_user.id}']
    if hero['vigor'] == 0:
        bot.send_message(
            message.chat.id, 'Ваше путешествие закончено. Создайте нового героя - /start')
        return
    # if reqpage == hero['paragraph']:
    #     bot.send_message(message.chat.id, 'Вы сейчас здесь')
    #     return
    # if reqpage not in hero['moves']:
    #     bot.send_message(message.chat.id, 'Вы не можете сюда попасть')
    #     return

    paragraph = generate_paragraph(reqpage)
    text = uncode_text(paragraph)
    set_moves(f'{message.from_user.id}', paragraph)

    bot.send_message(
        message.chat.id, f'⏳ Открываю...', parse_mode='Html')

    # time.sleep(5)

    bot.send_message(
        message.chat.id, text, parse_mode='Html')

    if paragraph['event'] == 'fight':
        with shelve.open('userdata', 'r') as userdata:
            hero = userdata[f'{message.from_user.id}']
        foes = []
        text = ''

        for foe in paragraph['fight']:
            foes.append(foe)
            name = foe['name']
            skill = foe['skill']
            vigor = foe['vigor']
            text += f'{name} 🗡{skill} 🫀{vigor} \n'

        while any(foe['vigor'] > 0 for foe in foes):

            for foe in foes:
                if foe['vigor'] > 0:

                    name = foe['name']

                    hero_strike = roll(2) + hero['skill']
                    foe_strike = roll(2) + foe['skill']

                    strike = random.randint(1, 6)
                    if hero_strike == foe_strike:
                        text += f'\nВы промахнулись'
                    if hero_strike > foe_strike:
                        foe['vigor'] -= strike
                        text += f'\n{name}  \nВы ударили 💥{strike}'
                    if hero_strike < foe_strike:
                        hero['vigor'] -= strike
                        text += f'\n{name} \nНанес вам удар -🫀{strike}'
                    if foe['vigor'] <= 0:
                        text += f', и добили 💀'
                    text += '\n'

            if hero['vigor'] <= 0:
                hero['vigor'] = 0
                hero['moves'] = []
                text += '\n💀 Вы умерли'
                break

        if hero['vigor'] > 0:
            text += '\nВы победили в этом бою!'

        vigor = hero['vigor']
        moves = hero['moves']
        with shelve.open('userdata', 'w') as userdata:
            hero = userdata[f'{message.from_user.id}']
            hero['vigor'] = vigor
            hero['moves'] = moves
            userdata[f'{message.from_user.id}'] = hero
            # userdata[f'{message.from_user.id}'] = hero

        bot.send_message(
            message.chat.id, f'Ход битвы: \n{text}', parse_mode='Html')  # \n{hero} \n{foes[0]}


bot.polling(non_stop=True)
