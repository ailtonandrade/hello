import json
import requests
import uuid
import time
import random
import shutil
import subprocess
from pathlib import Path
import math


# =========================
# CONFIGURAÇÕES
# =========================

COMFY_URL = "http://127.0.0.1:8188"
WORKFLOW_TEXT2IMG = Path("../stable-difusion-image/workflow_text2img.json")
WORKFLOW_IMG2IMG = Path("../stable-difusion-image/workflow_img2img.json")

FRAMES_DIR = Path("../stable-difusion-image/frames")
COMFY_INPUT = Path("../stable-difusion-image/ComfyUI/input")
COMFY_OUTPUT = Path("../stable-difusion-image/ComfyUI/output")

# resolução base dos frames (SD / ComfyUI)
FRAME_WIDTH = 540
FRAME_HEIGHT = 920

# resolução do vídeo final
VIDEO_WIDTH = 540
VIDEO_HEIGHT = 920  # use 1920 pra Shorts / 1080 pra horizontal

NUM_FRAMES = 12
FPS_INPUT = 2
FINAL_FPS = 12
FINAL_TIME = 5

BASE_SEED = random.randint(0, 2**31 - 1)

# 🔒 ANCHOR FRAME (anti-derretimento)
ANCHOR_EVERY = 3  # a cada N frames, volta pro frame âncora


class ComfyVideoGenerator:
    """Classe responsável por gerar conteúdo visual via ComfyUI e montar vídeo.

    Método principal: `get_video_content_by_comfy(theme, prompt_positive=None, prompt_negative=None)`
    """

    def __init__(self, comfy_url: str = COMFY_URL):
        self.comfy_url = comfy_url
        FRAMES_DIR.mkdir(exist_ok=True)
        COMFY_INPUT.mkdir(exist_ok=True)

    def _run_workflow(self, workflow_path: Path, image_input: str | None = None, prompt_positive: str | None = None, prompt_negative: str | None = None):
        start = time.perf_counter()

        with open(workflow_path, "r", encoding="utf-8") as f:
            wf = json.load(f)

        for node in wf["prompt"].values():
            if node["class_type"] == "EmptyLatentImage":
                node["inputs"]["width"] = FRAME_WIDTH
                node["inputs"]["height"] = FRAME_HEIGHT

            if node["class_type"] == "CLIPTextEncode":
                text = node["inputs"].get("text", "")
                if prompt_positive is not None or prompt_negative is not None:
                    node["inputs"]["text"] = prompt_negative if "NEGATIVE" in text.upper() and prompt_negative else (prompt_positive or text)

            if node["class_type"] == "KSampler":
                node["inputs"]["seed"] = BASE_SEED + random.randint(-5, 5)

            if image_input and node["class_type"] == "LoadImage":
                node["inputs"]["image"] = image_input

        r = requests.post(
            f"{self.comfy_url}/prompt",
            json={"prompt": wf["prompt"], "client_id": str(uuid.uuid4())},
            timeout=120,
        )

        if r.status_code != 200:
            print("❌ ERRO DO COMFYUI:")
            print(r.text)
            raise RuntimeError("Workflow rejeitado")

        prompt_id = r.json()["prompt_id"]

        while True:
            if requests.get(f"{self.comfy_url}/history/{prompt_id}").json():
                break
            time.sleep(0.5)

        files = list((COMFY_OUTPUT / "hybrid").glob("*.png"))
        if not files:
            raise RuntimeError("Nenhuma imagem encontrada")

        elapsed = time.perf_counter() - start
        return max(files, key=lambda p: p.stat().st_mtime), elapsed

    def get_video_content_by_comfy(self, theme: str, prompt_positive_comfy: str = "", prompt_negative_comfy: str = "", audio_duration: float | None = None) -> list[Path]:
        videos = []

        # calcular quantos vídeos gerar
        count = 1
        if audio_duration is not None and audio_duration > 0:
            count = max(1, math.ceil(audio_duration / FINAL_TIME))

        for vid_index in range(count):
            total_start = time.perf_counter()
            frame_times = []

            # FRAME 0 (TEXT2IMG)
            print("🎬 Gerando frame 0 (text2img)...", end=" ")
            frame0, t0 = self._run_workflow(WORKFLOW_TEXT2IMG, prompt_positive=prompt_positive_comfy, prompt_negative=prompt_negative_comfy)
            print(f"⏱️ {t0:.2f}s")

            shutil.copy(frame0, FRAMES_DIR / "000.png")
            frame_times.append(("frame_000", t0))

            current_frame = FRAMES_DIR / "000.png"
            anchor_frame = current_frame

            # IMG2IMG SEQUENCIAL
            for i in range(1, NUM_FRAMES):
                base_frame = anchor_frame if i % ANCHOR_EVERY == 0 else current_frame

                print(f"🖼️ Gerando frame {i} (img2img)...", end=" ")
                shutil.copy(base_frame, COMFY_INPUT / "input.png")

                new_frame, ti = self._run_workflow(WORKFLOW_IMG2IMG, image_input="input.png", prompt_positive=prompt_positive_comfy, prompt_negative=prompt_negative_comfy)
                print(f"⏱️ {ti:.2f}s")

                dst = FRAMES_DIR / f"{i:03d}.png"
                shutil.copy(new_frame, dst)
                frame_times.append((f"frame_{i:03d}", ti))
                current_frame = dst

            print("\n✅ Frames finalizados\n")

            # Montar vídeo
            random_number = random.randint(0, 9999)
            video_final = Path(f"./{theme}_{random_number}.mp4")

            print("🎥 Criando vídeo final...")
            video_start = time.perf_counter()

            subprocess.run([
                "ffmpeg",
                "-y",
                "-framerate",
                str(FPS_INPUT),
                "-i",
                str(FRAMES_DIR / "%03d.png"),
                "-vf",
                f"scale={VIDEO_WIDTH}:{VIDEO_HEIGHT}:force_original_aspect_ratio=decrease,"
                f"pad={VIDEO_WIDTH}:{VIDEO_HEIGHT}:(ow-iw)/2:(oh-ih)/2,"
                f"minterpolate=fps={FINAL_FPS}",
                "-t",
                str(FINAL_TIME),
                "-c:v",
                "libx264",
                "-pix_fmt",
                "yuv420p",
                "-movflags",
                "+faststart",
                str(video_final),
            ], check=True)

            video_elapsed = time.perf_counter() - video_start
            total_elapsed = time.perf_counter() - total_start

            print("\n🧹 Limpando frames...")
            for f in FRAMES_DIR.glob("*"):
                try:
                    f.unlink()
                except Exception:
                    pass

            print("\n⏱️ TEMPO POR FRAME:")
            for name, t in frame_times:
                print(f"  {name}: {t:.2f}s")

            print(f"\n🎥 Tempo render vídeo: {video_elapsed:.2f}s")
            print(f"⏱️ TEMPO TOTAL: {total_elapsed:.2f}s")

            print("\n🎉 VÍDEO FINAL PRONTO:")
            print(video_final.resolve())

            videos.append(video_final)

        return videos
