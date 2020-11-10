import aiohttp
import discord
from discord.ext import commands

from anisearch.bot import logger
from anisearch.queries import anime_query

flags = ['--search', '--characters', '--staff', '--image', '--relations', '--links', '--streams', '--all']


class Anime(commands.Cog, name='Anime'):

    def __init__(self, client):
        self.client = client

    @commands.command(name='anime', aliases=['a'], usage='anime <title> [flag]', brief='3s', ignore_extra=False)
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def cmd_anime(self, ctx, *, title):
        """Searches for an anime with the given title and displays information about the first result such as type, status, episodes, dates, description, and more!
        |--search --characters --staff --image --relations --links --streams --all"""
        args = title.split(' ')
        if args[len(args) - 1].startswith('--'):
            if args[len(args) - 2].startswith('--'):
                error_embed = discord.Embed(title='Too many command flags', color=0xff0000)
                await ctx.channel.send(embed=error_embed)
                logger.info('Server: %s | Response: Too many command flags' % ctx.guild.name)
            elif flags.__contains__(args[len(args) - 1]):
                flag = args[len(args) - 1]

                if flag == '--search':
                    args.remove('--search')
                    separator = ' '
                    title = separator.join(args)
                    api = 'https://graphql.anilist.co'
                    query = anime_query.query
                    variables = {
                        'title': title,
                        'page': 1,
                        'amount': 15
                    }
                    async with aiohttp.ClientSession() as session:
                        async with session.post(api, json={'query': query, 'variables': variables}) as r:
                            if r.status == 200:
                                json = await r.json()
                                if json['data']['Page']['media']:
                                    data = json['data']['Page']['media']
                                    try:
                                        anime_embed = discord.Embed(title='Search results for anime "%s"' % title,
                                                                    color=0x4169E1, timestamp=ctx.message.created_at)
                                        x = 0
                                        for i in data:
                                            if data[x]['title']['english'] is None or data[x]['title']['english'] == \
                                                    data[x]['title']['romaji']:
                                                value = str('[(' + data[x]['title']['romaji'] + ')](' +
                                                            data[x]['siteUrl'] + ')')
                                            else:
                                                value = str('[(' + data[x]['title']['english'] + ')](' +
                                                            data[x]['siteUrl'] + ')')
                                            anime_embed.add_field(name=str(x + 1) + '. ' + data[x]['title']['romaji'],
                                                                  value=value, inline=False)
                                            x = x + 1
                                        anime_embed.set_thumbnail(url=data[0]['coverImage']['large'])
                                        anime_embed.set_footer(text='Requested by %s' % ctx.author,
                                                               icon_url=ctx.author.avatar_url)
                                        await ctx.channel.send(embed=anime_embed)
                                        logger.info('Server: %s | Response: Anime Search - %s'
                                                        % (ctx.guild.name, title))
                                    except Exception as e:
                                        error_embed = discord.Embed(
                                            title='An error occurred while searching for the anime `%s` with the '
                                                  'command flag `%s`' % (title, flag),
                                            color=0xff0000)
                                        await ctx.channel.send(embed=error_embed)
                                        logger.exception(e)
                                else:
                                    error_embed = discord.Embed(
                                        title='The anime `%s` does not exist in the AniList database' % title,
                                        color=0xff0000)
                                    await ctx.channel.send(embed=error_embed)
                                    logger.info('Server: %s | Response: Not found' % ctx.guild.name)
                            else:
                                error_embed = discord.Embed(
                                    title='An error occurred while searching for the anime `%s` with the '
                                          'command flag `%s`' % (title, flag),
                                    color=0xff0000)
                                await ctx.channel.send(embed=error_embed)
                                logger.info('Server: %s | Response: Error' % ctx.guild.name)

                elif flag == '--characters':
                    args.remove('--characters')
                    separator = ' '
                    title = separator.join(args)
                    api = 'https://graphql.anilist.co'
                    query = anime_query.query
                    variables = {
                        'title': title,
                        'page': 1,
                        'amount': 1
                    }
                    async with aiohttp.ClientSession() as session:
                        async with session.post(api, json={'query': query, 'variables': variables}) as r:
                            if r.status == 200:
                                json = await r.json()
                                if json['data']['Page']['media']:
                                    data = json['data']['Page']['media'][0]
                                    try:
                                        try:
                                            color = int('0x' + data['coverImage']['color'].replace('#', ''), 0)
                                        except AttributeError:
                                            color = 0x4169E1
                                        if data['title']['english'] is None or data['title']['english'] == \
                                                data['title']['romaji']:
                                            anime_embed = discord.Embed(title=data['title']['romaji'],
                                                                        color=color, url=data['siteUrl'],
                                                                        timestamp=ctx.message.created_at)
                                        else:
                                            anime_embed = discord.Embed(title='%s (%s)' % (data['title']['romaji'],
                                                                                           data['title']['english']),
                                                                        color=color, url=data['siteUrl'],
                                                                        timestamp=ctx.message.created_at)
                                        anime_embed.set_thumbnail(url=data['coverImage']['large'])
                                        if data['characters']['edges']:
                                            characters = []
                                            x = 0
                                            characters_length = int(len(data['characters']['edges']))
                                            for i in range(0, characters_length - 1):
                                                characters.append(
                                                    str('[' + data['characters']['edges'][x]['node']['name']['full']
                                                        + '](' + data['characters']['edges'][x]['node']['siteUrl'] +
                                                        ') |'))
                                                x = x + 1
                                            characters.append(
                                                str('[' + data['characters']['edges'][x]['node']['name']['full']
                                                    + '](' + data['characters']['edges'][x]['node']['siteUrl'] +
                                                    ')'))
                                        else:
                                            characters = '[-]'
                                        if len(str(characters)) > 1024:
                                            characters = characters[0:15]
                                            characters[14] = str(characters[14]).replace(' |', '...')
                                            anime_embed.add_field(name='Characters',
                                                                  value=characters.__str__()[1:-1]
                                                                  .replace("'", "").replace(',', ''), inline=True)
                                        else:
                                            anime_embed.add_field(name='Characters',
                                                                  value=characters.__str__()[1:-1]
                                                                  .replace("'", "").replace(',', ''), inline=True)
                                        anime_embed.set_footer(text='Requested by %s' % ctx.author,
                                                               icon_url=ctx.author.avatar_url)
                                        await ctx.channel.send(embed=anime_embed)
                                        logger.info('Server: %s | Response: Anime Characters - %s'
                                                        % (ctx.guild.name, data['title']['romaji']))
                                    except Exception as e:
                                        error_embed = discord.Embed(
                                            title='An error occurred while searching for the anime `%s` with the '
                                                  'command flag `%s`' % (title, flag),
                                            color=0xff0000)
                                        await ctx.channel.send(embed=error_embed)
                                        logger.exception(e)
                                else:
                                    error_embed = discord.Embed(
                                        title='The anime `%s` does not exist in the AniList database' % title,
                                        color=0xff0000)
                                    await ctx.channel.send(embed=error_embed)
                                    logger.info('Server: %s | Response: Not found' % ctx.guild.name)
                            else:
                                error_embed = discord.Embed(
                                    title='An error occurred while searching for the anime `%s` with the '
                                          'command flag `%s`' % (title, flag),
                                    color=0xff0000)
                                await ctx.channel.send(embed=error_embed)
                                logger.info('Server: %s | Response: Error' % ctx.guild.name)

                elif flag == '--staff':
                    args.remove('--staff')
                    separator = ' '
                    title = separator.join(args)
                    api = 'https://graphql.anilist.co'
                    query = anime_query.query
                    variables = {
                        'title': title,
                        'page': 1,
                        'amount': 1
                    }
                    async with aiohttp.ClientSession() as session:
                        async with session.post(api, json={'query': query, 'variables': variables}) as r:
                            if r.status == 200:
                                json = await r.json()
                                if json['data']['Page']['media']:
                                    data = json['data']['Page']['media'][0]
                                    try:
                                        try:
                                            color = int('0x' + data['coverImage']['color'].replace('#', ''), 0)
                                        except AttributeError:
                                            color = 0x4169E1
                                        if data['title']['english'] is None or data['title']['english'] == \
                                                data['title']['romaji']:
                                            anime_embed = discord.Embed(title=data['title']['romaji'],
                                                                        color=color, url=data['siteUrl'],
                                                                        timestamp=ctx.message.created_at)
                                        else:
                                            anime_embed = discord.Embed(title='%s (%s)' % (data['title']['romaji'],
                                                                                           data['title']['english']),
                                                                        color=color, url=data['siteUrl'],
                                                                        timestamp=ctx.message.created_at)
                                        anime_embed.set_thumbnail(url=data['coverImage']['large'])
                                        if data['staff']['edges']:
                                            staff = []
                                            x = 0
                                            staff_length = int(len(data['staff']['edges']))
                                            for i in range(0, staff_length - 1):
                                                staff.append(
                                                    str('[' + data['staff']['edges'][x]['node']['name']['full']
                                                        + '](' + data['staff']['edges'][x]['node']['siteUrl'] +
                                                        ') |'))
                                                x = x + 1
                                            staff.append(
                                                str('[' + data['staff']['edges'][x]['node']['name']['full']
                                                    + '](' + data['staff']['edges'][x]['node']['siteUrl'] +
                                                    ')'))
                                        else:
                                            staff = '[-]'
                                        if len(str(staff)) > 1024:
                                            staff = staff[0:15]
                                            staff[14] = str(staff[14]).replace(' |', '...')
                                            anime_embed.add_field(name='Staff',
                                                                  value=staff.__str__()[1:-1]
                                                                  .replace("'", "").replace(',', ''), inline=True)
                                        else:
                                            anime_embed.add_field(name='Staff',
                                                                  value=staff.__str__()[1:-1]
                                                                  .replace("'", "").replace(',', ''), inline=True)
                                        anime_embed.set_footer(text='Requested by %s' % ctx.author,
                                                               icon_url=ctx.author.avatar_url)
                                        await ctx.channel.send(embed=anime_embed)
                                        logger.info('Server: %s | Response: Anime Staff - %s'
                                                        % (ctx.guild.name, data['title']['romaji']))
                                    except Exception as e:
                                        error_embed = discord.Embed(
                                            title='An error occurred while searching for the anime `%s` with the '
                                                  'command flag `%s`' % (title, flag),
                                            color=0xff0000)
                                        await ctx.channel.send(embed=error_embed)
                                        logger.exception(e)
                                else:
                                    error_embed = discord.Embed(
                                        title='The anime `%s` does not exist in the AniList database' % title,
                                        color=0xff0000)
                                    await ctx.channel.send(embed=error_embed)
                                    logger.info('Server: %s | Response: Not found' % ctx.guild.name)
                            else:
                                error_embed = discord.Embed(
                                    title='An error occurred while searching for the anime `%s` with the '
                                          'command flag `%s`' % (title, flag),
                                    color=0xff0000)
                                await ctx.channel.send(embed=error_embed)
                                logger.info('Server: %s | Response: Error' % ctx.guild.name)

                elif flag == '--image':
                    args.remove('--image')
                    separator = ' '
                    title = separator.join(args)
                    api = 'https://graphql.anilist.co'
                    query = anime_query.query
                    variables = {
                        'title': title,
                        'page': 1,
                        'amount': 1
                    }
                    async with aiohttp.ClientSession() as session:
                        async with session.post(api, json={'query': query, 'variables': variables}) as r:
                            if r.status == 200:
                                json = await r.json()
                                if json['data']['Page']['media']:
                                    data = json['data']['Page']['media'][0]
                                    try:
                                        try:
                                            color = int('0x' + data['coverImage']['color'].replace('#', ''), 0)
                                        except AttributeError:
                                            color = 0x4169E1
                                        if data['title']['english'] is None or data['title']['english'] == \
                                                data['title']['romaji']:
                                            anime_embed = discord.Embed(title=data['title']['romaji'],
                                                                        color=color, url=data['siteUrl'],
                                                                        timestamp=ctx.message.created_at)
                                        else:
                                            anime_embed = discord.Embed(title='%s (%s)' % (data['title']['romaji'],
                                                                                           data['title']['english']),
                                                                        color=color, url=data['siteUrl'],
                                                                        timestamp=ctx.message.created_at)
                                        if data['coverImage']['extraLarge']:
                                            anime_embed.set_image(url=data['coverImage']['extraLarge'])
                                        elif data['coverImage']['large']:
                                            anime_embed.set_image(url=data['coverImage']['large'])
                                        else:
                                            anime_embed.set_image(url=data['coverImage']['medium'])
                                        anime_embed.set_footer(text='Requested by %s' % ctx.author,
                                                               icon_url=ctx.author.avatar_url)
                                        await ctx.channel.send(embed=anime_embed)
                                        logger.info('Server: %s | Response: Anime Image - %s'
                                                        % (ctx.guild.name, data['title']['romaji']))
                                    except Exception as e:
                                        error_embed = discord.Embed(
                                            title='An error occurred while searching for the anime `%s` with the '
                                                  'command flag `%s`' % (title, flag),
                                            color=0xff0000)
                                        await ctx.channel.send(embed=error_embed)
                                        logger.exception(e)
                                else:
                                    error_embed = discord.Embed(
                                        title='The anime `%s` does not exist in the AniList database' % title,
                                        color=0xff0000)
                                    await ctx.channel.send(embed=error_embed)
                                    logger.info('Server: %s | Response: Not found' % ctx.guild.name)
                            else:
                                error_embed = discord.Embed(
                                    title='An error occurred while searching for the anime `%s` with the '
                                          'command flag `%s`' % (title, flag),
                                    color=0xff0000)
                                await ctx.channel.send(embed=error_embed)
                                logger.info('Server: %s | Response: Error' % ctx.guild.name)

                elif flag == '--relations':
                    args.remove('--relations')
                    separator = ' '
                    title = separator.join(args)
                    api = 'https://graphql.anilist.co'
                    query = anime_query.query
                    variables = {
                        'title': title,
                        'page': 1,
                        'amount': 1
                    }
                    async with aiohttp.ClientSession() as session:
                        async with session.post(api, json={'query': query, 'variables': variables}) as r:
                            if r.status == 200:
                                json = await r.json()
                                if json['data']['Page']['media']:
                                    data = json['data']['Page']['media'][0]
                                    try:
                                        try:
                                            color = int('0x' + data['coverImage']['color'].replace('#', ''), 0)
                                        except AttributeError:
                                            color = 0x4169E1
                                        if data['title']['english'] is None or data['title']['english'] == \
                                                data['title']['romaji']:
                                            anime_embed = discord.Embed(title=data['title']['romaji'],
                                                                        color=color, url=data['siteUrl'],
                                                                        timestamp=ctx.message.created_at)
                                        else:
                                            anime_embed = discord.Embed(title='%s (%s)' % (data['title']['romaji'],
                                                                                           data['title']['english']),
                                                                        color=color, url=data['siteUrl'],
                                                                        timestamp=ctx.message.created_at)
                                        anime_embed.set_thumbnail(url=data['coverImage']['large'])
                                        if data['relations']['edges']:
                                            relations = []
                                            x = 0
                                            relations_length = int(len(data['relations']['edges']))
                                            for i in range(0, relations_length - 1):
                                                relations.append(
                                                    str('[' + data['relations']['edges'][x]['node']['title']['romaji']
                                                        + '](' + data['relations']['edges'][x]['node']['siteUrl'] +
                                                        ') |'))
                                                x = x + 1
                                            relations.append(
                                                str('[' + data['relations']['edges'][x]['node']['title']['romaji']
                                                    + '](' + data['relations']['edges'][x]['node']['siteUrl'] +
                                                    ')'))
                                        else:
                                            relations = '[-]'
                                        if len(str(relations)) > 1024:
                                            try:
                                                relations = relations[0:15]
                                                relations[14] = str(relations[14]).replace(' |', '...')
                                            except IndexError:
                                                relations = relations[0:len(relations) - 1]
                                                relations[len(relations) - 1] = \
                                                    str(relations[len(relations) - 1]).replace(' |', '...')
                                            anime_embed.add_field(name='Relations',
                                                                  value=relations.__str__()[1:-1]
                                                                  .replace("'", "").replace(',', ''), inline=True)
                                        else:
                                            anime_embed.add_field(name='Relations',
                                                                  value=relations.__str__()[1:-1]
                                                                  .replace("'", "").replace(',', ''), inline=True)
                                        anime_embed.set_footer(text='Requested by %s' % ctx.author,
                                                               icon_url=ctx.author.avatar_url)
                                        await ctx.channel.send(embed=anime_embed)
                                        logger.info('Server: %s | Response: Anime Relations - %s'
                                                        % (ctx.guild.name, data['title']['romaji']))
                                    except Exception as e:
                                        error_embed = discord.Embed(
                                            title='An error occurred while searching for the anime `%s` with the '
                                                  'command flag `%s`' % (title, flag),
                                            color=0xff0000)
                                        await ctx.channel.send(embed=error_embed)
                                        logger.exception(e)
                                else:
                                    error_embed = discord.Embed(
                                        title='The anime `%s` does not exist in the AniList database' % title,
                                        color=0xff0000)
                                    await ctx.channel.send(embed=error_embed)
                                    logger.info('Server: %s | Response: Not found' % ctx.guild.name)
                            else:
                                error_embed = discord.Embed(
                                    title='An error occurred while searching for the anime `%s` with the '
                                          'command flag `%s`' % (title, flag),
                                    color=0xff0000)
                                await ctx.channel.send(embed=error_embed)
                                logger.info('Server: %s | Response: Error' % ctx.guild.name)

                elif flag == '--links':
                    args.remove('--links')
                    separator = ' '
                    title = separator.join(args)
                    api = 'https://graphql.anilist.co'
                    query = anime_query.query
                    variables = {
                        'title': title,
                        'page': 1,
                        'amount': 1
                    }
                    async with aiohttp.ClientSession() as session:
                        async with session.post(api, json={'query': query, 'variables': variables}) as r:
                            if r.status == 200:
                                json = await r.json()
                                if json['data']['Page']['media']:
                                    data = json['data']['Page']['media'][0]
                                    try:
                                        try:
                                            color = int('0x' + data['coverImage']['color'].replace('#', ''), 0)
                                        except AttributeError:
                                            color = 0x4169E1
                                        if data['title']['english'] is None or data['title']['english'] == \
                                                data['title']['romaji']:
                                            anime_embed = discord.Embed(title=data['title']['romaji'],
                                                                        color=color, url=data['siteUrl'],
                                                                        timestamp=ctx.message.created_at)
                                        else:
                                            anime_embed = discord.Embed(title='%s (%s)' % (data['title']['romaji'],
                                                                                           data['title']['english']),
                                                                        color=color, url=data['siteUrl'],
                                                                        timestamp=ctx.message.created_at)
                                        anime_embed.set_thumbnail(url=data['coverImage']['large'])
                                        if data['externalLinks']:
                                            links = []
                                            x = 0
                                            links_length = int(len(data['externalLinks']))
                                            for i in range(0, links_length - 1):
                                                links.append(
                                                    str('[' + data['externalLinks'][x]['site']
                                                        + '](' + data['externalLinks'][x]['url'] +
                                                        ') |'))
                                                x = x + 1
                                            links.append(str('[' + data['externalLinks'][x]['site']
                                                             + '](' + data['externalLinks'][x]['url'] +
                                                             ')'))
                                        else:
                                            links = '[-]'
                                        if len(str(links)) > 1024:
                                            links = links[0:15]
                                            links[14] = str(links[14]).replace(' |', '...')
                                            anime_embed.add_field(name='Links',
                                                                  value=links.__str__()[1:-1]
                                                                  .replace("'", "").replace(',', ''), inline=True)
                                        else:
                                            anime_embed.add_field(name='Links',
                                                                  value=links.__str__()[1:-1]
                                                                  .replace("'", "").replace(',', ''), inline=True)
                                        anime_embed.set_footer(text='Requested by %s' % ctx.author,
                                                               icon_url=ctx.author.avatar_url)
                                        await ctx.channel.send(embed=anime_embed)
                                        logger.info('Server: %s | Response: Anime Links - %s'
                                                        % (ctx.guild.name, data['title']['romaji']))
                                    except Exception as e:
                                        error_embed = discord.Embed(
                                            title='An error occurred while searching for the anime `%s` with the '
                                                  'command flag `%s`' % (title, flag),
                                            color=0xff0000)
                                        await ctx.channel.send(embed=error_embed)
                                        logger.exception(e)
                                else:
                                    error_embed = discord.Embed(
                                        title='The anime `%s` does not exist in the AniList database' % title,
                                        color=0xff0000)
                                    await ctx.channel.send(embed=error_embed)
                                    logger.info('Server: %s | Response: Not found' % ctx.guild.name)
                            else:
                                error_embed = discord.Embed(
                                    title='An error occurred while searching for the anime `%s` with the '
                                          'command flag `%s`' % (title, flag),
                                    color=0xff0000)
                                await ctx.channel.send(embed=error_embed)
                                logger.info('Server: %s | Response: Error' % ctx.guild.name)

                elif flag == '--streams':
                    args.remove('--streams')
                    separator = ' '
                    title = separator.join(args)
                    api = 'https://graphql.anilist.co'
                    query = anime_query.query
                    variables = {
                        'title': title,
                        'page': 1,
                        'amount': 1
                    }
                    async with aiohttp.ClientSession() as session:
                        async with session.post(api, json={'query': query, 'variables': variables}) as r:
                            if r.status == 200:
                                json = await r.json()
                                if json['data']['Page']['media']:
                                    data = json['data']['Page']['media'][0]
                                    try:
                                        try:
                                            color = int('0x' + data['coverImage']['color'].replace('#', ''), 0)
                                        except AttributeError:
                                            color = 0x4169E1
                                        if data['title']['english'] is None or data['title']['english'] == \
                                                data['title']['romaji']:
                                            anime_embed = discord.Embed(title=data['title']['romaji'],
                                                                        color=color, url=data['siteUrl'],
                                                                        timestamp=ctx.message.created_at)
                                        else:
                                            anime_embed = discord.Embed(title='%s (%s)' % (data['title']['romaji'],
                                                                                           data['title']['english']),
                                                                        color=color, url=data['siteUrl'],
                                                                        timestamp=ctx.message.created_at)
                                        anime_embed.set_thumbnail(url=data['coverImage']['large'])
                                        if data['streamingEpisodes']:
                                            streams = []
                                            x = 0
                                            streams_length = int(len(data['streamingEpisodes']))
                                            for i in range(0, streams_length - 1):
                                                streams.append(
                                                    str(data['streamingEpisodes'][x]['site'] + ': [' +
                                                        data['streamingEpisodes'][x]['title']
                                                        + '](' + data['streamingEpisodes'][x]['url'] + ')'))
                                                x = x + 1
                                        else:
                                            streams = '-'
                                        if len(str(streams)) > 1024:
                                            streams = streams[0:6]
                                            streams[5] = str(streams[5]).replace(')', ')...')
                                            anime_embed.add_field(name='Streams', value='\n'.join(streams), inline=True)
                                        else:
                                            anime_embed.add_field(name='Streams', value='\n'.join(streams), inline=True)
                                        anime_embed.set_footer(text='Requested by %s' % ctx.author,
                                                               icon_url=ctx.author.avatar_url)
                                        await ctx.channel.send(embed=anime_embed)
                                        logger.info('Server: %s | Response: Anime Streams - %s'
                                                        % (ctx.guild.name, data['title']['romaji']))
                                    except Exception as e:
                                        error_embed = discord.Embed(
                                            title='An error occurred while searching for the anime `%s` with the '
                                                  'command flag `%s`' % (title, flag),
                                            color=0xff0000)
                                        await ctx.channel.send(embed=error_embed)
                                        logger.exception(e)
                                else:
                                    error_embed = discord.Embed(
                                        title='The anime `%s` does not exist in the AniList database' % title,
                                        color=0xff0000)
                                    await ctx.channel.send(embed=error_embed)
                                    logger.info('Server: %s | Response: Not found' % ctx.guild.name)
                            else:
                                error_embed = discord.Embed(
                                    title='An error occurred while searching for the anime `%s` with the '
                                          'command flag `%s`' % (title, flag),
                                    color=0xff0000)
                                await ctx.channel.send(embed=error_embed)
                                logger.info('Server: %s | Response: Error' % ctx.guild.name)

                elif flag == '--all':
                    args.remove('--all')
                    separator = ' '
                    title = separator.join(args)
                    api = 'https://graphql.anilist.co'
                    query = anime_query.query
                    variables = {
                        'title': title,
                        'page': 1,
                        'amount': 1
                    }
                    async with aiohttp.ClientSession() as session:
                        async with session.post(api, json={'query': query, 'variables': variables}) as r:
                            if r.status == 200:
                                json = await r.json()
                                if json['data']['Page']['media']:
                                    data = json['data']['Page']['media'][0]
                                    try:
                                        try:
                                            color = int('0x' + data['coverImage']['color'].replace('#', ''), 0)
                                        except AttributeError:
                                            color = 0x4169E1
                                        if data['title']['english'] is None or data['title']['english'] == \
                                                data['title']['romaji']:
                                            anime_embed = discord.Embed(title=data['title']['romaji'],
                                                                        color=color,
                                                                        timestamp=ctx.message.created_at)
                                        else:
                                            anime_embed = discord.Embed(title='%s (%s)' % (data['title']['romaji'],
                                                                                           data['title']['english']),
                                                                        color=color,
                                                                        timestamp=ctx.message.created_at)
                                        anime_embed.set_thumbnail(url=data['coverImage']['large'])
                                        if data['description']:
                                            if len(data['description']) < 1024:
                                                anime_embed.add_field(name='Description',
                                                                      value=data['description']
                                                                      .replace('<br>', ' ')
                                                                      .replace('</br>', ' ')
                                                                      .replace('<i>', ' ')
                                                                      .replace('</i>', ' '),
                                                                      inline=False)
                                            else:
                                                anime_embed.add_field(name='Description',
                                                                      value=data['description']
                                                                      .replace('<br>', ' ')
                                                                      .replace('</br>', ' ')
                                                                      .replace('<i>', ' ')
                                                                      .replace('</i>', ' ')[0:1021] + '...',
                                                                      inline=False)
                                        else:
                                            anime_embed.add_field(name='Description', value='-', inline=False)
                                        anime_embed.add_field(name='Type',
                                                              value=data['format'].replace('_', ' ').title()
                                                              .replace('Tv', 'TV')
                                                              .replace('Ova', 'OVA')
                                                              .replace('Ona', 'ONA'),
                                                              inline=True)
                                        anime_embed.add_field(name='Status',
                                                              value=data['status'].replace('_', ' ').title(),
                                                              inline=True)
                                        if data['status'].title() == 'Releasing':
                                            if data['nextAiringEpisode']:
                                                if data['episodes']:
                                                    anime_embed.add_field(name='Released episodes',
                                                                          value='%s (%s Total)' %
                                                                                (data['nextAiringEpisode'][
                                                                                     'episode'] - 1,
                                                                                 data['episodes']),
                                                                          inline=True)
                                                else:
                                                    anime_embed.add_field(name='Released episodes',
                                                                          value=data['nextAiringEpisode'][
                                                                                    'episode'] - 1,
                                                                          inline=True)
                                            else:
                                                anime_embed.add_field(name='Released episodes',
                                                                      value='-',
                                                                      inline=True)
                                        else:
                                            if data['episodes']:
                                                anime_embed.add_field(name='Episodes', value=data['episodes'],
                                                                      inline=True)
                                            else:
                                                anime_embed.add_field(name='Episodes', value='-', inline=True)
                                        if data['season']:
                                            if data['seasonYear']:
                                                anime_embed.add_field(name='Season',
                                                                      value='%s %s' % (data['season'].title(),
                                                                                       data['seasonYear']),
                                                                      inline=True)
                                            else:
                                                anime_embed.add_field(name='Season', value=data['season'].title(),
                                                                      inline=True)
                                        else:
                                            anime_embed.add_field(name='Season', value='-', inline=True)

                                        if data['startDate']['day']:
                                            anime_embed.add_field(name='Start date',
                                                                  value='%s/%s/%s' % (data['startDate']['day'],
                                                                                      data['startDate']['month'],
                                                                                      data['startDate']['year']),
                                                                  inline=True)
                                        else:
                                            anime_embed.add_field(name='Start date', value='-', inline=True)
                                        if data['endDate']['day']:
                                            anime_embed.add_field(name='End date',
                                                                  value='%s/%s/%s' % (data['endDate']['day'],
                                                                                      data['endDate']['month'],
                                                                                      data['endDate']['year']),
                                                                  inline=True)
                                        else:
                                            anime_embed.add_field(name='End date', value='-', inline=True)
                                        if data['duration']:
                                            if data['episodes'] == 1:
                                                anime_embed.add_field(name='Duration',
                                                                      value=str(data['duration']) + ' min',
                                                                      inline=True)
                                            else:
                                                anime_embed.add_field(name='Duration',
                                                                      value=str(data['duration']) + ' min each',
                                                                      inline=True)
                                        else:
                                            anime_embed.add_field(name='Duration', value='-', inline=True)
                                        try:
                                            anime_embed.add_field(name='Source',
                                                                  value=data['source'].replace('_', ' ').title(),
                                                                  inline=True)
                                        except AttributeError:
                                            anime_embed.add_field(name='Source', value='-', inline=True)
                                        try:
                                            anime_embed.add_field(name='Studio',
                                                                  value=data['studios']['nodes'][0]['name'],
                                                                  inline=True)
                                        except IndexError:
                                            anime_embed.add_field(name='Studio', value='-', inline=True)
                                        if data['averageScore']:
                                            anime_embed.add_field(name='Ø Score', value=data['averageScore'],
                                                                  inline=True)
                                        else:
                                            anime_embed.add_field(name='Ø Score', value='-', inline=True)
                                        if data['popularity']:
                                            anime_embed.add_field(name='Popularity', value=data['popularity'],
                                                                  inline=True)
                                        else:
                                            anime_embed.add_field(name='Popularity', value='-', inline=True)
                                        if data['favourites']:
                                            anime_embed.add_field(name='Favourites', value=data['favourites'],
                                                                  inline=True)
                                        else:
                                            anime_embed.add_field(name='Favourites', value='-', inline=True)
                                        anime_embed.add_field(name='Genres', value=', '.join(data['genres']),
                                                              inline=False)
                                        if data['synonyms']:
                                            anime_embed.add_field(name='Synonyms', value=', '.join(data['synonyms']),
                                                                  inline=False)
                                        else:
                                            anime_embed.add_field(name='Synonyms', value='-', inline=True)
                                        anime_embed.add_field(name='AniList Link', value=data['siteUrl'], inline=False)
                                        anime_embed.add_field(name='MyAnimeList Link',
                                                              value='https://myanimelist.net/anime/' + str(
                                                                  data['idMal']),
                                                              inline=False)
                                        if data['characters']['edges']:
                                            characters = []
                                            x = 0
                                            characters_length = int(len(data['characters']['edges']))
                                            for i in range(0, characters_length - 1):
                                                characters.append(
                                                    str('[' + data['characters']['edges'][x]['node']['name']['full']
                                                        + '](' + data['characters']['edges'][x]['node']['siteUrl'] +
                                                        ') |'))
                                                x = x + 1
                                            characters.append(
                                                str('[' + data['characters']['edges'][x]['node']['name']['full']
                                                    + '](' + data['characters']['edges'][x]['node']['siteUrl'] +
                                                    ')'))
                                        else:
                                            characters = '[-]'
                                        if len(str(characters)) > 1024:
                                            characters = characters[0:15]
                                            characters[14] = str(characters[14]).replace(' |', '...')
                                            anime_embed.add_field(name='Characters',
                                                                  value=characters.__str__()[1:-1]
                                                                  .replace("'", "").replace(',', ''), inline=False)
                                        else:
                                            anime_embed.add_field(name='Characters',
                                                                  value=characters.__str__()[1:-1]
                                                                  .replace("'", "").replace(',', ''), inline=False)
                                        if data['staff']['edges']:
                                            staff = []
                                            x = 0
                                            staff_length = int(len(data['staff']['edges']))
                                            for i in range(0, staff_length - 1):
                                                staff.append(
                                                    str('[' + data['staff']['edges'][x]['node']['name']['full']
                                                        + '](' + data['staff']['edges'][x]['node']['siteUrl'] +
                                                        ') |'))
                                                x = x + 1
                                            staff.append(
                                                str('[' + data['staff']['edges'][x]['node']['name']['full']
                                                    + '](' + data['staff']['edges'][x]['node']['siteUrl'] +
                                                    ')'))
                                        else:
                                            staff = '[-]'
                                        if len(str(staff)) > 1024:
                                            staff = staff[0:15]
                                            staff[14] = str(staff[14]).replace(' |', '...')
                                            anime_embed.add_field(name='Staff',
                                                                  value=staff.__str__()[1:-1]
                                                                  .replace("'", "").replace(',', ''), inline=False)
                                        else:
                                            anime_embed.add_field(name='Staff',
                                                                  value=staff.__str__()[1:-1]
                                                                  .replace("'", "").replace(',', ''), inline=False)
                                        if data['relations']['edges']:
                                            relations = []
                                            x = 0
                                            relations_length = int(len(data['relations']['edges']))
                                            for i in range(0, relations_length - 1):
                                                relations.append(
                                                    str('[' + data['relations']['edges'][x]['node']['title']['romaji']
                                                        + '](' + data['relations']['edges'][x]['node']['siteUrl'] +
                                                        ') |'))
                                                x = x + 1
                                            relations.append(
                                                str('[' + data['relations']['edges'][x]['node']['title']['romaji']
                                                    + '](' + data['relations']['edges'][x]['node']['siteUrl'] +
                                                    ')'))
                                        else:
                                            relations = '[-]'
                                        if len(str(relations)) > 1024:
                                            try:
                                                relations = relations[0:15]
                                                relations[14] = str(relations[14]).replace(' |', '...')
                                            except IndexError:
                                                relations = relations[0:len(relations) - 1]
                                                relations[len(relations) - 1] = \
                                                    str(relations[len(relations) - 1]).replace(' |', '...')
                                            anime_embed.add_field(name='Relations',
                                                                  value=relations.__str__()[1:-1]
                                                                  .replace("'", "").replace(',', ''), inline=False)
                                        else:
                                            anime_embed.add_field(name='Relations',
                                                                  value=relations.__str__()[1:-1]
                                                                  .replace("'", "").replace(',', ''), inline=False)
                                        if data['externalLinks']:
                                            links = []
                                            x = 0
                                            links_length = int(len(data['externalLinks']))
                                            for i in range(0, links_length - 1):
                                                links.append(
                                                    str('[' + data['externalLinks'][x]['site']
                                                        + '](' + data['externalLinks'][x]['url'] +
                                                        ') |'))
                                                x = x + 1
                                            links.append(str('[' + data['externalLinks'][x]['site']
                                                             + '](' + data['externalLinks'][x]['url'] +
                                                             ')'))
                                        else:
                                            links = '[-]'
                                        if len(str(links)) > 1024:
                                            links = links[0:15]
                                            links[14] = str(links[14]).replace(' |', '...')
                                            anime_embed.add_field(name='Links',
                                                                  value=links.__str__()[1:-1]
                                                                  .replace("'", "").replace(',', ''), inline=False)
                                        else:
                                            anime_embed.add_field(name='Links',
                                                                  value=links.__str__()[1:-1]
                                                                  .replace("'", "").replace(',', ''), inline=False)
                                        if data['streamingEpisodes']:
                                            streams = []
                                            x = 0
                                            streams_length = int(len(data['streamingEpisodes']))
                                            for i in range(0, streams_length - 1):
                                                streams.append(
                                                    str(data['streamingEpisodes'][x]['site'] + ': [' +
                                                        data['streamingEpisodes'][x]['title']
                                                        + '](' + data['streamingEpisodes'][x]['url'] +
                                                        ')'))
                                                x = x + 1
                                        else:
                                            streams = '-'
                                        if len(str(streams)) > 1024:
                                            streams = streams[0:6]
                                            streams[5] = str(streams[5]).replace(')', ')...')
                                            anime_embed.add_field(name='Streams', value='\n'.join(streams),
                                                                  inline=False)
                                        else:
                                            anime_embed.add_field(name='Streams', value='\n'.join(streams),
                                                                  inline=False)
                                        if data['coverImage']['extraLarge']:
                                            anime_embed.set_image(url=data['coverImage']['extraLarge'])
                                        elif data['coverImage']['large']:
                                            anime_embed.set_image(url=data['coverImage']['large'])
                                        else:
                                            anime_embed.set_image(url=data['coverImage']['medium'])
                                        anime_embed.set_footer(text='Requested by %s' % ctx.author,
                                                               icon_url=ctx.author.avatar_url)
                                        await ctx.channel.send(embed=anime_embed)
                                        logger.info('Server: %s | Response: Anime All - %s' % (ctx.guild.name,
                                                                                                   data['title'][
                                                                                                             'romaji']))
                                    except Exception as e:
                                        error_embed = discord.Embed(
                                            title='An error occurred while searching for the anime `%s` with the '
                                                  'command flag `%s`' % (title, flag),
                                            color=0xff0000)
                                        await ctx.channel.send(embed=error_embed)
                                        logger.exception(e)
                                else:
                                    error_embed = discord.Embed(
                                        title='The anime `%s` does not exist in the AniList database' % title,
                                        color=0xff0000)
                                    await ctx.channel.send(embed=error_embed)
                                    logger.info('Server: %s | Response: Not found' % ctx.guild.name)
                            else:
                                error_embed = discord.Embed(
                                    title='An error occurred while searching for the anime `%s` with the '
                                          'command flag `%s`' % (title, flag),
                                    color=0xff0000)
                                await ctx.channel.send(embed=error_embed)
                                logger.info('Server: %s | Response: Error' % ctx.guild.name)

            else:
                error_embed = discord.Embed(title='The command flag is invalid or cannot be used with this command',
                                            color=0xff0000)
                await ctx.channel.send(embed=error_embed)
                logger.info('Server: %s | Response: Wrong command flags' % ctx.guild.name)

        else:
            api = 'https://graphql.anilist.co'
            query = anime_query.query
            variables = {
                'title': title,
                'page': 1,
                'amount': 1
            }
            async with aiohttp.ClientSession() as session:
                async with session.post(api, json={'query': query, 'variables': variables}) as r:
                    if r.status == 200:
                        json = await r.json()
                        if json['data']['Page']['media']:
                            data = json['data']['Page']['media'][0]
                            try:
                                try:
                                    color = int('0x' + data['coverImage']['color'].replace('#', ''), 0)
                                except AttributeError:
                                    color = 0x4169E1
                                if data['title']['english'] is None or data['title']['english'] == \
                                        data['title']['romaji']:
                                    anime_embed = discord.Embed(title=data['title']['romaji'],
                                                                color=color,
                                                                timestamp=ctx.message.created_at)
                                else:
                                    anime_embed = discord.Embed(title='%s (%s)' % (data['title']['romaji'],
                                                                                   data['title']['english']),
                                                                color=color,
                                                                timestamp=ctx.message.created_at)
                                anime_embed.set_thumbnail(url=data['coverImage']['large'])
                                if data['description']:
                                    if len(data['description']) < 1024:
                                        anime_embed.add_field(name='Description',
                                                              value=data['description']
                                                              .replace('<br>', ' ')
                                                              .replace('</br>', ' ')
                                                              .replace('<i>', ' ')
                                                              .replace('</i>', ' '),
                                                              inline=False)
                                    else:
                                        anime_embed.add_field(name='Description',
                                                              value=data['description']
                                                              .replace('<br>', ' ')
                                                              .replace('</br>', ' ')
                                                              .replace('<i>', ' ')
                                                              .replace('</i>', ' ')[0:1021] + '...',
                                                              inline=False)
                                else:
                                    anime_embed.add_field(name='Description', value='-', inline=False)
                                anime_embed.add_field(name='Type', value=data['format'].replace('_', ' ').title()
                                                      .replace('Tv', 'TV')
                                                      .replace('Ova', 'OVA')
                                                      .replace('Ona', 'ONA'),
                                                      inline=True)
                                anime_embed.add_field(name='Status', value=data['status'].replace('_', ' ').title(),
                                                      inline=True)
                                if data['status'].title() == 'Releasing':
                                    if data['nextAiringEpisode']:
                                        if data['episodes']:
                                            anime_embed.add_field(name='Released episodes',
                                                                  value='%s (%s Total)' %
                                                                        (data['nextAiringEpisode']['episode'] - 1,
                                                                         data['episodes']),
                                                                  inline=True)
                                        else:
                                            anime_embed.add_field(name='Released episodes',
                                                                  value=data['nextAiringEpisode']['episode'] - 1,
                                                                  inline=True)
                                    else:
                                        anime_embed.add_field(name='Released episodes',
                                                              value='-',
                                                              inline=True)
                                else:
                                    if data['episodes']:
                                        anime_embed.add_field(name='Episodes', value=data['episodes'], inline=True)
                                    else:
                                        anime_embed.add_field(name='Episodes', value='-', inline=True)
                                if data['season']:
                                    if data['seasonYear']:
                                        anime_embed.add_field(name='Season', value='%s %s' % (data['season'].title(),
                                                                                              data['seasonYear']),
                                                              inline=True)
                                    else:
                                        anime_embed.add_field(name='Season', value=data['season'].title(), inline=True)
                                else:
                                    anime_embed.add_field(name='Season', value='-', inline=True)

                                if data['startDate']['day']:
                                    anime_embed.add_field(name='Start date',
                                                          value='%s/%s/%s' % (data['startDate']['day'],
                                                                              data['startDate']['month'],
                                                                              data['startDate']['year']),
                                                          inline=True)
                                else:
                                    anime_embed.add_field(name='Start date', value='-', inline=True)
                                if data['endDate']['day']:
                                    anime_embed.add_field(name='End date', value='%s/%s/%s' % (data['endDate']['day'],
                                                                                               data['endDate']['month'],
                                                                                               data['endDate']['year']),
                                                          inline=True)
                                else:
                                    anime_embed.add_field(name='End date', value='-', inline=True)
                                if data['duration']:
                                    if data['episodes'] == 1:
                                        anime_embed.add_field(name='Duration', value=str(data['duration']) + ' min',
                                                              inline=True)
                                    else:
                                        anime_embed.add_field(name='Duration',
                                                              value=str(data['duration']) + ' min each',
                                                              inline=True)
                                else:
                                    anime_embed.add_field(name='Duration', value='-', inline=True)
                                try:
                                    anime_embed.add_field(name='Source', value=data['source'].replace('_', ' ').title(),
                                                          inline=True)
                                except AttributeError:
                                    anime_embed.add_field(name='Source', value='-', inline=True)
                                try:
                                    anime_embed.add_field(name='Studio', value=data['studios']['nodes'][0]['name'],
                                                          inline=True)
                                except IndexError:
                                    anime_embed.add_field(name='Studio', value='-', inline=True)
                                if data['averageScore']:
                                    anime_embed.add_field(name='Ø Score', value=data['averageScore'], inline=True)
                                else:
                                    anime_embed.add_field(name='Ø Score', value='-', inline=True)
                                if data['popularity']:
                                    anime_embed.add_field(name='Popularity', value=data['popularity'], inline=True)
                                else:
                                    anime_embed.add_field(name='Popularity', value='-', inline=True)
                                if data['favourites']:
                                    anime_embed.add_field(name='Favourites', value=data['favourites'], inline=True)
                                else:
                                    anime_embed.add_field(name='Favourites', value='-', inline=True)
                                if data['genres']:
                                    anime_embed.add_field(name='Genres', value=', '.join(data['genres']), inline=False)
                                else:
                                    anime_embed.add_field(name='Genres', value='-', inline=False)
                                if data['synonyms']:
                                    anime_embed.add_field(name='Synonyms', value=', '.join(data['synonyms']),
                                                          inline=False)
                                else:
                                    anime_embed.add_field(name='Synonyms', value='-', inline=True)
                                if data['siteUrl']:
                                    anime_embed.add_field(name='AniList Link', value=data['siteUrl'], inline=False)
                                else:
                                    anime_embed.add_field(name='AniList Link', value='-', inline=False)
                                if data['idMal']:
                                    anime_embed.add_field(name='MyAnimeList Link',
                                                          value='https://myanimelist.net/anime/' + str(data['idMal']),
                                                          inline=False)
                                else:
                                    anime_embed.add_field(name='MyAnimeList Link', value='-', inline=False)
                                anime_embed.set_footer(text='Requested by %s' % ctx.author,
                                                       icon_url=ctx.author.avatar_url)
                                await ctx.channel.send(embed=anime_embed)
                                logger.info('Server: %s | Response: Anime - %s' % (ctx.guild.name,
                                                                                       data['title']['romaji']))
                            except Exception as e:
                                error_embed = discord.Embed(
                                    title='An error occurred while searching for the anime `%s`' % title,
                                    color=0xff0000)
                                await ctx.channel.send(embed=error_embed)
                                logger.exception(e)
                        else:
                            error_embed = discord.Embed(
                                title='The anime `%s` does not exist in the AniList database' % title,
                                color=0xff0000)
                            await ctx.channel.send(embed=error_embed)
                            logger.info('Server: %s | Response: Not found' % ctx.guild.name)
                    else:
                        error_embed = discord.Embed(
                            title='An error occurred while searching for the anime `%s`' % title,
                            color=0xff0000)
                        await ctx.channel.send(embed=error_embed)
                        logger.info('Server: %s | Response: API Error' % ctx.guild.name)
