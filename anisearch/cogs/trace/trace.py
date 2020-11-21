import re

import discord
from discord.ext import commands, menus
from anisearch.utils.logger import logger
from anisearch.utils.menus import EmbedListMenu
from anisearch.utils.trace import trace, source


class Trace(commands.Cog, name='Trace'):

    def __init__(self, bot):
        self.bot = bot

    async def _trace(self, ctx, url):
        embeds = []
        try:
            data = (await trace(url))
        except Exception as exception:
            logger.exception(exception)
            embed = discord.Embed(title='Error', description='An error occurred while searching for the anime.',
                                  color=0xff0000, timestamp=ctx.message.created_at)
            embed.set_footer(text='Requested by {}'.format(ctx.author), icon_url=ctx.author.avatar_url)
            embeds.append(embed)
            return embeds
        if data is not None and len(data['docs']) > 0:
            data = data['docs']
            pages = len(data)
            current_page = 0
            for anime in data:
                current_page += 1
                try:
                    embed = discord.Embed(color=0x4169E1)
                    if anime['title_english'] is None or anime['title_english'] == anime['title_romaji']:
                        embed.title = anime['title_romaji']
                    else:
                        embed.title = '{} ({})'.format(anime['title_romaji'], anime['title_english'])
                    try:
                        image_url = f"https://trace.moe/thumbnail.php?anilist_id={anime['anilist_id']}&file=" \
                                    f"{anime['filename']}&t={anime['at']}&token={anime['tokenthumb']}" \
                            .replace(' ', '%20')
                        embed.set_image(url=image_url)
                    except Exception as exception:
                        logger.exception(exception)
                        pass
                    if anime['episode']:
                        embed.add_field(name='Episode', value=anime['episode'], inline=False)
                    if anime['synonyms']:
                        embed.add_field(name='Synonyms', value=', '.join(anime['synonyms']), inline=False)
                    if anime['anilist_id']:
                        anilist_link = 'https://anilist.co/anime/{}'.format(str(anime['anilist_id']))
                        embed.add_field(name='Anilist Link', value=anilist_link, inline=False)
                    if anime['mal_id']:
                        myanimelist_link = 'https://myanimelist.net/anime/{}'.format(str(anime['mal_id']))
                        embed.add_field(name='MyAnimeList Link', value=myanimelist_link, inline=False)
                    embed.set_footer(text='Provided by https://trace.moe • Page {}/{}'.format(current_page, pages))
                    embeds.append(embed)
                except Exception as exception:
                    logger.exception(exception)
                    embed = discord.Embed(title='Error', description='An error occurred while loading the embed.',
                                          color=0xff0000)
                    embed.set_footer(text='Provided by https://trace.moe • Page {}/{}'.format(current_page, pages))
                    embeds.append(embed)
            return embeds

    async def _source(self, ctx, url):
        embeds = []
        try:
            content = (await source(url))
            material = re.search(r'<strong>Material: </strong>(.*?)<br', content)
            artist = re.search(r'<strong>Creator: </strong>(.*?)<br', content)
            characters = re.search(r'<strong>Characters: </strong><br />(.*?)<br /></div>', content)
            pixiv = re.search(r'<strong>Pixiv ID: </strong><a href=\"(.*?)\" class', content)
            danbooru = re.search(r'<a href=\"https://danbooru\.donmai\.us/post/show/(\d+)\">', content)
            gelbooru = re.search(
                r'<a href=\"https://gelbooru\.com/index\.php\?page=post&s=view&id=(\d+)\">', content)
            yandere = re.search(r'<a href=\"https://yande\.re/post/show/(\d+)\">', content)
            konachan = re.search(r'<a href=\"http://konachan\.com/post/show/(\d+)\">', content)
            sankaku = re.search(r'<a href=\"https://chan\.sankakucomplex\.com/post/show/(\d+)\">', content)
            embed = discord.Embed(title='Source', color=0x4169E1)
            embed.set_thumbnail(url=url)
            if material:
                embed.add_field(name='Material', value=material.group(1), inline=False)
            if artist:
                embed.add_field(name='Artist', value=artist.group(1), inline=False)
            if characters:
                embed.add_field(name='Characters', value=str(characters.group(1)).replace('<br />', ', '), inline=False)
            if pixiv:
                embed.add_field(name='Pixiv', value=pixiv.group(1), inline=False)
            if danbooru:
                embed.add_field(name='Danbooru', value='https://danbooru.donmai.us/post/show/' +
                                                       danbooru.group(1), inline=False)
            if gelbooru:
                embed.add_field(name='Gelbooru', value='https://gelbooru.com/index.php?page=post&s=view&id=' +
                                gelbooru.group(1), inline=False)
            if yandere:
                embed.add_field(name='Yande.re',
                                value='https://yande.re/post/show/' + yandere.group(1), inline=False)
            if konachan:
                embed.add_field(name='Konachan', value='http://konachan.com/post/show/' + konachan.group(1),
                                inline=False)
            if sankaku:
                embed.add_field(name='Sankaku', value='https://chan.sankakucomplex.com/post/show/' +
                                sankaku.group(1), inline=False)
            embed.set_footer(text='Provided by https://saucenao.com')
            if material or artist or characters or pixiv or danbooru or gelbooru or yandere or konachan or sankaku:
                embeds.append(embed)
        except Exception as exception:
            logger.exception(exception)
            embed = discord.Embed(title='Error', description='An error occurred while searching for the source.',
                                  color=0xff0000)
            embed.set_footer(text='Requested by {}'.format(ctx.author), icon_url=ctx.author.avatar_url)
            embeds.append(embed)
        return embeds

    @commands.command(name='trace', aliases=['t'],
                      usage='trace <image-url|with image as attachment>', brief='5s', ignore_extra=False)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def cmd_trace(self, ctx, source=None):
        """Tries to find the anime the image is from through the image url or the image as attachment."""
        async with ctx.channel.typing():
            url = None
            if source is None:
                if ctx.message.attachments:
                    url = ctx.message.attachments[0].url
                else:
                    embed = discord.Embed(title='No image to look for the anime.', color=0xff0000)
                    await ctx.channel.send(embed=embed)
            else:
                url = source
            if url:
                if not url.endswith(('.jpg', '.png', '.bmp', '.jpeg')):
                    embed = discord.Embed(title='No correct url specified.', color=0xff0000)
                    await ctx.channel.send(embed=embed)
                else:
                    embeds = await self._trace(ctx, url)
                    if embeds:
                        menu = menus.MenuPages(source=EmbedListMenu(embeds), clear_reactions_after=True, timeout=30)
                        await menu.start(ctx)
                    else:
                        embed = discord.Embed(title='No anime found.', color=0xff0000)
                        await ctx.channel.send(embed=embed)

    @commands.command(name='source', aliases=['sauce'],
                      usage='source <image-url|with image as attachment>', brief='5s', ignore_extra=False)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def cmd_source(self, ctx, source=None):
        """Tries to find the source of an image through the image url or the image as attachment."""
        async with ctx.channel.typing():
            url = None
            if source is None:
                if ctx.message.attachments:
                    url = ctx.message.attachments[0].url
                else:
                    embed = discord.Embed(title='No image to look for the source.', color=0xff0000)
                    await ctx.channel.send(embed=embed)
            else:
                url = source
            if url:
                if not url.endswith(('.jpg', '.png', '.bmp', '.jpeg', '.gif')):
                    embed = discord.Embed(title='No correct url specified.', color=0xff0000)
                    await ctx.channel.send(embed=embed)
                else:
                    embeds = await self._source(ctx, url)
                    if embeds:
                        await ctx.channel.send(embed=embeds[0])
                    else:
                        embed = discord.Embed(title='No source found.', color=0xff0000)
                        await ctx.channel.send(embed=embed)
