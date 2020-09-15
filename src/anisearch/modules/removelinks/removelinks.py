import discord
import psycopg2
from discord.ext import commands

import main
from config import config


class RemoveLinks(commands.Cog, name='RemoveLinks'):

    def __init__(self, client):
        self.client = client

    @commands.command(name='removelinks', aliases=['rml', 'rmlinks'], ignore_extra=False)
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def cmd_removeanilist(self, ctx):
        """Removes the linked AniList and MyAnimeList Profile."""
        db = psycopg2.connect(host=config.DB_HOST, dbname=config.DB_NAME, user=config.DB_USER,
                              password=config.BD_PASSWORD)
        cur = db.cursor()
        linked = False
        try:
            cur.execute('SELECT id FROM users WHERE id = %s;', (ctx.author.id,))
            user_id = cur.fetchone()[0]
            db.commit()
            if user_id == ctx.author.id:
                linked = True
        except TypeError:
            error_embed = discord.Embed(
                title='You have no AniList/MyAnimeList Profile linked', color=0xff0000)
            await ctx.channel.send(embed=error_embed)
            main.logger.info('Server: %s | Response: No Profile linked' % ctx.guild.name)
        if linked:
            cur.execute('DELETE FROM users WHERE id = %s;', (ctx.author.id,))
            db.commit()
            cur.close()
            db.close()
            removeanilist_embed = discord.Embed(title='Removed the linked AniList and MyAnimeList Profile',
                                                color=0x4169E1)
            await ctx.channel.send(embed=removeanilist_embed)
            main.logger.info('Server: %s | Response: Links removed' % ctx.guild.name)


def setup(client):
    client.add_cog(RemoveLinks(client))
    main.logger.info('Loaded extension RemoveLinks')


def teardown():
    main.logger.info('Unloaded extension RemoveLinks')
