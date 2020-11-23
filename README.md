<p align="center">
  <br>
    <img src="assets/anisearch-banner.png" alt="AniSearch Banner Image">
  <br>
</p>
  
<h5 align="center">Searches and displays information about Anime, Manga, Characters, Staff, Studios and Profiles from AniList, MyAnimeList and Kitsu!</h5>
  
<p align="center">
  <a href="https://top.gg/bot/737236600878137363">
    <img src="https://top.gg/api/widget/status/737236600878137363.svg" alt="Discord Bots">
  </a>
  <a href="https://www.python.org/">
    <img src="https://img.shields.io/badge/python-3.8.6-blue" alt="Python">
  </a>
  <a href="https://github.com/IchBinLeoon/anisearch-discord-bot/actions">
    <img src="https://img.shields.io/github/workflow/status/IchBinLeoon/anisearch-discord-bot/CodeQL" alt="GitHub Workflow Status">
  </a>
  <a href="https://www.codefactor.io/repository/github/ichbinleoon/anisearch-discord-bot">
    <img src="https://www.codefactor.io/repository/github/ichbinleoon/anisearch-discord-bot/badge" alt="CodeFactor">
  </a>
  <a href="https://github.com/IchBinLeoon/anisearch-discord-bot/issues">
    <img src="https://img.shields.io/github/issues/IchBinLeoon/anisearch-discord-bot" alt="Issues">
  </a>
  <a href="https://github.com/IchBinLeoon/anisearch-discord-bot/issues">
    <img src="https://img.shields.io/github/issues-pr/IchBinLeoon/anisearch-discord-bot" alt="Pulls">
  </a>
  <a href="https://github.com/IchBinLeoon/anisearch-discord-bot/blob/master/LICENSE">
    <img src="https://img.shields.io/github/license/IchBinLeoon/anisearch-discord-bot" alt="Python">
  </a>
</p>

<p align="center">
  <a href="#AniSearch-v1.6">AniSearch</a>
  •
  <a href="#Features">Features</a>
  •
  <a href="#Contribute">Contribute</a>
  •
  <a href="#Running-AniSearch">Running AniSearch</a>
  •
  <a href="#Libraries-and-APIs">Libraries and API's</a>
  •
  <a href="#License">License</a>
</p>


