🎬 Hello Automation Suite - Youtube Downloader and Manager
<div align="center">
https://img.shields.io/badge/Python-3.13.0-blue.svg
https://img.shields.io/badge/Platform-Windows-0078D6.svg
https://img.shields.io/badge/Package_Manager-UV-FFD43B.svg
https://img.shields.io/badge/License-MIT-green.svg

Sistema completo de automação para criação e postagem de vídeos no YouTube

🚀 Começando • 📋 Pré-requisitos • ⚙️ Instalação • 📁 Estrutura • 🎯 Uso

</div>
✨ Recursos Principais
🎙️	Geração de Voz Realista - Usando Coqui TTS para áudio de alta qualidade (usa o python 3.11.14, tts não tem piedade de ninguém)
🎬	Edição Automática de Vídeo - Cria vídeos completos com MoviePy
🤖	Automação do YouTube - Posta vídeos automaticamente via OAUTH2 (boa sorte, google cloud te aguarda)
📝	Processamento de Texto - Usa Whisper para transcrição e eSpeak para TTS
🎨	Personalização Total - Temas, logos, overlays e elementos visuais
⚡	Otimizado para Windows - Configuração específica para Windows 10/11
📋 Pré-requisitos Obrigatórios (Windows)
1️⃣ Ferramentas de Compilação (CRÍTICO!)
powershell
# INSTALE PRIMEIRO! Sem isso nada funciona:

# 0. Baixe e instale o Ollama:
#    https://ollama.com/download/windows
#    Configure o ollama.exe no PATH das variáveis de ambiente do windows para usuário e sistema 

# 1. Baixe e instale o Visual Studio Build Tools:
#    https://visualstudio.microsoft.com/downloads/#build-tools-for-visual-studio-2022

# 2. Durante a instalação, SELECIONE:
#    ✅ "Desktop development with C++"
#    ✅ "Windows 10/11 SDK" (pelo menos versão 10.0.19041.0)

# 3. Após instalar, REINICIE o computador!
2️⃣ eSpeak NG (Síntese de Voz)
powershell
# 1. Baixe do site oficial:
#    https://github.com/espeak-ng/espeak-ng/releases
#    (Procure por "setup-espeak-ng-xxx.exe")

# 2. Instale normalmente (Next > Next > Finish)

# 3. Verifique se está no PATH:
#    - Pressione WIN + R, digite "sysdm.cpl"
#    - Clique em "Variáveis de Ambiente"
#    - Em "Variáveis do sistema", edite "Path"
#    - Adicione: "C:\Program Files\eSpeak NG" (ou onde instalou)
3️⃣ FFmpeg (Processamento de Vídeo/Audio)
powershell
# 1. Baixe do site oficial:
#    https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-full.7z

# 2. Extraia para: C:\ffmpeg

# 3. Adicione ao PATH do sistema:
#    - Pressione WIN + R, digite "sysdm.cpl"
#    - Variáveis de Ambiente > Path > Novo
#    - Adicione: C:\ffmpeg\bin

# 4. Teste no CMD:
#    ffmpeg -version
⚙️ Instalação
1️⃣ Clone o Repositório
powershell
# Abra o PowerShell ou CMD como Administrador

# Clone o repositório
git clone https://github.com/seu-usuario/youtube-automation.git
cd youtube-automation
2️⃣ Configure o Ambiente com UV
powershell
# Instale o UV (se ainda não tiver)
pip install uv

# Instale todas as dependências
uv add -r requirements.txt

# OU instale manualmente se tiver problemas:
uv add moviepy pyautogui pyperclip opencv-python pillow numpy soundfile
3️⃣ Instale Dependências Específicas
powershell
# Whisper (transcrição de áudio)
uv pip install openai-whisper

# Coqui TTS (geração de voz - PODE DAR TRABALHO NO WINDOWS!)
# Atentar-se a usar uv para criar o ambiente e python 3.11.14 ideal
Repositório do Coqui TTS
https://github.com/coqui-ai/TTS/tree/dev?tab=readme-ov-file#installation

📁 Estrutura do Projeto
text
📦 youtube-automation
├── 📜 main.py                         # Script principal de execução
├── 📜 voice_generator.py              # Geração de voz com Kokoro
├── 📜 video_generator.py              # Edição e criação de vídeos
├── 📜 youtube_manager.py              # Automação do YouTube
├── 📜 video_editor.py                 # Funções auxiliares de edição
├── 📜 youtube_manager.py              # Gerenciador do YouTube (antigo)
├── 📜 local_title_description_generator.py  # Gerador de títulos
├── 📜 bible.txt                       # Textos bíblicos para processar
│
├── 📁 videos/                         # VÍDEOS DE FUNDO (você precisa colocar aqui)
│   ├── pregacao001.mp4               # Vídeo de fundo para tema "pregacao"
│   ├── pregacao002.mp4
│   └── [tema]XXX.mp4                 # Padrão: {tema}{numero}.mp4
│
├── 📁 images/                         # IMAGENS E LOGOS
│   ├── logo-canal-parallelcuts.jpg   # Logo do canal
│   ├── logo-canal-tomteccortes.jpg   # Logo alternativo
│   └── subscribe.png                 # Imagem "Subscribe"
│
├── 📁 output_data_geracao_completa/   # VÍDEOS GERADOS (criado automaticamente)
├── 📁 downloads/                      # VÍDEOS BAIXADOS (criado automaticamente)
│
├── 📜 requirements.txt                # Lista de dependências
├── 📜 pyproject.toml                  # Configuração do UV
└── 📜 README.md                       # Este arquivo

