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

import logging

logger = logging.getLogger('anisearch')
logger.setLevel(logging.INFO)

formatter = logging.Formatter('%(name)s - %(asctime)s - %(levelname)s - %(message)s', datefmt='%d-%m-%Y %H:%M:%S')

file_handler = logging.FileHandler('./anisearch.log')
file_handler.setFormatter(formatter)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

if logger.hasHandlers():
    logger.handlers.clear()

logger.addHandler(file_handler)
logger.addHandler(stream_handler)
