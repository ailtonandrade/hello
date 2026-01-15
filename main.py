import pyautogui
import time
import os
import pyperclip
import subprocess
import random
from moviepy.editor import concatenate_videoclips, CompositeVideoClip, AudioFileClip, VideoFileClip
from moviepy.audio.AudioClip import concatenate_audioclips
from youtube_manager import YouTubeManager
from local_title_description_generator import LocalTitleDescriptionGenerator
from video_editor import VideoEditor
from moviepy.video.VideoClip import ColorClip, ImageClip
from PIL import Image, ImageDraw, ImageFont
import glob
from video_generator import generate_bible_video
from coquitts.voice_generator import generate_voice
from youtube_api_uploader import upload_video_to_youtube

# Define a global variable for screen orientation
SCREEN_ORIENTATION = "MOBILE"  # Options: "DESKTOP" or "MOBILE"

# Define global variables for channel and theme
CHANNEL = "parallelcuts"  # Replace with your default channel
THEME = "pregacao"  # Replace with your default theme

def click_image(image_path, confidence=0.8, region=None, offset_x=0, offset_y=0, retries=3, delay=1):
    attempt = 0
    while attempt < retries:
        try:
            location = pyautogui.locateOnScreen(image_path, confidence=confidence, region=region)
            if location:
                center_x = location.left + location.width // 2 + offset_x
                center_y = location.top + location.height // 2 + offset_y
                pyautogui.click(center_x, center_y)
                print(f"Clicou em [{image_path}] em ({center_x}, {center_y})")
                return  # Se a imagem for clicada, sai da função
            else:
                wait(10)
                print(f"Tentativa {attempt + 1}: Imagem não encontrada na tela.")
        except Exception as e:
            print(f"Tentativa {attempt + 1}: Erro ao procurar a imagem: {image_path} - {str(e)}")
       
        attempt += 1
        time.sleep(delay)  # Espera antes de tentar novamente
   
    print(f"Falha ao encontrar ou clicar na imagem após {retries} tentativas.")

def click_position(x, y):
    pyautogui.click(x, y)
    print(f"Clicou na posição ({x}, {y})")

def type_text(text, interval=0.1):
    try:
        # Copia o texto para a área de transferência
        pyperclip.copy(text)
        print(f"Texto copiado para a área de transferência: {text}")

        # Cola o texto no local desejado
        pyautogui.hotkey("ctrl", "v")
        print(f"Texto colado: {text}")
    except Exception as e:
        print(f"Erro ao digitar texto: {e}")

def wait(seconds):
    time.sleep(seconds)
    print(f"Aguardou {seconds} segundos")

def press_hotkey(*keys):
    pyautogui.hotkey(*keys)
    print(f"Hotkey pressionada: {' + '.join(keys)}")

def scroll_down(amount):
    pyautogui.scroll(-amount)
    print(f"Rolou para baixo {amount} unidades")

def load_files(folder, extensions):
    return [os.path.join(folder, f) for f in os.listdir(folder) if f.endswith(extensions)]

def adjust_video_aspect_ratio(video, aspect_ratio):
    target_aspect_ratio = aspect_ratio[0] / aspect_ratio[1]
    video_width, video_height = video.size
    current_aspect_ratio = video_width / video_height

    if current_aspect_ratio != target_aspect_ratio:
        new_width = int(video_height * target_aspect_ratio)
        new_height = int(video_width / target_aspect_ratio)

        if current_aspect_ratio > target_aspect_ratio:
            crop_width = (video_width - new_width) // 2
            video = video.crop(x1=crop_width, y1=0, x2=video_width - crop_width, y2=video_height)
        else:
            crop_height = (video_height - new_height) // 2
            video = video.crop(x1=0, y1=crop_height, x2=video_width, y2=video_height - crop_height)

    return video

def select_random_video(theme):
    """
    Seleciona um vídeo aleatório da pasta videos/{theme} com base no padrão {theme}001, {theme}002, etc.
    """
    video_files = glob.glob(f"videos/{theme}*.mp4")
    if not video_files:
        print(f"No videos found for theme: {theme}. Using a blank background.")
        return None
    return random.choice(video_files)

def repeat_video_to_duration(video_path, duration):
    """
    Repete o vídeo para preencher a duração total especificada.
    """
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

