from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session, send_file
import threading
import main
import auth
import os
import json


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

# controle de execução
current_generation_thread = None
current_cancel_event = None

@app.route('/generate', methods=['GET', 'POST'])
def generate():
    # requires login
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        # Get form data
        channel = request.form.get('channel')
        theme = request.form.get('theme')
        prompt_key = request.form.get('prompt_key')
        prompt_ollama = request.form.get('prompt_ollama')
        prompt_positive = request.form.get('prompt_positive')
        prompt_negative = request.form.get('prompt_negative')
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

        # apply additional settings into the main module so main() uses them
        voice_pitch = float(request.form.get('voice_pitch', getattr(main, 'VOICE_PITCH', 0.8)))
        voice_volume = float(request.form.get('voice_volume', getattr(main, 'VOICE_VOLUME', 1.2)))
        voice_radio_effect = request.form.get('voice_radio_effect') in ('on', 'true', '1')

        prompt_key = request.form.get('prompt_key', getattr(main, 'PROMPT_KEY', None))
        generate_new_frames = request.form.get('generate_new_frames') in ('on', 'true', '1')

        # write into main module
        main.CHANNEL = channel
        main.THEME = theme
        main.PROMPT_KEY = prompt_key
        main.PROMPT_POSITIVE_COMFY = prompt_positive
        main.PROMPT_NEGATIVE_COMFY = prompt_negative
        main.PROMPT_OLLAMA = prompt_ollama
        main.VOICE_NAME = voice_name
        main.VOICE_SPEED = voice_speed
        main.VOICE_PITCH = voice_pitch
        main.VOICE_VOLUME = voice_volume
        main.VOICE_RADIO_EFFECT = voice_radio_effect
        main.SUBTITLE_WORDS_PER_LINE = subtitle_words_per_line
        main.SUBTITLE_FONT_SIZE = subtitle_font_size
        main.SCREEN_ORIENTATION = screen_orientation
        main.SUBTITLE_FONT_COLOR = subtitle_font_color
        main.SUBTITLE_FONT = subtitle_font
        main.FORCE_TEXT = force_text
        main.GENERATE_NEW_FRAMES = generate_new_frames

        # reload prompts if prompt_key provided
        if prompt_key:
            try:
                p_ollama, p_pos, p_neg = main.load_prompts(prompt_key)
                main.PROMPT_OLLAMA = p_ollama
                main.PROMPT_POSITIVE_COMFY = p_pos
                main.PROMPT_NEGATIVE_COMFY = p_neg
                main.PROMPT_KEY = prompt_key
            except Exception as e:
                flash(f"Prompt key inválido: {e}", "warning")

        # check credits and consume 1 credit per generation
        user_id = session.get('user_id')
        if user_id is None:
            flash('Usuário não autenticado', 'danger')
            return redirect(url_for('login'))

        credits = auth.get_credits(user_id)
        if credits < 1:
            flash('Créditos insuficientes. Compre créditos no painel.', 'danger')
            return redirect(url_for('dashboard'))

        history_id = auth.consume_credits(user_id, 1)

        # Run main in a separate thread to avoid blocking
        cancel_event = threading.Event()

        # expose cancel event to main module so internal functions can check it
        main.CANCEL_EVENT = cancel_event

        def run_generation():
            try:
                main.main(
                    channel=channel,
                    theme=theme,
                    prompt_key=prompt_key,
                    prompt_ollama=main.PROMPT_OLLAMA,
                    prompt_positive_comfy=main.PROMPT_POSITIVE_COMFY,
                    prompt_negative_comfy=main.PROMPT_NEGATIVE_COMFY,
                    voice_name=voice_name,
                    voice_speed=voice_speed,
                    voice_pitch=voice_pitch,
                    voice_volume=voice_volume,
                    voice_radio_effect=voice_radio_effect,

                    subtitle_words_per_line=subtitle_words_per_line,
                    subtitle_font_size=subtitle_font_size,
                    subtitle_font_color=subtitle_font_color,
                    subtitle_font=subtitle_font,
                    screen_orientation=screen_orientation,

                    force_text=force_text,
                    generate_new_frames=generate_new_frames,
                )
                # main.youtube_upload(theme, channel, screen_orientation)
                print("✅ Geração e upload concluídos!")
            except Exception as e:
                print(f"❌ Erro durante geração: {e}")
            finally:
                # limpar evento
                try:
                    main.CANCEL_EVENT = None
                except Exception:
                    pass
                # depois que terminar, atualiza history com o arquivo gerado
                try:
                    gen_file = getattr(main, 'LAST_GENERATED_FILE', None)
                    if gen_file and history_id:
                        auth.update_history_file(history_id, gen_file)
                except Exception:
                    pass

        thread = threading.Thread(target=run_generation)
        thread.start()

        # guarda referências para rota de stop
        global current_generation_thread, current_cancel_event
        current_generation_thread = thread
        current_cancel_event = cancel_event

        flash("Geração de vídeo iniciada! Verifique o console para o progresso.", "success")
        return redirect(url_for('generate'))

    # pass user's prompt keys and templates for selects
    keys = auth.get_prompt_keys_for_user(session['user_id']) if 'user_id' in session else []
    templates = auth.get_templates_for_user(session['user_id']) if 'user_id' in session else []
    return render_template('video_form.html', prompt_keys=keys, templates=templates)


