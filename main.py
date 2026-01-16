import time
import os
import random
from datetime import datetime
from voice_generator import VoiceGenerator
from video_generator import VideoGenerator
from youtube_manager import YouTubeManager
from local_title_description_generator import LocalTitleDescriptionGenerator

# Define global variables for channel and theme
CHANNEL = "parallelcuts"
THEME = "pregacao"

def main():
    # Initialize generators
    voice_gen = VoiceGenerator()
    video_gen = VideoGenerator()
    youtube_mgr = YouTubeManager()
    title_gen = LocalTitleDescriptionGenerator()

    # Read full text from bible.txt
    with open("bible.txt", "r", encoding="utf-8") as file:
        verses = [line.strip() for line in file.readlines() if line.strip()]

    if len(verses) < 2:
        print("❌ Arquivo bible.txt precisa ter pelo menos 2 versículos!")
        return

    # Select 2 random consecutive verses
    start_index = random.randint(0, len(verses) - 2)
    selected_verses = verses[start_index:start_index + 2]
    full_text = " ".join(selected_verses)
    
    print(f"📖 Selecionados versículos {start_index + 1} a {start_index + 2}:")
    for i, verse in enumerate(selected_verses, 1):
        print(f"   {i}. {verse[:80]}{'...' if len(verse) > 80 else ''}")

    # Create output folder with current date and time
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_folder = os.path.join("output_data_geracao_completa", timestamp)
    os.makedirs(output_folder, exist_ok=True)
    print(f"📁 Pasta de saída criada: {output_folder}")

    print(f"📝 Processando texto completo ({len(full_text)} caracteres)...")

    # Generate audio for the complete text
    audio_path = os.path.join(output_folder, "audio_completo.wav")
    print("🎤 Gerando áudio com TTS Kokoro...")
    audio_duration = voice_gen.generate_audio(full_text, audio_path)

    if audio_duration == 0:
        print("❌ Falha ao gerar áudio")
        return

    print(f"✅ Áudio gerado com sucesso! Duração: {audio_duration:.2f} segundos")

    # Generate video with the audio duration
    video_path = os.path.join(output_folder, "video_final.mp4")
    print(f"🎬 Gerando vídeo com duração de {audio_duration:.2f} segundos...")
    video_gen.generate_video(audio_path, audio_duration, video_path, text=full_text)

    print(f"✅ Vídeo completo gerado: {video_path}")
    print(f"📦 Todos os arquivos estão em: {output_folder}\n")

def youtube_posting_cycle():
    """Main loop for YouTube posting automation"""
    title_description_generator = LocalTitleDescriptionGenerator()
    youtube_manager = YouTubeManager()
    
    minutos_cooldown = 2
    wait_time = minutos_cooldown * 60  # in seconds
    
    try:
        # Generate and post video
        youtube_manager.automate_youtube_posting(
            theme=THEME,
            channel=CHANNEL,
            title_description_generator=title_description_generator
        )
        
        # Countdown for next post
        while wait_time > 0:
            mins, secs = divmod(wait_time, 60)
            timeformat = '{:02d}:{:02d}'.format(mins, secs)
            print(f"Próxima postagem em: {timeformat}", end='\r')
            time.sleep(1)
            wait_time -= 1
            
    except Exception as e:
        print(f"❌ Erro geral no ciclo de postagem: {e}")
        # Continue with cooldown even on error
        while wait_time > 0:
            mins, secs = divmod(wait_time, 60)
            timeformat = '{:02d}:{:02d}'.format(mins, secs)
            print(f"Próxima postagem em: {timeformat}", end='\r')
            time.sleep(1)
            wait_time -= 1

if __name__ == "__main__":
    print("🚀 Script de macros iniciado")
    
    # Choose which function to run
    option = "1"
    if option == "1":
        main()
    elif option == "2":
        youtube_posting_cycle()
    else:
        print("Opção inválida")