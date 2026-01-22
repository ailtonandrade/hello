import json
import requests
import uuid
import time
import random
import shutil
import subprocess
from pathlib import Path


# =========================
# CONFIGURAÇÕES
# =========================

COMFY_URL = "http://127.0.0.1:8188"
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
FINAL_TIME = 5
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
    def _run_workflow(self, workflow_path, prompt_positive, prompt_negative):
        with open(workflow_path, "r", encoding="utf-8") as f:
            wf = json.load(f)

        for node in wf["prompt"].values():

            if node["class_type"] == "EmptyLatentImage":
                node["inputs"]["width"] = FRAME_WIDTH
                node["inputs"]["height"] = FRAME_HEIGHT

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
    def create_video_from_frame(self, frame_path, theme):

        overlay_files = list(OVERLAYS_DIR.glob("*.mp4"))
        if not overlay_files:
            raise RuntimeError("Nenhum overlay encontrado em ./overlays")

        overlay = random.choice(overlay_files)
        output_video = VIDEOS_DIR / f"{theme}_{random.randint(0,9999)}.mp4"

        filter_complex = (
            f"[0:v]scale={VIDEO_WIDTH}:{VIDEO_HEIGHT}:force_original_aspect_ratio=decrease,"
            f"pad={VIDEO_WIDTH}:{VIDEO_HEIGHT}:(ow-iw)/2:(oh-ih)/2,"
            f"format=rgb24,"
            f"fade=t=in:st=0:d={FADE_TIME},"
            f"fade=t=out:st={FINAL_TIME-FADE_TIME}:d={FADE_TIME}"
            f"[base];"
            f"[1:v]scale={VIDEO_WIDTH}:{VIDEO_HEIGHT},"
            f"format=rgb24,"
            f"colorlevels=rimax=1:gimax=1:bimax=1"
            f"[ov];"
            f"[base][ov]blend=all_mode=screen:all_opacity=1"
        )

        subprocess.run([
            "ffmpeg",
            "-y",
            "-loop", "1",
            "-i", str(frame_path),
            "-stream_loop", "-1",
            "-i", str(overlay),
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
    def generate(self, theme, prompt_positive, prompt_negative=""):

        print("🎬 Gerando frame único...")
        frame = self._run_workflow(
            WORKFLOW_TEXT2IMG,
            prompt_positive,
            prompt_negative
        )

        final_frame = FRAMES_DIR / "frame.png"
        shutil.copy(frame, final_frame)

        print("🎥 Gerando vídeo com overlay...")
        video = self.create_video_from_frame(final_frame, theme)

        shutil.rmtree(FRAMES_DIR, ignore_errors=True)
        FRAMES_DIR.mkdir(exist_ok=True)

        return video