@app.route('/status')
def status():
    try:
        return jsonify({
            'progress': getattr(main, 'PROGRESS', 0),
            'message': getattr(main, 'PROGRESS_MESSAGE', 'pronto')
        })
    except Exception:
        return jsonify({'progress': 0, 'message': 'erro'})


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = auth.authenticate_user(email, password)
        if not user:
            flash('Credenciais inválidas', 'danger')
            return redirect(url_for('login'))
        # generate JWT and store in session for server-side checks
        token = auth.create_jwt(user['id'])
        session['user_id'] = user['id']
        session['jwt'] = token
        flash('Login realizado', 'success')
        return redirect(url_for('dashboard'))
    return render_template('login.html')


### Prompt Keys CRUD and API
@app.route('/prompt_keys')
def prompt_keys():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    keys = auth.get_prompt_keys_for_user(session['user_id'])
    return render_template('prompt_keys.html', keys=keys)


@app.route('/prompt_keys/new', methods=['GET', 'POST'])
def prompt_key_new():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        name = request.form.get('name')
        p_ollama = request.form.get('prompt_ollama')
        p_pos = request.form.get('prompt_positive')
        p_neg = request.form.get('prompt_negative')
        auth.create_prompt_key(session['user_id'], name, p_ollama, p_pos, p_neg)
        flash('Prompt key criado', 'success')
        return redirect(url_for('prompt_keys'))
    return render_template('prompt_key_form.html', key=None)


