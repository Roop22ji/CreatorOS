/* =========================================================
   CREATOR MOBILE APP
========================================================= */

"use strict";


/* =========================================================
   CONFIGURATION
========================================================= */

const API_BASE = "";


/* =========================================================
   APPLICATION STATE
========================================================= */

const state = {

    token:
        localStorage.getItem(
            "creator_token"
        ) || "",

    user:
        JSON.parse(
            localStorage.getItem(
                "creator_user"
            ) || "null"
        ),

    currentVideo:
        null,

    currentScreen:
        "home"

};


/* =========================================================
   DOM HELPERS
========================================================= */

function $(selector) {

    return document.querySelector(
        selector
    );

}

function $all(selector) {

    return document.querySelectorAll(
        selector
    );

}


/* =========================================================
   API URL
========================================================= */

function api(path) {

    return API_BASE + path;

}


/* =========================================================
   API REQUEST
========================================================= */

async function apiRequest(
    path,
    options = {}
) {

    const headers =
        options.headers || {};

    if (
        state.token &&
        !headers.Authorization
    ) {

        headers.Authorization =
            "Bearer " +
            state.token;

    }

    options.headers = headers;

    const response =
        await fetch(
            api(path),
            options
        );

    let data = {};

    try {

        data =
            await response.json();

    } catch (
        error
    ) {

        data = {};

    }

    if (
        response.status === 401
    ) {

        logoutLocal();

    }

    return {
        response,
        data
    };

}


/* =========================================================
   TOAST
========================================================= */

let toastTimer = null;

function showToast(
    message
) {

    const toast =
        $("#toast");

    toast.textContent =
        message;

    toast.classList.add(
        "show"
    );

    clearTimeout(
        toastTimer
    );

    toastTimer =
        setTimeout(
            () => {

                toast.classList.remove(
                    "show"
                );

            },
            2500
        );

}


/* =========================================================
   SAVE LOGIN
========================================================= */

function saveLogin(
    token,
    user
) {

    state.token = token;

    state.user = user;

    localStorage.setItem(
        "creator_token",
        token
    );

    localStorage.setItem(
        "creator_user",
        JSON.stringify(
            user
        )
    );

}


/* =========================================================
   LOGOUT
========================================================= */

function logoutLocal() {

    state.token = "";

    state.user = null;

    localStorage.removeItem(
        "creator_token"
    );

    localStorage.removeItem(
        "creator_user"
    );

    updateProfileUI();

}


/* =========================================================
   SCREEN NAVIGATION
========================================================= */

function showScreen(
    name
) {

    const screens =
        $all(".screen");


    /* -------------------------------------------------------
       HIDE ALL SCREENS
    ------------------------------------------------------- */

    screens.forEach(
        screen => {

            screen.classList.remove(
                "active"
            );

        }
    );


    /* -------------------------------------------------------
       SHOW SELECTED SCREEN
    ------------------------------------------------------- */

    const target =
        $(
            "#" +
            name +
            "Screen"
        );

    if (target) {

        target.classList.add(
            "active"
        );

    }


    /* -------------------------------------------------------
       STOP SHORTS WHEN LEAVING
    ------------------------------------------------------- */

    if (
        state.currentScreen === "shorts" &&
        name !== "shorts"
    ) {

        if (
            typeof stopShorts ===
            "function"
        ) {

            stopShorts();

        }

    }


    /* -------------------------------------------------------
       SAVE CURRENT SCREEN
    ------------------------------------------------------- */

    state.currentScreen =
        name;


    /* -------------------------------------------------------
       UPDATE BOTTOM NAVIGATION
    ------------------------------------------------------- */

    updateNavigation(
        name
    );


    /* -------------------------------------------------------
       HOME
    ------------------------------------------------------- */

    if (
        name === "home"
    ) {

        loadForYouFeed();

    }


    /* -------------------------------------------------------
       PROFILE
    ------------------------------------------------------- */

    if (
        name === "profile"
    ) {

        loadProfile();

    }


    /* -------------------------------------------------------
       CREATOR STUDIO
    ------------------------------------------------------- */

    if (
        name === "studio"
    ) {
    
        loadCreatorStudio();
    
        loadCreatorBoost();
    
    }

    if (
        name === "notifications"
    ) {
    
        loadNotifications();
    
    }


    /* -------------------------------------------------------
       SHORTS
    ------------------------------------------------------- */

    if (
        name === "shorts"
    ) {

        loadShorts();

    }

    if (
        name === "creatorProfile"
    ) {
    
        // Public creator profile is
        // loaded manually by openCreatorProfile().
    
    }

}


/* =========================================================
   NAVIGATION STATE
========================================================= */

function updateNavigation(
    current
) {

    const buttons =
        $all(
            ".nav-button"
        );

    buttons.forEach(
        button => {

            button.classList.remove(
                "active"
            );

            if (
                button.dataset.screen ===
                current
            ) {

                button.classList.add(
                    "active"
                );

            }

        }
    );

}


/* =========================================================
   VIDEO FEED
========================================================= */

async function loadFeed() {

    const container =
        $("#videoFeed");

    if (!container) {
        return;
    }

    container.innerHTML = `
        <div class="loading-box">
            <div class="loading-spinner"></div>
            <div>Loading videos...</div>
        </div>
    `;

    try {

        const {
            response,
            data
        } =
            await apiRequest(
                "/api/videos"
            );

        if (
            !response.ok
        ) {

            throw new Error(
                data.error ||
                "Could not load videos."
            );

        }

        renderVideos(
            container,
            data.videos || []
        );

    } catch (
        error
    ) {

        container.innerHTML = `
            <div class="empty-box">
                <div>
                    
                </div>

                <div>
                    Could not load videos.
                </div>

                <div>
                    ${escapeHtml(
                        error.message
                    )}
                </div>

                <button
                    class="primary-button"
                    onclick="loadFeed()"
                >
                    Retry
                </button>
            </div>
        `;

    }

}

/* =========================================================
   FOR YOU FEED
========================================================= */

async function loadForYouFeed() {

    const container =
        $("#videoFeed");

    if (!container) {
        return;
    }


    container.innerHTML = `
        <div class="loading-box">

            <div class="loading-spinner"></div>

            <div>
                Loading For You...
            </div>

        </div>
    `;


    try {

        const {
            response,
            data
        } =
            await apiRequest(
                "/api/feed/for-you"
            );


        if (!response.ok) {

            throw new Error(
                data.error ||
                "Could not load For You."
            );

        }


        renderVideos(
            container,
            data.videos || []
        );


    } catch (
        error
    ) {

        container.innerHTML = `
            <div class="empty-box">

                <div>
                    
                </div>

                <div>
                    Could not load For You.
                </div>

                <div>
                    ${escapeHtml(
                        error.message
                    )}
                </div>

                <button
                    class="primary-button"
                    onclick="loadForYouFeed()"
                >
                    Retry
                </button>

            </div>
        `;

    }

}


/* =========================================================
   RENDER VIDEOS
========================================================= */

function renderVideos(
    container,
    videos
) {

    container.innerHTML = "";

    if (
        !videos.length
    ) {

        container.innerHTML = `
            <div class="empty-box">
                <div style="font-size:35px">
                    #🎬
                </div>

                <div>
                    No videos yet.
                </div>

                <div>
                    Be the first creator!
                </div>

                <button
                    class="primary-button"
                    onclick="showScreen('create')"
                >
                    Upload a video
                </button>
            </div>
        `;

        return;

    }

    videos.forEach(
        video => {

            container.appendChild(
                createVideoCard(
                    video
                )
            );

        }
    );

}


/* =========================================================
   VIDEO CARD
========================================================= */

