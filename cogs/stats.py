from discord.ext import commands
import discord
from token_and_api_key import *
from .utils import stat_func as sf
from .utils.hero_graph import hero_per_month
from .utils.hero_dictionary import hero_dic



class Stats:
    """Dota-related stats"""
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def last(self, ctx, *, number: int):
        """!last 0 - your last match"""
        player_id = player_dic[ctx.message.author.name]
        reply = sf.last_match(player_id, number)  # !last 0 == last match

        await self.bot.send_file(
            ctx.message.channel, 'images/lineup/lineup.png', content=reply)
        await self.bot.send_file(
            ctx.message.channel, 'images/lineup/itemlist.png')

    @commands.command(pass_context=True)
    async def p_last(self, ctx, *, player_name: str):
        """Same as !last but for any player"""
        player_id = player_dic[player_name.split()[1]]
        number = int(player_name.split()[0])
        reply = sf.last_match(player_id, number)

        await self.bot.send_file(
            ctx.message.channel, 'images/lineup/lineup.png', content=reply)
        await self.bot.send_file(
            ctx.message.channel, 'images/lineup/itemlist.png')

    @commands.command(pass_context=True)
    async def stats(self, ctx, games: int):
        """Your average stats in last <n> games"""
        player_id = player_dic[ctx.message.author.name]
        reply = sf.avg_stats(player_id, games)
        await self.bot.say(reply)

    @commands.command(pass_context=True)
    async def wr(self, ctx, hero_name):
        """Your winrate playing as a <hero_name>"""
        player_id = player_dic[ctx.message.author.name]
        try:
            hero_id = list(hero_dic.keys())[
                list(hero_dic.values()).index(hero_name)]
        except ValueError:
            await self.bot.say("Invalid hero name")
        reply = sf.winrate_hero(player_id, hero_id)
        await self.bot.say(reply)

    @commands.command(pass_context=True)
    async def wr_with(self, ctx, *, msg):
        """Your winrate with players (takes up to 4 arguments)"""
        names = msg.split()
        player_id = player_dic[ctx.message.author.name]
        for i, name in enumerate(names):
            names[i] = player_dic[name]
        reply = sf.winrate_with(player_id, names)
        await self.bot.say(reply)

    @commands.command(pass_context=True)
    async def wr_with_hero(self, ctx, *, msg):
        """Your winrate with <player> on specific <hero>"""
        player_id = player_dic[ctx.message.author.name]
        player_id2 = player_dic[msg.split()[0]]
        hero_name = ' '.join(msg.split()[1:])
        hero_id = list(hero_dic.keys())[list(
            hero_dic.values()).index(hero_name)]

        reply = sf.my_winrate_with_player_on(player_id, player_id2, hero_id)
        await self.bot.say(reply)

    @commands.command(pass_context=True)
    async def avg(self, ctx, *, hero_name):
        """Your average stats playing as a <hero_name>"""
        player_id = player_dic[ctx.message.author.name]
        hero_id = list(hero_dic.keys())[
            list(hero_dic.values()).index(hero_name)]
        reply = sf.avg_stats_with_hero(player_id, hero_id)
        await self.bot.say(reply)

    @commands.command(pass_context=True)
    async def game_stat(self, ctx, match_number: int):
        """End-game screen with kda and items for all players. !game_stat 0 - your last match"""
        player_id = player_dic[ctx.message.author.name]
        reply = last_match(player_id, match_number)
        sf.big_pic(player_id, match_number)
        await self.bot.send_file(
            ctx.message.channel,
            'images/lineup/itemlist2.png',
            content=reply
            )

    @commands.command(pass_context=True)
    async def hero_graph(self, ctx, hero_name):
        """Graph with your number of games played as a <hero_name> per month"""
        player_id = player_dic[ctx.message.author.name]
        hero_id = list(hero_dic.keys())[
            list(hero_dic.values()).index(hero_name)]
        reply = hero_per_month(player_id, hero_id)
        await self.bot.send_file(
                ctx.message.channel,
                'images/graphs/hero.png',
                content=reply)

    @commands.command(pass_context=True)
    async def records(self, ctx, *hero_name):
        """Your all-time records. Also takes <hero_name> argument for records as a hero"""
        player_id = player_dic[ctx.message.author.name]
        if hero_name:
            hero_id = list(hero_dic.keys())[
                list(hero_dic.values()).index(hero_name[0])]
            reply = sf.all_time_records(player_id, hero_id)
        else:
            reply = sf.all_time_records(player_id)
        await self.bot.say(reply)


def setup(bot):
    bot.add_cog(Stats(bot))
