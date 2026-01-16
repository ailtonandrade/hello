from kokoro import KPipeline
import soundfile as sf
import numpy as np
import os

class VoiceGenerator:
    def __init__(self, lang_code="p", voice="pm_santa", sample_rate=24000, 
                 speed=1.0, pitch=1.0, volume=1.0):
        self.lang_code = lang_code
        self.voice = voice
        self.sample_rate = sample_rate
        self.speed = max(0.5, min(2.0, speed))
        self.pitch = max(0.5, min(2.0, pitch))
        self.volume = max(0.0, min(2.0, volume))

    def generate_audio(self, text, output_file):
        """Gera áudio a partir do texto."""
        try:
            pipeline = KPipeline(lang_code=self.lang_code, repo_id='hexgrad/Kokoro-82M')
            generator = pipeline(text, voice=self.voice, speed=self.speed)
            
            audio_chunks = []
            for _, _, audio in generator:
                audio_chunks.append(audio)

            if not audio_chunks:
                return 0.0

            audio_data = np.concatenate(audio_chunks)
            
            # Ajustar pitch
            if self.pitch != 1.0:
                from scipy import signal
                new_length = int(len(audio_data) / self.pitch)
                audio_data = signal.resample(audio_data, new_length)
            
            # Ajustar volume
            if self.volume != 1.0:
                audio_data = audio_data * self.volume
            
            audio_data = np.clip(audio_data, -1.0, 1.0)
            
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            sf.write(output_file, audio_data, self.sample_rate)

            duration = len(audio_data) / self.sample_rate
            print(f"✅ Áudio: {duration:.2f}s")
            return duration
            
        except Exception as e:
            print(f"❌ Erro no áudio: {e}")
            
            # Fallback simples
            try:
                pipeline = KPipeline(lang_code=self.lang_code, repo_id='hexgrad/Kokoro-82M')
                generator = pipeline(text, voice=self.voice, speed=1.0)
                
                audio_chunks = []
                for _, _, audio in generator:
                    audio_chunks.append(audio)
                
                if audio_chunks:
                    audio_data = np.concatenate(audio_chunks)
                    os.makedirs(os.path.dirname(output_file), exist_ok=True)
                    sf.write(output_file, audio_data, self.sample_rate)
                    duration = len(audio_data) / self.sample_rate
                    print(f"✅ Áudio (fallback): {duration:.2f}s")
                    return duration
            except:
                pass
            
            return 0.0