function createVideoCard(
    video
) {

    const card =
        document.createElement(
            "article"
        );

    card.className =
        "video-card";

    const creator =
        video.creator || {};

    const videoUrl =
        video.video_url
            ? api(
                video.video_url
            )
            : "";

    const thumbnail =
        video.source === "youtube"
        ?
        `https://img.youtube.com/vi/${video.youtube_id}/hqdefault.jpg`
        :
        (
            video.thumbnail
            ?
            api(video.thumbnail)
            :
            ""
        );

    const isYouTube =
        video.source === "youtube";

    card.innerHTML = `
        

        ${
            video.boosted
            ? `
                <div class="boosted-label">
                    #🚀 Creator Boost
                </div>
            `
            : ""
        }

        <div
            class="video-preview"
            data-video-id="${video.id}"
            data-source="${video.source || 'creator'}"
            data-youtube-id="${video.youtube_id || ''}"
        >

        ${
            thumbnail
            ? `
                <img
                    src="${escapeAttribute(
                        thumbnail
                    )}"
                    alt=""
                    class="video-thumbnail-image"
                >
            `
            : `
                <div
                    class="random-thumbnail"
                    data-video-id="${video.id}"
                >
        
                    <div class="random-thumbnail-icon">
                        ${getRandomThumbnailIcon(
                            video.id
                        )}
                    </div>
        
                    <div class="random-thumbnail-title">
                        ${escapeHtml(
                            video.title ||
                            "Creator Video"
                        )}
                    </div>
        
                </div>
            `
        }

            <div class="video-play">
                ▶
            </div>

        </div>

        <div class="video-info">

            <h2 class="video-title">
                ${escapeHtml(
                    video.title ||
                    "Untitled"
                )}
            </h2>

            <div
                class="video-creator creator-clickable"
                data-creator="${escapeAttribute(
                    creator.username ||
                    "creator"
                )}"
            >
            
                @${escapeHtml(
                    creator.username ||
                    "creator"
                )}
        
            </div>

            <div class="video-stats">

                👁 ${Number(
                    video.views || 0
                )}

                &nbsp;&nbsp;

                ❤️ ${Number(
                    video.likes || 0
                )}

                &nbsp;&nbsp;

                💬 ${Number(
                    video.comments || 0
                )}

            </div>

            ${
                video.description
                ? `
                    <div class="video-description">

                        ${escapeHtml(
                            video.description
                        )}

                    </div>
                `
                : ""
            }

        </div>

    `;

    const preview =
        card.querySelector(
            ".video-preview"
        );

    if(
        isYouTube &&
        video.youtube_id
    ){
    
        preview.dataset.youtube =
            video.youtube_id;
    
    }

    preview.addEventListener(
        "click",
        () => {

            console.log("CLICK DATA FULL", JSON.stringify(video, null, 2));

            openVideo(
                video
            );

        }
    );

    

    const creatorElement =
    card.querySelector(
        ".creator-clickable"
    );

    if (creatorElement) {

        creatorElement.addEventListener(
            "click",
            event => {

                event.stopPropagation();

                openCreatorProfile(
                    creatorElement.dataset.creator
                );

            }
        );

    }

    return card;

}


async function enterVideoFullscreen(element) {

    if (!element) {
        return;
    }

    try {

        if (element.requestFullscreen) {

            await element.requestFullscreen();

        } 
        else if (element.webkitRequestFullscreen) {

            await element.webkitRequestFullscreen();

        }


        if (screen.orientation) {

            try {

                await screen.orientation.lock(
                    "landscape"
                );

            } catch(error) {

                console.log(
                    "Orientation lock unavailable",
                    error
                );

            }

        }

    } catch(error) {

        console.log(
            "Fullscreen error:",
            error
        );

    }

}



/* =========================================================
   OPEN VIDEO
========================================================= */

async function openVideo(
    video
) {

    console.log("VIDEO DATA:", video);

    state.currentVideo =
        video;

    if(video.source === "youtube"){

        openYoutubeVideo(video);

        return;

    }

    let finalVideo =
        video;

    try {

        const {
            response,
            data
        } =
            await apiRequest(
                "/api/videos/" +
                video.id
            );

        if (
            response.ok
        ) {

            finalVideo =
                data;

        }

    } catch (
        error
    ) {

        console.log(
            "Video details error:",
            error
        );

    }

    state.currentVideo =
        finalVideo;

    const player =
        $("#mainVideo");

    const videoUrl =
        finalVideo.video_url
            ? api(
                finalVideo.video_url
            )
            : "";

    player.src =
        videoUrl;



    player.load();


    showScreen(
        "player"
    );


    // Open fullscreen on mobile
    setTimeout(() => {

        enterVideoFullscreen(
            player
        );

    }, 300);



    $("#playerHeaderTitle")
        .textContent =
        finalVideo.title ||
        "Video";

    $("#playerTitle")
        .textContent =
        finalVideo.title ||
        "Video";

    const creator =
        finalVideo.creator || {};

    $("#playerCreator")
        .textContent =
        "@" +
        (
            creator.username ||
            "creator"
        );

    $("#playerStats")
        .innerHTML = `

        👁 ${Number(
            finalVideo.views || 0
        )}

        &nbsp;&nbsp;

        ❤️ ${Number(
            finalVideo.likes || 0
        )}

        &nbsp;&nbsp;

        💬 ${Number(
            finalVideo.comments || 0
        )}

    `;

    $("#playerDescription")
        .textContent =
        finalVideo.description ||
        "";

    showScreen(
        "player"
    );

}


async function enterVideoFullscreen(element) {

    if (!element) {
        return;
    }

    try {

        if (element.requestFullscreen) {

            await element.requestFullscreen();

        } 
        else if (element.webkitRequestFullscreen) {

            await element.webkitRequestFullscreen();

        }


        if (screen.orientation) {

            try {

                await screen.orientation.lock(
                    "landscape"
                );

            } catch(error) {

                console.log(
                    "Orientation lock not supported"
                );

            }

        }

    } catch(error) {

        console.log(
            "Fullscreen error:",
            error
        );

    }

}


function openYoutubeVideo(video){

    state.currentVideo =
        video;


    const player =
        $("#mainVideo");


    player.style.display =
        "none";


    let iframe =
        document.querySelector(
            "#youtubePlayer"
        );


    if(!iframe){

        iframe =
            document.createElement(
                "iframe"
            );

        iframe.id =
            "youtubePlayer";

        iframe.width =
            "100%";

        iframe.height =
            "100%";

        iframe.frameBorder =
            "0";

        iframe.allowFullscreen =
            true;

        iframe.allow =
        "accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture";
        
        iframe.referrerPolicy =
            "strict-origin-when-cross-origin";


        player.parentElement.appendChild(
            iframe
        );

    }


    iframe.src =
        "https://www.youtube.com/embed/" +
        video.youtube_id +
        "?enablejsapi=1&origin=" +
        encodeURIComponent(window.location.origin);

    $("#playerHeaderTitle")
        .textContent =
        video.title ||
        "YouTube Video";


    $("#playerTitle")
        .textContent =
        video.title ||
        "YouTube Video";


    const creator =
        video.creator || {};


    $("#playerCreator")
        .textContent =
        "@" +
        (
            creator.username ||
            "youtube"
        );


    $("#playerDescription")
        .textContent =
        video.description ||
        "";


    showScreen(
        "player"
    );
    
    
    // fullscreen YouTube player
    setTimeout(() => {
    
        enterVideoFullscreen(
            iframe
        );
    
    }, 500);

}



/* =========================================================
   COMMENTS
========================================================= */

async function loadComments() {

    if (
        !state.currentVideo
    ) {

        return;

    }

    const list =
        $("#commentsList");

    list.innerHTML =
        "Loading comments...";

    try {

        const {
            response,
            data
        } =
            await apiRequest(
                "/api/videos/" +
                state.currentVideo.id +
                "/comments"
            );

        if (
            !response.ok
        ) {

            throw new Error(
                data.error ||
                "Could not load comments."
            );

        }

        if (
            !data.length
        ) {

            list.innerHTML = `
                <div
                    style="
                        color:#858c99;
                        padding:10px;
                    "
                >
                    No comments yet.
                </div>
            `;

            return;

        }

        list.innerHTML = "";

        data.forEach(
            comment => {

                const item =
                    document.createElement(
                        "div"
                    );

                item.className =
                    "comment-item";

                item.innerHTML = `

                    <div class="comment-user">

                        @${escapeHtml(
                            comment.username ||
                            "user"
                        )}

                    </div>

                    <div class="comment-text">

                        ${escapeHtml(
                            comment.text
                        )}

                    </div>

                `;

                list.appendChild(
                    item
                );

            }
        );

    } catch (
        error
    ) {

        list.innerHTML =
            "Could not load comments.";

    }

}


/* =========================================================
   SEND COMMENT
========================================================= */

async function sendComment() {

    if (
        !state.currentVideo
    ) {

        return;

    }

    if (
        !state.token
    ) {

        showToast(
            "Login to comment."
        );

        showScreen(
            "login"
        );

        return;

    }

    const input =
        $("#commentInput");

    const text =
        input.value.trim();

    if (!text) {

        return;

    }

    const {
        response,
        data
    } =
        await apiRequest(
            "/api/videos/" +
            state.currentVideo.id +
            "/comments",
            {
                method: "POST",

                headers: {
                    "Content-Type":
                        "application/json"
                },

                body:
                    JSON.stringify({
                        text
                    })
            }
        );

    if (
        response.status === 201
    ) {

        input.value = "";

        showToast(
            "Comment added."
        );

        loadComments();

    } else {

        showToast(
            data.error ||
            "Could not add comment."
        );

    }

}


/* =========================================================
   LIKE
========================================================= */

