import discord
import psycopg2
from discord.ext.commands import when_mentioned_or
from animesearch import config
from animesearch.utils.logger import logger


def get_command_prefix(self, message):
    if isinstance(message.channel, discord.channel.DMChannel):
        return when_mentioned_or('as!')(self, message)
    else:
        try:
            db = psycopg2.connect(host=config.DB_HOST, dbname=config.DB_NAME, user=config.DB_USER,
                                  password=config.BD_PASSWORD)
            cur = db.cursor()
            try:
                cur.execute('SELECT prefix FROM guilds WHERE id = %s;', (message.guild.id,))
                prefix = cur.fetchone()[0]
                db.commit()
                cur.close()
                db.close()
                return when_mentioned_or(prefix, 'as!')(self, message)
            except TypeError:
                cur.execute('INSERT INTO guilds (id, prefix) VALUES (%s, %s)', (message.guild.id, 'as!'))
                cur.execute('SELECT prefix FROM guilds WHERE id = %s;', (message.guild.id,))
                prefix = cur.fetchone()[0]
                db.commit()
                cur.close()
                db.close()
                logger.info('Changed Prefix for Guild {} to {}'.format(message.guild.id, prefix))
                return when_mentioned_or(prefix, 'as!')(self, message)
        except Exception as exception:
            logger.exception(exception)
            return when_mentioned_or('as!')(self, message)


def select_prefix(ctx):
    if isinstance(ctx.channel, discord.channel.DMChannel):
        return 'as!'
    else:
        try:
            db = psycopg2.connect(host=config.DB_HOST, dbname=config.DB_NAME, user=config.DB_USER,
                                  password=config.BD_PASSWORD)
            cur = db.cursor()
            cur.execute('SELECT prefix FROM guilds WHERE id = %s;', (ctx.guild.id,))
            prefix = cur.fetchone()[0]
            db.commit()
            cur.close()
            db.close()
            return prefix
        except Exception as exception:
            logger.exception(exception)


def insert_prefix(guild):
    try:
        db = psycopg2.connect(host=config.DB_HOST, dbname=config.DB_NAME, user=config.DB_USER,
                              password=config.BD_PASSWORD)
        cur = db.cursor()
        cur.execute('INSERT INTO guilds (id, prefix) VALUES (%s, %s)', (guild.id, 'as!'))
        db.commit()
        cur.close()
        db.close()
        logger.info('Set Prefix for Guild {}'.format(guild.id))
    except Exception as exception:
        logger.exception(exception)


def delete_prefix(guild):
    try:
        db = psycopg2.connect(host=config.DB_HOST, dbname=config.DB_NAME, user=config.DB_USER,
                              password=config.BD_PASSWORD)
        cur = db.cursor()
        cur.execute('DELETE FROM guilds WHERE id = %s', (guild.id,))
        db.commit()
        cur.close()
        db.close()
        logger.info('Deleted Prefix for Guild {}'.format(guild.id))
    except Exception as exception:
        logger.exception(exception)


def change_prefix(ctx, prefix):
    try:
        db = psycopg2.connect(host=config.DB_HOST, dbname=config.DB_NAME, user=config.DB_USER,
                              password=config.BD_PASSWORD)
        cur = db.cursor()
        cur.execute('UPDATE guilds SET prefix = %s WHERE id = %s;', (prefix, ctx.guild.id,))
        cur.execute('SELECT prefix FROM guilds WHERE id = %s;', (ctx.guild.id,))
        prefix_new = cur.fetchone()[0]
        db.commit()
        cur.close()
        db.close()
        logger.info('Changed Prefix for Guild {} to {}'.format(ctx.guild.id, prefix))
        return prefix_new
    except Exception as exception:
        logger.exception(exception)
