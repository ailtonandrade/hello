from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session, send_file
import threading
import main
import auth
import os
import json
import smtplib
from email.message import EmailMessage
import urllib.parse
from config import BASE_URL, SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS, FROM_EMAIL
from config import STRIPE_SECRET_KEY, STRIPE_PUBLISHABLE_KEY, STRIPE_WEBHOOK_SECRET, SECRET_KEY


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
app.secret_key = SECRET_KEY


@app.context_processor
def inject_user_globals():
    """Inject `user` and `credits` into all templates when a user is logged in."""
    user = None
    credits = 0
    try:
        if session.get('user_id'):
            user = auth.get_user(session['user_id'])
            credits = auth.get_credits(session['user_id'])
    except Exception:
        pass
    return dict(user=user, credits=credits)


# controle de execução
current_generation_thread = None
current_cancel_event = None

@app.route('/generate', methods=['GET', 'POST'])
def generate():
    # requires login
    if 'user_id' not in session:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'error': 'not_authenticated'}), 401
        return redirect(url_for('login'))

    if request.method == 'POST':
        # Get form data
        channel = request.form.get('channel')
        theme = request.form.get('theme')
        prompt_ollama = request.form.get('prompt_ollama')
        prompt_positive = request.form.get('prompt_positive')
        prompt_negative = request.form.get('prompt_negative')
        voice_name = request.form.get('voice_name')
        voice_speed = float(request.form.get('voice_speed', 0.9))
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

        # prompt_key removed from web UI; templates supply prompt text directly
        prompt_key = None
        generate_new_frames = request.form.get('generate_new_frames') in ('on', 'true', '1')

        # write into main module
        main.CHANNEL = channel
        main.THEME = theme
        main.PROMPT_POSITIVE_COMFY = prompt_positive
        main.PROMPT_NEGATIVE_COMFY = prompt_negative
        main.PROMPT_OLLAMA = prompt_ollama
        main.VOICE_NAME = voice_name
        main.VOICE_SPEED = voice_speed
        main.VOICE_PITCH = voice_pitch
        main.VOICE_VOLUME = voice_volume
        main.VOICE_RADIO_EFFECT = voice_radio_effect
        # subtitle_words_per_line must come from main module configuration only
        subtitle_words_per_line = getattr(main, 'SUBTITLE_WORDS_PER_LINE', 3)
        main.SUBTITLE_FONT_SIZE = subtitle_font_size
        main.SCREEN_ORIENTATION = screen_orientation
        main.SUBTITLE_FONT_COLOR = subtitle_font_color
        main.SUBTITLE_FONT = subtitle_font
        main.FORCE_TEXT = force_text
        main.GENERATE_NEW_FRAMES = generate_new_frames

        # prompt keys removed from UI; template-provided prompts are used

        # check credits and consume 1 credit per generation
        user_id = session.get('user_id')
        if user_id is None:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'error': 'not_authenticated'}), 401
            flash('Usuário não autenticado', 'danger')
            return redirect(url_for('login'))

        credits = auth.get_credits(user_id)
        if credits < 1:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'error': 'insufficient_credits'}), 402
            flash('Créditos insuficientes. Compre créditos no painel.', 'danger')
            return redirect(url_for('dashboard'))

        history_id = auth.consume_credits(user_id, 1)

        # determine if current user is admin (only admins may trigger uploads)
        try:
            user_row = auth.get_user(user_id)
            is_admin = bool(user_row.get('is_admin')) if user_row else False
        except Exception:
            is_admin = False

        # If admin will trigger upload, create a separate history row to track it
        upload_history_id = None
        if is_admin:
            try:
                upload_history_id = auth.log_history(user_id, 'upload_initiated', 0, None)
            except Exception:
                upload_history_id = None

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
                    perform_upload=is_admin,
                )
                # do not reveal admin-only uploads to non-admin clients
                print("✅ Geração concluída!")
                if is_admin:
                    print("✅ Upload automático iniciado (usuário admin).")
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
                    # se criamos um registro de upload, atualize também com o arquivo
                    if gen_file and upload_history_id:
                        auth.update_history_file(upload_history_id, gen_file)
                except Exception:
                    pass

        thread = threading.Thread(target=run_generation)
        thread.start()

        # guarda referências para rota de stop
        global current_generation_thread, current_cancel_event
        current_generation_thread = thread
        current_cancel_event = cancel_event

        # If request came from AJAX, return JSON indicating start
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'started': True}), 202

        flash("Geração de vídeo iniciada! Verifique o console para o progresso.", "success")
        return redirect(url_for('generate'))

    # pass user's templates for select (users only see their own templates)
    templates = auth.get_templates_for_user(session['user_id']) if 'user_id' in session else []
    return render_template('video/video_form.html', templates=templates)


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
            # do not reveal whether email or password is incorrect
            payload = {'title': 'Falha no login', 'message': 'Credenciais inválidas. Verifique e tente novamente.', 'icon': '⚠️'}
            return render_template('auth/login.html', flash_message=payload)
        # generate JWT and store in session for server-side checks
        token = auth.create_jwt(user['id'])
        session['user_id'] = user['id']
        session['jwt'] = token
        flash('Login realizado', 'success')
        return redirect(url_for('dashboard'))
    return render_template('auth/login.html')


