# ============================================================
# YOUTUBE CHANNEL MANAGER
# NO YOUTUBE DATA API
#
# Add channel URLs to CHANNELS.
#
# Features:
#   • Simple channel configuration
#   • Up to 50 videos per channel
#   • Automatically mixes all channels
#   • Supports @handle URLs
#   • Uses channel page + RSS fallback
# ============================================================

import re
import requests
import xml.etree.ElementTree as ET
from urllib.parse import urlparse


# ============================================================
# SIMPLE CONFIGURATION
# ============================================================

CHANNELS = {

    "sourav_joshi_vlogs": {

        "channel_url":
            "https://www.youtube.com/@SouravJoshiVlogs",

        "channel_title":
            "Sourav Joshi Vlogs",

        "category":
            "vlogs",

    },


    "triggered_insaan": {

        "channel_url":
            "https://www.youtube.com/@TriggeredInsaan",

        "channel_title":
            "Triggered Insaan",

        "category":
            "gaming",

    },


    # ========================================================
    # ADD MORE CHANNELS HERE
    # ========================================================

    "dimple malhan": {
    
        "channel_url":
            "https://www.youtube.com/@DimpleMalhanVlogs",
    
        "channel_title":
            "Dimple malhan",
    
        "category":
            "entertainment",
    
    },
    "fukra insaann": {
    
        "channel_url":
            "https://www.youtube.com/@FukraInsaan",
    
        "channel_title":
            "Fukra Insaan",
    
        "category":
            "entertainment",
    
    },

    "Carzy xyz": {
    
        "channel_url":
            "https://www.youtube.com/results?search_query=crazy+xyz",
    
        "channel_title":
            "Crazy XYZ",
    
        "category":
            "entertainment",
    
    },

    "Mr indian hacker": {
    
        "channel_url":
            "https://www.youtube.com/@MRINDIANHACKER",
    
        "channel_title":
            "Mr Indian Hacker",
    
        "category":
            "experiment",
    
    },

    "amirextra": {
    
        "channel_url":
            "https://www.youtube.com/@AmitExtra2",
    
        "channel_title":
            "Amir Extra",
    
        "category":
            "gaming",
    
    },

    "anshextra": {
    
        "channel_url":
            "https://www.youtube.com/@anshextra7",
    
        "channel_title":
            "Ansh Extra",
    
        "category":
            "gaming",
    
    },

    "Malik kids": {
    
        "channel_url":
            "https://www.youtube.com/@Kritikapayal",
    
        "channel_title":
            "Malik Kids",
    
        "category":
            "gaming",
    
    },

    "niku vlogs": {
    
        "channel_url":
            "https://www.youtube.com/@NIkkuVlogz",
    
        "channel_title":
            "Nikku Vlogz",
    
        "category":
            "vlogz",
    
    },

    "tam ex": {
    
        "channel_url":
            "https://www.youtube.com/@TAMexOFFISIAL",
    
        "channel_title":
            "TAM EX",
    
        "category":
            "gaming",
    
    },

    "techno ": {
    
        "channel_url":
            "https://www.youtube.com/@TechnoGamerzOfficial",
    
        "channel_title":
            "Techno Gamerz",
    
        "category":
            "gaming",
    
    },

    "nirankari ": {
    
        "channel_url":
            "https://www.youtube.com/@NirankariOrgUpdates",
    
        "channel_title":
            "SNM",
    
        "category":
            "religious",
    
    },

    "coke studio": {
    
        "channel_url":
            "https://www.youtube.com/@cokestudio",
    
        "channel_title":
            "Coke Studio",
    
        "category":
            "songs",
    
    },













}


# ============================================================
# SETTINGS
# ============================================================

MAX_VIDEOS_PER_CHANNEL = 50

REQUEST_TIMEOUT = 20

USER_AGENT = (
    "Mozilla/5.0 "
    "(Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 "
    "(KHTML, like Gecko) "
    "Chrome/120.0 Safari/537.36"
)


# ============================================================
# YOUTUBE RSS
# ============================================================

RSS_URL = (
    "https://www.youtube.com/feeds/videos.xml"
    "?channel_id={}"
)


# ============================================================
# NAMESPACES
# ============================================================

NAMESPACES = {

    "yt":
        "http://www.youtube.com/xml/schemas/2015",

    "media":
        "http://search.yahoo.com/mrss/",

    "atom":
        "http://www.w3.org/2005/Atom",

}


