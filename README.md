<p align="center">
  <br>
    <img src="assets/anisearch-banner.png" alt="AniSearch Banner Image">
  <br>
</p>
  
<h5 align="center">Retrieves and displays information about anime, manga, characters, staff, studios and much more!</h5>
  
<p align="center">
  <a href="https://top.gg/bot/737236600878137363">
    <img src="https://top.gg/api/widget/status/737236600878137363.svg" alt="Status">
  </a>
  <a href="https://discord.gg/Bv94yQYZM8">
    <img src="https://img.shields.io/discord/835960108466176041?label=&logo=discord&logoColor=ffffff&color=7289DA&labelColor=7289DA&style=flat-square" alt="Discord">
  </a>
  <a href="https://www.python.org/">
    <img src="https://img.shields.io/badge/python->=&nbsp;3.8-blue?style=flat-square" alt="Python">
  </a>
  <a href="https://github.com/IchBinLeoon/anisearch-discord-bot/blob/main/LICENSE">
    <img src="https://img.shields.io/github/license/IchBinLeoon/anisearch-discord-bot?style=flat-square" alt="License">
  </a>
  <a href="https://www.codefactor.io/repository/github/ichbinleoon/anisearch-discord-bot">
    <img src="https://www.codefactor.io/repository/github/ichbinleoon/anisearch-discord-bot/badge?style=flat-square" alt="CodeFactor">
  </a>
  <a href="https://github.com/IchBinLeoon/anisearch-discord-bot">
    <img src="https://img.shields.io/github/repo-size/IchBinLeoon/anisearch-discord-bot?style=flat-square" alt="Size">
  </a>
</p>

<p align="center">
  <a href="https://github.com/IchBinLeoon/anisearch-discord-bot/commits/main">
    <img src="https://img.shields.io/github/last-commit/IchBinLeoon/anisearch-discord-bot?style=flat-square" alt="Commit">
  </a>
  <a href="https://github.com/IchBinLeoon/anisearch-discord-bot/actions">
    <img src="https://img.shields.io/github/workflow/status/IchBinLeoon/anisearch-discord-bot/CodeQL?label=CodeQL&style=flat-square" alt="CodeQL">
  </a>
  <a href="https://github.com/IchBinLeoon/anisearch-discord-bot/pulls">
    <img src="https://img.shields.io/github/issues-pr/IchBinLeoon/anisearch-discord-bot?style=flat-square" alt="Pulls">
  </a>
  <a href="https://github.com/IchBinLeoon/anisearch-discord-bot/issues">
    <img src="https://img.shields.io/github/issues/IchBinLeoon/anisearch-discord-bot?style=flat-square" alt="Issues">
  </a>
</p>

<p align="center">
  <a href="#-AniSearch-v16">AniSearch 🔍</a>
  •
  <a href="#-Commands">Commands ✨</a>
  •
  <a href="#-Contribute">Contribute 🤝</a>
  •
  <a href="#-Running-AniSearch">Running AniSearch 🚀</a>
  •
  <a href="#-Libraries-and-APIs">Libraries and API's 📚</a>
  •
  <a href="#-License">License 📝</a>
</p>


# 🔍 AniSearch
**AniSearch** is an easy-to-use Discord bot written in Python that allows you to search for anime, manga, characters, staff, studios and much more directly in Discord and displays the results as paginated embeds! 