@app.route('/prompt_keys/<int:pk_id>/edit', methods=['GET', 'POST'])
def prompt_key_edit(pk_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    key = auth.get_prompt_key(pk_id, session['user_id'])
    if not key:
        flash('Prompt key não encontrado', 'danger')
        return redirect(url_for('prompt_keys'))
    if request.method == 'POST':
        name = request.form.get('name')
        p_ollama = request.form.get('prompt_ollama')
        p_pos = request.form.get('prompt_positive')
        p_neg = request.form.get('prompt_negative')
        auth.update_prompt_key(pk_id, session['user_id'], name, p_ollama, p_pos, p_neg)
        flash('Prompt key atualizado', 'success')
        return redirect(url_for('prompt_keys'))
    return render_template('prompt_key_form.html', key=key)


@app.route('/prompt_keys/<int:pk_id>/delete', methods=['POST'])
def prompt_key_delete(pk_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    auth.delete_prompt_key(pk_id, session['user_id'])
    flash('Prompt key removido', 'success')
    return redirect(url_for('prompt_keys'))


@app.route('/api/prompt_key/<int:pk_id>')
def api_prompt_key(pk_id):
    key = auth.get_prompt_key(pk_id)
    if not key:
        return jsonify({'error': 'not found'}), 404
    return jsonify({
        'id': key['id'],
        'name': key['name'],
        'prompt_ollama': key.get('prompt_ollama'),
        'prompt_positive': key.get('prompt_positive'),
        'prompt_negative': key.get('prompt_negative')
    })


### Templates CRUD and API (store full form data as JSON)
@app.route('/templates')
def templates_list():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    temps = auth.get_templates_for_user(session['user_id'])
    return render_template('templates_list.html', templates=temps)


@app.route('/templates/new', methods=['GET', 'POST'])
def template_new():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        name = request.form.get('name') or 'untitled'
        # collect all form fields to store
        data = {k: request.form.get(k) for k in request.form.keys()}
        auth.create_template(session['user_id'], name, data)
        flash('Template salvo', 'success')
        return redirect(url_for('templates_list'))
    return render_template('template_form.html', template=None)


@app.route('/templates/<int:tid>/edit', methods=['GET', 'POST'])
def template_edit(tid):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    tpl = auth.get_template(tid, session['user_id'])
    if not tpl:
        flash('Template não encontrado', 'danger')
        return redirect(url_for('templates_list'))
    if request.method == 'POST':
        name = request.form.get('name') or tpl['name']
        data = {k: request.form.get(k) for k in request.form.keys()}
        auth.update_template(tid, session['user_id'], name, data)
        flash('Template atualizado', 'success')
        return redirect(url_for('templates_list'))
    return render_template('template_form.html', template=tpl)


@app.route('/templates/<int:tid>/delete', methods=['POST'])
def template_delete(tid):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    auth.delete_template(tid, session['user_id'])
    flash('Template removido', 'success')
    return redirect(url_for('templates_list'))


@app.route('/api/template/<int:tid>')
def api_template(tid):
    tpl = auth.get_template(tid)
    if not tpl:
        return jsonify({'error': 'not found'}), 404
    return jsonify({'id': tpl['id'], 'name': tpl['name'], 'data': tpl.get('data', {})})


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm = request.form.get('confirm_password')
        if not password or password != confirm:
            flash('Senha e confirmação não conferem', 'danger')
            return redirect(url_for('register'))
        phone = request.form.get('phone')
        cpf = request.form.get('cpf')
        try:
            uid = auth.create_user(name, email, password, phone, cpf)
        except ValueError as e:
            # user-friendly modal via template: pass flash payload
            payload = {'title': 'Erro', 'message': str(e), 'icon': '⚠️'}
            return render_template('register.html', flash_message=payload)
        except Exception as e:
            flash(f'Erro ao registrar: {e}', 'danger')
            return redirect(url_for('register'))
        flash('Conta criada, faça login', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Desconectado', 'success')
    return redirect(url_for('login'))


@app.route('/')
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = auth.get_user(session['user_id'])
    credits = auth.get_credits(user['id'])
    history = auth.get_history_for_user(user['id'])
    return render_template('dashboard.html', user=user, credits=credits, history=history)


@app.route('/download/<int:history_id>')
def download(history_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    # ensure the history belongs to user
    hs = auth.get_history_for_user(session['user_id'], limit=200)
    entry = next((h for h in hs if h['id'] == history_id), None)
    if not entry or not entry.get('file_path'):
        flash('Arquivo não encontrado', 'danger')
        return redirect(url_for('dashboard'))
    path = entry['file_path']
    if not os.path.exists(path):
        flash('Arquivo removido do servidor', 'danger')
        return redirect(url_for('dashboard'))
    return send_file(path, as_attachment=True)


@app.route('/stop', methods=['POST'])
def stop_generation():
    global current_cancel_event
    try:
        if current_cancel_event is not None:
            current_cancel_event.set()
            # also update main progress message
            try:
                main.PROGRESS_MESSAGE = 'cancelando'
            except Exception:
                pass
            return jsonify({'stopped': True})
        return jsonify({'stopped': False, 'reason': 'no active generation'})
    except Exception as e:
        return jsonify({'stopped': False, 'reason': str(e)})


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