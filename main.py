from cmath import log
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


class Hero:
    def __init__(self, name, skill, vigor, luck, gold, water, items, spells, paragraph, moves):
        self.name = name
        self.skill = skill
        self.vigor = vigor
        self.luck = luck
        self.gold = gold
        self.water = water
        self.items = items
        self.spells = spells
        self.paragraph = paragraph
        self.moves = moves


def create_character(id):
    hero = Hero(
        linecache.getline('names.txt', random.randint(
            0, 158)).replace("\n", ""),
        roll(1) + 6, roll(2) + 12, roll(1) + 6, 15, 2, '0/7',
        'левитации, огня, иллюзии, силы, слабости, копии, исцеления, плавания',
        0, [1])
    with shelve.open('userdata', 'w') as userdata:
        userdata[id] = hero

# PAGES ------------- add exclusions


class Paragraph:
    def __init__(self, id, event, fight, moves, rsvp, drops, takes, text):
        self.id = id
        self.event = event
        self.fight = fight
        self.moves = moves
        self.rsvp = rsvp
        self.drops = drops
        self.takes = takes
        self.text = text


def generate_paragraph(reqpage):
    with open('base.txt', 'r') as book:
        lines = book.readlines()
        paragraph = json.loads(lines[reqpage])
        paragraph = Paragraph(*paragraph)
    return paragraph


def uncode_text(paragraph):
    text = str(paragraph.id) + '. ' + \
        paragraph.text.replace('<br>', '\r\n').replace('<q>', '\"')
    return text


def set_moves(id, paragraph):
    with shelve.open('userdata', 'w') as userdata:
        hero = userdata[id]
        hero.moves = paragraph.moves
        hero.paragraph = paragraph.id
        userdata[id] = hero


# ITEMS

# FIGHTS


class Foe:
    def __init__(self, name, skill, vigor):
        self.name = name
        self.skill = skill
        self.vigor = vigor


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
        hero = userdata[f'{message.from_user.id}']
        if hero.vigor == 0:
            hero.name = '💀 ' + hero.name
    bot.send_message(
        message.chat.id, f'<b>Ваш герой — {hero.name}:</b> \r\n🗡 Мастерство: {hero.skill} \r\n🫀 Выносливость: {hero.vigor} \r\n☀️ Удача: {hero.luck} \r\n✨ Заклинания: {hero.spells}', parse_mode='Html')
    # \r\n💰 <i>Деньги: {hero.gold} \r\n💧 Вода: {hero.water} \r\n📦 Вещи: {hero.items}</i>


@bot.message_handler(commands=['debug'])
def debug(message):
    with shelve.open('userdata', 'r') as userdata:
        hero = userdata[f'{message.from_user.id}']
    paragraph = generate_paragraph(hero.paragraph)
    bot.send_message(
        message.chat.id, f'{message.from_user.id} \r\n✨ Userdata: {vars(hero)} \r\n✨ Paragraph: {vars(paragraph)}')

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
    if hero.vigor == 0:
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

    if paragraph.event == 'fight':
        with shelve.open('userdata', 'r') as userdata:
            hero = userdata[f'{message.from_user.id}']
        foes = []
        text = ''

        for foe in paragraph.fight:
            foe = Foe(*foe)
            foes.append(foe)
            text += f'{foe.name} 🗡{foe.skill} 🫀{foe.vigor} \n'

        while any(foe.vigor > 0 for foe in foes):
            for foe in foes:
                if foe.vigor > 0:

                    hero_strike = roll(2) + hero.skill
                    foe_strike = roll(2) + foe.skill

                    strike = random.randint(1, 6)
                    if hero_strike == foe_strike:
                        text += f'\nВы промахнулись'
                    if hero_strike > foe_strike:
                        foe.vigor -= strike
                        text += f'\n{foe.name}  \nВы ударили 💥{strike}'
                    if hero_strike < foe_strike:
                        hero.vigor -= strike
                        text += f'\n{foe.name} \nНанес вам удар -🫀{strike}'
                    if foe.vigor <= 0:
                        text += f', и добили 💀'
                    text += '\n'

            if hero.vigor <= 0:
                hero.vigor = 0
                hero.moves = []
                text += '\n💀 Вы умерли'
                break

        if hero.vigor > 0:
            text += '\nВы победили в этом бою!'

        with shelve.open('userdata', 'w') as userdata:
            upd = userdata[f'{message.from_user.id}']
            upd.vigor = hero.vigor
            upd.moves = hero.moves
            userdata[f'{message.from_user.id}'] = upd

        bot.send_message(
            message.chat.id, f'Ход битвы: \n{text}', parse_mode='Html')
        # \n{hero} \n{foes[0]}


bot.polling(non_stop=True)
