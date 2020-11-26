import psycopg2

from animesearch import config
from animesearch.utils.logger import logger


def update_anilist_profile(ctx, username):
    try:
        db = psycopg2.connect(host=config.DB_HOST, dbname=config.DB_NAME,
                              user=config.DB_USER, password=config.BD_PASSWORD)
        cur = db.cursor()
        try:
            cur.execute('UPDATE users SET anilist = %s WHERE id = %s;', (username, ctx.author.id,))
            cur.execute('SELECT anilist FROM users WHERE id = %s;', (ctx.author.id,))
            set_username = cur.fetchone()[0]
            db.commit()
            cur.close()
            db.close()
        except TypeError:
            cur.execute('INSERT INTO users (id, anilist) VALUES (%s, %s)', (ctx.author.id, username))
            cur.execute('SELECT anilist FROM users WHERE id = %s;', (ctx.author.id,))
            set_username = cur.fetchone()[0]
            db.commit()
            cur.close()
            db.close()
        logger.info('Set AniList Profile for User {} to {}'.format(ctx.author.id, set_username))
        return set_username
    except Exception as exception:
        logger.exception(exception)
        return None


def update_myanimelist_profile(ctx, username):
    try:
        db = psycopg2.connect(host=config.DB_HOST, dbname=config.DB_NAME,
                              user=config.DB_USER, password=config.BD_PASSWORD)
        cur = db.cursor()
        try:
            cur.execute('UPDATE users SET myanimelist = %s WHERE id = %s;', (username, ctx.author.id,))
            cur.execute('SELECT myanimelist FROM users WHERE id = %s;', (ctx.author.id,))
            set_username = cur.fetchone()[0]
            db.commit()
            cur.close()
            db.close()
        except TypeError:
            cur.execute('INSERT INTO users (id, myanimelist) VALUES (%s, %s)', (ctx.author.id, username))
            cur.execute('SELECT myanimelist FROM users WHERE id = %s;', (ctx.author.id,))
            set_username = cur.fetchone()[0]
            db.commit()
            cur.close()
            db.close()
        logger.info('Set MyAnimeList Profile for User {} to {}'.format(ctx.author.id, set_username))
        return set_username
    except Exception as exception:
        logger.exception(exception)
        return None


def update_kitsu_profile(ctx, username):
    try:
        db = psycopg2.connect(host=config.DB_HOST, dbname=config.DB_NAME,
                              user=config.DB_USER, password=config.BD_PASSWORD)
        cur = db.cursor()
        try:
            cur.execute('UPDATE users SET kitsu = %s WHERE id = %s;', (username, ctx.author.id,))
            cur.execute('SELECT kitsu FROM users WHERE id = %s;', (ctx.author.id,))
            set_username = cur.fetchone()[0]
            db.commit()
            cur.close()
            db.close()
        except TypeError:
            cur.execute('INSERT INTO users (id, kitsu) VALUES (%s, %s)', (ctx.author.id, username))
            cur.execute('SELECT kitsu FROM users WHERE id = %s;', (ctx.author.id,))
            set_username = cur.fetchone()[0]
            db.commit()
            cur.close()
            db.close()
        logger.info('Set Kitsu Profile for User {} to {}'.format(ctx.author.id, set_username))
        return set_username
    except Exception as exception:
        logger.exception(exception)
        return None


def select_anilist_profile(user_id):
    try:
        db = psycopg2.connect(host=config.DB_HOST, dbname=config.DB_NAME, user=config.DB_USER,
                              password=config.BD_PASSWORD)
        cur = db.cursor()
        try:
            cur.execute('SELECT anilist FROM users WHERE id = %s;', (user_id,))
            profile = cur.fetchone()[0]
            db.commit()
            cur.close()
            db.close()
        except TypeError:
            profile = None
        return profile
    except Exception as exception:
        logger.exception(exception)
        return None


def select_myanimelist_profile(user_id):
    try:
        db = psycopg2.connect(host=config.DB_HOST, dbname=config.DB_NAME, user=config.DB_USER,
                              password=config.BD_PASSWORD)
        cur = db.cursor()
        try:
            cur.execute('SELECT myanimelist FROM users WHERE id = %s;', (user_id,))
            profile = cur.fetchone()[0]
            db.commit()
            cur.close()
            db.close()
        except TypeError:
            profile = None
        return profile
    except Exception as exception:
        logger.exception(exception)
        return None


def select_kitsu_profile(user_id):
    try:
        db = psycopg2.connect(host=config.DB_HOST, dbname=config.DB_NAME, user=config.DB_USER,
                              password=config.BD_PASSWORD)
        cur = db.cursor()
        try:
            cur.execute('SELECT kitsu FROM users WHERE id = %s;', (user_id,))
            profile = cur.fetchone()[0]
            db.commit()
            cur.close()
            db.close()
        except TypeError:
            profile = None
        return profile
    except Exception as exception:
        logger.exception(exception)
        return None

