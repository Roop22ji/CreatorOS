# Creator OS

Creator OS is a beginner-focused mobile-first creator platform built around video sharing, creator profiles, social interaction, discovery, and creator growth.

The current project uses a Flask backend with database access and a mobile-first HTML/CSS/JavaScript frontend. It can also be wrapped as an Android app with a web-wrapper platform such as AppsGeyser.

## Current Features

- User registration and login
- JWT-based authentication
- Creator profiles
- Public creator profiles
- Follow / unfollow
- Followers and following counts
- Notifications
- Video upload
- Custom creator thumbnails
- Automatic video-frame thumbnail fallback
- Video feed and individual video player
- Views, likes, comments and sharing
- Shorts feed with autoplay and mobile controls
- Following feed
- Trending feed
- For You feed
- Creator Studio and analytics
- Creator Boost for beginner discovery
- Mobile-first responsive UI
- Creator OS branding

## Project Structure

```text
creator_program/
│
├── backend/
│   ├── app.py
│   ├── auth.py
│   ├── config.py
│   ├── database.py
│   ├── templates/
│   │   └── app.html
│   └── static/
│       ├── app.js
│       ├── app.css
│       └── creator-os-icon.png   # optional branding asset
│
├── mobile/
│   └── main.py
│
├── requirements.txt
└── README.md
```

## Requirements

The current development setup uses Windows with Python 3.8. The project has also been tested during development with 32-bit Python.

Main backend dependencies:

- Flask
- Flask-CORS
- Werkzeug
- PyJWT
- OpenCV
- Requests for API testing

## Installation

Open Command Prompt in the project directory.

### Check Python

```cmd
python --version
```

The current development environment uses Python 3.8. When several Python installations exist, use the exact interpreter:

```cmd
C:\Users\SAHIL\AppData\Local\Programs\Python\Python38-32\python.exe --version
```

### Install dependencies

```cmd
C:\Users\SAHIL\AppData\Local\Programs\Python\Python38-32\python.exe -m pip install -r requirements.txt
```

If your existing OpenCV installation is already working, keep the compatible build rather than replacing it unnecessarily.

## Running the Backend

From the project directory:

```cmd
C:\Users\SAHIL\AppData\Local\Programs\Python\Python38-32\python.exe backend\app.py
```

The Flask server normally runs at:

```text
http://127.0.0.1:5000
```

## Main API Endpoints

```text
GET  /api/health
GET  /api/database

POST /api/auth/register
POST /api/auth/login
GET  /api/auth/me
POST /api/auth/logout

GET  /api/videos
POST /api/videos
GET  /api/videos/<video_id>

GET  /api/videos/<video_id>/comments
POST /api/videos/<video_id>/comments
POST /api/videos/<video_id>/like

GET  /api/users/<username>
POST /api/users/<username>/follow
GET  /api/users/<username>/follow/status

GET  /api/feed/following
GET  /api/feed/for-you
GET  /api/feed/trending
GET  /api/shorts

GET  /api/notifications
POST /api/notifications/read

GET  /api/creator/studio
GET  /api/creator/boost
```

## Video Upload

The upload endpoint uses multipart form data. Typical fields are:

```text
video
thumbnail   # optional
 title
 description
```

When a creator supplies a thumbnail, Creator OS stores it. If no thumbnail is supplied, the backend can attempt to extract a frame from the uploaded video using OpenCV.

## Authentication

Authentication uses JWT tokens. Protected requests send:

```http
Authorization: Bearer YOUR_TOKEN
```

## Creator Boost

Creator OS includes a beginner-oriented Creator Boost system. Its purpose is to give promising small creators a discovery opportunity instead of making existing popularity the only ranking signal.

The current scoring system uses signals including views, likes, comments, freshness, creator performance and beginner discovery bonuses.

## Mobile UI

The frontend is designed around a mobile application viewport. Current screens include:

- Home
- Search
- Video player
- Create / Upload
- Profile
- Creator Studio
- Shorts
- Notifications
- Public Creator Profile
- Login
- Register

The Flask server renders the mobile web app from `/` and `/app`.

## Android Packaging

The web frontend can be wrapped into an Android application with a web-wrapper service such as AppsGeyser.

For local testing, the Android device must be able to reach the backend. For production, deploy Flask to a public HTTPS server and configure the frontend API base URL appropriately.

## Troubleshooting

### Connection refused on port 5000

Start the Flask server:

```cmd
C:\Users\SAHIL\AppData\Local\Programs\Python\Python38-32\python.exe backend\app.py
```

### 404 endpoint error

Check that Flask is running, the requested route exists, and the server has been restarted after backend changes.

### `ModuleNotFoundError: No module named 'jwt'`

Install the project dependencies:

```cmd
C:\Users\SAHIL\AppData\Local\Programs\Python\Python38-32\python.exe -m pip install -r requirements.txt
```

### OpenCV thumbnail problems

OpenCV is used for automatic thumbnail extraction. If OpenCV cannot decode a particular video, the upload may continue without an extracted thumbnail and the frontend can use its fallback thumbnail behavior.

### JavaScript changes not appearing

Use:

```text
Ctrl + F5
```

and verify that the page is loading `/static/app.js` and `/static/app.css` from the intended Flask server.

## Development Direction

Creator OS is being built in stages around this loop:

```text
Create
  ↓
Upload
  ↓
Discover
  ↓
Interact
  ↓
Grow
```

The long-term goal is to make Creator OS more than a video-sharing site: a place where beginners can publish, learn, improve, and grow.

## License

No open-source license has been selected yet. Until a license is added, treat the project as proprietary.
