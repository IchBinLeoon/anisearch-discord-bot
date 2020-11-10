import aiohttp
import discord
from discord.ext import commands

from anisearch.bot import logger
from anisearch.queries import studio_query

flags = ['--search']


class Studio(commands.Cog, name='Studio'):

    def __init__(self, client):
        self.client = client

    @commands.command(name='studio', usage='studio <name> [flag]', brief='3s', ignore_extra=False)
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def cmd_studio(self, ctx, *, name):
        """Searches for a studio with the given name and displays information about the first result such as the studio productions!
        |--search"""
        args = name.split(' ')
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
                    name = separator.join(args)
                    api = 'https://graphql.anilist.co'
                    query = studio_query.query
                    variables = {
                        'studio': name,
                        'page': 1,
                        'amount': 15
                    }
                    async with aiohttp.ClientSession() as session:
                        async with session.post(api, json={'query': query, 'variables': variables}) as r:
                            if r.status == 200:
                                json = await r.json()
                                if json['data']['Page']['studios']:
                                    data = json['data']['Page']['studios']
                                    try:
                                        character_embed = discord.Embed(
                                            title='Search results for studio "%s"' % name,
                                            color=0x4169E1,
                                            timestamp=ctx.message.created_at)
                                        x = 0
                                        for i in data:
                                            if data[x]['media']['edges']:
                                                productions = []
                                                if len(data[x]['media']['edges']) < 2:
                                                    length = len(data[x]['media']['edges'])
                                                else:
                                                    length = 2
                                                y = 0
                                                for j in range(0, length):
                                                    productions.append(str('[' + data[x]['media']['edges'][y]
                                                                           ['node']['title']['romaji'] + '](' + data[x]
                                                                           ['media']['edges'][y]['node']
                                                                           ['siteUrl'] + ')'))
                                                    y = y + 1
                                                if len(data[x]['media']['edges']) < 2:
                                                    value = ' | '.join(productions)
                                                else:
                                                    value = ' | '.join(productions) + '...'
                                            else:
                                                value = '-'
                                            character_embed.add_field(name=str(x + 1) + '. ' + data[x]['name'],
                                                                      value=value, inline=False)
                                            x = x + 1
                                        character_embed.set_footer(text='Requested by %s' % ctx.author,
                                                                   icon_url=ctx.author.avatar_url)
                                        await ctx.channel.send(embed=character_embed)
                                        logger.info('Server: %s | Response: Studio Search - %s'
                                                        % (ctx.guild.name, name))
                                    except Exception as e:
                                        error_embed = discord.Embed(
                                            title='An error occurred while searching for the studio `%s` with the '
                                                  'command flag `%s`' % (name, flag),
                                            color=0xff0000)
                                        await ctx.channel.send(embed=error_embed)
                                        logger.exception(e)
                                else:
                                    error_embed = discord.Embed(
                                        title='The studio `%s` does not exist in the AniList database' % name,
                                        color=0xff0000)
                                    await ctx.channel.send(embed=error_embed)
                                    logger.info('Server: %s | Response: Not found' % ctx.guild.name)
                            else:
                                error_embed = discord.Embed(
                                    title='An error occurred while searching for the studio `%s` with the '
                                          'command flag `%s`' % (name, flag),
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
            query = studio_query.query
            variables = {
                'studio': name,
                'page': 1,
                'amount': 1
            }
            async with aiohttp.ClientSession() as session:
                async with session.post(api, json={'query': query, 'variables': variables}) as r:
                    if r.status == 200:
                        json = await r.json()
                        if json['data']['Page']['studios']:
                            data = json['data']['Page']['studios'][0]
                            try:
                                studio_embed = discord.Embed(title=data['name'], url=data['siteUrl'],
                                                             color=0x4169E1, timestamp=ctx.message.created_at)
                                studio_embed.set_footer(text='Requested by %s' % ctx.author,
                                                        icon_url=ctx.author.avatar_url)
                                if data['media']['edges']:
                                    productions = []
                                    x = 0
                                    productions_length = int(len(data['media']['edges']))
                                    for i in range(0, productions_length - 1):
                                        productions.append(str('[' +
                                                               data['media']['edges'][x]['node']['title']['romaji'] +
                                                               '](' + data['media']['edges'][x]['node']['siteUrl'] +
                                                               ') |'))
                                        x = x + 1
                                    productions.append(str('[' + data['media']['edges'][x]['node']['title']['romaji'] +
                                                           '](' + data['media']['edges'][x]['node']['siteUrl'] + ')'))
                                else:
                                    productions = '[-]'
                                if len(str(productions)) > 1024:
                                    productions = productions[0:11]
                                    productions[10] = str(productions[10]).replace(' |', '...')
                                    studio_embed.add_field(name='Productions', value=productions.__str__()[1:-1]
                                                           .replace("'", "").replace(',', ''), inline=True)
                                else:
                                    studio_embed.add_field(name='Productions', value=productions.__str__()[1:-1]
                                                           .replace("'", "").replace(',', ''), inline=True)
                                await ctx.channel.send(embed=studio_embed)
                                logger.info('Server: %s | Response: Studio - %s' % (ctx.guild.name, data['name']))
                            except Exception as e:
                                error_embed = discord.Embed(
                                    title='An error occurred while searching for the studio `%s`' % name,
                                    color=0xff0000)
                                await ctx.channel.send(embed=error_embed)
                                logger.exception(e)
                        else:
                            error_embed = discord.Embed(
                                title='The studio `%s` does not exist in the AniList database' % name,
                                color=0xff0000)
                            await ctx.channel.send(embed=error_embed)
                            logger.info('Server: %s | Response: Not found' % ctx.guild.name)
                    else:
                        error_embed = discord.Embed(
                            title='An error occurred while searching for the studio `%s`' % name,
                            color=0xff0000)
                        await ctx.channel.send(embed=error_embed)
                        logger.info('Server: %s | Response: Not found' % ctx.guild.name)
