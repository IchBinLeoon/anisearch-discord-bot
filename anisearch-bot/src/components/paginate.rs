use std::future::pending;
use std::time::Duration;

use poise::serenity_prelude::{
    ButtonStyle, CacheHttp, ComponentInteraction, ComponentInteractionCollector,
    Context as SerenityContext, CreateActionRow, CreateButton, CreateComponent, CreateEmbed,
    CreateInteractionResponse, CreateInteractionResponseMessage, EmojiId, ModalInteraction,
    ModalInteractionCollector, UserId,
};
use poise::{CreateReply, Modal};
use tokio::sync::mpsc::{UnboundedSender, unbounded_channel};
use tokio::task::JoinHandle;
use tokio::{select, spawn};

use crate::Context;
use crate::components::ComponentError;

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

    custom_ids: Vec<String>,

    is_cancelled: bool,
}

impl<'a> Paginator<'a> {
    pub async fn paginate(&mut self, ctx: Context<'_>) -> Result<(), ComponentError> {
        let ctx_id = ctx.id();

        self.create_custom_ids(ctx_id);

        let msg_handle = ctx.send(self.create_reply()).await?;

        let (tx, mut rx) = unbounded_channel::<Event>();

        let collector_task = spawn(handle_interaction_collector(
            ctx.serenity_context().clone(),
            ctx_id,
            self.timeout,
            ctx.author().id,
            self.custom_ids.clone(),
            tx,
        ));

        while let Some(event) = rx.recv().await {
            let interaction = match event {
                Event::First(interaction) => {
                    self.go_to_first_page();
                    interaction
                }
                Event::Previous(interaction) => {
                    self.go_to_previous_page();
                    interaction
                }
                Event::Next(interaction) => {
                    self.go_to_next_page();
                    interaction
                }
                Event::Last(interaction) => {
                    self.go_to_last_page();
                    interaction
                }
                Event::Page(interaction, page) => {
                    self.go_to_page(page);

                    interaction
                        .create_response(ctx.http(), self.create_interaction_response())
                        .await?;

                    continue;
                }
                Event::Cancel => {
                    break;
                }
            };

            interaction
                .create_response(ctx.http(), self.create_interaction_response())
                .await?;
        }

        self.is_cancelled = true;

        msg_handle.edit(ctx, self.create_reply()).await?;

        collector_task.await?
    }

    fn create_custom_ids(&mut self, ctx_id: u64) {
        self.custom_ids = vec![
            format!("{ctx_id}_first"),
            format!("{ctx_id}_prev"),
            format!("{ctx_id}_next"),
            format!("{ctx_id}_last"),
            format!("{ctx_id}_page"),
            format!("{ctx_id}_modal"),
        ];
    }

    fn render_components(&self) -> Vec<CreateComponent> {
        let mut components = vec![];

        if !self.is_cancelled {
            let left_disabled = self.is_first_page();
            let right_disabled = self.is_last_page();

            let buttons = vec![
                CreateButton::new(&self.custom_ids[0])
                    .emoji(PAGE_FIRST_EMOJI)
                    .style(ButtonStyle::Secondary)
                    .disabled(left_disabled),
                CreateButton::new(&self.custom_ids[1])
                    .emoji(PAGE_PREV_EMOJI)
                    .style(ButtonStyle::Primary)
                    .disabled(left_disabled),
                CreateButton::new(&self.custom_ids[4])
                    .label(format!("{}/{}", self.current_page + 1, self.pages.len()))
                    .style(ButtonStyle::Secondary),
                CreateButton::new(&self.custom_ids[2])
                    .emoji(PAGE_NEXT_EMOJI)
                    .style(ButtonStyle::Primary)
                    .disabled(right_disabled),
                CreateButton::new(&self.custom_ids[3])
                    .emoji(PAGE_LAST_EMOJI)
                    .style(ButtonStyle::Secondary)
                    .disabled(right_disabled),
            ];

            components.push(CreateComponent::ActionRow(CreateActionRow::buttons(
                buttons,
            )));
        }

        if let Some(buttons) = self.get_current_page().buttons {
            components.push(CreateComponent::ActionRow(CreateActionRow::buttons(
                buttons,
            )));
        }

        components
    }