You can also:
- Search for a random anime or manga of a specific genre.
- View the opening and ending themes of an anime.
- View another user's profile with anime and manga stats from [AniList](https://anilist.co), [MyAnimeList](https://myanimelist.net) or [Kitsu](https://kitsu.io).
- Search for the anime or the source of an image.
- View the next airing, and the most recently aired anime episodes.
- View the latest anime related news from [Anime News Network](https://www.animenewsnetwork.com) and [Crunchyroll](https://www.crunchyroll.com) or the current trending anime or manga on AniList.

If you are interested in my bot, you can add it to your Discord server by clicking [here](https://discord.com/oauth2/authorize?client_id=737236600878137363&permissions=124992&scope=bot)!

<br>

[![Discord Bots](https://top.gg/api/widget/737236600878137363.svg)](https://top.gg/bot/737236600878137363)


# ✨ Commands
**AniSearch's Command Prefix:** `as! | @AniSearch | Customizable`

**Parameters:** `<> - required, [] - optional, | - either/or`

Do __not__ include `<>`, `[]` or `|` when executing the command.

### Search
- `anime <title>:` Searches for an anime with the given title and displays information about the search results such as type, status, episodes, description, and more!  
   <details close>
   <summary>Anime Example</summary>
   <br>
   <img src="assets/examples/anime-example.png">
   </details>

- `manga <title>:` Searches for a manga with the given title and displays information about the search results such as type, status, chapters, description, and more!  
   <details close>
   <summary>Manga Example</summary>
   <br>
   <img src="assets/examples/manga-example.png">
   </details>

- `character <name>:` Searches for a character with the given name and displays information about the search results such as description, synonyms, and appearances!  
   <details close>
   <summary>Character Example</summary>
   <br>
   <img src="assets/examples/character-example.png">
   </details>

- `staff <name>:` Searches for a staff with the given name and displays information about the search results such as description, staff roles, and character roles!  
   <details close>
   <summary>Staff Example</summary>
   <br>
   <img src="assets/examples/staff-example.png">
   </details>

- `studio <name>:` Searches for a studio with the given name and displays information about the search results such as the studio productions!  
   <details close>
   <summary>Studio Example</summary>
   <br>
   <img src="assets/examples/studio-example.png">
   </details>

- `random <anime|manga> <genre>:` Displays a random anime or manga of the specified genre.  

### Profile
- `anilist [username|@member]:` Displays information about the given AniList profile such as anime stats, manga stats and favorites.  

- `myanimelist [username|@member]:` Displays information about the given MyAnimeList profile such as anime stats, manga stats and favorites.  

- `kitsu [username|@member]:` Displays information about the given Kitsu profile such as anime stats, manga stats and favorites!  

- `setprofile <al|mal|kitsu> <username>:` Sets an AniList, MyAnimeList or Kitsu profile.  

- `profiles [@member]:` Displays the set profiles of you, or the specified user.  

- `removeprofiles:` Removes the set AniList, MyAnimeList and Kitsu profile.  

### Themes
- `themes <anime>:` Searches for the openings and endings of the given anime and displays them.  

- `theme <OP|ED> <anime>:` Displays a specific opening or ending of the given anime.  

### Image
- `trace <image-url|with image as attachment>:` Tries to find the anime the image is from through the image url or the image as attachment.  

- `source <image-url|with image as attachment>:` Tries to find the source of an image through the image url or the image as attachment.  

- `waifu:` Posts a random image of a waifu.  

- `neko:` Posts a random image of a catgirl.  

### Schedule
- `next:` Displays the next airing anime episodes.  

- `last:` Displays the most recently aired anime episodes.  

### News
- `aninews:` Displays the latest anime news from Anime News Network.  

- `crunchynews:` Displays the latest anime news from Crunchyroll.  

- `trending <anime|manga>:` Displays the current trending anime or manga on AniList.  

### Help
- `help [command]:` Shows help or displays information about a command.  

- `commands:` Displays all commands.  

- `about:` Displays information about the bot.  

- `stats:` Displays statistics about the bot.  

- `github:` Displays information about the GitHub repository.  

### Settings
Can only be used by a server administrator.

- `setprefix <prefix>:` Changes the current server prefix. Max 5 characters.  

### Admin
Can only be used by the bot owner.  

- `status:` Displays the current status of the bot.  

- `load <cog>:` Loads a cog.  

- `unload <cog>:` Unloads a cog.  

- `reload <cog>:` Reloads a cog.  

- `reloadall:` Reloads all cogs.  

- `sysinfo:` Displays basic information about the system on which the bot is currently running.  


# 🤝 Contribute
You have an idea or found a bug? Open [a new issue](https://github.com/IchBinLeoon/anisearch-discord-bot/issues) with detailed explanation.

You want to write code and add new things or fix a bug? 
First, please open [a new issue](https://github.com/IchBinLeoon/anisearch-discord-bot/issues) so we can discuss the changes you want to make. 
After that, it's just fork, clone to your computer, and when you're done, open a pull request! 
Most of the code should be commented, and once you're in, you should understand how everything works. 
For info, the bot still contains a lot of code from a very early version that can be rewritten.

You can also join the [support server](https://discord.gg/Bv94yQYZM8) to ask your questions or get support!

# 🚀 Running AniSearch
**Self-hosting isn't fully supported and I don't recommend you to self-host the bot unless you want to contribute to the code.**  

That's why I would prefer if you don't run an instance of my bot and recommend everyone to use the official instance instead, which you can add it to your Discord server [here](https://discord.com/oauth2/authorize?client_id=737236600878137363&permissions=124992&scope=bot)!  

Nevertheless, the installation steps are as follows:  

## Introduction
The bot and the associated admin panel can be run either as a Docker containers or manually. The admin panel can be accessed via port 5000 by default.

### Requirements:
- Either [Docker and Docker-Compose](https://www.docker.com/) or [Python](https://www.python.org/) 3.8+, [Go](https://golang.org/) 1.16+ and a [PostgreSQL](https://www.postgresql.org/) Database

## 1. ⚙️ Set up the Bot

1. Clone the repository.    

    ```
    $ git clone https://github.com/IchBinLeoon/anisearch-discord-bot
    ```
   
2. Change the working directory.

    ```
    $ cd anisearch-discord-bot
    ```

3. Create a [Discord Application](https://discord.com/developers/applications).

4. Rename `.env.example` to `.env`.  

5. Edit `.env` and fill in `BOT_TOKEN`, `BOT_OWNER_ID` and `BOT_SAUCENAO_API_KEY`.

    ```
    # The token the bot will use for auth with Discord.
    BOT_TOKEN=
    
    # The Discord ID of the user hosting the bot.
    BOT_OWNER_ID=
    
    # The SauceNAO API key. Is required for the `source` command.
    BOT_SAUCENAO_API_KEY=
    ```

## 2. Run

## 🐳 Docker
1. Make sure `Docker` and `Docker-Compose` are installed.

2. Build the images and run the bot, admin panel and database.

    ```
    $ docker-compose up --build
    ```
   
## 🔧 Manually
1. To be able to use the bot you need to set up a `PostgreSQL Database`. Make sure the tables are set up correctly as shown below to successfully connect to your database. Type the following in your `PSQL Tool`:

    ```sql
    CREATE TABLE IF NOT EXISTS guilds (id bigint, prefix VARCHAR (5));
    CREATE TABLE IF NOT EXISTS users (id bigint, anilist VARCHAR (255), myanimelist VARCHAR (255), kitsu VARCHAR (255));
    ```

2. Edit `.env` and change `BOT_API_HOST` and `WEB_HOST` to localhost or to the IP address of the device the bot and admin panel are running on. Also change the credentials for the Postgres database to match yours.

3. ### Bot
    - Make sure you have `Python 3.8` or higher.

    - Change the working directory.

        ```
        $ cd bot
        ```   

    - Set up and activate a venv.

        ```
        $ python3 -m venv venv
        $ source venv/bin/activate # On macOS and Linux
        $ .\venv\Scripts\activate # On Windows
        ```

    - Install the requirements.

        ```
        $ python -m pip install -r requirements.txt
        ```

    - Run the bot.

        ```
        $ python -m anisearch
        ```

4. ### Admin Panel
    - Make sure you have `Go 1.16` or higher.

    - Change the working directory.

        ```
        $ cd web
        ```

    - Build the executable.

        ```
        $ go build .
        ```

    - Run the admin panel.

        ```
        $ ./web # On macOS and Linux
        $ web.exe # On Windows
        ```


# 📚 Libraries and API's
Thanks to the people who made this discord bot possible.
#### [Rapptz/discord.py](https://github.com/Rapptz/discord.py)
#### [Rapptz/discord-ext-menus](https://github.com/Rapptz/discord-ext-menus)
#### [aio-libs/aiohttp](https://github.com/aio-libs/aiohttp)
#### [psycopg/psycopg2](https://github.com/psycopg/psycopg2)
#### [beautifulsoup4](https://www.crummy.com/software/BeautifulSoup/)
#### [top-gg/python-sdk ](https://github.com/top-gg/python-sdk)
#### [theskumar/python-dotenv](https://github.com/theskumar/python-dotenv)
#### [giampaolo/psutil](https://github.com/giampaolo/psutil)
#### [IchBinLeoon/waifu-py](https://github.com/IchBinLeoon/waifu-py)
#### [gin-gonic/gin](https://github.com/gin-gonic/gin)
#### [joho/godotenv](https://github.com/joho/godotenv)
#### [go-gorm/gorm](https://github.com/go-gorm/gorm)
#### [go-gorm/postgres](https://github.com/go-gorm/postgres)
#### [AniList/ApiV2-GraphQL-Docs](https://github.com/AniList/ApiV2-GraphQL-Docs)
#### [jikan-me/jikan](https://github.com/jikan-me/jikan)
#### [hummingbird-me/api-docs](https://github.com/hummingbird-me/api-docs)
#### [Waifu-pics/waifu-api](https://github.com/Waifu-pics/waifu-api)
#### [AnimeThemes/animethemes-server](https://github.com/AnimeThemes/animethemes-server)
#### [soruly/trace.moe](https://github.com/soruly/trace.moe)
#### [SauceNAO](https://saucenao.com/)
#### [AnimeNewsNetwork](https://www.animenewsnetwork.com/)
#### [Crunchyroll](https://www.crunchyroll.com/)


# 📝 License
This project is licensed under the GNU General Public License v3.0 (GPL-v3.0). See the [LICENSE](https://github.com/IchBinLeoon/anisearch-discord-bot/blob/main/LICENSE) file for more details.
