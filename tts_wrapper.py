import subprocess
import re
import tempfile
import wave
import shutil
from pathlib import Path


class CoquiTTS:
    def __init__(
        self,
        model_name="tts_models/multilingual/multi-dataset/xtts_v2",
        project_path="../coqui-tts",
        max_chars_per_chunk=350,  # seguro pra PT-BR narrativo
    ):
        self.model_name = model_name
        self.project_path = Path(project_path).resolve()
        self.script_path = self.project_path / "run_tts.py"
        self.max_chars_per_chunk = max_chars_per_chunk

        if not self.script_path.exists():
            raise FileNotFoundError(
                f"run_tts.py não encontrado em {self.project_path}"
            )

    # ---------------------------
    # 🔪 Chunking seguro
    # ---------------------------
    def _split_text(self, text: str):
        sentences = re.split(r'(?<=[.!?])\s+', text.strip())
        chunks = []
        current = ""

        def force_split(long_text):
            """Divide texto longo em pedaços seguros."""
            return [
                long_text[i:i + self.max_chars_per_chunk]
                for i in range(0, len(long_text), self.max_chars_per_chunk)
            ]

        for s in sentences:
            s = s.strip()
            if not s:
                continue

            # 🔥 frase sozinha já é grande demais → split forçado
            if len(s) > self.max_chars_per_chunk:
                if current:
                    chunks.append(current)
                    current = ""

                chunks.extend(force_split(s))
                continue

            candidate = (current + " " + s).strip()
            if len(candidate) <= self.max_chars_per_chunk:
                current = candidate
            else:
                if current:
                    chunks.append(current)
                current = s

        if current:
            chunks.append(current)

        return chunks


    # ---------------------------
    # 🔊 Gera WAV único
    # ---------------------------
    def _speak_single(self, *, text, output, language, speaker_wav):
        output = Path(output)
        output.parent.mkdir(parents=True, exist_ok=True)

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
    # 🔗 Concatena WAVs
    # ---------------------------
    def _concat_wavs(self, wavs, output):
        with wave.open(str(wavs[0]), "rb") as w:
            params = w.getparams()
            frames = [w.readframes(w.getnframes())]

        for wav in wavs[1:]:
            with wave.open(str(wav), "rb") as w:
                frames.append(w.readframes(w.getnframes()))

        output = Path(output)
        output.parent.mkdir(parents=True, exist_ok=True)

        with wave.open(str(output), "wb") as out:
            out.setparams(params)
            for f in frames:
                out.writeframes(f)

    # ---------------------------
    # 🚀 API pública
    # ---------------------------
    def speak(self, *, text, output, language="pt", speaker_wav=None) -> float:
        chunks = self._split_text(text)

        # Texto pequeno
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
            shutil.rmtree(temp_dir, ignore_errors=True)

        return 1.0
