<img align="right" hight="150px" width="150px" src="assets/anisearch-logo.png">

## AniSearch v1.5.2
Searches and displays information about Anime, Manga, Characters, Staff, Studios and  
Profiles from AniList and MyAnimeList!

[![Discord Bots](https://top.gg/api/widget/status/737236600878137363.svg)](https://top.gg/bot/737236600878137363)
[![GitHub Workflow Status](https://img.shields.io/github/workflow/status/IchBinLeoon/anisearch-discord-bot/CodeQL)](https://github.com/IchBinLeoon/anisearch-discord-bot/actions)
[![CodeFactor](https://www.codefactor.io/repository/github/ichbinleoon/anisearch-discord-bot/badge)](https://www.codefactor.io/repository/github/ichbinleoon/anisearch-discord-bot)
[![Issues](https://img.shields.io/github/issues/IchBinLeoon/anisearch-discord-bot)](https://github.com/IchBinLeoon/anisearch-discord-bot/issues)
[![Pulls](https://img.shields.io/github/issues-pr/IchBinLeoon/anisearch-discord-bot)](https://github.com/IchBinLeoon/anisearch-discord-bot/issues)
[![Python](https://img.shields.io/badge/python-3.8.6-blue)](https://www.python.org/)

---

# General
This is the GitHub Repository for the [AniSearch Discord Bot](https://top.gg/bot/737236600878137363). AniSearch is an easy-to-use Discord bot written in Python that allows you to search for Anime, Manga, Characters, Staff, Studios and Profiles right within [Discord](https://discord.com/) and displays the results from [AniList](https://anilist.co) and [MyAnimeList](https://myanimelist.net/)!

If you are interested in my bot, you can add it to your Discord server by clicking [here](https://discord.com/api/oauth2/authorize?client_id=737236600878137363&permissions=83968&scope=bot)!

If you would like to contact me, add me as a friend via Discord: `IchBinLeoon#9999`

[![Discord Bots](https://top.gg/api/widget/737236600878137363.svg)](https://top.gg/bot/737236600878137363)

If the bot is offline, it will most likely be updated. If the bot is offline for an extended period of time, my home network has likely broken down or something else bad has happened. In this case it would be very useful if someone notifies me.

# Bot Commands
A full documentation of AniSearch's commands can be found [here](https://top.gg/bot/737236600878137363) or with the command `as!help` if you have invited the bot to your server.

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

# Contribute
You have an idea or found a bug? Create [a new issue](https://github.com/IchBinLeoon/anisearch-discord-bot/issues) with detailed explanation.

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
