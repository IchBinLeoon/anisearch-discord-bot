import aiohttp
import discord
from discord.ext import commands

import main
from modules.studio import studio_query


class Studio(commands.Cog, name='Studio'):

    def __init__(self, client):
        self.client = client

    @commands.command(name='studio', usage='studio <name>', brief='3s', ignore_extra=False)
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def cmd_studio(self, ctx, *, name):
        """Searches for a studio and shows the first result."""
        if name.__contains__('--all'):
            error_embed = discord.Embed(title='Wrong arguments',
                                        color=0xff0000)
            await ctx.channel.send(embed=error_embed)
            main.logger.info('Server: %s | Response: Wrong arguments' % ctx.guild.name)
        elif name.__contains__('--chars') or name.__contains__('--characters'):
            error_embed = discord.Embed(title='Wrong arguments',
                                        color=0xff0000)
            await ctx.channel.send(embed=error_embed)
            main.logger.info('Server: %s | Response: Wrong arguments' % ctx.guild.name)
        else:
            api = 'https://graphql.anilist.co'
            query = studio_query.query
            variables = {
                'studio': name
            }
            async with aiohttp.ClientSession() as session:
                async with session.post(api, json={'query': query, 'variables': variables}) as r:
                    if r.status == 200:
                        json = await r.json()
                        data = json['data']['Studio']
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
                                    productions.append(str('[' + data['media']['edges'][x]['node']['title']['romaji'] +
                                                           '](' + data['media']['edges'][x]['node']['siteUrl'] + ') |'))
                                    x = x + 1
                                productions.append(str('[' + data['media']['edges'][x]['node']['title']['romaji'] + ']('
                                                       + data['media']['edges'][x]['node']['siteUrl'] + ')'))
                            else:
                                productions = '[-]'
                            if len(str(productions)) > 1024:
                                productions = productions[0:15]
                                productions[14] = str(productions[14]).replace(' |', '...')
                                studio_embed.add_field(name='Productions', value=productions.__str__()[1:-1]
                                                       .replace("'", "").replace(',', ''), inline=True)
                            else:
                                studio_embed.add_field(name='Productions', value=productions.__str__()[1:-1]
                                                       .replace("'", "").replace(',', ''), inline=True)
                            await ctx.channel.send(embed=studio_embed)
                            main.logger.info('Server: %s | Response: Studio - %s' % (ctx.guild.name, data['name']))
                        except Exception as e:
                            error_embed = discord.Embed(
                                title='An error occurred while searching for the studio `%s`' % name,
                                color=0xff0000)
                            await ctx.channel.send(embed=error_embed)
                            main.logger.exception(e)
                    else:
                        error_embed = discord.Embed(
                            title='The studio `%s` does not exist in the AniList database' % name,
                            color=0xff0000)
                        await ctx.channel.send(embed=error_embed)
                        main.logger.info('Server: %s | Response: Not found' % ctx.guild.name)


def setup(client):
    client.add_cog(Studio(client))
    main.logger.info('Loaded extension Studio')


def teardown():
    main.logger.info('Unloaded extension Studio')
