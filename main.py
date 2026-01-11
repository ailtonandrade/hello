import pyautogui
import time
import os
import pyperclip
import subprocess
from youtube_manager import YouTubeManager
from local_title_description_generator import LocalTitleDescriptionGenerator

def click_image(image_path, confidence=0.8, region=None, offset_x=0, offset_y=0):
    try:
        location = pyautogui.locateOnScreen(image_path, confidence=confidence, region=region)
        if location:
            center_x = location.left + location.width // 2 + offset_x
            center_y = location.top + location.height // 2 + offset_y
            pyautogui.click(center_x, center_y)
            print(f"Clicou em [{image_path}] em ({center_x}, {center_y})")
        else:
            print("Imagem não encontrada na tela.")
    except Exception as e:
        print(f"Erro ao procurar a imagem: {image_path}")

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

def youtube_manager():
    # Instanciar gerenciadores
    channel = "parallelcuts"
    theme = "pregacao"  # Variável de tema para geração de título e descrição
    title_description_generator = LocalTitleDescriptionGenerator()
    youtube_manager = YouTubeManager()

    # ABRE JANELA
    try:
        wait(4)
        open_or_launch_window("C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe")
        wait(5)
        press_hotkey("win", "shift", "up")
        press_hotkey("win", "left")
        wait(2)
    except Exception as e:
        print(f"Erro ao abrir o Chrome: {e}")
        return

    # ACESSA YOUTUBE
    try:
        click_image("fav-youtube.png", region=(0, 0, 320, 1080), offset_x=10, offset_y=10)
        wait(4)
        click_image("barra-url-youtube.png", region=(0, 0, 320, 1080), offset_x=10, offset_y=10)
        time_now = time.strftime("%M%S", time.localtime())
        type_text("youtube.com/results?search_query=" + theme + "&sp=EgQIAhAJ")
        wait(2)
        press_hotkey("enter")
        wait(7)
        click_image("botao-todos-youtube.png", region=(0, 0, 1920, 1080), offset_x=200, offset_y=10)
        wait(3)
        click_image("botao-unclick-shorts-youtube.png", region=(0, 0, 1920, 1080), offset_x=70, offset_y=100)
        wait(3)
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
        video_info = youtube_manager.download_video(url, download_path="./downloads")
        if video_info:
            print(f"Vídeo salvo em: {video_info['filepath']}\nObtendo informações do vídeo...")

            # PROCESSA E EDITA VIDEO
            youtube_manager.process_downloaded_video(video_info, channel)

            # OBTER INFOS DO VIDEO
            generated_info = title_description_generator.generate(theme)
            video_info["generated_info"] = generated_info

            if generated_info["title"]:
                print("Título gerado:", generated_info["title"])
                wait(1)

            if generated_info["description"]:
                print("Descrição gerada:", generated_info["description"])
                wait(1)

    except Exception as e:
        print(f"Erro ao baixar ou processar o vídeo: {e}")
        press_hotkey("alt", "f4")  # Fecha a janela do Chrome
        return

    #ACESSA PARA POSTAR
    click_image("fav-youtube.png", region=(0, 0, 1920, 1080), offset_x=10, offset_y=10)
    wait(8)
    click_image("botao-criar-youtube.png", region=(0, 0, 1920, 1080), offset_x=10, offset_y=10)
    wait(2)
    click_image("botao-enviar-video-youtube.png", region=(0, 0, 1920, 1080), offset_x=10, offset_y=10)
    wait(4)
    click_image("botao-selecionar-arquivos-youtube.png", region=(0, 0, 1920, 1080), offset_x=10, offset_y=10)
    wait(4)

    #ENCONTRAR VIDEO NA PASTA
    if video_info and "filepath" in video_info:
        if not os.path.exists(video_info['filepath']):
            print("Caminho do vídeo não encontrado:", video_info['filepath'])
            return
        click_image("botao-nova-pasta-windows.png", region=(0, 0, 1920, 1080), offset_x=-20, offset_y=-25)
        wait(4)
        video_folder_path = os.path.dirname(os.path.abspath(video_info['filepath']))
        type_text(video_folder_path)
        wait(2)
        press_hotkey("enter")
        wait(1)
        press_hotkey("tab")
        wait(1)
        press_hotkey("tab")
        wait(1)
        press_hotkey("tab")
        wait(1)
        press_hotkey("tab")
        wait(1)
        press_hotkey("space")
        wait(1)
        press_hotkey("enter")

        #INSERE TITULO E DESCRICAO
        wait(15)
        click_image("label-titulo-youtube.png", region=(0, 0, 1920, 1080), offset_x=10, offset_y=10)
        wait(5)
        press_hotkey("ctrl", "a")
        wait(2)
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
        click_image("botao-avancar-publicando-youtube.png", region=(0, 0, 1920, 1080), offset_x=10, offset_y=10)
        wait(2)
        press_hotkey("space")
        wait(1)
        press_hotkey("down")
        wait(1)
        press_hotkey("down")
        wait(1)
        click_image("botao-avancar-publicando-youtube.png", region=(0, 0, 1920, 1080), offset_x=10, offset_y=10)
        wait(2)
        click_image("botao-avancar-publicando-youtube.png", region=(0, 0, 1920, 1080), offset_x=10, offset_y=10)
        wait(2)
        click_image("botao-avancar-publicando-youtube.png", region=(0, 0, 1920, 1080), offset_x=10, offset_y=10)
        wait(2)
        click_image("botao-publico-publicando-youtube.png", region=(0, 0, 1920, 1080), offset_x=10, offset_y=10)
        wait(2)
        click_image("botao-publicar-publicando-youtube.png", region=(0, 0, 1920, 1080), offset_x=10, offset_y=10)
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

if __name__ == "__main__":
    print("🚀 Script de macros iniciado")

    while True:
        wait_time = 20*60  # Espera 5 minutos para que um novo vídeo seja publicado

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