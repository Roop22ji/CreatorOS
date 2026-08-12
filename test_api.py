import requests


API = "http://127.0.0.1:5000"


def register():

    print()
    print("REGISTER TEST")
    print("=" * 50)

    data = {

        "username": "creator_test",

        "email": "creator@test.com",

        "password": "12345678",

        "display_name": "Creator Test"
    }

    response = requests.post(

        API + "/api/auth/register",

        json=data
    )

    print(
        "Status:",
        response.status_code
    )

    print(
        response.text
    )


def login():

    print()
    print("LOGIN TEST")
    print("=" * 50)

    data = {

        "login":
            "creator_test",

        "password":
            "12345678"
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


if __name__ == "__main__":

    register()

    login()