import discord
import psycopg2
from discord.ext import commands

import main
from config import config


class GuildJoin(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        main.logger.info('Joined server %s' % guild.name)
        db = psycopg2.connect(host=config.DB_HOST, dbname=config.DB_NAME, user=config.DB_USER,
                              password=config.BD_PASSWORD)
        cur = db.cursor()
        cur.execute('INSERT INTO guilds (id, prefix) VALUES (%s, %s)', (guild.id, 'as!'))
        db.commit()
        cur.close()
        db.close()
        guild_join_embed = discord.Embed(title="Joined server %s" % guild.name,
                                         color=0x4169E1)
        guild_join_embed.add_field(name="Owner", value=guild.owner,
                                   inline=True)
        guild_join_embed.add_field(name="Server ID", value=guild.id,
                                   inline=True)
        guild_join_embed.add_field(name="Created", value=guild.created_at.strftime('%d/%m/%Y, %H:%M:%S'),
                                   inline=True)
        guild_join_embed.add_field(name="Region", value=guild.region,
                                   inline=True)
        guild_join_embed.add_field(name="Members", value=guild.member_count,
                                   inline=True)
        guild_join_embed.add_field(name="Tier", value=guild.premium_tier,
                                   inline=True)
        guild_join_embed.set_thumbnail(url=guild.icon_url)
        await self.client.get_user(main.__owner_id__).send(embed=guild_join_embed)


def setup(client):
    client.add_cog(GuildJoin(client))
    main.logger.info('Loaded extension GuildJoin')


def teardown():
    main.logger.info('Unloaded extension GuildJoin')
