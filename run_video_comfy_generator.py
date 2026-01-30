import json
import requests
import uuid
import time
import random
import shutil
import subprocess
from pathlib import Path
from config import COMFY_URL


# =========================
# CONFIGURAÇÕES
# =========================

WORKFLOW_TEXT2IMG = Path("../stable-difusion-image/workflow_text2img.json")

COMFY_INPUT = Path("../stable-difusion-image/ComfyUI/input")
COMFY_OUTPUT = Path("../stable-difusion-image/ComfyUI/output")

FRAMES_DIR = Path("./frames")
OVERLAYS_DIR = Path("./overlays")
VIDEOS_DIR = Path("./videos")

FRAME_WIDTH = 540
FRAME_HEIGHT = 920

VIDEO_WIDTH = 540
VIDEO_HEIGHT = 920
FINAL_FPS = 12
FINAL_TIME = 5 if VIDEO_HEIGHT > VIDEO_WIDTH else 10
FADE_TIME = 0.3

BASE_SEED = random.randint(0, 2**31 - 1)


class ComfySingleFrameVideoGenerator:

    def __init__(self, comfy_url: str = COMFY_URL):
        self.comfy_url = comfy_url
        FRAMES_DIR.mkdir(exist_ok=True)
        COMFY_INPUT.mkdir(exist_ok=True)
        OVERLAYS_DIR.mkdir(exist_ok=True)
        VIDEOS_DIR.mkdir(exist_ok=True)

    # -------------------------
    # 🧠 ComfyUI text2img
    # -------------------------
    def _run_workflow(self, workflow_path, prompt_positive, prompt_negative, screen_orientation="MOBILE"):

        # start from module-level defaults and override for DESKTOP if needed
        frame_width = FRAME_WIDTH
        frame_height = FRAME_HEIGHT
        video_width = VIDEO_WIDTH
        video_height = VIDEO_HEIGHT

        if screen_orientation.upper() == "DESKTOP":
            frame_height = 540
            frame_width = 920
            video_width = 920
            video_height = 540

        with open(workflow_path, "r", encoding="utf-8") as f:
            wf = json.load(f)

        for node in wf["prompt"].values():

            if node["class_type"] == "EmptyLatentImage":
                node["inputs"]["width"] = frame_width
                node["inputs"]["height"] = frame_height

            if node["class_type"] == "CLIPTextEncode":
                text = node["inputs"].get("text", "")
                if prompt_positive or prompt_negative:
                    node["inputs"]["text"] = (
                        prompt_negative if "NEGATIVE" in text.upper() and prompt_negative
                        else (prompt_positive or text)
                    )

            if node["class_type"] == "KSampler":
                node["inputs"]["seed"] = random.randint(0, 2**31 - 1)

        r = requests.post(
            f"{self.comfy_url}/prompt",
            json={"prompt": wf["prompt"], "client_id": str(uuid.uuid4())},
            timeout=120,
        )

        if r.status_code != 200:
            raise RuntimeError(r.text)

        prompt_id = r.json()["prompt_id"]

        while True:
            if requests.get(f"{self.comfy_url}/history/{prompt_id}").json():
                break
            time.sleep(0.4)

        images = list((COMFY_OUTPUT / "hybrid").glob("*.png"))
        if not images:
            raise RuntimeError("Nenhuma imagem gerada")

        return max(images, key=lambda p: p.stat().st_mtime)

    # -------------------------
    # 🎥 Frame → vídeo 5s
    # -------------------------
    def create_video_from_frame(self, frame_path, theme, screen_orientation="MOBILE"):
        import random
        # start from module-level defaults and override for DESKTOP if needed
        frame_width = FRAME_WIDTH
        frame_height = FRAME_HEIGHT
        video_width = VIDEO_WIDTH
        video_height = VIDEO_HEIGHT

        if screen_orientation.upper() == "DESKTOP":
            frame_height = 540
            frame_width = 920
            video_width = 920
            video_height = 540

        output_video = VIDEOS_DIR / f"{theme}_{random.randint(0,9999)}.mp4"

        # 🎛️ CONTROLES DE ZOOM (AJUSTE AQUI)
        zoom_start = 1.00
        zoom_end   = 1.05   # ex: 1.02 bem sutil | 1.06 mais cinematográfico

        zoom_min = 1.00
        zoom_max = random.choice([1.03, 1.04, 1.05])  # variação sutil

        # decide direção
        zoom_in = random.choice([True, False])

        if zoom_in:
            zoom_start = zoom_min
            zoom_end = zoom_max
        else:
            zoom_start = zoom_max
            zoom_end = zoom_min
        
        filter_complex = (
            f"[0:v]"
            f"scale={video_width}:{video_height}:force_original_aspect_ratio=decrease,"
            f"pad={video_width}:{video_height}:(ow-iw)/2:(oh-ih)/2,"
            f"zoompan="
                f"z='{zoom_start}+({zoom_end}-{zoom_start})*on/({FINAL_TIME*FINAL_FPS}-1)':"
                f"x='iw/2-(iw/zoom/2)':"
                f"y='ih/2-(ih/zoom/2)':"
                f"d=1,"
            f"scale={video_width}:{video_height},"
            f"format=gbrp,"
            f"fade=t=in:st=0:d={FADE_TIME},"
            f"fade=t=out:st={FINAL_TIME-FADE_TIME}:d={FADE_TIME}"
        )

        subprocess.run([
            "ffmpeg",
            "-y",
            "-loop", "1",
            "-i", str(frame_path),
            "-filter_complex", filter_complex,
            "-t", str(FINAL_TIME),
            "-r", str(FINAL_FPS),
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-movflags", "+faststart",
            str(output_video)
        ], check=True)

        return output_video


    # -------------------------
    # 🚀 API pública
    # -------------------------
    def generate(self, theme, audio_duration, prompt_positive, prompt_negative="", cancel_event=None, screen_orientation="MOBILE"):
        total_generated_time = 0
        iteration = 0

        while total_generated_time < audio_duration:
            # checa cancelamento pedido
            if cancel_event is not None and getattr(cancel_event, 'is_set', lambda: False)():
                print("⚠️ Geração interrompida pelo usuário")
                return None
            iteration += 1
            print(f"🎬 Gerando frame #{iteration} (tempo coberto: {total_generated_time:.2f}s / {audio_duration:.2f}s)")

            frame = self._run_workflow(
                WORKFLOW_TEXT2IMG,
                prompt_positive,
                prompt_negative,
                screen_orientation=screen_orientation
            )

            final_frame = FRAMES_DIR / f"frame_{iteration:03d}.png"
            shutil.copy(frame, final_frame)

            print("🎥 Gerando vídeo com overlay...")
            video = self.create_video_from_frame(
                final_frame,
                theme,
                screen_orientation=screen_orientation
            )

            # checa cancelamento após criação do vídeo
            if cancel_event is not None and getattr(cancel_event, 'is_set', lambda: False)():
                print("⚠️ Geração interrompida pelo usuário (após criação de vídeo)")
                return None

            total_generated_time += FINAL_TIME

        print(f"✅ Geração concluída. Tempo total gerado: {total_generated_time:.2f}s")

        shutil.rmtree(FRAMES_DIR, ignore_errors=True)
        FRAMES_DIR.mkdir(exist_ok=True)
        return video