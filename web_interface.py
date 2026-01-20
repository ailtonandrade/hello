from flask import Flask, render_template, request, redirect, url_for, flash
import threading
from main import main, youtube_upload

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

if __name__ == '__main__':
    app.run(debug=True)