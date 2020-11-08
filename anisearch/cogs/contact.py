import discord
from discord.ext import commands

from anisearch import bot


class Contact(commands.Cog, name='Contact'):

    def __init__(self, client):
        self.client = client

    @commands.command(name='contact', usage='contact <message>', brief='3s', ignore_extra=False)
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def cmd_contact(self, ctx, *, message):
        """Contacts the creator of the bot."""
        contact_embed = discord.Embed(title='Contact',
                                      color=0x4169E1)
        contact_embed.add_field(name='Author', value=ctx.author,
                                inline=True)
        contact_embed.add_field(name='ID', value=ctx.author.id,
                                inline=True)
        contact_embed.add_field(name='Message', value=message,
                                inline=False)
        user = await self.client.fetch_user(bot.__ownerid__)
        await user.send(embed=contact_embed)
        contact_return_embed = discord.Embed(title='Creator contacted', color=0x4169E1)
        await ctx.channel.send(embed=contact_return_embed)


def setup(client):
    client.add_cog(Contact(client))
    bot.logger.info('Loaded extension Contact')


def teardown():
    bot.logger.info('Unloaded extension Contact')