# AniSearch v1.6
This is the GitHub Repository for the [AniSearch Discord Bot](https://top.gg/bot/737236600878137363). AniSearch is an easy-to-use Discord bot written in Python that allows you to search for Anime, Manga, Characters, Staff, Studios and Profiles right within Discord and displays results from [AniList](https://anilist.co), [MyAnimeList](https://myanimelist.net/) and [Kitsu](https://kitsu.io/)!

If you are interested in my bot, you can add it to your Discord server by clicking [here](https://discord.com/oauth2/authorize?client_id=737236600878137363&permissions=124992&scope=bot)!

If you would like to contact me, add me as a friend via Discord: `IchBinLeoon#9999`

[![Discord Bots](https://top.gg/api/widget/737236600878137363.svg)](https://top.gg/bot/737236600878137363)


# Features
## Commands
**AniSearch's Command Prefix:** `as! | @AniSearch | Customizable`

**Parameters:** `<> - required, [] - optional, | - either/or`

Do __not__ include `<>`, `[]` or `|` when executing the command.

### Search
`anime <title>:` Searches for an anime with the given title and displays information about the search results such as type, status, episodes, description, and more!  

`manga <title>:` Searches for a manga with the given title and displays information about the search results such as type, status, chapters, description, and more!  

`character <name>:` Searches for a character with the given name and displays information about the search results such as description, synonyms, and appearances!  

`staff <name>:` Searches for a staff with the given name and displays information about the search results such as description, staff roles, and character roles!  

`studio <name>:` Searches for a studio with the given name and displays information about the search results such as the studio productions!

`random <anime|manga> <genre>:` Displays a random anime or manga of the specified genre.  

### Profile
`anilist <username>:` Displays information about the given AniList Profile such as anime stats, manga stats and favorites.  

`myanimelist <username>:` Displays information about the given MyAnimeList Profile such as anime stats, manga stats and favorites.  

`kitsu <username>:` Displays information about the given Kitsu Profile such as anime stats and manga stats!  

`setprofile <al|mal|kitsu> <username>:` Sets an AniList, MyAnimeList or Kitsu Profile.  

`remove:` Removes the set AniList, MyAnimeList and Kitsu Profile.  

### Image
`trace <image-url|with image as attachment>:` Tries to find the anime the image is from through the image url or the image as attachment.  

`source <image-url|with image as attachment>:` Tries to find the source of an image through the image url or the image as attachment.  

### Info
`help [command]:` Shows help or displays information about a command.  

`commands:` Displays all commands.  

`about:` Displays information about the bot.  

`stats:` Displays statistics about the bot.  

### Settings
Server Administrator Permissions Required

`prefix <prefix>:` Changes the current server prefix.  

## Examples

<details close>
<summary>Anime</summary>
<br>
<img src="assets/anime-example.gif" width="70%">
</details>

<details close>
<summary>Manga</summary>
<br>
<img src="assets/manga-example.gif" width="70%">
</details>

# Contribute
You have an idea or found a bug? Create [a new issue](https://github.com/IchBinLeoon/anisearch-discord-bot/issues) with detailed explanation.


# Running AniSearch
Self-hosting isn't fully supported. I would prefer if you don't run an instance of my bot and recommend everyone to use the official instance instead.  

Nevertheless, the installation steps are as follows:  

## 1. Setup Database
To be able to use the bot you need to set up a `PostgreSQL Database`.

Make sure the tables are set up correctly as shown below to successfully connect to your PostgreSQL Database.

### Database Table Structure

guilds

| id | prefix |
|--------------|--------------|
| bigint | character varying (255) |

users

| id | anilist | myanimelist | kitsu |
|--------------|--------------|--------------|--------------|
| bigint | character varying (255) | character varying (255) | character varying (255) |

### Query Tool

```sql
CREATE TABLE guilds (
    id bigint,
    prefix VARCHAR (255)
)

CREATE TABLE users (
    id bigint,
    anilist VARCHAR (255),
    myanimelist VARCHAR (255),
    kitsu VARCHAR (255)
)
```

## 2. Setup Bot
1. Clone the Repository.    

    ```
    git clone https://github.com/IchBinLeoon/anisearch-discord-bot
    ```

2. Create a [Discord Application](https://discord.com/developers/applications).

3. Edit `config.example.py`.   

    ```py
    # The token the bot will use for auth with Discord.
    TOKEN = 'my cool bot token'

    # The Discord ID of the user hosting the bot.
    OWNER_ID = 'my discord id'

    # The Postgres database credentials.
    DB_HOST = 'hostname'
    DB_NAME = 'database'
    DB_USER = 'username'
    BD_PASSWORD = 'password'
    ```

4. Rename `config.example.py` to `config.py`.

## 3. Run
### Docker
1. Make sure `Docker` and `Docker-Compose` are installed.

2. Build the image and run the bot.

    ```
    docker-compose up
    ```

### Manual
1. Make sure you have `Python 3.8.6` or higher.

2. Install the requirements.

    ```
    pip3 install -r requirements.txt
    ```

3. Run AniSearch.

    ```
    python3 -m anisearch
    ```


# Libraries and API's
Thanks to the people who made this discord bot possible.  
#### [Rapptz/discord.py](https://github.com/Rapptz/discord.py)  
#### [AniList/ApiV2-GraphQL-Docs](https://github.com/AniList/ApiV2-GraphQL-Docs)  
#### [abhinavk99/jikanpy](https://github.com/abhinavk99/jikanpy)  
#### [Kitsu API](https://kitsu.docs.apiary.io/#)  
#### [soruly/trace.moe](https://github.com/soruly/trace.moe)  
#### [SauceNAO](https://saucenao.com)  
#### [aio-libs/aiohttp](https://github.com/aio-libs/aiohttp)  
#### [psf/requests](https://github.com/psf/requests)  
#### [psycopg/psycopg2](https://github.com/psycopg/psycopg2)  


# License
This project is licensed under the GNU General Public License v3.0 (GPL-3.0). See the [LICENSE](https://github.com/IchBinLeoon/anisearch-discord-bot/blob/master/LICENSE) file for more details.