async function likeCurrentVideo() {

    if (
        !state.currentVideo
    ) {

        return;

    }

    if (
        !state.token
    ) {

        showToast(
            "Login to like videos."
        );

        showScreen(
            "login"
        );

        return;

    }

    const {
        response,
        data
    } =
        await apiRequest(
            "/api/videos/" +
            state.currentVideo.id +
            "/like",
            {
                method: "POST"
            }
        );

    if (
        response.ok
    ) {

        state.currentVideo.likes =
            data.likes;

        $("#playerStats")
            .innerHTML = `

            👁 ${Number(
                state.currentVideo.views ||
                0
            )}

            &nbsp;&nbsp;

            ❤️ ${Number(
                data.likes ||
                0
            )}

            &nbsp;&nbsp;

            💬 ${Number(
                state.currentVideo.comments ||
                0
            )}

        `;

        $("#likeButton")
            .textContent =
            data.liked
                ? "❤️ Liked"
                : "❤️ Like";

    } else {

        showToast(
            data.error ||
            "Could not like video."
        );

    }

}


/* =========================================================
   SEARCH
========================================================= */

async function performSearch() {

    const input =
        $("#searchInput");

    const query =
        input.value.trim();

    const results =
        $("#searchResults");

    if (!query) {

        results.innerHTML = `
            <div class="empty-box">
                Type something to search.
            </div>
        `;

        return;

    }

    results.innerHTML = `
        <div class="loading-box">
            <div class="loading-spinner"></div>
            <div>Searching...</div>
        </div>
    `;

    try {

        const {
            response,
            data
        } =
            await apiRequest(
                "/api/videos?q=" +
                encodeURIComponent(
                    query
                )
            );

        if (
            !response.ok
        ) {

            throw new Error(
                data.error ||
                "Search failed."
            );

        }

        renderVideos(
            results,
            data.videos || []
        );

    } catch (
        error
    ) {

        results.innerHTML = `
            <div class="empty-box">

                ${escapeHtml(
                    error.message
                )}

            </div>
        `;

    }

}


/* =========================================================
   LOGIN
========================================================= */

async function login() {

    const loginValue =
        $("#loginValue")
            .value
            .trim();

    const password =
        $("#loginPassword")
            .value;

    const status =
        $("#loginStatus");

    if (
        !loginValue ||
        !password
    ) {

        status.textContent =
            "Enter your login and password.";

        return;

    }

    status.textContent =
        "Logging in...";

    try {

        const {
            response,
            data
        } =
            await apiRequest(
                "/api/auth/login",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body:
                        JSON.stringify({
                            login:
                                loginValue,

                            password:
                                password
                        })
                }
            );

        if (
            response.ok
        ) {

            saveLogin(
                data.token,
                data.user
            );

            status.textContent =
                "";

            $("#loginPassword")
                .value = "";

            updateProfileUI();

            showToast(
                "Login successful."
            );

            showScreen(
                "home"
            );

        } else {

            status.textContent =
                data.error ||
                "Login failed.";

        }

    } catch (
        error
    ) {

        status.textContent =
            error.message;

    }

}


/* =========================================================
   REGISTER
========================================================= */

async function register() {

    const username =
        $("#registerUsername")
            .value
            .trim();

    const email =
        $("#registerEmail")
            .value
            .trim();

    const displayName =
        $("#registerDisplayName")
            .value
            .trim();

    const password =
        $("#registerPassword")
            .value;

    const status =
        $("#registerStatus");

    if (
        !username ||
        !email ||
        !password
    ) {

        status.textContent =
            "Username, email and password are required.";

        return;

    }

    status.textContent =
        "Creating account...";

    try {

        const {
            response,
            data
        } =
            await apiRequest(
                "/api/auth/register",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body:
                        JSON.stringify({

                            username,

                            email,

                            display_name:
                                displayName,

                            password

                        })
                }
            );

        if (
            response.status === 201
        ) {

            saveLogin(
                data.token,
                data.user
            );

            status.textContent =
                "";

            updateProfileUI();

            showToast(
                "Welcome to Creator!"
            );

            showScreen(
                "home"
            );

        } else {

            status.textContent =
                data.error ||
                "Could not create account.";

        }

    } catch (
        error
    ) {

        status.textContent =
            error.message;

    }

}


/* =========================================================
   PROFILE
========================================================= */

async function loadProfile() {

    updateProfileUI();

    if (
        !state.token
    ) {

        return;

    }

    const username =
        state.user &&
        state.user.username;

    if (!username) {

        return;

    }

    try {

        const {
            response,
            data
        } =
            await apiRequest(
                "/api/users/" +
                encodeURIComponent(
                    username
                )
            );

        if (
            response.ok
        ) {

            const user =
                data.user || {};

            $("#profileVideos")
                .textContent =
                data.videos
                    ? data.videos.length
                    : 0;

            $("#profileFollowers")
                .textContent =
                user.followers ||
                0;

            $("#profileFollowing")
                .textContent =
                user.following ||
                0;

            renderVideos(
                $("#profileVideosList"),
                data.videos || []
            );

        }

    } catch (
        error
    ) {

        console.log(
            "Profile error:",
            error
        );

    }

}


/* =========================================================
   UPDATE PROFILE UI
========================================================= */

function updateProfileUI() {

    if (
        state.user &&
        state.token
    ) {

        $("#profileUsername")
            .textContent =
            "@" +
            (
                state.user.username ||
                "creator"
            );

        $("#profileDisplayName")
            .textContent =
            state.user.display_name ||
            "Creator";

        $("#profileBio")
            .textContent =
            state.user.bio ||
            "No bio yet.";

        $("#profileLoginButton")
            .textContent =
            "LOGOUT";

    } else {

        $("#profileUsername")
            .textContent =
            "@guest";

        $("#profileDisplayName")
            .textContent =
            "Guest";

        $("#profileBio")
            .textContent =
            "Login to see your creator profile.";

        $("#profileLoginButton")
            .textContent =
            "LOGIN";

        $("#profileVideos")
            .textContent =
            "0";

        $("#profileFollowers")
            .textContent =
            "0";

        $("#profileFollowing")
            .textContent =
            "0";

    }

}

/* =========================================================
   UPLOAD
========================================================= */

function setupUpload() {

    const input =
        $("#videoFileInput");

    const fileText =
        $("#selectedFileText");

    input.addEventListener(
        "change",
        () => {

            const file =
                input.files[0];

            if (!file) {

                fileText.textContent =
                    "MP4, WebM, MOV and other video formats";

                return;

            }

            const size =
                (
                    file.size /
                    1024 /
                    1024
                ).toFixed(
                    1
                );

            fileText.textContent =
                file.name +
                " • " +
                size +
                " MB";

        }
    );

    /* -------------------------------------------------------
       THUMBNAIL SELECTION
    ------------------------------------------------------- */

    const thumbnailInput =
        $("#thumbnailFileInput");

    const thumbnailText =
        $("#thumbnailFileText");

    const thumbnailPreview =
        $("#thumbnailPreview");

    const thumbnailPreviewImage =
        $("#thumbnailPreviewImage");


    thumbnailInput.addEventListener(
        "change",
        () => {

            const file =
                thumbnailInput.files[0];

            if (!file) {

                thumbnailText.textContent =
                    "Optional — JPG, PNG or WebP";

                thumbnailPreview.classList.add(
                    "hidden"
                );

                thumbnailPreviewImage.src =
                    "";

                return;
            }


            thumbnailText.textContent =
                file.name;


            const reader =
                new FileReader();


            reader.onload =
                event => {

                    thumbnailPreviewImage.src =
                        event.target.result;

                    thumbnailPreview.classList.remove(
                        "hidden"
                    );

                };


            reader.readAsDataURL(
                file
            );

        }
    );

}


