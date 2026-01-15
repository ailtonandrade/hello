from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file
from pytubefix import YouTube
import os

app = Flask(__name__)
app.secret_key = "a5sd1f65as1d6f1a6sd1f6asd5f15a1sd6f1as6"

# Ensure the youtube_downloads directory exists
def ensure_download_dir():
    download_dir = "youtube_downloads"
    os.makedirs(download_dir, exist_ok=True)
    return download_dir

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        if "fetch" in request.form:
            url = request.form.get("url")
            if not url:
                flash("Please enter a YouTube URL.", "error")
                return redirect(url_for("index"))

            try:
                # Create a YouTube object
                yt = YouTube(url)

                # Retrieve available streams
                streams = yt.streams.filter(progressive=True, file_extension="mp4").all()
                audio_streams = yt.streams.filter(only_audio=True).all()

                # Store streams in session for later use
                session["streams"] = [
                    {"itag": stream.itag, "resolution": stream.resolution, "type": "video"}
                    for stream in streams
                ]
                session["audio_streams"] = [
                    {"itag": stream.itag, "type": "audio"}
                    for stream in audio_streams
                ]
                session["url"] = url

                flash("Streams fetched successfully. Please select one to download.", "success")
                return redirect(url_for("index"))
            except Exception as e:
                flash(f"An error occurred: {e}", "error")
                return redirect(url_for("index"))

        elif "clear" in request.form:
            session.pop("streams", None)
            session.pop("audio_streams", None)
            session.pop("url", None)
            flash("Inputs cleared successfully.", "success")
            return redirect(url_for("index"))

    streams = session.get("streams", [])
    audio_streams = session.get("audio_streams", [])
    return render_template("index.html", streams=streams, audio_streams=audio_streams)

@app.route("/download", methods=["POST"])
def download():
    itag = request.form.get("itag")

    if not itag:
        flash("Please select a stream.", "error")
        return redirect(url_for("index"))

    try:
        # Retrieve the selected stream
        url = session.get("url")
        yt = YouTube(url)
        stream = yt.streams.get_by_itag(itag)

        # Ensure the download directory exists
        download_dir = ensure_download_dir()
        file_path = stream.download(output_path=download_dir)

        # Clear session after download
        session.pop("streams", None)
        session.pop("audio_streams", None)
        session.pop("url", None)

        # Send the file to the client for download
        return send_file(file_path, as_attachment=True)
    except Exception as e:
        flash(f"An error occurred: {e}", "error")
        return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)