from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import os

def upload_video_to_youtube(video_path, title, description, category_id="22", privacy_status="public"):
    """
    Upload a video to YouTube using the YouTube Data API.

    Args:
        video_path (str): Path to the video file to upload.
        title (str): Title of the video.
        description (str): Description of the video.
        category_id (str): YouTube category ID (default is "22" for People & Blogs).
        privacy_status (str): Privacy status of the video ("public", "private", or "unlisted").

    Returns:
        dict: Response from the YouTube API.
    """
    try:
        # Authenticate and build the YouTube API client
        api_service_name = "youtube"
        api_version = "v3"
        credentials_path = "credentials.json"  # Replace with your credentials file path

        if not os.path.exists(credentials_path):
            raise FileNotFoundError("YouTube API credentials file not found.")

        from google.oauth2.credentials import Credentials
        credentials = Credentials.from_authorized_user_file(credentials_path, [
            "https://www.googleapis.com/auth/youtube.upload"
        ])

        youtube = build(api_service_name, api_version, credentials=credentials)

        # Prepare the video metadata
        body = {
            "snippet": {
                "title": title,
                "description": description,
                "categoryId": category_id
            },
            "status": {
                "privacyStatus": privacy_status
            }
        }

        # Upload the video
        media = MediaFileUpload(video_path, chunksize=-1, resumable=True)
        request = youtube.videos().insert(
            part=",".join(body.keys()),
            body=body,
            media_body=media
        )

        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                print(f"Uploaded {int(status.progress() * 100)}%.")

        print("Upload complete.")
        return response

    except Exception as e:
        print(f"Error uploading video: {e}")
        return None

if __name__ == "__main__":
    # Example usage
    video_path = "example_video.mp4"
    title = "Example Video Title"
    description = "This is an example description for the video."
    upload_video_to_youtube(video_path, title, description)