import pyautogui
import time
import os
import pyperclip
import subprocess
from youtube_oauth import get_access_token, youtube_upload_video

class YouTubeManager:
    def __init__(self, screen_orientation="MOBILE"):
        self.screen_orientation = screen_orientation

    def click_image(self, image_path, confidence=0.8, region=None, offset_x=0, offset_y=0, retries=3, delay=1):
        attempt = 0
        image_path = os.path.join("images", image_path)
        while attempt < retries:
            try:
                location = pyautogui.locateOnScreen(image_path, confidence=confidence, region=region)
                if location:
                    center_x = location.left + location.width // 2 + offset_x
                    center_y = location.top + location.height // 2 + offset_y
                    pyautogui.click(center_x, center_y)
                    print(f"Clicou em [{image_path}] em ({center_x}, {center_y})")
                    return True
                else:
                    time.sleep(10)
                    print(f"Tentativa {attempt + 1}: Imagem não encontrada na tela.")
            except Exception as e:
                print(f"Tentativa {attempt + 1}: Erro ao procurar a imagem: {image_path} - {str(e)}")
           
            attempt += 1
            time.sleep(delay)
       
        print(f"Falha ao encontrar ou clicar na imagem após {retries} tentativas.")
        return False

    def type_text(self, text, interval=0.1):
        try:
            pyperclip.copy(text)
            print(f"Texto copiado para a área de transferência: {text}")
            pyautogui.hotkey("ctrl", "v")
            print(f"Texto colado: {text}")
            return True
        except Exception as e:
            print(f"Erro ao digitar texto: {e}")
            return False

    def wait(self, seconds):
        time.sleep(seconds)
        print(f"Aguardou {seconds} segundos")

    def press_hotkey(self, *keys):
        pyautogui.hotkey(*keys)
        print(f"Hotkey pressionada: {' + '.join(keys)}")

    def scroll_down(self, amount):
        pyautogui.scroll(-amount)
        print(f"Rolou para baixo {amount} unidades")

    def get_clipboard_text(self):
        try:
            text = pyperclip.paste()
            print(f"Texto capturado da área de transferência: {text}")
            return text
        except Exception as e:
            print(f"Erro ao capturar texto da área de transferência: {e}")
            return None

    def open_or_launch_window(self, executable_path):
        try:
            subprocess.Popen(executable_path, shell=True)
            print(f"Abrindo uma nova janela do programa: {executable_path}")
            return True
        except Exception as e:
            print(f"Erro ao abrir o programa: {e}")
            return False

    def automate_youtube_posting(self, theme, channel, title_description_generator, video_path=None):
        """
        Primeiro tenta via OAuth.
        Se falhar, cai para modo manual.
        """

        video_info = {
            "filepath": video_path,
            "generated_info": title_description_generator.generate(theme)
        }

        # 1️⃣ tenta modo moderno
        if self.upload_youtube_oauth(video_info):
            return

        # 2️⃣ fallback manual
        self.upload_youtube_manual(
            theme,
            channel,
            title_description_generator,
            video_path
        )
        
    def upload_youtube_manual(self, theme, channel, title_description_generator, video_path=None):
        """
        Automate the YouTube posting process.
        """
        try:
            # ABRE JANELA
            self.wait(3)
            self.open_or_launch_window("C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe")
            self.wait(7)
            self.press_hotkey("win", "shift", "up")
            self.press_hotkey("win", "left")
            self.wait(2)
        except Exception as e:
            print(f"Erro ao abrir o Chrome: {e}")
            return

        # ACESSA YOUTUBE
        try:
            self.click_image("fav-youtube.png", region=(0, 0, 320, 1080), offset_x=10, offset_y=10)
            self.wait(3)
        except Exception as e:
            print(f"Erro ao acessar o YouTube: {e}")
            self.press_hotkey("alt", "f4")
            return
        

        # Generate video info if not provided
        video_info = {
            "filepath": video_path,
            "generated_info": title_description_generator.generate(theme) if title_description_generator else {}
        }

        # ACESSA PARA POSTAR
        self.wait(5)
        self.click_image("fav-youtube.png", region=(0, 0, 1020, 1020), offset_x=10, offset_y=10)
        self.wait(5)
        self.click_image("botao-criar-youtube.png", region=(0, 0, 1920, 1920), offset_x=10, offset_y=10)
        self.wait(2)
        self.click_image("botao-enviar-video-youtube.png", region=(0, 0, 1920, 1080), offset_x=10, offset_y=10)
        self.wait(10)
        
        # Upload process...
        self._upload_video_manual(video_info)

    def upload_youtube_oauth(self, video_info):
        try:
            youtube_upload_video(
                video_path=video_info["filepath"],
                title=video_info["generated_info"]["title"],
                description=video_info["generated_info"]["description"],
                is_short=True
            )
            return True
        except Exception as e:
            print(f"⚠️ OAuth falhou, fallback manual: {e}")
            return False



    def _upload_video_manual(self, video_info):
        """Internal method to handle video upload."""
        if not video_info or "filepath" not in video_info or not os.path.exists(video_info['filepath']):
            print("Caminho do vídeo não encontrado.")
            return

        self.click_image("botao-selecionar-arquivos-youtube.png", region=(0, 0, 1920, 1080), offset_x=10, offset_y=10)
        self.wait(5)
        
        # Navigate to video folder
        self.click_image("botao-nova-pasta-windows.png", region=(0, 0, 1920, 1080), offset_x=-20, offset_y=-25)
        self.wait(3)
        
        video_folder_path = os.path.dirname(os.path.abspath(video_info['filepath']))
        self.type_text(video_folder_path)
        self.wait(3)
        self.press_hotkey("enter")
        self.wait(2)
        
        # Select video file
        for _ in range(4):
            self.press_hotkey("tab")
            self.wait(3)

        self.press_hotkey("down")
        self.press_hotkey("space")
        self.wait(1)
        self.press_hotkey("enter")

        # Fill title and description
        self._fill_video_info(video_info)
        
        # Complete upload process
        self._complete_upload()

    def _fill_video_info(self, video_info):
        """Fill video title and description."""
        self.wait(15)
        self.click_image("label-titulo-youtube.png", region=(0, 0, 1920, 1080), offset_x=10, offset_y=10)
        self.wait(5)
        self.press_hotkey("ctrl", "a")
        self.wait(3)
        self.press_hotkey("backspace")
        self.wait(2)
        
        if "generated_info" in video_info and "title" in video_info["generated_info"]:
            self.type_text(video_info["generated_info"]["title"])
       
        self.wait(5)
        self.click_image("label-descricao-youtube.png", region=(0, 0, 1920, 1080), offset_x=10, offset_y=10)
        self.wait(5)
        
        if "generated_info" in video_info and "description" in video_info["generated_info"]:
            self.type_text(video_info["generated_info"]["description"])
        self.wait(5)

    def _complete_upload(self):
        """Complete the YouTube upload process."""
        self.wait(3)
        self.click_image("botao-avancar-publicando-youtube.png", region=(0, 0, 1920, 1920), offset_x=10, offset_y=10)
        self.wait(5)
        self.press_hotkey("space")
        self.wait(5)
        self.press_hotkey("down")
        self.wait(5)
        self.press_hotkey("down")
        self.wait(5)
        
        # Click through remaining steps
        for _ in range(3):
            self.click_image("botao-avancar-publicando-youtube.png", region=(0, 0, 1920, 1920), offset_x=10, offset_y=10)
            self.wait(5)
        
        self.click_image("botao-publico-publicando-youtube.png", region=(0, 0, 1920, 1920), offset_x=10, offset_y=10)
        self.wait(5)
        self.click_image("botao-publicar-publicando-youtube.png", region=(0, 0, 1920, 1920), offset_x=10, offset_y=10)
        print("Vídeo publicado com sucesso!")