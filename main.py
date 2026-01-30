import time
import os
import re
import random
import subprocess
import json
import requests
from datetime import datetime
from voice_generator import VoiceGenerator
from video_generator import VideoGenerator
from youtube_manager import YouTubeManager
from instagram_manager import InstagramManager
from local_title_description_generator import LocalTitleDescriptionGenerator
from run_video_comfy_generator import ComfySingleFrameVideoGenerator
from prompts import PROMPTS

# Configurações fixas
CHANNEL = "tomdouniverso"
THEME = "universe_sleep_shorts"
VOICE_NAME = "Thom" # deactivated
SCREEN_ORIENTATION = "MOBILE"  # "MOBILE" ou "DESKTOP"
VOICE_SPEED = 1.1
VOICE_PITCH = 0.9
VOICE_VOLUME = 1.2
VOICE_RADIO_EFFECT = True
SUBTITLE_WORDS_PER_LINE = 3 if SCREEN_ORIENTATION == "MOBILE" else 8
SUBTITLE_FONT_SIZE = 55 if SCREEN_ORIENTATION == "MOBILE" else 40

SUBTITLE_FONT_COLOR = (255, 191, 0, 200)
SUBTITLE_FONT = "Lilita.ttf"
FORCE_TEXT = None
PROMPT_KEY = "universe_sleep_shorts"
GENERATE_NEW_FRAMES = True
# Progress tracking (0-100)
PROGRESS = 0
PROGRESS_MESSAGE = "pronto"
CANCEL_EVENT = None
LAST_GENERATED_FILE = None

def load_prompts(prompt_key):
    if prompt_key not in PROMPTS:
        raise KeyError(f"Prompt '{prompt_key}' não encontrado em prompts.py")

    p = PROMPTS[prompt_key]

    return (
        p.get("ollama", "").strip(),
        p.get("comfy_positive", "").strip(),
        p.get("comfy_negative", "").strip()
    )

PROMPT_OLLAMA, PROMPT_POSITIVE_COMFY, PROMPT_NEGATIVE_COMFY = load_prompts(PROMPT_KEY)
# \\ Configurações fixas