# ============================================================
# HTTP HEADERS
# ============================================================

HEADERS = {

    "User-Agent":
        USER_AGENT,

    "Accept-Language":
        "en-US,en;q=0.9",

}


# ============================================================
# GET CHANNEL ID
# ============================================================

def get_channel_id(channel_url):

    if not channel_url:

        return None


    channel_url = str(
        channel_url
    ).strip()


    # --------------------------------------------------------
    # Direct channel ID
    # --------------------------------------------------------

    match = re.search(
        r"/channel/"
        r"(UC[a-zA-Z0-9_-]{20,})",
        channel_url
    )


    if match:

        return match.group(1)


    # --------------------------------------------------------
    # Request channel page
    # --------------------------------------------------------

    try:

        response = requests.get(
            channel_url,
            headers=HEADERS,
            timeout=REQUEST_TIMEOUT
        )


        if response.status_code != 200:

            print(
                "Channel page failed:",
                response.status_code
            )

            return None


        html = response.text


    except Exception as error:

        print(
            "Channel request error:",
            error
        )

        return None


    # --------------------------------------------------------
    # Search several possible channel ID formats
    # --------------------------------------------------------

    patterns = [

        r'"channelId":"(UC[a-zA-Z0-9_-]{20,})"',

        r'"externalId":"(UC[a-zA-Z0-9_-]{20,})"',

        r'"browseId":"(UC[a-zA-Z0-9_-]{20,})"',

        r'"channel_id":"(UC[a-zA-Z0-9_-]{20,})"',

        r'"externalChannelId":"(UC[a-zA-Z0-9_-]{20,})"',

    ]


    for pattern in patterns:

        match = re.search(
            pattern,
            html
        )

        if match:

            return match.group(1)


    return None


# ============================================================
# EXTRACT VIDEO ID
# ============================================================

def extract_youtube_id(value):

    if not value:

        return None


    value = str(
        value
    ).strip()


    # --------------------------------------------------------
    # Raw ID
    # --------------------------------------------------------

    if re.fullmatch(
        r"[a-zA-Z0-9_-]{11}",
        value
    ):

        return value


    # --------------------------------------------------------
    # watch?v=
    # --------------------------------------------------------

    match = re.search(
        r"[?&]v=([a-zA-Z0-9_-]{11})",
        value
    )

    if match:

        return match.group(1)


    # --------------------------------------------------------
    # youtu.be
    # --------------------------------------------------------

    match = re.search(
        r"youtu\.be/"
        r"([a-zA-Z0-9_-]{11})",
        value
    )

    if match:

        return match.group(1)


    # --------------------------------------------------------
    # shorts
    # --------------------------------------------------------

    match = re.search(
        r"/shorts/"
        r"([a-zA-Z0-9_-]{11})",
        value
    )

    if match:

        return match.group(1)


    # --------------------------------------------------------
    # embed
    # --------------------------------------------------------

    match = re.search(
        r"/embed/"
        r"([a-zA-Z0-9_-]{11})",
        value
    )

    if match:

        return match.group(1)


    return None


# ============================================================
# EXTRACT VIDEO IDS FROM CHANNEL HTML
# ============================================================

def extract_video_ids_from_html(html):

    video_ids = []

    seen = set()


    # ========================================================
    # PATTERN 1
    # ========================================================

    patterns = [

        r'"videoId":"([a-zA-Z0-9_-]{11})"',

        r'"videoId":\s*"([a-zA-Z0-9_-]{11})"',

        r'watch\?v=([a-zA-Z0-9_-]{11})',

        r'youtu\.be/([a-zA-Z0-9_-]{11})',

    ]


    for pattern in patterns:

        matches = re.findall(
            pattern,
            html
        )


        for video_id in matches:

            if video_id in seen:

                continue


            seen.add(
                video_id
            )

            video_ids.append(
                video_id
            )


            if len(video_ids) >= MAX_VIDEOS_PER_CHANNEL:

                return video_ids


    return video_ids


# ============================================================
# LOAD VIDEOS FROM CHANNEL PAGE
# ============================================================

