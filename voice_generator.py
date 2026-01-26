import os
import subprocess
import wave
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
        try:
            self.coqui.speak(
                text=text,
                output=output_file,
                language=self.language,
                speaker_wav=self.voice_file_path,
            )
        except Exception as e:
            # Ensure failures are visible and return 0 so caller can handle
            print(f"[VoiceGenerator] Erro ao gerar TTS: {e}")
            return 0.0
    
        
        # 🎛️ 2. FFmpeg FX
        temp_file = output_file.replace(".wav", "_fx.wav")

        # Detect input WAV sample rate to avoid wrong resampling when
        # Coqui/XTTS outputs at a different rate than `self.sample_rate`.
        try:
            with wave.open(output_file, "rb") as wf:
                input_rate = wf.getframerate()
        except Exception:
            input_rate = self.sample_rate

        new_rate = int(input_rate * self.pitch)

        radio_chain = (
            "highpass=f=180,"
            "lowpass=f=6000,"
            "acompressor=threshold=-24dB:ratio=4:attack=5:release=80,"
            "equalizer=f=250:t=q:w=1:g=-4,"
            "equalizer=f=4000:t=q:w=1:g=6,"
            "alimiter=limit=0.95"
        )

        # Ajuste de pitch: alteramos a taxa de amostragem temporariamente
        # e em seguida resampleamos de volta para evitar pitch/tempo incorreto.
        # `asetrate` altera o pitch; `aresample` devolve à taxa original.
        filter_chain = f"asetrate={new_rate},aresample={input_rate},atempo={self.speed}"

        # DEBUG: mostrar parâmetros do processamento (remover/ajustar conforme desejado)
        print(f"[VoiceGenerator] input_rate={input_rate} new_rate={new_rate} pitch={self.pitch} speed={self.speed}")

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
