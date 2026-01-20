import subprocess
from pathlib import Path


class CoquiTTS:
    def __init__(self, model_name="tts_models/multilingual/multi-dataset/xtts_v2", project_path="../coqui-tts"):
        self.model_name = model_name
        self.project_path = Path(project_path).resolve()
        self.script_path = self.project_path / "run_tts.py"

        if not self.script_path.exists():
            raise FileNotFoundError("run_tts.py não encontrado no coqui-tts")

    def speak(self, *, text, output, language = "pt", speaker_wav=None) -> float:
        # uv run tts --model_name tts_models/multilingual/multi-dataset/xtts_v2 --text "Olá! Isso é um teste em português 
        # brasileiro, usando o modelo XTTS versão dois." --language_idx pt --speaker_wav audio.wav --out_path voz_xtts_ptbr.wav

        # 🔥 MODELOS VALIDOS (JSON REAL)
        model = self.model_name

        cmd = [
            "uv", "run",
            "--project", str(self.project_path),
            "tts",
            "--model_name", model,
            "--text", text,
            "--language_idx", language,   # ex: "pt"
            "--out_path", output,
        ]

        if speaker_wav:
            cmd += ["--speaker_wav", speaker_wav]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            raise RuntimeError(result.stderr.strip())

        return 1.0
