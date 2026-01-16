from kokoro import KPipeline
import soundfile as sf
import numpy as np
import os

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
        self.speed = max(0.5, min(2.0, speed))  # Clamp entre 0.5 e 2.0
        self.pitch = max(0.5, min(2.0, pitch))  # Clamp entre 0.5 e 2.0
        self.volume = max(0.0, min(2.0, volume))  # Clamp entre 0.0 e 2.0

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
            print(f"🎤 Gerando áudio com voz: {self.voice}")
            print(f"   📊 Configurações - Velocidade: {self.speed}x, Tom: {self.pitch}x, Volume: {self.volume}x")
            
            # CORREÇÃO: Usar apenas o nome da voz, sem parâmetros do eSpeak
            # O Kokoro tem seu próprio sistema de parâmetros
            pipeline = KPipeline(lang_code=self.lang_code)
            
            # Usar os parâmetros do Kokoro corretamente
            # Kokoro usa: text, voice=voice_name, speed=speed_value
            generator = pipeline(
                text, 
                voice=self.voice,
                speed=self.speed  # Kokoro aceita speed diretamente
            )

            audio_chunks = []
            for _, _, audio in generator:
                audio_chunks.append(audio)

            if not audio_chunks:
                print("❌ Nenhum áudio gerado")
                return 0.0

            audio_data = np.concatenate(audio_chunks)
            
            # Aplicar ajuste de pitch e volume manualmente
            if self.pitch != 1.0:
                # Ajuste simples de pitch (alterando velocidade de playback)
                from scipy import signal
                new_length = int(len(audio_data) / self.pitch)
                audio_data = signal.resample(audio_data, new_length)
            
            if self.volume != 1.0:
                audio_data = audio_data * self.volume
            
            # Garantir que o áudio está no range válido
            audio_data = np.clip(audio_data, -1.0, 1.0)
            
            # Criar diretório se não existir
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            
            sf.write(output_file, audio_data, self.sample_rate)

            duration = len(audio_data) / self.sample_rate
            print(f"✅ Áudio gerado: {output_file} (Duração: {duration:.2f}s)")
            return duration
            
        except Exception as e:
            print(f"❌ Erro ao gerar áudio: {e}")
            
            # Tentar fallback: usar velocidade padrão
            try:
                print("🔄 Tentando com velocidade padrão...")
                pipeline = KPipeline(lang_code=self.lang_code)
                generator = pipeline(text, voice=self.voice, speed=1.0)  # Velocidade padrão
                
                audio_chunks = []
                for _, _, audio in generator:
                    audio_chunks.append(audio)
                
                if audio_chunks:
                    audio_data = np.concatenate(audio_chunks)
                    
                    # Ajustar volume apenas
                    if self.volume != 1.0:
                        audio_data = audio_data * self.volume
                    
                    os.makedirs(os.path.dirname(output_file), exist_ok=True)
                    sf.write(output_file, audio_data, self.sample_rate)
                    
                    duration = len(audio_data) / self.sample_rate
                    print(f"✅ Áudio gerado (fallback): {output_file} (Duração: {duration:.2f}s)")
                    return duration
            except Exception as e2:
                print(f"❌ Fallback também falhou: {e2}")
            
            return 0.0

    def set_voice_config(self, speed=None, pitch=None, volume=None):
        """
        Update voice configuration parameters.
        
        Args:
            speed (float, optional): Speech speed multiplier (0.5-2.0)
            pitch (float, optional): Voice pitch multiplier (0.5-2.0)
            volume (float, optional): Audio volume multiplier (0.0-2.0)
        """
        if speed is not None:
            self.speed = max(0.5, min(2.0, speed))
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

    def generate_audio_simple(self, text, output_file):
        """
        Versão simplificada para quando a versão com parâmetros falha.
        Usa configurações padrão.
        """
        try:
            print(f"🎤 Gerando áudio (modo simples) com voz: {self.voice}")
            
            pipeline = KPipeline(lang_code=self.lang_code)
            generator = pipeline(text, voice=self.voice)  # Sem parâmetros extras
            
            audio_chunks = []
            for _, _, audio in generator:
                audio_chunks.append(audio)
            
            if not audio_chunks:
                print("❌ Nenhum áudio gerado")
                return 0.0
            
            audio_data = np.concatenate(audio_chunks)
            
            # Ajustar volume apenas
            if self.volume != 1.0:
                audio_data = audio_data * self.volume
            
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            sf.write(output_file, audio_data, self.sample_rate)
            
            duration = len(audio_data) / self.sample_rate
            print(f"✅ Áudio gerado (simples): {output_file} (Duração: {duration:.2f}s)")
            return duration
            
        except Exception as e:
            print(f"❌ Erro no modo simples: {e}")
            return 0.0