def youtube_manager():
    try:
        video_path = generate_bible_video(duration=30)
        if not video_path:
            print("Failed to generate video. No valid content available.")
            return

        # Define metadata for the video
        title = "Bible Verse Video"
        description = "Inspirational Bible verses brought to life."

        # Upload the video using the YouTube API
        response = upload_video_to_youtube(video_path, title, description)
        if response:
            print("Video uploaded successfully:", response)
        else:
            print("Failed to upload video.")

    except Exception as e:
        print(f"Error in YouTube manager: {e}")

    # ABRE JANELA
    try:
        wait(3)
        open_or_launch_window("C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe")
        wait(7)
        press_hotkey("win", "shift", "up")
        press_hotkey("win", "left")
        wait(2)
    except Exception as e:
        print(f"Erro ao abrir o Chrome: {e}")
        return

    # ACESSA YOUTUBE
    try:
        click_image("fav-youtube.png", region=(0, 0, 320, 1080), offset_x=10, offset_y=10)
        wait(3)
        click_image("barra-url-youtube.png", region=(0, 0, 320, 1080), offset_x=10, offset_y=10)
        type_text("youtube.com/results?search_query=" + THEME + "&sp=EgQIAxAJ")
        wait(3)
        press_hotkey("enter")
        wait(40)
        click_image("botao-lupa-youtube.png", region=(0, 0, 1920, 1080), offset_x=-200, offset_y=200)
        wait(20)
        scroll_down(500)
    except Exception as e:
        print(f"Erro ao acessar o YouTube: {e}")
        press_hotkey("alt", "f4")  # Fecha a janela do Chrome
        return

    # CAPTURA URL VIDEO
    try:
        click_image("barra-url-youtube.png", region=(0, 0, 320, 1080), offset_x=10, offset_y=10)
        press_hotkey("ctrl", "c")
        url = get_clipboard_text()
        print(f"URL copiada: {url}")
    except Exception as e:
        print(f"Erro ao capturar URL do vídeo: {e}")
        press_hotkey("alt", "f4")  # Fecha a janela do Chrome
        return

    # DOWNLOAD VIDEO
    video_info = {
        "filepath": "",
        "generated_info": {
            "title": "",
            "description": ""
        },
    }
    try:
        # video_info = youtube_manager.download_video(url, download_path="./downloads")
        video_info["filepath"] = video_path
        if video_info:
            print(f"Vídeo salvo em: {video_info['filepath']}\nObtendo informações do vídeo...")

            # OBTER INFOS DO VIDEO
            generated_info = title_description_generator.generate(THEME)
            video_info["generated_info"] = generated_info

            if generated_info["title"]:
                print("Título gerado:", generated_info["title"])
                wait(1)

            if generated_info["description"]:
                print("Descrição gerada:", generated_info["description"])
                wait(1)

            # PROCESSA E EDITA VIDEO
            youtube_manager.process_downloaded_video(video_info, CHANNEL)

    except Exception as e:
        print(f"Erro ao baixar ou processar o vídeo: {e}")
        press_hotkey("alt", "f4")  # Fecha a janela do Chrome
        return

    #ACESSA PARA POSTAR
    click_image("fav-youtube.png", region=(0, 0, 1920, 1080), offset_x=10, offset_y=10)
    wait(18)
    click_image("botao-criar-youtube.png", region=(0, 0, 1920, 1080), offset_x=10, offset_y=10)
    wait(14)
    click_image("botao-enviar-video-youtube.png", region=(0, 0, 1920, 1080), offset_x=10, offset_y=10)
    wait(25)
    click_image("botao-selecionar-arquivos-youtube.png", region=(0, 0, 1920, 1080), offset_x=10, offset_y=10)
    wait(25)

    #ENCONTRAR VIDEO NA PASTA
    if video_info and "filepath" in video_info:
        if not os.path.exists(video_info['filepath']):
            print("Caminho do vídeo não encontrado:", video_info['filepath'])
            return
        click_image("botao-nova-pasta-windows.png", region=(0, 0, 1920, 1080), offset_x=-20, offset_y=-25)
        wait(3)
        video_folder_path = os.path.dirname(os.path.abspath(video_info['filepath']))
        type_text(video_folder_path)
        wait(3)
        press_hotkey("enter")
        wait(11)
        press_hotkey("tab")
        wait(3)
        press_hotkey("tab")
        wait(3)
        press_hotkey("tab")
        wait(3)
        press_hotkey("tab")
        wait(3)
        press_hotkey("space")
        wait(3)
        press_hotkey("enter")

        #INSERE TITULO E DESCRICAO
        wait(15)
        click_image("label-titulo-youtube.png", region=(0, 0, 1920, 1080), offset_x=10, offset_y=10)
        wait(5)
        press_hotkey("ctrl", "a")
        wait(3)
        press_hotkey("backspace")
        wait(2)
        if video_info and "generated_info" in video_info:
            type_text(video_info["generated_info"]["title"])
   
        wait(5)
        click_image("label-descricao-youtube.png", region=(0, 0, 1920, 1080), offset_x=10, offset_y=10)
        wait(5)
        if video_info and "generated_info" in video_info:
            type_text(video_info["generated_info"]["description"])
        wait(5)

        #POSTAR VIDEO
        click_image("botao-avancar-publicando-youtube.png", region=(0, 0, 1920, 1920), offset_x=10, offset_y=10)
        wait(5)
        press_hotkey("space")
        wait(5)
        press_hotkey("down")
        wait(5)
        press_hotkey("down")
        wait(5)
        click_image("botao-avancar-publicando-youtube.png", region=(0, 0, 1920, 1920), offset_x=10, offset_y=10)
        wait(5)
        click_image("botao-avancar-publicando-youtube.png", region=(0, 0, 1920, 1920), offset_x=10, offset_y=10)
        wait(5)
        click_image("botao-avancar-publicando-youtube.png", region=(0, 0, 1920, 1920), offset_x=10, offset_y=10)
        wait(5)
        click_image("botao-publico-publicando-youtube.png", region=(0, 0, 1920, 1920), offset_x=10, offset_y=10)
        wait(5)
        click_image("botao-publicar-publicando-youtube.png", region=(0, 0, 1920, 1920), offset_x=10, offset_y=10)
    else:
        print("Caminho do vídeo não disponível para upload.")

