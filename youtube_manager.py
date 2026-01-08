import os
import random
from pytubefix import YouTube
from templates import title_templates, description_templates

class YouTubeManager:
    def __init__(self):
        pass

    def download_video(self, url, download_path="./downloads"):
        """
        Baixa um vídeo do YouTube para o diretório especificado, criando uma subpasta com base no título do vídeo.

        :param url: URL do vídeo do YouTube.
        :param download_path: Caminho para salvar o vídeo baixado.
        :return: Dicionário com informações do vídeo baixado ou None se o download falhar.
        """
        # Remover parâmetros adicionais da URL
        if "&" in url:
            url = url.split("&")[0]
            print(f"URL limpa: {url}")

        if not os.path.exists(download_path):
            os.makedirs(download_path)

        try:
            # Obter informações do vídeo
            yt = YouTube(url)
            title = yt.title

            # Tentar encontrar streams em 1080p, 720p ou a melhor disponível
            streams_1080p = yt.streams.filter(res="1080p", progressive=True, file_extension='mp4')
            streams_720p = yt.streams.filter(res="720p", progressive=True, file_extension='mp4')
            best_stream = None

            if streams_1080p:
                best_stream = streams_1080p.first()
                print("Encontrado stream em 1080p.")
            elif streams_720p:
                best_stream = streams_720p.first()
                print("Encontrado stream em 720p.")
            else:
                best_stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
                if best_stream:
                    print(f"Nenhum stream em 1080p ou 720p. Baixando a melhor resolução disponível: {best_stream.resolution}.")
                else:
                    print("Nenhum stream disponível para download.")
                    return None

            # Criar subpasta com os 10 primeiros caracteres do título (sem espaços ou caracteres especiais)
            sanitized_title = ''.join(c for c in title[:20] if c.isalnum())
            subfolder = os.path.join(download_path, sanitized_title)
            if not os.path.exists(subfolder):
                os.makedirs(subfolder)

            # Nome do arquivo com título e resolução
            resolution = best_stream.resolution
            filename = f"{sanitized_title}_{resolution}.mp4"
            filepath = os.path.join(subfolder, filename)

            # Baixar o vídeo
            print(f"Baixando vídeo de {url} para {filepath}...")
            best_stream.download(output_path=subfolder, filename=filename)
            print("Download concluído!")

            # Obter tamanho do arquivo
            file_size = os.path.getsize(filepath) if os.path.exists(filepath) else None

            # Retornar informações do vídeo
            return {
                "title": title,
                "filepath": filepath,
                "extension": "mp4",
                "size": file_size
            }

        except Exception as e:
            print(f"Erro ao baixar o vídeo: {e}")
            return None

class LocalTitleDescriptionGenerator:
    def __init__(self):
        # Modelos de título e descrição importados do arquivo templates.py
        self.title_templates = title_templates
        self.description_templates = description_templates

    def generate(self, theme):
        """
        Gera um título e uma descrição com base no tema fornecido.

        :param theme: Tema para gerar o título e a descrição.
        :return: Dicionário com título e descrição gerados.
        """
        title = random.choice(self.title_templates).format(theme)
        description = random.choice(self.description_templates).format(theme)
        return {
            "title": title,
            "description": description
        }