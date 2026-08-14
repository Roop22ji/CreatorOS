import os
import time
import re
import uuid
import cv2
import random
import requests
from flask import (
    Flask,
    request,
    jsonify,
    send_from_directory,
    render_template
)

from flask_cors import CORS

from werkzeug.utils import secure_filename

from config import config

from database import (
    initialize_database,
    get_connection,
    database_test
)

from auth import (
    hash_password,
    verify_password,
    create_token,
    login_required,
    get_current_user
)


# ============================================================
# APPLICATION
# ============================================================

app = Flask(
    __name__
)

CORS(
    app
)

app.config[
    "MAX_CONTENT_LENGTH"
] = config.MAX_UPLOAD_SIZE


# ============================================================
# CREATE DIRECTORIES
# ============================================================

os.makedirs(
    config.UPLOAD_FOLDER,
    exist_ok=True
)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def now():

    return int(
        time.time()
    )


def valid_username(username):

    return re.match(
        r"^[a-zA-Z0-9_]{3,30}$",
        username
    )


def valid_email(email):

    return re.match(
        r"^[^@\s]+@[^@\s]+\.[^@\s]+$",
        email
    )


def allowed_video(filename):

    if "." not in filename:

        return False

    extension = filename.rsplit(
        ".",
        1
    )[1].lower()

    return extension in (
        config.ALLOWED_VIDEO_EXTENSIONS
    )




# ============================================================
# AUTO VIDEO THUMBNAIL
# ============================================================

def create_video_thumbnail(
    video_path,
    output_folder
):

    try:

        capture = cv2.VideoCapture(
            video_path
        )

        if not capture.isOpened():

            print(
                "Could not open video for thumbnail:"
            )

            return None


        frame_count = int(
            capture.get(
                cv2.CAP_PROP_FRAME_COUNT
            )
        )

        fps = float(
            capture.get(
                cv2.CAP_PROP_FPS
            )
        )


        if frame_count <= 0:

            capture.release()

            return None


        # ----------------------------------------------------
        # Determine duration
        # ----------------------------------------------------

        duration = (
            frame_count / fps
            if fps > 0
            else 0
        )


        # ----------------------------------------------------
        # Choose a random point from 15%-85% of video
        # ----------------------------------------------------

        if duration > 2:

            random_time = random.uniform(
                duration * 0.15,
                duration * 0.85
            )

            capture.set(
                cv2.CAP_PROP_POS_MSEC,
                random_time * 1000
            )

        else:

            random_frame = random.randint(
                0,
                max(
                    0,
                    frame_count - 1
                )
            )

            capture.set(
                cv2.CAP_PROP_POS_FRAMES,
                random_frame
            )


        success, frame = capture.read()


        # ----------------------------------------------------
        # Fallback if random frame failed
        # ----------------------------------------------------

        if not success:

            capture.set(
                cv2.CAP_PROP_POS_FRAMES,
                frame_count // 2
            )

            success, frame = capture.read()


        capture.release()


        if not success:

            return None


        # ----------------------------------------------------
        # Create filename
        # ----------------------------------------------------

        thumbnail_filename = (
            str(uuid.uuid4())
            + ".jpg"
        )

        thumbnail_path = os.path.join(
            output_folder,
            thumbnail_filename
        )


        # ----------------------------------------------------
        # Save JPEG
        # ----------------------------------------------------

        saved = cv2.imwrite(
            thumbnail_path,
            frame,
            [
                cv2.IMWRITE_JPEG_QUALITY,
                85
            ]
        )


        if not saved:

            return None


        return thumbnail_filename


    except Exception as error:

        print(
            "Automatic thumbnail error:",
            error
        )

        return None


def user_to_dict(user):

    if not user:

        return None

    return {

        "id": user["id"],

        "username": user["username"],

        "email": user["email"]
            if "email" in user.keys()
            else "",

        "display_name": user["display_name"],

        "bio": user["bio"],

        "avatar": user["avatar"],

        "verified": bool(
            user["verified"]
        ),

        "created_at": user["created_at"]
    }

# ============================================================
# YOUTUBE API
# ============================================================

def get_youtube_videos(
    query="technology",
    limit=5
):

    print()
    print("========================================")
    print("YOUTUBE SEARCH STARTED")
    print("========================================")

    # --------------------------------------------------------
    # CHECK API KEY
    # --------------------------------------------------------

    api_key = config.YOUTUBE_API_KEY

    print(
        "YOUTUBE API KEY EXISTS:",
        bool(api_key)
    )

    if not api_key:

        print(
            "YOUTUBE ERROR: API KEY IS EMPTY"
        )

        return []


    # --------------------------------------------------------
    # REQUEST
    # --------------------------------------------------------

    url = (
        "https://www.googleapis.com/"
        "youtube/v3/search"
    )


    params = {

        "part":
            "snippet",

        "q":
            query,

        "type":
            "video",

        "maxResults":
            limit,

        "key":
            api_key,

        "regionCode":
            "IN"

    }


    try:

        print(
            "YOUTUBE QUERY:",
            query
        )

        response = requests.get(
            url,
            params=params,
            timeout=10
        )


        print(
            "YOUTUBE STATUS:",
            response.status_code
        )


        # ----------------------------------------------------
        # ERROR
        # ----------------------------------------------------

        if response.status_code != 200:

            print(
                "YOUTUBE API ERROR:"
            )

            print(
                response.text
            )

            return []


        data = response.json()


        print(
            "YOUTUBE ITEMS:",
            len(
                data.get(
                    "items",
                    []
                )
            )
        )


        videos = []


        # ----------------------------------------------------
        # BUILD VIDEOS
        # ----------------------------------------------------

        for item in data.get(
            "items",
            []
        ):

            video_id = (
                item
                .get("id", {})
                .get("videoId")
            )


            if not video_id:

                continue


            snippet = item.get(
                "snippet",
                {}
            )


            print(
                "YOUTUBE VIDEO:",
                video_id,
                snippet.get(
                    "title",
                    ""
                )
            )


            videos.append({

                "id":
                    "youtube_" +
                    video_id,

                "source":
                    "youtube",

                "youtube_id":
                    video_id,

                "video_url":
                    "https://www.youtube.com/embed/"
                    + video_id,

                "title":
                    snippet.get(
                        "title",
                        "YouTube Video"
                    ),

                "description":
                    snippet.get(
                        "description",
                        ""
                    ),

                "thumbnail":
                    snippet
                    .get("thumbnails", {})
                    .get("high", {})
                    .get("url", ""),

                "creator":
                {

                    "username":
                        snippet.get(
                            "channelTitle",
                            "YouTube"
                        )

                }

            })


        print(
            "YOUTUBE FINAL COUNT:",
            len(videos)
        )

        print(
            "========================================"
        )


        return videos


    except Exception as error:

        print(
            "YOUTUBE FETCH EXCEPTION:",
            repr(error)
        )

        return []



# ============================================================
# HOME / MAIN MOBILE APP
# ============================================================

@app.route("/")
def home():

    return render_template(
        "app.html"
    )


# ============================================================
# MOBILE WEB APP
# ============================================================

@app.route("/app")
def mobile_app():

    return render_template(
        "app.html"
    )
    
