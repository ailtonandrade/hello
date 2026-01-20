from flask import Flask, render_template, request, redirect, url_for, flash
import threading
from main import main, youtube_upload


CHANNEL = "parallelcuts"
THEME = "pregacao"
VOICE_NAME = "pm_alex" #pm_alex #pf_dora
VOICE_SPEED = 1
VOICE_PITCH = 0.8
VOICE_VOLUME = 1.2
VOICE_RADIO_EFFECT = True
SUBTITLE_WORDS_PER_LINE = 3
SUBTITLE_FONT_SIZE = 45
SCREEN_ORIENTATION = "MOBILE"
SUBTITLE_FONT_COLOR = (255, 191, 0, 200)  # Amarelo âmbar
SUBTITLE_FONT = "Lilita.ttf"


app = Flask(__name__)
app.secret_key = "secret_key_for_flask"

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Get form data
        channel = request.form.get('channel')
        theme = request.form.get('theme')
        voice_name = request.form.get('voice_name')
        voice_speed = float(request.form.get('voice_speed', 0.9))
        subtitle_words_per_line = int(request.form.get('subtitle_words_per_line', 3))
        subtitle_font_size = int(request.form.get('subtitle_font_size', 55))
        screen_orientation = request.form.get('screen_orientation')
        subtitle_font_color_r = int(request.form.get('subtitle_font_color_r', 255))
        subtitle_font_color_g = int(request.form.get('subtitle_font_color_g', 191))
        subtitle_font_color_b = int(request.form.get('subtitle_font_color_b', 0))
        subtitle_font_color_a = int(request.form.get('subtitle_font_color_a', 200))
        subtitle_font_color = (subtitle_font_color_r, subtitle_font_color_g, subtitle_font_color_b, subtitle_font_color_a)
        subtitle_font = request.form.get('subtitle_font')
        force_text = request.form.get('force_text') if request.form.get('force_text') else None

        # Run main in a separate thread to avoid blocking
        def run_generation():
            try:
                main(channel, theme, voice_name, voice_speed, subtitle_words_per_line, subtitle_font_size, screen_orientation, subtitle_font_color, subtitle_font, force_text)
                #youtube_upload(theme, channel, screen_orientation)
                print("✅ Geração e upload concluídos!")
            except Exception as e:
                print(f"❌ Erro durante geração: {e}")

        thread = threading.Thread(target=run_generation)
        thread.start()

        flash("Geração de vídeo iniciada! Verifique o console para o progresso.", "success")
        return redirect(url_for('index'))

    return render_template('video_form.html')


@app.route("/preview", methods=["POST"])
def preview():
    from video_generator import VideoGenerator
    import random

    theme = request.form.get("theme")
    screen_orientation = request.form.get("screen_orientation")
    channel = request.form.get("channel")
    subtitle_font = request.form.get("subtitle_font")

    # Gerar vídeo
    vg = VideoGenerator(
        theme=theme,
        channel=channel,
        zoom_strength=0.015,
        grain_intensity=0.03,
        vignette_intensity=0.6,
        screen_orientation=screen_orientation,
        subtitle_font=subtitle_font,
        subtitle_font_size=SUBTITLE_FONT_SIZE,
        subtitle_words_per_line=SUBTITLE_WORDS_PER_LINE,
    )

    path = vg.generate_preview_frame(
        duration=6.0,
        t=random.uniform(0.5, 3.0),
        output_path="static/previews/preview_current.jpg"
    )

    return {
        "status": "ready",
        "preview": f"/{path}"
    }


if __name__ == '__main__':
    app.run(debug=True)