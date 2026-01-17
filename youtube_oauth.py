# youtube_oauth.py
import os
import json
import time
import requests
from youtube_config import YOUTUBE_CLIENT_ID, YOUTUBE_CLIENT_SECRET

TOKEN_FILE = "youtube_token.json"
TOKEN_URL = "https://oauth2.googleapis.com/token"
YOUTUBE_UPLOAD_INIT_URL = "https://www.googleapis.com/upload/youtube/v3/videos"


class YouTubeOAuthError(Exception):
    pass


class YouTubeUploadError(Exception):
    pass


# =========================
# 🔐 OAUTH / TOKEN
# =========================

def get_access_token():
    if not os.path.exists(TOKEN_FILE):
        raise YouTubeOAuthError("youtube_token.json não encontrado")

    with open(TOKEN_FILE, "r") as f:
        token = json.load(f)

    created_at = token.get("created_at", 0)
    expires_in = token.get("expires_in", 3600)

    # ainda válido
    if time.time() < created_at + expires_in - 60:
        return token["access_token"]

    # refresh token
    data = {
        "client_id": YOUTUBE_CLIENT_ID,
        "client_secret": YOUTUBE_CLIENT_SECRET,
        "refresh_token": token["refresh_token"],
        "grant_type": "refresh_token",
    }

    response = requests.post(TOKEN_URL, data=data)
    if response.status_code != 200:
        raise YouTubeOAuthError(response.text)

    new_data = response.json()

    token["access_token"] = new_data["access_token"]
    token["expires_in"] = new_data["expires_in"]
    token["created_at"] = int(time.time())

    with open(TOKEN_FILE, "w") as f:
        json.dump(token, f, indent=2)

    return token["access_token"]

def get_authenticated_channel_info(access_token):
    url = "https://www.googleapis.com/youtube/v3/channels"
    params = {
        "part": "snippet",
        "mine": "true"
    }
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()

    data = response.json()
    if not data.get("items"):
        raise Exception("Nenhum canal encontrado para este token")

    channel = data["items"][0]
    return {
        "channel_id": channel["id"],
        "title": channel["snippet"]["title"]
    }


# =========================
# 📤 UPLOAD YOUTUBE
# =========================

def youtube_upload_video(
    video_path: str,
    title: str,
    description: str,
    privacy: str = "public",
    category_id: str = "22",
    is_short: bool = False
):
    access_token = get_access_token()

    # obtém info do canal autenticado
    channel_info = get_authenticated_channel_info(access_token)
    print(f"📺 Canal autenticado: {channel_info['title']} ({channel_info['channel_id']})")

    if not os.path.exists(video_path):
        raise YouTubeUploadError("Arquivo de vídeo não encontrado")

    if is_short and "#shorts" not in description.lower():
        description += "\n\n#Shorts"

    metadata = {
        "snippet": {
            "title": title[:100],
            "description": description[:5000],
            "categoryId": category_id
        },
        "status": {
            "privacyStatus": privacy,
            "selfDeclaredMadeForKids": False
        }
    }

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json; charset=UTF-8",
        "X-Upload-Content-Type": "video/mp4"
    }

    params = {
        "uploadType": "resumable",
        "part": "snippet,status"
    }

    # inicia upload
    init_response = requests.post(
        YOUTUBE_UPLOAD_INIT_URL,
        headers=headers,
        params=params,
        json=metadata
    )

    if init_response.status_code not in (200, 201):
        raise YouTubeUploadError(init_response.text)

    upload_url = init_response.headers.get("Location")
    if not upload_url:
        raise YouTubeUploadError("Upload URL não retornada")

    # envia vídeo
    with open(video_path, "rb") as f:
        upload_headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "video/mp4"
        }

        upload_response = requests.put(
            upload_url,
            headers=upload_headers,
            data=f
        )

    if upload_response.status_code not in (200, 201):
        raise YouTubeUploadError(upload_response.text)

    video_id = upload_response.json().get("id")
    if not video_id:
        raise YouTubeUploadError("Upload finalizado, mas video_id não retornado")

    print(f"🎬 Vídeo enviado com sucesso! ID: {video_id}")
    return video_id
