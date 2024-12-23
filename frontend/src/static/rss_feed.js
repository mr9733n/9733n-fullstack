// rss_feed.js
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

function encodeId(id) {
    return id.replace(/[^a-zA-Z0-9]/g, "_"); // Замена всех недопустимых символов на "_"
}

function toggleArticleText(blockId, link) {
    var block = document.getElementById(blockId);
    var loader = block.querySelector('.loader');
    var articleText = block.querySelector('.article-text');

    if (articleText.style.display === 'none') {
        loader.style.display = 'inline-block';
        articleText.style.display = 'none';

        // Fetch the article details
        $.get(`/get_article_details?url=${encodeURIComponent(link)}`, function (data) {
            if (data.error) {
                articleText.innerText = 'Failed to fetch article.';
            } else {
                articleText.innerHTML = `
                <div class="article-image">
                    ${data.images
                        .map(
                            img =>
                                `<img src="${img}" alt="" onclick="openImageModal('${img}', 'Full-size Image')" style="cursor:pointer; "/>`
                        )
                        .join('')}</div>
                    <div class="article-text">${data.article_text}</dev>

                `;
            }

            loader.style.display = 'none';
            articleText.style.display = 'block';
        });
    } else {
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
			var rawBlockId = "block-" + entry.link; // Исходный ID
			var safeBlockId = encodeId(rawBlockId); // Преобразуем ID
			var html = `<div class='block' id='${safeBlockId}'>
				<h1><a href='javascript:void(0);' onclick='toggleArticleText("${safeBlockId}", "${entry.link}");'><b>${entry.title}</b></a></h1>
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

function openImageModal(imgSrc, captionText) {
    // Replace '/m/' with '/l/' in the URL to get the larger version of the image
    const largeImgSrc = imgSrc.replace('/m/', '/l/');
    const modal = document.getElementById('imageModal');
    const modalImg = document.getElementById('modalImage');
    const caption = document.getElementById('caption');

    modal.style.display = 'block';
    modalImg.src = largeImgSrc;
    caption.textContent = captionText || '';

    // Close the modal when clicked outside the image
    modal.onclick = function (event) {
        if (event.target === modal) {
            closeModal();
        }
    };
}

function closeModal() {
    const modal = document.getElementById('imageModal');
    modal.style.display = 'none';
}

// Dynamically attach `onclick` handler when displaying images
function createImageElement(imgSrc, altText, captionText) {
    const largeImgSrc = imgSrc.replace('/m/', '/l/');
    return `<img
                src="${imgSrc}"
                alt="${altText}"
                onclick="openImageModal('${largeImgSrc}', '${captionText}')"
                style="cursor:pointer;"
            />`;
}