#=================================================
# HEALTH
# ============================================================

@app.route(
    "/api/health",
    methods=["GET"]
)
def health():

    return jsonify({

        "success": True,

        "message":
            "Creator Platform API is running",

        "app":
            config.APP_NAME,

        "version":
            "1.0.0"
    })


# ============================================================
# DATABASE STATUS
# ============================================================

@app.route(
    "/api/database",
    methods=["GET"]
)
def database_status():

    tables = database_test()

    return jsonify({

        "success": True,

        "tables": tables
    })


# ============================================================
# REGISTER
# ============================================================

@app.route(
    "/api/auth/register",
    methods=["POST"]
)
def register():

    data = request.get_json(
        silent=True
    ) or {}

    username = str(
        data.get("username", "")
    ).strip()

    email = str(
        data.get("email", "")
    ).strip().lower()

    password = str(
        data.get("password", "")
    )

    display_name = str(
        data.get("display_name", "")
    ).strip()


    # ========================================================
    # VALIDATION
    # ========================================================

    if not valid_username(username):

        return jsonify({
            "success": False,
            "error":
                "Username must contain 3-30 letters, numbers or _"
        }), 400


    if not valid_email(email):

        return jsonify({
            "success": False,
            "error":
                "Invalid email"
        }), 400


    if len(password) < 6:

        return jsonify({
            "success": False,
            "error":
                "Password must contain at least 6 characters"
        }), 400


    if not display_name:

        display_name = username


    # ========================================================
    # DATABASE
    # ========================================================

    connection = get_connection()

    try:

        existing = connection.execute(
            """
            SELECT id
            FROM users
            WHERE username = ?
               OR email = ?
            """,
            (
                username,
                email
            )
        ).fetchone()


        if existing:

            return jsonify({
                "success": False,
                "error":
                    "Username or email already exists"
            }), 409


        # ====================================================
        # CREATE USER
        # ====================================================

        password_hash = hash_password(
            password
        )


        cursor = connection.execute(
            """
            INSERT INTO users
            (
                username,
                email,
                password_hash,
                display_name,
                bio,
                avatar,
                verified,
                created_at
            )

            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                username,
                email,
                password_hash,
                display_name,
                "",
                "",
                0,
                now()
            )
        )


        connection.commit()


        user_id = cursor.lastrowid


        # ====================================================
        # GET CREATED USER
        # ====================================================

        user = connection.execute(
            """
            SELECT *
            FROM users
            WHERE id = ?
            """,
            (
                user_id,
            )
        ).fetchone()


        if not user:

            connection.rollback()

            return jsonify({
                "success": False,
                "error":
                    "Could not create account"
            }), 500


        token = create_token(
            user_id
        )


        return jsonify({

            "success": True,

            "message":
                "Account created successfully",

            "token":
                token,

            "user":
                user_to_dict(user)

        }), 201


    except Exception as error:

        connection.rollback()

        print(
            "REGISTER ERROR:",
            repr(error)
        )

        return jsonify({

            "success": False,

            "error":
                "Could not create account",

            "details":
                str(error)

        }), 500


    finally:

        connection.close()


# ============================================================
# LOGIN
# ============================================================

@app.route(
    "/api/auth/login",
    methods=["POST"]
)
def login():

    data = request.get_json(
        silent=True
    ) or {}

    login_value = str(
        data.get(
            "login",
            ""
        )
    ).strip().lower()

    password = str(
        data.get(
            "password",
            ""
        )
    )

    if not login_value or not password:

        return jsonify({

            "success": False,

            "error":
                "Login and password are required"

        }), 400

    connection = get_connection()

    user = connection.execute(
        """
        SELECT *
        FROM users

        WHERE
            LOWER(username) = ?
            OR
            LOWER(email) = ?
        """,
        (
            login_value,
            login_value
        )
    ).fetchone()

    connection.close()

    if not user:

        return jsonify({

            "success": False,

            "error":
                "Invalid username/email or password"

        }), 401

    if not verify_password(
        password,
        user["password_hash"]
    ):

        return jsonify({

            "success": False,

            "error":
                "Invalid username/email or password"

        }), 401

    token = create_token(
        user["id"]
    )

    return jsonify({

        "success": True,

        "message":
            "Login successful",

        "token":
            token,

        "user":
            user_to_dict(user)

    })


# ============================================================
# CURRENT USER
# ============================================================

@app.route(
    "/api/auth/me",
    methods=["GET"]
)
@login_required
def me(user):

    return jsonify({

        "success": True,

        "user":
            user_to_dict(user)

    })


# ============================================================
# LOGOUT
# ============================================================

@app.route(
    "/api/auth/logout",
    methods=["POST"]
)
@login_required
def logout(user):

    # JWT is stateless.
    # The mobile app simply deletes its token.

    return jsonify({

        "success": True,

        "message":
            "Logged out successfully"

    })


# ============================================================
# UPDATE PROFILE
# ============================================================

@app.route(
    "/api/users/me",
    methods=["PUT"]
)
@login_required
def update_profile(user):

    data = request.get_json(
        silent=True
    ) or {}

    display_name = str(
        data.get(
            "display_name",
            user["display_name"]
        )
    ).strip()

    bio = str(
        data.get(
            "bio",
            user["bio"]
        )
    ).strip()

    if len(display_name) > 100:

        return jsonify({

            "success": False,

            "error":
                "Display name is too long"

        }), 400

    if len(bio) > 500:

        return jsonify({

            "success": False,

            "error":
                "Bio is too long"

        }), 400

    connection = get_connection()

    connection.execute(
        """
        UPDATE users

        SET
            display_name = ?,
            bio = ?

        WHERE id = ?
        """,
        (
            display_name,
            bio,
            user["id"]
        )
    )

    connection.commit()

    updated = connection.execute(
        """
        SELECT *
        FROM users
        WHERE id = ?
        """,
        (user["id"],)
    ).fetchone()

    connection.close()

    return jsonify({

        "success": True,

        "user":
            user_to_dict(updated)

    })


# ============================================================
# PUBLIC PROFILE
# ============================================================

@app.route(
    "/api/users/<username>",
    methods=["GET"]
)
def public_profile(username):

    connection = get_connection()

    user = connection.execute(
        """
        SELECT
            id,
            username,
            display_name,
            bio,
            avatar,
            verified,
            created_at

        FROM users

        WHERE LOWER(username) = ?
        """,
        (
            username.lower(),
        )
    ).fetchone()

    if not user:

        connection.close()

        return jsonify({

            "success": False,

            "error":
                "User not found"

        }), 404

    followers = connection.execute(
        """
        SELECT COUNT(*) AS count
        FROM followers
        WHERE following_id = ?
        """,
        (user["id"],)
    ).fetchone()["count"]

    following = connection.execute(
        """
        SELECT COUNT(*) AS count
        FROM followers
        WHERE follower_id = ?
        """,
        (user["id"],)
    ).fetchone()["count"]

    videos = connection.execute(
        """
        SELECT
            id,
            title,
            description,
            filename,
            thumbnail,
            views,
            likes,
            comments_count,
            created_at

        FROM videos

        WHERE user_id = ?

        ORDER BY created_at DESC
        """,
        (user["id"],)
    ).fetchall()

    connection.close()

    return jsonify({

        "success": True,

        "user": {

            "id":
                user["id"],

            "username":
                user["username"],

            "display_name":
                user["display_name"],

            "bio":
                user["bio"],

            "avatar":
                user["avatar"],

            "verified":
                bool(user["verified"]),

            "followers":
                followers,

            "following":
                following,

            "created_at":
                user["created_at"]
        },

        "videos": [

            {

                "id":
                    video["id"],

                "title":
                    video["title"],

                "description":
                    video["description"],

                "video_url":
                    "/media/" +
                    video["filename"],

                "thumbnail":
                    video["thumbnail"],

                "views":
                    video["views"],

                "likes":
                    video["likes"],

                "comments":
                    video["comments_count"],

                "created_at":
                    video["created_at"]
            }

            for video in videos
        ]

    })


# ============================================================
# FOLLOW / UNFOLLOW USER
# ============================================================

@app.route(
    "/api/users/<username>/follow",
    methods=["POST"]
)
@login_required
def follow_user(
    user,
    username
):

    connection = get_connection()

    # --------------------------------------------------------
    # FIND TARGET USER
    # --------------------------------------------------------

    target = connection.execute(
        """
        SELECT
            id,
            username,
            display_name
        FROM users
        WHERE LOWER(username) = ?
        """,
        (
            username.lower(),
        )
    ).fetchone()

    if not target:

        connection.close()

        return jsonify({

            "success": False,

            "error":
                "User not found"

        }), 404


    # --------------------------------------------------------
    # PREVENT SELF-FOLLOW
    # --------------------------------------------------------

    if target["id"] == user["id"]:

        connection.close()

        return jsonify({

            "success": False,

            "error":
                "You cannot follow yourself"

        }), 400


    # --------------------------------------------------------
    # CHECK CURRENT FOLLOW STATE
    # --------------------------------------------------------

    existing = connection.execute(
        """
        SELECT id
        FROM followers
        WHERE follower_id = ?
          AND following_id = ?
        """,
        (
            user["id"],
            target["id"]
        )
    ).fetchone()


    # --------------------------------------------------------
    # UNFOLLOW
    # --------------------------------------------------------

    if existing:

        connection.execute(
            """
            DELETE FROM followers
            WHERE follower_id = ?
              AND following_id = ?
            """,
            (
                user["id"],
                target["id"]
            )
        )

        following = False


    # --------------------------------------------------------
    # FOLLOW
    # --------------------------------------------------------

    else:

        connection.execute(
            """
            INSERT INTO followers
            (
                follower_id,
                following_id,
                created_at
            )
            VALUES (?, ?, ?)
            """,
            (
                user["id"],
                target["id"],
                now()
            )
        )

        following = True


        # ----------------------------------------------------
        # CREATE NOTIFICATION
        # ----------------------------------------------------

        connection.execute(
            """
            INSERT INTO notifications
            (
                user_id,
                sender_id,
                notification_type,
                message,
                created_at
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                target["id"],
                user["id"],
                "follow",
                "started following you",
                now()
            )
        )


    connection.commit()


    # --------------------------------------------------------
    # FOLLOWER COUNT
    # --------------------------------------------------------

    follower_count = connection.execute(
        """
        SELECT COUNT(*) AS count
        FROM followers
        WHERE following_id = ?
        """,
        (
            target["id"],
        )
    ).fetchone()["count"]


    connection.close()


    return jsonify({

        "success": True,

        "following":
            following,

        "followers":
            follower_count

    })


