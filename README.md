
# Hello

Projeto de utilitários para processamento de áudio, geração de vídeos e integração com serviços (YouTube, Instagram, etc.). Contém scripts para síntese de voz, edição de vídeo e uma interface web simples.

## Descrição

Conjunto de ferramentas e exemplos usados para gerar vídeos a partir de texto, manipular áudio e automatizar publicações. Integra com bibliotecas como `moviepy`, `faster-whisper` (ou `whisper`) e utilitários locais para TTS.

## Requisitos

⚠️ A Hello usa Python 3.13.0 [vai rodar o principal , movuepy e post youtube]
⚠️ Stable Diffusion - Comfy usa Python 3.11.14 [vai gerar imagem/video localmente] (https://github.com/ailtonandrade/hello-sd-generator-service)
⚠️	Coqui TTS usa o Python 3.11.14 [vai gerar a narração] (https://github.com/ailtonandrade/hello-coqui-tts-service)

- Python 3.13 ou superior
- ffmpeg instalado no sistema (usado por `moviepy`)
- GPU com CUDA (opcional, depende de bibliotecas como `faster-whisper`)

## Instalação

1. Crie e ative um ambiente virtual (recomendado):

```bash
python -m venv .venv
.\.venv\Scripts\activate
```

2. Instale as dependências:

```bash
pip install -r requirements.txt
```

3. Se desejar usar recursos de TTS locais, veja o diretório `coqui-tts` e instale-o conforme necessário.

## Uso

- Executar o script principal (exemplo):

```bash
python main.py
```

- Interface web (se aplicável):

```bash
python app.py
```

- Gerar vídeo usando o helper `run_video.py` (ex.: ComfyUI local):

```bash
python run_video.py
```

Parâmetros e scripts principais:

- `main.py`: ponto de entrada de exemplo.
- `app.py`: possível interface web.
- `run_video.py`: fluxo para gerar frames usando ComfyUI.
- `video_generator.py`, `video_editor.py`: helpers para montagem e edição de vídeo.
- `tts_wrapper.py`, `voice_generator.py`: utilitários de síntese de voz.

## Observações

- Alguns pacotes exigem bibliotecas de sistema (ex.: `ffmpeg`).
- O arquivo `pyproject.toml` contém a lista canônica de dependências; `requirements.txt` foi gerado a partir dele.

## Estrutura

- `audios/`, `videos/`, `images/`, `output/`: pastas para artefatos gerados.
- `templates/`: modelos HTML usados pela interface.

## Licença

Consulte o arquivo `LICENSE` no repositório.
