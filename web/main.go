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

package main

import (
	"encoding/json"
	"fmt"
	"github.com/gin-gonic/gin"
	"github.com/joho/godotenv"
	"gorm.io/driver/postgres"
	"gorm.io/gorm"
	"html/template"
	"io"
	"io/ioutil"
	"log"
	"math"
	"net/http"
	"os"
	"strings"
)

var (
	host string
	port string
	mode string
	botApiHost string
	botApiPort string
	botApiSecretKey string
	dbHost string
	dbPort string
	dbName string
	dbUser string
	dbPassword string
)

var (
	db *gorm.DB
	connErr error
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
	Shards []Shard
}

func index(c *gin.Context) {
	urlStr := fmt.Sprintf("http://%s:%s/api?type=stats", botApiHost, botApiPort)

	headers := make(map[string]string)
	headers["Authentication"] = botApiSecretKey

	data, err := request("GET", urlStr, headers, nil)
	if err != nil {
		log.Println(err)
	}

	Data := Stats{}
	if err := json.Unmarshal([]byte(data), &Data); err != nil {
		log.Println(err)
	}

	c.HTML(http.StatusOK, "index.tmpl", gin.H {
		"ready": Data.IsReady,
		"guilds": Data.GuildCount,
		"users": Data.UserCount,
		"channels": Data.ChannelCount,
		"uptime": int(math.Round(Data.Uptime)),
		"shards": Data.ShardCount,
		"latency": fmt.Sprintf("%.5f", Data.Latency),
		"cogs": Data.CogCount,
	})
}

func logs(c *gin.Context) {
	urlStr := fmt.Sprintf("http://%s:%s/api?type=logs", botApiHost, botApiPort)

	headers := make(map[string]string)
	headers["Authentication"] = botApiSecretKey

	data, err := request("GET", urlStr, headers, nil)
	if err != nil {
		log.Println(err)
	}

	Data := Logs{}
	if err := json.Unmarshal([]byte(data), &Data); err != nil {
		log.Println(err)
	}

	c.String(http.StatusOK, Data.Logs)
}

func shards(c *gin.Context) {
	urlStr := fmt.Sprintf("http://%s:%s/api?type=shards", botApiHost, botApiPort)

	headers := make(map[string]string)
	headers["Authentication"] = botApiSecretKey

	data, err := request("GET", urlStr, headers, nil)
	if err != nil {
		log.Println(err)
	}

	Data := Shards{}
	if err := json.Unmarshal([]byte(data), &Data); err != nil {
		log.Println(err)
	}

	var shardStrList []string
	for j, i := range Data.Shards {
		str := fmt.Sprintf("%d.\tID: %d | ShardCount: %d | IsClosed: %t | Latency: %.5f | IsWsRatelimited: %t", j, i.ID, i.ShardCount, i.IsClosed, i.Latency, i.IsWsRatelimited)
		shardStrList = append(shardStrList, str)
	}

	str := strings.Join(shardStrList, "\n")

	c.String(http.StatusOK, str)
}

func request(method string, url string, headers map[string]string, body io.Reader) (string, error) {
	client := &http.Client{}

	req, _ := http.NewRequest(method, url, body)

	if headers != nil {
		for key, value := range headers {
			req.Header.Add(key, value)
		}
	}

	res, err := client.Do(req)
	if err != nil {
		return "", err
	}

	data, err := ioutil.ReadAll(res.Body)
	if err := res.Body.Close(); err != nil {
		return "", err
	}

	return string(data), nil
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

func guilds(c *gin.Context) {
	var guilds []Guild

	db.Unscoped().Find(&guilds)

	var guildStrList []string
	for j, i := range guilds {
		str := fmt.Sprintf("%d.\tID: %d | Prefix: %s", j, i.ID, i.Prefix)
		guildStrList = append(guildStrList, str)
	}

	data := strings.Join(guildStrList, "\n")

	c.String(http.StatusOK, data)
}

func users(c *gin.Context) {
	var users []User

	db.Unscoped().Find(&users)

	var userStrList []string
	for j, i := range users {

		var profiles []string
		if i.Anilist != "" {
			profiles = append(profiles, fmt.Sprintf("AL: %s", i.Anilist))
		}
		if i.Myanimelist != "" {
			profiles = append(profiles, fmt.Sprintf("MAL: %s", i.Myanimelist))
		}
		if i.Kitsu != "" {
			profiles = append(profiles, fmt.Sprintf("Kitsu: %s", i.Kitsu))
		}
		profilesStr := strings.Join(profiles, " | ")

		str := fmt.Sprintf("%d.\tID: %d | %s", j, i.ID, profilesStr)
		userStrList = append(userStrList, str)
	}

	data := strings.Join(userStrList, "\n")

	c.String(http.StatusOK, data)
}

func formatUptime(uptime int) string {
	t := float64(uptime)

	h := math.Floor(t / 3600)
	m := math.Floor((t - h * 3600) / 60)
	s := t - (h * 3600 + m * 60)

	return fmt.Sprintf("%02.f:%02.f:%02.f", h, m, s)
}

func init() {
	if _, err := os.Stat("../.env"); err == nil {
		if err := godotenv.Load("../.env"); err != nil {
			log.Fatal(err)
		}
	}

	host = os.Getenv("WEB_HOST")
	port = os.Getenv("WEB_PORT")
	mode = os.Getenv("WEB_MODE")

	botApiHost = os.Getenv("BOT_API_HOST")
	botApiPort = os.Getenv("BOT_API_PORT")
	botApiSecretKey = os.Getenv("BOT_API_SECRET_KEY")

	dbHost = os.Getenv("DB_HOST")
	dbPort = os.Getenv("DB_PORT")
	dbName = os.Getenv("DB_NAME")
	dbUser = os.Getenv("DB_USER")
	dbPassword = os.Getenv("DB_PASSWORD")
}

func main() {
	log.Println("Starting AniSearch Admin Panel")

	connStr := fmt.Sprintf("host=%s port=%s dbname=%s user=%s password=%s sslmode=disable", dbHost, dbPort, dbName, dbUser, dbPassword)
	db, connErr = gorm.Open(postgres.Open(connStr), &gorm.Config{})
	if connErr != nil {
		log.Fatal(connErr)
	} else {
		log.Println(fmt.Sprintf(`Connected to database "%s" on %s:%s`, dbName, dbHost, dbPort))
	}

	gin.SetMode(mode)
	router := gin.Default()

	router.SetFuncMap(template.FuncMap{
		"formatUptime": formatUptime,
	})

	router.LoadHTMLGlob("templates/*")

	router.GET("/", index)
	router.GET("/logs", logs)
	router.GET("/shards", shards)
	router.GET("/guilds", guilds)
	router.GET("/users", users)

	bindStr := fmt.Sprintf("%s:%s", host, port)
	if err := router.Run(bindStr); err != nil {
		log.Fatal(err)
	}
}