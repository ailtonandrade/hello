import os
import random
import glob
from moviepy.editor import concatenate_videoclips, CompositeVideoClip, AudioFileClip, VideoFileClip
from moviepy.audio.AudioClip import concatenate_audioclips
from moviepy.video.VideoClip import ColorClip, ImageClip
from PIL import Image, ImageDraw, ImageFont
from video_editor import add_text, add_logo, add_image

# Define a global variable for screen orientation
SCREEN_ORIENTATION = "MOBILE"  # Options: "DESKTOP" or "MOBILE"

# Utility functions

def load_files(folder, extensions):
    return [os.path.join(folder, f) for f in os.listdir(folder) if f.endswith(extensions)]

def select_random_video(theme):
    video_files = glob.glob(f"videos/{theme}*.mp4")
    if not video_files:
        print(f"No videos found for theme: {theme}. Using a blank background.")
        return None
    return random.choice(video_files)

def repeat_video_to_duration(video_path, duration):
    try:
        clip = VideoFileClip(video_path)
        clips = []
        total_duration = 0
        while total_duration < duration:
            clips.append(clip)
            total_duration += clip.duration
        return concatenate_videoclips(clips).subclip(0, duration)
    except Exception as e:
        print(f"Error repeating video {video_path}: {e}")
        return ColorClip(size=(1080, 1920), color=(0, 0, 0)).set_duration(duration)

def get_video_size():
    if SCREEN_ORIENTATION == "DESKTOP":
        return (1920, 1080)
    else:  # Default to MOBILE
        return (1080, 1920)

# Define global variables for channel and theme
CHANNEL = "parallelcuts"  # Replace with your default channel
THEME = "pregacao"  # Replace with your default theme


def generate_bible_video(duration=30):
    # Configurações centralizadas
    config = {
        "font_size": 67,
        "font_color": "yellow",
        "font_bold": True,
        "text_capslock": True,
        "line_spacing": 10,
        "padding_x": 170,  # Padding horizontal
        "padding_y": 50,  # Padding vertical
        "video_aspect_ratio": (9, 16),
    }

    # Caminhos para logo e imagem de subscribe
    logo_path = os.path.join('images', f'logo-canal-{CHANNEL}.jpg')  # Substituir pelo caminho real do logo
    subscribe_image_path = os.path.join('images', 'subscribe.png')  # Substituir pelo caminho real da imagem de subscribe

    # Selecionar vídeo de fundo
    background_video_path = select_random_video(THEME)
    video_size = get_video_size()

    if background_video_path:
        final_video = repeat_video_to_duration(background_video_path, duration)
        final_video = final_video.resize(video_size)  # Resize to match the orientation
    else:
        final_video = ColorClip(size=video_size, color=(0, 0, 0)).set_duration(duration)

    # Carregar versículos da Bíblia
    with open("bible.txt", "r", encoding="utf-8") as bible_file:
        verses = [line.strip() for line in bible_file if line.strip()]

    # Selecionar versículos para exibição
    if len(verses) < 3:
        print("Not enough verses available. Using all available verses.")
        verses_to_display = verses
    else:
        start_index = random.randint(0, len(verses) - 3)
        verses_to_display = verses[start_index:start_index + 3]

    # Adicionar texto ao vídeo
    for i, verse in enumerate(verses_to_display):
        final_video = add_text(
            video=final_video,
            text=verse,
            config=config,
            duration=duration / len(verses_to_display),
            start_time=i * (duration / len(verses_to_display))
        )

    # Adicionar logo
    final_video = add_logo(
        video=final_video,  # Passando o objeto de vídeo diretamente
        logo_path=logo_path,
        x_percent=0.45,  # Posição horizontal (5% da largura)
        y_percent=0.02,  # Posição vertical (5% da altura)
        size_multiplier=0.8,  # Tamanho relativo ao vídeo
        opacity=0.7  # Opacidade do logo
    )

    # Adicionar imagem de subscribe
    final_video = add_image(
        video=final_video,  # Passando o objeto de vídeo diretamente
        image_path=subscribe_image_path,
        x=0.2,  # Posição horizontal (80% da largura)
        y=0.7,  # Posição vertical (80% da altura)
        size_multiplier=0.8,  # Tamanho relativo ao vídeo
        opacity=0.6  # Opacidade da imagem
    )

    # Adicionar áudio
    audio_files = load_files("audios", ".mp3")
    audio_clips = []
    total_audio_duration = 0
    for audio_file in audio_files:
        if total_audio_duration >= duration:
            break
        try:
            audio_clip = AudioFileClip(audio_file)
            audio_clips.append(audio_clip)
            total_audio_duration += audio_clip.duration
        except Exception as e:
            print(f"Error loading audio file {audio_file}: {e}")

    if audio_clips:
        final_audio = concatenate_audioclips(audio_clips).subclip(0, duration)
        final_video = final_video.set_audio(final_audio)

    # Salvar vídeo final
    output_dir = "output_data_geraca_completa"
    os.makedirs(output_dir, exist_ok=True)
    output_path = f"{output_dir}/{THEME}_final_video.mp4"
    final_video.write_videofile(output_path, codec="libx264", audio_codec="aac", fps=24)

    return output_path