def load_channel_page_videos(
    channel_url,
    channel_key,
    channel_config
):

    print(
        "Trying channel page..."
    )


    try:

        response = requests.get(
            channel_url,
            headers=HEADERS,
            timeout=REQUEST_TIMEOUT
        )


        if response.status_code != 200:

            print(
                "Channel page status:",
                response.status_code
            )

            return []


        html = response.text


    except Exception as error:

        print(
            "Channel page error:",
            error
        )

        return []


    video_ids = extract_video_ids_from_html(
        html
    )


    print(
        "VIDEO IDS FOUND FROM PAGE:",
        len(video_ids)
    )


    videos = []


    channel_title = channel_config.get(
        "channel_title",
        channel_key
    )


    category = channel_config.get(
        "category",
        "general"
    )


    for number, youtube_id in enumerate(
        video_ids,
        start=1
    ):

        videos.append({

            "id":
                youtube_id,

            "youtube_id":
                youtube_id,

            "title":
                f"{channel_title} Video {number}",

            "description":
                "",

            "category":
                category,

            "thumbnail":
                (
                    "https://i.ytimg.com/vi/"
                    +
                    youtube_id
                    +
                    "/hqdefault.jpg"
                ),

            "video_url":
                (
                    "https://www.youtube.com/embed/"
                    +
                    youtube_id
                ),

            "youtube_url":
                (
                    "https://www.youtube.com/watch?v="
                    +
                    youtube_id
                ),

            "channel_title":
                channel_title,

            "views":
                0,

            "likes":
                0,

            "comments":
                0,

            "created_at":
                0,

            "source":
                "youtube",

            "creator": {

                "username":
                    channel_key,

                "display_name":
                    channel_title,

                "avatar":
                    "",

                "verified":
                    True

            }

        })


    return videos


# ============================================================
# LOAD RSS
# ============================================================

def load_channel_rss(
    channel_id,
    channel_key,
    channel_config
):

    if not channel_id:

        return []


    url = RSS_URL.format(
        channel_id
    )


    try:

        response = requests.get(
            url,
            headers=HEADERS,
            timeout=REQUEST_TIMEOUT
        )


        if response.status_code != 200:

            print(
                "RSS failed:",
                response.status_code
            )

            return []


        root = ET.fromstring(
            response.content
        )


    except Exception as error:

        print(
            "RSS error:",
            error
        )

        return []


    channel_title = channel_config.get(
        "channel_title",
        channel_key
    )


    category = channel_config.get(
        "category",
        "general"
    )


    videos = []


    entries = root.findall(
        "atom:entry",
        NAMESPACES
    )


    for entry in entries:

        if len(videos) >= MAX_VIDEOS_PER_CHANNEL:

            break


        # ----------------------------------------------------
        # VIDEO ID
        # ----------------------------------------------------

        video_element = entry.find(
            "yt:videoId",
            NAMESPACES
        )


        if (
            video_element is None
            or not video_element.text
        ):

            continue


        youtube_id = (
            video_element.text.strip()
        )


        # ----------------------------------------------------
        # TITLE
        # ----------------------------------------------------

        title_element = entry.find(
            "atom:title",
            NAMESPACES
        )


        if (
            title_element is not None
            and title_element.text
        ):

            title = (
                title_element.text.strip()
            )

        else:

            title = "YouTube Video"


        # ----------------------------------------------------
        # PUBLISHED
        # ----------------------------------------------------

        published_element = entry.find(
            "atom:published",
            NAMESPACES
        )


        if (
            published_element is not None
            and published_element.text
        ):

            published = (
                published_element.text
            )

        else:

            published = ""


        # ----------------------------------------------------
        # DESCRIPTION
        # ----------------------------------------------------

        description = ""


        media_group = entry.find(
            "media:group",
            NAMESPACES
        )


        if media_group is not None:

            description_element = (
                media_group.find(
                    "media:description",
                    NAMESPACES
                )
            )


            if (
                description_element is not None
                and description_element.text
            ):

                description = (
                    description_element.text.strip()
                )


        # ----------------------------------------------------
        # VIDEO
        # ----------------------------------------------------

        videos.append({

            "id":
                youtube_id,

            "youtube_id":
                youtube_id,

            "title":
                title,

            "description":
                description,

            "category":
                category,

            "thumbnail":
                (
                    "https://i.ytimg.com/vi/"
                    +
                    youtube_id
                    +
                    "/hqdefault.jpg"
                ),

            "video_url":
                (
                    "https://www.youtube.com/embed/"
                    +
                    youtube_id
                ),

            "youtube_url":
                (
                    "https://www.youtube.com/watch?v="
                    +
                    youtube_id
                ),

            "channel_title":
                channel_title,

            "views":
                0,

            "likes":
                0,

            "comments":
                0,

            "created_at":
                published,

            "source":
                "youtube",

            "creator": {

                "username":
                    channel_key,

                "display_name":
                    channel_title,

                "avatar":
                    "",

                "verified":
                    True

            }

        })


    return videos


