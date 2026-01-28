from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file, jsonify
from pytubefix import YouTube
import os
import threading
import uuid
import time

# in-memory job store for downloads: { job_id: {status, downloaded, total, percent, message, filepath}} 
DOWNLOAD_JOBS = {}

app = Flask(__name__)
app.secret_key = "a5sd1f65as1d6f1a6sd1f6asd5f15a1sd6f1as6"

# Ensure the youtube_downloads directory exists
def ensure_download_dir():
    # default to the project's `videos` folder
    base = os.path.dirname(os.path.abspath(__file__))
    download_dir = os.path.join(base, "videos")
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
                streams = yt.streams.filter(progressive=False, file_extension="mp4").all()
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
    # Modern downloader page
    return render_template('youtube/downloader.html')

@app.route('/api/fetch_streams', methods=['POST'])
def api_fetch_streams():
    data = None
    try:
        data = request.get_json(force=True)
    except Exception:
        data = request.form or {}

    url = data.get('url') if data else None
    if not url:
        return jsonify({'error': 'missing url'}), 400

    try:
        yt = YouTube(url)
        streams = yt.streams.filter(progressive=False, file_extension="mp4").all()
        audio_streams = yt.streams.filter(only_audio=True).all()

        seen_resolutions = set()
        unique_streams = []
        for stream in streams:
            if stream.resolution in seen_resolutions:
                continue
            size = getattr(stream, 'filesize', None) or getattr(stream, 'filesize_approx', None)
            duration = getattr(yt, 'length', None) or getattr(stream, 'duration', None)
            unique_streams.append({
                'itag': stream.itag,
                'resolution': stream.resolution,
                'filesize': size,
                'filesize_human': _bytes_to_human(size),
                'duration': duration,
                'duration_human': _seconds_to_human(duration)
            })
            seen_resolutions.add(stream.resolution)

        seen_audio = set()
        unique_audio = []
        for stream in audio_streams:
            q = getattr(stream, 'abr', str(stream.itag))
            if q in seen_audio:
                continue
            size = getattr(stream, 'filesize', None) or getattr(stream, 'filesize_approx', None)
            duration = getattr(yt, 'length', None) or getattr(stream, 'duration', None)
            unique_audio.append({
                'itag': stream.itag,
                'quality': q,
                'filesize': size,
                'filesize_human': _bytes_to_human(size),
                'duration': duration,
                'duration_human': _seconds_to_human(duration)
            })
            seen_audio.add(q)

        return jsonify({'title': yt.title, 'thumbnail': yt.thumbnail_url, 'streams': unique_streams, 'audio_streams': unique_audio})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
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

        # optional inputs
        download_dir = request.form.get('download_dir', '').strip()
        filename = request.form.get('filename', '').strip()

        # sanitize filename: remove extension if provided
        if filename:
            filename = os.path.splitext(filename)[0]

        # determine output directory
        if download_dir:
            download_dir = os.path.expanduser(download_dir)
            download_dir = os.path.abspath(download_dir)
            os.makedirs(download_dir, exist_ok=True)
        else:
            download_dir = ensure_download_dir()

        # save session choices for convenience
        session['download_dir'] = download_dir
        session['download_filename'] = filename

        # Perform download (pytube will add extension)
        if filename:
            file_path = stream.download(output_path=download_dir, filename=filename)
        else:
            file_path = stream.download(output_path=download_dir)

        # Clear session selections except download prefs
        session.pop("streams", None)
        session.pop("audio_streams", None)
        session.pop("url", None)
        session.pop("thumbnail", None)
        session.pop("title", None)

        # Send the file to the client for download
        return send_file(file_path, as_attachment=True)
    except Exception as e:
        flash(f"An error occurred: {e}", "error")
        return redirect(url_for("index"))


