var updateInterval = 180000;

function formatDate(inputDate) {
    var date = new Date(inputDate);
    var formattedDate = date.toDateString() + ' ' + date.toLocaleTimeString();
    return formattedDate;
}

var lastKnownNews = null;

document.addEventListener('DOMContentLoaded', function () {
    if (!Notification) {
        alert('Web notifications are not supported in this browser.');
        return;
    }

    if (Notification.permission !== 'granted') {
        Notification.requestPermission().then(function (permission) {
            if (permission === 'granted') {
                console.log('Notification permission granted.');
            }
        });
    }
});

function toggleArticleText(blockId, link) {
    var block = document.getElementById(blockId);
    var loader = block.querySelector('.loader');
    var articleText = block.querySelector('.article-text');

    if (articleText.style.display === 'none') {
        // Показываем лоадер и скрываем текст
        loader.style.display = 'inline-block';
        articleText.style.display = 'none';

        // Выполняем запрос к серверу Flask для получения article_text
        $.get("/get_article_text?url=" + encodeURIComponent(link), function (data) {
            if (data.error) {
                articleText.innerText = 'Failed to fetch article.';
            } else {
                articleText.innerText = data.article_text;
            }

            // Скрываем лоадер и показываем текст
            loader.style.display = 'none';
            articleText.style.display = 'block';
        });
    } else {
        // Скрываем текст
        articleText.style.display = 'none';
    }



}

function updateFeeds() {
    $.post("/get_feeds", {}, function (data) {
        if (data.error) {
            $("#rss-feed").html("<p class='error'>" + data.error + "</p>");
            return;
        }

        console.log(data);
        if (data.length === 0) {
            return;
        }

        var latestNews = data[0];

        if (!lastKnownNews || lastKnownNews.title !== latestNews.title) {
            sendNotification(latestNews.title, latestNews.link);
            lastKnownNews = latestNews;
        }

        $("#rss-feed").empty();
        for (let entry of data) {
            var blockId = "block-" + entry.id;
            var html = `<div class='block' id='${blockId}'>
                <h1><a href='javascript:void(0);' onclick='toggleArticleText("${blockId}", "${entry.link}");'><b>${entry.title}</b></a></h1>
                <p>${entry.description}</p>
                <p class='date' data-date>${formatDate(entry.published)}</p>
                <div class='loader'></div>
                <div class='article-text' style='display: none;'></div>
            </div>`;

            $("#rss-feed").append(html);
        }
    });
}

function sendNotification(title) {
    if (Notification.permission === 'granted') {
        var notification = new Notification(title, {
            body: 'New news available!'
        });

        notification.onclick = function () {

        };
    }
}

setInterval(updateFeeds, updateInterval);

$(document).ready(function () {
    updateFeeds();
});