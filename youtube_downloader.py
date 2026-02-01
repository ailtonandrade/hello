from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file, jsonify
from pytubefix import YouTube
import os

app = Flask(__name__)
app.secret_key = "a5sd1f65as1d6f1a6sd1f6asd5f15a1sd6f1as6"

# Ensure the youtube_downloads directory exists
def ensure_download_dir():
    # default to a downloads folder in the project
    download_dir = os.path.join(os.getcwd(), 'downloads')
    os.makedirs(download_dir, exist_ok=True)
    return download_dir


def _bytes_to_human(n):
    try:
        n = int(n)
    except Exception:
        return None
    if n < 1024:
        return f"{n} B"
    for unit in ['KB', 'MB', 'GB', 'TB']:
        n /= 1024.0
        if n < 1024.0:
            return f"{n:,.1f} {unit}"
    return f"{n:,.1f} PB"


def _seconds_to_human(s):
    try:
        s = int(s)
    except Exception:
        return None
    if s <= 0:
        return None
    h, rem = divmod(s, 3600)
    m, sec = divmod(rem, 60)
    if h:
        return f"{h:d}:{m:02d}:{sec:02d}"
    return f"{m:d}:{sec:02d}"

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
                streams = yt.streams.filter(progressive=True).all()
                audio_streams = yt.streams.filter(only_audio=True).all()

                # Store streams in session for later use (remove duplicates)
                seen_resolutions = set()
                unique_streams = []
                for stream in streams:
                    if stream.resolution not in seen_resolutions:
                        size = getattr(stream, 'filesize', None) or getattr(stream, 'filesize_approx', None)
                        duration = getattr(yt, 'length', None) or getattr(stream, 'duration', None)
                        unique_streams.append({
                            "itag": stream.itag,
                            "resolution": stream.resolution,
                            "type": "video",
                            "filesize": size,
                            "filesize_human": _bytes_to_human(size),
                            "duration": duration,
                            "duration_human": _seconds_to_human(duration)
                        })
                        seen_resolutions.add(stream.resolution)
                
                seen_audio_qualities = set()
                unique_audio_streams = []
                for stream in audio_streams:
                    # Use abr (audio bitrate) for uniqueness, fallback to itag if not available
                    quality_key = getattr(stream, 'abr', str(stream.itag))
                    if quality_key not in seen_audio_qualities:
                        size = getattr(stream, 'filesize', None) or getattr(stream, 'filesize_approx', None)
                        duration = getattr(yt, 'length', None) or getattr(stream, 'duration', None)
                        unique_audio_streams.append({
                            "itag": stream.itag,
                            "type": "audio",
                            "quality": quality_key,
                            "filesize": size,
                            "filesize_human": _bytes_to_human(size),
                            "duration": duration,
                            "duration_human": _seconds_to_human(duration)
                        })
                        seen_audio_qualities.add(quality_key)

                session["streams"] = unique_streams
                session["audio_streams"] = unique_audio_streams
                session["url"] = url
                session["thumbnail"] = yt.thumbnail_url
                session["title"] = yt.title

                flash("Streams fetched successfully. Please select one to download.", "success")
                return redirect(url_for("index"))
            except Exception as e:
                flash(f"An error occurred: {e}", "error")
                return redirect(url_for("index"))

        elif "clear" in request.form:
            session.pop("streams", None)
            session.pop("audio_streams", None)
            session.pop("url", None)
            session.pop("thumbnail", None)
            session.pop("title", None)
            flash("Inputs cleared successfully.", "success")
            return redirect(url_for("index"))

        elif "itag" in request.form:
            # download
            itag = request.form.get("itag")
            if not itag:
                flash("Please select a stream.", "error")
                return redirect(url_for("index"))

            try:
                url = request.form.get("url")
                if not url:
                    flash("No URL in form.", "error")
                    return redirect(url_for("index"))
                yt = YouTube(url)
                stream = yt.streams.get_by_itag(itag)

                download_dir = request.form.get('download_dir', '').strip()
                filename = request.form.get('filename', '').strip()

                if filename:
                    filename = os.path.splitext(filename)[0]

                if download_dir:
                    download_dir = os.path.expanduser(download_dir)
                    download_dir = os.path.abspath(download_dir)
                    os.makedirs(download_dir, exist_ok=True)
                else:
                    download_dir = ensure_download_dir()

                if filename:
                    file_path = stream.download(output_path=download_dir, filename=filename)
                else:
                    file_path = stream.download(output_path=download_dir)

                return send_file(file_path, as_attachment=True)
            except Exception as e:
                flash(f"An error occurred: {e}", "error")
                return redirect(url_for("index"))

    streams = session.get("streams", [])
    audio_streams = session.get("audio_streams", [])
    # choose default itag: first 1080p video stream if present
    default_itag = None
    for s in streams:
        res = s.get('resolution') or ''
        if res and '1080' in str(res):
            default_itag = s.get('itag')
            break
    # ensure default download dir is set in session so the form shows it
    if not session.get('download_dir'):
        session['download_dir'] = ensure_download_dir()
    return render_template("index.html", streams=streams, audio_streams=audio_streams, default_itag=default_itag)


@app.route('/youtube')
def youtube_page():
    # Redirect to main page
    return redirect(url_for('index'))
@app.route('/login')
def login():
    return redirect(url_for('index'))

@app.route('/generate')
def generate():
    return redirect(url_for('index'))

@app.route('/templates')
def templates():
    return redirect(url_for('index'))

@app.route('/payments')
def payments():
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    return redirect(url_for('index'))

@app.route("/download", methods=["GET", "POST"])
def download():
    print("Download called with method", request.method)
    if request.method == "GET":
        return redirect(url_for('index'))
    return "Download route reached. URL: " + request.form.get("url", "none") + ", itag: " + request.form.get("itag", "none")


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)