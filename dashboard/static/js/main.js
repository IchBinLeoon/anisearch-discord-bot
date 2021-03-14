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