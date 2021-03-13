function dashboard() {
    window.location.href = "/";
}

function autoRefresh() {
    window.location.href = "/logs";
}

setInterval(autoRefresh, 60000)