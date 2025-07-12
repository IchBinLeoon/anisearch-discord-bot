use std::time::Duration;

use poise::serenity_prelude::{
    ButtonStyle, ComponentInteractionCollector, CreateActionRow, CreateButton, CreateEmbed,
    CreateInteractionResponse, CreateInteractionResponseMessage, EmojiId,
};
use poise::{CreateReply, Modal, execute_modal_on_component_interaction};

use crate::Context;
use crate::error::Result;

const PAGE_PREV_EMOJI: EmojiId = EmojiId::new(1393372751624011806);
const PAGE_NEXT_EMOJI: EmojiId = EmojiId::new(1393372843039002656);
const PAGE_FIRST_EMOJI: EmojiId = EmojiId::new(1393372856200597584);
const PAGE_LAST_EMOJI: EmojiId = EmojiId::new(1393372866120122398);

#[derive(Debug, Modal)]
#[name = "Skip to Page"]
struct PageModal {
    #[name = "Page Number"]
    #[placeholder = "Enter a page number..."]
    page: String,
}

pub struct Paginator<'a> {
    pages: Vec<Page<'a>>,
    current_page: usize,

    timeout: Duration,
    ephemeral: bool,

    button_ids: Vec<String>,

    is_closed: bool,
}

impl<'a> Paginator<'a> {
    pub async fn paginate(&mut self, ctx: Context<'_>) -> Result<()> {
        let ctx_id = ctx.id();

        self.create_button_ids(ctx_id);

        let handle = ctx
            .send(self.create_reply(self.render_components()))
            .await?;

        while let Some(interaction) = ComponentInteractionCollector::new(ctx.serenity_context())
            .filter(move |interaction| interaction.data.custom_id.starts_with(&ctx_id.to_string()))
            .timeout(self.timeout)
            .await
        {
            if interaction.user.id != ctx.author().id {
                continue;
            }

            let id = interaction.data.custom_id.as_str();

            if id == self.button_ids[0] {
                self.go_to_first_page()
            } else if id == self.button_ids[1] {
                self.go_to_previous_page()
            } else if id == self.button_ids[2] {
                self.go_to_next_page()
            } else if id == self.button_ids[3] {
                self.go_to_last_page()
            } else if id == self.button_ids[4] {
                let data = execute_modal_on_component_interaction::<PageModal>(
                    ctx.serenity_context(),
                    interaction.clone(),
                    None,
                    Some(self.timeout),
                )
                .await?;

                if let Some(modal) = data {
                    if let Ok(page) = modal.page.parse::<usize>() {
                        self.go_to_page(page);

                        handle
                            .edit(ctx, self.create_reply(self.render_components()))
                            .await?;
                    }
                }

                continue;
            }

            interaction
                .create_response(
                    ctx.http(),
                    CreateInteractionResponse::UpdateMessage(
                        CreateInteractionResponseMessage::new()
                            .embed(self.get_current_page().embed)
                            .components(self.render_components())
                            .ephemeral(self.ephemeral),
                    ),
                )
                .await?;
        }

        self.is_closed = true;

        handle
            .edit(ctx, self.create_reply(self.render_components()))
            .await?;

        Ok(())
    }

    fn create_button_ids(&mut self, ctx_id: u64) {
        self.button_ids = vec![
            format!("{ctx_id}_first"),
            format!("{ctx_id}_prev"),
            format!("{ctx_id}_next"),
            format!("{ctx_id}_last"),
            format!("{ctx_id}_page"),
        ];
    }

