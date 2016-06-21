import discord
import dota2api
import logging
import time
import sys
import cv2
import numpy as np
from datetime import datetime, timedelta
from token_and_api_key import *
# TO DO : 1. match mode
#         2. сделать, чтобы можно было смотреть любой матч(например, пятый с конца)
#         3. средний ммр? какая-нибудь статистика?
#         4. инвентарь с итемами
#         5. проблема с итемами (нужно определять их через номера)
#         6. поэтому дагоны пока не различаются и диффузалы и тревела +necro
#         7. итемы медведя
logging.basicConfig(level=logging.INFO)
client = discord.Client()
api = dota2api.Initialise(api_key)


def time_diff(start_time):
    time_passed = timedelta(seconds=int(time.time() - start_time))
    d = datetime(1, 1, 1, 1) + time_passed
    if d.month-1 != 0:
        return "{}mo {}d ago".format(
            d.month-1, d.day-1)
    else:
        if d.day-1 != 0:
            return "{}d {}h ago".format(d.day-1, d.hour)
        else:
            return "{}h {}m ago".format(d.hour, d.minute)


def win_lose(player_id):  # in dire need of refactoring
    global match, player_index, game_status
    array3 = []
    game_type = "Solo "
    for i in range(10):
        if player_id == match['players'][i]['account_id']:
            player_index = i

        if match['players'][i]['account_id'] in list(player_dic.values()) and (
                match['players'][i]['account_id'] != player_id):
                game_type = "party with: "
                array3.append('{} ({})'.format(
                    dic_reverse[match['players'][i]['account_id']],
                    match['players'][i]['hero_name']))
    game_status = game_type + ", ".join(array3)
    if (player_index > 4 and match['radiant_win']) or (
        player_index < 5 and not match['radiant_win']
    ):
        return "Lost as {}".format(match['players'][player_index]['hero_name'])
    elif (player_index > 4 and not match['radiant_win']) or (
          player_index < 5 and match['radiant_win']
    ):
        return "Won as {}".format(match['players'][player_index]['hero_name'])


def last_match(player_id, match_number):
    global match
    while True:
        try:
            hist = api.get_match_history(account_id='{}'.format(player_id))
            last_match_id = (hist['matches'][match_number]['match_id'])
            match = api.get_match_details(match_id='{}'.format(last_match_id))
        except dota2api.src.exceptions.APITimeoutError:
            continue
        else:
            break
    stats = {}
    stats['result'] = win_lose(player_id)
    # =========================== hero images
    img_empty = cv2.imread('images/heroes/empty.png', -1)
    img_dic = {}
    array1 = []

    for j in range(10):  # объявление 10 переменных и присвоение им
        img_dic['img{}'.format(j)] = cv2.imread(  # картинки героя
            'images/heroes/{} icon.png'.format(
                match['players'][j]['hero_name'].lower()
                ), -1  # cv2 -flag
                                 )
        if j == 5:  # пустое изображение для пробела между командами
            array1.append(img_empty)

        array1.append(img_dic['img{}'.format(j)])

    whole_image = np.hstack(array1)
    cv2.imwrite('images/heroes/lineup/lineup.png', whole_image)
    # ================================= item images
    item_dic = {}
    array2 = []
    for j in range(6):
        try:
            item_dic['img{}'.format(j)] = cv2.imread(
                'images/items/{} icon.png'.format(
                    match['players'][player_index][
                        'item_{}_name'.format(j)].lower()
                ), 1  # cv2 -flag
            )
            array2.append(item_dic['img{}'.format(j)])
        except KeyError:  # если айтем отсутствует в слоте
            item_dic['img{}'.format(j)] = cv2.imread(
                'images/items/empty icon.png', -1)

    whole_items = np.hstack(array2)
    cv2.imwrite('images/heroes/lineup/itemlist.png', whole_items)

    stats['game_status'] = game_status
    stats['kda'] = "{kills}/{deaths}/{assists}".format(
        **match['players'][player_index])

    stats['date'] = datetime.fromtimestamp(
        int(match['start_time'])).strftime('%d-%m-%Y %H:%M:%S')

    stats['time_passed'] = time_diff(match['start_time'])

    stats['m'], stats['s'] = divmod(match['duration'], 60)

    # dotabuff = "http://www.dotabuff.com/matches/{}".format(last_match_id)

    reply = """{result} KDA: {kda}, Duration: {m}m{s}s,
        played on {date} ({time_passed}),
    {game_status}""".format(**stats)

    return reply


