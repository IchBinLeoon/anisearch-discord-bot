use tokio::sync::RwLock;

use crate::services::anilist::AUTOCOMPLETE_LIMIT;
use crate::services::anilist::trie::Trie;

pub struct AniListAutocompleteCache {
    anime_titles: RwLock<Trie>,
    manga_titles: RwLock<Trie>,
    character_names: RwLock<Trie>,
    staff_names: RwLock<Trie>,
    studio_names: RwLock<Trie>,
    genres: RwLock<Option<Trie>>,
    tags: RwLock<Option<Trie>>,
}

impl AniListAutocompleteCache {
    pub fn new() -> Self {
        Self {
            anime_titles: RwLock::new(Trie::new()),
            manga_titles: RwLock::new(Trie::new()),
            character_names: RwLock::new(Trie::new()),
            staff_names: RwLock::new(Trie::new()),
            studio_names: RwLock::new(Trie::new()),
            genres: RwLock::new(None),
            tags: RwLock::new(None),
        }
    }

    async fn search(lock: &RwLock<Trie>, word: &str) -> Vec<String> {
        let guard = lock.read().await;

        guard.search(word, AUTOCOMPLETE_LIMIT)
    }

    async fn insert(lock: &RwLock<Trie>, words: Vec<String>) {
        let mut guard = lock.write().await;

        for word in &words {
            guard.insert(word);
        }
    }

    pub async fn search_anime_titles(&self, title: &str) -> Vec<String> {
        Self::search(&self.anime_titles, title).await
    }

    pub async fn search_manga_titles(&self, title: &str) -> Vec<String> {
        Self::search(&self.manga_titles, title).await
    }

    pub async fn search_character_names(&self, name: &str) -> Vec<String> {
        Self::search(&self.character_names, name).await
    }

    pub async fn search_staff_names(&self, name: &str) -> Vec<String> {
        Self::search(&self.staff_names, name).await
    }

    pub async fn search_studio_names(&self, name: &str) -> Vec<String> {
        Self::search(&self.studio_names, name).await
    }

    pub async fn insert_anime_titles(&self, titles: Vec<String>) {
        Self::insert(&self.anime_titles, titles).await;
    }

    pub async fn insert_manga_titles(&self, titles: Vec<String>) {
        Self::insert(&self.manga_titles, titles).await;
    }

    pub async fn insert_character_names(&self, names: Vec<String>) {
        Self::insert(&self.character_names, names).await;
    }

    pub async fn insert_staff_names(&self, names: Vec<String>) {
        Self::insert(&self.staff_names, names).await;
    }

    pub async fn insert_studio_names(&self, names: Vec<String>) {
        Self::insert(&self.studio_names, names).await;
    }

    async fn search_option(lock: &RwLock<Option<Trie>>, word: &str) -> Option<Vec<String>> {
        let guard = lock.read().await;

        (*guard)
            .as_ref()
            .map(|trie| trie.search(word, AUTOCOMPLETE_LIMIT))
    }

    async fn insert_option(lock: &RwLock<Option<Trie>>, words: Vec<String>) {
        let mut guard = lock.write().await;

        *guard = Some(Trie::new());

        if let Some(ref mut trie) = *guard {
            for word in &words {
                trie.insert(word);
            }
        }
    }

    pub async fn search_genres(&self, genre: &str) -> Option<Vec<String>> {
        Self::search_option(&self.genres, genre).await
    }

    pub async fn search_tags(&self, tag: &str) -> Option<Vec<String>> {
        Self::search_option(&self.tags, tag).await
    }

    pub async fn insert_genres(&self, genres: Vec<String>) {
        Self::insert_option(&self.genres, genres).await;
    }

    pub async fn insert_tags(&self, tags: Vec<String>) {
        Self::insert_option(&self.tags, tags).await;
    }
}
