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

function redirectLogs() {
    window.location.href = "/logs";
}

function reconnect() {
    window.location.href = "/?reconnect=true";
}

function countUptime() {
    let hour = Math.floor(uptime / 3600);
    let minute = Math.floor((uptime - hour * 3600) / 60);
    let seconds = uptime - (hour * 3600 + minute * 60);
    if(hour < 10)
        hour = "0" + hour;
    if(minute < 10)
        minute = "0" + minute;
    if(seconds < 10)
        seconds = "0" + seconds;
    document.getElementById("uptime").innerHTML = hour + ":" + minute + ":" + seconds;
    ++uptime;
}

if (uptime != null)
    setInterval(countUptime, 1000);

function autoRefresh() {
    location.reload();
}

setInterval(autoRefresh, 60000)