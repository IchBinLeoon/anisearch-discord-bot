#[macro_export]
macro_rules! anilist_url {
    ($kind:expr, $id:expr) => {
        format!("{}/{}/{}", ANILIST_BASE_URL, $kind, $id)
    };
}

#[macro_export]
macro_rules! anilist_media_url {
    ($type_:path, $media_type:expr, $id:expr) => {
        match $media_type {
            Some(<$type_>::ANIME) => $crate::anilist_anime_url!($id),
            Some(<$type_>::MANGA) => $crate::anilist_manga_url!($id),
            _ => unreachable!(),
        }
    };
}

#[macro_export]
macro_rules! anilist_anime_url {
    ($id:expr) => {
        $crate::anilist_url!("anime", $id)
    };
}

#[macro_export]
macro_rules! anilist_manga_url {
    ($id:expr) => {
        $crate::anilist_url!("manga", $id)
    };
}

#[macro_export]
macro_rules! anilist_character_url {
    ($id:expr) => {
        $crate::anilist_url!("character", $id)
    };
}

#[macro_export]
macro_rules! anilist_staff_url {
    ($id:expr) => {
        $crate::anilist_url!("staff", $id)
    };
}

#[macro_export]
macro_rules! anilist_studio_url {
    ($id:expr) => {
        $crate::anilist_url!("studio", $id)
    };
}

#[macro_export]
macro_rules! myanimelist_url {
    ($kind:expr, $id:expr) => {
        format!("{}/{}/{}", MYANIMELIST_BASE_URL, $kind, $id)
    };
}

#[macro_export]
macro_rules! myanimelist_media_url {
    ($type_:path, $media_type:expr, $id:expr) => {
        match $media_type {
            Some(<$type_>::ANIME) => $crate::myanimelist_anime_url!($id),
            Some(<$type_>::MANGA) => $crate::myanimelist_manga_url!($id),
            _ => unreachable!(),
        }
    };
}

#[macro_export]
macro_rules! myanimelist_anime_url {
    ($id:expr) => {
        $crate::myanimelist_url!("anime", $id)
    };
}

#[macro_export]
macro_rules! myanimelist_manga_url {
    ($id:expr) => {
        $crate::myanimelist_url!("manga", $id)
    };
}
