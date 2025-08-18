use poise::ChoiceParameter;
use strum::Display;

use crate::clients::anilist::media_query::{MediaSeason, MediaSort, MediaType};

#[derive(Display, ChoiceParameter)]
pub enum MediaChoice {
    Anime,
    Manga,
}

impl From<MediaChoice> for MediaType {
    fn from(value: MediaChoice) -> Self {
        match value {
            MediaChoice::Anime => MediaType::ANIME,
            MediaChoice::Manga => MediaType::MANGA,
        }
    }
}

#[derive(ChoiceParameter)]
pub enum SeasonChoice {
    Winter,
    Spring,
    Summer,
    Fall,
}

impl From<SeasonChoice> for MediaSeason {
    fn from(value: SeasonChoice) -> Self {
        match value {
            SeasonChoice::Winter => MediaSeason::WINTER,
            SeasonChoice::Spring => MediaSeason::SPRING,
            SeasonChoice::Summer => MediaSeason::SUMMER,
            SeasonChoice::Fall => MediaSeason::FALL,
        }
    }
}

#[derive(ChoiceParameter)]
pub enum SortChoice {
    Popularity,
    Score,
    #[name = "Start Date"]
    StartDate,
    Title,
}

impl From<SortChoice> for MediaSort {
    fn from(value: SortChoice) -> Self {
        match value {
            SortChoice::Popularity => MediaSort::POPULARITY_DESC,
            SortChoice::Score => MediaSort::SCORE_DESC,
            SortChoice::StartDate => MediaSort::START_DATE,
            SortChoice::Title => MediaSort::TITLE_ROMAJI,
        }
    }
}