def send_reset_email(to_email, token):
    """Try to send reset token via SMTP. If SMTP not configured, log token to console."""
    smtp_host = SMTP_HOST
    smtp_port = SMTP_PORT
    smtp_user = SMTP_USER
    smtp_pass = SMTP_PASS
    from_addr = FROM_EMAIL
    subject = 'Redefinição de senha — Código de verificação'
    # include a link with the email pre-filled so user can click to open reset form
    reset_link = f"{BASE_URL}/reset-password?email={urllib.parse.quote(to_email)}"
    body = (
        f'Seu código para redefinição de senha é: {token}\n\n'
        f'Você também pode abrir o formulário de redefinição clicando neste link:\n{reset_link}\n\n'
        'Este código expira em 15 minutos.'
    )
    if not smtp_host or not smtp_port:
        print(f"[DEV] reset token for {to_email}: {token}")
        return False
    try:
        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = from_addr
        msg['To'] = to_email
        msg.set_content(body)
        if smtp_port == 465:
            s = smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=10)
        else:
            s = smtplib.SMTP(smtp_host, smtp_port, timeout=10)
            s.starttls()
        if smtp_user and smtp_pass:
            s.login(smtp_user, smtp_pass)
        s.send_message(msg)
        s.quit()
        return True
    except Exception as e:
        print(f"Failed sending reset email: {e}")
        print(f"[DEV] reset token for {to_email}: {token}")
        return False


@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        if not email:
            flash('Informe o e-mail', 'danger')
            return redirect(url_for('forgot_password'))
        try:
            token = auth.create_password_reset_for_email(email)
        except ValueError as e:
            payload = {'title': 'Erro', 'message': str(e), 'icon': '⚠️'}
            return render_template('auth/forgot_password.html', flash_message=payload)
        sent = send_reset_email(email, token)
        # prepare masked email for UI feedback
        def mask_email(e):
            try:
                local, dom = e.split('@', 1)
            except Exception:
                return e
            local_pref = local[:3] if len(local) > 3 else local[0]
            tld = dom.split('.')[-1] if '.' in dom else ''
            dom_main = dom.split('.')[0]
            dom_pref = dom_main[0] if dom_main else ''
            masked = f"{local_pref}...@{dom_pref}...{('.' + tld) if tld else ''}"
            return masked

        masked = mask_email(email)
        if sent:
            payload = {
                'title': 'Código enviado',
                'message': f'Enviaremos um e-mail para {masked} com instruções para redefinir sua senha.',
                'icon': '📧',
                'redirect_on_close': url_for('login')
            }
        else:
            payload = {
                'title': 'Token gerado',
                'message': f'Token gerado e registrado no servidor (SMTP não configurado). Verifique os logs para o e-mail {masked}.',
                'icon': '⚠️',
                'redirect_on_close': url_for('login')
            }
        return render_template('auth/forgot_password.html', flash_message=payload)
    return render_template('auth/forgot_password.html')


