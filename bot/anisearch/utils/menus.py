import logging

from nextcord.ext import menus

log = logging.getLogger(__name__)


class EmbedListButtonMenu(menus.ListPageSource):

    def __init__(self, data):
        super().__init__(data, per_page=1)

    async def format_page(self, menu, embeds):
        return embeds


class SearchButtonMenuPages(menus.ButtonMenuPages):
    STOP = '\N{CROSS MARK}'


class ProfileButtonMenuPages(menus.ButtonMenuPages, inherit_buttons=False):
    PREVIOUS_PAGE = '\N{BUST IN SILHOUETTE}'
    NEXT_PAGE = '\N{WHITE MEDIUM STAR}'
    STOP = '\N{CROSS MARK}'

    def __init__(self, source, **kwargs):
        super().__init__(source, **kwargs)

        self.add_item(menus.MenuPaginationButton(emoji=self.PREVIOUS_PAGE))
        self.add_item(menus.MenuPaginationButton(emoji=self.NEXT_PAGE))
        self.add_item(menus.MenuPaginationButton(emoji=self.STOP))

        self._disable_unavailable_buttons()


