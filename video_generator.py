import os
import gc
import random
import glob
from moviepy.editor import (
    concatenate_videoclips, VideoFileClip, ColorClip, AudioFileClip, 
    CompositeVideoClip, ImageClip, CompositeAudioClip, concatenate_audioclips
)
from video_editor import add_logo, add_image, add_text
from PIL import Image, ImageDraw, ImageFont
from faster_whisper import WhisperModel
from effects_templates import VideoEffects

class VideoGenerator:
    def __init__(self, theme="pregacao", screen_orientation="MOBILE", channel="parallelcuts", 
                 subtitle_font="lilita.ttf", subtitle_font_size=50, subtitle_color="white", 
                 subtitle_words_per_line=3, subtitle_one_word_at_a_time=False,
                 video_style="simple", template_config=None):
        """
        Inicializa o gerador de vídeo com templates personalizáveis.
        
        Args:
            template_config: Dicionário com configurações de template para cada elemento
                Exemplo: {
                    "logo": {"x_percent": 0.45, "y_percent": 0.02, "size": 0.8, "opacity": 0.7},
                    "subscribe": {"x": 0.2, "y": 0.7, "size": 0.8, "opacity": 0.6},
                    "background": {"clip_duration": 4.0, "transition": "fade"},
                    "subtitle": {"font_size": 50, "color": "white", "bg_color": None}
                }
        """
        self.theme = theme
        self.screen_orientation = screen_orientation
        self.channel = channel
        self.subtitle_font = subtitle_font
        self.subtitle_font_size = subtitle_font_size
        self.subtitle_color = subtitle_color
        self.subtitle_words_per_line = subtitle_words_per_line
        self.subtitle_one_word_at_a_time = subtitle_one_word_at_a_time
        self.video_style = video_style
        
        # Configurações de template (padrão se não fornecido)
        self.template_config = template_config or self._get_default_template()
        
        # Inicializar gerenciador de efeitos
        self.effects = VideoEffects()
        self.effects.screen_orientation = screen_orientation

    def _get_default_template(self):
        """Retorna template padrão para todos os elementos."""
        return {
            "logo": {
                "x_percent": 0.45, "y_percent": 0.02, 
                "size_multiplier": 0.8, "opacity": 0.7
            },
            "subscribe": {
                "x": 0.2, "y": 0.7, 
                "size_multiplier": 0.8, "opacity": 0.6
            },
            "background": {
                "clip_duration": 4.0,
                "transition": "random",  # random, fade, slide, zoom
                "random_start": True
            },
            "subtitle": {
                "font_size": 50,
                "color": "white",
                "bg_color": None,
                "outline": False,
                "shadow": True,
                "animation": "fade"  # fade, typewriter, slide, bounce
            },
            "text_overlay": {
                "enabled": False,
                "text": "",
                "position": ("center", 0.1),
                "font_size": 40,
                "color": "#FFFFFF",
                "animation": "fade_in_out"
            }
        }

    def get_video_size(self):
        return (1920, 1080) if self.screen_orientation == "DESKTOP" else (1080, 1920)

    def select_random_video(self):
        """Seleciona vídeo aleatório do tema."""
        video_files = glob.glob(f"videos/{self.theme}*.mp4")
        return random.choice(video_files) if video_files else None

    def create_video_sequence(self, duration):
        """Cria sequência de vídeo com transições configuráveis."""
        video_files = glob.glob(f"videos/{self.theme}*.mp4")
        if not video_files:
            return ColorClip(size=self.get_video_size(), color=(0, 0, 0)).set_duration(duration)
        
        clips = []
        total_duration = 0
        target_size = self.get_video_size()
        
        while total_duration < duration:
            video_path = random.choice(video_files)
            try:
                clip = VideoFileClip(video_path)
                clip = self.resize_and_crop(clip, target_size)
                
                # Configuração do template
                clip_duration = min(
                    self.template_config["background"]["clip_duration"],
                    duration - total_duration
                )
                
                # Posição aleatória ou fixa
                if self.template_config["background"]["random_start"]:
                    start_time = random.uniform(0, max(0, clip.duration - clip_duration))
                else:
                    start_time = 0
                
                clip_segment = clip.subclip(start_time, start_time + clip_duration)
                clips.append(clip_segment)
                total_duration += clip_duration
                clip.close()
                
            except Exception as e:
                print(f"Erro no vídeo {video_path}: {e}")
                blank_clip = ColorClip(size=target_size, color=(0, 0, 0))
                blank_clip = blank_clip.set_duration(min(4.0, duration - total_duration))
                clips.append(blank_clip)
                total_duration += blank_clip.duration
        
        # Aplica transição baseada no template
        try:
            final_video = self._apply_transition(clips, duration)
        except Exception as e:
            print(f"Erro na transição: {e}, usando concatenação simples")
            final_video = concatenate_videoclips(clips)
        
        if final_video.duration > duration:
            final_video = final_video.subclip(0, duration)
        
        return final_video

    def _apply_transition(self, clips, total_duration):
        """Aplica transição baseada no template."""
        transition_type = self.template_config["background"]["transition"]
        
        if transition_type == "fade" and len(clips) > 1:
            # Transição fade entre clips
            transition_duration = 0.5
            result_clips = [clips[0]]
            
            for i in range(1, len(clips)):
                clip_with_fade = clips[i].crossfadein(transition_duration)
                result_clips.append(clip_with_fade.set_start(
                    result_clips[-1].duration - transition_duration
                ))
            
            return CompositeVideoClip(result_clips).subclip(0, total_duration)
        
        elif transition_type == "random" and len(clips) > 1:
            # Transição aleatória
            transition_types = ["fade", "slide", "zoom"]
            selected_type = random.choice(transition_types)
            self.template_config["background"]["transition"] = selected_type
            return self._apply_transition(clips, total_duration)
        
        # Transição padrão (concatenação simples)
        return concatenate_videoclips(clips)

    def resize_and_crop(self, clip, target_size):
        """Redimensiona e corta vídeo para o tamanho alvo."""
        target_width, target_height = target_size
        clip_width, clip_height = clip.size
        
        scale = max(target_width / clip_width, target_height / clip_height)
        
        try:
            resized_clip = clip.resize(scale)
            current_width, current_height = resized_clip.size
            crop_x = (current_width - target_width) // 2
            crop_y = (current_height - target_height) // 2
            
            return resized_clip.crop(
                x1=crop_x, y1=crop_y,
                x2=crop_x + target_width,
                y2=crop_y + target_height
            )
        except Exception as e:
            print(f"Erro no resize/crop: {e}")
            return clip

    def apply_video_style(self, video, text=""):
        """Aplica estilo visual ao vídeo."""
        print(f"🎨 Aplicando estilo: {self.video_style}")
        
        style_map = {
            "cinematic": lambda: self.effects.template_cinematic(
                video, title="Versículo do Dia", subtitle="Deus te abençoe! 🙏"
            ),
            "instagram": lambda: self.effects.template_instagram_story(
                video, text=text[:30] + "..." if text else "Siga nosso canal!"
            ),
            "tiktok": lambda: self.effects.template_tiktok_video(
                video, caption=text[:40] + "..." if text else "Isso muda tudo! ✨", effect="zoom"
            ),
            "simple": lambda: self._apply_simple_effects(video),
            "vintage": lambda: self._apply_vintage_effects(video),
            "modern": lambda: self._apply_modern_effects(video, text)
        }
        
        return style_map.get(self.video_style, lambda: video)()

    def _apply_simple_effects(self, video):
        """Aplica efeitos simples."""
        video = self.effects.overlay_vignette(video, intensity=0.3)
        return self.effects.overlay_film_grain(video, intensity=0.01)

    def _apply_vintage_effects(self, video):
        """Aplica efeitos vintage."""
        video = self.effects.overlay_color_filter(video, "sepia", intensity=0.4)
        video = self.effects.overlay_vignette(video, intensity=0.5)
        return self.effects.overlay_film_grain(video, intensity=0.03)

    def _apply_modern_effects(self, video, text):
        """Aplica efeitos modernos."""
        video = self.effects.overlay_color_filter(video, "cool", intensity=0.2)
        if text:
            words = text.split()[:5]
            short_text = " ".join(words)
            text_clip = self.effects.text_template_fade_in_out(
                short_text, duration=video.duration,
                font_size=40, font_color="#00FFFF", position=("center", 0.9)
            )
            video = CompositeVideoClip([video, text_clip])
        return video

    def generate_word_timestamps(self, audio_path):
        """Gera timestamps das palavras usando Whisper."""
        try:
            model = WhisperModel("small", device="cpu", compute_type="int8")
            segments, _ = model.transcribe(audio_path, word_timestamps=True)
            
            return [
                (word.word.strip(), word.start, word.end)
                for segment in segments for word in segment.words
            ]
        except Exception as e:
            print(f"Erro no Whisper: {e}")
            return []

    def add_synchronized_subtitles(self, video, audio_path):
        """Adiciona legendas sincronizadas com template aplicável."""
        word_timestamps = self.generate_word_timestamps(audio_path)
        if not word_timestamps:
            print("⚠️ Não foi possível gerar timestamps")
            return video
        
        subtitle_segments = self._group_subtitle_segments(word_timestamps)
        text_clips = self._create_subtitle_clips(video, subtitle_segments)
        
        if text_clips:
            try:
                final_video = CompositeVideoClip([video] + text_clips)
                if final_video and final_video.duration > 0:
                    print(f"✅ Legendas adicionadas: {len(text_clips)} segmentos")
                    return final_video
            except Exception as e:
                print(f"Erro ao compor legendas: {e}")
        
        return video

    def _group_subtitle_segments(self, word_timestamps):
        """Agrupa palavras em segmentos de legenda."""
        if self.subtitle_one_word_at_a_time:
            return [
                {"text": word, "start_time": start, "duration": end - start}
                for word, start, end in word_timestamps
            ]
        
        # Modo agrupado
        segments = []
        current_segment = []
        current_start = 0
        
        for i, (word, start, end) in enumerate(word_timestamps):
            current_segment.append(word)
            
            if len(current_segment) == 1:
                current_start = start
            
            should_create = (
                len(current_segment) >= self.subtitle_words_per_line or
                end - current_start > 3.0 or
                i == len(word_timestamps) - 1
            )
            
            if should_create and current_segment:
                segments.append({
                    "text": " ".join(current_segment),
                    "start_time": current_start,
                    "duration": end - current_start
                })
                current_segment = []
                current_start = end
        
        return segments

    def _create_subtitle_clips(self, video, segments):
        """Cria clips de legenda com template aplicado."""
        text_clips = []
        config = self.template_config["subtitle"]
        
        for segment in segments:
            if not segment.get("text") or segment.get("duration", 0) <= 0:
                continue
            
            try:
                # Aplica template de legenda
                if config.get("animation") == "typewriter":
                    text_clip = self._create_typing_subtitle(segment, video.size, config)
                elif config.get("animation") == "slide":
                    text_clip = self._create_sliding_subtitle(segment, video.size, config)
                elif config.get("animation") == "bounce":
                    text_clip = self._create_bouncing_subtitle(segment, video.size, config)
                else:
                    # Animação padrão (fade)
                    text_clip = self._create_fade_subtitle(segment, video.size, config)
                
                if text_clip:
                    text_clips.append(text_clip)
                    
            except Exception as e:
                print(f"Erro ao criar legenda: {e}")
                continue
        
        return text_clips

    def _create_fade_subtitle(self, segment, video_size, config):
        """Cria legenda com efeito fade."""
        img = Image.new("RGBA", video_size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Configura fonte
        font_path = os.path.join('images', self.subtitle_font)
        try:
            font = ImageFont.truetype(font_path, config["font_size"])
        except:
            font = ImageFont.load_default()
        
        # Renderiza texto
        text_bbox = draw.textbbox((0, 0), segment["text"], font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        
        x = (video_size[0] - text_width) // 2
        y = (video_size[1] - text_height) // 2
        
        # Aplica efeitos do template
        if config.get("bg_color"):
            padding = 10
            draw.rectangle(
                [x-padding, y-padding, x+text_width+padding, y+text_height+padding],
                fill=config["bg_color"]
            )
        
        if config.get("shadow"):
            # Sombra
            draw.text((x+2, y+2), segment["text"], fill="#00000080", font=font)
        
        if config.get("outline"):
            # Contorno
            for dx, dy in [(-1,-1), (-1,1), (1,-1), (1,1)]:
                draw.text((x+dx, y+dy), segment["text"], fill="#000000", font=font)
        
        # Texto principal
        draw.text((x, y), segment["text"], fill=config["color"], font=font)
        
        # Salva e cria clip
        temp_path = f"temp_text_{segment['start_time']:.3f}.png"
        img.save(temp_path, "PNG")
        
        text_clip = ImageClip(temp_path, transparent=True)
        text_clip = text_clip.set_duration(max(segment["duration"], 0.1))
        text_clip = text_clip.set_start(segment["start_time"])
        
        # Aplica fade
        fade_duration = min(0.3, segment["duration"] / 3)
        text_clip = text_clip.crossfadein(fade_duration).crossfadeout(fade_duration)
        
        return text_clip

    def _create_typing_subtitle(self, segment, video_size, config):
        """Cria legenda com efeito de digitação."""
        # Implementação simplificada - você pode expandir
        return self._create_fade_subtitle(segment, video_size, config)

    def _create_sliding_subtitle(self, segment, video_size, config):
        """Cria legenda com efeito de slide."""
        # Implementação simplificada
        return self._create_fade_subtitle(segment, video_size, config)

    def _create_bouncing_subtitle(self, segment, video_size, config):
        """Cria legenda com efeito de bounce."""
        # Implementação simplificada
        return self._create_fade_subtitle(segment, video_size, config)

    def add_song(self, video, volume=0.3):
        """Adiciona música de fundo."""
        if video is None:
            return None
        
        song_files = glob.glob("songs/pregacao*.mp3")
        if not song_files:
            return video
        
        try:
            selected_song = random.choice(song_files)
            print(f"🎵 Adicionando: {os.path.basename(selected_song)}")
            
            song_clip = AudioFileClip(selected_song)
            if song_clip.duration <= 0:
                song_clip.close()
                return video
            
            # Aplica efeitos de áudio baseados no estilo
            if self.video_style == "cinematic":
                song_clip = self.effects.audio_echo(song_clip, delay=0.1, decay=0.3)
            elif self.video_style == "vintage":
                from moviepy.audio.fx.all import audio_normalize
                song_clip = audio_normalize(song_clip)
            
            song_clip = song_clip.volumex(volume)
            
            # Loop se necessário
            video_duration = video.duration
            if song_clip.duration < video_duration:
                repeat_count = int(video_duration // song_clip.duration) + 1
                song_clip = concatenate_audioclips([song_clip] * repeat_count)
            
            song_clip = song_clip.subclip(0, video_duration)
            
            # Mistura com áudio existente
            existing_audio = video.audio
            if existing_audio and existing_audio.duration > 0:
                final_audio = CompositeAudioClip([existing_audio, song_clip])
            else:
                final_audio = song_clip
            
            return video.set_audio(final_audio)
            
        except Exception as e:
            print(f"Erro na música: {e}")
            return video

    def apply_element_templates(self, video):
        """Aplica templates para logo, subscribe e outros elementos."""
        # Logo
        logo_path = f"images/logo-canal-{self.channel}.jpg"
        if os.path.exists(logo_path):
            logo_config = self.template_config["logo"]
            try:
                video = add_logo(video, logo_path, **logo_config)
                print("✅ Logo aplicado")
            except Exception as e:
                print(f"Erro no logo: {e}")
        
        # Subscribe image
        subscribe_path = "images/subscribe.png"
        if os.path.exists(subscribe_path):
            subscribe_config = self.template_config["subscribe"]
            try:
                video = add_image(video, subscribe_path, **subscribe_config)
                print("✅ Subscribe aplicado")
            except Exception as e:
                print(f"Erro no subscribe: {e}")
        
        # Text overlay se configurado
        if self.template_config["text_overlay"]["enabled"]:
            text_config = self.template_config["text_overlay"]
            try:
                text_clip = self.effects.text_template_fade_in_out(
                    text_config["text"],
                    duration=video.duration,
                    font_size=text_config["font_size"],
                    font_color=text_config["color"],
                    position=text_config["position"]
                )
                video = CompositeVideoClip([video, text_clip])
                print("✅ Overlay de texto aplicado")
            except Exception as e:
                print(f"Erro no text overlay: {e}")
        
        return video

    def generate_video(self, audio_path, audio_duration, output_path, text=None):
        """Gera vídeo final com todos os templates aplicados."""
        print(f"🎬 Criando vídeo ({audio_duration:.2f}s)")
        
        # Cria sequência de vídeo
        video = self.create_video_sequence(audio_duration)
        if video is None or not hasattr(video, 'duration') or video.duration <= 0:
            raise ValueError("Falha ao criar sequência de vídeo")
        
        # Adiciona áudio principal
        try:
            audio_clip = AudioFileClip(audio_path) if os.path.exists(audio_path) else None
            if audio_clip and audio_clip.duration > 0:
                video = video.set_audio(audio_clip)
        except Exception as e:
            print(f"⚠️ Erro no áudio: {e}")
        
        # Adiciona música de fundo
        video = self.add_song(video, volume=0.3)
        
        # Aplica estilo visual
        video = self.apply_video_style(video, text)
        
        # Aplica templates de elementos (logo, subscribe, etc.)
        video = self.apply_element_templates(video)
        
        # Adiciona legendas se houver texto
        if text:
            video = self.add_synchronized_subtitles(video, audio_path)
        
        # Salva vídeo
        self._save_video(video, output_path)
        
        # Limpeza
        self._cleanup_temp_files()
        if 'audio_clip' in locals():
            audio_clip.close()
        video.close()
        
        return output_path

    def _save_video(self, video, output_path):
        """Salva o vídeo final."""
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
        
        try:
            video.write_videofile(
                output_path, 
                codec="libx264", 
                fps=24, 
                audio_codec="aac",
                verbose=False,
                threads=1
            )
            print(f"✅ Vídeo salvo: {output_path}")
        except Exception as e:
            print(f"❌ Erro ao salvar: {e}")
            raise

    def _cleanup_temp_files(self):
        """Limpa arquivos temporários."""
        try:
            for temp_file in glob.glob("temp_text_*.png"):
                os.remove(temp_file)
        except Exception as e:
            print(f"⚠️ Erro na limpeza: {e}")

    def create_final_video(self, texts, output_video_path, output_folder=None):
        """Cria vídeo completo a partir de textos."""
        from voice_generator import VoiceGenerator
        
        try:
            voice_gen = VoiceGenerator()
            full_text = " ".join(texts)
            
            audio_path = os.path.join(output_folder, "temp_audio.wav") if output_folder else "temp_audio.wav"
            audio_duration = voice_gen.generate_audio(full_text, audio_path)
            
            if audio_duration == 0:
                print("Falha no áudio")
                return
            
            self.generate_video(audio_path, audio_duration, output_video_path, text=full_text)
            
            if os.path.exists(audio_path):
                os.remove(audio_path)
                
        except Exception as e:
            print(f"Erro ao criar vídeo: {e}")