def get_text_by_ollama(prompt, theme=None):
    """Request text from Ollama. If `theme` contains 'long', iteratively request
    continuations until the model completes the thought or a safety limit is hit.
    Returns the accumulated full text.
    """
    print(f"🤖 Solicitando texto ao modelo Ollama/Qwen2.5 às {datetime.now().strftime('%H:%M:%S')}...")

    def _call_http(p: str, timeout=600):
        try:
            payload = {
                "model": "qwen2.5:7b-instruct",
                "prompt": p,
                "stream": False,
                "options": {"num_predict": 100, "temperature": 0.6}
            }
            resp = requests.post("http://localhost:11434/api/generate", json=payload, timeout=timeout)
            resp.raise_for_status()
            return resp.json().get("response", "").strip()
        except Exception as e:
            print(f"⚠️ Falha na chamada HTTP ao Ollama: {e}")
            return None

    def _call_subprocess(p: str):
        try:
            result = subprocess.run([
                "ollama", "run", "qwen2.5:7b-instruct"
            ], input=p, capture_output=True, text=True, check=True)
            return result.stdout.strip() if result.stdout else None
        except Exception as e:
            print(f"⚠️ Falha ao chamar Ollama via subprocess: {e}")
            return None

    # initial try
    text = _call_http(prompt, timeout=1200)
    if text is None:
        text = _call_subprocess(prompt)

    if not text:
        print("❌ Nenhuma resposta do modelo.")
        return ""

    print(f"✅ Resposta inicial recebida às {datetime.now().strftime('%H:%M:%S')}. Tamanho: {len(text)} chars")

    # If theme indicates long output, iteratively continue until the model
    # finishes the reasoning (heuristic: ends with sentence-final punctuation)
    if theme and "long" in theme.lower():
        print("ℹ️ Tema 'long' detectado — tentando gerar texto longo por continuação automática.")
    
        def _is_finished(t: str):
            if not t:
                return False
            return bool(re.search(r"[\.\!\?\—…\"]\s*$", t))

        def _has_cutoff(t: str):
            # ends with alphanumeric -> likely cut mid-word
            return bool(re.search(r"\w$", t)) and not bool(re.search(r"[\.\!\?\—…\"]\s*$", t))

        max_rounds = 12
        min_rounds = 5
        rounds = 0
        accumulated = text

        # Ensure we attempt at least `min_rounds` continuations for 'long' themes.
        # Do not return immediately even if the initial chunk looks finished.

        while rounds < max_rounds:
            rounds += 1
            cont_prompt = (
                "Continue the following text in Brazilian Portuguese, keeping the same style and tone. "
                "Do not repeat sentences already written. Continue from where it stopped:\n\n"
                + accumulated[-4000:]
            )

            next_chunk = _call_http(cont_prompt, timeout=900)
            if next_chunk is None:
                next_chunk = _call_subprocess(cont_prompt)

            if not next_chunk:
                print(f"⚠️ Continuação vazia no round {rounds}; interrompendo.")
                break

            # detect and remove overlap
            overlap = 0
            max_ol = min(len(accumulated), len(next_chunk), 800)
            for ol in range(max_ol, 0, -1):
                if accumulated.endswith(next_chunk[:ol]):
                    overlap = ol
                    break

            appended = next_chunk[overlap:].strip()
            if not appended:
                print(f"⚠️ Sem novo conteúdo no round {rounds}; interrompendo.")
                break

            # join cleanly
            if accumulated and not accumulated.endswith("\n") and not appended.startswith("\n"):
                accumulated = accumulated + appended
            else:
                accumulated = accumulated + appended

            print(f"ℹ️ Round {rounds} aplicado — tamanho atual: {len(accumulated)} chars")

            # if finished (sentence end) and not cut off mid-word, stop only
            # after we've reached the minimum number of rounds
            if _is_finished(accumulated) and not _has_cutoff(accumulated) and rounds >= min_rounds:
                print("✅ Texto finalizado pelo modelo (detecção heurística).")
                break

            # if reached very large size, stop to avoid runaway
            if len(accumulated) > 20000:
                print("⚠️ Tamanho máximo atingido — interrompendo continuações.")
                break

        # final safety: if ends with alphanumeric (cut mid-word), attempt a few short finishes
        if _has_cutoff(accumulated):
            for finish_round in range(3):
                finish_prompt = (
                    "Complete the last word and finish the sentence naturally in Brazilian Portuguese. "
                    "Do not repeat previous content. Continue:\n\n" + accumulated[-1000:]
                )
                next_chunk = _call_http(finish_prompt, timeout=90)
                if next_chunk is None:
                    next_chunk = _call_subprocess(finish_prompt)
                if not next_chunk:
                    break

                # remove overlap and append
                overlap = 0
                max_ol = min(len(accumulated), len(next_chunk), 300)
                for ol in range(max_ol, 0, -1):
                    if accumulated.endswith(next_chunk[:ol]):
                        overlap = ol
                        break
                appended = next_chunk[overlap:].strip()
                if appended:
                    if not accumulated.endswith(" ") and not appended.startswith(" "):
                        accumulated = accumulated + " " + appended
                    else:
                        accumulated = accumulated + appended
                if not re.search(r"\w$", accumulated):
                    break

        # Post-process accumulated text: remove excessive newlines, dedupe
        # consecutive repeated sentences, fix spacing around punctuation and
        # return a single coherent long text.
        try:
            # normalize whitespace
            t = re.sub(r"[\r\t]+", " ", accumulated)
            t = re.sub(r"\n{2,}", "\n", t)

            # split into sentence-like chunks (keep semicolons too since
            # downstream sanitization may convert periods)
            parts = re.split(r'(?<=[\.\!\?\;…])\s+', t)
            cleaned_parts = []
            prev_norm = None
            for p in parts:
                s = p.strip()
                if not s:
                    continue
                # normalize for duplication check: lowercase, remove punctuation and extra spaces
                norm = re.sub(r"[^a-z0-9]+", "", s.lower(), flags=re.UNICODE)
                if norm == prev_norm:
                    continue
                cleaned_parts.append(s)
                prev_norm = norm

            cleaned = " ".join(cleaned_parts)

            # fix spacing before punctuation and ensure single space after punctuation
            cleaned = re.sub(r"\s+([,;:\.!\?])", r"\1", cleaned)
            cleaned = re.sub(r"([,;:\.!\?])(?!\s)", r"\1 ", cleaned)
            cleaned = re.sub(r"\s{2,}", " ", cleaned).strip()

            # final safety: collapse stray newlines to spaces
            cleaned = re.sub(r"\s*\n\s*", " ", cleaned)

        except Exception:
            cleaned = re.sub(r"\s+", " ", accumulated).strip()

        return cleaned

    return text

def create_output_folder():
    """Cria pasta de saída."""
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_folder = os.path.join("output", timestamp)
    os.makedirs(output_folder, exist_ok=True)
    print(f"📁 Pasta de saída criada: {output_folder}")
    return output_folder