@app.route('/download_async', methods=['POST'])
def download_async():
    itag = request.form.get('itag')
    if not itag:
        return jsonify({'error':'missing itag'}), 400

    url = session.get('url')
    if not url:
        return jsonify({'error':'no url in session'}), 400

    # options
    download_dir = request.form.get('download_dir', '').strip() or ensure_download_dir()
    filename = request.form.get('filename', '').strip()
    if filename:
        filename = os.path.splitext(filename)[0]

    # prepare job
    job_id = str(uuid.uuid4())
    job = {
        'status':'queued',
        'downloaded':0,
        'total':0,
        'percent':0,
        'message':'queued',
        'filepath':None,
        'started_at': time.time()
    }
    job['cancelled'] = False
    DOWNLOAD_JOBS[job_id] = job

    def worker(job_id, url, itag, download_dir, filename):
        job = DOWNLOAD_JOBS.get(job_id)
        try:
            yt = YouTube(url)
            stream = yt.streams.get_by_itag(itag)
            if not stream:
                job.update({'status':'error','message':'stream not found'})
                return

            # progress callback
            def on_progress(s, chunk, bytes_remaining):
                try:
                    # abort if cancelled
                    if job.get('cancelled'):
                        job.update({'status':'cancelled','message':'cancelled by user'})
                        raise Exception('Cancelled by user')
                    total = getattr(s, 'filesize', None) or getattr(s, 'filesize_approx', None) or 0
                    downloaded = total - bytes_remaining if total else 0
                    percent = int((downloaded / total) * 100) if total else 0
                    job.update({'status':'downloading','downloaded':downloaded,'total':total,'percent':percent,'message':'downloading'})
                except Exception:
                    pass

            try:
                # register callback if supported
                if hasattr(yt, 'register_on_progress_callback'):
                    yt.register_on_progress_callback(on_progress)
            except Exception:
                pass

            job.update({'status':'started','message':'starting download'})
            # perform download
            output_path = download_dir
            if filename:
                out = stream.download(output_path=output_path, filename=filename)
            else:
                out = stream.download(output_path=output_path)

            # determine desired extension: video -> mp4, audio -> mp3
            try:
                mime = getattr(stream, 'mime_type', '') or ''
                is_video = False
                if 'video' in mime:
                    is_video = True
                # fallback: presence of resolution indicates video
                if getattr(stream, 'resolution', None):
                    is_video = True

                desired_ext = 'mp4' if is_video else 'mp3'
                base, ext = os.path.splitext(out)
                ext = ext.lstrip('.').lower()

                converted_path = out
                if ext != desired_ext:
                    # convert using ffmpeg if available
                    converted_path = f"{base}.{desired_ext}"
                    try:
                        if desired_ext == 'mp3':
                            # extract audio to mp3
                            cmd = [
                                'ffmpeg', '-y', '-i', out,
                                '-vn', '-acodec', 'libmp3lame', '-q:a', '2', converted_path
                            ]
                        else:
                            # convert to mp4 (copy video if possible)
                            cmd = [
                                'ffmpeg', '-y', '-i', out,
                                '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', converted_path
                            ]
                        import subprocess as _sub
                        _sub.run(cmd, check=True, stdout=_sub.PIPE, stderr=_sub.PIPE)
                        # remove original if conversion succeeded
                        try:
                            os.remove(out)
                        except Exception:
                            pass
                    except Exception as e_conv:
                        # conversion failed; keep original file
                        converted_path = out

                job.update({'status':'done','percent':100,'downloaded': os.path.getsize(converted_path) if os.path.exists(converted_path) else 0,'total': os.path.getsize(converted_path) if os.path.exists(converted_path) else 0,'message':'completed','filepath':converted_path})
            except Exception:
                # fallback to raw file info
                job.update({'status':'done','percent':100,'downloaded': os.path.getsize(out) if os.path.exists(out) else 0,'total': os.path.getsize(out) if os.path.exists(out) else 0,'message':'completed','filepath':out})
        except Exception as e:
            msg = str(e)
            if job.get('cancelled') or 'cancel' in msg.lower():
                job.update({'status':'cancelled','message': 'cancelled by user'})
                # try to remove partial file if exists
                try:
                    fp = job.get('filepath')
                    if fp and os.path.exists(fp):
                        os.remove(fp)
                except Exception:
                    pass
            else:
                job.update({'status':'error','message':msg})

    t = threading.Thread(target=worker, args=(job_id, url, itag, download_dir, filename), daemon=True)
    t.start()

    return jsonify({'job_id': job_id})


@app.route('/download_status')
def download_status():
    job_id = request.args.get('job_id')
    if not job_id or job_id not in DOWNLOAD_JOBS:
        return jsonify({'error':'job not found'}), 404
    job = DOWNLOAD_JOBS[job_id]
    return jsonify(job)


@app.route('/download_file/<job_id>')
def download_file(job_id):
    job = DOWNLOAD_JOBS.get(job_id)
    if not job:
        return "Job not found", 404
    if job.get('status') != 'done' or not job.get('filepath'):
        return "File not ready", 404
    return send_file(job['filepath'], as_attachment=True)


@app.route('/cancel_download', methods=['POST'])
def cancel_download():
    data = None
    try:
        data = request.get_json(force=True)
    except Exception:
        data = request.form

    job_id = data.get('job_id') if data else None
    if not job_id or job_id not in DOWNLOAD_JOBS:
        return jsonify({'error':'job not found'}), 404

    job = DOWNLOAD_JOBS[job_id]
    job['cancelled'] = True
    job['message'] = 'cancelling'
    job['status'] = 'cancelling'
    return jsonify({'ok':True})

if __name__ == "__main__":
    app.run(debug=True)