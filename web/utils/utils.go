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

package utils

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
	m := math.Floor((t - h * 3600) / 60)
	s := t - (h * 3600 + m * 60)

	return fmt.Sprintf("%02.f:%02.f:%02.f", h, m, s)
}