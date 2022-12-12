from typing import Union, List, Dict

import discord


class BaseView(discord.ui.View):
    def __init__(self, interaction: discord.Interaction, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._interaction = interaction

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return self._interaction.user == interaction.user

    async def on_timeout(self) -> None:
        await self.close()

    async def close(self) -> None:
        if not self.is_finished():
            self.stop()
        try:
            await self._interaction.edit_original_response(view=None)
        except discord.NotFound:
            pass


class BasePaginationView(BaseView):
    def __init__(
        self,
        interaction: discord.Interaction,
        pages: Union[List[discord.Embed], List[List[discord.Embed]]],
        *args,
        **kwargs
    ) -> None:
        super().__init__(interaction, *args, **kwargs)
        self.pages = pages
        self.current_page = 0

        self.disable_unavailable_buttons()

    async def show_page(self, interaction: discord.Interaction, number: int) -> None:
        try:
            page = self.pages[number]
        except IndexError:
            return

        kwargs = await self._get_kwargs_from_page(page)

        self.current_page = number
        self.disable_unavailable_buttons()

        await interaction.response.edit_message(**kwargs, view=self)

    async def _get_kwargs_from_page(
        self, page: Union[discord.Embed, List[discord.Embed]]
    ) -> Dict[str, Union[discord.Embed, List[discord.Embed]]]:
        if isinstance(page, discord.Embed):
            return {'embed': page}
        elif isinstance(page, list) and all(isinstance(i, discord.Embed) for i in page):
            return {'embeds': page}
        raise TypeError

    def disable_unavailable_buttons(self) -> None:
        raise NotImplementedError

    async def go_to_first_page(self, interaction: discord.Interaction) -> None:
        await self.show_page(interaction, 0)

    async def go_to_previous_page(self, interaction: discord.Interaction) -> None:
        await self.show_page(interaction, self.current_page - 1)

    async def go_to_next_page(self, interaction: discord.Interaction) -> None:
        await self.show_page(interaction, self.current_page + 1)

    async def go_to_last_page(self, interaction: discord.Interaction) -> None:
        await self.show_page(interaction, len(self.pages) - 1)


class SimplePaginationView(BasePaginationView):
    def __init__(
        self,
        interaction: discord.Interaction,
        pages: Union[List[discord.Embed], List[List[discord.Embed]]],
        *args,
        **kwargs
    ) -> None:
        super().__init__(interaction, pages, *args, **kwargs)

    def disable_unavailable_buttons(self) -> None:
        self.on_previous.disabled = self.current_page == 0
        self.on_next.disabled = self.current_page == len(self.pages) - 1

    @discord.ui.button(emoji='\N{BLACK LEFT-POINTING TRIANGLE}', style=discord.ButtonStyle.blurple)
    async def on_previous(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.go_to_previous_page(interaction)

    @discord.ui.button(emoji='\N{BLACK RIGHT-POINTING TRIANGLE}', style=discord.ButtonStyle.blurple)
    async def on_next(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.go_to_next_page(interaction)

    @discord.ui.button(emoji='\N{WASTEBASKET}', style=discord.ButtonStyle.red)
    async def on_close(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.close()


class PaginationView(BasePaginationView):
    def __init__(
        self,
        interaction: discord.Interaction,
        pages: Union[List[discord.Embed], List[List[discord.Embed]]],
        *args,
        **kwargs
    ) -> None:
        super().__init__(interaction, pages, *args, **kwargs)

    def disable_unavailable_buttons(self) -> None:
        self.on_first.disabled = self.on_previous.disabled = self.current_page == 0
        self.on_last.disabled = self.on_next.disabled = self.current_page == len(self.pages) - 1

    @discord.ui.button(
        emoji='\N{BLACK LEFT-POINTING DOUBLE TRIANGLE WITH VERTICAL BAR}', style=discord.ButtonStyle.blurple
    )
    async def on_first(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.go_to_first_page(interaction)

    @discord.ui.button(emoji='\N{BLACK LEFT-POINTING TRIANGLE}', style=discord.ButtonStyle.blurple)
    async def on_previous(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.go_to_previous_page(interaction)

    @discord.ui.button(emoji='\N{BLACK RIGHT-POINTING TRIANGLE}', style=discord.ButtonStyle.blurple)
    async def on_next(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.go_to_next_page(interaction)

    @discord.ui.button(
        emoji='\N{BLACK RIGHT-POINTING DOUBLE TRIANGLE WITH VERTICAL BAR}', style=discord.ButtonStyle.blurple
    )
    async def on_last(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.go_to_last_page(interaction)

    @discord.ui.button(emoji='\N{WASTEBASKET}', style=discord.ButtonStyle.red)
    async def on_close(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.close()
