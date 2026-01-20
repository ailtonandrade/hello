import os
from tts_wrapper import CoquiTTS


class VoiceGenerator:
    def __init__(
        self,
        sample_rate=24000,
        speed=1.1,
        pitch=0.9,
        volume=1.2,
        coqui_model="tts_models/multilingual/multi-dataset/xtts_v2",
        voice_file_path=None,
        language="pt",
    ):
        self.sample_rate = sample_rate
        self.speed = speed
        self.pitch = pitch
        self.volume = volume
        self.coqui_model = coqui_model
        self.voice_file_path = voice_file_path
        self.language = language

        self.coqui = CoquiTTS(model_name=self.coqui_model)

    def generate_audio(self, text: str, output_file: str) -> float:
        """
        Gera áudio usando Coqui XTTS-v2.
        Retorna duração aproximada em segundos.
        """

        os.makedirs(os.path.dirname(output_file), exist_ok=True)

        self.coqui.speak(
            text=text,
            output=output_file,
            language=self.language,
            speaker_wav=self.voice_file_path,
            speed=self.speed,
            volume=self.volume,
            pitch=self.pitch,
        )

        # duração aproximada (XTTS não retorna isso nativamente)
        word_count = max(len(text.split()), 1)
        estimated_duration = word_count / 2.2  # fala natural PT-BR

        return estimated_duration
