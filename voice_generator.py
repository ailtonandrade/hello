from kokoro import KPipeline
import soundfile as sf
import numpy as np

class VoiceGenerator:
    def __init__(self, lang_code="p", voice="pm_santa", sample_rate=24000):
        self.lang_code = lang_code
        self.voice = voice
        self.sample_rate = sample_rate

    def generate_audio(self, text, output_file):
        """
        Generate audio for the given text and save it to the specified file.

        Args:
            text (str): The text to convert to speech.
            output_file (str): Path to save the generated audio file.

        Returns:
            float: Duration of the generated audio in seconds.
        """
        try:
            pipeline = KPipeline(lang_code=self.lang_code)
            generator = pipeline(text, voice=self.voice)

            audio_chunks = []
            for _, _, audio in generator:
                audio_chunks.append(audio)

            audio_data = np.concatenate(audio_chunks)
            sf.write(output_file, audio_data, self.sample_rate)

            duration = len(audio_data) / self.sample_rate
            print(f"Audio generated: {output_file} (Duration: {duration:.2f} seconds)")
            return duration
        except Exception as e:
            print(f"Error generating audio: {e}")
            return 0.0