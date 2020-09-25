import aiohttp
import discord
from discord.ext import commands

import main
from modules.manga import manga_query

flags = ['--search', '--characters', '--staff', '--image', '--relations', '--links', '--all']


class Manga(commands.Cog, name='Manga'):

    def __init__(self, client):
        self.client = client

    @commands.command(name='manga', aliases=['m'], usage='manga <title>',
                      brief='3s --search --characters --staff --image --relations --links --all',
                      ignore_extra=False)
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def cmd_manga(self, ctx, *, title):
        """Searches for a manga with the given title and displays information about the first result such as type, status, chapters, dates, description, and more!"""
        args = title.split(' ')
        if args[len(args) - 1].startswith('--'):
            if args[len(args) - 2].startswith('--'):
                error_embed = discord.Embed(title='Too many command flags', color=0xff0000)
                await ctx.channel.send(embed=error_embed)
                main.logger.info('Server: %s | Response: Too many command flags' % ctx.guild.name)
            elif flags.__contains__(args[len(args) - 1]):
                flag = args[len(args) - 1]

                if flag == '--search':
                    args.remove('--search')
                    separator = ' '
                    title = separator.join(args)
                    api = 'https://graphql.anilist.co'
                    query = manga_query.query
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
                                        manga_embed = discord.Embed(title='Search results for manga "%s"' % title,
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
                                            manga_embed.add_field(name=str(x + 1) + '. ' + data[x]['title']['romaji'],
                                                                  value=value, inline=False)
                                            x = x + 1
                                        manga_embed.set_thumbnail(url=data[0]['coverImage']['large'])
                                        manga_embed.set_footer(text='Requested by %s' % ctx.author,
                                                               icon_url=ctx.author.avatar_url)
                                        await ctx.channel.send(embed=manga_embed)
                                        main.logger.info('Server: %s | Response: Manga Search - %s'
                                                         % (ctx.guild.name, title))
                                    except Exception as e:
                                        error_embed = discord.Embed(
                                            title='An error occurred while searching for the manga `%s` with the '
                                                  'command flag `%s`' % (title, flag),
                                            color=0xff0000)
                                        await ctx.channel.send(embed=error_embed)
                                        main.logger.exception(e)
                                else:
                                    error_embed = discord.Embed(
                                        title='The manga `%s` does not exist in the AniList database' % title,
                                        color=0xff0000)
                                    await ctx.channel.send(embed=error_embed)
                                    main.logger.info('Server: %s | Response: Not found' % ctx.guild.name)
                            else:
                                error_embed = discord.Embed(
                                    title='An error occurred while searching for the manga `%s` with the '
                                          'command flag `%s`' % (title, flag),
                                    color=0xff0000)
                                await ctx.channel.send(embed=error_embed)
                                main.logger.info('Server: %s | Response: Error' % ctx.guild.name)

                elif flag == '--characters':
                    args.remove('--characters')
                    separator = ' '
                    title = separator.join(args)
                    api = 'https://graphql.anilist.co'
                    query = manga_query.query
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
                                            manga_embed = discord.Embed(title=data['title']['romaji'],
                                                                        color=color, url=data['siteUrl'],
                                                                        timestamp=ctx.message.created_at)
                                        else:
                                            manga_embed = discord.Embed(title='%s (%s)' % (data['title']['romaji'],
                                                                                           data['title']['english']),
                                                                        color=color, url=data['siteUrl'],
                                                                        timestamp=ctx.message.created_at)
                                        manga_embed.set_thumbnail(url=data['coverImage']['large'])
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
                                            manga_embed.add_field(name='Characters',
                                                                  value=characters.__str__()[1:-1]
                                                                  .replace("'", "").replace(',', ''), inline=True)
                                        else:
                                            manga_embed.add_field(name='Characters',
                                                                  value=characters.__str__()[1:-1]
                                                                  .replace("'", "").replace(',', ''), inline=True)
                                        manga_embed.set_footer(text='Requested by %s' % ctx.author,
                                                               icon_url=ctx.author.avatar_url)
                                        await ctx.channel.send(embed=manga_embed)
                                        main.logger.info('Server: %s | Response: Manga Characters - %s'
                                                         % (ctx.guild.name, data['title']['romaji']))
                                    except Exception as e:
                                        error_embed = discord.Embed(
                                            title='An error occurred while searching for the manga `%s` with the '
                                                  'command flag `%s`' % (title, flag),
                                            color=0xff0000)
                                        await ctx.channel.send(embed=error_embed)
                                        main.logger.exception(e)
                                else:
                                    error_embed = discord.Embed(
                                        title='The manga `%s` does not exist in the AniList database' % title,
                                        color=0xff0000)
                                    await ctx.channel.send(embed=error_embed)
                                    main.logger.info('Server: %s | Response: Not found' % ctx.guild.name)
                            else:
                                error_embed = discord.Embed(
                                    title='An error occurred while searching for the manga `%s` with the '
                                          'command flag `%s`' % (title, flag),
                                    color=0xff0000)
                                await ctx.channel.send(embed=error_embed)
                                main.logger.info('Server: %s | Response: Error' % ctx.guild.name)

                elif flag == '--staff':
                    args.remove('--staff')
                    separator = ' '
                    title = separator.join(args)
                    api = 'https://graphql.anilist.co'
                    query = manga_query.query
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
                                            manga_embed = discord.Embed(title=data['title']['romaji'],
                                                                        color=color, url=data['siteUrl'],
                                                                        timestamp=ctx.message.created_at)
                                        else:
                                            manga_embed = discord.Embed(title='%s (%s)' % (data['title']['romaji'],
                                                                                           data['title']['english']),
                                                                        color=color, url=data['siteUrl'],
                                                                        timestamp=ctx.message.created_at)
                                        manga_embed.set_thumbnail(url=data['coverImage']['large'])
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
                                            manga_embed.add_field(name='Staff',
                                                                  value=staff.__str__()[1:-1]
                                                                  .replace("'", "").replace(',', ''), inline=True)
                                        else:
                                            manga_embed.add_field(name='Staff',
                                                                  value=staff.__str__()[1:-1]
                                                                  .replace("'", "").replace(',', ''), inline=True)
                                        manga_embed.set_footer(text='Requested by %s' % ctx.author,
                                                               icon_url=ctx.author.avatar_url)
                                        await ctx.channel.send(embed=manga_embed)
                                        main.logger.info('Server: %s | Response: Manga Staff - %s'
                                                         % (ctx.guild.name, data['title']['romaji']))
                                    except Exception as e:
                                        error_embed = discord.Embed(
                                            title='An error occurred while searching for the manga `%s` with the '
                                                  'command flag `%s`' % (title, flag),
                                            color=0xff0000)
                                        await ctx.channel.send(embed=error_embed)
                                        main.logger.exception(e)
                                else:
                                    error_embed = discord.Embed(
                                        title='The manga `%s` does not exist in the AniList database' % title,
                                        color=0xff0000)
                                    await ctx.channel.send(embed=error_embed)
                                    main.logger.info('Server: %s | Response: Not found' % ctx.guild.name)
                            else:
                                error_embed = discord.Embed(
                                    title='An error occurred while searching for the manga `%s` with the '
                                          'command flag `%s`' % (title, flag),
                                    color=0xff0000)
                                await ctx.channel.send(embed=error_embed)
                                main.logger.info('Server: %s | Response: Error' % ctx.guild.name)

                elif flag == '--image':
                    args.remove('--image')
                    separator = ' '
                    title = separator.join(args)
                    api = 'https://graphql.anilist.co'
                    query = manga_query.query
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
                                            manga_embed = discord.Embed(title=data['title']['romaji'],
                                                                        color=color, url=data['siteUrl'],
                                                                        timestamp=ctx.message.created_at)
                                        else:
                                            manga_embed = discord.Embed(title='%s (%s)' % (data['title']['romaji'],
                                                                                           data['title']['english']),
                                                                        color=color, url=data['siteUrl'],
                                                                        timestamp=ctx.message.created_at)
                                        if data['coverImage']['extraLarge']:
                                            manga_embed.set_image(url=data['coverImage']['extraLarge'])
                                        elif data['coverImage']['large']:
                                            manga_embed.set_image(url=data['coverImage']['large'])
                                        else:
                                            manga_embed.set_image(url=data['coverImage']['medium'])
                                        manga_embed.set_footer(text='Requested by %s' % ctx.author,
                                                               icon_url=ctx.author.avatar_url)
                                        await ctx.channel.send(embed=manga_embed)
                                        main.logger.info('Server: %s | Response: Manga Image - %s'
                                                         % (ctx.guild.name, data['title']['romaji']))
                                    except Exception as e:
                                        error_embed = discord.Embed(
                                            title='An error occurred while searching for the manga `%s` with the '
                                                  'command flag `%s`' % (title, flag),
                                            color=0xff0000)
                                        await ctx.channel.send(embed=error_embed)
                                        main.logger.exception(e)
                                else:
                                    error_embed = discord.Embed(
                                        title='The manga `%s` does not exist in the AniList database' % title,
                                        color=0xff0000)
                                    await ctx.channel.send(embed=error_embed)
                                    main.logger.info('Server: %s | Response: Not found' % ctx.guild.name)
                            else:
                                error_embed = discord.Embed(
                                    title='An error occurred while searching for the manga `%s` with the '
                                          'command flag `%s`' % (title, flag),
                                    color=0xff0000)
                                await ctx.channel.send(embed=error_embed)
                                main.logger.info('Server: %s | Response: Error' % ctx.guild.name)

                elif flag == '--relations':
                    args.remove('--relations')
                    separator = ' '
                    title = separator.join(args)
                    api = 'https://graphql.anilist.co'
                    query = manga_query.query
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
                                            manga_embed = discord.Embed(title=data['title']['romaji'],
                                                                        color=color, url=data['siteUrl'],
                                                                        timestamp=ctx.message.created_at)
                                        else:
                                            manga_embed = discord.Embed(title='%s (%s)' % (data['title']['romaji'],
                                                                                           data['title']['english']),
                                                                        color=color, url=data['siteUrl'],
                                                                        timestamp=ctx.message.created_at)
                                        manga_embed.set_thumbnail(url=data['coverImage']['large'])
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
                                            manga_embed.add_field(name='Relations',
                                                                  value=relations.__str__()[1:-1]
                                                                  .replace("'", "").replace(',', ''), inline=True)
                                        else:
                                            manga_embed.add_field(name='Relations',
                                                                  value=relations.__str__()[1:-1]
                                                                  .replace("'", "").replace(',', ''), inline=True)
                                        manga_embed.set_footer(text='Requested by %s' % ctx.author,
                                                               icon_url=ctx.author.avatar_url)
                                        await ctx.channel.send(embed=manga_embed)
                                        main.logger.info('Server: %s | Response: Manga Relations - %s'
                                                         % (ctx.guild.name, data['title']['romaji']))
                                    except Exception as e:
                                        error_embed = discord.Embed(
                                            title='An error occurred while searching for the manga `%s` with the '
                                                  'command flag `%s`' % (title, flag),
                                            color=0xff0000)
                                        await ctx.channel.send(embed=error_embed)
                                        main.logger.exception(e)
                                else:
                                    error_embed = discord.Embed(
                                        title='The manga `%s` does not exist in the AniList database' % title,
                                        color=0xff0000)
                                    await ctx.channel.send(embed=error_embed)
                                    main.logger.info('Server: %s | Response: Not found' % ctx.guild.name)
                            else:
                                error_embed = discord.Embed(
                                    title='An error occurred while searching for the manga `%s` with the '
                                          'command flag `%s`' % (title, flag),
                                    color=0xff0000)
                                await ctx.channel.send(embed=error_embed)
                                main.logger.info('Server: %s | Response: Error' % ctx.guild.name)

                elif flag == '--links':
                    args.remove('--links')
                    separator = ' '
                    title = separator.join(args)
                    api = 'https://graphql.anilist.co'
                    query = manga_query.query
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
                                            manga_embed = discord.Embed(title=data['title']['romaji'],
                                                                        color=color, url=data['siteUrl'],
                                                                        timestamp=ctx.message.created_at)
                                        else:
                                            manga_embed = discord.Embed(title='%s (%s)' % (data['title']['romaji'],
                                                                                           data['title']['english']),
                                                                        color=color, url=data['siteUrl'],
                                                                        timestamp=ctx.message.created_at)
                                        manga_embed.set_thumbnail(url=data['coverImage']['large'])
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
                                            manga_embed.add_field(name='Links',
                                                                  value=links.__str__()[1:-1]
                                                                  .replace("'", "").replace(',', ''), inline=True)
                                        else:
                                            manga_embed.add_field(name='Links',
                                                                  value=links.__str__()[1:-1]
                                                                  .replace("'", "").replace(',', ''), inline=True)
                                        manga_embed.set_footer(text='Requested by %s' % ctx.author,
                                                               icon_url=ctx.author.avatar_url)
                                        await ctx.channel.send(embed=manga_embed)
                                        main.logger.info('Server: %s | Response: Manga Links - %s'
                                                         % (ctx.guild.name, data['title']['romaji']))
                                    except Exception as e:
                                        error_embed = discord.Embed(
                                            title='An error occurred while searching for the manga `%s` with the '
                                                  'command flag `%s`' % (title, flag),
                                            color=0xff0000)
                                        await ctx.channel.send(embed=error_embed)
                                        main.logger.exception(e)
                                else:
                                    error_embed = discord.Embed(
                                        title='The manga `%s` does not exist in the AniList database' % title,
                                        color=0xff0000)
                                    await ctx.channel.send(embed=error_embed)
                                    main.logger.info('Server: %s | Response: Not found' % ctx.guild.name)
                            else:
                                error_embed = discord.Embed(
                                    title='An error occurred while searching for the manga `%s` with the '
                                          'command flag `%s`' % (title, flag),
                                    color=0xff0000)
                                await ctx.channel.send(embed=error_embed)
                                main.logger.info('Server: %s | Response: Error' % ctx.guild.name)

                elif flag == '--all':
                    args.remove('--all')
                    separator = ' '
                    title = separator.join(args)
                    api = 'https://graphql.anilist.co'
                    query = manga_query.query
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
                                            manga_embed = discord.Embed(title=data['title']['romaji'],
                                                                        color=color,
                                                                        timestamp=ctx.message.created_at)
                                        else:
                                            manga_embed = discord.Embed(title='%s (%s)' % (data['title']['romaji'],
                                                                                           data['title']['english']),
                                                                        color=color,
                                                                        timestamp=ctx.message.created_at)
                                        manga_embed.set_thumbnail(url=data['coverImage']['large'])
                                        if data['description']:
                                            if len(data['description']) < 1024:
                                                manga_embed.add_field(name='Description',
                                                                      value=data['description']
                                                                      .replace('<br>', ' ')
                                                                      .replace('</br>', ' ')
                                                                      .replace('<i>', ' ')
                                                                      .replace('</i>', ' '),
                                                                      inline=False)
                                            else:
                                                manga_embed.add_field(name='Description',
                                                                      value=data['description']
                                                                      .replace('<br>', ' ')
                                                                      .replace('</br>', ' ')
                                                                      .replace('<i>', ' ')
                                                                      .replace('</i>', ' ')[0:1021] + '...',
                                                                      inline=False)
                                        else:
                                            manga_embed.add_field(name='Description', value='-', inline=False)
                                        manga_embed.add_field(name='Type',
                                                              value=data['format'].replace('_', ' ').title()
                                                              .replace('Tv', 'TV')
                                                              .replace('Ova', 'OVA')
                                                              .replace('Ona', 'ONA'),
                                                              inline=True)
                                        manga_embed.add_field(name='Status',
                                                              value=data['status'].replace('_', ' ').title(),
                                                              inline=True)
                                        if data['chapters']:
                                            if data['volumes']:
                                                manga_embed.add_field(name='Chapters',
                                                                      value='%s (%s Volumes)' % (data['chapters'],
                                                                                                 data['volumes']),
                                                                      inline=True)
                                            else:
                                                manga_embed.add_field(name='Chapters', value='%s' % data['chapters'],
                                                                      inline=True)
                                        else:
                                            if data['volumes']:
                                                manga_embed.add_field(name='Chapters',
                                                                      value='- (%s Volumes)' % data['volumes'],
                                                                      inline=True)
                                            else:
                                                manga_embed.add_field(name='Chapters', value='-', inline=True)
                                        if data['startDate']['day']:
                                            manga_embed.add_field(name='Start date',
                                                                  value='%s/%s/%s' % (data['startDate']['day'],
                                                                                      data['startDate']['month'],
                                                                                      data['startDate']['year']),
                                                                  inline=True)
                                        else:
                                            manga_embed.add_field(name='Start date', value='-', inline=True)
                                        if data['endDate']['day']:
                                            manga_embed.add_field(name='End date',
                                                                  value='%s/%s/%s' % (data['endDate']['day'],
                                                                                      data['endDate']['month'],
                                                                                      data['endDate']['year']),
                                                                  inline=True)
                                        else:
                                            manga_embed.add_field(name='End date', value='-', inline=True)
                                        try:
                                            manga_embed.add_field(name='Source',
                                                                  value=data['source'].replace('_', ' ').title(),
                                                                  inline=True)
                                        except AttributeError:
                                            manga_embed.add_field(name='Source', value='-', inline=True)
                                        if data['averageScore']:
                                            manga_embed.add_field(name='Ø Score', value=data['averageScore'],
                                                                  inline=True)
                                        else:
                                            manga_embed.add_field(name='Ø Score', value='-', inline=True)
                                        if data['popularity']:
                                            manga_embed.add_field(name='Popularity', value=data['popularity'],
                                                                  inline=True)
                                        else:
                                            manga_embed.add_field(name='Popularity', value='-', inline=True)
                                        if data['favourites']:
                                            manga_embed.add_field(name='Favourites', value=data['favourites'],
                                                                  inline=True)
                                        else:
                                            manga_embed.add_field(name='Favourites', value='-', inline=True)
                                        manga_embed.add_field(name='Genres', value=', '.join(data['genres']),
                                                              inline=False)
                                        if data['synonyms']:
                                            manga_embed.add_field(name='Synonyms', value=', '.join(data['synonyms']),
                                                                  inline=False)
                                        else:
                                            manga_embed.add_field(name='Synonyms', value='-', inline=True)
                                        manga_embed.add_field(name='AniList Link', value=data['siteUrl'], inline=False)
                                        manga_embed.add_field(name='MyAnimeList Link',
                                                              value='https://myanimelist.net/manga/' + str(
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
                                            manga_embed.add_field(name='Characters',
                                                                  value=characters.__str__()[1:-1]
                                                                  .replace("'", "").replace(',', ''), inline=False)
                                        else:
                                            manga_embed.add_field(name='Characters',
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
                                            manga_embed.add_field(name='Staff',
                                                                  value=staff.__str__()[1:-1]
                                                                  .replace("'", "").replace(',', ''), inline=False)
                                        else:
                                            manga_embed.add_field(name='Staff',
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
                                            manga_embed.add_field(name='Relations',
                                                                  value=relations.__str__()[1:-1]
                                                                  .replace("'", "").replace(',', ''), inline=False)
                                        else:
                                            manga_embed.add_field(name='Relations',
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
                                            manga_embed.add_field(name='Links',
                                                                  value=links.__str__()[1:-1]
                                                                  .replace("'", "").replace(',', ''), inline=True)
                                        else:
                                            manga_embed.add_field(name='Links',
                                                                  value=links.__str__()[1:-1]
                                                                  .replace("'", "").replace(',', ''), inline=True)
                                        if data['coverImage']['extraLarge']:
                                            manga_embed.set_image(url=data['coverImage']['extraLarge'])
                                        elif data['coverImage']['large']:
                                            manga_embed.set_image(url=data['coverImage']['large'])
                                        else:
                                            manga_embed.set_image(url=data['coverImage']['medium'])
                                        manga_embed.set_footer(text='Requested by %s' % ctx.author,
                                                               icon_url=ctx.author.avatar_url)
                                        await ctx.channel.send(embed=manga_embed)
                                        main.logger.info('Server: %s | Response: Manga All - %s' % (ctx.guild.name,
                                                                                                    data['title'][
                                                                                                        'romaji']))
                                    except Exception as e:
                                        error_embed = discord.Embed(
                                            title='An error occurred while searching for the manga `%s` with the '
                                                  'command flag `%s`' % (title, flag),
                                            color=0xff0000)
                                        await ctx.channel.send(embed=error_embed)
                                        main.logger.exception(e)
                                else:
                                    error_embed = discord.Embed(
                                        title='The manga `%s` does not exist in the AniList database' % title,
                                        color=0xff0000)
                                    await ctx.channel.send(embed=error_embed)
                                    main.logger.info('Server: %s | Response: Not found' % ctx.guild.name)
                            else:
                                error_embed = discord.Embed(
                                    title='An error occurred while searching for the manga `%s` with the '
                                          'command flag `%s`' % (title, flag),
                                    color=0xff0000)
                                await ctx.channel.send(embed=error_embed)
                                main.logger.info('Server: %s | Response: Error' % ctx.guild.name)

            else:
                error_embed = discord.Embed(title='Wrong command flag', color=0xff0000)
                await ctx.channel.send(embed=error_embed)
                main.logger.info('Server: %s | Response: Wrong command flags' % ctx.guild.name)

        else:
            api = 'https://graphql.anilist.co'
            query = manga_query.query
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
                                    manga_embed = discord.Embed(title=data['title']['romaji'],
                                                                color=color,
                                                                timestamp=ctx.message.created_at)
                                else:
                                    manga_embed = discord.Embed(title='%s (%s)' % (data['title']['romaji'],
                                                                                   data['title']['english']),
                                                                color=color,
                                                                timestamp=ctx.message.created_at)
                                manga_embed.set_thumbnail(url=data['coverImage']['large'])
                                if data['description']:
                                    if len(data['description']) < 1024:
                                        manga_embed.add_field(name='Description',
                                                              value=data['description']
                                                              .replace('<br>', ' ')
                                                              .replace('</br>', ' ')
                                                              .replace('<i>', ' ')
                                                              .replace('</i>', ' '),
                                                              inline=False)
                                    else:
                                        manga_embed.add_field(name='Description',
                                                              value=data['description']
                                                              .replace('<br>', ' ')
                                                              .replace('</br>', ' ')
                                                              .replace('<i>', ' ')
                                                              .replace('</i>', ' ')[0:1021] + '...',
                                                              inline=False)
                                else:
                                    manga_embed.add_field(name='Description', value='-', inline=False)
                                manga_embed.add_field(name='Type', value=data['format'].replace('_', ' ').title()
                                                      .replace('Tv', 'TV')
                                                      .replace('Ova', 'OVA')
                                                      .replace('Ona', 'ONA'),
                                                      inline=True)
                                manga_embed.add_field(name='Status', value=data['status'].replace('_', ' ').title(),
                                                      inline=True)
                                if data['chapters']:
                                    if data['volumes']:
                                        manga_embed.add_field(name='Chapters',
                                                              value='%s (%s Volumes)' % (data['chapters'],
                                                                                         data['volumes']),
                                                              inline=True)
                                    else:
                                        manga_embed.add_field(name='Chapters', value='%s' % data['chapters'],
                                                              inline=True)
                                else:
                                    if data['volumes']:
                                        manga_embed.add_field(name='Chapters', value='- (%s Volumes)' % data['volumes'],
                                                              inline=True)
                                    else:
                                        manga_embed.add_field(name='Chapters', value='-', inline=True)
                                if data['startDate']['day']:
                                    manga_embed.add_field(name='Start date',
                                                          value='%s/%s/%s' % (data['startDate']['day'],
                                                                              data['startDate']['month'],
                                                                              data['startDate']['year']),
                                                          inline=True)
                                else:
                                    manga_embed.add_field(name='Start date', value='-', inline=True)
                                if data['endDate']['day']:
                                    manga_embed.add_field(name='End date', value='%s/%s/%s' % (data['endDate']['day'],
                                                                                               data['endDate']['month'],
                                                                                               data['endDate']['year']),
                                                          inline=True)
                                else:
                                    manga_embed.add_field(name='End date', value='-', inline=True)
                                try:
                                    manga_embed.add_field(name='Source', value=data['source'].replace('_', ' ').title(),
                                                          inline=True)
                                except AttributeError:
                                    manga_embed.add_field(name='Source', value='-', inline=True)
                                if data['averageScore']:
                                    manga_embed.add_field(name='Ø Score', value=data['averageScore'], inline=True)
                                else:
                                    manga_embed.add_field(name='Ø Score', value='-', inline=True)
                                if data['popularity']:
                                    manga_embed.add_field(name='Popularity', value=data['popularity'], inline=True)
                                else:
                                    manga_embed.add_field(name='Popularity', value='-', inline=True)
                                if data['favourites']:
                                    manga_embed.add_field(name='Favourites', value=data['favourites'], inline=True)
                                else:
                                    manga_embed.add_field(name='Favourites', value='-', inline=True)
                                manga_embed.add_field(name='Genres', value=', '.join(data['genres']), inline=False)
                                if data['synonyms']:
                                    manga_embed.add_field(name='Synonyms', value=', '.join(data['synonyms']),
                                                          inline=False)
                                else:
                                    manga_embed.add_field(name='Synonyms', value='-', inline=True)
                                manga_embed.add_field(name='AniList Link', value=data['siteUrl'], inline=False)
                                manga_embed.add_field(name='MyAnimeList Link',
                                                      value='https://myanimelist.net/manga/' + str(data['idMal']),
                                                      inline=False)
                                manga_embed.set_footer(text='Requested by %s' % ctx.author,
                                                       icon_url=ctx.author.avatar_url)
                                await ctx.channel.send(embed=manga_embed)
                                main.logger.info('Server: %s | Response: Manga - %s' % (ctx.guild.name,
                                                                                        data['title']['romaji']))
                            except Exception as e:
                                error_embed = discord.Embed(
                                    title='An error occurred while searching for the manga `%s`' % title,
                                    color=0xff0000)
                                await ctx.channel.send(embed=error_embed)
                                main.logger.exception(e)
                        else:
                            error_embed = discord.Embed(
                                title='The manga `%s` does not exist in the AniList database' % title,
                                color=0xff0000)
                            await ctx.channel.send(embed=error_embed)
                            main.logger.info('Server: %s | Response: Not found' % ctx.guild.name)
                    else:
                        error_embed = discord.Embed(
                            title='An error occurred while searching for the manga `%s`' % title,
                            color=0xff0000)
                        await ctx.channel.send(embed=error_embed)
                        main.logger.info('Server: %s | Response: Error' % ctx.guild.name)


def setup(client):
    client.add_cog(Manga(client))
    main.logger.info('Loaded extension Manga')


def teardown():
    main.logger.info('Unloaded extension Manga')
