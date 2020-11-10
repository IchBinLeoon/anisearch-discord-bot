from anisearch import config
from anisearch.bot import AniSearchBot


def main():
    bot = AniSearchBot()
    bot.run(config.TOKEN)


if __name__ == '__main__':
    main()
