import re

import aiohttp
import discord
from discord.ext import commands

from anisearch.bot import logger


class Source(commands.Cog, name='Source'):

    def __init__(self, client):
        self.client = client

    @commands.command(name='source', aliases=['sauce'], usage='source <image-url|with image as attachment>',
                      brief='5s', ignore_extra=False)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def cmd_source(self, ctx, source=None):
        """Tries to find the source of an image through the image url or the image as attachment."""
        url = None
        if source is None:
            if ctx.message.attachments:
                url = ctx.message.attachments[0].url
            else:
                error_embed = discord.Embed(title='No image to look for the source', color=0xff0000)
                await ctx.channel.send(embed=error_embed)
                logger.info('Server: %s | Response: No image' % ctx.guild.name)
        else:
            url = source
        if url:
            if not url.endswith(('.jpg', '.png', '.bmp', '.gif', '.jpeg')):
                error_embed = discord.Embed(title='No correct url specified', color=0xff0000)
                await ctx.channel.send(embed=error_embed)
                logger.info('Server: %s | Response: No correct url' % ctx.guild.name)
            else:
                saucenao = 'http://saucenao.com/search.php?db=999&url=%s' % url
                async with aiohttp.ClientSession() as cs:
                    async with cs.get(saucenao) as r:
                        content = await r.text()
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
                        source_embed = discord.Embed(title='Source', color=0x4169E1, timestamp=ctx.message.created_at)
                        source_embed.set_thumbnail(url=url)
                        if material:
                            source_embed.add_field(name='Material', value=material.group(1), inline=False)
                        if artist:
                            source_embed.add_field(name='Artist', value=artist.group(1), inline=False)
                        if characters:
                            source_embed.add_field(name='Characters', value=str(characters.group(1))
                                                   .replace('<br />', ', '), inline=False)
                        if pixiv:
                            source_embed.add_field(name='Pixiv', value=pixiv.group(1), inline=False)
                        if danbooru:
                            source_embed.add_field(name='Danbooru', value='https://danbooru.donmai.us/post/show/' +
                                                                          danbooru.group(1), inline=False)
                        if gelbooru:
                            source_embed.add_field(name='Gelbooru',
                                                   value='https://gelbooru.com/index.php?page=post&s=view&id=' +
                                                         gelbooru.group(1), inline=False)
                        if yandere:
                            source_embed.add_field(name='Yande.re',
                                                   value='https://yande.re/post/show/' + yandere.group(1), inline=False)
                        if konachan:
                            source_embed.add_field(name='Konachan',
                                                   value='http://konachan.com/post/show/' + konachan.group(1),
                                                   inline=False)
                        if sankaku:
                            source_embed.add_field(name='Sankaku',
                                                   value='https://chan.sankakucomplex.com/post/show/' +
                                                         sankaku.group(1), inline=False)
                        source_embed.set_footer(text='Provided by https://saucenao.com')
                        if material or artist or characters or pixiv or danbooru or gelbooru or yandere or konachan or \
                                sankaku:
                            await ctx.channel.send(embed=source_embed)
                            logger.info('Server: %s | Response: Source' % ctx.guild.name)
                        else:
                            error_embed = discord.Embed(title='No source found', color=0xff0000)
                            await ctx.channel.send(embed=error_embed)
                            logger.info('Server: %s | Response: No source found' % ctx.guild.name)