/* =========================================================
   VIDEO UPLOAD WITH PROGRESS
========================================================= */
let isShort = false;
function uploadVideo() {

    if (
        !state.token
    ) {

        showToast(
            "Login before uploading."
        );

        showScreen(
            "login"
        );

        return;

    }

    const file =
        $("#videoFileInput")
            .files[0];
    const thumbnailFile =
        $("#thumbnailFileInput")
            .files[0];

    const title =
        $("#videoTitleInput")
            .value
            .trim();

    const description =
        $("#videoDescriptionInput")
            .value
            .trim();

    const status =
        $("#uploadStatus");

    if (!file) {

        status.textContent =
            "Choose a video first.";

        return;

    }

    if (!title) {

        status.textContent =
            "Enter a video title.";

        return;

    }

    const formData =
        new FormData();

    formData.append(
        "video",
        file
    );

    let type = "video";


    if(
        document.getElementById("shortsCheckbox").checked
    ){
        type = "short";
    }


    formData.append(
        "content_type",
        type
    );
    
    formData.append(
        "title",
        title
    );
    
    formData.append(
        "description",
        description
    );

    // formData.append(
    //     "is_short",
    //     isShort ? "true" : "false"
    // );
    formData.append(
        "is_short",
        "true"
    );
    formData.append(
        "is_short",
        "false"
    );
    
    if (thumbnailFile) {
    
        formData.append(
            "thumbnail",
            thumbnailFile
        );
    
    }

    const xhr =
        new XMLHttpRequest();

    xhr.open(
        "POST",
        api(
            "/api/videos"
        )
    );

    xhr.setRequestHeader(
        "Authorization",
        "Bearer " +
        state.token
    );

    $(".upload-progress")
        .classList.remove(
            "hidden"
        );

    status.textContent =
        "";

    $("#uploadProgressBar")
        .style.width =
        "0%";

    xhr.upload.addEventListener(
        "progress",
        event => {

            if (
                event.lengthComputable
            ) {

                const percent =
                    (
                        event.loaded /
                        event.total
                    ) *
                    100;

                $("#uploadProgressBar")
                    .style.width =
                    percent +
                    "%";

                $("#uploadProgressText")
                    .textContent =
                    "Uploading " +
                    Math.round(
                        percent
                    ) +
                    "%";

            }

        }
    );

    xhr.addEventListener(
        "load",
        () => {

            $(".upload-progress")
                .classList.add(
                    "hidden"
                );

            let data = {};

            try {

                data =
                    JSON.parse(
                        xhr.responseText
                    );

            } catch (
                error
            ) {}

            if (
                xhr.status === 201
            ) {

                status.textContent =
                    "Video uploaded successfully!";

                $("#videoFileInput")
                    .value = "";

                $("#videoTitleInput")
                    .value = "";

                $("#videoDescriptionInput")
                    .value = "";

                $("#selectedFileText")
                    .textContent =
                    "MP4, WebM, MOV and other video formats";
         

                $("#thumbnailFileInput")
                .value = "";
                
                $("#thumbnailFileText")
                    .textContent =
                    "Optional — JPG, PNG or WebP";
                
                $("#thumbnailPreview")
                    .classList.add(
                        "hidden"
                    );
                
                $("#thumbnailPreviewImage")
                    .src = "";


                showToast(
                    "Video uploaded!"
                );

                setTimeout(
                    () => {

                        showScreen(
                            "home"
                        );

                    },
                    700
                );

            } else {

                status.textContent =
                    data.error ||
                    "Upload failed.";

            }

        }
    );

    xhr.addEventListener(
        "error",
        () => {

            $(".upload-progress")
                .classList.add(
                    "hidden"
                );

            status.textContent =
                "Network error during upload.";

        }
    );

    xhr.send(
        formData
    );

}


/* =========================================================
   SHARE
========================================================= */

async function shareVideo() {

    if (
        !state.currentVideo
    ) {

        return;

    }

    const url =
        window.location.origin +
        "/media/" +
        state.currentVideo.video_url
            .replace(
                "/media/",
                ""
            );

    if (
        navigator.share
    ) {

        try {

            await navigator.share({

                title:
                    state.currentVideo.title,

                text:
                    state.currentVideo.description ||
                    "Check out this video!",

                url

            });

        } catch (
            error
        ) {

            // User cancelled share.

        }

    } else {

        try {

            await navigator.clipboard.writeText(
                window.location.origin +
                state.currentVideo.video_url
            );

            showToast(
                "Video link copied."
            );

        } catch (
            error
        ) {

            showToast(
                "Sharing is not supported here."
            );

        }

    }

}


/* =========================================================
   HTML SAFETY
========================================================= */

function escapeHtml(
    value
) {

    return String(
        value
    )
        .replace(
            /&/g,
            "&amp;"
        )
        .replace(
            /</g,
            "&lt;"
        )
        .replace(
            />/g,
            "&gt;"
        )
        .replace(
            /"/g,
            "&quot;"
        )
        .replace(
            /'/g,
            "&#039;"
        );

}

function escapeAttribute(
    value
) {

    return escapeHtml(
        value
    );

}


/* =========================================================
   EVENT LISTENERS
========================================================= */

function setupNavigation() {

    $all(
        ".nav-button, .nav-create-button"
    )
        .forEach(
            button => {

                button.addEventListener(
                    "click",
                    () => {

                        showScreen(
                            button.dataset.screen
                        );

                    }
                );

            }
        );

}


function setupTopButtons() {

    $("#searchTopButton")
        .addEventListener(
            "click",
            () => {

                showScreen(
                    "search"
                );

                $("#searchInput")
                    .focus();

            }
        );

    $("#profileTopButton")
        .addEventListener(
            "click",
            () => {

                showScreen(
                    "profile"
                );

            }
        );

}


function setupTabs() {

    $all(
        ".feed-tab"
    )
        .forEach(
            button => {

                button.addEventListener(
                    "click",
                    () => {

                        $all(
                            ".feed-tab"
                        )
                            .forEach(
                                item =>
                                item.classList.remove(
                                    "active"
                                )
                            );

                        button.classList.add(
                            "active"
                        );

                        if (
                            button.dataset.feed ===
                            "for-you"
                        ) {
                        
                            loadForYouFeed();
                        
                        }
                        
                        
                        else if (
                            button.dataset.feed ===
                            "following"
                        ) {
                        
                            loadFollowingFeed();
                        
                        }
                        
                        
                        else if (
                            button.dataset.feed ===
                            "trending"
                        ) {
                        
                            loadTrendingFeed();
                        
                        }

                    }
                );

            }
        );

}


function setupButtons() {

    $("#searchBackButton")
        .addEventListener(
            "click",
            () => {
                showScreen(
                    "home"
                );
            }
        );

    $("#playerBackButton")
        .addEventListener(
            "click",
            () => {

                const video =
                    $("#mainVideo");

                video.pause();

                video.removeAttribute(
                    "src"
                );

                video.load();

                showScreen(
                    "home"
                );

            }
        );

    $("#searchButton")
        .addEventListener(
            "click",
            performSearch
        );

    $("#searchInput")
        .addEventListener(
            "keydown",
            event => {

                if (
                    event.key ===
                    "Enter"
                ) {

                    performSearch();

                }

            }
        );

    $("#likeButton")
        .addEventListener(
            "click",
            likeCurrentVideo
        );

    $("#commentButton")
        .addEventListener(
            "click",
            () => {

                const panel =
                    $("#commentsPanel");

                panel.classList.toggle(
                    "hidden"
                );

                if (
                    !panel.classList.contains(
                        "hidden"
                    )
                ) {

                    loadComments();

                }

            }
        );

    $("#sendCommentButton")
        .addEventListener(
            "click",
            sendComment
        );

    $("#commentInput")
        .addEventListener(
            "keydown",
            event => {

                if (
                    event.key ===
                    "Enter"
                ) {

                    sendComment();

                }

            }
        );

    $("#shareButton")
        .addEventListener(
            "click",
            shareVideo
        );

    $("#loginButton")
        .addEventListener(
            "click",
            login
        );

    $("#registerButton")
        .addEventListener(
            "click",
            register
        );

    $("#openRegisterButton")
        .addEventListener(
            "click",
            () => {

                showScreen(
                    "register"
                );

            }
        );

    $("#openLoginButton")
        .addEventListener(
            "click",
            () => {

                showScreen(
                    "login"
                );

            }
        );

    $("#profileLoginButton")
        .addEventListener(
            "click",
            () => {

                if (
                    state.token
                ) {

                    logoutLocal();

                    showToast(
                        "Logged out."
                    );

                    updateProfileUI();

                } else {

                    showScreen(
                        "login"
                    );

                }

            }
        );

    $("#uploadVideoButton")
        .addEventListener(
            "click",
            uploadVideo
        );
    

    $("#openStudioButton")
    .addEventListener(
        "click",
        () => {

            showScreen(
                "studio"
            );

        }
    );

    $("#studioBackButton")
        .addEventListener(
            "click",
            () => {

                showScreen(
                    "profile"
                );

            }
        );

    $("#studioUploadButton")
        .addEventListener(
            "click",
            () => {

                showScreen(
                    "create"
                );

            }
        );


    $("#markNotificationsRead")
    .addEventListener(
        "click",
        async () => {

            if (!state.token) {
                return;
            }

            await apiRequest(
                "/api/notifications/read",
                {
                    method:
                        "POST"
                }
            );

            loadNotifications();

            showToast(
                "Notifications marked as read."
            );

        }
    );

    /* =====================================================
       PUBLIC CREATOR PROFILE
    ====================================================== */

    const creatorProfileBackButton =
        $("#creatorProfileBackButton");

    if (
        creatorProfileBackButton
    ) {

        creatorProfileBackButton
            .addEventListener(
                "click",
                () => {

                    showScreen(
                        "home"
                    );

                }
            );

    }


    const creatorFollowButton =
        $("#creatorFollowButton");

    if (
        creatorFollowButton
    ) {

        creatorFollowButton
            .addEventListener(
                "click",
                toggleCreatorFollow
            );

    }


}


