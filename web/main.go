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
	"io"
	"io/ioutil"
	"log"
	"net/http"
	"os"
)

var (
	host string
	port string
	mode string
	botApiHost string
	botApiPort string
	botApiSecretKey string
)

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

}

func main() {

	gin.SetMode(mode)
	router := gin.Default()

	router.LoadHTMLGlob("templates/*")
	router.GET("/", index)
	router.GET("/logs", logs)

	bindStr := fmt.Sprintf("%s:%s", host, port)
	if err := router.Run(bindStr); err != nil {
		log.Fatal(err)
	}

}