import time
from functools import wraps

import jwt

from flask import request, jsonify

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from config import config
from database import get_connection


# ============================================================
# PASSWORD FUNCTIONS
# ============================================================

def hash_password(password):

    return generate_password_hash(
        password
    )


def verify_password(password, password_hash):

    return check_password_hash(
        password_hash,
        password
    )


# ============================================================
# CREATE TOKEN
# ============================================================

def create_token(user_id):

    current_time = int(
        time.time()
    )

    expiration = current_time + (
        config.TOKEN_EXPIRATION_DAYS
        * 24
        * 60
        * 60
    )

    payload = {

        "user_id": user_id,

        "iat": current_time,

        "exp": expiration
    }

    token = jwt.encode(
        payload,
        config.SECRET_KEY,
        algorithm="HS256"
    )

    return token


# ============================================================
# GET TOKEN FROM REQUEST
# ============================================================

def get_token_from_request():

    authorization = request.headers.get(
        "Authorization",
        ""
    )

    if not authorization:

        return None

    if not authorization.startswith(
        "Bearer "
    ):

        return None

    token = authorization[
        len("Bearer "):
    ]

    return token


# ============================================================
# VERIFY TOKEN
# ============================================================

def verify_token(token):

    try:

        payload = jwt.decode(
            token,
            config.SECRET_KEY,
            algorithms=["HS256"]
        )

        return payload

    except jwt.ExpiredSignatureError:

        return None

    except jwt.InvalidTokenError:

        return None


# ============================================================
# CURRENT USER
# ============================================================

def get_current_user():

    token = get_token_from_request()

    if not token:

        return None

    payload = verify_token(
        token
    )

    if not payload:

        return None

    user_id = payload.get(
        "user_id"
    )

    if not user_id:

        return None

    connection = get_connection()

    user = connection.execute(
        """
        SELECT
            id,
            username,
            email,
            display_name,
            bio,
            avatar,
            verified,
            created_at

        FROM users

        WHERE id = ?
        """,
        (user_id,)
    ).fetchone()

    connection.close()

    return user


# ============================================================
# LOGIN REQUIRED DECORATOR
# ============================================================

def login_required(function):

    @wraps(function)
    def wrapper(*args, **kwargs):

        user = get_current_user()

        if not user:

            return jsonify({
                "success": False,
                "error": "Authentication required"
            }), 401

        return function(
            user,
            *args,
            **kwargs
        )

    return wrapper


# ============================================================
# OPTIONAL AUTHENTICATION
# ============================================================

def optional_user():

    return get_current_user()
