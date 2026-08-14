import time
from database import get_connection


# ============================================================
# SAVE YOUTUBE VIDEOS TO CACHE
# ============================================================

def save_youtube_cache(videos):

    connection = get_connection()

    for video in videos:

        connection.execute(
            """
            INSERT OR REPLACE INTO youtube_cache
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
                video["title"],
                video.get("description", ""),
                video.get("thumbnail", ""),
                video["creator"]["username"],
                "https://youtube.com/watch?v="
                + video["youtube_id"],
                int(time.time())
            )
        )

    connection.commit()
    connection.close()



# ============================================================
# LOAD FROM CACHE
# ============================================================

def get_cached_youtube(limit=50):

    connection = get_connection()

    rows = connection.execute(
        """
        SELECT *

        FROM youtube_cache

        ORDER BY created_at DESC

        LIMIT ?
        """,
        (limit,)
    ).fetchall()


    connection.close()


    videos = []


    for row in rows:

        videos.append({

            "id":
                "youtube_" + row["youtube_id"],

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

        })


    return videos