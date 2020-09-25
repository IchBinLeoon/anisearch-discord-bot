# AniSearch

[![Version](https://img.shields.io/badge/Version-1.5-red?logo=github&style=flat-square)](https://github.com/IchBinLeoon/anisearch-discord-bot)
[![Library](https://img.shields.io/badge/Library-discord.py-3775A9?logo=pypi&style=flat-square)](https://github.com/Rapptz/discord.py)
[![Python](https://img.shields.io/badge/Python-3.8.5-3776AB?logo=python&style=flat-square)](https://www.python.org/)
[![Invite](https://img.shields.io/badge/Invite-Link-7289DA?logo=discord&style=flat-square)](https://discord.com/oauth2/authorize?client_id=737236600878137363&permissions=83968&scope=bot)

## General
This easy-to-use bot allows you to search for Anime, Manga, Characters, Staff, Studios and Profiles right within Discord and get results from AniList and MyAnimeList!

If you are interested in my bot, you can add it to your Discord server by clicking [here](https://discord.com/api/oauth2/authorize?client_id=737236600878137363&permissions=83968&scope=bot)!

If you would like to contact me, use the `contact <message>` command or add me as a friend via Discord: `IchBinLeoon#9999`

## Commands

**Parameters:** `<> - required | [] - optional`   

Do ***not*** include `<>` or `[]` when executing the command.  

**Command Flags:**  
`--search:` Displays all search results.    
`--characters:` Displays the characters in the media.   
`--staff:` Displays the staff who produced the media.   
`--image:` Displays the cover images of the media.   
`--relations:` Displays other media in the same or connecting franchise.   
`--links:` Displays external links to another sites related to the media.    
`--streams:` Displays links to legal streaming episodes on external sites.    
`--all:` Displays the first search results including all command flags. 

### Search
* anime
  * Usage: `anime <title>`
  * Description: Searches for an anime with the given title and displays information about the first result such as type, status, episodes, dates, description, and more!
  * Flags: You can include one of these command flags at the end for more or specific information. Available flags: `--search, --characters, --staff, --image, --relations, --links, --streams, --all`
  * Cooldown: `3s`
  * Aliases: `a`
* manga
  * Usage: `manga <title>`
  * Description: Searches for a manga with the given title and displays information about the first result such as type, status, chapters, dates, description, and more!
  * Flags: You can include one of these command flags at the end for more or specific information. Available flags: `--search, --characters, --staff, --image, --relations, --all`
  * Cooldown: `3s`
  * Aliases: `m`
* character
  * Usage: `character <name>`
  * Description: Searches for a character with the given name and displays information about the first result such as description, synonyms, and appearances!
  * Flags: You can include one of these command flags at the end for more or specific information. Available flags: `--search, --image`
  * Cooldown: `3s`
  * Aliases: `c, char`
* staff
  * Usage: `staff <name>`
  * Description: Searches for a staff with the given name and displays information about the first result such as description, staff roles, and character roles!
  * Flags: You can include one of these command flags at the end for more or specific information. Available flags: `--search, --image`
  * Cooldown: `3s`
  * Aliases: -
* studio
  * Usage: `studio <name>`
  * Description: Searches for a studio with the given name and displays information about the first result such as the studio productions!
  * Flags: You can include one of these command flags at the end for more or specific information. Available flags: `--search`
  * Cooldown: `3s`
  * Aliases: -
* random
  * Usage: `random <anime/manga> <genre>`
  * Description: Displays information about a random anime or manga of the specified genre.
  * Cooldown: `7s`
  * Aliases: `r, rndm`
 
### Profile
* anilist
  * Usage: `anilist [username/@member]`
  * Description: Displays information about the given AniList Profile such as anime stats, manga stats and favorites.
  * Cooldown: `5s`
  * Aliases: `al`
* myanimelist
  * Usage: `myanimelist [username/@member]`
  * Description: Displays information about the given MyAnimeList Profile such as anime stats, manga stats and favorites.
  * Cooldown: `5s`
  * Aliases: `mal`
* link
  * Usage: `link <anilist/myanimelist> <username>`
  * Description: Links an AniList or MyAnimeList Profile.
  * Cooldown: `5s`
  * Aliases: `l`
* removelinks
  * Usage: `removelinks`
  * Description: Removes the linked AniList and MyAnimeList Profile.
  * Cooldown: `10s`
  * Aliases: `rml, rmlinks`
  
### Info
* help
  * Usage: `help [command]`
  * Description: Shows help or displays information about a command.
  * Cooldown: `3s`
  * Aliases: `h`
* commands
  * Usage: `commands`
  * Description: Displays all commands.
  * Cooldown: `3s`
  * Aliases: `cmds`
* about
  * Usage: `about`
  * Description: Displays information and stats about the bot.
  * Cooldown: `3s`
  * Aliases: -
* contact
  * Usage: `contact <message>`
  * Description: Contacts the creator of the bot.
  * Cooldown: `3s`
  * Aliases: -
* ping
  * Usage: `ping`
  * Description: Checks the latency of the bot.
  * Cooldown: `3s`
  * Aliases: -
  
### Server Administrator
* prefix
  * Usage: `prefix <prefix>`
  * Description: Changes the current server prefix.
  * Cooldown: `10s`
  * Aliases: -  
  
## Discord Bot List
[![Discord Bots](https://top.gg/api/widget/737236600878137363.svg)](https://top.gg/bot/737236600878137363)

## Libraries and API's
Thanks to the people who made this discord bot possible.

#### [Rapptz/discord.py](https://github.com/Rapptz/discord.py)
#### [AniList/ApiV2-GraphQL-Docs](https://github.com/AniList/ApiV2-GraphQL-Docs)
#### [aio-libs/aiohttp](https://github.com/aio-libs/aiohttp)
#### [psf/requests](https://github.com/psf/requests)
#### [psycopg/psycopg2](https://github.com/psycopg/psycopg2)
#### [Jikan API](https://jikan.moe/)