🎯 Como Usar
Opção 1: Gerar Vídeos Localmente
powershell
# Execute o script principal
uv run main.py

# Isso irá:
# 1. Obter do Ollama um texto via prompt que foi passado
# 2. Gerar áudio com TTS e leganda com Whisper
# 3. Criar vídeos com os áudios
# 4. Salvar em output_data_geracao_completa/
Opção 2: Postar Automaticamente no YouTube
powershell
uv run main.py

# No menu, selecione:
# [2] Postar no YouTube
#
# ⚠️ IMPORTANTE: Configure antes!
# 2. Realize a oAuth2 do google rodando 
# youtube_oauth.py

# Gerar áudio
voice_gen = VoiceGenerator()
audio_duration = voice_gen.generate_audio("Seu texto aqui", "audio.wav")

# Gerar vídeo
video_gen = VideoGenerator(theme="pregacao", channel="parallelcuts")
video_gen.generate_video("audio.wav", audio_duration, "video_final.mp4")

⚠️ Troubleshooting - Problemas Comuns no Windows
❌ "error: Microsoft Visual C++ 14.0 or greater is required"
powershell
# SOLUÇÃO:
# 1. Instale/Reinstale o Visual Studio Build Tools (veja pré-requisitos)
# 2. Reinicie o computador
# 3. Tente instalar com --only-binary:
uv pip install --only-binary :all: numpy
❌ Kokoro não instala no Windows
powershell

❌ "FFmpeg not found"
powershell
# 1. Verifique se o FFmpeg está no PATH
# 2. Ou defina manualmente no código:
import os
os.environ["IMAGEIO_FFMPEG_EXE"] = "C:\\ffmpeg\\bin\\ffmpeg.exe"

🔧 Configuração
Variáveis Globais (em main.py)
python
CHANNEL = "parallelcuts"    # Seu canal
THEME = "pregacao"          # Tema dos vídeos
SCREEN_ORIENTATION = "MOBILE"  # "MOBILE" ou "DESKTOP"
Preparar Arquivos Necessários
powershell

# 1. Coloque vídeos de fundo na pasta videos/
#    Nomeie como: {tema}{numero}.mp4
#    Exemplo: pregacao001.mp4, pregacao002.mp4

# 2. Coloque logos em images/
#    Nomeie como: logo-canal-{canal}.jpg
#    Exemplo: logo-canal-parallelcuts.jpg

# 3. Para automação YouTube, capture screenshots:
#    - fav-youtube.png (ícone do YouTube)
#    - barra-url-youtube.png
#    - botao-lupa-youtube.png
#    - botao-criar-youtube.png
#    - etc...
📝 Personalização
Modificar Estilo dos Vídeos
Edite video_generator.py:

python
# Ajuste posição do logo
video = add_logo(video, logo_path, 
                 x_percent=0.45,    # Posição X (0-1)
                 y_percent=0.02,    # Posição Y (0-1)
                 size_multiplier=0.8, # Tamanho
                 opacity=0.7)       # Transparência

# Ajuste imagem de subscribe
video = add_image(video, "images/subscribe.png",
                  x=0.2, y=0.7,    # Posição
                  size_multiplier=0.8,
                  opacity=0.6)
Mudar Voz (Coqui-tts)
python
# Tem um arquivo em coqui-tts (que vem do outro repo separado https://github.com/ailtonandrade/hello-coqui-tts-service
é só baixar ele e por numa pasta próxima a desse projeto)
# O nome do arquivo é audio.wav
# Se trocar ele, a voz muda

Crie uma branch (git checkout -b feature/nova-feature)

Commit suas mudanças (git commit -m 'Add nova feature')

Push para a branch (git push origin feature/nova-feature)

Abra um Pull Request

📄 Licença
Este projeto está sob a licença MIT. Veja o arquivo LICENSE para detalhes.

⭐ Suporte
Se este projeto te ajudou, deixe uma ⭐ no GitHub!

Problemas? Abra uma issue no GitHub.

<div align="center">
Desenvolvido com ❤️ para criadores de conteúdo do YouTube
</div>
