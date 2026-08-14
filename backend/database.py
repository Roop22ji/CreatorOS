import sqlite3

from config import config


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_connection():
    """
    Create a connection to the SQLite database.
    """

    connection = sqlite3.connect(
        config.DATABASE_PATH
    )

    connection.row_factory = sqlite3.Row

    # Allows SQLite foreign-key relationships.
    connection.execute(
        "PRAGMA foreign_keys = ON"
    )

    return connection


# ============================================================
# DATABASE INITIALIZATION
# ============================================================

def initialize_database():

    connection = get_connection()

    cursor = connection.cursor()

    # ========================================================
    # USERS
    # ========================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            username TEXT NOT NULL UNIQUE,

            email TEXT NOT NULL UNIQUE,

            password_hash TEXT NOT NULL,

            display_name TEXT DEFAULT '',

            bio TEXT DEFAULT '',

            avatar TEXT DEFAULT '',

            verified INTEGER DEFAULT 0,

            created_at INTEGER NOT NULL
        )
    """)

    # ========================================================
    # VIDEOS
    # ========================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS videos (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            user_id INTEGER NOT NULL,

            title TEXT NOT NULL,

            description TEXT DEFAULT '',

            filename TEXT NOT NULL,

            thumbnail TEXT DEFAULT '',

            video_type TEXT DEFAULT 'video',

            views INTEGER DEFAULT 0,

            likes INTEGER DEFAULT 0,

            comments_count INTEGER DEFAULT 0,

            source TEXT DEFAULT 'creator',

            youtube_id TEXT,

            youtube_url TEXT,

            visibility TEXT DEFAULT 'public',

            is_short INTEGER DEFAULT 0,

            created_at INTEGER NOT NULL,

            FOREIGN KEY(user_id)
                REFERENCES users(id)
                ON DELETE CASCADE
        )
    """)
    
   
    # ========================================================
    # VIDEO TYPE MIGRATION
    # ========================================================

    video_columns = cursor.execute(
        "PRAGMA table_info(videos)"
    ).fetchall()

    video_column_names = [
        column["name"]
        for column in video_columns
    ]

    if "youtube_id" not in video_column_names:

        cursor.execute("""
            ALTER TABLE videos
            ADD COLUMN youtube_id TEXT
        """)


    if "youtube_url" not in video_column_names:

        cursor.execute("""
            ALTER TABLE videos
            ADD COLUMN youtube_url TEXT
        """)

    if "source" not in video_column_names:

        cursor.execute("""
            ALTER TABLE videos
            ADD COLUMN source TEXT DEFAULT 'creator'
        """)

    if "video_type" not in video_column_names:

        cursor.execute("""
            ALTER TABLE videos
            ADD COLUMN video_type TEXT DEFAULT 'video'
        """)

        cursor.execute("""
            UPDATE videos
            SET video_type = 'video'
            WHERE video_type IS NULL
            OR video_type = ''
        """)


    # ========================================================
    # LIKES
    # ========================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS likes (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            user_id INTEGER NOT NULL,

            video_id INTEGER NOT NULL,

            created_at INTEGER NOT NULL,

            UNIQUE(user_id, video_id),

            FOREIGN KEY(user_id)
                REFERENCES users(id)
                ON DELETE CASCADE,

            FOREIGN KEY(video_id)
                REFERENCES videos(id)
                ON DELETE CASCADE
        )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS youtube_cache (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        youtube_id TEXT UNIQUE,

        title TEXT,

        description TEXT DEFAULT '',

        thumbnail TEXT DEFAULT '',

        channel_title TEXT DEFAULT '',

        youtube_url TEXT,

        created_at INTEGER NOT NULL
    )
    """)



    youtube_columns = cursor.execute(
        "PRAGMA table_info(youtube_cache)"
    ).fetchall()

    youtube_column_names = [
        column["name"]
        for column in youtube_columns
    ]


    if "youtube_id" not in youtube_column_names:
        cursor.execute(
            "ALTER TABLE youtube_cache ADD COLUMN youtube_id TEXT"
        )

    if "channel_title" not in youtube_column_names:
        cursor.execute(
            "ALTER TABLE youtube_cache ADD COLUMN channel_title TEXT DEFAULT ''"
        )

    if "youtube_url" not in youtube_column_names:
        cursor.execute(
            "ALTER TABLE youtube_cache ADD COLUMN youtube_url TEXT"
        )

    # ========================================================
    # COMMENTS
    # ========================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS comments (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            user_id INTEGER NOT NULL,

            video_id INTEGER NOT NULL,

            text TEXT NOT NULL,

            created_at INTEGER NOT NULL,

            FOREIGN KEY(user_id)
                REFERENCES users(id)
                ON DELETE CASCADE,

            FOREIGN KEY(video_id)
                REFERENCES videos(id)
                ON DELETE CASCADE
        )
    """)

    # ========================================================
    # FOLLOWERS
    # ========================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS followers (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            follower_id INTEGER NOT NULL,

            following_id INTEGER NOT NULL,

            created_at INTEGER NOT NULL,

            UNIQUE(follower_id, following_id),

            FOREIGN KEY(follower_id)
                REFERENCES users(id)
                ON DELETE CASCADE,

            FOREIGN KEY(following_id)
                REFERENCES users(id)
                ON DELETE CASCADE
        )
    """)

    # ========================================================
    # NOTIFICATIONS
    # ========================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notifications (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            user_id INTEGER NOT NULL,

            sender_id INTEGER,

            notification_type TEXT NOT NULL,

            video_id INTEGER,

            message TEXT DEFAULT '',

            is_read INTEGER DEFAULT 0,

            created_at INTEGER NOT NULL,

            FOREIGN KEY(user_id)
                REFERENCES users(id)
                ON DELETE CASCADE,

            FOREIGN KEY(sender_id)
                REFERENCES users(id)
                ON DELETE SET NULL,

            FOREIGN KEY(video_id)
                REFERENCES videos(id)
                ON DELETE SET NULL
        )
    """)

    # ========================================================
    # VIDEO VIEWS
    # ========================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS video_views (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            video_id INTEGER NOT NULL,

            user_id INTEGER,

            ip_address TEXT,

            created_at INTEGER NOT NULL,

            FOREIGN KEY(video_id)
                REFERENCES videos(id)
                ON DELETE CASCADE,

            FOREIGN KEY(user_id)
                REFERENCES users(id)
                ON DELETE SET NULL
        )
    """)

    # ========================================================
    # SEARCH HISTORY
    # ========================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS search_history (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            user_id INTEGER,

            query TEXT NOT NULL,

            created_at INTEGER NOT NULL,

            FOREIGN KEY(user_id)
                REFERENCES users(id)
                ON DELETE CASCADE
        )
    """)

    # ========================================================
    # INDEXES
    # ========================================================

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS
        idx_videos_user
        ON videos(user_id)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS
        idx_videos_created
        ON videos(created_at)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS
        idx_comments_video
        ON comments(video_id)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS
        idx_likes_video
        ON likes(video_id)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS
        idx_followers_following
        ON followers(following_id)
    """)

    # ========================================================
    # ADD is_short COLUMN TO EXISTING DATABASE
    # ========================================================

    columns = connection.execute(
        "PRAGMA table_info(videos)"
    ).fetchall()

    column_names = [
        column["name"]
        for column in columns
    ]

    if "is_short" not in column_names:

        connection.execute(
            """
            ALTER TABLE videos
            ADD COLUMN is_short INTEGER DEFAULT 0
            """
        )

    connection.commit()

    connection.close()







# ============================================================
# DATABASE TEST
# ============================================================

def database_test():

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type='table'
        ORDER BY name
    """)

    tables = cursor.fetchall()

    connection.close()

    return [
        row["name"]
        for row in tables
    ]
