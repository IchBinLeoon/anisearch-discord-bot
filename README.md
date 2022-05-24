# 🔍 AniSearch

[![Status](https://top.gg/api/widget/status/737236600878137363.svg)](https://top.gg/bot/737236600878137363)
[![Discord](https://img.shields.io/discord/835960108466176041?label=&logo=discord&logoColor=ffffff&color=7289DA&labelColor=7289DA&style=flat-square)](https://discord.gg/Bv94yQYZM8)
[![Commit](https://img.shields.io/github/last-commit/IchBinLeoon/anisearch-discord-bot?style=flat-square)](https://github.com/IchBinLeoon/anisearch-discord-bot/commits/main)
[![Size](https://img.shields.io/github/repo-size/IchBinLeoon/anisearch-discord-bot?style=flat-square)](https://github.com/IchBinLeoon/anisearch-discord-bot)
[![License](https://img.shields.io/github/license/IchBinLeoon/anisearch-discord-bot?style=flat-square)](https://github.com/IchBinLeoon/anisearch-discord-bot/blob/main/LICENSE)

The source code of the AniSearch Discord Bot.

[![Discord Bots](https://top.gg/api/widget/737236600878137363.svg)](https://top.gg/bot/737236600878137363)

# 🤝 Contribute
You have an idea or found a bug? Open [a new issue](https://github.com/IchBinLeoon/anisearch-discord-bot/issues) with detailed explanation.

You want to write code and add new things or fix a bug? Just fork, clone to your computer, and when you're done, open a pull request!

You can also join the [support server](https://discord.gg/Bv94yQYZM8) to ask your questions or get support!

# 🛠️ Structure
| Codebase             | Description                 |
| -------------------- | --------------------------- |
| [bot](bot)           | Discord Bot                 |
| [web](web)           | Admin Panel                 |
| [notifier](notifier) | Notification Service        |
| [gh-pages](gh-pages) | GitHub Pages Website        |

# 🚀 Running
**I would prefer if you don't run an instance of my bot unless you want to contribute to the code.** 

Use the official instance instead, which you can add to your server [here](https://discord.com/api/oauth2/authorize?client_id=737236600878137363&permissions=92224&scope=bot%20applications.commands)!

Nevertheless, the installation steps are as follows:  

1. Make sure `Docker` and `Docker-Compose` are installed.

2. Clone the repository.
    ```
    $ git clone https://github.com/IchBinLeoon/anisearch-discord-bot
    ```
    
3. Change the working directory.
    ```
    $ cd anisearch-discord-bot
    ```
    
4. Create a [Discord Application](https://discord.com/developers/applications).

5. Rename `.env.example` to `.env`.

6. Edit `.env` and fill in `BOT_TOKEN`, `BOT_OWNER_ID` and `BOT_SAUCENAO_API_KEY`.
    ```
    # The token the bot will use for auth with Discord.
    BOT_TOKEN=
    
    # The Discord ID of the user hosting the bot.
    BOT_OWNER_ID=
    
    # The SauceNAO API key. Is required for the `source` command.
    BOT_SAUCENAO_API_KEY=
    ```

7. Build the images and run the discord bot, episode notification service, admin panel and postgresql database.
    ```
    $ docker-compose up --build -d
    ```
    
# ⚖️ License
This project is licensed under the GNU General Public License v3.0 (GPL-v3.0). See the [LICENSE](https://github.com/IchBinLeoon/anisearch-discord-bot/blob/main/LICENSE) file for more details.
