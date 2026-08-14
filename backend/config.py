import os

from dotenv import load_dotenv

load_dotenv()





class Config:
    # ---------------------------------------------------------
    # BASIC APPLICATION SETTINGS
    # ---------------------------------------------------------

    APP_NAME = "CreatorOS"

    import os

    YOUTUBE_API_KEY = os.environ.get(
        "YOUTUBE_API_KEY"
    )

    



    # IMPORTANT:
    # Change this before making the application public.
    SECRET_KEY = os.environ.get(
        "CREATOR_SECRET_KEY",
        "creator-platform-development-secret-change-this"
    )

    # ---------------------------------------------------------
    # DATABASE
    # ---------------------------------------------------------

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    DATABASE_PATH = os.path.join(
        BASE_DIR,
        "creator.db"
    )

    # ---------------------------------------------------------
    # SERVER
    # ---------------------------------------------------------

    HOST = "0.0.0.0"

    PORT = 5000

    DEBUG = True

    # ---------------------------------------------------------
    # UPLOAD SETTINGS
    # ---------------------------------------------------------

    UPLOAD_FOLDER = os.path.join(
        BASE_DIR,
        "uploads"
    )

    MAX_UPLOAD_SIZE = 500 * 1024 * 1024  # 500 MB

    # ---------------------------------------------------------
    # TOKEN SETTINGS
    # ---------------------------------------------------------

    TOKEN_EXPIRATION_DAYS = 7

    # ---------------------------------------------------------
    # ALLOWED VIDEO EXTENSIONS
    # ---------------------------------------------------------

    ALLOWED_VIDEO_EXTENSIONS = {
        "mp4",
        "mov",
        "webm",
        "mkv",
        "avi"
    }

    # ---------------------------------------------------------
    # ALLOWED IMAGE EXTENSIONS
    # ---------------------------------------------------------

    ALLOWED_IMAGE_EXTENSIONS = {
        "jpg",
        "jpeg",
        "png",
        "webp"
    }


    

config = Config()
