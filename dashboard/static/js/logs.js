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

function redirectDashboard() {
    window.location.href = "/";
}

function scrollUp() {
    window.scrollTo(0, 0);
}

function scrollDown() {
    window.scrollTo(0, document.body.scrollHeight);
}

function autoRefresh() {
    location.reload();
}

setInterval(autoRefresh, 60000)

window.onscroll = function() {stickyFunction()};

const dashboardButton = document.getElementById("button-container");

const sticky = dashboardButton.offsetTop;

function stickyFunction() {
    if (window.pageYOffset >= sticky)
        dashboardButton.classList.add("sticky")
    else
        dashboardButton.classList.remove("sticky");
}