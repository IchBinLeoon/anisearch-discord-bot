from discord.ext import menus


class EmbedListMenu(menus.ListPageSource):
    def __init__(self, data):
        super().__init__(data, per_page=1)

    async def format_page(self, menu, embeds):
        return embeds
