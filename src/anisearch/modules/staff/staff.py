import aiohttp
import discord
from discord.ext import commands

import main
from modules.staff import staff_query


class Staff(commands.Cog, name='Staff'):

    def __init__(self, client):
        self.client = client

    @commands.command(name='staff', ignore_extra=False)
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def cmd_staff(self, ctx, *, staff):
        """Searches for a staff and shows the first result."""
        if staff.__contains__('--all'):
            parameters = staff.split()
            if parameters.__contains__('--all'):
                parameters.remove('--all')
            separator = ' '
            staff = separator.join(parameters)
            api = 'https://graphql.anilist.co'
            query = staff_query.query_pages
            variables = {
                'staff': staff,
                'page': 1,
                'amount': 10,
            }
            async with aiohttp.ClientSession() as session:
                async with session.post(api, json={'query': query, 'variables': variables}) as r:
                    if r.status == 200:
                        json = await r.json()
                        if json['data']['Page']['staff']:
                            data = json['data']['Page']['staff']
                        try:
                            anime_embed = discord.Embed(title='Search results for Staff "%s"' % staff,
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
                            main.logger.info('Server: %s | Response: Staff All - %s' % (ctx.guild.name, staff))
                        except Exception as e:
                            error_embed = discord.Embed(
                                title='An error occurred while searching for the staff `%s`' % staff,
                                color=0xff0000)
                            await ctx.channel.send(embed=error_embed)
                            main.logger.exception(e)
                    else:
                        error_embed = discord.Embed(
                            title='The staff `%s` does not exist in the AniList database' % staff,
                            color=0xff0000)
                        await ctx.channel.send(embed=error_embed)
                        main.logger.info('Server: %s | Response: Not found' % ctx.guild.name)
        elif staff.__contains__('--chars') or staff.__contains__('--characters'):
            error_embed = discord.Embed(title='Wrong arguments',
                                        color=0xff0000)
            await ctx.channel.send(embed=error_embed)
            main.logger.info('Server: %s | Response: Wrong arguments' % ctx.guild.name)
        else:
            api = 'https://graphql.anilist.co'
            query = staff_query.query
            variables = {
                'staff': staff
            }
            async with aiohttp.ClientSession() as session:
                async with session.post(api, json={'query': query, 'variables': variables}) as r:
                    if r.status == 200:
                        json = await r.json()
                        data = json['data']['Staff']
                        try:
                            if data['name']['native'] is None:
                                staff_embed = discord.Embed(title='%s' % data['name']['full'],
                                                            url=data['siteUrl'],
                                                            color=0x4169E1,
                                                            timestamp=ctx.message.created_at)
                            elif data['name']['full'] is None or data['name']['full'] == data['name']['native']:
                                staff_embed = discord.Embed(title=data['name']['native'],
                                                            url=data['siteUrl'],
                                                            color=0x4169E1,
                                                            timestamp=ctx.message.created_at)
                            else:
                                staff_embed = discord.Embed(title='%s (%s)' % (data['name']['full'],
                                                                               data['name']['native']),
                                                            url=data['siteUrl'],
                                                            color=0x4169E1,
                                                            timestamp=ctx.message.created_at)
                            staff_embed.set_thumbnail(url=data['image']['large'])
                            try:
                                if len(data['description']) < 1024:
                                    staff_embed.add_field(name='Description',
                                                          value=data['description'].replace('<br>', ' ')
                                                          .replace('</br>', ' ')
                                                          .replace('<i>', ' ').replace('</i>', ' '), inline=False)
                                else:
                                    staff_embed.add_field(name='Description',
                                                          value=data['description'].replace('<br>', ' ')
                                                          .replace('</br>', ' ')
                                                          .replace('<i>', ' ').replace('</i>', ' ')[0:1021] + '...',
                                                          inline=False)
                            except TypeError:
                                staff_embed.add_field(name='Description',
                                                      value='N/A', inline=False)
                            if data['staffMedia']['edges']:
                                staff_roles = []
                                x = 0
                                staff_roles_length = int(len(data['staffMedia']['edges']))
                                for i in range(0, staff_roles_length - 1):
                                    staff_roles.append(
                                        str('[' + data['staffMedia']['edges'][x]['node']['title']['romaji'] + ']('
                                            + data['staffMedia']['edges'][x]['node']['siteUrl'] + ') |'))
                                    x = x + 1
                                staff_roles.append(
                                    str('[' + data['staffMedia']['edges'][x]['node']['title']['romaji'] + ']('
                                        + data['staffMedia']['edges'][x]['node']['siteUrl'] + ')'))
                            else:
                                staff_roles = '[N/A]'
                            if len(str(staff_roles)) > 1024:
                                staff_roles = staff_roles[0:10]
                                staff_roles[9] = str(staff_roles[9]).replace(' |', '...')
                                staff_embed.add_field(name='Staff Roles', value=staff_roles.__str__()[1:-1]
                                                      .replace("'", "")
                                                      .replace(',', ''), inline=True)
                            else:
                                staff_embed.add_field(name='Staff Roles', value=staff_roles.__str__()[1:-1]
                                                      .replace("'", "")
                                                      .replace(',', ''), inline=True)
                            if data['characters']['edges']:
                                characters = []
                                x = 0
                                characters_length = int(len(data['characters']['edges']))
                                for i in range(0, characters_length - 1):
                                    characters.append(
                                        str('[' + data['characters']['edges'][x]['node']['name']['full'] + ']('
                                            + data['characters']['edges'][x]['node']['siteUrl'] + ') |'))
                                    x = x + 1
                                characters.append(str('[' + data['characters']['edges'][x]['node']['name']['full']
                                                      + '](' + data['characters']['edges'][x]['node']['siteUrl'] + ')'))
                            else:
                                characters = '[N/A]'
                            if len(str(characters)) > 1024:
                                characters = characters[0:15]
                                characters[14] = str(characters[14]).replace(' |', '...')
                                staff_embed.add_field(name='Character Roles', value=characters.__str__()[1:-1]
                                                      .replace("'", "").replace(',', ''), inline=False)
                            else:
                                staff_embed.add_field(name='Character Roles', value=characters.__str__()[1:-1]
                                                      .replace("'", "").replace(',', ''), inline=False)
                            staff_embed.set_footer(text='Requested by %s' % ctx.author,
                                                   icon_url=ctx.author.avatar_url)
                            await ctx.channel.send(embed=staff_embed)
                            main.logger.info('Server: %s | Response: Staff - %s' % (ctx.guild.name,
                                                                                    data['name']['full']))
                        except Exception as e:
                            error_embed = discord.Embed(
                                title='An error occurred while searching for the staff `%s`' % staff,
                                color=0xff0000)
                            await ctx.channel.send(embed=error_embed)
                            main.logger.exception(e)
                    else:
                        error_embed = discord.Embed(
                            title='The staff `%s` does not exist in the AniList database' % staff,
                            color=0xff0000)
                        await ctx.channel.send(embed=error_embed)
                        main.logger.info('Server: %s | Response: Not found' % ctx.guild.name)


def setup(client):
    client.add_cog(Staff(client))
    main.logger.info('Loaded extension Staff')


def teardown():
    main.logger.info('Unloaded extension Staff')