/* =========================================================
   INITIALIZATION
========================================================= */

function initializeApp() {

    setupNavigation();

    setupTopButtons();

    setupTabs();

    setupButtons();

    setupUpload();

    updateProfileUI();

    showScreen(
        "home"
    );

}


document.addEventListener(
    "DOMContentLoaded",
    initializeApp
);

/* =========================================================
   CREATOR STUDIO
========================================================= */

async function loadCreatorStudio() {

    if (!state.token) {

        showToast(
            "Login to access Creator Studio."
        );

        showScreen(
            "login"
        );

        return;
    }

    $("#studioVideos")
        .textContent = "—";

    $("#studioViews")
        .textContent = "—";

    $("#studioLikes")
        .textContent = "—";

    $("#studioFollowers")
        .textContent = "—";

    $("#studioVideosList")
        .innerHTML = `
            <div class="loading-box">
                <div class="loading-spinner"></div>
                <div>Loading studio...</div>
            </div>
        `;

    try {

        const {
            response,
            data
        } = await apiRequest(
            "/api/creator/studio"
        );

        if (!response.ok) {

            throw new Error(
                data.error ||
                "Could not load Creator Studio."
            );
        }

        const analytics =
            data.analytics || {};

        $("#studioVideos")
            .textContent =
            Number(
                analytics.videos || 0
            );

        $("#studioViews")
            .textContent =
            Number(
                analytics.views || 0
            );

        $("#studioLikes")
            .textContent =
            Number(
                analytics.likes || 0
            );

        $("#studioFollowers")
            .textContent =
            Number(
                analytics.followers || 0
            );

        renderStudioVideos(
            data.videos || []
        );

    } catch (error) {

        $("#studioVideosList")
            .innerHTML = `
                <div class="empty-box">
                    ${escapeHtml(
                        error.message
                    )}
                </div>
            `;
    }
}


/* =========================================================
   RENDER STUDIO VIDEOS
========================================================= */

function renderStudioVideos(
    videos
) {

    const container =
        $("#studioVideosList");

    container.innerHTML = "";

    if (!videos.length) {

        container.innerHTML = `
            <div class="empty-box">

                🎬

                <div>
                    You haven't uploaded any videos yet.
                </div>

            </div>
        `;

        return;
    }

    videos.forEach(
        video => {

            const item =
                document.createElement(
                    "div"
                );

            item.className =
                "studio-video-item";

            const thumbnail =
                video.thumbnail
                    ? api(
                        video.thumbnail
                    )
                    : "";

            item.innerHTML = `

                <div class="studio-video-thumb">

                    ${
                        thumbnail
                        ? `
                            <img
                                src="${escapeAttribute(
                                    thumbnail
                                )}"
                                alt=""
                            >
                        `
                        : `
                            🎬
                        `
                    }

                </div>

                <div class="studio-video-info">

                    <div class="studio-video-title">

                        ${escapeHtml(
                            video.title ||
                            "Untitled"
                        )}

                    </div>

                    <div class="studio-video-stats">

                        👁 ${Number(
                            video.views || 0
                        )}

                        &nbsp; ❤️ ${Number(
                            video.likes || 0
                        )}

                        &nbsp; 💬 ${Number(
                            video.comments || 0
                        )}

                    </div>

                    <button
                        class="studio-delete"
                        data-video-id="${video.id}"
                    >
                        Manage video
                    </button>

                    <button 
                        class="delete-video-btn"
                        onclick="deleteVideo(${video.id})">
                        🗑 Delete
                    </button>

                </div>

                

            `;

            const manage =
                item.querySelector(
                    ".studio-delete"
                );

            manage.addEventListener(
                "click",
                () => {

                    openVideo(
                        video
                    );

                }
            );

            container.appendChild(
                item
            );

        }
    );
}

/* =========================================================
   SHORTS SYSTEM
========================================================= */

let shortsVideos = [];

let shortsObserver = null;

let viewedShorts = new Set();

let currentShortVideo = null;


/* =========================================================
   LOAD SHORTS
========================================================= */

async function loadShorts() {

    const feed = $("#shortsFeed");

    if (!feed) {
        return;
    }

    feed.innerHTML = `
        <div class="shorts-loading">

            <div class="loading-spinner"></div>

            <div>
                Loading Shorts...
            </div>

        </div>
    `;

    try {

        const {
            response,
            data
        } = await apiRequest(
            "/api/videos"
        );

        if (!response.ok) {

            throw new Error(
                data.error ||
                "Could not load Shorts."
            );

        }

        shortsVideos =
            data.videos || [];

        renderShorts(
            shortsVideos
        );

    } catch (error) {

        console.error(
            "Shorts loading error:",
            error
        );

        feed.innerHTML = `
            <div class="shorts-loading">

                <div
                    style="font-size:40px"
                >
                    ❌
                </div>

                <div>
                    Could not load Shorts.
                </div>

                <div
                    style="
                        color:#777f8c;
                        font-size:12px;
                        margin-top:5px;
                        text-align:center;
                        padding:0 20px;
                    "
                >
                    ${escapeHtml(
                        error.message
                    )}
                </div>

                <button
                    class="primary-button"
                    style="
                        width:200px;
                        margin-top:12px;
                    "
                    onclick="loadShorts()"
                >
                    Retry
                </button>

            </div>
        `;

    }

}


/* =========================================================
   RENDER SHORTS
========================================================= */

function renderShorts(
    videos
) {

    const feed =
        $("#shortsFeed");

    if (!feed) {
        return;
    }

    feed.innerHTML = "";

    if (!videos.length) {

        feed.innerHTML = `
            <div class="shorts-loading">

                <div
                    style="font-size:45px"
                >
                    🎬
                </div>

                <div>
                    No Shorts yet.
                </div>

                <button
                    class="primary-button"
                    style="
                        width:220px;
                        margin-top:10px;
                    "
                    onclick="showScreen('create')"
                >
                    Upload a Video
                </button>

            </div>
        `;

        return;
    }

    videos.forEach(
        video => {

            const short =
                createShortItem(
                    video
                );

            feed.appendChild(
                short
            );

        }
    );

    setupShortObserver();

}


/* =========================================================
   CREATE SHORT ITEM
========================================================= */

