import discord
from discord.ext import commands

import main


class ErrorHandler(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):

        if isinstance(error, commands.CommandNotFound):
            error_embed = discord.Embed(title='The command was not found',
                                        color=0xff0000)
            await ctx.channel.send(embed=error_embed)
            main.logger.info('Server: %s | Author: %s | Try: %s' % (ctx.guild.name, ctx.author, ctx.message.content))
            main.logger.info('Server: %s | Response: Command not found' % ctx.guild.name)

        if isinstance(error, commands.CommandOnCooldown):
            error_embed = discord.Embed(title='The command is on cooldown for `{:.2f}s`'.format(error.retry_after),
                                        color=0xff0000)
            await ctx.channel.send(embed=error_embed)
            main.logger.info('Server: %s | Response: Command on cooldown' % ctx.guild.name)

        if isinstance(error, commands.TooManyArguments):
            error_embed = discord.Embed(title='Too many arguments',
                                        color=0xff0000)
            await ctx.channel.send(embed=error_embed)
            main.logger.info('Server: %s | Response: Too many arguments' % ctx.guild.name)

        if isinstance(error, commands.MissingRequiredArgument):
            error_embed = discord.Embed(title='Missing required argument',
                                        color=0xff0000)
            await ctx.channel.send(embed=error_embed)
            main.logger.info('Server: %s | Response: Missing required argument' % ctx.guild.name)

        if isinstance(error, commands.BadArgument):
            error_embed = discord.Embed(title='Wrong arguments',
                                        color=0xff0000)
            await ctx.channel.send(embed=error_embed)
            main.logger.info('Server: %s | Response: Wrong arguments' % ctx.guild.name)

        if isinstance(error, commands.MissingPermissions):
            error_embed = discord.Embed(title='Missing permissions',
                                        color=0xff0000)
            await ctx.channel.send(embed=error_embed)
            main.logger.info('Server: %s | Response: Missing permissions' % ctx.guild.name)


def setup(client):
    client.add_cog(ErrorHandler(client))
    main.logger.info('Loaded extension ErrorHandler')


def teardown():
    main.logger.info('Unloaded extension ErrorHandler')
