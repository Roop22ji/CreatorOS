# ============================================================
# YOUTUBE CHANNEL MANAGER
# NO YOUTUBE API
# ============================================================


CHANNELS = {

    "sourav_joshi_vlogs": {

        "channel_title": "Sourav Joshi Vlogs",

        "category": "vlogs",

        "videos": [

            
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
            "https://www.youtube.com/watch?v=uyXI_xSZ1Lg",
            "https://www.youtube.com/watch?v=870j2LgScxY",

        ]

    },
    
    "malik family": {

        "channel_title": "Malik Kids",

        "category": "vlogs",

        "videos": [

            "https://www.youtube.com/watch?v=BPF3G_-gLt4",
            "https://www.youtube.com/watch?v=UdsGGybqQ28",
            "https://www.youtube.com/watch?v=eaRAG2GtbNM"

        ]

    },

    "mr indian hacker": {

        "channel_title": "Mr Indian Hacker",

        "category": "experiment",

        "videos": [

            "https://www.youtube.com/watch?v=jlQ9K7ORz5Y",
            "https://www.youtube.com/watch?v=39pST9HAOYU",
            "https://www.youtube.com/watch?v=zoN9xJW54PE",
            "https://www.youtube.com/watch?v=NOaLPTzrMMo&list=PLs2q0kQKcqmbVh62oHewVvqNp5ufxhPNK",
            "https://www.youtube.com/watch?v=O3vmDDTiZao",
            "https://www.youtube.com/watch?v=XjOOSuQhe8E",
            "https://www.youtube.com/watch?v=9JdADVvuIjM",
            "https://www.youtube.com/watch?v=AgZO6yYq6cc",


        ]

    },
    "nikku_vlogs": {

        "channel_title": "Nikku Vlogs",

        "category": "experiment",

        "videos": [

            "https://www.youtube.com/watch?v=A9Jy7LwVtFQ",
            "https://www.youtube.com/watch?v=A40xn8UfxzY",
            "https://www.youtube.com/watch?v=58w6QfcLVxs",
            "https://www.youtube.com/watch?v=RJt9p0QnXQc",
            "https://www.youtube.com/watch?v=M8PpmZ7-9Ow",
            "https://www.youtube.com/watch?v=LiFbT_cJ5b0",
            "https://www.youtube.com/watch?v=0xKW0z7vmg0",
            "https://www.youtube.com/watch?v=rY4o8t2ymI8",


        ]

    },
    "techno gamerz": {

        "channel_title": "Techno Gamerz",

        "category": "experiment",

        "videos": [

            "https://www.youtube.com/watch?v=YG14X4QDpGo",
            "https://www.youtube.com/watch?v=N3ySdpmqF9Y&t=4893s",
            "https://www.youtube.com/watch?v=BE3I2kmzrwg",
            "https://www.youtube.com/watch?v=97NW_Qcxhh0",
            "https://www.youtube.com/watch?v=RSm9Su3WtxA",
            "https://www.youtube.com/watch?v=px9AwXq2_lA",
            "https://www.youtube.com/watch?v=Z2XKA-wQjac",
            "https://www.youtube.com/watch?v=n9vED3JsHZ0",


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