def get_clipboard_text():
    try:
        text = pyperclip.paste()
        print(f"Texto capturado da área de transferência: {text}")
        return text
    except Exception as e:
        print(f"Erro ao capturar texto da área de transferência: {e}")
        return None

def open_or_launch_window(executable_path):
    try:
        # Abre o programa diretamente, sem verificar processos existentes
        subprocess.Popen(executable_path, shell=True)
        print(f"Abrindo uma nova janela do programa: {executable_path}")
    except Exception as e:
        print(f"Erro ao abrir o programa: {e}")

def add_voice_to_video(video, text, output_audio_path):
    """
    Generate voice from text and add it to the video.

    Args:
        video: The video clip to add the audio to.
        text (str): The text to convert to speech.
        output_audio_path (str): The path to save the generated audio file.

    Returns:
        Video clip with the added audio.
    """
    generate_voice(text, output_audio_path)

    # Add the generated audio to the video
    audio_clip = AudioFileClip(output_audio_path)
    return video.set_audio(audio_clip)

if __name__ == "__main__":
    print("🚀 Script de macros iniciado")
    #canais parallelcuts e tomteccortes
    channel = "parallelcuts"
    theme = "pregacao"  # Variável de tema para geração de título e descrição
    minutos_cooldown = 2
   
    # Ensure title_description_generator is defined
    # Assuming LocalTitleDescriptionGenerator is the intended class
    title_description_generator = LocalTitleDescriptionGenerator()

    while True:
        wait_time = minutos_cooldown*60  # Espera 1 hora para que um novo vídeo seja publicado

        try:
            youtube_manager()
            #print da contagem regressiva ate a nova postagem
            while wait_time > 0:
                mins, secs = divmod(wait_time, 60)
                timeformat = '{:02d}:{:02d}'.format(mins, secs)
                print(f"Próxima postagem em: {timeformat}", end='\r')
                wait(1)
                wait_time -= 1
        except Exception as e:
            print(f"❌ Erro geral: {e}")
            #print da contagem regressiva ate a nova postagem
            while wait_time > 0:
                mins, secs = divmod(wait_time, 60)
                timeformat = '{:02d}:{:02d}'.format(mins, secs)
                print(f"Próxima postagem em: {timeformat}", end='\r')
                wait(1)
                wait_time -= 1

            youtube_manager()