import discord
import psycopg2
from discord.ext import commands

from anisearch import config
from anisearch.bot import logger


class Remove(commands.Cog, name='Remove'):

    def __init__(self, client):
        self.client = client

    @commands.command(name='remove', aliases=['rm'], usage='remove', brief='10s',
                      ignore_extra=False)
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def cmd_remove(self, ctx):
        """Removes the set AniList and MyAnimeList Profile."""
        db = psycopg2.connect(host=config.DB_HOST, dbname=config.DB_NAME, user=config.DB_USER,
                              password=config.BD_PASSWORD)
        cur = db.cursor()
        profile_set = False
        try:
            cur.execute('SELECT id FROM users WHERE id = %s;', (ctx.author.id,))
            user_id = cur.fetchone()[0]
            db.commit()
            if user_id == ctx.author.id:
                profile_set = True
        except TypeError:
            error_embed = discord.Embed(
                title='You have no AniList/MyAnimeList Profile set', color=0xff0000)
            await ctx.channel.send(embed=error_embed)
            logger.info('Server: %s | Response: No Profile set' % ctx.guild.name)
        if profile_set:
            cur.execute('DELETE FROM users WHERE id = %s;', (ctx.author.id,))
            db.commit()
            cur.close()
            db.close()
            removeanilist_embed = discord.Embed(title='Removed the set AniList and MyAnimeList Profile',
                                                color=0x4169E1)
            await ctx.channel.send(embed=removeanilist_embed)
            logger.info('Server: %s | Response: Removed' % ctx.guild.name)
