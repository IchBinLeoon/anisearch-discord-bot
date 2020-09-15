import discord
import psycopg2
from discord.ext import commands

import main
from config import config


class Prefix(commands.Cog, name='Prefix'):

    def __init__(self, client):
        self.client = client

    @commands.command(name='prefix', ignore_extra=False)
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.has_permissions(administrator=True)
    async def cmd_prefix(self, ctx, prefix):
        """Changes the current server prefix."""
        db = psycopg2.connect(host=config.DB_HOST, dbname=config.DB_NAME, user=config.DB_USER,
                              password=config.BD_PASSWORD)
        cur = db.cursor()
        cur.execute('UPDATE guilds SET prefix = %s WHERE id = %s;', (prefix, ctx.guild.id,))
        cur.execute('SELECT prefix FROM guilds WHERE id = %s;', (ctx.guild.id,))
        prefix = cur.fetchone()[0]
        db.commit()
        cur.close()
        db.close()
        if prefix == 'as!':
            prefix_embed = discord.Embed(title='Prefix resetted', color=0x4169E1)
            await ctx.channel.send(embed=prefix_embed)
            main.logger.info('Server: %s | Response: Prefix resetted' % ctx.guild.name)
        else:
            prefix_embed = discord.Embed(title='Prefix changed to `%s`' % prefix, color=0x4169E1)
            await ctx.channel.send(embed=prefix_embed)
            main.logger.info('Server: %s | Response: Prefix changed to %s' % (ctx.guild.name, prefix))


def setup(client):
    client.add_cog(Prefix(client))
    main.logger.info('Loaded extension Prefix')


def teardown():
    main.logger.info('Unloaded extension Prefix')
