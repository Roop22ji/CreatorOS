import os
import requests


# ============================================================
# CONFIGURATION
# ============================================================

API = "http://127.0.0.1:5000"

USERNAME = "creator_test"

PASSWORD = "12345678"


# ============================================================
# LOGIN
# ============================================================

def login():

    print()
    print("=" * 60)
    print("LOGIN")
    print("=" * 60)

    data = {

        "login": USERNAME,

        "password": PASSWORD
    }

    response = requests.post(

        API + "/api/auth/login",

        json=data
    )

    print(
        "Status:",
        response.status_code
    )

    print(
        response.text
    )

    if response.status_code != 200:

        print()
        print(
            "LOGIN FAILED"
        )

        return None

    result = response.json()

    return result["token"]


# ============================================================
# UPLOAD VIDEO
# ============================================================

def upload_video(token):

    print()
    print("=" * 60)
    print("VIDEO UPLOAD TEST")
    print("=" * 60)

    # --------------------------------------------------------
    # CHANGE THIS PATH
    # --------------------------------------------------------
    #
    # Put an MP4 video somewhere on your PC.
    #
    # Example:
    #
    # C:\Users\SAHIL\Desktop\test.mp4
    #
    # Then change the path below.
    #

    video_path = (
        r"C:\Users\SAHIL\Desktop\test.mp4"
    )

    if not os.path.exists(
        video_path
    ):

        print()

        print(
            "VIDEO FILE NOT FOUND:"
        )

        print(
            video_path
        )

        print()

        print(
            "Put an MP4 file at that location "
            "or change video_path in this file."
        )

        return None

    print(
        "Uploading:"
    )

    print(
        video_path
    )

    try:

        with open(
            video_path,
            "rb"
        ) as video:

            files = {

                "video": (

                    os.path.basename(
                        video_path
                    ),

                    video,

                    "video/mp4"
                )
            }

            data = {

                "title":
                    "My First Creator Video",

                "description":
                    "This is my first video on Creator Platform."
            }

            headers = {

                "Authorization":
                    "Bearer " + token
            }

            response = requests.post(

                API + "/api/videos",

                headers=headers,

                data=data,

                files=files,

                timeout=300
            )

    except Exception as error:

        print()
        print(
            "UPLOAD ERROR:"
        )

        print(
            error
        )

        return None

    print()
    print(
        "Status:",
        response.status_code
    )

    print(
        response.text
    )

    if response.status_code not in (
        200,
        201
    ):

        print()
        print(
            "UPLOAD FAILED"
        )

        return None

    result = response.json()

    return result


# ============================================================
# GET VIDEO FEED
# ============================================================

def get_videos():

    print()
    print("=" * 60)
    print("VIDEO FEED")
    print("=" * 60)

    response = requests.get(

        API + "/api/videos",

        timeout=20
    )

    print(
        "Status:",
        response.status_code
    )

    print()

    print(
        response.text
    )

    return response


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    print()
    print("=" * 60)
    print("CREATOR PLATFORM VIDEO TEST")
    print("=" * 60)

    token = login()

    if not token:

        print()

        print(
            "Cannot continue because login failed."
        )

        raise SystemExit

    print()

    print(
        "JWT TOKEN RECEIVED"
    )

    print()

    result = upload_video(
        token
    )

    print()

    get_videos()

    print()

    print("=" * 60)

    print(
        "VIDEO TEST FINISHED"
    )

    print("=" * 60)