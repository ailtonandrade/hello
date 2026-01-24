Otom - AI Media Generator

Projeto de utilitários para processamento de áudio, geração de vídeos e integração com serviços como YouTube e Instagram.
Inclui scripts para síntese de voz (TTS), geração de imagens/vídeos e uma interface web simples.

==================================================

DESCRIÇÃO

Conjunto de ferramentas usadas para gerar vídeos a partir de texto, manipular áudio e automatizar publicações.
Integra bibliotecas como moviepy, faster-whisper (ou whisper) e serviços locais de TTS e Stable Diffusion.

O projeto é dividido em serviços independentes, cada um com seu ambiente Python específico.

==================================================

REQUISITOS E AMBIENTES

OTOM (CORE)
- Python 3.13.0
- Responsável pelo fluxo principal, MoviePy e upload (YouTube)

STABLE DIFFUSION (COMFYUI)
- Python 3.11.14
- Geração local de imagens e vídeos
- Repositório:
  https://github.com/ailtonandrade/hello-sd-generator-service

COQUI TTS
- Python 3.11.14
- Geração de narração por voz
- Repositório:
  https://github.com/ailtonandrade/hello-coqui-tts-service

OUTROS REQUISITOS
- ffmpeg instalado no sistema (usado pelo moviepy)
- GPU com CUDA (opcional, depende de bibliotecas como faster-whisper)

==================================================

GERENCIAMENTO DE DEPENDÊNCIAS

O projeto utiliza UV para gerenciamento de ambientes e dependências.

- pyproject.toml contém a definição canônica das dependências
- requirements.txt é derivado dele

==================================================

INSTALAÇÃO

1) Criar ambiente virtual:

uv venv
source .venv/bin/activate
(no Windows, use o ativador equivalente)

2) Instalar dependências:

uv pip install -r requirements.txt

==================================================

USO

========================================================================

Otom AI Media Generator (/hello) - Python 3.13
Escolher entre Python ou Interface Web

Padrão:
> cd .\ pasta do main.py
> python --version (verificar se versão é 3.13.0)
> .\.venv\Scripts\activate.ps1

Aqui só escolher um dos dois:
    Python:
    > python main.py

    Interface web:
    > python web_interface.py

Espere ate aparecer
...
> Running on http://127.0.0.1:5000

========================================================================

Otom AI Media Generator (/hello) - Python 3.10.19
(Eg.: stable-difusion-imag\ComfyUI\main.py)

> cd path-to\stable-difusion-image\ComfyUI
> .\.venv\Scripts\activate.ps1
> python --version (verificar se versão é 3.10.19)
> python main.py --directml

Espere ate aparecer
...
> Starting server
> To see the GUI go to: http://127.0.0.1:xxxx

Abra no seu navegador a URL

==================================================

SCRIPTS PRINCIPAIS

main.py
- Ponto de entrada do fluxo principal

app.py
- Interface web (opcional)

run_video.py
- Geração de frames e vídeos via ComfyUI

video_generator.py, video_editor.py
- Helpers para montagem e edição de vídeo

tts_wrapper.py, voice_generator.py
- Utilitários de síntese de voz

==================================================

ESTRUTURA DO PROJETO

songs/, videos/, images/, output/
- Artefatos gerados

templates/
- Templates HTML usados pela interface web

==================================================

OBSERVAÇÕES

- Alguns pacotes exigem dependências de sistema (ex.: ffmpeg)
- Cada serviço (core, SD, TTS) roda em ambiente isolado
- Projeto voltado para uso local e automação de pipelines

==================================================

LICENÇA

Consulte o arquivo LICENSE no repositório.
