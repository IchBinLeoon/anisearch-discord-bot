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
	"github.com/gin-gonic/gin"
	"github.com/joho/godotenv"
	"io/ioutil"
	"log"
	"net/http"
	"os"
)

var WebHost string
var WebPort string
var BotApiHost string
var BotApiPort string
var BotApiSecretKey string

type Stats struct {
	Ready string `json:"ready"`
	Guilds string `json:"guilds"`
	Users string `json:"users"`
	Channels string `json:"channels"`
	Uptime string `json:"uptime"`
	Shards string `json:"shards"`
	Latency string `json:"latency"`
	Cogs string `json:"cogs"`
}

type Logs struct {
	Logs string `json:"logs"`
}

func index(c *gin.Context) {

	data, _ := request()

	Data := Stats{}
	if err := json.Unmarshal([]byte(data), &Data); err != nil {
		log.Fatal(err)
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

	data, _ := request()

	Data := Logs{}
	if err := json.Unmarshal([]byte(data), &Data); err != nil {
		log.Fatal(err)
	}

	c.String(http.StatusOK, Data.Logs)

}

func request() (string, error) {

	client := &http.Client{}

	url := "http://" + BotApiHost + ":" + BotApiPort
	req, err := http.NewRequest("GET", url, nil)
	if err != nil {
		log.Fatal(err)
	}

	req.Header.Add("Authentication", BotApiSecretKey)
	res, err := client.Do(req)

	if err != nil {
		data := `{"ready": "-", "guilds": "-", "users": "-", "channels": "-", "uptime": "-", "shards": "-", "latency": "-", "cogs": "-", "logs": ""}`
		return data, err
	}

	data, err := ioutil.ReadAll(res.Body)
	defer res.Body.Close()

	if err != nil {
		log.Fatal(err)
	}

	return string(data), nil

}

func init() {

	if _, err := os.Stat("../.env"); err == nil {
		if err := godotenv.Load("../.env"); err != nil {
			log.Fatal(err)
		}
	}

	WebHost = os.Getenv("WEB_HOST")
	WebPort = os.Getenv("WEB_PORT")
	BotApiHost = os.Getenv("BOT_API_HOST")
	BotApiPort = os.Getenv("BOT_API_PORT")
	BotApiSecretKey = os.Getenv("BOT_API_SECRET_KEY")

}

func main() {

	gin.SetMode(gin.ReleaseMode)
	router := gin.Default()

	router.LoadHTMLGlob("templates/*")
	router.GET("/", index)
	router.GET("/logs", logs)

	if err := router.Run(WebHost + ":" + WebPort); err != nil {
		log.Fatal(err)
	}

}
