import logging
from datetime import datetime

import nextcord
from nextcord import utils
from nextcord.ext import commands, application_checks

from anisearch.bot import AniSearchBot
from anisearch.cogs.help import HelpView

log = logging.getLogger(__name__)


class Events(commands.Cog, name='Events'):
    def __init__(self, bot: AniSearchBot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_guild_join(self, guild: nextcord.Guild):
        log.info(f'Bot joined guild {guild.id}')
        self.bot.db.insert_guild(guild)

        embed = nextcord.Embed(
            title='Hey there!',
            description=f'**Thanks for using <@!{737236600878137363}>!**\n\n'
                        f'A few things to get started with the bot:\n\n'
                        f'• To display all commands use:\n'
                        f'`as!{utils.get(self.bot.commands, name="commands").usage}`\n\n'
                        f'• To display information about a command use:\n'
                        f'`as!{utils.get(self.bot.commands, name="help").usage}`\n\n'
                        f'• To change the server prefix use:\n'
                        f'`as!{utils.get(self.bot.commands, name="setprefix").usage}`\n\n'
                        f'• Do **not** include `<>`, `[]` or `|` when executing a command.\n\n'
                        f'In case of any problems, bugs, suggestions or if you just '
                        f'want to chat, feel free to join the support server!\n\n'
                        f'**Have fun with the bot!**',
            color=0x4169E1
        )
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        embed.set_author(name='AniSearch Bot', icon_url=self.bot.user.display_avatar.url)

        try:
            await (await self.bot.fetch_user(guild.owner_id)).send(embed=embed, view=HelpView())
        except nextcord.errors.Forbidden:
            pass

    @commands.Cog.listener()
    async def on_guild_remove(self, guild: nextcord.Guild):
        log.info(f'Bot left guild {guild.id}')
        self.bot.db.delete_guild(guild)

    @commands.Cog.listener()
    async def on_application_command_error(self, interaction: nextcord.Interaction, exception: Exception):
        error = getattr(exception, 'original', exception)

        if isinstance(error, application_checks.errors.ApplicationNoPrivateMessage):
            title = 'This command cannot be used in private messages.'
        elif isinstance(error, application_checks.errors.ApplicationMissingPermissions):
            title = 'You are missing permissions to execute this command.'
        else:
            title = 'An unknown error occurred.'

            embed = nextcord.Embed(
                title=f':x: {error.__class__.__name__}',
                description=f'```{str(exception)}```',
                color=0xff0000
            )
            embed.set_author(name='AniSearch Command Error', icon_url=self.bot.user.display_avatar.url)
            embed.add_field(name='Command', value=f'`{interaction.application_command.qualified_name}`', inline=False)

            if interaction.data.get('options'):
                options = ', '.join([f'`{i.get("name")}: {i.get("value")}`' for i in interaction.data.get('options')])
                embed.add_field(name='Options', value=options, inline=False)

            await (await self.bot.application_info()).owner.send(embed=embed)

        embed = nextcord.Embed(title=f':x: {title}', color=0xff0000, timestamp=datetime.now())

        embed.set_author(name='AniSearch Error', icon_url=self.bot.user.display_avatar.url)
        embed.set_footer(text=interaction.user.display_name, icon_url=interaction.user.display_avatar)

        await interaction.response.send_message(embed=embed, ephemeral=True)


def setup(bot: AniSearchBot):
    bot.add_cog(Events(bot))
    log.info('Events cog loaded')


def teardown(bot: AniSearchBot):
    log.info('Events cog unloaded')
