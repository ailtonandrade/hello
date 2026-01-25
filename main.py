import time
import os
import re
import random
import subprocess
import json
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
THEME = "universe_sleep"
VOICE_NAME = "Thom" # deactivated
VOICE_SPEED = 1
VOICE_PITCH = 0.9
VOICE_VOLUME = 1.2
VOICE_RADIO_EFFECT = True
SUBTITLE_WORDS_PER_LINE = 3
SUBTITLE_FONT_SIZE = 55
SCREEN_ORIENTATION = "MOBILE"
SUBTITLE_FONT_COLOR = (255, 191, 0, 200)
SUBTITLE_FONT = "Lilita.ttf"
FORCE_TEXT = None
PROMPT_KEY = "universe_sleep"
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

def get_text_by_ollama(prompt_ollama):
    print("🧠 Enviando prompt para o Ollama...")
    print(f"⏳ [{datetime.now().strftime('%H:%M:%S')}] Aguardando resposta do modelo (gemma3:4b)...")

    try:
        result = subprocess.run(
            [
                "ollama", "run", "qwen2.5:7b-instruct",
            ],
            input=prompt_ollama,
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=True
        )

        if result.stdout.strip():
            print(f"✅ [{datetime.now().strftime('%H:%M:%S')}] Resposta recebida com sucesso.")
            return result.stdout.strip()
        else:
            print(f"⚠️ [{datetime.now().strftime('%H:%M:%S')}] Ollama respondeu, mas o texto veio vazio.")
            return None

    except subprocess.CalledProcessError as e:
        print("❌ Erro ao executar o Ollama.")
        print(f"STDERR: {e.stderr}")
        return None

    except Exception as e:
        print("❌ Erro inesperado ao chamar o Ollama.")
        print(e)
        return None

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
    ):
    """Gera vídeo completo."""

    print("🎬 INICIANDO GERAÇÃO DE VÍDEO")

    global PROGRESS, PROGRESS_MESSAGE
    PROGRESS = 1
    PROGRESS_MESSAGE = "iniciando"

    # =========================
    # TEXTO
    # =========================
    FORCE_TEXT = get_text_by_ollama(prompt_ollama) if force_text is None else force_text
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


def youtube_upload(theme, channel, screen_orientation):
    # Upload para YouTube
    print("📤 Preparando upload para YouTube...")
    output_folder = get_most_recent_output_folder()
    if output_folder:
        video_path = os.path.join(output_folder, "video.mp4")
        if os.path.exists(video_path):
            youtube_manager = YouTubeManager(screen_orientation=screen_orientation)
            title_desc_gen = LocalTitleDescriptionGenerator()
            youtube_manager.automate_youtube_posting(theme, channel, title_desc_gen, video_path)
            print("✅ Upload para YouTube iniciado!")
        else:
            print("❌ Vídeo não encontrado na pasta de saída.")
    else:
        print("❌ Nenhuma pasta de saída encontrada.")

def instagram_upload(theme, channel, screen_orientation):
    # Upload para Instagram
    print("📤 Preparando upload para Instagram...")
    output_folder = get_most_recent_output_folder()
    if output_folder:
        video_path = os.path.join(output_folder, "video.mp4")
        if os.path.exists(video_path):
            instagram_manager = InstagramManager(screen_orientation=screen_orientation)
            title_desc_gen = LocalTitleDescriptionGenerator()
            instagram_manager.automate_instagram_posting(theme, channel, title_desc_gen, video_path)
            print("✅ Upload para Instagram iniciado!")
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
            
            youtube_upload(THEME, CHANNEL, SCREEN_ORIENTATION)
            # instagram_upload("pregacao", "parallelcuts", "MOBILE")

        except Exception as e:
            print(f"❌ Erro: {e}")

        finally:
            cleanup_temp_files()

            elapsed = time.time() - start_time
            minutes = int(elapsed // 60)
            seconds = int(elapsed % 60)

            print("🧹 Limpeza concluída")
            print(f"⏱️ Tempo total de execução: {minutes}m {seconds}s")

        #pausar por 30 minutos
        time.sleep(30*60)