# ============================================================
# FOLLOW STATUS
# ============================================================

@app.route(
    "/api/users/<username>/follow/status",
    methods=["GET"]
)
@login_required
def follow_status(
    user,
    username
):

    connection = get_connection()

    target = connection.execute(
        """
        SELECT id
        FROM users
        WHERE LOWER(username) = ?
        """,
        (
            username.lower(),
        )
    ).fetchone()

    if not target:

        connection.close()

        return jsonify({

            "success": False,

            "error":
                "User not found"

        }), 404


    following = connection.execute(
        """
        SELECT id
        FROM followers

        WHERE follower_id = ?
          AND following_id = ?
        """,
        (
            user["id"],
            target["id"]
        )
    ).fetchone() is not None


    connection.close()


    return jsonify({

        "success": True,

        "following":
            following

    })



# ============================================================
# FOLLOWING FEED
# ============================================================

@app.route(
    "/api/feed/following",
    methods=["GET"]
)
@login_required
def following_feed(user):

    connection = get_connection()

    videos = connection.execute(
        """
        SELECT

            videos.id,

            videos.title,

            videos.description,

            videos.filename,
            videos.thumbnail,
            videos.source,
            videos.youtube_id,
            videos.views,

            videos.likes,

            videos.comments_count,

            videos.created_at,

            users.id AS user_id,

            users.username,

            users.display_name,

            users.avatar,

            users.verified

        FROM videos

        JOIN users
            ON users.id = videos.user_id

        JOIN followers
            ON followers.following_id = videos.user_id

        WHERE
            followers.follower_id = ?

            AND

            videos.visibility = 'public'
            AND

            videos.is_short = 0

            

        ORDER BY
            videos.created_at DESC

        LIMIT 100
        """,
        (
            user["id"],
        )
    ).fetchall()

    connection.close()


    result = []

    for video in videos:

        result.append({

            "id":
                video["id"],

            "title":
                video["title"],

            "description":
                video["description"],

            "video_url":
                "/media/"
                + video["filename"],

            "thumbnail":
                video["thumbnail"],

            "views":
                video["views"],

            "likes":
                video["likes"],

            "comments":
                video["comments_count"],

            "created_at":
                video["created_at"],

            "creator": {

                "id":
                    video["user_id"],

                "username":
                    video["username"],

                "display_name":
                    video["display_name"],

                "avatar":
                    video["avatar"],

                "verified":
                    bool(
                        video["verified"]
                    )
            }

        })


    return jsonify({

        "success": True,

        "count":
            len(result),

        "videos":
            result

    })
# ============================================================
# NOTIFICATIONS
# ============================================================

@app.route(
    "/api/notifications",
    methods=["GET"]
)
@login_required
def notifications(user):

    connection = get_connection()

    rows = connection.execute(
        """
        SELECT

            notifications.id,

            notifications.notification_type,

            notifications.message,

            notifications.video_id,

            notifications.is_read,

            notifications.created_at,

            users.username,

            users.display_name,

            users.avatar

        FROM notifications

        LEFT JOIN users
            ON users.id = notifications.sender_id

        WHERE
            notifications.user_id = ?

        ORDER BY
            notifications.created_at DESC

        LIMIT 100
        """,
        (
            user["id"],
        )
    ).fetchall()

    connection.close()


    return jsonify({

        "success": True,

        "notifications": [

            {

                "id":
                    row["id"],

                "type":
                    row["notification_type"],

                "message":
                    row["message"],

                "video_id":
                    row["video_id"],

                "is_read":
                    bool(
                        row["is_read"]
                    ),

                "created_at":
                    row["created_at"],

                "sender": {

                    "username":
                        row["username"],

                    "display_name":
                        row["display_name"],

                    "avatar":
                        row["avatar"]
                }

            }

            for row in rows
        ]

    })

