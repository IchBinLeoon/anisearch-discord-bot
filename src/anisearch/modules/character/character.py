import aiohttp
import discord
from discord.ext import commands

import main
from modules.character import character_query


class Character(commands.Cog, name='Character'):

    def __init__(self, client):
        self.client = client

    @commands.command(name='character', aliases=['c', 'char'], ignore_extra=False)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def cmd_character(self, ctx, *, character):
        """Searches for a character and shows the first result."""
        if character.__contains__('--all'):
            parameters = character.split()
            if parameters.__contains__('--all'):
                parameters.remove('--all')
            separator = ' '
            character = separator.join(parameters)
            api = 'https://graphql.anilist.co'
            query = character_query.query_pages
            variables = {
                'character': character,
                'page': 1,
                'amount': 10,
            }
            async with aiohttp.ClientSession() as session:
                async with session.post(api, json={'query': query, 'variables': variables}) as r:
                    if r.status == 200:
                        json = await r.json()
                        if json['data']['Page']['characters']:
                            data = json['data']['Page']['characters']
                        try:
                            anime_embed = discord.Embed(title='Search results for Character "%s"' % character,
                                                        color=0x4169E1, timestamp=ctx.message.created_at)
                            x = 0
                            for i in data:
                                anime_embed.add_field(name=str(x + 1) + '. ' + data[x]['name']['full'],
                                                      value=data[x]['siteUrl'], inline=False)
                                x = x + 1
                            anime_embed.set_thumbnail(url=data[0]['image']['large'])
                            anime_embed.set_footer(text='Requested by %s' % ctx.author,
                                                   icon_url=ctx.author.avatar_url)
                            await ctx.channel.send(embed=anime_embed)
                            main.logger.info('Server: %s | Response: Character All - %s' % (ctx.guild.name, character))
                        except Exception as e:
                            error_embed = discord.Embed(
                                title='An error occurred while searching for the character `%s`' % character,
                                color=0xff0000)
                            await ctx.channel.send(embed=error_embed)
                            main.logger.error(e)
                    else:
                        error_embed = discord.Embed(
                            title='The character `%s` does not exist in the AniList database' % character,
                            color=0xff0000)
                        await ctx.channel.send(embed=error_embed)
                        main.logger.info('Server: %s | Response: Not found' % ctx.guild.name)
        elif character.__contains__('--chars') or character.__contains__('--characters'):
            error_embed = discord.Embed(title='Bad argument',
                                        color=0xff0000)
            await ctx.channel.send(embed=error_embed)
            main.logger.info('Server: %s | Response: Bad argument' % ctx.guild.name)
        else:
            api = 'https://graphql.anilist.co'
            query = character_query.query
            variables = {
                'character': character
            }
            async with aiohttp.ClientSession() as session:
                async with session.post(api, json={'query': query, 'variables': variables}) as r:
                    if r.status == 200:
                        json = await r.json()
                        data = json['data']['Character']
                        try:
                            if data['name']['full'] is None or data['name']['full'] == data['name']['native']:
                                character_embed = discord.Embed(title=data['name']['native'], url=data['siteUrl'],
                                                                color=0x4169E1,
                                                                timestamp=ctx.message.created_at)
                            else:
                                character_embed = discord.Embed(title='%s (%s)' % (data['name']['full'],
                                                                                   data['name']['native']),
                                                                url=data['siteUrl'],
                                                                color=0x4169E1,
                                                                timestamp=ctx.message.created_at)
                            character_embed.set_thumbnail(url=data['image']['large'])
                            try:
                                if len(data['description']) < 1024:
                                    character_embed.add_field(name='Description',
                                                              value=data['description'].replace('<br>', ' ').replace(
                                                                  '</br>', ' ')
                                                              .replace('<i>', ' ').replace('</i>', ' '), inline=False)
                                else:
                                    character_embed.add_field(name='Description',
                                                              value=data['description'].replace('<br>', ' ').replace(
                                                                  '</br>', ' ')
                                                              .replace('<i>', ' ').replace('</i>', ' ')[0:1021] + '...',
                                                              inline=False)
                            except TypeError:
                                character_embed.add_field(name='Description',
                                                          value='N/A', inline=False)
                            if data['media']['edges']:
                                appearances = []
                                x = 0
                                appearances_length = int(len(data['media']['edges']))
                                for i in range(0, appearances_length - 1):
                                    appearances.append(str('[' + data['media']['edges'][x]['node']['title']['romaji'] +
                                                           '](' + data['media']['edges'][x]['node']['siteUrl'] + ') |'))
                                    x = x + 1
                                appearances.append(str('[' + data['media']['edges'][x]['node']['title']['romaji'] + ']('
                                                       + data['media']['edges'][x]['node']['siteUrl'] + ')'))
                            else:
                                appearances = 'N/A'
                            if len(str(appearances)) > 1024:
                                appearances = appearances[0:10]
                                appearances[9] = str(appearances[9]).replace(' |', '...')
                                character_embed.add_field(name='Appearances', value=appearances.__str__()[1:-1]
                                                          .replace("'", "").replace(',', ''), inline=True)
                            else:
                                character_embed.add_field(name='Appearances', value=appearances.__str__()[1:-1]
                                                          .replace("'", "").replace(',', ''), inline=True)
                            character_embed.set_footer(text='Requested by %s' % ctx.author,
                                                       icon_url=ctx.author.avatar_url)
                            await ctx.channel.send(embed=character_embed)
                            main.logger.info('Server: %s | Response: Character - %s' % (ctx.guild.name,
                                                                                        data['name']['full']))
                        except Exception as e:
                            error_embed = discord.Embed(
                                title='An error occurred while searching for the character `%s`' % character,
                                color=0xff0000)
                            await ctx.channel.send(embed=error_embed)
                            main.logger.error(e)
                    else:
                        error_embed = discord.Embed(
                            title='The character `%s` does not exist in the AniList database' % character,
                            color=0xff0000)
                        await ctx.channel.send(embed=error_embed)
                        main.logger.info('Server: %s | Response: Not found' % ctx.guild.name)


def setup(client):
    client.add_cog(Character(client))
    main.logger.info('Loaded extension Character')


def teardown():
    main.logger.info('Unloaded extension Character')
