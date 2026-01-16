import time
import os
import re
import random
from datetime import datetime
from voice_generator import VoiceGenerator
from video_generator import VideoGenerator

# Configurações fixas
CHANNEL = "parallelcuts"
THEME = "pregacao"
VOICE_NAME = "pm_santa"
VOICE_SPEED = 0.6
SUBTITLE_WORDS_PER_LINE = 3
SUBTITLE_FONT_SIZE = 45
SCREEN_ORIENTATION = "MOBILE"
SUBTITLE_FONT = "lilita.ttf"
FORCE_TEXT = """
    Irmãos e irmãs, [hoje] vamos meditar na poderosa [palavra] do [Senhor]!
    O [apóstolo] [Paulo] nos diz na [carta] aos [Romanos]:
    Essa [mensagem] foi escrita para fortalecer a [fé] dos que creem.
    Que o [Espírito] nos conduz e nos direciona a ser como [Cristo].
    """


def sanitize_text(text, force_text=None):

    if force_text:
        return force_text
    
    text = text.replace("\n", " ").replace("\r", " ").strip()
    text = re.sub(r'^\s*(\d+)\s+', '', text)
    text = re.sub(r'\.\s*(\d+)\s+', '.', text)
    
    return ' '.join(text.split())

def select_random_verses(verses, count=2):
    """Seleciona versículos consecutivos."""
    if len(verses) < count:
        return verses
    start_index = random.randint(0, len(verses) - count)
    return verses[start_index:start_index + count]

def create_output_folder():
    """Cria pasta de saída."""
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_folder = os.path.join("output", timestamp)
    os.makedirs(output_folder, exist_ok=True)
    return output_folder

def main():
    """Gera vídeo completo."""
    print("🎬 INICIANDO GERAÇÃO DE VÍDEO")
    
    # Carregar versículos
    try:
        with open("bible.txt", "r", encoding="utf-8") as file:
            verses = [line.strip() for line in file.readlines() if line.strip()]
        
        if len(verses) < 2:
            print("❌ bible.txt precisa ter pelo menos 2 versículos!")
            return
    except Exception as e:
        print(f"❌ Erro ao ler bible.txt: {e}")
        return
    
    # Selecionar versículos
    selected_verses = select_random_verses(verses, 2)
    full_text = " ".join(selected_verses)
    full_text = sanitize_text(full_text, FORCE_TEXT)
    print(f"📝 Texto: {full_text[:100]}...")
    
    # Criar pasta de saída
    output_folder = create_output_folder()
    
    # Gerar áudio
    voice_gen = VoiceGenerator(voice=VOICE_NAME, speed=VOICE_SPEED)
    audio_path = os.path.join(output_folder, "audio.wav")
    
    print("🎤 Gerando áudio...")
    audio_duration = voice_gen.generate_audio(full_text, audio_path)
    
    if audio_duration == 0:
        print("❌ Falha ao gerar áudio")
        return
    
    # Gerar vídeo
    video_gen = VideoGenerator(
        theme=THEME,
        channel=CHANNEL,
        screen_orientation=SCREEN_ORIENTATION,
        subtitle_font=SUBTITLE_FONT,
        subtitle_font_size=SUBTITLE_FONT_SIZE,
        subtitle_words_per_line=SUBTITLE_WORDS_PER_LINE,
        video_style="simple",
        optimize_memory=True
    )
    
    print(f"🎬 Gerando vídeo ({audio_duration:.1f}s)...")
    video_path = os.path.join(output_folder, "video.mp4")
    
    try:
        video_gen.generate_video(audio_path, audio_duration, video_path, full_text)
        
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

if __name__ == "__main__":
    try:
        main()
        pass
    except Exception as e:
        print(f"❌ Erro: {e}")
    finally:
        # Limpar arquivos temporários após terminar
        cleanup_temp_files()
        print("🧹 Limpeza concluída")