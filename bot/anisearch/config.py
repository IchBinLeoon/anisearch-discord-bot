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

import os

BOT_TOKEN = os.getenv('BOT_TOKEN')
BOT_OWNER_ID = os.getenv('BOT_OWNER_ID')
BOT_SAUCENAO_API_KEY = os.getenv('BOT_SAUCENAO_API_KEY')
BOT_TOPGG_TOKEN = os.getenv('BOT_TOPGG_TOKEN')
BOT_LEVEL = os.getenv('BOT_LEVEL')
BOT_API_HOST = os.getenv('BOT_API_HOST')
BOT_API_PORT = os.getenv('BOT_API_PORT')
BOT_API_SECRET_KEY = os.getenv('BOT_API_SECRET_KEY')

DB_HOST = os.getenv('POSTGRES_HOST')
DB_PORT = os.getenv('POSTGRES_PORT')
DB_NAME = os.getenv('POSTGRES_DB')
DB_USER = os.getenv('POSTGRES_USER')
DB_PASSWORD = os.getenv('POSTGRES_PASSWORD')
