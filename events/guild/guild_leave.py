import psycopg2
from discord.ext import commands

import anisearch
from config import config


class GuildLeave(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        anisearch.logger.info('Left server %s' % guild.name)
        db = psycopg2.connect(host=config.DB_HOST, dbname=config.DB_NAME, user=config.DB_USER,
                              password=config.BD_PASSWORD)
        cur = db.cursor()
        cur.execute('DELETE FROM guilds WHERE id = %s', (guild.id,))
        db.commit()
        cur.close()
        db.close()


def setup(client):
    client.add_cog(GuildLeave(client))
    anisearch.logger.info('Loaded extension GuildLeave')


def teardown():
    anisearch.logger.info('Unloaded extension GuildLeave')