def avg_stats(player_id, number_of_games):
    array2 = [0]*10
    while True:
        try:
            hist = api.get_match_history(account_id='{}'.format(player_id))
        except dota2api.src.exceptions.APITimeoutError:
            continue
        else:
            break
    array_stat = ['kills',
                  'deaths',
                  'assists',
                  'last_hits',
                  'denies',
                  'gold_per_min',
                  'xp_per_min',
                  'hero_damage',
                  'tower_damage',
                  'level'
                  ]
    for i in range(number_of_games):
        while True:
            try:
                match_id = (hist['matches'][i]['match_id'])
                match = api.get_match_details(match_id='{}'.format(match_id))
            except dota2api.src.exceptions.APITimeoutError:
                continue
            else:
                break

        for i in range(10):
            if player_id == match['players'][i]['account_id']:
                player_index = i
        x = match['players'][player_index]
        for i in range(10):
            array2[i] += x[array_stat[i]]

    statList = [round(x / number_of_games, 2) for x in array2]
    return """Your avg stats in last {} games: **k**:{} **d**:{} **a**:{}, **last hits**: {}, **denies**: {}, **gpm**: {}, **xpm**: {}, **hero damage**: {}, **tower_damage**: {}, **level**: {}""".format(number_of_games, *statList)


@client.event
async def on_message(message):
    # do not want the bot to reply to itself
    if message.author == client.user:
        return

    # для теста
    if message.content.startswith('!hello'):
        msg = 'Hello {0.author.mention}'.format(message)
        await client.send_message(message.channel, msg)
        #  все пофиксить надо :(
    try:
        if message.content.startswith('!last'):

            if message.content == '!last':
                player_id = player_dic[message.author.name]
                reply = last_match(player_id, 0)

            elif str(message.content)[:-2] == '!last':
                match_number = int(str(message.content)[-2:])
                player_id = player_dic[message.author.name]
                reply = last_match(player_id, match_number)

            elif str(message.content)[:-2] != '!last':
                if str(message.content)[5] == ' ':
                    name = str(message.content).strip()[6:]
                    match_number = 0
                elif str(message.content)[7] == ' ':
                    name = str(message.content).strip()[8:]
                    match_number = int(str(message.content)[5:7])

                player_id = player_dic[name]
                reply = last_match(player_id, match_number)

            await client.send_message(message.channel, reply)
            await client.send_file(
                message.channel, 'images/heroes/lineup/lineup.png')
            await client.send_file(
                message.channel, 'images/heroes/lineup/itemlist.png')

        if message.content.startswith('!stats'):
            n = int(str(message.content)[-2:])
            player_id = player_dic[message.author.name]
            stats = avg_stats(player_id, n)
            await client.send_message(message.channel, stats)
    except dota2api.src.exceptions.APIError:
        await client.send_message(
            message.channel,
            "Cannot get match history for a user that hasn't allowed it.")
    # except dota2api.src.exceptions.APITimeoutError:
    #    await client.send_message(
    #        message.channel,
    #        "HTTP 503: Please try again later.")
    except ValueError:
        await client.send_message(
           message.channel, " :(")

    if message.content == '!help1':
        await client.send_message(message.channel, help_msg)
# ============= only memes below ==============================================
    if message.content.startswith('%'):
        name = str(message.content).strip().lower()[1:]
        await client.send_file(
            message.channel, 'images/twitch/{}.png'.format(name))

    if message.content.startswith('!new_patch'):
        await client.send_file(message.channel, 'images/new_patch.gif')
        await client.change_status(game=discord.Game(name='DOTA2'))

    if message.content.startswith('!hero'):
        name = str(message.content).strip().lower()[6:]
        await client.send_file(
            message.channel, 'images/heroes/{} icon.png'.format(name))

    if message.content.startswith('!item'):
        name = str(message.content).strip().lower()[6:]
        await client.send_file(
            message.channel, 'images/items/{} icon.png'.format(name))

    if message.content.startswith('!wow'):
        await client.send_file(
            message.channel, 'images/wow.png')


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

client.run(token)
