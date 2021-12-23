"""
This file is part of the AniSearch Discord Bot.

Copyright (C) 2021 IchBinLeoon

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.
"""

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


