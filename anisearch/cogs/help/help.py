from datetime import timedelta
from time import time
from typing import Optional

import psutil
from discord.utils import get
import discord
import psycopg2
from discord.ext import commands
from anisearch import config, bot
from anisearch.bot import get_prefix
from anisearch.utils.logger import logger

invite = 'https://discord.com/oauth2/authorize?client_id=737236600878137363&permissions=124992&scope=bot'
vote = 'https://top.gg/bot/737236600878137363/vote'
github = 'https://github.com/IchBinLeoon/anisearch-discord-bot'


class Help(commands.Cog, name='Help'):

    def __init__(self, bot):
        self.bot = bot
        self.bot.remove_command('help')

    @commands.command(name='help', aliases=['h'], usage='help [command]', brief='3s', ignore_extra=False)
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def help(self, ctx, cmd: Optional[str]):
        """Shows help or displays information about a command."""
        prefix = get_prefix(ctx)
        if cmd is None:
            embed = discord.Embed(title='AniSearch',
                                  description=f'**Current server prefix:** `{prefix}`\n'
                                              f'\n'
                                              f'**Command help:**\n'
                                              f'`{prefix}help [command]`\n'
                                              f'\n'
                                              f'**Command list:**\n'
                                              f'`{prefix}commands`\n'
                                              f'\n'
                                              f'**Links:**\n'
                                              f'[Invite AniSearch!]({invite}) | '
                                              f'[Vote for AniSearch!]({vote})',
                                  color=0x4169E1)
            embed.set_thumbnail(url=self.bot.user.avatar_url)
            await ctx.send(embed=embed)
        else:
            if command := get(self.bot.commands, name=cmd):
                embed = discord.Embed(title='Command - {}'.format(command), colour=0x4169E1)
                embed.add_field(name='Usage', value='`{}{}`'.format(prefix, command.usage),
                                inline=False)
                embed.add_field(name='Description', value='{}'.format(command.help), inline=False)
                embed.add_field(name='Cooldown', value='`{}`'.format(command.brief), inline=False)
                if command.aliases:
                    aliases = ', '.join(command.aliases)
                    embed.add_field(name='Aliases', value='`{}`'.format(aliases), inline=False)
                else:
                    aliases = '-'
                    embed.add_field(name='Aliases', value=aliases, inline=False)
                embed.set_footer(text='<> - required, [] - optional, | - either/or')
                await ctx.send(embed=embed)
            else:
                embed = discord.Embed(title='The command `{}` does not exist.'.format(cmd),
                                      color=0xff0000)
                await ctx.channel.send(embed=embed)

    @commands.command(name='commands', aliases=['cmds'], usage='commands', brief='3s', ignore_extra=False)
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def cmds(self, ctx):
        """Displays all commands."""
        prefix = get_prefix(ctx)
        embed = discord.Embed(description=f'To view information about a specified command use: '
                                          f'`{prefix}help [command]`\n'
                                          f'Current server prefix: `{prefix}`\n'
                                          f'\n'
                                          f'**Parameters:** `<> - required, [] - optional, | - either/or`\n'
                                          f'\n'
                                          f'Do __not__ include `<>` or `[]` when executing the command.\n'
                                          f'\n'
                                          f'**Search**\n'
                                          f'```'
                                          f'• {prefix}{self.bot.get_command("anime").usage}\n'
                                          f'• {prefix}{self.bot.get_command("manga").usage}\n'
                                          f'• {prefix}{self.bot.get_command("character").usage}\n'
                                          f'• {prefix}{self.bot.get_command("staff").usage}\n'
                                          f'• {prefix}{self.bot.get_command("studio").usage}\n'
                                          f'```'
                                          f'\n'
                                          f'**Info**\n'
                                          f'```'
                                          f'• {prefix}{self.bot.get_command("help").usage}\n'
                                          f'• {prefix}{self.bot.get_command("commands").usage}\n'
                                          f'```'
                                          f'\n'
                                          f'**Server Administrator**\n'
                                          f'```'
                                          f'• {prefix}{self.bot.get_command("prefix").usage}\n'
                                          f'```',
                              colour=0x4169E1, timestamp=ctx.message.created_at)
        embed.set_footer(text='Requested by {}'.format(ctx.author), icon_url=ctx.author.avatar_url)
        embed.set_author(name="AniSearch's commands".format(self.bot.user.name), icon_url=self.bot.user.avatar_url)
        await ctx.send(embed=embed)

    @commands.command(name='about', usage='about', brief='3s', ignore_extra=False)
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def about(self, ctx):
        """Displays information and stats about the bot."""
        embed = discord.Embed(title='About AniSearch',
                              description='<@!{}> is an easy-to-use Discord bot written in Python that allows '
                                          'you to search for Anime, Manga, Characters, Staff, Studios and '
                                          'Profiles right within Discord and displays the results from '
                                          '[AniList](https://anilist.co) and '
                                          '[MyAnimeList](https://myanimelist.net/)!'.format(737236600878137363),
                              color=0x4169E1, timestamp=ctx.message.created_at)
        embed.add_field(name='❯ Creator', value='<@!{}>'.format(223871059068321793),
                        inline=True)
        embed.add_field(name='❯ Version', value='v{}'.format(bot.version),
                        inline=True)
        embed.add_field(name='❯ Commands', value='as!help',
                        inline=True)
        proc = psutil.Process()
        with proc.oneshot():
            uptime = timedelta(seconds=round(time() - proc.create_time()))
        try:
            embed.add_field(name='❯ Uptime', value=str(uptime), inline=True)
        except AttributeError:
            embed.add_field(name='❯ Uptime', value='-',
                            inline=True)
        embed.add_field(name='❯ Guilds', value=str(len(self.bot.guilds)),
                        inline=True)
        users = 0
        for guild in self.bot.guilds:
            users = users + guild.member_count
        embed.add_field(name='❯ Users', value=users,
                        inline=True)
        embed.add_field(name='❯ Invite', value='[Click me!]({})'.format(invite),
                        inline=True)
        embed.add_field(name='❯ Vote', value='[Click me!]({})'.format(vote),
                        inline=True)
        embed.add_field(name='❯ GitHub', value='[Click me!]({})'.format(github),
                        inline=True)
        embed.set_thumbnail(url=self.bot.user.avatar_url)
        embed.set_footer(text='Requested by {}'.format(ctx.author), icon_url=ctx.author.avatar_url)
        await ctx.channel.send(embed=embed)

    @commands.command(name='prefix', usage='prefix <prefix>', brief='10s', ignore_extra=False)
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.has_permissions(administrator=True)
    async def prefix(self, ctx, prefix):
        """Changes the current server prefix."""
        if len(prefix) > 5:
            embed = discord.Embed(title='The prefix cannot be longer than 5 characters.', color=0xff0000)
            await ctx.channel.send(embed=embed)
        else:
            db = psycopg2.connect(host=config.DB_HOST, dbname=config.DB_NAME, user=config.DB_USER,
                                  password=config.BD_PASSWORD)
            cur = db.cursor()
            cur.execute('SELECT prefix FROM guilds WHERE id = %s;', (ctx.guild.id,))
            prefix_old = cur.fetchone()[0]
            cur.execute('UPDATE guilds SET prefix = %s WHERE id = %s;', (prefix, ctx.guild.id,))
            cur.execute('SELECT prefix FROM guilds WHERE id = %s;', (ctx.guild.id,))
            prefix = cur.fetchone()[0]
            db.commit()
            cur.close()
            db.close()
            if prefix == 'as!':
                embed = discord.Embed(title='Prefix resetted.', color=0x4169E1)
                await ctx.channel.send(embed=embed)
                logger.info('Resetted Prefix for Guild {}'.format(ctx.guild.id, prefix))
            else:
                embed = discord.Embed(title='Changed the prefix from `{}` to `{}`.'.format(prefix_old, prefix),
                                      color=0x4169E1)
                await ctx.channel.send(embed=embed)
                logger.info('Set Prefix for Guild {} to {}'.format(ctx.guild.id, prefix))
