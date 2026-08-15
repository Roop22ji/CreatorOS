# ============================================================
# YOUTUBE CHANNEL MANAGER
# NO YOUTUBE API
# ============================================================


CHANNELS = {

    "sourav_joshi_vlogs": {

        "channel_title": "Sourav Joshi Vlogs",

        "category": "vlogs",

        "videos": [

            "7UU-oODb0jE"
            "72XfOlN6hbk"
            "ozEOf31-d5Y"

        ]

    },

    "Amit_extra": {

        "channel_title": "amitextra",

        "category": "gaming",

        "videos": [

            "puRIPW-C1hg"
            

        ]

    },

    "triggered_insaan": {

        "channel_title": "triggered",

        "category": "gaming",

        "videos": [

            "fyPt7sowHIQ&t=67s"
            "g_NaHx4zbuc&t=1933s"
            "p7coaVdQVWw"
            

        ]

    },
    "random": {

        "channel_title": "random",

        "category": "gaming",

        "videos": [

            "https://www.youtube.com/watch?v=MPmKAk7mjDo",
            "https://www.youtube.com/watch?v=b7A3Pbny-7M",
            "https://www.youtube.com/watch?v=YtO22syoxFg&t=468s",
            "https://www.youtube.com/watch?v=7xxeWVBOViQ",
            "https://www.youtube.com/watch?v=zf2iFLkHWP8",
            "https://www.youtube.com/watch?v=Af6i6ChAVTw",
            "https://www.youtube.com/watch?v=pzBi1nwDn8U",
            "https://www.youtube.com/watch?v=MW_q00eHyfY",
            "https://www.youtube.com/watch?v=YpTgLi1detk",
            "https://www.youtube.com/watch?v=2znLf_9fPrc",
            "https://www.youtube.com/watch?v=gLAjowInE6s",
            "https://www.youtube.com/watch?v=bbHx4M7CAGw",
    
            "https://www.youtube.com/watch?v=jR6Y4H87Bag",
            "https://www.youtube.com/watch?v=_pUa1UQEctQ",
            "https://www.youtube.com/watch?v=q6Do9Qj_cMs",
            "https://www.youtube.com/watch?v=DdUWrJcE4uI",
            "https://www.youtube.com/watch?v=kLujv40zGFE",
            "https://www.youtube.com/watch?v=bnDecJ1X6Wg",
            "https://www.youtube.com/watch?v=I_WXKWgwRvM",
            "https://www.youtube.com/watch?v=VKe2u_tEWVo",
            "https://www.youtube.com/watch?v=ZungsQqN8qQ",
            "https://www.youtube.com/watch?v=uyXI_xSZ1Lg"
        
            

        ]

    },


}


def extract_youtube_id(value):

    """
    Extract a YouTube video ID from:

    https://www.youtube.com/watch?v=VIDEO_ID
    https://youtu.be/VIDEO_ID
    https://www.youtube.com/embed/VIDEO_ID

    Or accept a raw video ID.
    """

    if not value:
        return None

    value = str(value).strip()


    # --------------------------------------------------------
    # Raw YouTube ID
    # --------------------------------------------------------

    if (
        "youtube.com" not in value
        and
        "youtu.be" not in value
    ):

        return value


    # --------------------------------------------------------
    # youtube.com/watch?v=
    # --------------------------------------------------------

    if "watch?v=" in value:

        video_id = value.split(
            "watch?v=",
            1
        )[1]

        video_id = video_id.split(
            "&",
            1
        )[0]

        return video_id


    # --------------------------------------------------------
    # youtu.be/VIDEO_ID
    # --------------------------------------------------------

    if "youtu.be/" in value:

        video_id = value.split(
            "youtu.be/",
            1
        )[1]

        video_id = video_id.split(
            "?",
            1
        )[0]

        video_id = video_id.split(
            "&",
            1
        )[0]

        return video_id


    # --------------------------------------------------------
    # youtube.com/embed/VIDEO_ID
    # --------------------------------------------------------

    if "/embed/" in value:

        video_id = value.split(
            "/embed/",
            1
        )[1]

        video_id = video_id.split(
            "?",
            1
        )[0]

        return video_id


    return None


def build_channel_videos():

    """
    Convert CHANNELS into the format
    used by YOUTUBE_CATALOG.
    """

    videos = []


    for channel_key, channel in CHANNELS.items():

        channel_title = channel.get(
            "channel_title",
            "YouTube"
        )

        category = channel.get(
            "category",
            "general"
        )

        video_list = channel.get(
            "videos",
            []
        )


        for video_number, value in enumerate(
            video_list,
            start=1
        ):

            youtube_id = extract_youtube_id(
                value
            )


            if not youtube_id:

                continue


            videos.append({

                "id":
                    youtube_id,

                "youtube_id":
                    youtube_id,

                "title":
                    f"{channel_title} Video {video_number}",

                "description":
                    "",

                "category":
                    category,

                "thumbnail":
                    (
                        "https://img.youtube.com/vi/"
                        +
                        youtube_id
                        +
                        "/hqdefault.jpg"
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
