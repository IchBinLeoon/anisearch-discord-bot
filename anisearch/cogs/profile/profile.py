from typing import Optional
import discord
import psycopg2
from discord.ext import commands
from anisearch import config
from anisearch.utils.database.profile import update_anilist_profile, select_anilist_profile, select_myanimelist_profile, \
    select_kitsu_profile
from anisearch.utils.database.profile import update_myanimelist_profile
from anisearch.utils.database.profile import update_kitsu_profile
from anisearch.utils.logger import logger
from anisearch.utils.queries.user_query import SEARCH_USER_QUERY
from anisearch.utils.requests import anilist_request
from anisearch.utils.requests import myanimelist_request
from anisearch.utils.requests import kitsu_request


class Profile(commands.Cog, name='Profile'):

    def __init__(self, bot):
        self.bot = bot

    async def _set_anilist_profile(self, ctx, username):
        try:
            try:
                variables = {'search': username, 'page': 1, 'amount': 15}
                data = (await anilist_request(SEARCH_USER_QUERY, variables))
            except Exception as exception:
                logger.exception(exception)
                embed = discord.Embed(title='Error', description='An error occurred while setting the AniList Profile '
                                                                 '`{}`.'.format(username),
                                      color=0xff0000, timestamp=ctx.message.created_at)
                embed.set_footer(text='Requested by {}'.format(ctx.author), icon_url=ctx.author.avatar_url)
                await ctx.channel.send(embed=embed)
            if data is not None:
                data = data['data']['User']
                set_username = update_anilist_profile(ctx, data['name'])
                if set_username:
                    embed = discord.Embed(title='Set AniList Profile {}.'.format(set_username), color=0x4169E1)
                    await ctx.channel.send(embed=embed)
                else:
                    embed = discord.Embed(title='Error',
                                          description='An error occurred while setting the AniList Profile '
                                                      '`{}`.'.format(username),
                                          color=0xff0000, timestamp=ctx.message.created_at)
                    embed.set_footer(text='Requested by {}'.format(ctx.author), icon_url=ctx.author.avatar_url)
                    await ctx.channel.send(embed=embed)
            else:
                embed = discord.Embed(title='The AniList Profile `{}` could not be found.'.format(username),
                                      color=0xff0000)
                await ctx.channel.send(embed=embed)
        except Exception as exception:
            logger.exception(exception)
            embed = discord.Embed(title='Error', description='An error occurred while setting the MyAnimeList Profile '
                                                             '`{}`.'.format(username),
                                  color=0xff0000, timestamp=ctx.message.created_at)
            embed.set_footer(text='Requested by {}'.format(ctx.author), icon_url=ctx.author.avatar_url)
            await ctx.channel.send(embed=embed)

    async def _set_myanimelist_profile(self, ctx, username):
        try:
            try:
                user = await myanimelist_request('user', username)
            except Exception as exception:
                logger.exception(exception)
                embed = discord.Embed(title='Error', description='An error occurred while setting the MyAnimeList '
                                                                 'Profile `{}`.'.format(username),
                                      color=0xff0000, timestamp=ctx.message.created_at)
                embed.set_footer(text='Requested by {}'.format(ctx.author), icon_url=ctx.author.avatar_url)
                await ctx.channel.send(embed=embed)
            if user is not None:
                set_username = update_myanimelist_profile(ctx, user.get('username'))
                if set_username:
                    embed = discord.Embed(title='Set MyAnimeList Profile {}.'.format(set_username), color=0x4169E1)
                    await ctx.channel.send(embed=embed)
                else:
                    embed = discord.Embed(title='Error', description='An error occurred while setting the MyAnimeList '
                                                                     'Profile `{}`.'.format(username),
                                          color=0xff0000, timestamp=ctx.message.created_at)
                    embed.set_footer(text='Requested by {}'.format(ctx.author), icon_url=ctx.author.avatar_url)
                    await ctx.channel.send(embed=embed)
            else:
                embed = discord.Embed(title='The MyAnimeList Profile `{}` could not be found.'.format(username),
                                      color=0xff0000)
                await ctx.channel.send(embed=embed)
        except Exception as exception:
            logger.exception(exception)
            embed = discord.Embed(title='Error', description='An error occurred while setting the MyAnimeList Profile '
                                                             '`{}`.'.format(username),
                                  color=0xff0000, timestamp=ctx.message.created_at)
            embed.set_footer(text='Requested by {}'.format(ctx.author), icon_url=ctx.author.avatar_url)
            await ctx.channel.send(embed=embed)

    async def _set_kitsu_profile(self, ctx, username):
        try:
            try:
                data = await kitsu_request('user', username)
            except Exception as exception:
                logger.exception(exception)
                embed = discord.Embed(title='Error', description='An error occurred while setting the Kitsu Profile '
                                                                 '`{}`.'.format(username),
                                      color=0xff0000, timestamp=ctx.message.created_at)
                embed.set_footer(text='Requested by {}'.format(ctx.author), icon_url=ctx.author.avatar_url)
                await ctx.channel.send(embed=embed)
            if data['data'] is not None and len(data['data']) > 0:
                user = data['data'][0]
                set_username = update_kitsu_profile(ctx, user['attributes']['name'])
                if set_username:
                    embed = discord.Embed(title='Set Kitsu Profile {}.'.format(set_username), color=0x4169E1)
                    await ctx.channel.send(embed=embed)
                else:
                    embed = discord.Embed(title='Error', description='An error occurred while setting the Kitsu Profile'
                                                                     ' `{}`.'.format(username),
                                          color=0xff0000, timestamp=ctx.message.created_at)
                    embed.set_footer(text='Requested by {}'.format(ctx.author), icon_url=ctx.author.avatar_url)
                    await ctx.channel.send(embed=embed)
            else:
                embed = discord.Embed(title='The Kitsu Profile `{}` could not be found.'.format(username),
                                      color=0xff0000)
                await ctx.channel.send(embed=embed)
        except Exception as exception:
            logger.exception(exception)
            embed = discord.Embed(title='Error', description='An error occurred while setting the Kitsu Profile '
                                                             '`{}`.'.format(username),
                                  color=0xff0000, timestamp=ctx.message.created_at)
            embed.set_footer(text='Requested by {}'.format(ctx.author), icon_url=ctx.author.avatar_url)
            await ctx.channel.send(embed=embed)

    async def _show_profiles(self, ctx, user_id):
        anilist = select_anilist_profile(user_id)
        myanimelist = select_myanimelist_profile(user_id)
        kitsu = select_kitsu_profile(user_id)
        if anilist:
            anilist_profile = anilist
        else:
            anilist_profile = '*Not Set*'
        if myanimelist:
            myanimelist_profile = myanimelist
        else:
            myanimelist_profile = '*Not Set*'
        if kitsu:
            kitsu_profile = kitsu
        else:
            kitsu_profile = '*Not Set*'
        embed = discord.Embed(title=self.bot.get_user(user_id).name, color=0x4169E1)
        embed.add_field(name='AniList', value=anilist_profile,
                        inline=True)
        embed.add_field(name='MyAnimeList', value=myanimelist_profile,
                        inline=True)
        embed.add_field(name='Kitsu', value=kitsu_profile,
                        inline=True)
        await ctx.channel.send(embed=embed)

    @commands.command(name='setprofile', aliases=['set'], usage='setprofile <al|mal|kitsu> <username>',
                      brief='10s', ignore_extra=False)
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def cmd_setprofile(self, ctx, site: Optional[str], username: Optional[str]):
        """Sets an AniList, MyAnimeList or Kitsu Profile."""
        async with ctx.channel.typing():
            if site:
                if username:
                    if site == 'AniList' or site == 'anilist' or site == 'al':
                        await self._set_anilist_profile(ctx, username)
                    elif site == 'MyAnimeList' or site == 'myanimelist' or site == 'mal':
                        await self._set_myanimelist_profile(ctx, username)
                    elif site == 'Kitsu' or site == 'kitsu':
                        await self._set_kitsu_profile(ctx, username)
                    else:
                        ctx.command.reset_cooldown(ctx)
                        raise discord.ext.commands.BadArgument
                elif site.startswith('<@!'):
                    user_id = int(site.replace('<@!', '').replace('>', ''))
                    await self._show_profiles(ctx, user_id)
                else:
                    ctx.command.reset_cooldown(ctx)
                    raise discord.ext.commands.BadArgument
            else:
                await self._show_profiles(ctx, ctx.author.id)

    @commands.command(name='remove', aliases=['rm'], usage='remove', brief='10s', ignore_extra=False)
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def cmd_remove(self, ctx):
        """Removes the set AniList, MyAnimeList and Kitsu Profile."""
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
            embed = discord.Embed(title='You have no Profile set.', color=0xff0000)
            await ctx.channel.send(embed=embed)
        if profile_set:
            cur.execute('DELETE FROM users WHERE id = %s;', (ctx.author.id,))
            db.commit()
            cur.close()
            db.close()
            logger.info('Removed all Profiles for User {}'.format(ctx.author.id))
            embed = discord.Embed(title='Removed the set AniList, MyAnimeList and Kitsu Profile.', color=0x4169E1)
            await ctx.channel.send(embed=embed)
