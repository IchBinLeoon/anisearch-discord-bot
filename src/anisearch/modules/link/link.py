from typing import Optional

import discord
import psycopg2
from discord.ext import commands

import main
from config import config


class Link(commands.Cog, name='Link'):

    def __init__(self, client):
        self.client = client

    @commands.command(name='link', aliases=['l'], usage='link <anilist/myanimelist> <username>',
                      brief='5s', ignore_extra=False)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def cmd_link(self, ctx, site: Optional[str], username: Optional[str]):
        """Links an AniList or MyAnimeList Profile."""
        if site:
            if username:
                if site == 'AniList' or site == 'anilist' or site == 'al':
                    db = psycopg2.connect(host=config.DB_HOST, dbname=config.DB_NAME, user=config.DB_USER,
                                          password=config.BD_PASSWORD)
                    cur = db.cursor()
                    try:
                        cur.execute('UPDATE users SET anilist = %s WHERE id = %s;', (username, ctx.author.id,))
                        cur.execute('SELECT anilist FROM users WHERE id = %s;', (ctx.author.id,))
                        username = cur.fetchone()[0]
                        db.commit()
                        cur.close()
                        db.close()
                        linkanilist_embed = discord.Embed(title='Linked AniList Profile `%s`' % username,
                                                          color=0x4169E1)
                        await ctx.channel.send(embed=linkanilist_embed)
                        main.logger.info('Server: %s | Response: Link AniList - %s' % (ctx.guild.name, username))
                    except TypeError:
                        cur.execute('INSERT INTO users (id, anilist) VALUES (%s, %s)', (ctx.author.id, username))
                        cur.execute('SELECT anilist FROM users WHERE id = %s;', (ctx.author.id,))
                        username = cur.fetchone()[0]
                        db.commit()
                        cur.close()
                        db.close()
                        linkanilist_embed = discord.Embed(title='Linked AniList Profile `%s`' % username,
                                                          color=0x4169E1)
                        await ctx.channel.send(embed=linkanilist_embed)
                        main.logger.info('Server: %s | Response: Link AniList - %s' % (ctx.guild.name, username))
                elif site == 'MyAnimeList' or site == 'myanimelist' or site == 'mal':
                    db = psycopg2.connect(host=config.DB_HOST, dbname=config.DB_NAME, user=config.DB_USER,
                                          password=config.BD_PASSWORD)
                    cur = db.cursor()
                    try:
                        cur.execute('UPDATE users SET myanimelist = %s WHERE id = %s;', (username, ctx.author.id,))
                        cur.execute('SELECT myanimelist FROM users WHERE id = %s;', (ctx.author.id,))
                        username = cur.fetchone()[0]
                        db.commit()
                        cur.close()
                        db.close()
                        linkmyanimelist_embed = discord.Embed(title='Linked MyAnimeList Profile `%s`' % username,
                                                              color=0x4169E1)
                        await ctx.channel.send(embed=linkmyanimelist_embed)
                        main.logger.info('Server: %s | Response: Link MyAnimeList - %s' % (ctx.guild.name, username))
                    except TypeError:
                        cur.execute('INSERT INTO users (id, myanimelist) VALUES (%s, %s)', (ctx.author.id, username))
                        cur.execute('SELECT myanimelist FROM users WHERE id = %s;', (ctx.author.id,))
                        username = cur.fetchone()[0]
                        db.commit()
                        cur.close()
                        db.close()
                        linkmyanimelist_embed = discord.Embed(title='Linked MyAnimeList Profile `%s`' % username,
                                                              color=0x4169E1)
                        await ctx.channel.send(embed=linkmyanimelist_embed)
                        main.logger.info('Server: %s | Response: Link MyAnimeList - %s' % (ctx.guild.name, username))
                else:
                    error_embed = discord.Embed(title='Wrong arguments',
                                                color=0xff0000)
                    await ctx.channel.send(embed=error_embed)
                    main.logger.info('Server: %s | Response: Wrong arguments' % ctx.guild.name)

            elif site.startswith('<@!'):
                user_id = int(site.replace('<@!', '').replace('>', ''))
                db = psycopg2.connect(host=config.DB_HOST, dbname=config.DB_NAME, user=config.DB_USER,
                                      password=config.BD_PASSWORD)
                cur = db.cursor()
                try:
                    cur.execute('SELECT anilist FROM users WHERE id = %s;', (user_id,))
                    anilist_profile = cur.fetchone()[0]
                    db.commit()
                except TypeError:
                    anilist_profile = 'Not linked'
                try:
                    cur.execute('SELECT myanimelist FROM users WHERE id = %s;', (user_id,))
                    myanimelist_profile = cur.fetchone()[0]
                    db.commit()
                except TypeError:
                    myanimelist_profile = 'Not linked'
                cur.close()
                db.close()
                user_name = self.client.get_user(user_id).name
                embed = discord.Embed(title=user_name, color=0x4169E1)
                embed.add_field(name="AniList", value=anilist_profile,
                                inline=True)
                embed.add_field(name="MyAnimeList", value=myanimelist_profile,
                                inline=True)
                await ctx.channel.send(embed=embed)
                main.logger.info('Server: %s | Response: Links - %s' % (ctx.guild.name, user_name))
            else:
                error_embed = discord.Embed(title='Missing required argument',
                                            color=0xff0000)
                await ctx.channel.send(embed=error_embed)
                main.logger.info('Server: %s | Response: Missing required argument' % ctx.guild.name)
        else:
            db = psycopg2.connect(host=config.DB_HOST, dbname=config.DB_NAME, user=config.DB_USER,
                                  password=config.BD_PASSWORD)
            cur = db.cursor()
            try:
                cur.execute('SELECT anilist FROM users WHERE id = %s;', (ctx.author.id,))
                anilist_profile = cur.fetchone()[0]
                db.commit()
            except TypeError:
                anilist_profile = 'Not linked'
            try:
                cur.execute('SELECT myanimelist FROM users WHERE id = %s;', (ctx.author.id,))
                myanimelist_profile = cur.fetchone()[0]
                db.commit()
            except TypeError:
                myanimelist_profile = 'Not linked'
            cur.close()
            db.close()
            embed = discord.Embed(title=ctx.author.name, color=0x4169E1)
            embed.add_field(name="AniList", value=anilist_profile,
                            inline=True)
            embed.add_field(name="MyAnimeList", value=myanimelist_profile,
                            inline=True)
            await ctx.channel.send(embed=embed)
            main.logger.info('Server: %s | Response: Links - %s' % (ctx.guild.name, ctx.author.name))


def setup(client):
    client.add_cog(Link(client))
    main.logger.info('Loaded extension Link')


def teardown():
    main.logger.info('Unloaded extension Link')
