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
	Ready 	 bool 	 `json:"ready"`
	Guilds 	 int  	 `json:"guilds"`
	Users 	 int  	 `json:"users"`
	Channels int  	 `json:"channels"`
	Uptime 	 int  	 `json:"uptime"`
	Shards 	 int  	 `json:"shards"`
	Latency  float32 `json:"latency"`
	Cogs 	 int  	 `json:"cogs"`
}

type Logs struct {
	Logs string `json:"logs"`
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
		"ready": Data.Ready,
		"guilds": Data.Guilds,
		"users": Data.Users,
		"channels": Data.Channels,
		"uptime": Data.Uptime,
		"shards": Data.Shards,
		"latency": Data.Latency,
		"cogs": Data.Cogs,
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
		str := fmt.Sprintf("%d.\tID: %d | AL: %s | MAL: %s | Kitsu: %s", j, i.ID, i.Anilist, i.Myanimelist, i.Kitsu)
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

	var hStr string
	if h < 10 {hStr = fmt.Sprintf("0%d", int(h))} else {hStr = fmt.Sprintf("%d", int(h))}
	var mStr string
	if m < 10 {mStr = fmt.Sprintf("0%d", int(m))} else {mStr = fmt.Sprintf("%d", int(m))}
	var sStr string
	if s < 10 {sStr = fmt.Sprintf("0%d", int(s))} else {sStr = fmt.Sprintf("%d", int(s))}

	return fmt.Sprintf("%s:%s:%s", hStr, mStr, sStr)
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
	router.GET("/guilds", guilds)
	router.GET("/users", users)

	bindStr := fmt.Sprintf("%s:%s", host, port)
	if err := router.Run(bindStr); err != nil {
		log.Fatal(err)
	}
}