import random
from typing import Optional

import discord
import psycopg2
from discord.ext import commands

import anisearch
from config import config

example_sites = ['anilist', 'myanimelist']


def get_prefix(ctx):
    db = psycopg2.connect(host=config.DB_HOST, dbname=config.DB_NAME, user=config.DB_USER, password=config.BD_PASSWORD)
    cur = db.cursor()
    cur.execute('SELECT prefix FROM guilds WHERE id = %s;', (ctx.guild.id,))
    prefix = cur.fetchone()[0]
    db.commit()
    cur.close()
    db.close()
    return prefix


class SetProfile(commands.Cog, name='SetProfile'):

    def __init__(self, client):
        self.client = client

    @commands.command(name='setprofile', aliases=['set'], usage='setprofile <anilist|myanimelist> <username>',
                      brief='5s', ignore_extra=False)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def cmd_setprofile(self, ctx, site: Optional[str], username: Optional[str]):
        """Sets an AniList or MyAnimeList Profile."""
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
                        setanilist_embed = discord.Embed(title='Set AniList Profile `%s`' % username,
                                                         color=0x4169E1)
                        await ctx.channel.send(embed=setanilist_embed)
                        anisearch.logger.info('Server: %s | Response: Set AniList - %s' % (ctx.guild.name, username))
                    except TypeError:
                        cur.execute('INSERT INTO users (id, anilist) VALUES (%s, %s)', (ctx.author.id, username))
                        cur.execute('SELECT anilist FROM users WHERE id = %s;', (ctx.author.id,))
                        username = cur.fetchone()[0]
                        db.commit()
                        cur.close()
                        db.close()
                        setanilist_embed = discord.Embed(title='Set AniList Profile `%s`' % username,
                                                         color=0x4169E1)
                        await ctx.channel.send(embed=setanilist_embed)
                        anisearch.logger.info('Server: %s | Response: Set AniList - %s' % (ctx.guild.name, username))
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
                        setmyanimelist_embed = discord.Embed(title='Set MyAnimeList Profile `%s`' % username,
                                                             color=0x4169E1)
                        await ctx.channel.send(embed=setmyanimelist_embed)
                        anisearch.logger.info(
                            'Server: %s | Response: Set MyAnimeList - %s' % (ctx.guild.name, username))
                    except TypeError:
                        cur.execute('INSERT INTO users (id, myanimelist) VALUES (%s, %s)', (ctx.author.id, username))
                        cur.execute('SELECT myanimelist FROM users WHERE id = %s;', (ctx.author.id,))
                        username = cur.fetchone()[0]
                        db.commit()
                        cur.close()
                        db.close()
                        setmyanimelist_embed = discord.Embed(title='Set MyAnimeList Profile `%s`' % username,
                                                             color=0x4169E1)
                        await ctx.channel.send(embed=setmyanimelist_embed)
                        anisearch.logger.info(
                            'Server: %s | Response: Set MyAnimeList - %s' % (ctx.guild.name, username))
                else:
                    prefix = get_prefix(ctx)
                    example_site = random.choice(example_sites)
                    example_username = ctx.author.name
                    example = '`%ssetprofile %s %s`' % (prefix, example_site, example_username)
                    error_embed = discord.Embed(title='Wrong arguments. Example: %s' % example,
                                                color=0xff0000)
                    await ctx.channel.send(embed=error_embed)
                    await ctx.command.reset_cooldown(ctx)
                    anisearch.logger.info('Server: %s | Response: Wrong arguments' % ctx.guild.name)

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
                    anilist_profile = 'Not set'
                if anilist_profile is None:
                    anilist_profile = 'Not set'
                try:
                    cur.execute('SELECT myanimelist FROM users WHERE id = %s;', (user_id,))
                    myanimelist_profile = cur.fetchone()[0]
                    db.commit()
                except TypeError:
                    myanimelist_profile = 'Not set'
                if myanimelist_profile is None:
                    myanimelist_profile = 'Not set'
                cur.close()
                db.close()
                user_name = self.client.get_user(user_id).name
                embed = discord.Embed(title=user_name, color=0x4169E1)
                embed.add_field(name="AniList", value=anilist_profile,
                                inline=True)
                embed.add_field(name="MyAnimeList", value=myanimelist_profile,
                                inline=True)
                await ctx.channel.send(embed=embed)
                anisearch.logger.info('Server: %s | Response: Profiles - %s' % (ctx.guild.name, user_name))
            else:
                error_embed = discord.Embed(title='Missing required argument',
                                            color=0xff0000)
                await ctx.channel.send(embed=error_embed)
                await ctx.command.reset_cooldown(ctx)
                anisearch.logger.info('Server: %s | Response: Missing required argument' % ctx.guild.name)
        else:
            db = psycopg2.connect(host=config.DB_HOST, dbname=config.DB_NAME, user=config.DB_USER,
                                  password=config.BD_PASSWORD)
            cur = db.cursor()
            try:
                cur.execute('SELECT anilist FROM users WHERE id = %s;', (ctx.author.id,))
                anilist_profile = cur.fetchone()[0]
                db.commit()
            except TypeError:
                anilist_profile = 'Not set'
            if anilist_profile is None:
                anilist_profile = 'Not set'
            try:
                cur.execute('SELECT myanimelist FROM users WHERE id = %s;', (ctx.author.id,))
                myanimelist_profile = cur.fetchone()[0]
                db.commit()
            except TypeError:
                myanimelist_profile = 'Not set'
            if myanimelist_profile is None:
                myanimelist_profile = 'Not set'
            cur.close()
            db.close()
            embed = discord.Embed(title=ctx.author.name, color=0x4169E1)
            embed.add_field(name="AniList", value=anilist_profile,
                            inline=True)
            embed.add_field(name="MyAnimeList", value=myanimelist_profile,
                            inline=True)
            await ctx.channel.send(embed=embed)
            anisearch.logger.info('Server: %s | Response: Profiles - %s' % (ctx.guild.name, ctx.author.name))


def setup(client):
    client.add_cog(SetProfile(client))
    anisearch.logger.info('Loaded extension SetProfile')


def teardown():
    anisearch.logger.info('Unloaded extension SetProfile')
