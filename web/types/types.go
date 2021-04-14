/*
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
*/

package types

import "gorm.io/gorm"

type Stats struct {
	IsReady      bool    `json:"is_ready"`
	GuildCount   int     `json:"guild_count"`
	UserCount    int     `json:"user_count"`
	ChannelCount int     `json:"channel_count"`
	Uptime       float64 `json:"uptime"`
	ShardCount   int     `json:"shard_count"`
	Latency      float64 `json:"latency"`
	CogCount     int     `json:"cog_count"`
}

type Logs struct {
	Logs string `json:"logs"`
}

type Shard struct {
	ID              int     `json:"id"`
	ShardCount      int     `json:"shard_count"`
	IsClosed        bool    `json:"is_closed"`
	Latency         float64 `json:"latency"`
	IsWsRatelimited bool    `json:"is_ws_ratelimited"`
}

type Shards struct {
	Shards []Shard `json:"shards"`
}

type Guild struct {
	gorm.Model

	ID     int64
	Prefix string
}

type User struct {
	gorm.Model

	ID          int64
	Anilist     string
	Myanimelist string
	Kitsu       string
}