def sanitize_Text(text):
    """Sanitiza o texto removendo espaços extras e linhas em branco."""
    # Remove espaços extras
    text = re.sub(r'[ \t]+', ' ', text)
    # Remove linhas em branco
    text = re.sub(r'\n\s*\n', '\n', text)
    # Remover os \n
    text = text.replace('\n', ' ')
    # Remove espaços no início e fim do texto
    text = text.strip()
    # Remove retissos desnecessários
    text = re.sub(r'\.{3,}', '...', text)
    # Troca pontos por vírgulas
    text = re.sub(r'(?<!\.)\.(?!\.)', ';', text)
    return text

def main(
        channel="parallelcuts",
        theme="pregacao",
        prompt_key=PROMPT_KEY,
        prompt_ollama=PROMPT_OLLAMA, 
        prompt_positive_comfy=PROMPT_POSITIVE_COMFY, 
        prompt_negative_comfy=PROMPT_NEGATIVE_COMFY,
        voice_name="Thom",
        voice_speed=1.0,
        voice_pitch=0.9,
        voice_volume=1.2,
        voice_radio_effect=True,
        subtitle_words_per_line=3,
        subtitle_font_size=55,
        subtitle_font_color=(255, 191, 0, 200),
        subtitle_font="Lilita.ttf",
        screen_orientation="MOBILE",
        force_text=None,
        generate_new_frames=True,
        perform_upload=True,
    ):
    """Gera vídeo completo."""

    print("🎬 INICIANDO GERAÇÃO DE VÍDEO")

    global PROGRESS, PROGRESS_MESSAGE
    PROGRESS = 1
    PROGRESS_MESSAGE = "iniciando"

    # =========================
    # TEXTO
    # =========================
    FORCE_TEXT = get_text_by_ollama(prompt_ollama, THEME) if force_text is None else force_text
    FORCE_TEXT = sanitize_Text(FORCE_TEXT)

    print(f"📝 Texto final para geração:\n{FORCE_TEXT}\n")

    PROGRESS = 5
    PROGRESS_MESSAGE = "texto pronto"

    # =========================
    # OUTPUT
    # =========================
    output_folder = create_output_folder()

    # =========================
    # ÁUDIO
    # =========================
    voice_gen = VoiceGenerator(
        speed=voice_speed,
        pitch=voice_pitch,
        volume=voice_volume,
        radio_fx=voice_radio_effect,
        voice_file_path=f"vozes/{voice_name}.wav",
        language="pt"
    )

    audio_path = os.path.join(output_folder, "audio.wav")

    print(f"🎤 Iniciando áudio às {datetime.now().strftime('%H:%M:%S')}...")
    audio_duration = voice_gen.generate_audio(FORCE_TEXT, audio_path)

    if audio_duration <= 0:
        PROGRESS = 0
        PROGRESS_MESSAGE = "falha no áudio"
        print("❌ Falha ao gerar áudio")
        return

    print(f"✅ Áudio gerado ({audio_duration:.2f}s)")
    PROGRESS = 30
    PROGRESS_MESSAGE = "áudio gerado"

    if CANCEL_EVENT and CANCEL_EVENT.is_set():
        PROGRESS = 0
        PROGRESS_MESSAGE = "cancelado"
        print("⚠️ Cancelado após áudio")
        return

    # =========================
    # VISUAL (COMFY)
    # =========================
    if generate_new_frames:
        try:
            comfy_gen = ComfySingleFrameVideoGenerator()
            print("🎨 Gerando visual base...")

            base_video = comfy_gen.generate(
                theme=theme,
                audio_duration=audio_duration,
                prompt_positive=prompt_positive_comfy,
                prompt_negative=prompt_negative_comfy,
                screen_orientation=screen_orientation,
            )

            print(f"✅ Visual gerado: {base_video}")
            PROGRESS = 60
            PROGRESS_MESSAGE = "visual gerado"

            if CANCEL_EVENT and CANCEL_EVENT.is_set():
                PROGRESS = 0
                PROGRESS_MESSAGE = "cancelado"
                print("⚠️ Cancelado após visual")
                return

        except Exception as e:
            print(f"❌ Erro no ComfyUI: {e}")
            PROGRESS = 0
            PROGRESS_MESSAGE = "erro visual"
            return
    else:
        print("ℹ️ Usando visual pré-gerado")

    # =========================
    # VÍDEO FINAL
    # =========================
    video_gen = VideoGenerator(
        theme=theme,
        channel=channel,
        zoom_strength=0.025,
        grain_intensity=0.08,
        vignette_intensity=0.9,
        screen_orientation=screen_orientation,
        subtitle_font=subtitle_font,
        subtitle_font_size=subtitle_font_size,
        subtitle_words_per_line=subtitle_words_per_line,
    )

    video_path = os.path.join(output_folder, "video.mp4")

    print(f"🎬 Gerando vídeo ({audio_duration:.1f}s)...")
    video_gen.generate_video(
        audio_path,
        subtitle_font_color,
        audio_duration,
        video_path,
        FORCE_TEXT
    )

    if os.path.exists(video_path):
        size_mb = os.path.getsize(video_path) / (1024 * 1024)
        print("✅ VÍDEO GERADO COM SUCESSO!")
        print(f"📍 {video_path}")
        print(f"⏱️ {audio_duration:.1f}s | 📦 {size_mb:.1f} MB")

        try:
            LAST_GENERATED_FILE = video_path
        except Exception:
            pass

        PROGRESS = 100
        PROGRESS_MESSAGE = "concluído"
    else:
        PROGRESS = 0
        PROGRESS_MESSAGE = "erro final"
        print("❌ Vídeo não foi criado")

    # -------------------------
    # Uploads condicionais
    # -------------------------
    if perform_upload:
        try:
            youtube_upload(theme, channel, FORCE_TEXT, screen_orientation)
        except Exception as e:
            print(f"❌ Erro ao iniciar upload para YouTube: {e}")