# ============================================================
# LOAD ONE CHANNEL
# ============================================================

def load_one_channel(
    channel_key,
    channel_config
):

    channel_url = channel_config.get(
        "channel_url"
    )


    channel_title = channel_config.get(
        "channel_title",
        channel_key
    )


    print()
    print(
        "========================================"
    )

    print(
        "CHANNEL:",
        channel_title
    )

    print(
        "URL:",
        channel_url
    )


    # ========================================================
    # FIRST: CHANNEL PAGE
    # ========================================================

    videos = load_channel_page_videos(
        channel_url,
        channel_key,
        channel_config
    )


    # ========================================================
    # GET CHANNEL ID
    # ========================================================

    channel_id = get_channel_id(
        channel_url
    )


    if channel_id:

        print(
            "CHANNEL ID:",
            channel_id
        )

    else:

        print(
            "CHANNEL ID NOT FOUND"
        )


    # ========================================================
    # RSS FALLBACK
    # ========================================================

    if len(videos) < MAX_VIDEOS_PER_CHANNEL:

        print(
            "Channel page returned",
            len(videos),
            "videos."
        )

        print(
            "Trying RSS fallback..."
        )


        rss_videos = load_channel_rss(
            channel_id,
            channel_key,
            channel_config
        )


        existing_ids = {

            video.get(
                "youtube_id"
            )

            for video in videos

        }


        for video in rss_videos:

            youtube_id = video.get(
                "youtube_id"
            )


            if youtube_id in existing_ids:

                continue


            videos.append(
                video
            )


            existing_ids.add(
                youtube_id
            )


            if len(videos) >= MAX_VIDEOS_PER_CHANNEL:

                break


    # ========================================================
    # FINAL LIMIT
    # ========================================================

    videos = videos[
        :MAX_VIDEOS_PER_CHANNEL
    ]


    print(
        "FINAL VIDEOS:",
        len(videos)
    )


    return videos


# ============================================================
# BUILD ALL CHANNEL VIDEOS
# ============================================================

def build_channel_videos():

    """
    Load every configured channel.

    Then mix them evenly using round-robin.

    Example with 3 channels:

        Channel A #1
        Channel B #1
        Channel C #1

        Channel A #2
        Channel B #2
        Channel C #2

        Channel A #3
        Channel B #3
        Channel C #3
    """

    channel_lists = []


    print()
    print()
    print("========================================")
    print("       YOUTUBE CHANNEL MANAGER")
    print("========================================")
    print(
        "CHANNELS:",
        len(CHANNELS)
    )
    print(
        "MAX PER CHANNEL:",
        MAX_VIDEOS_PER_CHANNEL
    )
    print("========================================")


    # ========================================================
    # LOAD EVERY CHANNEL
    # ========================================================

    for channel_key, channel_config in CHANNELS.items():

        videos = load_one_channel(
            channel_key,
            channel_config
        )


        if videos:

            channel_lists.append(
                videos
            )


    # ========================================================
    # EVEN MIX
    # ========================================================

    mixed_videos = []


    position = 0


    while channel_lists:

        if position >= len(channel_lists):

            position = 0


        queue = channel_lists[
            position
        ]


        if queue:

            video = queue.pop(0)

            mixed_videos.append(
                video
            )


        # ----------------------------------------------------
        # Remove empty channel
        # ----------------------------------------------------

        if not queue:

            channel_lists.pop(
                position
            )

        else:

            position += 1


    # ========================================================
    # RESULT
    # ========================================================

    print()
    print("========================================")
    print("YOUTUBE MIX COMPLETE")
    print("========================================")

    print(
        "TOTAL MIXED VIDEOS:",
        len(mixed_videos)
    )

    print(
        "========================================")


    return mixed_videos
