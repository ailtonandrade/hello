import subprocess
from pathlib import Path


class CoquiTTS:
    def __init__(
        self,
        model_name="tts_models/multilingual/multi-dataset/xtts_v2",
        project_path="../coqui-tts",
    ):  

        self.model_name = model_name
        self.project_path = Path(project_path).resolve()
        self.script_path = self.project_path / "run_tts.py"

        if not self.script_path.exists():
            raise FileNotFoundError(
                f"run_tts.py não encontrado em {self.project_path}"
            )

    # ---------------------------
    # 🔊 Gera WAV único (texto inteiro)
    # ---------------------------
    def _speak_single(self, *, text, output, language, speaker_wav):
        output = Path(output)
        output.parent.mkdir(parents=True, exist_ok=True)
        
        # low profile
        self.model_name = "tts_models/multilingual/multi-dataset/your_tts"
        language = "pt-br"
        
        cmd = [
            "uv", "run",
            "--project", str(self.project_path),
            "tts",
            "--model_name", self.model_name,
            "--text", text,
            "--language_idx", language,
            "--out_path", str(output),
        ]

        if speaker_wav:
            cmd += ["--speaker_wav", str(speaker_wav)]

        result = subprocess.run(
            cmd,
            capture_output=True
        )

        stdout = result.stdout.decode("utf-8", errors="replace")
        stderr = result.stderr.decode("utf-8", errors="replace")

        if result.returncode != 0:
            raise RuntimeError(
                f"XTTS falhou:\n{stderr or stdout}"
            )

        if not output.exists():
            raise RuntimeError(
                f"XTTS NÃO GEROU O WAV:\n{output}\n\n{stderr or stdout}"
            )

    # ---------------------------
    # 🚀 API pública
    # ---------------------------
    def speak(self, *, text, output, language="pt", speaker_wav=None) -> float:
        """
        Gera áudio TTS em WAV a partir do texto completo.
        Retorna 1.0 apenas como placeholder de compatibilidade.
        """
        if not text or not text.strip():
            raise ValueError("Texto vazio para TTS")

        self._speak_single(
            text=text.strip(),
            output=output,
            language=language,
            speaker_wav=speaker_wav,
        )

        return 1.0
