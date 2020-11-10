import discord
from discord.ext import commands
from anisearch.bot import logger


class Ping(commands.Cog, name='Ping'):

    def __init__(self, client):
        self.client = client

    @commands.command(name='ping', usage='ping', brief='3s', ignore_extra=False)
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def cmd_ping(self, ctx):
        """Checks the latency of the bot."""
        ping = round(self.client.latency * 1000)
        ping_embed = discord.Embed(title='Latency: `%sms`' % ping,
                                   color=0x4169E1)
        await ctx.channel.send(embed=ping_embed)
        logger.info('Server: %s | Response: Ping' % ctx.guild.name)