@app.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        email = request.form.get('email')
        token = request.form.get('token')
        password = request.form.get('password')
        confirm = request.form.get('confirm_password')
        if not email or not token:
            flash('E-mail e token são necessários', 'danger')
            return redirect(url_for('reset_password'))
        if not password or password != confirm:
            payload = {'title': 'Erro', 'message': 'Senha e confirmação não conferem', 'icon': '⚠️'}
            return render_template('auth/reset_password.html', flash_message=payload, email=email)
        # basic password strength
        ok_len = len(password) >= 8
        ok_num = any(c.isdigit() for c in password)
        ok_spec = any(not c.isalnum() for c in password)
        if not (ok_len and ok_num and ok_spec):
            payload = {'title': 'Senha fraca', 'message': 'Senha precisa ter mínimo 8 caracteres, incluir ao menos 1 número e 1 caractere especial', 'icon': '⚠️'}
            return render_template('auth/reset_password.html', flash_message=payload, email=email)
        uid = auth.verify_and_consume_password_reset(email, token)
        if not uid:
            payload = {'title': 'Erro', 'message': 'Token inválido ou expirado', 'icon': '⚠️'}
            return render_template('auth/reset_password.html', flash_message=payload, email=email)
        # set new password
        auth.set_password(uid, password)
        flash('Senha redefinida com sucesso. Faça login.', 'success')
        return redirect(url_for('login'))
    # GET
    email = request.args.get('email')
    return render_template('auth/reset_password.html', email=email)


### Prompt Keys removed: functionality consolidated into Templates


### Templates CRUD and API (store full form data as JSON)
@app.route('/templates')
def templates_list():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = auth.get_user(session['user_id'])
    if not user or not user.get('is_admin'):
        flash('Acesso negado: apenas administradores.', 'danger')
        return redirect(url_for('dashboard'))
    temps = auth.get_templates_for_user(session['user_id'])
    return render_template('user_templates/templates_list.html', templates=temps)


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
        # If called from AJAX (form on generate page), return OK so client can reload
        return ('', 200)
    return render_template('user_templates/template_form.html', template=None)


@app.route('/templates/<int:tid>/edit', methods=['GET', 'POST'])
def template_edit(tid):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = auth.get_user(session['user_id'])
    tpl = auth.get_template(tid)
    if not tpl:
        flash('Template não encontrado', 'danger')
        return redirect(url_for('templates_list'))
    # allow owner or admin
    if tpl.get('user_id') != session['user_id'] and not (user and user.get('is_admin')):
        flash('Acesso negado: apenas proprietário ou administrador.', 'danger')
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        name = request.form.get('name') or tpl['name']
        data = {k: request.form.get(k) for k in request.form.keys()}
        # if admin editing another's template, allow admin update
        if user and user.get('is_admin') and tpl.get('user_id') != session['user_id']:
            auth.update_template_admin(tid, name, data)
        else:
            auth.update_template(tid, session['user_id'], name, data)
        flash('Template atualizado', 'success')
        return ('', 200)
    return render_template('user_templates/template_form.html', template=tpl)


@app.route('/templates/<int:tid>/delete', methods=['POST'])
def template_delete(tid):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = auth.get_user(session['user_id'])
    tpl = auth.get_template(tid)
    if not tpl:
        flash('Template não encontrado', 'danger')
        return redirect(url_for('dashboard'))
    # allow owner or admin
    if tpl.get('user_id') != session['user_id'] and not (user and user.get('is_admin')):
        flash('Acesso negado: apenas proprietário ou administrador.', 'danger')
        return redirect(url_for('dashboard'))
    if user and user.get('is_admin') and tpl.get('user_id') != session['user_id']:
        auth.delete_template_admin(tid)
    else:
        auth.delete_template(tid, session['user_id'])
    flash('Template removido', 'success')
    return ('', 200)


@app.route('/terms-of-use')
def terms_of_use():
    return render_template('terms/terms_of_use.html')


@app.route('/terms-of-responsibility')
def terms_of_responsibility():
    return render_template('terms/terms_of_responsibility.html')


