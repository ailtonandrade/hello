import subprocess
from pathlib import Path


class CoquiTTS:
    def __init__(self, project_path="../coqui-tts"):
        self.project_path = Path(project_path).resolve()
        self.script_path = self.project_path / "run_tts.py"

        if not self.script_path.exists():
            raise FileNotFoundError("run_tts.py não encontrado no coqui-tts")

    def speak(
        self,
        *,
        text: str,
        output: str,
        language: str = "pt",
        speaker_wav: str | None = None,
    ) -> float:

        # 🔥 MODELOS VALIDOS (JSON REAL)
        if speaker_wav:
            model = "tts_models/multilingual/multi-dataset/xtts_v2"
        else:
            if language == "pt":
                model = "tts_models/pt/cv/vits"
            else:
                model = "tts_models/en/ljspeech/vits"

        cmd = [
            "uv", "run",
            "--project", str(self.project_path),
            "python", str(self.script_path),
            "--text", text,
            "--out", output,
            "--lang", language,
            "--model", model,
        ]

        if speaker_wav:
            cmd += ["--speaker-wav", speaker_wav]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            raise RuntimeError(result.stderr.strip())

        return 1.0
