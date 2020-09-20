import aiohttp
import discord
from discord.ext import commands

import main
from modules.character import character_query


class Character(commands.Cog, name='Character'):

    def __init__(self, client):
        self.client = client

    @commands.command(name='character', aliases=['c', 'char'], usage='character <name>', brief='3s', ignore_extra=False)
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def cmd_character(self, ctx, *, name):
        """Searches for a character and shows the first result."""
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
                                character_embed.add_field(name='Description', value='-', inline=False)
                            if data['name']['alternative'] != ['']:
                                synonyms = []
                                x = 0
                                synonyms_length = int(len(data['name']['alternative']))
                                for i in range(0, synonyms_length - 1):
                                    synonyms.append(str(data['name']['alternative'][x] + ' | '))
                                    x = x + 1
                                synonyms.append(str(data['name']['alternative'][x]))
                            else:
                                synonyms = '[-]'
                            if len(str(synonyms)) > 1024:
                                synonyms = synonyms[0:10]
                                synonyms[9] = str(synonyms[9]).replace(' |', '...')
                                character_embed.add_field(name='Synonyms', value=synonyms.__str__()[1:-1], inline=False)
                            else:
                                character_embed.add_field(name='Synonyms', value=synonyms.__str__()[1:-1]
                                                          .replace("'", "").replace(',', ''),
                                                          inline=False)
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