function createShortItem(
    video
) {

    const item =
        document.createElement(
            "article"
        );

    item.className =
        "short-item";

    item.dataset.videoId =
        video.id;

    const creator =
        video.creator || {};

    const videoUrl =
        video.video_url
            ? api(
                video.video_url
            )
            : "";

    item.innerHTML = `

        <video
            class="short-video"
            src="${escapeAttribute(
                videoUrl
            )}"
            playsinline
            muted
            loop
            preload="metadata"
        ></video>
        
        <div
            class="short-play-overlay"
            data-play-overlay
        >
            ▶
        </div>
        
        <div class="short-progress">
            <div
                class="short-progress-bar"
                data-progress
            ></div>
        </div>


        <div
            class="short-gradient"
        ></div>


        <button
            class="short-mute-button"
            data-action="mute"
        >
            🔇
        </button>


        <div class="short-actions">

            <button
                class="short-action"
                data-action="like"
            >

                <span
                    class="short-action-icon"
                >
                    ❤️
                </span>

                <span
                    class="short-action-count"
                    data-like-count
                >
                    ${Number(
                        video.likes || 0
                    )}
                </span>

            </button>


            <button
                class="short-action"
                data-action="comment"
            >

                <span
                    class="short-action-icon"
                >
                    💬
                </span>

                <span
                    class="short-action-count"
                >
                    ${Number(
                        video.comments || 0
                    )}
                </span>

            </button>


            <button
                class="short-action"
                data-action="share"
            >

                <span
                    class="short-action-icon"
                >
                    ↗
                </span>

                <span
                    class="short-action-count"
                >
                    Share
                </span>

            </button>

        </div>


        <div class="short-bottom-info">

            <div class="short-creator">

                @${escapeHtml(
                    creator.username ||
                    "creator"
                )}

            </div>


            <div class="short-title">

                ${escapeHtml(
                    video.title ||
                    "Untitled"
                )}

            </div>


            ${
                video.description
                ? `
                    <div
                        class="short-description"
                    >
                        ${escapeHtml(
                            video.description
                        )}
                    </div>
                `
                : ""
            }

        </div>

    `;


    const videoElement =
        item.querySelector(
            ".short-video"
        );

    const progressBar =
    item.querySelector(
        "[data-progress]"
    );
    
    videoElement.addEventListener(
        "timeupdate",
        () => {
    
            if (
                !progressBar ||
                !videoElement.duration
            ) {
                return;
            }
    
            const percent =
                (
                    videoElement.currentTime /
                    videoElement.duration
                ) * 100;
    
            progressBar.style.width =
                percent + "%";
    
        }
    );


    /* =====================================================
    TAP VIDEO = PLAY / PAUSE
    ===================================================== */

    let lastShortTap = 0;

    videoElement.addEventListener(
        "click",
        () => {

            const currentTime =
                Date.now();

            const isDoubleTap =
                currentTime -
                lastShortTap <
                300;

            lastShortTap =
                currentTime;


            /*
            * DOUBLE TAP = LIKE
            */
            if (
                isDoubleTap
            ) {

                likeShort(
                    video,
                    item
                );

                showDoubleLike(
                    item
                );

                return;

            }


            /*
            * SINGLE TAP = PLAY / PAUSE
            */
            if (
                videoElement.paused
            ) {

                playShort(
                    item
                );

            } else {

                videoElement.pause();

                updatePlayOverlay(
                    item,
                    true
                );

            }

        }
    );


    /*
     * Mute button
     */

    item.querySelector(
        "[data-action='mute']"
    )
    .addEventListener(
        "click",
        event => {

            event.stopPropagation();

            videoElement.muted =
                !videoElement.muted;

            updateMuteButton(
                item,
                videoElement
            );

        }
    );


    /*
     * Like
     */

    item.querySelector(
        "[data-action='like']"
    )
    .addEventListener(
        "click",
        event => {

            event.stopPropagation();

            likeShort(
                video,
                item
            );

        }
    );


    /*
     * Comments
     */

    item.querySelector(
        "[data-action='comment']"
    )
    .addEventListener(
        "click",
        event => {

            event.stopPropagation();

            openShortComments(
                video
            );

        }
    );


    /*
     * Share
     */

    item.querySelector(
        "[data-action='share']"
    )
    .addEventListener(
        "click",
        event => {

            event.stopPropagation();

            shareShort(
                video
            );

        }
    );


    return item;

}


/* =========================================================
   MUTE BUTTON
========================================================= */

function updateMuteButton(
    item,
    video
) {

    const button =
        item.querySelector(
            "[data-action='mute']"
        );

    if (!button) {
        return;
    }

    button.textContent =
        video.muted
            ? "🔇"
            : "🔊";

}


/* =========================================================
   SHORTS OBSERVER
========================================================= */

function setupShortObserver() {

    if (
        shortsObserver
    ) {

        shortsObserver.disconnect();

    }

    const feed =
        $("#shortsFeed");

    if (!feed) {
        return;
    }


    shortsObserver =
        new IntersectionObserver(
            entries => {

                let bestEntry = null;

                entries.forEach(
                    entry => {

                        const item =
                            entry.target;

                        const video =
                            item.querySelector(
                                ".short-video"
                            );

                        if (!video) {
                            return;
                        }

                        if (
                            entry.isIntersecting
                        ) {

                            if (
                                !bestEntry ||
                                entry.intersectionRatio >
                                bestEntry.intersectionRatio
                            ) {

                                bestEntry =
                                    entry;

                            }

                        }

                    }
                );


                if (!bestEntry) {

                    document
                        .querySelectorAll(
                            "#shortsFeed .short-video"
                        )
                        .forEach(
                            video => {

                                video.pause();

                            }
                        );

                    return;

                }


                const activeItem =
                    bestEntry.target;


                document
                    .querySelectorAll(
                        "#shortsFeed .short-item"
                    )
                    .forEach(
                        item => {

                            if (
                                item !==
                                activeItem
                            ) {

                                pauseShort(
                                    item
                                );

                            }

                        }
                    );


                if (
                    bestEntry.intersectionRatio
                    >=
                    0.60
                ) {

                    playShort(
                        activeItem
                    );

                }

            },
            {
                root:
                    feed,

                threshold: [
                    0.25,
                    0.50,
                    0.60,
                    0.75,
                    0.90
                ]
            }
        );

}


/* =========================================================
   PLAY SHORT
========================================================= */

async function playShort(
    item
) {

    const video =
        item.querySelector(
            ".short-video"
        );

    if (!video) {
        return;
    }


    /*
     * Pause all other Shorts.
     */

    document
        .querySelectorAll(
            ".short-video"
        )
        .forEach(
            other => {

                if (
                    other !== video
                ) {

                    other.pause();

                }

            }
        );


    /*
     * Mobile autoplay normally works
     * when the video starts muted.
     */

    video.muted = true;

    updateMuteButton(
        item,
        video
    );


    try {

        await video.play();

        updatePlayOverlay(
            item,
            false
        );

    } catch (
        error
    ) {

        console.log(
            "Autoplay blocked:",
            error
        );

    }


    /*
     * Count view once per loaded Shorts session.
     */

    const videoId =
        Number(
            item.dataset.videoId
        );

    if (
        videoId &&
        !viewedShorts.has(
            videoId
        )
    ) {

        viewedShorts.add(
            videoId
        );

        countShortView(
            videoId
        );

    }

}


/* =========================================================
   PAUSE SHORT
========================================================= */

function pauseShort(
    item
) {

    const video =
        item.querySelector(
            ".short-video"
        );

    if (video) {

        video.pause();

        updatePlayOverlay(
            item,
            true
        );

    }

}


/* =========================================================
   COUNT SHORT VIEW
========================================================= */

async function countShortView(
    videoId
) {

    try {

        await apiRequest(
            "/api/videos/" +
            videoId
        );

    } catch (error) {

        console.log(
            "View counting error:",
            error
        );

    }

}


/* =========================================================
   LIKE SHORT
========================================================= */

async function likeShort(
    video,
    item
) {

    if (!state.token) {

        showToast(
            "Login to like videos."
        );

        showScreen(
            "login"
        );

        return;
    }


    try {

        const {
            response,
            data
        } =
            await apiRequest(
                "/api/videos/" +
                video.id +
                "/like",
                {
                    method:
                        "POST"
                }
            );


        if (!response.ok) {

            showToast(
                data.error ||
                "Could not like video."
            );

            return;
        }


        const count =
            item.querySelector(
                "[data-like-count]"
            );

        if (count) {

            count.textContent =
                Number(
                    data.likes || 0
                );

        }


        showToast(
            data.liked
                ? "Liked ❤️"
                : "Like removed"
        );


    } catch (error) {

        console.log(
            error
        );

        showToast(
            "Connection error."
        );

    }

}


/* =========================================================
   SHORT COMMENTS
========================================================= */

async function openShortComments(
    video
) {

    currentShortVideo =
        video;

    const panel =
        $("#shortCommentsPanel");

    if (!panel) {
        return;
    }

    panel.classList.remove(
        "hidden"
    );

    await loadShortComments();

}


/* =========================================================
   LOAD SHORT COMMENTS
========================================================= */

async function loadShortComments() {

    if (
        !currentShortVideo
    ) {

        return;
    }

    const list =
        $("#shortCommentsList");

    if (!list) {
        return;
    }

    list.innerHTML =
        "Loading comments...";


    try {

        const {
            response,
            data
        } =
            await apiRequest(
                "/api/videos/" +
                currentShortVideo.id +
                "/comments"
            );


        if (!response.ok) {

            throw new Error(
                data.error ||
                "Could not load comments."
            );

        }


        list.innerHTML = "";


        if (!data.length) {

            list.innerHTML = `
                <div
                    style="
                        padding:18px;
                        text-align:center;
                        color:#858c99;
                    "
                >
                    No comments yet.
                </div>
            `;

            return;
        }


        data.forEach(
            comment => {

                const item =
                    document.createElement(
                        "div"
                    );

                item.className =
                    "short-comment-item";

                item.innerHTML = `

                    <div
                        class="short-comment-user"
                    >
                        @${escapeHtml(
                            comment.username ||
                            "user"
                        )}
                    </div>

                    <div
                        class="short-comment-text"
                    >
                        ${escapeHtml(
                            comment.text
                        )}
                    </div>

                `;

                list.appendChild(
                    item
                );

            }
        );


    } catch (error) {

        list.innerHTML = `
            <div
                style="
                    padding:18px;
                    color:#858c99;
                "
            >
                ${escapeHtml(
                    error.message
                )}
            </div>
        `;

    }

}


/* =========================================================
   SEND SHORT COMMENT
========================================================= */

