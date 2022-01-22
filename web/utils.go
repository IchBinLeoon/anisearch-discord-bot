package main

import (
	"fmt"
	"io"
	"io/ioutil"
	"math"
	"net/http"
)

func Request(method string, url string, headers map[string]string, body io.Reader) (string, error) {
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

func FormatUptime(uptime int) string {
	t := float64(uptime)

	h := math.Floor(t / 3600)
	m := math.Floor((t - h*3600) / 60)
	s := t - (h*3600 + m*60)

	return fmt.Sprintf("%02.f:%02.f:%02.f", h, m, s)
}
