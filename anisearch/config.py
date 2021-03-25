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

from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('TOKEN')

OWNER_ID = os.getenv('OWNER_ID')

DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')

SAUCENAO = os.getenv('SAUCENAO')

TOPGG_TOKEN = os.getenv('TOPGG_TOKEN')

IPC_HOST = os.getenv('IPC_HOST')
IPC_PORT = os.getenv('IPC_PORT')
IPC_SECRET_KEY = os.getenv('IPC_SECRET_KEY')
