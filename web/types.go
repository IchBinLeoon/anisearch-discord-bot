package main

import (
	"github.com/lib/pq"
	"gorm.io/gorm"
)

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

	ID        int64
	Prefix    string
	Channel   int64
	Role      int64
	Watchlist pq.Int64Array `gorm:"type:integer[]"`
}

type User struct {
	gorm.Model

	ID          int64
	Anilist     string
	Myanimelist string
	Kitsu       string
}
