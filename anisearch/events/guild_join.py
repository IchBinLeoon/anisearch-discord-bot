import psycopg2
from discord.ext import commands

from anisearch import bot
from anisearch.config import config


class GuildJoin(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        bot.logger.info('Joined server %s' % guild.name)
        db = psycopg2.connect(host=config.DB_HOST, dbname=config.DB_NAME, user=config.DB_USER,
                              password=config.BD_PASSWORD)
        cur = db.cursor()
        cur.execute('INSERT INTO guilds (id, prefix) VALUES (%s, %s)', (guild.id, 'as!'))
        db.commit()
        cur.close()
        db.close()


def setup(client):
    client.add_cog(GuildJoin(client))
    bot.logger.info('Loaded extension GuildJoin')


def teardown():
    bot.logger.info('Unloaded extension GuildJoin')
