import psycopg2
from discord.ext import commands

import anisearch
from config import config


class GuildJoin(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        anisearch.logger.info('Joined server %s' % guild.name)
        db = psycopg2.connect(host=config.DB_HOST, dbname=config.DB_NAME, user=config.DB_USER,
                              password=config.BD_PASSWORD)
        cur = db.cursor()
        cur.execute('INSERT INTO guilds (id, prefix) VALUES (%s, %s)', (guild.id, 'as!'))
        db.commit()
        cur.close()
        db.close()


def setup(client):
    client.add_cog(GuildJoin(client))
    anisearch.logger.info('Loaded extension GuildJoin')


def teardown():
    anisearch.logger.info('Unloaded extension GuildJoin')
