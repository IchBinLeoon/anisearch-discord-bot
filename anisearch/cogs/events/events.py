import dbl
import discord
import psycopg2
from discord.ext import commands

from anisearch import config
from anisearch.utils.logger import logger


class Events(commands.Cog, name='Events'):

    def __init__(self, bot):
        self.bot = bot
        self.topgg_token = config.TOPGG
        self.dblpy = dbl.DBLClient(self.bot, self.topgg_token, autopost=True)

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        logger.info('Joined server {}'.format(guild.name))
        db = psycopg2.connect(host=config.DB_HOST, dbname=config.DB_NAME, user=config.DB_USER,
                              password=config.BD_PASSWORD)
        cur = db.cursor()
        cur.execute('INSERT INTO guilds (id, prefix) VALUES (%s, %s)', (guild.id, 'as!'))
        db.commit()
        cur.close()
        db.close()
        logger.info('Set Prefix for Guild {}'.format(guild.id))

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        logger.info('Left server {}'.format(guild.name))
        db = psycopg2.connect(host=config.DB_HOST, dbname=config.DB_NAME, user=config.DB_USER,
                              password=config.BD_PASSWORD)
        cur = db.cursor()
        cur.execute('DELETE FROM guilds WHERE id = %s', (guild.id,))
        db.commit()
        cur.close()
        db.close()
        logger.info('Removed Prefix for Guild {}'.format(guild.id))

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            embed = discord.Embed(title='The command was not found.', color=0xff0000)
            await ctx.channel.send(embed=embed)
        if isinstance(error, commands.CommandOnCooldown):
            embed = discord.Embed(title='The command is on cooldown for `{:.2f}s`.'.format(error.retry_after),
                                  color=0xff0000)
            await ctx.channel.send(embed=embed)
        if isinstance(error, commands.TooManyArguments):
            embed = discord.Embed(title='Too many arguments.', color=0xff0000)
            await ctx.channel.send(embed=embed)
            ctx.command.reset_cooldown(ctx)
        if isinstance(error, commands.MissingRequiredArgument):
            embed = discord.Embed(title='Missing required argument.', color=0xff0000)
            await ctx.channel.send(embed=embed)
            ctx.command.reset_cooldown(ctx)
        if isinstance(error, commands.BadArgument):
            embed = discord.Embed(title='Wrong arguments.', color=0xff0000)
            await ctx.channel.send(embed=embed)
            ctx.command.reset_cooldown(ctx)
        if isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(title='Missing permissions.', color=0xff0000)
            await ctx.channel.send(embed=embed)
            ctx.command.reset_cooldown(ctx)
        if isinstance(error, commands.BotMissingPermissions):
            embed = discord.Embed(title='Bot missing permissions.', color=0xff0000)
            await ctx.channel.send(embed=embed)
            ctx.command.reset_cooldown(ctx)

    @commands.Cog.listener()
    async def on_guild_post(self):
        logger.info('TopGG server count posted ({})'.format(self.dblpy.guild_count()))