def cleanup_temp_files():
    """Limpeza simples e direta."""
    import os
    import glob
    
    patterns = [
        "temp_text_*",
        "tmpss_*", 
        "video_finalTEMP_MPY_*", 
        "temp-audio.*",
        "temp_*.mp4",
        "temp_*.wav",
        "temp_*.mp3",
    ]
    
    removed = 0
    for pattern in patterns:
        for file in glob.glob(pattern):
            try:
                if os.path.isfile(file):
                    os.remove(file)
                    removed += 1
            except:
                pass
    
    print(f"🧹 Limpeza realizada nos arquivos temporários")
    return removed

def get_most_recent_output_folder():
    """Retorna a pasta de saída mais recente que contenha video.mp4."""
    output_dir = "output"
    if not os.path.exists(output_dir):
        return None

    folders = [
        os.path.join(output_dir, f)
        for f in os.listdir(output_dir)
        if os.path.isdir(os.path.join(output_dir, f))
    ]

    # Ordena por data de modificação (mais recente primeiro)
    folders.sort(key=os.path.getmtime, reverse=True)

    for folder in folders:
        video_path = os.path.join(folder, "video.mp4")
        if os.path.isfile(video_path):
            return folder

    return None


def youtube_upload(theme, channel, text_narration, screen_orientation):
    # Upload para YouTube
    print("📤 Preparando upload para YouTube...")
    output_folder = get_most_recent_output_folder()
    if output_folder:
        video_path = os.path.join(output_folder, "video.mp4")
        if os.path.exists(video_path):
            youtube_manager = YouTubeManager(screen_orientation=screen_orientation)
            youtube_manager.automate_youtube_posting(theme, channel, text_narration, video_path)
            print("✅ Upload para YouTube iniciado!")
        else:
            print("❌ Vídeo não encontrado na pasta de saída.")
    else:
        print("❌ Nenhuma pasta de saída encontrada.")

if __name__ == "__main__":
    while True:
        start_time = time.time()  # ⏱️ início
        try:
            main(
                channel=CHANNEL,
                theme=THEME,
                prompt_key=PROMPT_KEY,
                prompt_ollama=PROMPT_OLLAMA,
                prompt_positive_comfy=PROMPT_POSITIVE_COMFY,
                prompt_negative_comfy=PROMPT_NEGATIVE_COMFY,
                voice_name=VOICE_NAME,
                voice_speed=VOICE_SPEED,
                voice_pitch=VOICE_PITCH,
                voice_volume=VOICE_VOLUME,
                voice_radio_effect=VOICE_RADIO_EFFECT,
                subtitle_words_per_line=SUBTITLE_WORDS_PER_LINE,
                subtitle_font_size=SUBTITLE_FONT_SIZE,
                subtitle_font_color=SUBTITLE_FONT_COLOR,
                subtitle_font=SUBTITLE_FONT,
                screen_orientation=SCREEN_ORIENTATION,
                force_text=FORCE_TEXT,
                generate_new_frames=GENERATE_NEW_FRAMES,
            )

        except Exception as e:
            print(f"❌ Erro: {e}")

        finally:
            cleanup_temp_files()

            elapsed = time.time() - start_time
            hours = int(elapsed // 3600)
            minutes = int((elapsed % 3600) // 60)
            seconds = int(elapsed % 60)

            print("🧹 Limpeza concluída")
            print(f"⏱️ Tempo total de execução: {hours}h {minutes}m {seconds}s")

        #pausar por 3 horas
        time.sleep(3*60*60)