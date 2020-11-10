import random
from typing import Optional

import aiohttp
import discord
import psycopg2
from discord.ext import commands
from jikanpy import AioJikan

from anisearch import config
from anisearch.bot import logger
from anisearch.queries import anilist_query

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
                    api = 'https://graphql.anilist.co'
                    query = anilist_query.query
                    variables = {
                        'username': username
                    }
                    async with aiohttp.ClientSession() as session:
                        async with session.post(api, json={'query': query, 'variables': variables}) as r:
                            if r.status == 200:
                                json_data = await r.json()
                                data = json_data['data']['User']
                                try:
                                    anime_count = data['statistics']['anime']['count']
                                    anime_mean_score = data['statistics']['anime']['meanScore']
                                    anime_days_watched = round(data['statistics']['anime']
                                                               ['minutesWatched'] / 60 / 24, 2)
                                    anime_episodes_watched = data['statistics']['anime']['episodesWatched']
                                    manga_count = data['statistics']['manga']['count']
                                    manga_mean_score = data['statistics']['manga']['meanScore']
                                    manga_chapters_read = data['statistics']['manga']['chaptersRead']
                                    manga_volumes_read = data['statistics']['manga']['volumesRead']
                                    db = psycopg2.connect(host=config.DB_HOST, dbname=config.DB_NAME,
                                                          user=config.DB_USER, password=config.BD_PASSWORD)
                                    cur = db.cursor()
                                    try:
                                        cur.execute('UPDATE users SET anilist = %s WHERE id = %s;',
                                                    (data['name'], ctx.author.id,))
                                        cur.execute('SELECT anilist FROM users WHERE id = %s;', (ctx.author.id,))
                                        username = cur.fetchone()[0]
                                        db.commit()
                                        cur.close()
                                        db.close()
                                    except TypeError:
                                        cur.execute('INSERT INTO users (id, anilist) VALUES (%s, %s)',
                                                    (ctx.author.id, data['name']))
                                        cur.execute('SELECT anilist FROM users WHERE id = %s;', (ctx.author.id,))
                                        username = cur.fetchone()[0]
                                        db.commit()
                                        cur.close()
                                        db.close()
                                    setanilist_embed = discord.Embed(title='Set AniList Profile `%s`' % username,
                                                                     color=0x4169E1)
                                    setanilist_embed.add_field(name='Anime Stats',
                                                               value=f'Anime Count: {anime_count}\n'
                                                                     f'Mean Score: {anime_mean_score}\n'
                                                                     f'Days Watched: {anime_days_watched}\n'
                                                                     f'Episodes: {anime_episodes_watched}\n',
                                                               inline=True)
                                    setanilist_embed.add_field(name='Manga Stats',
                                                               value=f'Manga Count: {manga_count}\n'
                                                                     f'Mean Score: {manga_mean_score}\n'
                                                                     f'Chapters Read: {manga_chapters_read}\n'
                                                                     f'Volumes Read: {manga_volumes_read}\n',
                                                               inline=True)
                                    setanilist_embed.add_field(name='Anime List',
                                                               value='https://anilist.co/user/%s/animelist' %
                                                                     data['name'],
                                                               inline=False)
                                    setanilist_embed.add_field(name='Manga List',
                                                               value='https://anilist.co/user/%s/mangalist' %
                                                                     data['name'],
                                                               inline=False)
                                    if data['avatar']['large']:
                                        setanilist_embed.set_thumbnail(url=data['avatar']['large'])
                                    await ctx.channel.send(embed=setanilist_embed)
                                    logger.info('Server: %s | Response: Set AniList - %s' % (ctx.guild.name,
                                                                                                 username))
                                except Exception as e:
                                    error_embed = discord.Embed(
                                        title='An error occurred while setting the AniList Profile `%s`' % username,
                                        color=0xff0000)
                                    await ctx.channel.send(embed=error_embed)
                                    logger.exception(e)
                            else:
                                error_embed = discord.Embed(
                                    title='The user `%s` cannot be found on AniList' % username,
                                    color=0xff0000)
                                await ctx.channel.send(embed=error_embed)
                                logger.info('Server: %s | Response: Not found' % ctx.guild.name)

                elif site == 'MyAnimeList' or site == 'myanimelist' or site == 'mal':
                    aio_jikan = AioJikan()
                    try:
                        user = await aio_jikan.user(username=username)
                        try:
                            anime = user.get('anime_stats')
                            manga = user.get('manga_stats')
                            anime_days_watched = anime.get('days_watched')
                            anime_mean_score = anime.get('mean_score')
                            anime_watching = anime.get('watching')
                            anime_completed = anime.get('completed')
                            anime_on_hold = anime.get('on_hold')
                            anime_dropped = anime.get('dropped')
                            anime_plan_to_watch = anime.get('plan_to_watch')
                            anime_total_entries = anime.get('total_entries')
                            anime_rewatched = anime.get('rewatched')
                            anime_episodes_watched = anime.get('episodes_watched')
                            manga_days_read = manga.get('days_read')
                            manga_mean_score = manga.get('mean_score')
                            manga_reading = manga.get('reading')
                            manga_completed = manga.get('completed')
                            manga_on_hold = manga.get('on_hold')
                            manga_dropped = manga.get('dropped')
                            manga_plan_to_read = manga.get('plan_to_read')
                            manga_reread = manga.get('reread')
                            manga_total_entries = manga.get('total_entries')
                            manga_chapters_read = manga.get('chapters_read')
                            manga_volumes_read = manga.get('volumes_read')
                            db = psycopg2.connect(host=config.DB_HOST, dbname=config.DB_NAME, user=config.DB_USER,
                                                  password=config.BD_PASSWORD)
                            cur = db.cursor()
                            try:
                                cur.execute('UPDATE users SET myanimelist = %s WHERE id = %s;',
                                            (user.get('username'), ctx.author.id,))
                                cur.execute('SELECT myanimelist FROM users WHERE id = %s;', (ctx.author.id,))
                                username = cur.fetchone()[0]
                                db.commit()
                                cur.close()
                                db.close()
                            except TypeError:
                                cur.execute('INSERT INTO users (id, myanimelist) VALUES (%s, %s)',
                                            (ctx.author.id, user.get('username')))
                                cur.execute('SELECT myanimelist FROM users WHERE id = %s;', (ctx.author.id,))
                                username = cur.fetchone()[0]
                                db.commit()
                                cur.close()
                                db.close()
                            setmyanimelist_embed = discord.Embed(title='Set MyAnimeList Profile `%s`' % username
                                                                       ,
                                                                 color=0x4169E1)
                            setmyanimelist_embed.add_field(name='Anime Stats',
                                                           value=f'Days Watched: {anime_days_watched}\n'
                                                                 f'Mean Score: {anime_mean_score}\n'
                                                                 f'Watching: {anime_watching}\n'
                                                                 f'Completed: {anime_completed}\n'
                                                                 f'On-Hold: {anime_on_hold}\n'
                                                                 f'Dropped: {anime_dropped}\n'
                                                                 f'Plan to Watch: {anime_plan_to_watch}\n'
                                                                 f'Total Entries: {anime_total_entries}\n'
                                                                 f'Rewatched: {anime_rewatched}\n'
                                                                 f'Episodes: {anime_episodes_watched}\n',
                                                           inline=True)
                            setmyanimelist_embed.add_field(name='Manga Stats',
                                                           value=f'Days Read: {manga_days_read}\n'
                                                                 f'Mean Score: {manga_mean_score}\n'
                                                                 f'Reading: {manga_reading}\n'
                                                                 f'Completed: {manga_completed}\n'
                                                                 f'On-Hold: {manga_on_hold}\n'
                                                                 f'Dropped: {manga_dropped}\n'
                                                                 f'Plan to Read: {manga_plan_to_read}\n'
                                                                 f'Reread: {manga_reread}\n'
                                                                 f'Total Entries: {manga_total_entries}\n'
                                                                 f'Chapters Read: {manga_chapters_read}\n'
                                                                 f'Volumes Read: {manga_volumes_read}\n',
                                                           inline=True)
                            setmyanimelist_embed.add_field(name='Anime List',
                                                           value='https://myanimelist.net/animelist/%s' % user.get(
                                                               'username'),
                                                           inline=False)
                            setmyanimelist_embed.add_field(name='Manga List',
                                                           value='https://myanimelist.net/mangalist/%s' % user.get(
                                                               'username'),
                                                           inline=False)
                            if user.get('image_url'):
                                setmyanimelist_embed.set_thumbnail(url=user.get('image_url'))
                            await ctx.channel.send(embed=setmyanimelist_embed)
                            logger.info('Server: %s | Response: Set MyAnimeList - %s' %
                                            (ctx.guild.name, username))
                        except Exception as e:
                            error_embed = discord.Embed(
                                title='An error occurred while setting the MyAnimeList Profile `%s`' % username,
                                color=0xff0000)
                            await ctx.channel.send(embed=error_embed)
                            logger.exception(e)
                    except:
                        error_embed = discord.Embed(
                            title='The user `%s` cannot be found on MyAnimeList'
                                  % username,
                            color=0xff0000)
                        await ctx.channel.send(embed=error_embed)
                        logger.info('Server: %s | Response: Not found' % ctx.guild.name)
                    await aio_jikan.close()

                else:
                    prefix = get_prefix(ctx)
                    example_site = random.choice(example_sites)
                    example_username = ctx.author.name
                    example = '`%ssetprofile %s %s`' % (prefix, example_site, example_username)
                    error_embed = discord.Embed(title='Wrong arguments. Example: %s' % example,
                                                color=0xff0000)
                    await ctx.channel.send(embed=error_embed)
                    await ctx.command.reset_cooldown(ctx)
                    logger.info('Server: %s | Response: Wrong arguments' % ctx.guild.name)

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
                logger.info('Server: %s | Response: Profiles - %s' % (ctx.guild.name, user_name))
            else:
                error_embed = discord.Embed(title='Missing required argument',
                                            color=0xff0000)
                await ctx.channel.send(embed=error_embed)
                await ctx.command.reset_cooldown(ctx)
                logger.info('Server: %s | Response: Missing required argument' % ctx.guild.name)
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
            logger.info('Server: %s | Response: Profiles - %s' % (ctx.guild.name, ctx.author.name))
