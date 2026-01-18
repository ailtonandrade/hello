import os
import numpy as np
import soundfile as sf
from kokoro import KPipeline
from tts_wrapper import CoquiTTS


class VoiceGenerator:
    def __init__(
        self,
        lang_code="p",
        voice="pm_santa",
        sample_rate=24000,
        speed=1.0,
        pitch=1.0,
        volume=1.0,
        coqui_model="tts_models/multilingual/multi-dataset/xtts_v2",
        voice_file_path=None,
    ):
        self.lang_code = lang_code
        self.voice = voice
        self.sample_rate = sample_rate
        self.speed = speed
        self.pitch = pitch
        self.volume = volume
        self.coqui_model = coqui_model
        self.voice_file_path = voice_file_path

        self.coqui = CoquiTTS()

    def _generate_with_kokoro(self, text, output_file):
        pipeline = KPipeline(
            lang_code=self.lang_code,
            repo_id="hexgrad/Kokoro-82M",
        )

        generator = pipeline(text, voice=self.voice, speed=self.speed)

        audio = np.concatenate([chunk for _, _, chunk in generator])

        if self.pitch != 1.0:
            from scipy import signal
            audio = signal.resample(audio, int(len(audio) / self.pitch))

        audio *= self.volume
        audio = np.clip(audio, -1.0, 1.0)

        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        sf.write(output_file, audio, self.sample_rate)

        return len(audio) / self.sample_rate

    def generate_audio(self, text, output_file, prefer_coqui=True):
        if prefer_coqui:
            try:
                self.coqui.speak(
                    text=text,
                    output=output_file,
                    language="pt" if self.lang_code == "p" else "en",
                    model=self.coqui_model,
                    speaker_wav=self.voice_file_path,
                )
                return 1.0
            except Exception as e:
                print(f"⚠️ Coqui falhou → Kokoro: {e}")

        return self._generate_with_kokoro(text, output_file)
