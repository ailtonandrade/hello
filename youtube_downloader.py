from pytubefix import YouTube
import os

def download_youtube_video():
    url = input("Enter the YouTube video URL: ")
    try:
        # Create a YouTube object
        yt = YouTube(url)

        # Get the highest resolution stream
        stream = yt.streams.get_highest_resolution()

        # Ensure the youtube_downloads directory exists
        download_dir = "youtube_downloads"
        os.makedirs(download_dir, exist_ok=True)

        # Download the video
        print(f"Downloading: {yt.title}")
        stream.download(output_path=download_dir)
        print(f"Download complete! Video saved to {download_dir}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    download_youtube_video()