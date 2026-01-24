import os
import subprocess
from tts_wrapper import CoquiTTS


class VoiceGenerator:
    def __init__(
        self,
        sample_rate=16000,
        speed=1.05,
        pitch=0.95,
        volume=1.15,
        radio_fx=True,
        model_name="tts_models/multilingual/multi-dataset/xtts_v2",
        voice_file_path=None,
        language="pt",
    ):
        self.sample_rate = sample_rate
        self.speed = speed
        self.pitch = pitch
        self.volume = volume
        self.radio_fx = radio_fx
        self.model_name = model_name
        self.voice_file_path = voice_file_path
        self.language = language

        self.coqui = CoquiTTS(model_name=self.model_name)

    def generate_audio(self, text: str, output_file: str) -> float:
        os.makedirs(os.path.dirname(output_file), exist_ok=True)

        # 🎙️ 1. gera áudio base
        self.coqui.speak(
            text=text,
            output=output_file,
            language=self.language,
            speaker_wav=self.voice_file_path,
        )
    
        
        # 🎛️ 2. FFmpeg FX
        temp_file = output_file.replace(".wav", "_fx.wav")
        rate = int(self.sample_rate * self.pitch)

        radio_chain = (
            "highpass=f=180,"
            "lowpass=f=6000,"
            "acompressor=threshold=-24dB:ratio=4:attack=5:release=80,"
            "equalizer=f=250:t=q:w=1:g=-4,"
            "equalizer=f=4000:t=q:w=1:g=6,"
            "alimiter=limit=0.95"
        )

        filter_chain = f"asetrate={rate},atempo={self.speed}"

        if self.radio_fx:
            filter_chain += f",{radio_chain}"

        filter_chain += f",volume={self.volume}"

        cmd = [
            "ffmpeg", "-y",
            "-i", output_file,
            "-filter:a", filter_chain,
            temp_file
        ]

        subprocess.run(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True
        )

        os.replace(temp_file, output_file)

        # ⏱️ duração estimada
        word_count = max(len(text.split()), 1)
        return word_count / 2.2
