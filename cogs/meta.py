from discord.ext import commands
import discord
from .utils import stats_related, checks
import os
from .utils.resources import db
from csv import reader
import shlex
from token_and_api_key import log_chat_id
from cogs.utils.hero_dictionary import hero_dic


class Meta:

    def __init__(self, bot):
        self.bot = bot

    def get_discord_id(self, ctx, name):
        discord_id = 0
        for member in ctx.message.server.members:
            if name == member.name:
                discord_id = member.id
        return discord_id

    @commands.command(pass_context=True)
    async def wololo(self, ctx):
        message = await self.bot.say('0')
        for i in range(1, 100):
            await self.bot.edit_message(message, '{}'.format(i))

    @commands.command()
    async def uptime(self):
        """Bot's current uptime"""
        reply = stats_related.time_diff(self.bot.uptime)
        await self.bot.say(reply)

    @commands.command()
    async def join(self):
        """Joins a server."""
        perms = discord.Permissions.none()
        perms.read_messages = True
        perms.send_messages = True
        perms.manage_roles = True
        perms.ban_members = True
        perms.kick_members = True
        perms.manage_messages = True
        perms.embed_links = True
        perms.read_message_history = True
        perms.attach_files = True
        await self.bot.say(discord.utils.oauth_url(self.bot.client_id, perms))

    @commands.command()
    async def about(self):
        """Tells you information about the bot itself."""
        revision = os.popen(r'git show -s HEAD --format="%s (%cr)"').read().strip()
        result = ['**About Me:**']
        result.append('- Author: Егор#5310 (Discord ID: 134716781750124544)')
        result.append('- Library: discord.py (Python)')
        result.append('- Source code : https://github.com/bozhko-egor/dota2-discord-bot')
        result.append('- Latest Change: {}'.format(revision))
        result.append('- Uptime: {}'.format(stats_related.time_diff(self.bot.uptime)))
        await self.bot.say('\n'.join(result))

    @commands.command(hidden=True, pass_context=True)
    @checks.is_owner()
    async def add_player(self, ctx, steamid: int, *, player_name):
            discord_id = self.get_discord_id(ctx, player_name)
            if discord_id:
                db.add_id(discord_id, ctx.message.server.id, steamid)
                await self.bot.say('Done!')
            else:
                await self.bot.say('Invalid player name')

    @commands.command(hidden=True, pass_context=True)
    @checks.is_owner()
    async def delete_player(self, ctx, *, player_name):
        discord_id = self.get_discord_id(ctx, player_name)
        if discord_id:
            reply = db.delete_id(discord_id, ctx.message.server.id)
            if reply:
                await self.bot.say(reply)
            else:
                await self.bot.say("Done!")
        else:
            await self.bot.say('Invalid player name')

    @commands.command(pass_context=True, no_pm=True)
    async def add_steamid(self, ctx, steamid: int):
        """Makes connection discord id - steam id"""
        discord_id = ctx.message.author.id
        reply = db.add_id(discord_id, ctx.message.server.id, steamid)
        if reply:
            await self.bot.say(reply)
        else:
            await self.bot.say("Done!")

    @commands.command(pass_context=True, no_pm=True)
    async def delete_steamid(self, ctx):
        discord_id = ctx.message.author.id
        reply = db.delete_id(discord_id, ctx.message.server.id)
        if reply:
            await self.bot.say(reply)
        else:
            await self.bot.say("Done!")

    @commands.command(hidden=True)
    async def patchnotes(self):
        """ ???"""
        with open('patchnotes.txt', 'r') as f:
            changelog = f.read()
        await self.bot.say(changelog)

    @commands.command(name='quit', hidden=True)
    @checks.is_owner()
    async def _quit(self):
        """Quits the bot."""
        await self.bot.logout()

def setup(bot):
    bot.add_cog(Meta(bot))
