import aiohttp
import discord
from discord.ext import commands

import main
from modules.character import character_query

flags = ['--search', '--image']


class Character(commands.Cog, name='Character'):

    def __init__(self, client):
        self.client = client

    @commands.command(name='character', aliases=['c', 'char'], usage='character <name> [flag]',
                      brief='3s --search --image', ignore_extra=False)
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def cmd_character(self, ctx, *, name):
        """Searches for a character with the given name and displays information about the first result such as description, synonyms, and appearances!"""
        args = name.split(' ')
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
                    name = separator.join(args)
                    api = 'https://graphql.anilist.co'
                    query = character_query.query
                    variables = {
                        'character': name,
                        'page': 1,
                        'amount': 15
                    }
                    async with aiohttp.ClientSession() as session:
                        async with session.post(api, json={'query': query, 'variables': variables}) as r:
                            if r.status == 200:
                                json = await r.json()
                                if json['data']['Page']['characters']:
                                    data = json['data']['Page']['characters']
                                    try:
                                        character_embed = discord.Embed(
                                            title='Search results for character "%s"' % name,
                                            color=0x4169E1,
                                            timestamp=ctx.message.created_at)
                                        x = 0
                                        for i in data:
                                            if data[x]['name']['full'] is None or data[x]['name']['full'] == \
                                                    data[x]['name']['native']:
                                                char_name = str(x + 1) + '. ' + data[x]['name']['native']
                                            else:
                                                if data[x]['name']['native']:
                                                    char_name = str(x + 1) + '. ' + data[x]['name']['full'] + ' (' + \
                                                                data[x]['name']['native'] + ')'
                                                else:
                                                    char_name = str(x + 1) + '. ' + data[x]['name']['full']
                                            if data[x]['media']['edges']:
                                                productions = []
                                                if len(data[x]['media']['edges']) < 2:
                                                    length = len(data[x]['media']['edges'])
                                                else:
                                                    length = 2
                                                y = 0
                                                for j in range(0, length):
                                                    productions.append(str('[' +
                                                                           data[x]['media']['edges'][y]['node']['title']
                                                                           ['romaji'] +
                                                                           '](' + data[x]['media']['edges'][y]['node']
                                                                           ['siteUrl'] +
                                                                           ')'))
                                                    y = y + 1
                                                if len(data[x]['media']['edges']) < 2:
                                                    value = ' | '.join(productions)
                                                else:
                                                    value = ' | '.join(productions) + '...'
                                            else:
                                                value = '-'
                                            character_embed.add_field(name=char_name, value=value, inline=False)
                                            x = x + 1
                                        character_embed.set_thumbnail(url=data[0]['image']['large'])
                                        character_embed.set_footer(text='Requested by %s' % ctx.author,
                                                                   icon_url=ctx.author.avatar_url)
                                        await ctx.channel.send(embed=character_embed)
                                        main.logger.info('Server: %s | Response: Character Search - %s'
                                                         % (ctx.guild.name, name))
                                    except Exception as e:
                                        error_embed = discord.Embed(
                                            title='An error occurred while searching for the character `%s` with the '
                                                  'command flag `%s`' % (name, flag),
                                            color=0xff0000)
                                        await ctx.channel.send(embed=error_embed)
                                        main.logger.exception(e)
                                else:
                                    error_embed = discord.Embed(
                                        title='The character `%s` does not exist in the AniList database' % name,
                                        color=0xff0000)
                                    await ctx.channel.send(embed=error_embed)
                                    main.logger.info('Server: %s | Response: Not found' % ctx.guild.name)
                            else:
                                error_embed = discord.Embed(
                                    title='An error occurred while searching for the character `%s` with the '
                                          'command flag `%s`' % (name, flag),
                                    color=0xff0000)
                                await ctx.channel.send(embed=error_embed)
                                main.logger.info('Server: %s | Response: Error' % ctx.guild.name)

                elif flag == '--image':
                    args.remove('--image')
                    separator = ' '
                    name = separator.join(args)
                    api = 'https://graphql.anilist.co'
                    query = character_query.query
                    variables = {
                        'character': name,
                        'page': 1,
                        'amount': 1
                    }
                    async with aiohttp.ClientSession() as session:
                        async with session.post(api, json={'query': query, 'variables': variables}) as r:
                            if r.status == 200:
                                json = await r.json()
                                if json['data']['Page']['characters']:
                                    data = json['data']['Page']['characters'][0]
                                    try:
                                        if data['name']['full'] is None or data['name']['full'] == data['name']['native']:
                                            character_embed = discord.Embed(title=data['name']['native'],
                                                                            url=data['siteUrl'],
                                                                            color=0x4169E1,
                                                                            timestamp=ctx.message.created_at)
                                        else:
                                            if data['name']['native']:
                                                title = '%s (%s)' % (data['name']['full'], data['name']['native'])
                                            else:
                                                title = data['name']['full']
                                            character_embed = discord.Embed(title=title, url=data['siteUrl'],
                                                                            color=0x4169E1,
                                                                            timestamp=ctx.message.created_at)
                                        if data['image']['large']:
                                            character_embed.set_image(url=data['image']['large'])
                                        else:
                                            character_embed.set_image(url=data['image']['medium'])
                                        character_embed.set_footer(text='Requested by %s' % ctx.author,
                                                                   icon_url=ctx.author.avatar_url)
                                        await ctx.channel.send(embed=character_embed)
                                        main.logger.info('Server: %s | Response: Character Image - %s'
                                                         % (ctx.guild.name, name))
                                    except Exception as e:
                                        error_embed = discord.Embed(
                                            title='An error occurred while searching for the character `%s` with the '
                                                  'command flag `%s`' % (name, flag),
                                            color=0xff0000)
                                        await ctx.channel.send(embed=error_embed)
                                        main.logger.exception(e)
                                else:
                                    error_embed = discord.Embed(
                                        title='The character `%s` does not exist in the AniList database' % name,
                                        color=0xff0000)
                                    await ctx.channel.send(embed=error_embed)
                                    main.logger.info('Server: %s | Response: Not found' % ctx.guild.name)
                            else:
                                error_embed = discord.Embed(
                                    title='An error occurred while searching for the character `%s` with the '
                                          'command flag `%s`' % (name, flag),
                                    color=0xff0000)
                                await ctx.channel.send(embed=error_embed)
                                main.logger.info('Server: %s | Response: Error' % ctx.guild.name)

            else:
                error_embed = discord.Embed(title='The command flag is invalid or cannot be used with this command',
                                            color=0xff0000)
                await ctx.channel.send(embed=error_embed)
                main.logger.info('Server: %s | Response: Wrong command flags' % ctx.guild.name)

        else:
            api = 'https://graphql.anilist.co'
            query = character_query.query
            variables = {
                'character': name,
                'page': 1,
                'amount': 1
            }
            async with aiohttp.ClientSession() as session:
                async with session.post(api, json={'query': query, 'variables': variables}) as r:
                    if r.status == 200:
                        json = await r.json()
                        if json['data']['Page']['characters']:
                            data = json['data']['Page']['characters'][0]
                            try:
                                if data['name']['full'] is None or data['name']['full'] == data['name']['native']:
                                    character_embed = discord.Embed(title=data['name']['native'], url=data['siteUrl'],
                                                                    color=0x4169E1,
                                                                    timestamp=ctx.message.created_at)
                                else:
                                    if data['name']['native']:
                                        title = '%s (%s)' % (data['name']['full'], data['name']['native'])
                                    else:
                                        title = data['name']['full']
                                    character_embed = discord.Embed(title=title, url=data['siteUrl'], color=0x4169E1,
                                                                    timestamp=ctx.message.created_at)
                                character_embed.set_thumbnail(url=data['image']['large'])
                                try:
                                    if len(data['description']) < 1024:
                                        character_embed.add_field(name='Description',
                                                                  value=data['description'].replace('<br>', ' ')
                                                                  .replace('</br>', ' ')
                                                                  .replace('<i>', ' ').replace('</i>', ' '),
                                                                  inline=False)
                                    else:
                                        character_embed.add_field(name='Description',
                                                                  value=data['description'].replace('<br>', ' ')
                                                                  .replace('</br>', ' ')
                                                                  .replace('<i>', ' ')
                                                                  .replace('</i>', ' ')[0:1021] + '...',
                                                                  inline=False)
                                except TypeError:
                                    character_embed.add_field(name='Description', value='-', inline=False)
                                if data['name']['alternative'] != ['']:
                                    synonyms = data['name']['alternative']
                                    synonyms = ', '.join(synonyms)
                                else:
                                    synonyms = '-'
                                character_embed.add_field(name='Synonyms', value=synonyms,
                                                          inline=False)
                                if data['media']['edges']:
                                    appearances = []
                                    x = 0
                                    appearances_length = int(len(data['media']['edges']))
                                    for i in range(0, appearances_length - 1):
                                        appearances.append(str('[' +
                                                               data['media']['edges'][x]['node']['title']['romaji'] +
                                                               '](' + data['media']['edges'][x]['node']['siteUrl'] +
                                                               ') |'))
                                        x = x + 1
                                    appearances.append(str('[' + data['media']['edges'][x]['node']['title']['romaji'] +
                                                           '](' + data['media']['edges'][x]['node']['siteUrl'] + ')'))
                                else:
                                    appearances = '[-]'
                                if len(str(appearances)) > 1024:
                                    appearances = appearances[0:10]
                                    appearances[9] = str(appearances[9]).replace(' |', '...')
                                    character_embed.add_field(name='Appearances', value=appearances.__str__()[1:-1]
                                                              .replace("'", "").replace(',', ''), inline=False)
                                else:
                                    character_embed.add_field(name='Appearances', value=appearances.__str__()[1:-1]
                                                              .replace("'", "").replace(',', ''), inline=False)
                                character_embed.set_footer(text='Requested by %s' % ctx.author,
                                                           icon_url=ctx.author.avatar_url)
                                await ctx.channel.send(embed=character_embed)
                                main.logger.info('Server: %s | Response: Character - %s' % (ctx.guild.name,
                                                                                            data['name']['full']))
                            except Exception as e:
                                error_embed = discord.Embed(
                                    title='An error occurred while searching for the character `%s`' % name,
                                    color=0xff0000)
                                await ctx.channel.send(embed=error_embed)
                                main.logger.exception(e)
                        else:
                            error_embed = discord.Embed(
                                title='The character `%s` does not exist in the AniList database' % name,
                                color=0xff0000)
                            await ctx.channel.send(embed=error_embed)
                            main.logger.info('Server: %s | Response: Not found' % ctx.guild.name)
                    else:
                        error_embed = discord.Embed(
                            title='An error occurred while searching for the character `%s`' % name,
                            color=0xff0000)
                        await ctx.channel.send(embed=error_embed)
                        main.logger.info('Server: %s | Response: Error' % ctx.guild.name)


def setup(client):
    client.add_cog(Character(client))
    main.logger.info('Loaded extension Character')


def teardown():
    main.logger.info('Unloaded extension Character')