async function sendShortComment() {

    if (
        !currentShortVideo
    ) {

        return;
    }

    if (!state.token) {

        showToast(
            "Login to comment."
        );

        showScreen(
            "login"
        );

        return;
    }


    const input =
        $("#shortCommentInput");

    if (!input) {
        return;
    }

    const text =
        input.value.trim();

    if (!text) {
        return;
    }


    try {

        const {
            response,
            data
        } =
            await apiRequest(
                "/api/videos/" +
                currentShortVideo.id +
                "/comments",
                {
                    method:
                        "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body:
                        JSON.stringify({
                            text
                        })
                }
            );


        if (
            response.status === 201
        ) {

            input.value = "";

            showToast(
                "Comment added."
            );

            loadShortComments();

        } else {

            showToast(
                data.error ||
                "Could not add comment."
            );

        }

    } catch (error) {

        showToast(
            "Connection error."
        );

    }

}


/* =========================================================
   SHARE SHORT
========================================================= */

async function shareShort(
    video
) {

    const link =
        window.location.origin +
        video.video_url;


    if (
        navigator.share
    ) {

        try {

            await navigator.share({

                title:
                    video.title ||
                    "Creator Video",

                text:
                    video.description ||
                    "Check out this video!",

                url:
                    link

            });

        } catch (error) {

            /*
             * User cancelled share.
             */

        }

        return;
    }


    try {

        await navigator.clipboard.writeText(
            link
        );

        showToast(
            "Video link copied."
        );

    } catch (error) {

        showToast(
            "Sharing is not supported here."
        );

    }

}


/* =========================================================
   STOP SHORTS
========================================================= */

function stopShorts() {

    document
        .querySelectorAll(
            ".short-video"
        )
        .forEach(
            video => {

                video.pause();

            }
        );

}

/* =========================================================
   PUBLIC CREATOR PROFILE
========================================================= */

let currentCreatorUsername = "";


/* =========================================================
   OPEN CREATOR PROFILE
========================================================= */

async function openCreatorProfile(
    username
) {

    if (!username) {
        return;
    }

    currentCreatorUsername =
        username;

    $("#creatorProfileUsername")
        .textContent =
        "@" + username;

    $("#creatorProfileDisplayName")
        .textContent =
        "Loading...";

    $("#creatorProfileBio")
        .textContent =
        "";

    $("#creatorProfileVideos")
        .textContent =
        "—";

    $("#creatorProfileFollowers")
        .textContent =
        "—";

    $("#creatorProfileFollowing")
        .textContent =
        "—";

    $("#creatorProfileVideos")
        .innerHTML = `
            <div class="loading-box">
                <div class="loading-spinner"></div>
                <div>Loading creator...</div>
            </div>
        `;

    showScreen(
        "creatorProfile"
    );


    try {

        const {
            response,
            data
        } = await apiRequest(
            "/api/users/" +
            encodeURIComponent(
                username
            )
        );

        if (!response.ok) {

            throw new Error(
                data.error ||
                "Creator not found."
            );

        }


        const user =
            data.user || {};


        $("#creatorProfileUsername")
            .innerHTML = `
                @${escapeHtml(
                    user.username ||
                    username
                )}
        
                ${
                    user.verified
                    ? `<span
                            style="
                                color:#4da3ff;
                                margin-left:4px;
                            "
                       >✓</span>`
                    : ""
                }
            `;


        $("#creatorProfileDisplayName")
            .textContent =
            user.display_name ||
            "Creator";


        $("#creatorProfileBio")
            .textContent =
            user.bio ||
            "No bio yet.";


        $("#creatorProfileVideos")
            .textContent =
            Number(
                (data.videos || []).length
            );


        $("#creatorProfileFollowers")
            .textContent =
            Number(
                user.followers || 0
            );


        $("#creatorProfileFollowing")
            .textContent =
            Number(
                user.following || 0
            );


        /*
         * Don't show Follow on your own profile.
         */

        if (
            state.user &&
            state.user.username &&
            state.user.username.toLowerCase() ===
            username.toLowerCase()
        ) {

            $("#creatorFollowButton")
                .textContent =
                "Your Profile";

            $("#creatorFollowButton")
                .disabled = true;

        } else {

            $("#creatorFollowButton")
                .disabled = false;

            /*
             * We will get the real follow state
             * from the status endpoint below.
             */

            await loadFollowState(
                username
            );

        }


        renderVideos(
            $("#creatorProfileVideos"),
            data.videos || []
        );


    } catch (
        error
    ) {

        $("#creatorProfileVideos")
            .innerHTML = `
                <div class="empty-box">
                    ${escapeHtml(
                        error.message
                    )}
                </div>
            `;

    }

}


/* =========================================================
   FOLLOW STATE
========================================================= */

async function loadFollowState(
    username
) {

    if (
        !state.token
    ) {

        $("#creatorFollowButton")
            .textContent =
            "Follow";

        return;
    }


    try {

        const {
            response,
            data
        } =
            await apiRequest(
                "/api/users/" +
                encodeURIComponent(
                    username
                ) +
                "/follow/status"
            );


        if (
            response.ok
        ) {

            updateFollowButton(
                data.following
            );

        } else {

            $("#creatorFollowButton")
                .textContent =
                "Follow";

        }

    } catch (
        error
    ) {

        $("#creatorFollowButton")
            .textContent =
            "Follow";

    }

}


/* =========================================================
   FOLLOW BUTTON UI
========================================================= */

function updateFollowButton(
    following
) {

    const button =
        $("#creatorFollowButton");

    if (!button) {
        return;
    }

    button.dataset.following =
        following
            ? "true"
            : "false";

    button.textContent =
        following
            ? "Following ✓"
            : "Follow";

}


/* =========================================================
   FOLLOW / UNFOLLOW
========================================================= */

async function toggleCreatorFollow() {

    if (
        !currentCreatorUsername
    ) {

        return;
    }


    if (
        !state.token
    ) {

        showToast(
            "Login to follow creators."
        );

        showScreen(
            "login"
        );

        return;
    }


    const button =
        $("#creatorFollowButton");


    const oldText =
        button.textContent;


    button.disabled =
        true;

    button.textContent =
        "Please wait...";


    try {

        const {
            response,
            data
        } =
            await apiRequest(
                "/api/users/" +
                encodeURIComponent(
                    currentCreatorUsername
                ) +
                "/follow",
                {
                    method:
                        "POST"
                }
            );


        if (!response.ok) {

            button.disabled =
                false;

            button.textContent =
                oldText;

            showToast(
                data.error ||
                "Could not update follow."
            );

            return;
        }


        updateFollowButton(
            data.following
        );


        $("#creatorProfileFollowers")
            .textContent =
            Number(
                data.followers || 0
            );


        showToast(
            data.following
                ? "Following ❤️"
                : "Unfollowed"
        );


    } catch (
        error
    ) {

        button.textContent =
            oldText;

        showToast(
            "Connection error."
        );

    }


    button.disabled =
        false;

}

/* =========================================================
   NOTIFICATIONS
========================================================= */

async function loadNotifications() {

    const container =
        $("#notificationsList");

    if (!container) {
        return;
    }


    if (!state.token) {

        container.innerHTML = `
            <div class="empty-box">

                🔔

                <div>
                    Login to see notifications.
                </div>

                <button
                    class="primary-button"
                    onclick="showScreen('login')"
                >
                    Login
                </button>

            </div>
        `;

        return;
    }


    container.innerHTML = `
        <div class="loading-box">

            <div class="loading-spinner"></div>

            <div>
                Loading notifications...
            </div>

        </div>
    `;


    try {

        const {
            response,
            data
        } =
            await apiRequest(
                "/api/notifications"
            );


        if (!response.ok) {

            throw new Error(
                data.error ||
                "Could not load notifications."
            );

        }


        renderNotifications(
            data.notifications || []
        );


    } catch (
        error
    ) {

        container.innerHTML = `
            <div class="empty-box">

                ${escapeHtml(
                    error.message
                )}

            </div>
        `;

    }

}


/* =========================================================
   RENDER NOTIFICATIONS
========================================================= */

function renderNotifications(
    notifications
) {

    const container =
        $("#notificationsList");

    container.innerHTML = "";


    if (!notifications.length) {

        container.innerHTML = `
            <div class="empty-box">

                🔔

                <div>
                    No notifications yet.
                </div>

            </div>
        `;

        return;
    }


    notifications.forEach(
        notification => {

            const item =
                document.createElement(
                    "div"
                );

            item.className =
                "notification-item";


            let icon =
                "🔔";

            if (
                notification.type ===
                "follow"
            ) {

                icon = "👥";

            }


            const sender =
                notification.sender ||
                {};


            item.innerHTML = `

                <div
                    class="notification-icon"
                >
                    ${icon}
                </div>

                <div
                    class="notification-content"
                >

                    <div
                        class="notification-text"
                    >

                        <strong>
                            @${escapeHtml(
                                sender.username ||
                                "someone"
                            )}
                        </strong>

                        ${escapeHtml(
                            notification.message ||
                            ""
                        )}

                    </div>

                    <div
                        class="notification-time"
                    >
                        ${formatNotificationTime(
                            notification.created_at
                        )}
                    </div>

                </div>

            `;


            container.appendChild(
                item
            );

        }
    );

}