@app.route('/api/template/<int:tid>')
def api_template(tid):
    # API access restricted to admins
    if 'user_id' not in session:
        return jsonify({'error': 'not authenticated'}), 401
    user = auth.get_user(session['user_id'])
    tpl = auth.get_template(tid)
    if not tpl:
        return jsonify({'error': 'not found'}), 404
    # allow owner or admin to fetch
    if tpl.get('user_id') != session['user_id'] and not (user and user.get('is_admin')):
        return jsonify({'error': 'forbidden'}), 403
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
            return render_template('auth/register.html', flash_message=payload)
        except Exception as e:
            flash(f'Erro ao registrar: {e}', 'danger')
            return redirect(url_for('register'))
        flash('Conta criada, faça login', 'success')
        return redirect(url_for('login'))
    return render_template('auth/register.html')


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
    return render_template('dashboard/dashboard.html', user=user, credits=credits, history=history)


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


@app.route('/buy')
def buy():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    packages = auth.get_credit_packages()
    return render_template('billing/buy.html', packages=packages)


@app.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    if 'user_id' not in session:
        return jsonify({'error': 'not authenticated'}), 401
    pkg_id = request.form.get('package_id') or request.json.get('package_id')
    if not pkg_id:
        return jsonify({'error': 'package_id required'}), 400
    pkg = auth.get_credit_package(int(pkg_id))
    if not pkg:
        return jsonify({'error': 'package not found'}), 404
    # stripe integration
    try:
        import stripe
    except Exception:
        return jsonify({'error': 'stripe library not installed'}), 500
    if not STRIPE_SECRET_KEY:
        return jsonify({'error': 'stripe secret key not configured'}), 500
    stripe.api_key = STRIPE_SECRET_KEY
    domain = BASE_URL.rstrip('/')
    try:
        session_obj = stripe.checkout.Session.create(
            payment_method_types=['card'],
            mode='payment',
            line_items=[{
                'price_data': {
                    'currency': 'brl',
                    'product_data': {'name': f"{pkg['name']} - {pkg['credits']} créditos"},
                    'unit_amount': int(pkg['price_cents'])
                },
                'quantity': 1
            }],
            success_url=f"{domain}/dashboard?payment=success",
            cancel_url=f"{domain}/dashboard?payment=cancel",
            metadata={'user_id': session['user_id'], 'package_id': str(pkg['id'])}
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    # create payment record
    try:
        auth.create_payment(session['user_id'], pkg['id'], session_obj.id, pkg['price_cents'], pkg['credits'], status='pending')
    except Exception:
        pass

    return redirect(session_obj.url, code=303)


@app.route('/stripe-webhook', methods=['POST'])
def stripe_webhook():
    payload = request.data
    sig_header = request.headers.get('Stripe-Signature')
    event = None
    try:
        import stripe
        stripe.api_key = STRIPE_SECRET_KEY
        if STRIPE_WEBHOOK_SECRET and sig_header:
            event = stripe.Webhook.construct_event(payload, sig_header, STRIPE_WEBHOOK_SECRET)
        else:
            # best-effort parse without verification
            event = stripe.Event.construct_from(json.loads(payload), stripe.api_key)
    except Exception as e:
        print('Webhook error:', e)
        return jsonify({'status': 'error', 'reason': str(e)}), 400

    # handle checkout.session.completed
    if event['type'] == 'checkout.session.completed':
        session_obj = event['data']['object']
        session_id = session_obj.get('id')
        meta = session_obj.get('metadata', {})
        # update payment record
        rec = auth.update_payment_status_by_session(session_id, 'completed', metadata=session_obj)
        # if record exists, add credits to user
        try:
            if rec and rec.get('user_id'):
                pkg = auth.get_credit_package(rec.get('package_id'))
                credits_to_add = rec.get('credits') or (pkg['credits'] if pkg else 0)
                auth.add_credits(rec.get('user_id'), credits_to_add, action='purchase')
        except Exception as e:
            print('Error granting credits:', e)

    return jsonify({'status': 'ok'})


@app.route('/payments')
def payments():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    payments = auth.get_payments_for_user(session['user_id'])
    # attach package name
    for p in payments:
        try:
            pkg = auth.get_credit_package(p.get('package_id'))
            p['package_name'] = pkg['name'] if pkg else None
        except Exception:
            p['package_name'] = None
    return render_template('billing/payments_list.html', payments=payments)


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