import subprocess
import re
import tempfile
import wave
from pathlib import Path


class CoquiTTS:
    def __init__(
        self,
        model_name="tts_models/multilingual/multi-dataset/xtts_v2",
        project_path="../coqui-tts",
        max_chars_per_chunk=650,  # ~300 tokens PT-BR
    ):
        self.model_name = model_name
        self.project_path = Path(project_path).resolve()
        self.script_path = self.project_path / "run_tts.py"
        self.max_chars_per_chunk = max_chars_per_chunk

        if not self.script_path.exists():
            raise FileNotFoundError("run_tts.py não encontrado no coqui-tts")

    # ---------------------------
    # 🔪 Chunking seguro
    # ---------------------------
    def _split_text(self, text: str):
        sentences = re.split(r'(?<=[.!?])\s+', text.strip())
        chunks = []
        current = ""

        for s in sentences:
            if len(current) + len(s) <= self.max_chars_per_chunk:
                current += " " + s
            else:
                chunks.append(current.strip())
                current = s

        if current.strip():
            chunks.append(current.strip())

        return chunks

    # ---------------------------
    # 🔊 Gera WAV único (interno)
    # ---------------------------
    def _speak_single(self, *, text, output, language, speaker_wav):
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

        result = subprocess.run(cmd, capture_output=True)

        stderr = result.stderr.decode("utf-8", errors="replace")

        if result.returncode != 0:
            raise RuntimeError(stderr.strip())

    # ---------------------------
    # 🔗 Concatena WAVs
    # ---------------------------
    def _concat_wavs(self, wavs, output):
        with wave.open(str(wavs[0]), "rb") as w:
            params = w.getparams()
            frames = [w.readframes(w.getnframes())]

        for wav in wavs[1:]:
            with wave.open(str(wav), "rb") as w:
                frames.append(w.readframes(w.getnframes()))

        with wave.open(str(output), "wb") as out:
            out.setparams(params)
            for f in frames:
                out.writeframes(f)

    # ---------------------------
    # 🚀 API pública
    # ---------------------------
    def speak(self, *, text, output, language="pt", speaker_wav=None) -> float:
        chunks = self._split_text(text)

        # Texto pequeno → direto
        if len(chunks) == 1:
            self._speak_single(
                text=chunks[0],
                output=output,
                language=language,
                speaker_wav=speaker_wav,
            )
            return 1.0

        # Texto grande → chunk + concat
        temp_dir = Path(tempfile.mkdtemp(prefix="coqui_chunks_"))
        wavs = []

        try:
            for i, chunk in enumerate(chunks):
                wav_path = temp_dir / f"part_{i:03d}.wav"
                self._speak_single(
                    text=chunk,
                    output=wav_path,
                    language=language,
                    speaker_wav=speaker_wav,
                )
                wavs.append(wav_path)

            self._concat_wavs(wavs, Path(output))

        finally:
            # limpeza opcional (comenta se quiser debug)
            for f in wavs:
                f.unlink(missing_ok=True)
            temp_dir.rmdir()

        return 1.0