    fn render_components(&self) -> Vec<CreateActionRow> {
        let mut components = vec![];

        if !self.is_closed {
            let left_disabled = self.is_first_page();
            let right_disabled = self.is_last_page();

            let buttons = vec![
                CreateButton::new(&self.button_ids[0])
                    .emoji(PAGE_FIRST_EMOJI)
                    .style(ButtonStyle::Secondary)
                    .disabled(left_disabled),
                CreateButton::new(&self.button_ids[1])
                    .emoji(PAGE_PREV_EMOJI)
                    .style(ButtonStyle::Primary)
                    .disabled(left_disabled),
                CreateButton::new(&self.button_ids[4])
                    .label(format!("{}/{}", self.current_page + 1, self.pages.len()))
                    .style(ButtonStyle::Secondary),
                CreateButton::new(&self.button_ids[2])
                    .emoji(PAGE_NEXT_EMOJI)
                    .style(ButtonStyle::Primary)
                    .disabled(right_disabled),
                CreateButton::new(&self.button_ids[3])
                    .emoji(PAGE_LAST_EMOJI)
                    .style(ButtonStyle::Secondary)
                    .disabled(right_disabled),
            ];

            components.push(CreateActionRow::buttons(buttons));
        }

        if let Some(buttons) = self.get_current_page().buttons {
            components.push(CreateActionRow::buttons(buttons));
        }

        components
    }

    fn create_reply(&self, components: Vec<CreateActionRow<'a>>) -> CreateReply<'a> {
        CreateReply::new()
            .embed(self.get_current_page().embed)
            .components(components)
            .ephemeral(self.ephemeral)
    }

    fn get_current_page(&self) -> Page<'a> {
        self.pages[self.current_page].clone()
    }

    fn is_first_page(&self) -> bool {
        self.current_page == 0
    }

    fn is_last_page(&self) -> bool {
        self.current_page == self.pages.len() - 1
    }

    fn go_to_page(&mut self, page: usize) {
        let page = page.saturating_sub(1);

        if page > self.pages.len() - 1 {
            self.go_to_last_page()
        } else {
            self.current_page = page;
        }
    }

    fn go_to_first_page(&mut self) {
        self.current_page = 0;
    }

    fn go_to_previous_page(&mut self) {
        if self.current_page > 0 {
            self.current_page -= 1;
        }
    }

    fn go_to_next_page(&mut self) {
        if self.current_page < self.pages.len() - 1 {
            self.current_page += 1;
        }
    }

    fn go_to_last_page(&mut self) {
        self.current_page = self.pages.len() - 1;
    }
}

impl<'a> Paginator<'a> {
    pub fn builder() -> PaginatorBuilder<'a> {
        PaginatorBuilder::default()
    }
}

pub struct PaginatorBuilder<'a> {
    pages: Vec<Page<'a>>,
    timeout: Duration,
    ephemeral: bool,
}

impl<'a> PaginatorBuilder<'a> {
    pub fn pages(mut self, pages: Vec<Page<'a>>) -> Self {
        self.pages = pages;
        self
    }

    pub fn timeout(mut self, timeout: Duration) -> Self {
        self.timeout = timeout;
        self
    }

    pub fn ephemeral(mut self, ephemeral: bool) -> Self {
        self.ephemeral = ephemeral;
        self
    }

    pub fn build(self) -> Paginator<'a> {
        Paginator {
            pages: self.pages,
            current_page: 0,
            timeout: self.timeout,
            ephemeral: self.ephemeral,
            button_ids: Vec::new(),
            is_closed: false,
        }
    }
}

impl<'a> Default for PaginatorBuilder<'a> {
    fn default() -> Self {
        Self {
            pages: Vec::new(),
            timeout: Duration::from_secs(180),
            ephemeral: false,
        }
    }
}

#[derive(Clone)]
pub struct Page<'a> {
    embed: CreateEmbed<'a>,
    buttons: Option<Vec<CreateButton<'a>>>,
}

impl<'a> Page<'a> {
    pub fn new(embed: CreateEmbed<'a>) -> Self {
        Self {
            embed,
            buttons: None,
        }
    }

    pub fn add_link_buttons(mut self, buttons: Vec<CreateButton<'a>>) -> Self {
        self.buttons = Some(buttons);
        self
    }
}