/* =========================================================
   FOLLOWING FEED
========================================================= */

async function loadFollowingFeed() {

    const container =
        $("#videoFeed");

    if (!container) {
        return;
    }


    if (!state.token) {

        container.innerHTML = `
            <div class="empty-box">

                👥

                <div>
                    Login to see your Following feed.
                </div>

                <button
                    class="primary-button"
                    onclick="showScreen('login')"
                >
                    Login
                </button>

            </div>
        `;

        return;
    }


    container.innerHTML = `
        <div class="loading-box">

            <div class="loading-spinner"></div>

            <div>
                Loading Following...
            </div>

        </div>
    `;


    try {

        const {
            response,
            data
        } =
            await apiRequest(
                "/api/feed/following"
            );


        if (!response.ok) {

            throw new Error(
                data.error ||
                "Could not load Following feed."
            );

        }


        renderVideos(
            container,
            data.videos || []
        );


    } catch (
        error
    ) {

        container.innerHTML = `
            <div class="empty-box">

                ❌

                <div>
                    ${escapeHtml(
                        error.message
                    )}
                </div>

                <button
                    class="primary-button"
                    onclick="loadFollowingFeed()"
                >
                    Retry
                </button>

            </div>
        `;

    }

}

/* =========================================================
   NOTIFICATION TIME
========================================================= */

function formatNotificationTime(
    timestamp
) {

    if (!timestamp) {
        return "";
    }

    const date =
        new Date(
            Number(timestamp) *
            1000
        );

    return date.toLocaleString();

}

/* =========================================================
   RANDOM THUMBNAIL
========================================================= */

const RANDOM_THUMBNAIL_ICONS = [
    "🎬",
    "🚀",
    "🔥",
    "✨",
    "🎮",
    "🎵",
    "📸",
    "🌟",
    "💡",
    "🎨",
    "🏆",
    "❤️"
];


function getRandomThumbnailIcon(
    videoId
) {

    /*
     * Use the video ID so the same video
     * gets the same random-looking thumbnail
     * every time the feed reloads.
     */

    const index =
        Number(videoId) %
        RANDOM_THUMBNAIL_ICONS.length;

    return RANDOM_THUMBNAIL_ICONS[
        index
    ];

}

/* =========================================================
   TRENDING FEED
========================================================= */

async function loadTrendingFeed() {

    const container =
        $("#videoFeed");

    if (!container) {
        return;
    }


    container.innerHTML = `
        <div class="loading-box">

            <div class="loading-spinner"></div>

            <div>
                Loading Trending...
            </div>

        </div>
    `;


    try {

        const {
            response,
            data
        } =
            await apiRequest(
                "/api/feed/trending"
            );


        if (!response.ok) {

            throw new Error(
                data.error ||
                "Could not load Trending feed."
            );

        }


        renderVideos(
            container,
            data.videos || []
        );


    } catch (
        error
    ) {

        container.innerHTML = `
            <div class="empty-box">

                ❌

                <div>
                    Could not load Trending.
                </div>

                <div>
                    ${escapeHtml(
                        error.message
                    )}
                </div>

                <button
                    class="primary-button"
                    onclick="loadTrendingFeed()"
                >
                    Retry
                </button>

            </div>
        `;

    }

}

/* =========================================================
   FOR YOU FEED
========================================================= */

async function loadForYouFeed() {

    const container =
        $("#videoFeed");

    if (!container) {
        return;
    }


    container.innerHTML = `
        <div class="loading-box">

            <div class="loading-spinner"></div>

            <div>
                Loading your feed...
            </div>

        </div>
    `;


    try {

        const {
            response,
            data
        } =
            await apiRequest(
                "/api/feed/for-you"
            );


        if (!response.ok) {

            throw new Error(
                data.error ||
                "Could not load your feed."
            );

        }


        renderVideos(
            container,
            data.videos || []
        );


    } catch (
        error
    ) {

        container.innerHTML = `
            <div class="empty-box">

                ❌

                <div>
                    Could not load your feed.
                </div>

                <div>
                    ${escapeHtml(
                        error.message
                    )}
                </div>

                <button
                    class="primary-button"
                    onclick="loadForYouFeed()"
                >
                    Retry
                </button>

            </div>
        `;

    }

}

/* =========================================================
   SHORT PLAY OVERLAY
========================================================= */

function updatePlayOverlay(
    item,
    show
) {

    const overlay =
        item.querySelector(
            "[data-play-overlay]"
        );

    if (!overlay) {
        return;
    }

    if (show) {

        overlay.classList.add(
            "visible"
        );

    } else {

        overlay.classList.remove(
            "visible"
        );

    }

}

function showDoubleLike(
    item
) {

    const heart =
        document.createElement(
            "div"
        );

    heart.className =
        "double-like-heart";

    heart.textContent =
        "❤️";

    item.appendChild(
        heart
    );

    setTimeout(
        () => {

            heart.remove();

        },
        800
    );

}

/* =========================================================
   CREATOR BOOST
========================================================= */

async function loadCreatorBoost() {

    const scoreElement =
        $("#boostScore");

    const levelElement =
        $("#boostLevel");

    const progressBar =
        $("#boostProgressBar");

    const nextText =
        $("#boostNextText");

    const bestVideo =
        $("#boostBestVideo");


    if (!scoreElement) {
        return;
    }


    try {

        const {
            response,
            data
        } =
            await apiRequest(
                "/api/creator/boost"
            );


        if (!response.ok) {

            throw new Error(
                data.error ||
                "Could not load Creator Boost."
            );

        }


        const boost =
            data.boost || {};


        const score =
            Number(
                boost.score || 0
            );


        scoreElement.textContent =
            score;


        levelElement.textContent =
            boost.level_name ||
            "🌱 New Creator";


        const nextScore =
            boost.next_score;


        if (
            nextScore
        ) {

            const previousScore =
                boost.level === 0
                    ? 0
                    : boost.level === 1
                    ? 50
                    : 150;


            const range =
                nextScore -
                previousScore;


            const current =
                Math.max(
                    0,
                    score -
                    previousScore
                );


            const percent =
                Math.min(
                    100,
                    (
                        current /
                        range
                    ) * 100
                );


            progressBar.style.width =
                percent + "%";


            nextText.textContent =
                nextScore -
                score +
                " points to next level";

        } else {

            progressBar.style.width =
                "100%";

            nextText.textContent =
                "Maximum boost level reached 🚀";

        }


        const best =
            boost.best_video;


        if (best) {

            bestVideo.innerHTML = `

                <strong>
                    🔥 Best performing video
                </strong>

                <div
                    class="boost-video-title"
                >
                    ${escapeHtml(
                        best.title ||
                        "Untitled"
                    )}
                </div>

                <div
                    class="boost-video-stats"
                >
                    ${Number(
                        best.views || 0
                    )} views
                    ·
                    ${Number(
                        best.likes || 0
                    )} likes
                    ·
                    ${Number(
                        best.comments || 0
                    )} comments
                </div>

            `;

        }

    } catch (
        error
    ) {

        console.log(
            "Creator Boost error:",
            error
        );

    }

}

async function deleteVideo(videoId){

    if(!confirm("Delete this video permanently?")){
        return;
    }


    const token = localStorage.getItem("creator_token");

    console.log("DELETE TOKEN:", token);


    const response = await fetch(
        `/api/videos/${videoId}`,
        {
            method:"DELETE",

            headers:{
                "Authorization":
                "Bearer " + token
            }
        }
    );


    const data = await response.json();


    if(data.success){

        alert(
            "Video deleted"
        );

        location.reload();

    }
    else{

        alert(
            data.error
        );

    }

}

const shortsCheckbox = document.getElementById("shortsCheckbox");
const videoCheckbox = document.getElementById("videoCheckbox");


if(shortsCheckbox && videoCheckbox){

    shortsCheckbox.addEventListener("change",()=>{

        if(shortsCheckbox.checked){
            videoCheckbox.checked = false;
        }

    });


    videoCheckbox.addEventListener("change",()=>{

        if(videoCheckbox.checked){
            shortsCheckbox.checked = false;
        }

    });

}
