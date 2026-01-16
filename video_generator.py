import os
import gc
import random
import glob
import numpy as np
from moviepy.editor import (
    concatenate_videoclips, VideoFileClip, ColorClip, 
    AudioFileClip, CompositeVideoClip, ImageClip,
    CompositeAudioClip, concatenate_audioclips
)
from PIL import Image, ImageDraw, ImageFont

class VideoGenerator:
    def __init__(self, theme="pregacao", screen_orientation="MOBILE", 
                 channel="parallelcuts", subtitle_font="lilita.ttf", 
                 subtitle_font_size=50, subtitle_words_per_line=3,
                 video_style="simple", optimize_memory=True):
        
        self.theme = theme
        self.screen_orientation = screen_orientation
        self.channel = channel
        self.subtitle_font = subtitle_font
        self.subtitle_font_size = subtitle_font_size
        self.subtitle_words_per_line = subtitle_words_per_line
        self.video_style = video_style
        self.optimize_memory = optimize_memory
        self.effects = VideoEffects()
        self.whisper_model = None

    def get_video_size(self):
        return (720, 1280) if self.screen_orientation == "MOBILE" else (1280, 720)

    def create_video_sequence(self, duration):
        """Cria sequência de vídeos de fundo."""
        video_files = glob.glob(f"videos/{self.theme}*.mp4")
        if not video_files:
            blank_clip = ColorClip(size=self.get_video_size(), color=(0, 0, 0))
            return blank_clip.set_duration(duration)
        
        clips = []
        total_duration = 0
        target_size = self.get_video_size()
        
        while total_duration < duration:
            video_path = random.choice(video_files)
            
            try:
                clip = VideoFileClip(video_path, audio=False)
                clip = clip.resize(target_size)
                
                clip_duration = min(4.0, duration - total_duration)
                start_time = random.uniform(0, max(0, clip.duration - clip_duration))
                clip_segment = clip.subclip(start_time, start_time + clip_duration)
                clips.append(clip_segment)
                total_duration += clip_duration
                clip.close()
            except:
                blank_clip = ColorClip(size=target_size, color=(0, 0, 0))
                blank_clip = blank_clip.set_duration(min(4.0, duration - total_duration))
                clips.append(blank_clip)
                total_duration += blank_clip.duration
        
        if not clips:
            blank_clip = ColorClip(size=target_size, color=(0, 0, 0))
            return blank_clip.set_duration(duration)
        
        try:
            final_video = concatenate_videoclips(clips)
            if final_video.duration > duration:
                final_video = final_video.subclip(0, duration)
            return final_video
        except:
            return ColorClip(size=target_size, color=(0, 0, 0)).set_duration(duration)

    def _load_whisper(self):
        """Carrega modelo Whisper se necessário."""
        if self.whisper_model is None:
            try:
                from faster_whisper import WhisperModel
                self.whisper_model = WhisperModel("tiny", device="cpu", compute_type="int8")
            except ImportError:
                print("⚠️ Whisper não instalado. Use: pip install faster-whisper")
                self.whisper_model = None
        return self.whisper_model

    def transcribe_audio(self, audio_path):
        """Transcreve áudio e retorna palavras com timestamps."""
        model = self._load_whisper()
        if not model:
            return []
        
        try:
            segments, _ = model.transcribe(audio_path, word_timestamps=True, beam_size=1)
            words = []
            for segment in segments:
                for word in segment.words:
                    words.append({
                        "text": word.word.strip(),
                        "start": word.start,
                        "end": word.end,
                        "duration": word.end - word.start
                    })
            return words
        except Exception as e:
            print(f"❌ Erro na transcrição: {e}")
            return []

    def create_subtitle_clips(self, words, video_size):
        """Cria clips de legenda sincronizados."""
        if not words:
            return []
        
        clips = []
        current_line = []
        current_start = 0
        
        for i, word in enumerate(words):
            current_line.append(word["text"])
            
            if len(current_line) == 1:
                current_start = word["start"]
            
            # Verifica se deve criar uma nova linha
            should_create = (
                len(current_line) >= self.subtitle_words_per_line or
                i == len(words) - 1 or
                word["end"] - current_start > 3.0
            )
            
            if should_create and current_line:
                segment = {
                    "text": " ".join(current_line),
                    "start": current_start,
                    "duration": word["end"] - current_start
                }
                
                # Cria clip da legenda
                clip = self._create_subtitle_clip(segment, video_size)
                if clip:
                    clips.append(clip)
                
                current_line = []
                current_start = word["end"]
        
        return clips

    def _create_subtitle_clip(self, segment, video_size):
        """Legenda com efeito de sombra."""
        try:
            img = Image.new("RGBA", video_size, (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            
            font_path = os.path.join('images', self.subtitle_font)
            if os.path.exists(font_path):
                font = ImageFont.truetype(font_path, self.subtitle_font_size)
            else:
                font = ImageFont.load_default()
            
            text_bbox = draw.textbbox((0, 0), segment["text"], font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
            
            x = (video_size[0] - text_width) // 2
            y = video_size[1] - text_height - 100
            
            # Sombra
            shadow_offset = 3
            draw.text((x+shadow_offset, y+shadow_offset), segment["text"], 
                    fill=(0, 0, 0, 150), font=font)
            
            # Texto principal
            draw.text((x, y), segment["text"], fill=(255, 255, 255, 255), font=font)
            
            img_array = np.array(img)
            duration = max(segment["duration"], 0.1)
            clip = ImageClip(img_array, transparent=True, duration=duration)
            clip = clip.set_start(segment["start"])
            clip = clip.fadein(0.2).fadeout(0.2)
            
            return clip
            
        except Exception as e:
            print(f"⚠️ Erro na legenda: {e}")
            return None

    def add_synchronized_subtitles(self, video, audio_path):
        """Adiciona legendas sincronizadas com a fala."""
        if not audio_path or not os.path.exists(audio_path):
            return video
        
        # Transcrever áudio
        print("📝 Transcrevendo áudio...")
        words = self.transcribe_audio(audio_path)
        
        if not words:
            return video
        
        # Criar clips de legenda
        print(f"🎬 Criando {len(words)} legendas...")
        subtitle_clips = self.create_subtitle_clips(words, video.size)
        
        if not subtitle_clips:
            return video
        
        # Adicionar legendas ao vídeo
        return CompositeVideoClip([video] + subtitle_clips)

    def add_logo(self, video):
        """Adiciona logo do canal."""
        logo_path = f"images/logo-canal-{self.channel}.jpg"
        if os.path.exists(logo_path):
            try:
                logo_clip = ImageClip(logo_path, duration=video.duration)
                logo_clip = logo_clip.resize(height=100)
                logo_clip = logo_clip.set_position(("center", 20))
                logo_clip = logo_clip.set_opacity(0.7)
                return CompositeVideoClip([video, logo_clip])
            except Exception as e:
                print(f"⚠️ Erro ao adicionar logo: {e}")
        return video

    def add_subscribe_image(self, video):
        """Adiciona imagem 'subscribe'."""
        subscribe_path = "images/subscribe.png"
        if os.path.exists(subscribe_path):
            try:
                img_clip = ImageClip(subscribe_path, duration=video.duration)
                # Redimensionar proporcionalmente
                img_clip = img_clip.resize(height=150)
                
                # Calcular posição (x=30%, y=80% da altura)
                x_pos = int(video.size[0] * 0.3)
                y_pos = int(video.size[1] * 0.8)
                
                img_clip = img_clip.set_position((x_pos, y_pos))
                img_clip = img_clip.set_opacity(0.7)
                return CompositeVideoClip([video, img_clip])
            except Exception as e:
                print(f"⚠️ Erro ao adicionar subscribe: {e}")
        return video

    def add_image(self, video, image_path, x_pos=0.3, y_pos=0.8, 
            height=None, width=None, opacity=0.7):

        if not os.path.exists(image_path):
            print(f"⚠️ Imagem não encontrada: {image_path}")
            return video
        
        try:
            img_clip = ImageClip(image_path, duration=video.duration)
            
            # Redimensionar
            if height:
                img_clip = img_clip.resize(height=height)
            elif width:
                img_clip = img_clip.resize(width=width)
            else:
                # Redimensionar proporcionalmente se muito grande
                max_height = video.size[1] // 4  # Máximo 25% da altura do vídeo
                if img_clip.h > max_height:
                    img_clip = img_clip.resize(height=max_height)
            
            # Calcular posição
            if isinstance(x_pos, float):
                x_pos = int(video.size[0] * x_pos)
            if isinstance(y_pos, float):
                y_pos = int(video.size[1] * y_pos)
            
            img_clip = img_clip.set_position((x_pos, y_pos))
            img_clip = img_clip.set_opacity(opacity)
            
            return CompositeVideoClip([video, img_clip])
            
        except Exception as e:
            print(f"⚠️ Erro ao adicionar imagem {os.path.basename(image_path)}: {e}")
            return video

    def add_voice_audio(self, video, audio_path):
        """Adiciona apenas o áudio de voz ao vídeo."""
        if not os.path.exists(audio_path):
            return video
        
        try:
            voice_audio = AudioFileClip(audio_path)
            return video.set_audio(voice_audio)
        except Exception as e:
            print(f"⚠️ Erro ao adicionar voz: {e}")
            return video

    def add_background_music(self, video, audio_duration):
        """Adiciona música de fundo ao vídeo."""
        try:
            # Procurar músicas na pasta songs
            music_files = glob.glob(f"songs/{self.theme}*.mp3")
            
            if not music_files:
                music_files = glob.glob("songs/*.mp3")
            
            if not music_files:
                print("🎵 Nenhuma música de fundo encontrada")
                return video
            
            # Selecionar música aleatória
            music_path = random.choice(music_files)
            print(f"🎵 Adicionando música: {os.path.basename(music_path)}")
            
            # Carregar música
            music_clip = AudioFileClip(music_path)
            
            # Se música for menor que duração, fazer loop
            if music_clip.duration < audio_duration:
                repeat_count = int(audio_duration // music_clip.duration) + 1
                music_clips = [music_clip] * repeat_count
                music_clip = concatenate_audioclips(music_clips)
            
            # Cortar para duração exata
            music_clip = music_clip.subclip(0, audio_duration)
            
            # Ajustar volume (30% do volume original)
            music_clip = music_clip.volumex(0.3)
            
            # Misturar com áudio existente se houver
            if video.audio:
                final_audio = CompositeAudioClip([video.audio, music_clip])
            else:
                final_audio = music_clip
            
            return video.set_audio(final_audio)
            
        except Exception as e:
            print(f"⚠️ Erro na música de fundo: {e}")
            return video

    def apply_video_effects(self, video):
        """Aplica efeitos visuais baseados no estilo."""
        if self.video_style == "cinematic":
            video = self.effects.apply_vignette(video, intensity=0.7)
            video = self.effects.apply_sepia(video, intensity=0.3)
        elif self.video_style == "vintage":
            video = self.effects.apply_sepia(video, intensity=0.6)
            video = self.effects.apply_vignette(video, intensity=0.4)
        elif self.video_style == "dramatic":
            video = self.effects.apply_vignette(video, intensity=0.8)
        return video

    def generate_video(self, audio_path, audio_duration, output_path, text=None):
        """Gera vídeo final com otimização AMD/CPU."""
        
        video = None
        try:
            # 1. Criar sequência de vídeo
            video = self.create_video_sequence(audio_duration)
            
            # 2. Adicionar áudio de voz
            video = self.add_voice_audio(video, audio_path)
            
            # 3. Adicionar música de fundo
            video = self.add_background_music(video, audio_duration)
            
            # 4. Aplicar efeitos visuais
            if self.video_style != "simple":
                video = self.apply_video_effects(video)
            
            # 5. Adicionar legendas
            if text and audio_duration < 120:
                video = self.add_synchronized_subtitles(video, audio_path)
            
            # 6. Adicionar logo
            logo_path = f"images/logo-canal-{self.channel}.jpg"
            video = self.add_image(video, logo_path, x_pos=0.45, y_pos=0.02, 
                                height=100, opacity=0.7)
            
            # 7. Adicionar subscribe
            subscribe_path = "images/subscribe.png"
            video = self.add_image(video, subscribe_path, x_pos=0.3, y_pos=0.8, 
                                height=80, opacity=0.6)
            
            # 8. Salvar vídeo
            output_dir = os.path.dirname(output_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)
            
            # Tentar AMD primeiro
            if not self.save_with_amd_acceleration(video, output_path):
                # Se AMD falhar, usar CPU
                self.save_with_cpu(video, output_path)
            
            print(f"✅ Vídeo salvo: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"❌ Erro ao gerar vídeo: {e}")
            raise
        finally:
            if video:
                video.close()

    def save_with_amd_acceleration(self, video, output_path):
        """AMD RX 580 para TUDO - vídeo e áudio."""
        import subprocess
        import tempfile
        
        try:
            print("🚀🚀🚀 AMD RX 580 - TUDO NA GPU! 🚀🚀🚀")
            
            # 1. Exportar SOMENTE ÁUDIO (CPU rápido, mas necessário)
            audio_temp = None
            if hasattr(video, 'audio') and video.audio is not None:
                audio_temp = tempfile.NamedTemporaryFile(suffix='.mp3', delete=False)
                audio_temp.close()
                
                print("🔊 Exportando áudio (única parte CPU)...")
                video.audio.write_audiofile(
                    audio_temp.name,
                    fps=44100,
                    verbose=False
                )
            
            # 2. AGORA VEM A GPU PESADA!
            print("🎮 INICIANDO ENCODING AMD RX 580...")
            
            # Comando FFmpeg que usa GPU para TUDO que puder
            cmd = [
                'ffmpeg',
                '-hwaccel', 'auto',          # Usa GPU para DECODE
                '-hwaccel_device', '0',      # GPU 0 (sua RX 580)
                
                # Input de vídeo RAW via pipe
                '-f', 'rawvideo',
                '-vcodec', 'rawvideo',
                '-s', f'{video.size[0]}x{video.size[1]}',
                '-pix_fmt', 'rgb24',
                '-r', '24',
                '-i', '-',                   # Vídeo vem do stdin
            ]
            
            # Adicionar áudio se existir
            if audio_temp and os.path.exists(audio_temp.name):
                cmd.extend(['-i', audio_temp.name])
            
            # PARÂMETROS AMD - GPU PARA ENCODING!
            cmd.extend([
                '-c:v', 'h264_amf',          # ⬅️⬅️⬅️ GPU ENCODING!
                '-quality', 'balanced',
                '-b:v', '3M',
                '-preset', 'fast',
            ])
            
            # Configurar áudio
            if audio_temp and os.path.exists(audio_temp.name):
                cmd.extend([
                    '-c:a', 'aac',
                    '-b:a', '192k',
                ])
            
            # Output
            cmd.extend(['-y', output_path])
            
            print(f"🔥 Comando GPU: {' '.join(cmd[:15])}...")
            
            # Iniciar FFmpeg
            process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=10**8
            )
            
            # 3. ENVIAR FRAMES DIRETO PARA GPU
            total_frames = int(video.duration * 24)
            print(f"🎬 Enviando {total_frames} frames para AMD RX 580...")
            
            for i in range(total_frames):
                try:
                    frame = video.get_frame(i / 24)
                    process.stdin.write(frame.tobytes())
                    
                    if i % 48 == 0:  # Progresso a cada 2 segundos
                        percent = (i / total_frames) * 100
                        print(f"📊 GPU: {percent:.1f}%", end='\r')
                except Exception as e:
                    print(f"⚠️ Frame {i} erro: {e}")
                    continue
            
            # Fechar e esperar
            process.stdin.close()
            
            # Monitorar logs da GPU
            for line in process.stderr:
                if 'amf' in line.lower():
                    print(f"🔥 GPU ativa: {line.strip()[:60]}")
                if 'frame=' in line:
                    print(f"🎬 {line.strip()}", end='\r')
            
            process.wait()
            
            # Limpar temporários
            if audio_temp and os.path.exists(audio_temp.name):
                os.remove(audio_temp.name)
            
            if process.returncode == 0:
                print("\n✅✅✅ GPU FINALIZOU TUDO! ✅✅✅")
                return True
            else:
                print(f"\n❌ GPU falhou: código {process.returncode}")
                return False
                
        except Exception as e:
            print(f"❌ Erro GPU total: {e}")
            import traceback
            traceback.print_exc()
            
            # Limpar se falhar
            if 'audio_temp' in locals() and audio_temp and os.path.exists(audio_temp.name):
                try:
                    os.remove(audio_temp.name)
                except:
                    pass
            
            return False
        
    def save_with_cpu(self, video, output_path):
        """Fallback para CPU."""
        try:
            print("🖥️  Usando CPU para encoding...")
            
            video.write_videofile(
                output_path,
                fps=24,
                codec='libx264',
                audio_codec='aac',
                verbose=False,
                threads=6,                    # Usa mais threads
                preset='fast',                # Preset rápido
                ffmpeg_params=['-crf', '23']  # Quality factor
            )
            return True
        except Exception as e:
            print(f"❌ Erro com CPU: {e}")
            return False


# Mantenha a mesma classe VideoEffects
import numpy as np
from moviepy.editor import *
from PIL import Image, ImageDraw, ImageFont

class VideoEffects:
    def __init__(self):
        pass
    
    def apply_vignette(self, clip, intensity=0.6):
        """Adiciona efeito vinheta."""
        w, h = clip.size
        X, Y = np.ogrid[:h, :w]
        mask = 1.0 - intensity * np.sqrt((X - h/2.0)**2 + (Y - w/2.0)**2) / np.sqrt((h/2.0)**2 + (w/2.0)**2)
        mask = np.maximum(mask, 0)
        mask = np.dstack([mask, mask, mask])
        
        return clip.fl_image(lambda frame: (frame * mask).astype('uint8'))
    
    def apply_sepia(self, clip, intensity=0.7):
        """Aplica filtro sépia."""
        sepia_filter = np.array([
            [0.393, 0.769, 0.189],
            [0.349, 0.686, 0.168],
            [0.272, 0.534, 0.131]
        ])
        
        def apply_sepia_filter(frame):
            return np.clip(frame.dot(sepia_filter.T) * intensity + frame * (1 - intensity), 0, 255).astype('uint8')
        
        return clip.fl_image(apply_sepia_filter)
    
    def create_text_overlay(self, text, duration, font_size=60, color="white"):
        """Cria overlay de texto simples."""
        img = Image.new("RGBA", (720, 1280), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.truetype("lilita.ttf", font_size)
        except:
            font = ImageFont.load_default()
        
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        
        x = (720 - text_width) // 2
        y = 1280 - text_height - 100
        
        draw.text((x, y), text, fill=color, font=font)
        
        img_array = np.array(img)
        text_clip = ImageClip(img_array, transparent=True, duration=duration)
        return text_clip.fadein(0.5).fadeout(0.5)