import discord
from discord.ext import commands
import main


class Ping(commands.Cog, name='Ping'):

    def __init__(self, client):
        self.client = client

    @commands.command(name='ping', ignore_extra=False)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def cmd_ping(self, ctx):
        """Checks the latency of the bot."""
        ping = round(self.client.latency * 1000)
        ping_embed = discord.Embed(title='Latency: `%sms`' % ping,
                                   color=0x4169E1)
        await ctx.channel.send(embed=ping_embed)
        main.logger.info('Server: %s | Response: Ping' % ctx.guild.name)


def setup(client):
    client.add_cog(Ping(client))
    main.logger.info('Loaded extension Ping')


def teardown():
    main.logger.info('Unloaded extension Ping')
