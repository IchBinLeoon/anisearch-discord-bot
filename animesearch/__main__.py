import sys

import psycopg2

from animesearch import config
from animesearch.bot import AnimeSearchBot
from animesearch.utils.logger import logger


def main():
    logger.info('Starting AnimeSearch')
    try:
        checks()
        start_bot()
    except Exception as exception:
        logger.exception(exception)
        sys.exit()


def checks():
    logger.info('Checking Database')
    try:
        db = psycopg2.connect(host=config.DB_HOST, dbname=config.DB_NAME, user=config.DB_USER,
                              password=config.BD_PASSWORD)
        logger.info('Database connection is working properly')
    except Exception as exception:
        logger.exception(exception)
        logger.info('Cannot connect to Database')
        sys.exit()
    logger.info('Checking Tables')
    cur = db.cursor()
    cur.execute('SELECT EXISTS(SELECT * FROM information_schema.tables WHERE TABLE_NAME = %s)', ('guilds',))
    guilds_table = cur.fetchone()[0]
    if guilds_table:
        logger.info('Guilds Table exist')
    else:
        logger.info("Guilds Table doesn't exist")
        logger.info('Creating Guilds Table')
        cur.execute('CREATE TABLE guilds (id bigint, prefix VARCHAR (255))')
        logger.info('Guilds Table created')
    cur.execute('SELECT EXISTS(SELECT * FROM information_schema.tables WHERE TABLE_NAME = %s)', ('users',))
    users_table = cur.fetchone()[0]
    if users_table:
        logger.info('Users Table exist')
    else:
        logger.info("Users Table doesn't exist")
        logger.info('Creating Users Table')
        cur.execute('CREATE TABLE users (id bigint, anilist VARCHAR (255), myanimelist VARCHAR (255), kitsu '
                    'VARCHAR (255))')
        logger.info('Users Table created')
    db.commit()
    cur.close()
    db.close()
    logger.info('Database Check completed')


def start_bot():
    logger.info('Running Bot')
    try:
        bot = AnimeSearchBot()
        bot.run(config.TOKEN)
    except Exception as exception:
        logger.exception(exception)
        sys.exit()


if __name__ == '__main__':
    main()
