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
from local_title_description_generator import LocalTitleDescriptionGenerator

# Configurações fixas
CHANNEL = "parallelcuts"
THEME = "pregacao"
VOICE_NAME = "pm_alex" #pm_alex #pf_dora
VOICE_SPEED = 0.9
SUBTITLE_WORDS_PER_LINE = 3
SUBTITLE_FONT_SIZE = 55
SCREEN_ORIENTATION = "MOBILE"
SUBTITLE_FONT_COLOR = (255, 191, 0, 200)  # Amarelo âmbar
SUBTITLE_FONT = "Lilita.ttf"
FORCE_TEXT = None  # Defina uma string para forçar um texto específico

def get_text_by_ollama():
    prompt = """
    Gere UMA reflexão bública contextualizada em uma situação cotidiana.
    O texto deve parecer uma narração falada por um pastor fazendo uma ministração, natural e fluida.
    Não use linguagem acadêmica.
    Não faça listas.
    Não acrescente introduções nem conclusões.
    Não use emojis.
    Não use numeros romanos.
    Não use hífens em nenhuma parte do texto.
    Use pontuação para ajudar na entonação, como ; ! , ? ... .
    Use colchetes [] para destacar palavras importantes.
    Use linguagem simples, como se estivesse fazendo uma ministração.
    Use o português do Brasil.
    Não ultrapasse 50 palavras no total.
    Responda APENAS com o texto final, sem títulos, sem comentários extras e sem explicações fora do texto.
    """

    print("🧠 Enviando prompt para o Ollama...")
    print(f"⏳ [{datetime.now().strftime('%H:%M:%S')}] Aguardando resposta do modelo (gemma3:4b)...")

    try:
        result = subprocess.run(
            [
                "ollama", "run", "gemma3:1b",
            ],
            input=prompt,               # 👈 prompt vai no stdin
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
    text = re.sub(r'(?<!\.)\.(?!\.)', ',', text)

    return text

def main(channel="parallelcuts", theme="pregacao", voice_name="pm_alex", voice_speed=0.9, subtitle_words_per_line=3, subtitle_font_size=55, screen_orientation="MOBILE", subtitle_font_color=(255, 191, 0, 200), subtitle_font="Lilita.ttf", force_text=None):
    """Gera vídeo completo."""
    print("🎬 INICIANDO GERAÇÃO DE VÍDEO")
    
    FORCE_TEXT = get_text_by_ollama() if force_text is None else force_text

    FORCE_TEXT = sanitize_Text(FORCE_TEXT)

    # Criar pasta de saída
    output_folder = create_output_folder()
    
    # Gerar áudio
    voice_gen = VoiceGenerator(voice=voice_name, speed=voice_speed, volume=1.2, voice_file_path="vozes/audio001.wav")
    audio_path = os.path.join(output_folder, "audio.wav")
    
    print("🎤 Gerando áudio...")
    audio_duration = voice_gen.generate_audio(FORCE_TEXT, audio_path)
    
    if audio_duration == 0:
        print("❌ Falha ao gerar áudio")
        return
    
    # Gerar vídeo
    video_gen = VideoGenerator(
        theme=theme,
        channel=channel,
        screen_orientation=screen_orientation,
        subtitle_font=subtitle_font,
        subtitle_font_size=subtitle_font_size,
        subtitle_words_per_line=subtitle_words_per_line,
        video_style="simple",
        optimize_memory=True
    )
    
    print(f"🎬 Gerando vídeo ({audio_duration:.1f}s)...")
    video_path = os.path.join(output_folder, "video.mp4")
    
    try:
        video_gen.generate_video(audio_path, subtitle_font_color, audio_duration, video_path, FORCE_TEXT)
        
        if os.path.exists(video_path):
            size_mb = os.path.getsize(video_path) / (1024 * 1024)
            print(f"\n✅ VÍDEO GERADO COM SUCESSO!")
            print(f"📍 Local: {video_path}")
            print(f"⏱️  Duração: {audio_duration:.1f}s")
            print(f"📦 Tamanho: {size_mb:.1f} MB")
        else:
            print("❌ Vídeo não criado")
            
    except Exception as e:
        print(f"❌ Erro: {e}")


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

if __name__ == "__main__":
    try:
        main()
        youtube_upload("pregacao", "parallelcuts", "MOBILE")
    except Exception as e:
        print(f"❌ Erro: {e}")
    finally:
        # Limpar arquivos temporários após terminar
        cleanup_temp_files()
        print("🧹 Limpeza concluída")