    fn create_reply(&self) -> CreateReply {
        CreateReply::new()
            .embed(self.get_current_page().embed)
            .components(self.render_components())
            .ephemeral(self.ephemeral)
    }

    fn create_interaction_response(&self) -> CreateInteractionResponse {
        CreateInteractionResponse::UpdateMessage(
            CreateInteractionResponseMessage::new()
                .embed(self.get_current_page().embed)
                .components(self.render_components())
                .ephemeral(self.ephemeral),
        )
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
        if page >= 1 && page <= self.pages.len() {
            self.current_page = page - 1;
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

enum Event {
    First(ComponentInteraction),
    Previous(ComponentInteraction),
    Next(ComponentInteraction),
    Last(ComponentInteraction),
    Page(ModalInteraction, usize),
    Cancel,
}

async fn handle_interaction_collector(
    serenity_ctx: SerenityContext,
    ctx_id: u64,
    timeout: Duration,
    author_id: UserId,
    custom_ids: Vec<String>,
    tx: UnboundedSender<Event>,
) -> Result<(), ComponentError> {
    let mut modal_task: Option<JoinHandle<Result<(), ComponentError>>> = None;

    let res = async {
        loop {
            select! {
                interaction = ComponentInteractionCollector::new(&serenity_ctx)
                    .author_id(author_id)
                    .filter(move |i| i.data.custom_id.starts_with(&ctx_id.to_string()))
                    .timeout(timeout)
                => {
                    match interaction {
                        Some(interaction) => {
                            let id = interaction.data.custom_id.as_str();

                            if id == custom_ids[0] {
                                tx.send(Event::First(interaction))?;
                            } else if id == custom_ids[1] {
                                tx.send(Event::Previous(interaction))?;
                            } else if id == custom_ids[2] {
                                tx.send(Event::Next(interaction))?;
                            } else if id == custom_ids[3] {
                                tx.send(Event::Last(interaction))?;
                            } else if id == custom_ids[4] {
                                let modal_id = custom_ids[5].clone();

                                interaction
                                    .create_response(
                                        serenity_ctx.http(),
                                        PageModal::create(None, modal_id.clone()),
                                    )
                                    .await?;

                                if let Some(task) = &modal_task && !task.is_finished() {
                                    continue;
                                }

                                let serenity_ctx = serenity_ctx.clone();
                                let tx = tx.clone();

                                modal_task = Some(spawn(async move {
                                    if let Some(interaction) = ModalInteractionCollector::new(&serenity_ctx)
                                        .author_id(author_id)
                                        .filter(move |i| i.data.custom_id.as_str() == modal_id)
                                        .timeout(timeout)
                                        .await
                                    {
                                        let modal = PageModal::parse(interaction.clone().data);

                                        if let Ok(page) = modal.page.parse::<usize>() {
                                            tx.send(Event::Page(interaction, page))?;
                                        } else {
                                            interaction
                                                .create_response(
                                                    serenity_ctx.http(),
                                                    CreateInteractionResponse::Acknowledge,
                                                )
                                                .await?;
                                        }
                                    }

                                    Ok(())
                                }));
                            }
                        }
                        None => {
                            return Ok(());
                        }
                    }
                }

                modal_res = async {
                    match modal_task.as_mut() {
                        Some(task) => task.await,
                        None => pending().await,
                    }
                } => {
                    modal_res??;

                    modal_task = None;
                }
            }
        }
    }.await;

    if let Some(task) = modal_task {
        task.abort();
    }

    tx.send(Event::Cancel)?;

    res
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
            custom_ids: Vec::new(),
            is_cancelled: false,
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
