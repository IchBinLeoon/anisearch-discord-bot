import platform

import discord
from discord.ext import commands

import main


class About(commands.Cog, name='About'):

    def __init__(self, client):
        self.client = client

    @commands.command(name='about', ignore_extra=False)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def cmd_about(self, ctx):
        """Displays information about the bot."""
        about_embed = discord.Embed(title='About %s' % self.client.user.name,
                                    description='<@!%s> is an easy-to-use Discord bot that allows you to search for '
                                                'Anime, Manga, Characters, Staff, Studios and Profiles right within '
                                                'Discord and get results from AniList and MyAnimeList!\n\n If you have '
                                                'any suggestions use `contact <message>` or add me as a friend via '
                                                'discord.' % self.client.user.id,
                                    color=0x4169E1, timestamp=ctx.message.created_at)
        about_embed.add_field(name='❯ Creator', value='<@!%s>' % main.__owner_id__,
                              inline=True)
        about_embed.add_field(name='❯ Version', value='v%s' % main.__version__,
                              inline=True)
        about_embed.add_field(name='❯ Command list', value='as!help',
                              inline=True)
        about_embed.add_field(name='❯ Library', value='Discord.py',
                              inline=True)
        about_embed.add_field(name='❯ Python version', value='v%s' % platform.python_version(),
                              inline=True)
        about_embed.add_field(name='❯ Invite', value='[Click me!](https://discord.com/oauth2/authorize?client_id'
                                                     '=737236600878137363&permissions=83968&scope=bot)',
                              inline=True)
        about_embed.add_field(name='❯ Vote', value='[Click me!](https://top.gg/bot/737236600878137363/vote)',
                              inline=True)
        about_embed.set_thumbnail(url=self.client.user.avatar_url)
        about_embed.set_footer(text='Requested by %s' % ctx.author, icon_url=ctx.author.avatar_url)
        await ctx.channel.send(embed=about_embed)

    @commands.command(name='contact', ignore_extra=False)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def cmd_contact(self, ctx, *, message):
        """Contacts the creator of the bot."""
        contact_embed = discord.Embed(title='Contact',
                                      color=0x4169E1, timestamp=ctx.message.created_at)
        contact_embed.add_field(name='Author', value=ctx.author,
                                inline=False)
        contact_embed.add_field(name='Message', value=message,
                                inline=False)
        contact_embed.set_footer(text='Requested by %s' % ctx.author, icon_url=ctx.author.avatar_url)
        await self.client.get_user(main.__owner_id__).send(embed=contact_embed)
        contact_return_embed = discord.Embed(title='Creator contacted', color=0x4169E1)
        await ctx.channel.send(embed=contact_return_embed)


def setup(client):
    client.add_cog(About(client))
    main.logger.info('Loaded extension About')


def teardown():
    main.logger.info('Unloaded extension About')