# ============================================================
# MARK NOTIFICATIONS AS READ
# ============================================================

@app.route(
    "/api/notifications/read",
    methods=["POST"]
)
@login_required
def mark_notifications_read(user):

    connection = get_connection()

    connection.execute(
        """
        UPDATE notifications

        SET is_read = 1

        WHERE user_id = ?
        """,
        (
            user["id"],
        )
    )

    connection.commit()

    connection.close()

    return jsonify({

        "success": True

    })

# ============================================================
# DELETE OWN VIDEO
# ============================================================

@app.route(
    "/api/videos/<int:video_id>",
    methods=["DELETE"]
)
@login_required
def delete_video(
    user,
    video_id
):

    connection = get_connection()

    # ========================================================
    # FIND VIDEO
    # ========================================================

    video = connection.execute(
        """
        SELECT
            id,
            user_id,
            filename,
            
            thumbnail
        FROM videos
        WHERE id = ?
        """,
        (
            video_id,
        )
    ).fetchone()

    if not video:

        connection.close()

        return jsonify({

            "success": False,

            "error":
                "Video not found"

        }), 404

    # ========================================================
    # SECURITY
    # ========================================================
    # User can delete ONLY their own video.

    if video["user_id"] != user["id"]:

        connection.close()

        return jsonify({

            "success": False,

            "error":
                "You can only delete your own videos"

        }), 403

    # ========================================================
    # FILE PATH
    # ========================================================

    video_path = os.path.join(
        config.UPLOAD_FOLDER,
        video["filename"]
    )

    thumbnail_filename = video["thumbnail"]

    thumbnail_path = None

    if thumbnail_filename:

        # Database stores something like:
        # /media/abc.jpg

        thumbnail_name = (
            thumbnail_filename
            .replace("/media/", "")
            .replace("\\media\\", "")
        )

        thumbnail_path = os.path.join(
            config.UPLOAD_FOLDER,
            thumbnail_name
        )

    # ========================================================
    # DELETE DATABASE RECORD
    # ========================================================

    try:

        connection.execute(
            """
            DELETE FROM videos
            WHERE id = ?
            """,
            (
                video_id,
            )
        )

        connection.commit()

    except Exception as error:

        connection.rollback()
        connection.close()

        return jsonify({

            "success": False,

            "error":
                "Could not delete video",

            "details":
                str(error)

        }), 500

    connection.close()

    # ========================================================
    # DELETE VIDEO FILE
    # ========================================================

    try:

        if os.path.exists(video_path):

            os.remove(
                video_path
            )

    except Exception as error:

        print(
            "Could not delete video file:",
            error
        )

    # ========================================================
    # DELETE THUMBNAIL
    # ========================================================

    try:

        if thumbnail_path:

            if os.path.exists(
                thumbnail_path
            ):

                os.remove(
                    thumbnail_path
                )

    except Exception as error:

        print(
            "Could not delete thumbnail:",
            error
        )

    # ========================================================
    # RESPONSE
    # ========================================================

    return jsonify({

        "success": True,

        "message":
            "Video deleted successfully",

        "video_id":
            video_id

    })

# ============================================================
# UPLOAD VIDEO
# ============================================================

