import discord


def anilist_request_error_embed(ctx, cmd, text, exception):
    embed = discord.Embed(title='Error', description='An error occurred while searching the {} `{}`.\n\n'
                                                     '**Exception:** `{}`'.format(cmd, text, exception),
                          color=0xff0000, timestamp=ctx.message.created_at)
    embed.set_footer(text='Requested by {}'.format(ctx.author), icon_url=ctx.author.avatar_url)
    return embed


def anilist_not_found_error_embed(ctx, cmd, text):
    embed = discord.Embed(title='The {} `{}` could not be found.'.format(cmd, text), color=0xff0000)
    return embed


def anilist_load_embed_error_embed(ctx, cmd, exception, current_page, pages):
    embed = discord.Embed(title='Error', description='An error occurred while loading the embed for '
                                                     'the {}.\n\n**Exception:** `{}`'.format(cmd, exception),
                          color=0xff0000, timestamp=ctx.message.created_at)
    embed.set_footer(text='Requested by {} • Page {}/{}'.format(ctx.author, current_page, pages),
                     icon_url=ctx.author.avatar_url)
    return embed
