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
    def __init__(self, name, skill, overskill, vigor, luck, gold, water, items, spells, paragraph, moves):
        self.name = name
        self.skill = skill
        self.overskill = overskill
        self.vigor = vigor
        self.luck = luck
        self.gold = gold
        self.water = water
        self.items = items
        self.spells = spells
        self.paragraph = paragraph
        self.moves = moves


def create_hero(id):
    hero = Hero(
        linecache.getline('names.txt', random.randint(
            0, 158)).replace("\n", ""),
        roll(1) + 6, 0, roll(2) + 12, roll(1) + 6, 15, 2, ['Меч'],
        ['левитации', 'огня', 'иллюзии', 'силы',
            'слабости', 'копии', 'исцеления', 'плавания'],
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

def exchange_items(message, paragraph, hero):
    if paragraph.rsvp:
        if 'spell' in paragraph.rsvp:
            if paragraph.rsvp['spell'] not in hero.spells:
                bot.send_message(
                    message.chat.id, 'У вас нет нужного заклятия')
                return
        if 'item' in paragraph.rsvp:
            if paragraph.rsvp['item'] not in hero.items:
                bot.send_message(message.chat.id, 'У вас нет нужного предмета')
                return

        if paragraph.takes:
            if 'item' in paragraph.takes:
                item = paragraph.takes['item']
                hero.items.remove(f'{item}')
            if 'spell' in paragraph.takes:
                spell = paragraph.takes['spell']
                hero.spells.remove(f'{spell}')

    if paragraph.takes:
        if 'skill' in paragraph.takes:
            skill = paragraph.takes['skill']
            hero.skill += skill
        if 'vigor' in paragraph.takes:
            vigor = paragraph.takes['vigor']
            hero.vigor += vigor
        if 'luck' in paragraph.takes:
            luck = paragraph.takes['luck']
            hero.luck += luck

    if paragraph.drops:
        if 'spell' in paragraph.drops:
            hero.spells.append(paragraph.drops['spell'])
        if 'item' in paragraph.drops:
            hero.items += paragraph.drops['item']
        if 'skill' in paragraph.drops:
            hero.skill += paragraph.drops['skill']
        if 'overskill' in paragraph.drops:
            hero.overskill += paragraph.drops['overskill']
        if 'vigor' in paragraph.drops:
            hero.vigor += paragraph.drops['vigor']
        if 'luck' in paragraph.drops:
            hero.luck += paragraph.drops['luck']

    with shelve.open('userdata', 'w') as userdata:
        userdata[f'{message.from_user.id}'] = hero

# FIGHTS


class Foe:
    def __init__(self, name, skill, vigor):
        self.name = name
        self.skill = skill
        self.vigor = vigor


def fight(message, paragraph, hero):
    with shelve.open('userdata', 'r') as userdata:
        hero = userdata[f'{message.from_user.id}']
    foes = []
    text = ''

    hero.skill = hero.skill + hero.overskill

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
                if hero_strike < foe_strike:
                    hero.vigor -= strike
                    text += f'\n{foe.name} \nНанес вам удар -🫀{strike}'
                if hero_strike > foe_strike:
                    foe.vigor -= strike
                    text += f'\n{foe.name}  \nВы ударили 💥{strike}'
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

    hero.overskill = 0

    with shelve.open('userdata', 'w') as userdata:
        userdata[f'{message.from_user.id}'] = hero

    return text

# COMMANDS

# start - рестарт
# hero - герой


@bot.message_handler(commands=['start'])
def start(message):
    try:
        bot.send_message(
            message.chat.id, f'<b>Старт игры</b> \r\n⏳ Создание нового героя...', parse_mode='Html')
        create_hero(f'{message.from_user.id}')

        time.sleep(3)

        hero(message)

        time.sleep(3)

        paragraph = generate_paragraph(1)
        text = uncode_text(paragraph)
        set_moves(f'{message.from_user.id}', paragraph)
        bot.send_message(
            message.chat.id, text, parse_mode='Html')
    except:
        bot.send_message(
            message.chat.id, 'Что-то сломалось, попробуйте начать еще раз - /start')


@bot.message_handler(commands=['hero'])
def hero(message):
    try:
        with shelve.open('userdata', 'r') as userdata:
            hero = userdata[f'{message.from_user.id}']
            if hero.vigor == 0:
                hero.name = '💀 ' + hero.name
            items = ', '.join(hero.items)
            spells = ', '.join(hero.spells)
        bot.send_message(
            message.chat.id, f'<b>Ваш герой — {hero.name}:</b> \r\n🗡 Мастерство: {hero.skill} \r\n🫀 Выносливость: {hero.vigor} \r\n☀️ Удача: {hero.luck} \r\n📦 Вещи: {items} \r\n✨ Заклинания: {spells}', parse_mode='Html')
        # \r\n💰 <i>Деньги: {hero.gold} \r\n💧 Вода: {hero.water} \r\n📦 Вещи: {hero.items}</i>
    except:
        bot.send_message(
            message.chat.id, 'Что-то сломалось, попробуйте повторить команду')


@bot.message_handler(commands=['debug'])
def debug(message):
    try:
        with shelve.open('userdata', 'r') as userdata:
            hero = userdata[f'{message.from_user.id}']
        paragraph = generate_paragraph(hero.paragraph)
        bot.send_message(
            message.chat.id, f'{message.from_user.id} \r\n✨ Userdata: {vars(hero)} \r\n✨ Paragraph: {vars(paragraph)}')
    except:
        bot.send_message(
            message.chat.id, 'Пиздец, даже дебаг не работает!')

# MESSAGE


@bot.message_handler()
def get_user_text(message):
    try:
        if not message.text.isnumeric():
            bot.send_message(message.chat.id, 'Введите номер страницы')
            return
        reqpage = int(message.text)
        if not (reqpage > 0 and reqpage <= 619):
            bot.send_message(message.chat.id, 'Такой страницы нет')
            return

        with shelve.open('userdata', 'r') as userdata:
            hero = userdata[f'{message.from_user.id}']
        if hero.vigor == 0:
            bot.send_message(
                message.chat.id, 'Ваше путешествие закончено. Создайте нового героя - /start')
            return
        if reqpage == hero.paragraph:
            bot.send_message(message.chat.id, 'Вы сейчас здесь')
            return
        if reqpage not in hero.moves:
            bot.send_message(message.chat.id, 'Вы не можете сюда попасть')
            return

        paragraph = generate_paragraph(reqpage)
        text = f'🗡{hero.skill} 🫀{hero.vigor} ☀️{hero.luck} 📦{len(hero.items)} \n{uncode_text(paragraph)}'

        bot.send_message(
            message.chat.id, f'⏳ Открываю...', parse_mode='Html')

        time.sleep(3)

        exchange_items(message, paragraph, hero)
        set_moves(f'{message.from_user.id}', paragraph)

        bot.send_message(
            message.chat.id, text, parse_mode='Html')

        if paragraph.event == 'fight':
            bot.send_message(
                message.chat.id, f'Ход битвы: \n{fight(message, paragraph, hero)}', parse_mode='Html')
    except:
        bot.send_message(
            message.chat.id, 'Что-то сломалось, попробуйте еще раз')


bot.polling(non_stop=True)
