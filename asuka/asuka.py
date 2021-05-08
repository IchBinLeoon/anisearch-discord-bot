"""
This file is part of the AniSearch Discord Bot.

Copyright (C) 2021 IchBinLeoon

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.
"""

import asyncio
import logging
import os
import time

import aiohttp
import psycopg2
import psycopg2.pool
from dotenv import load_dotenv

load_dotenv()

BOT_API_HOST = os.getenv('BOT_API_HOST')
BOT_API_PORT = os.getenv('BOT_API_PORT')
BOT_API_SECRET_KEY = os.getenv('BOT_API_SECRET_KEY')

DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s: %(message)s',
                    datefmt='%m/%d/%Y %H:%M:%S')

ANILIST_API_ENDPOINT = 'https://graphql.anilist.co'

TIME = 600


def handle_exception(loop, context):
    msg = context.get('exception', context['message'])
    logging.error(f'Caught exception: {msg}')


class Asuka:

    def __init__(self):
        self.pool = psycopg2.pool.SimpleConnectionPool(5, 10, host=DB_HOST, port=DB_PORT, dbname=DB_NAME, user=DB_USER,
                                                       password=DB_PASSWORD)
        self.loop = asyncio.get_event_loop()
        self.session = None

    async def _session(self):
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session

    async def __aexit__(self, exc_type, exc, tb):
        await self.close()

    async def close(self):
        if self.session is not None:
            await self.session.close()

    async def fetch_anilist(self):
        query = '''
        query ($page: Int, $perPage: Int, $notYetAired: Boolean, $sort: [AiringSort]) {
          Page(page: $page, perPage: $perPage) {
            airingSchedules(notYetAired: $notYetAired, sort: $sort) {
              airingAt
              episode
              media {
                id
                title {
                  romaji
                  english
                }
                coverImage {
                  large
                }
                siteUrl
              }
            }
          }
        }
        '''
        variables = {'page': 1, 'perPage': 50, 'notYetAired': True, 'sort': 'TIME'}
        session = await self._session()
        r = await session.post(ANILIST_API_ENDPOINT, json={'query': query, 'variables': variables})
        logging.info(f'{r.method} {r.url} {r.status} {r.reason}')
        if r.status != 200:
            return None
        return await r.json()

    async def clear_table(self):
        conn = self.pool.getconn()
        try:
            with conn.cursor() as cur:
                cur.execute('DELETE FROM schedule;')
                conn.commit()
                logging.info('Cleared database table')
        finally:
            self.pool.putconn(conn)

    async def insert_table(self, data):
        conn = self.pool.getconn()
        try:
            with conn.cursor() as cur:
                for entry in data.get('data')['Page']['airingSchedules']:
                    try:
                        cur.execute('INSERT INTO schedule (id, time, episode, romaji, english, image, url) VALUES '
                                    '(%s, %s,  %s, %s, %s, %s, %s)',
                                    (entry.get('media')['id'],
                                     entry.get('airingAt'),
                                     entry.get('episode'),
                                     entry.get('media')['title']['romaji'],
                                     entry.get('media')['title']['english'],
                                     entry.get('media')['coverImage']['large'],
                                     entry.get('media')['siteUrl']))
                    except Exception as e:
                        logging.exception(e)
                conn.commit()
                logging.info('Inserted new database entries')
        finally:
            self.pool.putconn(conn)

    async def check(self):
        logging.info('Checking database entries')
        new_episodes = []
        conn = self.pool.getconn()
        try:
            with conn.cursor() as cur:
                cur.execute('SELECT * FROM schedule')
                for row in cur:
                    if row[1] < time.time():
                        logging.info(f'New episode: {row[3]} [{row[0]}]')
                        payload = {
                            'id': row[0],
                            'episode': row[2],
                            'romaji': row[3],
                            'english': row[4],
                            'image': row[5],
                            'url': row[6]
                        }
                        session = await self._session()
                        r = await session.post(f'http://{BOT_API_HOST}:{BOT_API_PORT}/api/schedule?type=notification',
                                               headers={'Authentication': BOT_API_SECRET_KEY}, json=payload)
                        logging.info(f'{r.method} {r.url} {r.status} {r.reason}')
                        if r.status == 200:
                            new_episodes.append(row[0])
            with conn.cursor() as cur:
                for episode in new_episodes:
                    cur.execute('DELETE FROM schedule WHERE id = %s;', (episode,))
                    logging.info(f'Deleted {episode} from database')
                conn.commit()
        finally:
            self.pool.putconn(conn)

    async def work(self):
        while True:
            await self.check()
            await asyncio.sleep(1)
            data = await self.fetch_anilist()
            if data is not None:
                await self.clear_table()
                await asyncio.sleep(1)
                await self.insert_table(data)
            await asyncio.sleep(TIME)

    def run(self):
        loop = self.loop
        loop.set_exception_handler(handle_exception)
        loop.run_until_complete(self.clear_table())
        loop.create_task(self.work())
        try:
            loop.run_forever()
        except KeyboardInterrupt:
            logging.info('Process interrupted')
        finally:
            logging.info('Stopping Asuka')
            self.pool.closeall()
            loop.close()


if __name__ == '__main__':
    logging.info('Starting Asuka')
    a = Asuka()
    a.run()
