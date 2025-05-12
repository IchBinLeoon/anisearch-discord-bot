# 🔍 AniSearch

[![Discord](https://img.shields.io/discord/835960108466176041?logo=discord&logoColor=ffffff)](https://discord.gg/Bv94yQYZM8)
[![Version](https://img.shields.io/github/v/tag/IchBinLeoon/anisearch-discord-bot?label=version)](https://github.com/IchBinLeoon/anisearch-discord-bot/tags)
[![Issues](https://img.shields.io/github/issues/IchBinLeoon/anisearch-discord-bot)](https://github.com/IchBinLeoon/anisearch-discord-bot/issues)
[![Pulls](https://img.shields.io/github/issues-pr/IchBinLeoon/anisearch-discord-bot)](https://github.com/IchBinLeoon/anisearch-discord-bot/pulls)
[![License](https://img.shields.io/github/license/IchBinLeoon/anisearch-discord-bot)](https://github.com/IchBinLeoon/anisearch-discord-bot/blob/main/LICENSE)

The source code of the AniSearch Bot.

# 🤝 Contribute
You have an idea or found a bug? Open [a new issue](https://github.com/IchBinLeoon/anisearch-discord-bot/issues) with detailed explanation.

You want to write code and add new things or fix a bug? Just fork, clone to your computer, and when you're done, open a pull request!

You can also join the [support server](https://discord.gg/Bv94yQYZM8) to ask your questions or get support!

# 🚀 Running
**I would prefer if you don't run an instance of my bot unless you want to contribute to the code.**

Use the official instance instead, which you can add to your server [here](https://discord.com/api/oauth2/authorize?client_id=737236600878137363&permissions=18432&scope=bot%20applications.commands)!

Nevertheless, the installation steps are as follows:

1. Make sure `Docker` and `Docker Compose` are installed.

2. Clone the repository and change the working directory.
    ```
    git clone https://github.com/IchBinLeoon/anisearch-discord-bot
    cd anisearch-discord-bot
    ```

3. Create a [Discord Application](https://discord.com/developers/applications).

4. Rename `.env.example` to `.env` and fill in `BOT_TOKEN`.

5. Build the images and run the bot along with the database.
    ```
    docker-compose up -d
    ```

# ⚖️ License
This project is licensed under the GNU General Public License v3.0 (GPL-v3.0). See the [LICENSE](https://github.com/IchBinLeoon/anisearch-discord-bot/blob/main/LICENSE) file for more details.
