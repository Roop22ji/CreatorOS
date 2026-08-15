import time
from database import get_connection


# ============================================================
# SAVE YOUTUBE VIDEOS TO CACHE
# ============================================================

def save_youtube_cache(videos):

    connection = get_connection()

    for video in videos:

        try:

            connection.execute(
                """
                INSERT OR IGNORE INTO youtube_cache
                (
                    youtube_id,
                    title,
                    description,
                    thumbnail,
                    channel_title,
                    youtube_url,
                    created_at
                )

                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,

                (
                    video["youtube_id"],

                    video.get(
                        "title",
                        ""
                    ),

                    video.get(
                        "description",
                        ""
                    ),

                    video.get(
                        "thumbnail",
                        ""
                    ),

                    video.get(
                        "creator",
                        {}
                    ).get(
                        "username",
                        "YouTube"
                    ),

                    "https://youtube.com/watch?v="
                    + video["youtube_id"],

                    int(time.time())
                )
            )


        except Exception as e:

            print(
                "CACHE SAVE ERROR:",
                e
            )


    connection.commit()
    connection.close()


    print(
        "CACHE SAVED:",
        len(videos)
    )



# ============================================================
# LOAD YOUTUBE CACHE (OLD + NEW MIX)
# ============================================================

def get_cached_youtube(limit=100, offset=0):

    connection = get_connection()


    rows = connection.execute(
        """
        SELECT *

        FROM youtube_cache

        ORDER BY RANDOM()

        LIMIT ?
        OFFSET ?

        """,
        (
            limit,
            offset
        )

    ).fetchall()


    connection.close()


    videos = []


    for row in rows:

        videos.append(

            {

                "id":
                    "youtube_"
                    + row["youtube_id"],


                "source":
                    "youtube",


                "youtube_id":
                    row["youtube_id"],


                "youtube_url":
                    row["youtube_url"],


                "video_url":
                    "https://www.youtube.com/embed/"
                    + row["youtube_id"],


                "title":
                    row["title"],


                "description":
                    row["description"],


                "thumbnail":
                    row["thumbnail"],


                "views":
                    0,


                "likes":
                    0,


                "comments":
                    0,


                "boosted":
                    True,


                "boost_level":
                    1,


                "creator":
                {

                    "username":
                        row["channel_title"],


                    "display_name":
                        row["channel_title"],


                    "verified":
                        False

                }

            }

        )


    print(
        "YOUTUBE CACHE LOADED:",
        len(videos)
    )


    return videos



# ============================================================
# CACHE COUNT
# ============================================================

def youtube_cache_count():

    connection = get_connection()


    row = connection.execute(
        """
        SELECT COUNT(*) AS total

        FROM youtube_cache
        """
    ).fetchone()


    connection.close()


    return row["total"]



# ============================================================
# OWNER REFRESH - ONLY ADD NEW VIDEOS
# ============================================================

def owner_refresh_youtube(new_videos):

    print(
        "OWNER REFRESH: ADDING NEW VIDEOS"
    )


    save_youtube_cache(
        new_videos
    )


    print(
        "TOTAL CACHE:",
        youtube_cache_count()
    )