@app.route(
    "/api/videos",
    methods=["POST"]
)
@login_required
def upload_video(user):

    content_type = str(
        request.form.get(
            "content_type",
            "video"
        )
    ).lower().strip()

    is_short_value = str(
        request.form.get(
            "is_short",
            ""
        )
    ).lower().strip()


    if is_short_value in (
        "true",
        "1",
        "yes",
        "on"
    ):
        is_short = 1

    elif content_type in (
        "short",
        "shorts"
    ):
        is_short = 1

    else:
        is_short = 0

    content_type = request.form.get(
        "content_type",
        "video"
    ).lower().strip()


    if content_type == "short":
        is_short = 1
    else:
        is_short = 0

    video_file = request.files.get(
        "video"
    )

    thumbnail_file = request.files.get(
        "thumbnail"
    )

    title = str(
        request.form.get(
            "title",
            ""
        )
    ).strip()

    description = str(
        request.form.get(
            "description",
            ""
        )
    ).strip()

    # is_short = int(
    #     request.form.get(
    #         "is_short",
    #         0
    #     )
    # )

    # is_short = request.form.get(
    #     "is_short",
    #     "0"
    # ).lower() in (
    #     "1",
    #     "true",
    #     "yes",
    #     "on"
    # )

    # ========================================================
    # SHORT STATUS
    # ========================================================

    # Frontend can send:
    # is_short = "true"
    # is_short = "1"
    # is_short = "on"
    #
    # Anything else means normal video.

    # ========================================================
    # SHORT STATUS
    # ========================================================

    content_type = str(
        request.form.get(
            "content_type",
            "video"
        )
    ).lower().strip()


    if content_type in ("short", "shorts"):
        is_short = 1
    else:
        is_short = 0

    # ========================================================
    # VALIDATION
    # ========================================================

    if not video_file:

        return jsonify({

            "success": False,

            "error":
                "Video file is required"

        }), 400

    if not title:

        return jsonify({

            "success": False,

            "error":
                "Video title is required"

        }), 400

    if not allowed_video(
        video_file.filename
    ):

        return jsonify({

            "success": False,

            "error":
                "Unsupported video format"

        }), 400

    # ========================================================
    # SAVE VIDEO
    # ========================================================

    original_name = secure_filename(
        video_file.filename
    )

    extension = original_name.rsplit(
        ".",
        1
    )[1].lower()

    filename = (
        str(uuid.uuid4())
        + "."
        + extension
    )

    destination = os.path.join(
        config.UPLOAD_FOLDER,
        filename
    )

    thumbnail_filename = None

    try:

        video_file.save(
            destination
        )

        # ====================================================
        # CUSTOM THUMBNAIL
        # ====================================================

        if thumbnail_file:

            thumbnail_original = secure_filename(
                thumbnail_file.filename
            )

            if "." in thumbnail_original:

                thumbnail_extension = (
                    thumbnail_original
                    .rsplit(".", 1)[1]
                    .lower()
                )

                if thumbnail_extension in (
                    "jpg",
                    "jpeg",
                    "png",
                    "webp"
                ):

                    thumbnail_filename = (
                        str(uuid.uuid4())
                        + "."
                        + thumbnail_extension
                    )

                    thumbnail_destination = os.path.join(
                        config.UPLOAD_FOLDER,
                        thumbnail_filename
                    )

                    thumbnail_file.save(
                        thumbnail_destination
                    )

        # ====================================================
        # AUTOMATIC THUMBNAIL
        # ====================================================

        if not thumbnail_filename:

            thumbnail_filename = create_video_thumbnail(
                destination,
                config.UPLOAD_FOLDER
            )

    except Exception as error:

        # Remove video if database/save process fails
        try:
            if os.path.exists(destination):
                os.remove(destination)
        except Exception:
            pass

        return jsonify({

            "success": False,

            "error":
                "Could not save video",

            "details":
                str(error)

        }), 500

    # ========================================================
    # DATABASE
    # ========================================================

    connection = get_connection()

    try:

        print("USER ID:", user["id"])

        print("VIDEO DATA:")
        print(title)
        print(description)
        print(filename)
        print(thumbnail_filename)
        print(is_short)


        cursor = connection.execute(
            """
            INSERT INTO videos
            (
                user_id,
                title,
                description,
                filename,
                thumbnail,
                is_short,
                source,
                youtube_id,
                youtube_url,
                created_at
            )

            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user["id"],
                title,
                description,
                filename,
                (
                    "/media/" + thumbnail_filename
                    if thumbnail_filename
                    else ""
                ),
                is_short,
                "creator",
                None,
                None,
                now()
            )
        )


        connection.commit()

        video_id = cursor.lastrowid


    except Exception as error:

        print(
            "DATABASE INSERT ERROR:",
            error
        )

        connection.rollback()
        connection.close()

        return jsonify({

            "success": False,

            "error": str(error)

        }), 500


        connection.close()

        return jsonify({

            "success": False,
            "error": str(error)

        }), 500

    connection.close()

    # ========================================================
    # RESPONSE
    # ========================================================

    return jsonify({

        "success": True,

        "message":
            "Short uploaded successfully"
            if is_short
            else
            "Video uploaded successfully",

        "video_id":
            video_id,

        "is_short":
            bool(is_short),

        "source":
            "creator",

        "video_url":
            "/media/" + filename,

        "thumbnail":
            (
                "/media/" + thumbnail_filename
                if thumbnail_filename
                else None
            )

    }), 201

# ============================================================
# VIDEO FEED
# ============================================================

@app.route(
    "/api/videos",
    methods=["GET"]
)
def videos():

    search = request.args.get(
        "q",
        ""
    ).strip()

    connection = get_connection()

    if search:

        rows = connection.execute(
            """
            SELECT

                videos.id,

                videos.title,

                videos.description,

                videos.filename,

                videos.source,
                videos.youtube_id,
                videos.youtube_url,

                videos.thumbnail,

                videos.views,

                videos.likes,

                videos.comments_count,

                videos.created_at,

                users.id AS user_id,

                users.username,

                users.display_name,

                users.avatar,

                users.verified

            FROM videos

            JOIN users
                ON users.id = videos.user_id

            WHERE

                videos.visibility = 'public'

                AND

                videos.is_short = 0

                AND

                (
                    videos.title LIKE ?
                    OR
                    videos.description LIKE ?
                    OR
                    users.username LIKE ?
                )

            ORDER BY
                videos.created_at DESC

            LIMIT 100
            """,
            (
                "%" + search + "%",
                "%" + search + "%",
                "%" + search + "%"
            )
        ).fetchall()

    else:

        rows = connection.execute(
            """
            SELECT

                videos.id,

                videos.title,

                videos.description,

                videos.filename,

                videos.source,
                videos.youtube_id,
                videos.youtube_url,

                videos.thumbnail,

                videos.views,

                videos.likes,

                videos.comments_count,

                videos.created_at,

                users.id AS user_id,

                users.username,

                users.display_name,

                users.avatar,

                users.verified

            FROM videos

            JOIN users
                ON users.id = videos.user_id

            WHERE
                videos.visibility = 'public'

            ORDER BY
                videos.created_at DESC

            LIMIT 100
            """
        ).fetchall()

    connection.close()

    result = []

    for video in rows:

        result.append({

            "id":
                video["id"],

            "title":
                video["title"],

            "description":
                video["description"],

            "video_url":
            (
                "/media/" + video["filename"]
                if video["source"] != "youtube"
                else None
            ),
            "source":
                video["source"],

            "youtube_id":
                video["youtube_id"],

            "youtube_url":
                video["youtube_url"],

            "thumbnail":
                video["thumbnail"],

            "views":
                video["views"],

            "likes":
                video["likes"],

            "comments":
                video["comments_count"],

            "created_at":
                video["created_at"],

            "creator": {

                "id":
                    video["user_id"],

                "username":
                    video["username"],

                "display_name":
                    video["display_name"],

                "avatar":
                    video["avatar"],

                "verified":
                    bool(video["verified"])
            }

        })

    return jsonify({

        "success": True,

        "count":
            len(result),

        "videos":
            result

    })


# ============================================================
# GET SINGLE VIDEO
# ============================================================

@app.route(
    "/api/videos/<int:video_id>",
    methods=["GET"]
)
def get_video(video_id):

    connection = get_connection()

    video = connection.execute(
        """
        SELECT

            videos.id,
            videos.title,
            videos.description,
            videos.filename,
            videos.thumbnail,
            videos.views,
            videos.likes,
            videos.comments_count,
            videos.created_at,

            users.id AS user_id,
            users.username,
            users.display_name,
            users.avatar,
            users.verified

        FROM videos

        JOIN users
            ON users.id = videos.user_id

        WHERE videos.id = ?

          AND videos.visibility = 'public'

          AND videos.is_short = 0

        """,
        (
            video_id,
        )
    ).fetchone()

    if not video:

        connection.close()

        return jsonify({

            "success": False,

            "error":
                "Video not found"

        }), 404


    # --------------------------------------------------------
    # INCREMENT VIEW COUNT
    # --------------------------------------------------------

    connection.execute(
        """
        UPDATE videos

        SET views = views + 1

        WHERE id = ?
        """,
        (
            video_id,
        )
    )

    connection.commit()


    # --------------------------------------------------------
    # READ UPDATED VIEW COUNT
    # --------------------------------------------------------

    updated_views = connection.execute(
        """
        SELECT views
        FROM videos
        WHERE id = ?
        """,
        (
            video_id,
        )
    ).fetchone()["views"]


    connection.close()


    return jsonify({

        "success": True,

        "id":
            video["id"],

        "title":
            video["title"],

        "description":
            video["description"],

        "video_url":
            "/media/" +
            video["filename"],

        "thumbnail":
            video["thumbnail"],

        "views":
            updated_views,

        "likes":
            video["likes"],

        "comments":
            video["comments_count"],

        "created_at":
            video["created_at"],

        "creator": {

            "id":
                video["user_id"],

            "username":
                video["username"],

            "display_name":
                video["display_name"],

            "avatar":
                video["avatar"],

            "verified":
                bool(
                    video["verified"]
                )

        }

    })


# ============================================================
# GET VIDEO COMMENTS
# ============================================================

@app.route(
    "/api/videos/<int:video_id>/comments",
    methods=["GET"]
)
def get_video_comments(video_id):

    connection = get_connection()

    # Make sure the video exists
    video = connection.execute(
        """
        SELECT id
        FROM videos
        WHERE id = ?
        """,
        (video_id,)
    ).fetchone()

    if not video:

        connection.close()

        return jsonify({
            "success": False,
            "error": "Video not found"
        }), 404

    rows = connection.execute(
        """
        SELECT
            comments.id,
            comments.text,
            comments.created_at,

            users.id AS user_id,
            users.username,
            users.display_name,
            users.avatar

        FROM comments

        JOIN users
            ON users.id = comments.user_id

        WHERE comments.video_id = ?

        ORDER BY comments.created_at ASC
        """,
        (video_id,)
    ).fetchall()

    connection.close()

    return jsonify([
        {
            "id": row["id"],
            "text": row["text"],
            "created_at": row["created_at"],
            "user_id": row["user_id"],
            "username": row["username"],
            "display_name": row["display_name"],
            "avatar": row["avatar"]
        }
        for row in rows
    ])


# ============================================================
# ADD VIDEO COMMENT
# ============================================================

@app.route(
    "/api/videos/<int:video_id>/comments",
    methods=["POST"]
)
@login_required
def add_video_comment(
    user,
    video_id
):

    data = request.get_json(
        silent=True
    ) or {}

    text = str(
        data.get(
            "text",
            ""
        )
    ).strip()

    if not text:

        return jsonify({
            "success": False,
            "error": "Comment cannot be empty"
        }), 400

    if len(text) > 1000:

        return jsonify({
            "success": False,
            "error": "Comment is too long"
        }), 400

    connection = get_connection()

    video = connection.execute(
        """
        SELECT
            id,
            user_id
        FROM videos
        WHERE id = ?
        """,
        (video_id,)
    ).fetchone()

    if not video:

        connection.close()

        return jsonify({
            "success": False,
            "error": "Video not found"
        }), 404

    cursor = connection.execute(
        """
        INSERT INTO comments
        (
            video_id,
            user_id,
            text,
            created_at
        )
        VALUES (?, ?, ?, ?)
        """,
        (
            video_id,
            user["id"],
            text,
            now()
        )
    )

    # Keep comment count synchronized
    connection.execute(
        """
        UPDATE videos
        SET comments_count = (
            SELECT COUNT(*)
            FROM comments
            WHERE video_id = ?
        )
        WHERE id = ?
        """,
        (
            video_id,
            video_id
        )
    )

    connection.commit()

    comment_id = cursor.lastrowid

    connection.close()

    return jsonify({
        "success": True,
        "comment_id": comment_id,
        "message": "Comment added successfully"
    }), 201




# ============================================================
# LIKE / UNLIKE VIDEO
# ============================================================

@app.route(
    "/api/videos/<int:video_id>/like",
    methods=["POST"]
)
@login_required
def like_video(
    user,
    video_id
):

    connection = get_connection()


    # --------------------------------------------------------
    # CHECK VIDEO
    # --------------------------------------------------------

    video = connection.execute(
        """
        SELECT id
        FROM videos
        WHERE id = ?
        """,
        (
            video_id,
        )
    ).fetchone()


    if not video:

        connection.close()

        return jsonify({

            "success": False,

            "error":
                "Video not found"

        }), 404


    # --------------------------------------------------------
    # CHECK EXISTING LIKE
    # --------------------------------------------------------

    existing = connection.execute(
        """
        SELECT id
        FROM likes

        WHERE user_id = ?
          AND video_id = ?
        """,
        (
            user["id"],
            video_id
        )
    ).fetchone()


    # --------------------------------------------------------
    # UNLIKE
    # --------------------------------------------------------

    if existing:

        connection.execute(
            """
            DELETE FROM likes

            WHERE user_id = ?
              AND video_id = ?
            """,
            (
                user["id"],
                video_id
            )
        )

        liked = False


    # --------------------------------------------------------
    # LIKE
    # --------------------------------------------------------

    else:

        connection.execute(
            """
            INSERT INTO likes
            (
                user_id,
                video_id,
                created_at
            )

            VALUES (?, ?, ?)
            """,
            (
                user["id"],
                video_id,
                now()
            )
        )

        liked = True


    # --------------------------------------------------------
    # RECALCULATE TOTAL
    # --------------------------------------------------------

    total_likes = connection.execute(
        """
        SELECT COUNT(*) AS count
        FROM likes
        WHERE video_id = ?
        """,
        (
            video_id,
        )
    ).fetchone()["count"]


    # Keep videos.likes synchronized
    connection.execute(
        """
        UPDATE videos

        SET likes = ?

        WHERE id = ?
        """,
        (
            total_likes,
            video_id
        )
    )


    connection.commit()

    connection.close()


    return jsonify({

        "success": True,

        "liked":
            liked,

        "likes":
            total_likes

    })





# ============================================================
# SERVE VIDEO FILE
# ============================================================

@app.route(
    "/media/<path:filename>"
)
def media(filename):

    return send_from_directory(
        config.UPLOAD_FOLDER,
        filename
    )


# ============================================================
# CREATOR BOOST
# ============================================================

@app.route(
    "/api/creator/boost",
    methods=["GET"]
)
@login_required
def creator_boost(user):

    connection = get_connection()

    videos = connection.execute(
        """
        SELECT
            id,
            title,
            views,
            likes,
            comments_count,
            created_at
        FROM videos
        WHERE user_id = ?
        ORDER BY created_at DESC
        """,
        (
            user["id"],
        )
    ).fetchall()

    connection.close()

    total_score = 0

    best_video = None
    best_score = 0

    current_time = now()

    video_results = []

    for video in videos:

        views = int(
            video["views"] or 0
        )

        likes = int(
            video["likes"] or 0
        )

        comments = int(
            video["comments_count"] or 0
        )

        age_seconds = max(
            0,
            current_time -
            int(
                video["created_at"] or
                current_time
            )
        )

        age_hours = (
            age_seconds / 3600
        )

        freshness = max(
            0,
            100 -
            (age_hours * 2)
        )

        score = (
            views * 1
            +
            likes * 5
            +
            comments * 8
            +
            freshness
        )

        score = int(
            round(score)
        )

        total_score += score

        if score > best_score:

            best_score = score

            best_video = {
                "id":
                    video["id"],

                "title":
                    video["title"],

                "score":
                    score,

                "views":
                    views,

                "likes":
                    likes,

                "comments":
                    comments
            }

        video_results.append({

            "id":
                video["id"],

            "title":
                video["title"],

            "score":
                score,

            "views":
                views,

            "likes":
                likes,

            "comments":
                comments

        })

    # --------------------------------------------------------
    # BOOST LEVEL
    # --------------------------------------------------------

    if total_score >= 300:

        level = 3
        level_name = "🌟 Level 3"

    elif total_score >= 150:

        level = 2
        level_name = "🔥 Level 2"

    elif total_score >= 50:

        level = 1
        level_name = "🚀 Level 1"

    else:

        level = 0
        level_name = "🌱 New Creator"

    # --------------------------------------------------------
    # NEXT LEVEL
    # --------------------------------------------------------

    if level == 0:

        next_score = 50

    elif level == 1:

        next_score = 150

    elif level == 2:

        next_score = 300

    else:

        next_score = None

    return jsonify({

        "success":
            True,

        "boost": {

            "score":
                int(total_score),

            "level":
                level,

            "level_name":
                level_name,

            "next_score":
                next_score,

            "best_video":
                best_video,

            "videos":
                video_results
        }

    })

# ============================================================
# CREATOR STUDIO ANALYTICS
# ============================================================

@app.route(
    "/api/creator/studio",
    methods=["GET"]
)
@login_required
def creator_studio(user):

    connection = get_connection()

    # --------------------------------------------------------
    # VIDEO COUNT + TOTAL VIEWS
    # --------------------------------------------------------

    video_stats = connection.execute(
        """
        SELECT
            COUNT(*) AS video_count,
            COALESCE(SUM(views), 0) AS total_views
        FROM videos
        WHERE user_id = ?
        """,
        (user["id"],)
    ).fetchone()

    # --------------------------------------------------------
    # TOTAL LIKES
    # --------------------------------------------------------

    like_stats = connection.execute(
        """
        SELECT
            COALESCE(SUM(likes), 0) AS total_likes
        FROM videos
        WHERE user_id = ?
        """,
        (user["id"],)
    ).fetchone()

    # --------------------------------------------------------
    # FOLLOWERS
    # --------------------------------------------------------

    follower_stats = connection.execute(
        """
        SELECT
            COUNT(*) AS follower_count
        FROM followers
        WHERE following_id = ?
        """,
        (user["id"],)
    ).fetchone()

    # --------------------------------------------------------
    # FOLLOWING
    # --------------------------------------------------------

    following_stats = connection.execute(
        """
        SELECT
            COUNT(*) AS following_count
        FROM followers
        WHERE follower_id = ?
        """,
        (user["id"],)
    ).fetchone()

    # --------------------------------------------------------
    # CREATOR VIDEOS
    # --------------------------------------------------------

    videos = connection.execute(
        """
        SELECT
            id,
            title,
            description,
            filename,
            thumbnail,
            views,
            likes,
            comments_count,
            created_at
        FROM videos
        WHERE user_id = ?
        ORDER BY created_at DESC
        """,
        (user["id"],)
    ).fetchall()

    connection.close()

    return jsonify({
        "success": True,

        "analytics": {
            "videos":
                video_stats["video_count"],

            "views":
                video_stats["total_views"],

            "likes":
                like_stats["total_likes"],

            "followers":
                follower_stats["follower_count"],

            "following":
                following_stats["following_count"]
        },

        "videos": [
            {
                "id":
                    video["id"],

                "title":
                    video["title"],

                "description":
                    video["description"],

                "source":
                    video["source"],


                "youtube_id":
                    video["youtube_id"],


                "video_url":
                    (
                        "/media/" + video["filename"]
                        if video["filename"]
                        else None
                    ),

                "thumbnail":
                    video["thumbnail"],

                "views":
                    video["views"],

                "likes":
                    video["likes"],

                "comments":
                    video["comments_count"],

                "created_at":
                    video["created_at"]
            }

            for video in videos
        ]
    })




# ============================================================
# FOR YOU FEED + CREATOR BOOST
# ============================================================

@app.route(
    "/api/feed/for-you",
    methods=["GET"]
)
def for_you_feed():

    

    connection = get_connection()

    # --------------------------------------------------------
    # Get public videos
    # --------------------------------------------------------

    rows = connection.execute(
        """
        SELECT

            videos.id,
            videos.title,
            videos.description,
            videos.filename,
            videos.source,
            videos.youtube_id,
            videos.youtube_url,
            videos.thumbnail,
            videos.views,
            videos.likes,
            videos.comments_count,
            videos.created_at,
            

            users.id AS user_id,
            users.username,
            users.display_name,
            users.avatar,
            users.verified

        FROM videos

        JOIN users
            ON users.id = videos.user_id

        WHERE
            videos.visibility = 'public'

            AND

            videos.is_short = 0

        ORDER BY
            videos.created_at DESC

        LIMIT 200
        """
    ).fetchall()


    # --------------------------------------------------------
    # Calculate Creator Boost level for every creator
    # --------------------------------------------------------

    creator_stats = {}

    for video in rows:

        creator_id = video["user_id"]


        views = int(
            video["views"] or 0
            )

        likes = int(
                video["likes"] or 0
            )

        comments = int(
                video["comments_count"] or 0
            )


        if creator_id not in creator_stats:

            creator_stats[
                creator_id
            ] = {

                "views": 0,

                "likes": 0,

                "comments": 0

            }


        creator_stats[
            creator_id
        ]["views"] += views


        creator_stats[
            creator_id
        ]["likes"] += likes


        creator_stats[
            creator_id
        ]["comments"] += comments


    # --------------------------------------------------------
    # Convert score → boost level
    # --------------------------------------------------------

    def get_boost_level(
        score,
        total_views,
        total_likes,
        total_comments
    ):

        # New creators always receive
        # an initial discovery opportunity.
        if total_views < 20:

            return 1

        engagement_rate = 0

        if total_views > 0:

            engagement_rate = (
                (
                    total_likes +
                    total_comments
                )
                /
                total_views
            ) * 100


        # Strong engagement
        if (
            total_views >= 100
            and engagement_rate >= 8
        ):

            return 3


        # Growing creator
        if (
            total_views >= 20
            and engagement_rate >= 5
        ):

            return 2


        # Still eligible for beginner boost
        return 1


    # --------------------------------------------------------
    # Score each video
    # --------------------------------------------------------

    current_time = now()

    scored_videos = []


    for video in rows:

        views = int(
            video["views"] or 0
        )

        likes = int(
            video["likes"] or 0
        )

        comments = int(
            video["comments_count"] or 0
        )

        created_at = int(
            video["created_at"] or
            current_time
        )

        age_hours = max(
            0,
            (
                current_time -
                created_at
            ) / 3600
        )


        # ----------------------------------------------------
        # Normal recommendation score
        # ----------------------------------------------------

        engagement_score = (
            views * 0.5
            +
            likes * 5
            +
            comments * 8
        )


        freshness_score = max(
            0,
            100 -
            (age_hours * 2)
        )


        # ----------------------------------------------------
        # Creator boost
        # ----------------------------------------------------

        creator = creator_stats.get(
                video["user_id"],
                {
                    "views": 0,
                    "likes": 0,
                    "comments": 0
                }
            )


        creator_total_score = (
            creator["views"]
            +
            (
                creator["likes"]
                * 5
            )
            +
            (
                creator["comments"]
                * 8
            )
        )


        boost_level = get_boost_level(
                creator_total_score,
                creator["views"],
                creator["likes"],
                creator["comments"]
            )

        boost_bonus = {
            0: 0,
            1: 40,
            2: 80,
            3: 120
        }.get(
            boost_level,
            0
        )


        # ----------------------------------------------------
        # Beginner protection
        #
        # Small creators receive a modest extra chance.
        # The bonus is capped.
        # ----------------------------------------------------

        beginner_bonus = 0

        if views < 100:

            beginner_bonus = 35

        elif views < 500:

            beginner_bonus = 15


        final_score = (
            engagement_score
            +
            freshness_score
            +
            boost_bonus
            +
            beginner_bonus
        )


        scored_videos.append({

            "score":
                final_score,

            "video":
                video,

            "boost_level":
                boost_level,

            "boosted":
                boost_level > 0

        })


    # --------------------------------------------------------
    # Sort recommendations
    # --------------------------------------------------------

    scored_videos.sort(
        key=lambda item:
            item["score"],
        reverse=True
    )


    # --------------------------------------------------------
    # Build response
    # --------------------------------------------------------

    result = []


    for item in scored_videos[:100]:

        video = item["video"]

        result.append({

            "id":
                video["id"],

            "title":
                video["title"],

            "description":
                video["description"],

            "video_url":
                (
                    "/media/" + video["filename"]
                    if video["source"] != "youtube"
                    else ""
                ),

            "source":
                video["source"],

            "youtube_id":
                video["youtube_id"],

            "youtube_url":
                video["youtube_url"],

            "thumbnail":
                video["thumbnail"],

            "views":
                video["views"],

            "likes":
                video["likes"],

            "comments":
                video["comments_count"],

            "created_at":
                video["created_at"],

            "boosted":
                item["boosted"],

            "boost_level":
                item["boost_level"],

            "creator": {

                "id":
                    video["user_id"],

                "username":
                    video["username"],

                "display_name":
                    video["display_name"],

                "avatar":
                    video["avatar"],

                "verified":
                    bool(
                        video["verified"]
                    )

            }

        })

    topics = [

        "ravi kishan memes",
        "gaming",
        "Minecraft",
        "GTA 5 gameplay",
        "football highlights",
        "cricket",
        "AI technology",
        "technology news",
        "science",
        "space",
        "coding",
        "programming",
        "movies",
        "music",
        "funny shorts",
        "animals",
        "memes",
        "education",
        "fitness",
        "travel",
        "free fire",
        "basketball",
        "sports",

]

    youtube_videos = []


    selected_topics = random.sample(
        topics,
        23
    )


    for topic in selected_topics:

        videos = get_youtube_videos(
            topic,
            10
        )

        youtube_videos.extend(
            videos
        )

    print("YOUTUBE VIDEOS ADDED:")
    for y in youtube_videos:
        print(
            y["title"],
            y["youtube_id"]
        )

    print(
        "TOTAL YOUTUBE:",
        len(youtube_videos)
    )


    result.extend(
        youtube_videos
    )
    random.shuffle(result)

    return jsonify({

        "success":
            True,

        "count":
            len(result),

        "videos":
            result

    })


# ============================================================
# TRENDING FEED
# ============================================================

@app.route(
    "/api/feed/trending",
    methods=["GET"]
)
def trending_feed():

    connection = get_connection()

    videos = connection.execute(
        """
        SELECT

            videos.id,
            videos.title,
            videos.description,
            videos.filename,
            videos.thumbnail,
            videos.views,
            videos.likes,
            videos.comments_count,
            videos.created_at,

            users.id AS user_id,
            users.username,
            users.display_name,
            users.avatar,
            users.verified

        FROM videos

        JOIN users
            ON users.id = videos.user_id

        WHERE
            videos.visibility = 'public'

            AND

            videos.is_short = 0

        ORDER BY
            (
                (videos.views * 1) +
                (videos.likes * 5) +
                (videos.comments_count * 3)
            ) DESC,

            videos.created_at DESC

        LIMIT 100
        """
    ).fetchall()

    connection.close()

    result = []

    for video in videos:

        result.append({

            "id":
                video["id"],

            "title":
                video["title"],

            "description":
                video["description"],

            "video_url":
                "/media/" +
                video["filename"],

            "thumbnail":
                video["thumbnail"],

            "views":
                video["views"],

            "likes":
                video["likes"],

            "comments":
                video["comments_count"],

            "created_at":
                video["created_at"],

            "creator": {

                "id":
                    video["user_id"],

                "username":
                    video["username"],

                "display_name":
                    video["display_name"],

                "avatar":
                    video["avatar"],

                "verified":
                    bool(
                        video["verified"]
                    )

            }

        })


    return jsonify({

        "success":
            True,

        "count":
            len(result),

        "videos":
            result

    })



# ============================================================
# SHORTS FEED
# ============================================================

@app.route(
    "/api/shorts",
    methods=["GET"]
)
def shorts():

    connection = get_connection()

    rows = connection.execute(
        """
        SELECT

            videos.id,
            videos.title,
            videos.description,
            videos.filename,
            videos.thumbnail,
            videos.views,
            videos.likes,
            videos.created_at,
            videos.is_short,

            users.id AS user_id,
            users.username,
            users.display_name,
            users.avatar

        FROM videos

        JOIN users
            ON users.id = videos.user_id

        WHERE
            videos.visibility = 'public'

            AND

            videos.is_short = 1

        ORDER BY
            videos.created_at DESC

        LIMIT 50
        """
    ).fetchall()

    connection.close()

    result = []

    for video in rows:

        result.append({

            "id":
                video["id"],

            "title":
                video["title"],

            "description":
                video["description"],

            "video_url":
                "/media/" +
                video["filename"],

            "thumbnail":
                video["thumbnail"],

            "views":
                video["views"],

            "likes":
                video["likes"],

            "created_at":
                video["created_at"],

            "creator": {

                "id":
                    video["user_id"],

                "username":
                    video["username"],

                "display_name":
                    video["display_name"],

                "avatar":
                    video["avatar"]
            }

        })

    return jsonify({

        "success":
            True,

        "count":
            len(result),

        "shorts":
            result

    })



@app.route("/api/debug/videos")
def debug_videos():

    connection=get_connection()

    rows=connection.execute(
        """
        SELECT
            id,
            title,
            filename,
            is_short,
            visibility,
            video_type
        FROM videos
        ORDER BY id DESC
        """
    ).fetchall()

    connection.close()

    return jsonify([
        {
            "id":row["id"],
            "title":row["title"],
            "filename":row["filename"],
            "is_short":row["is_short"],
            "visibility":row["visibility"],
            "video_type":row["video_type"]
        }
        for row in rows
    ])


# ============================================================
# ERROR HANDLERS
# ============================================================

@app.errorhandler(413)
def file_too_large(error):

    return jsonify({

        "success": False,

        "error":
            "Video is too large. Maximum upload size is 500 MB."

    }), 413


@app.errorhandler(404)
def not_found(error):

    return jsonify({

        "success": False,

        "error":
            "The requested endpoint was not found",

        "path":
            request.path

    }), 404


# ============================================================
# START SERVER
# ============================================================

if __name__ == "__main__":

    print()
    print("=" * 60)
    print("       CREATOR PLATFORM SERVER")
    print("=" * 60)
    print()

    print("Initializing database...")

    initialize_database()

    print("Database ready.")

    print()

    print(
        "Database tables:"
    )

    for table in database_test():

        print(
            "  ✓",
            table
        )

    print()

    print(
        "Server:"
    )

    print(
        "  http://127.0.0.1:5000"
    )

    print()

    print(
        "API:"
    )

    print(
        "  http://127.0.0.1:5000/api/health"
    )

    print()

    print("=" * 60)

    print()

    app.run(

        host=config.HOST,

        port=config.PORT,

        debug=config.DEBUG
    )

# @app.route("/api/debug/videos")
# def debug_videos():

#     connection = get_connection()

#     rows = connection.execute(
#         """
#         SELECT 
#             id,
#             title,
#             is_short
#         FROM videos
#         ORDER BY id DESC
#         LIMIT 20
#         """
#     ).fetchall()

#     connection.close()

#     return jsonify([
#         {
#             "id": row["id"],
#             "title": row["title"],
#             "is_short": row["is_short"]
#         }
#         for row in rows
#     ])
