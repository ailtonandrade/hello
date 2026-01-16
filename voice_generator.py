from kokoro import KPipeline
import soundfile as sf
import numpy as np

class VoiceGenerator:
    def __init__(self, lang_code="p", voice="pm_santa", sample_rate=24000, 
                 speed=1.0, pitch=1.0, volume=1.0):
        """
        Initialize VoiceGenerator with voice configuration.
        
        Args:
            lang_code (str): Language code ('p' for Portuguese)
            voice (str): Voice name (e.g., 'pm_santa', 'pf_santa', etc.)
            sample_rate (int): Audio sample rate in Hz
            speed (float): Speech speed multiplier (0.5-2.0, default 1.0)
            pitch (float): Voice pitch multiplier (0.5-2.0, default 1.0) 
            volume (float): Audio volume multiplier (0.0-2.0, default 1.0)
        """
        self.lang_code = lang_code
        self.voice = voice
        self.sample_rate = sample_rate
        self.speed = max(0.1, min(3.0, speed))  # Clamp between 0.1 and 3.0
        self.pitch = max(0.5, min(2.0, pitch))  # Clamp between 0.5 and 2.0
        self.volume = max(0.0, min(2.0, volume))  # Clamp between 0.0 and 2.0

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
            # Create pipeline with voice configuration
            pipeline = KPipeline(lang_code=self.lang_code)
            
            # Apply voice modifications using eSpeak options
            # Speed: -s (speed in words per minute, default ~160)
            # Pitch: -p (pitch adjustment)
            voice_options = f"{self.voice}"
            
            # Add speed modification (eSpeak uses -s for speed in wpm)
            if self.speed != 1.0:
                base_speed = 160  # Default eSpeak speed
                adjusted_speed = int(base_speed * self.speed)
                voice_options += f" -s {adjusted_speed}"
            
            # Add pitch modification (eSpeak uses -p for pitch)
            if self.pitch != 1.0:
                pitch_value = int(50 * self.pitch)  # Base pitch around 50
                voice_options += f" -p {pitch_value}"
            
            print(f"🎤 Gerando áudio com voz: {voice_options}")
            print(f"   📊 Configurações - Velocidade: {self.speed}x, Tom: {self.pitch}x, Volume: {self.volume}x")
            
            generator = pipeline(text, voice=voice_options)

            audio_chunks = []
            for _, _, audio in generator:
                audio_chunks.append(audio)

            if not audio_chunks:
                print("❌ Nenhum áudio gerado")
                return 0.0

            audio_data = np.concatenate(audio_chunks)
            
            # Apply volume adjustment
            if self.volume != 1.0:
                audio_data = audio_data * self.volume
            
            # Ensure audio data is in valid range
            audio_data = np.clip(audio_data, -1.0, 1.0)
            
            sf.write(output_file, audio_data, self.sample_rate)

            duration = len(audio_data) / self.sample_rate
            print(f"✅ Áudio gerado: {output_file} (Duração: {duration:.2f}s)")
            return duration
            
        except Exception as e:
            print(f"❌ Erro ao gerar áudio: {e}")
            return 0.0

    def set_voice_config(self, speed=None, pitch=None, volume=None):
        """
        Update voice configuration parameters.
        
        Args:
            speed (float, optional): Speech speed multiplier (0.1-3.0)
            pitch (float, optional): Voice pitch multiplier (0.5-2.0)
            volume (float, optional): Audio volume multiplier (0.0-2.0)
        """
        if speed is not None:
            self.speed = max(0.1, min(3.0, speed))
        if pitch is not None:
            self.pitch = max(0.5, min(2.0, pitch))
        if volume is not None:
            self.volume = max(0.0, min(2.0, volume))
        
        print(f"🎛️ Configuração de voz atualizada - Velocidade: {self.speed}x, Tom: {self.pitch}x, Volume: {self.volume}x")

    def get_available_voices(self):
        """
        Get list of available voices for the current language.
        
        Returns:
            list: List of available voice names
        """
        # Common Portuguese voices in Kokoro
        portuguese_voices = [
            "pm_santa",    # Male Santa
            "pf_santa",    # Female Santa
            "pm_arctic",   # Male Arctic
            "pf_arctic",   # Female Arctic
            "pm_bel",      # Male Bel
            "pf_bel",      # Female Bel
        ]
        
        return portuguese_voices

    def test_voice(self, text="Olá, esta é uma configuração de teste de voz.", output_file="test_voice.wav"):
        """
        Generate a test audio file with current voice configuration.
        
        Args:
            text (str): Test text to generate
            output_file (str): Output file path
        """
        print(f"🧪 Testando voz com configurações atuais...")
        duration = self.generate_audio(text, output_file)
        if duration > 0:
            print(f"✅ Teste concluído! Arquivo salvo: {output_file}")
        else:
            print("❌ Falha no teste de voz")
        return duration