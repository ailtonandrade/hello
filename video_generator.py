import os
import gc
import random
import glob
from moviepy.editor import concatenate_videoclips, VideoFileClip, ColorClip, AudioFileClip, CompositeVideoClip, ImageClip, CompositeAudioClip, concatenate_audioclips
from video_editor import add_logo, add_image, add_text
from PIL import Image, ImageDraw, ImageFont
from faster_whisper import WhisperModel
from effects_templates import VideoEffects

class VideoGenerator:
    def __init__(self, theme="pregacao", screen_orientation="MOBILE", channel="parallelcuts", 
                 subtitle_font="arial.ttf", subtitle_font_size=50, subtitle_color="white", 
                 subtitle_words_per_line=3, subtitle_one_word_at_a_time=False,
                 video_style="simple"):
        self.theme = theme
        self.screen_orientation = screen_orientation
        self.channel = channel
        self.subtitle_font = subtitle_font
        self.subtitle_font_size = subtitle_font_size
        self.subtitle_color = subtitle_color
        self.subtitle_words_per_line = subtitle_words_per_line
        self.subtitle_one_word_at_a_time = subtitle_one_word_at_a_time
        self.video_style = video_style
    
        # Inicializar gerenciador de efeitos
        self.effects = VideoEffects()
        self.effects.screen_orientation = screen_orientation  # Passar orientação

    def get_video_size(self):
        return (1920, 1080) if self.screen_orientation == "DESKTOP" else (1080, 1920)

    def select_random_video(self):
        video_files = glob.glob(f"videos/{self.theme}*.mp4")
        if not video_files:
            print(f"No videos found for theme: {self.theme}. Using a blank background.")
            return None
        return random.choice(video_files)

    def create_video_sequence(self, duration):

        video_files = glob.glob(f"videos/{self.theme}*.mp4")
        if not video_files:
            print(f"No videos found for theme: {self.theme}. Using a blank background.")
            return ColorClip(size=self.get_video_size(), color=(0, 0, 0)).set_duration(duration)
        
        clips = []
        total_duration = 0
        target_size = self.get_video_size()
        
        while total_duration < duration:
            # Select random video
            video_path = random.choice(video_files)
            
            try:
                clip = VideoFileClip(video_path)
                
                # Resize/crop to target dimensions
                clip = self.resize_and_crop(clip, target_size)
                
                # Take 4 seconds from random position in the video
                clip_duration = min(4.0, duration - total_duration)
                start_time = random.uniform(0, max(0, clip.duration - clip_duration))
                clip_segment = clip.subclip(start_time, start_time + clip_duration)
                
                clips.append(clip_segment)
                total_duration += clip_duration
                
                clip.close()
                
            except Exception as e:
                print(f"Error processing video {video_path}: {e}")
                # Use blank clip as fallback
                blank_clip = ColorClip(size=target_size, color=(0, 0, 0)).set_duration(min(4.0, duration - total_duration))
                clips.append(blank_clip)
                total_duration += blank_clip.duration
        
        # Concatenate all clips
        try:
            final_video = concatenate_videoclips(clips)
            if final_video is None or not hasattr(final_video, 'duration') or final_video.duration <= 0:
                print("⚠️ concatenate_videoclips retornou vídeo inválido, usando clip em branco")
                final_video = ColorClip(size=self.get_video_size(), color=(0, 0, 0)).set_duration(duration)
        except Exception as e:
            print(f"⚠️ Erro ao concatenar clips: {e}, usando clip em branco")
            final_video = ColorClip(size=self.get_video_size(), color=(0, 0, 0)).set_duration(duration)
        
        # Trim to exact duration if needed
        if final_video.duration > duration:
            final_video = final_video.subclip(0, duration)
        
        return final_video

    def resize_and_crop(self, clip, target_size):

        target_width, target_height = target_size
        clip_width, clip_height = clip.size
        
        # Calculate scaling factor to fit target dimensions
        scale_width = target_width / clip_width
        scale_height = target_height / clip_height
        scale = max(scale_width, scale_height)
        
        try:
            # Resize clip
            resized_clip = clip.resize(scale)
            
            # Crop to target dimensions (center crop)
            current_width, current_height = resized_clip.size
            crop_x = (current_width - target_width) // 2
            crop_y = (current_height - target_height) // 2
            
            cropped_clip = resized_clip.crop(x1=crop_x, y1=crop_y, 
                                           x2=crop_x + target_width, 
                                           y2=crop_y + target_height)
            
            if cropped_clip is None or not hasattr(cropped_clip, 'size'):
                raise ValueError("crop returned invalid clip")
            
            return cropped_clip
        except Exception as e:
            print(f"⚠️ Erro ao redimensionar/cortar clip: {e}, retornando clip original")
            return clip

    def apply_video_style(self, video, text=""):
        """
        Aplica estilo de vídeo baseado na configuração.
        
        Args:
            video: VideoFileClip original
            text: Texto para usar em templates
            
        Returns:
            VideoFileClip com efeitos aplicados
        """
        print(f"🎨 Aplicando estilo: {self.video_style}")
        
        if self.video_style == "cinematic":
            # Template cinematográfico
            return self.effects.template_cinematic(
                video, 
                title="Versículo do Dia",
                subtitle="Deus te abençoe! 🙏"
            )
            
        elif self.video_style == "instagram":
            # Template Instagram Stories
            instagram_text = "Siga nosso canal!" if not text else text[:30] + "..."
            return self.effects.template_instagram_story(
                video,
                text=instagram_text,
                music_path=None  # Música já é adicionada separadamente
            )
            
        elif self.video_style == "tiktok":
            # Template TikTok
            tiktok_caption = "Isso muda tudo! ✨" if not text else text[:40] + "..."
            return self.effects.template_tiktok_video(
                video,
                caption=tiktok_caption,
                effect="zoom"
            )
            
        elif self.video_style == "simple":
            # Estilo simples com efeitos básicos
            video = self.effects.overlay_vignette(video, intensity=0.3)
            video = self.effects.overlay_film_grain(video, intensity=0.01)
            return video
            
        elif self.video_style == "vintage":
            # Estilo vintage
            video = self.effects.overlay_color_filter(video, "sepia", intensity=0.4)
            video = self.effects.overlay_vignette(video, intensity=0.5)
            video = self.effects.overlay_film_grain(video, intensity=0.03)
            return video
            
        elif self.video_style == "modern":
            # Estilo moderno
            video = self.effects.overlay_color_filter(video, "cool", intensity=0.2)
            # Adicionar texto flutuante se houver
            if text:
                words = text.split()[:5]
                short_text = " ".join(words)
                text_clip = self.effects.text_template_fade_in_out(
                    short_text,
                    duration=video.duration,
                    font_size=40,
                    font_color="#00FFFF",
                    position=("center", 0.9)
                )
                video = CompositeVideoClip([video, text_clip])
            return video
            
        else:
            # Estilo padrão (sem efeitos especiais)
            print(f"🎨 Estilo '{self.video_style}' não encontrado, usando padrão")
            return video
        
    def generate_word_timestamps(self, audio_path):

        try:
            # Load Whisper model (using a smaller model for speed)
            model = WhisperModel("small", device="cpu", compute_type="int8")
            
            # Transcribe with word-level timestamps
            segments, info = model.transcribe(audio_path, word_timestamps=True)
            
            word_timestamps = []
            for segment in segments:
                for word_info in segment.words:
                    word_timestamps.append((
                        word_info.word.strip(),
                        word_info.start,
                        word_info.end
                    ))
            
            print(f"📝 Transcrição completa gerada com {len(word_timestamps)} palavras")
            return word_timestamps
            
        except Exception as e:
            print(f"❌ Erro na transcrição com Whisper: {e}")
            print("🔄 Usando método alternativo de sincronização...")
            
            # Fallback: estimate based on text length
            return self._estimate_word_timestamps(audio_path)

    def _estimate_word_timestamps(self, audio_path):

        try:
            # Get audio duration
            audio_clip = AudioFileClip(audio_path)
            audio_duration = audio_clip.duration
            audio_clip.close()
            
            # For now, return empty list as we don't have the text here
            # This will be handled by the calling method
            return []
            
        except Exception as e:
            print(f"❌ Erro ao estimar timestamps: {e}")
            return []

    def add_synchronized_subtitles(self, video, audio_path):

        try:
            # Generate precise word timestamps using Whisper
            word_timestamps = self.generate_word_timestamps(audio_path)
            
            if not word_timestamps:
                print("⚠️ Não foi possível gerar timestamps das palavras")
                return video
            
            # Group words into subtitle segments (improved grouping)
            subtitle_segments = []
            
            if self.subtitle_one_word_at_a_time:
                # One word at a time mode
                for word, start_time, end_time in word_timestamps:
                    subtitle_segments.append({
                        'text': word,
                        'start_time': start_time,
                        'duration': end_time - start_time
                    })
                print(f"📝 Modo uma palavra por vez: {len(subtitle_segments)} segmentos criados")
                
                # Warning for too many segments
                if len(subtitle_segments) > 100:
                    print("⚠️ Muitos segmentos de legenda detectados (>50). Isso pode causar problemas de performance.")
                    print("💡 Considere usar modo agrupado definindo subtitle_one_word_at_a_time=False")
            else:
                # Grouped words mode
                current_segment = []
                current_start = 0
                max_segment_duration = 3.0  # Maximum duration for each subtitle segment
                
                for i, (word, start_time, end_time) in enumerate(word_timestamps):
                    current_segment.append(word)
                    
                    if len(current_segment) == 1:
                        current_start = start_time
                    
                    # Check if we should create a new segment
                    should_create_segment = False
                    
                    # Create segment if we have enough words per line
                    if len(current_segment) >= self.subtitle_words_per_line:
                        should_create_segment = True
                    
                    # Create segment if duration is too long
                    elif end_time - current_start > max_segment_duration:
                        should_create_segment = True
                    
                    # Create segment if this is the last word
                    elif i == len(word_timestamps) - 1:
                        should_create_segment = True
                    
                    if should_create_segment and current_segment:
                        # Create subtitle segment
                        subtitle_text = " ".join(current_segment)
                        duration = end_time - current_start
                        
                        subtitle_segments.append({
                            'text': subtitle_text,
                            'start_time': current_start,
                            'duration': duration
                        })
                        
                        current_segment = []
                        current_start = end_time
                
                # Add remaining words if any
                if current_segment:
                    last_end_time = word_timestamps[-1][2] if word_timestamps else current_start + 1.0
                    subtitle_text = " ".join(current_segment)
                    duration = last_end_time - current_start
                    
                    subtitle_segments.append({
                        'text': subtitle_text,
                        'start_time': current_start,
                        'duration': duration
                    })
                
                print(f"📝 Modo palavras agrupadas: {len(subtitle_segments)} segmentos criados")
            
            print(f"📝 Criando {len(subtitle_segments)} segmentos de legenda")
            
            # Create text clips for each segment
            text_clips = []
            
            for i, segment in enumerate(subtitle_segments):
                try:
                    # Validate segment data
                    if not segment.get('text') or segment.get('duration', 0) <= 0:
                        print(f"⚠️ Segmento {i} inválido: texto='{segment.get('text')}', duração={segment.get('duration')}")
                        continue
                    
                    # Create text configuration
                    config = {
                        "font_size": self.subtitle_font_size,
                        "font_color": self.subtitle_color,
                        "padding_x": 20,
                        "padding_y": 20,
                        "line_spacing": 10
                    }
                    
                    # Create text image
                    font_path = os.path.join('images', self.subtitle_font)
                    try:
                        font = ImageFont.truetype(font_path, config["font_size"])
                    except:
                        # Fallback to default font
                        font = ImageFont.load_default()
                    
                    img = Image.new("RGBA", video.size, color=(0, 0, 0, 0))  # Transparent background
                    draw = ImageDraw.Draw(img)

                    max_width = video.size[0] - config["padding_x"] * 2
                    lines = []
                    words = segment['text'].split()
                    current_line = ""

                    for word in words:
                        test_line = f"{current_line} {word}".strip()
                        try:
                            text_bbox = draw.textbbox((0, 0), test_line, font=font)
                            text_width = text_bbox[2] - text_bbox[0]
                        except:
                            text_width = len(test_line) * config["font_size"] * 0.6

                        if text_width <= max_width:
                            current_line = test_line
                        else:
                            lines.append(current_line)
                            current_line = word

                    if current_line:
                        lines.append(current_line)

                    try:
                        line_height = draw.textbbox((0, 0), "A", font=font)[3] - draw.textbbox((0, 0), "A", font=font)[1]
                    except:
                        line_height = config["font_size"]
                    
                    total_text_height = line_height * len(lines) + config["line_spacing"] * (len(lines) - 1)

                    y_offset = (img.height - total_text_height) // 2
                    for line in lines:
                        try:
                            text_bbox = draw.textbbox((0, 0), line, font=font)
                            text_width = text_bbox[2] - text_bbox[0]
                        except:
                            text_width = len(line) * config["font_size"] * 0.6
                        
                        x_position = (img.width - text_width) // 2
                        draw.text((x_position, y_offset), line, fill=config["font_color"], font=font)
                        y_offset += line_height + config["line_spacing"]

                    temp_image_path = f"temp_text_{segment['start_time']:.3f}.png"
                    img.save(temp_image_path, "PNG")

                    # Create text clip with validation
                    duration = max(segment['duration'], 0.1)  # Minimum 0.1 seconds
                    text_clip = ImageClip(temp_image_path, transparent=True).set_duration(duration).set_start(segment['start_time'])
                    
                    # Validate text clip
                    if text_clip.duration > 0 and text_clip.start >= 0:
                        text_clips.append(text_clip)
                    else:
                        print(f"⚠️ Clip de texto inválido descartado: duração={text_clip.duration}, início={text_clip.start}")
                        os.remove(temp_image_path)  # Clean up invalid file
                    
                except Exception as e:
                    print(f"⚠️ Erro ao criar clip de texto para segmento {i}: {e}")
                    continue
            
            # Composite video with all text clips
            if text_clips:
                try:
                    # Validate all text clips before composition
                    valid_clips = []
                    for i, clip in enumerate(text_clips):
                        if clip and hasattr(clip, 'duration') and clip.duration > 0:
                            valid_clips.append(clip)
                        else:
                            print(f"⚠️ Clip de texto {i} inválido descartado")
                    
                    print(f"📊 Usando {len(valid_clips)} clips de texto válidos de {len(text_clips)} criados")
                    
                    if len(valid_clips) > 50:
                        print("⚠️ Muitos clips de texto detectados. Isso pode causar problemas de performance.")
                        print("💡 Considere usar modo agrupado (subtitle_one_word_at_a_time=False)")
                    
                    if valid_clips:
                        try:
                            final_video = CompositeVideoClip([video] + valid_clips)
                            if final_video is not None and hasattr(final_video, 'duration') and final_video.duration > 0:
                                print(f"✅ Vídeo composto com {len(valid_clips)} legendas")
                                return final_video
                            else:
                                print("⚠️ CompositeVideoClip falhou, retornando vídeo original")
                                return video
                        except Exception as e:
                            print(f"⚠️ Erro no CompositeVideoClip das legendas: {e}")
                            return video
                    else:
                        print("⚠️ Nenhum clip de texto válido encontrado")
                        return video
                        
                except Exception as e:
                    print(f"⚠️ Erro ao compor vídeo com legendas: {e}")
                    print("🔄 Retornando vídeo sem legendas")
                    return video
            else:
                return video
                
        except Exception as e:
            print(f"⚠️ Erro geral ao adicionar legendas: {e}")
            return video

    def add_song(self, video, volume=0.3):

        # IMPORTANTE: Sempre retornar o vídeo, mesmo que haja erro!
        if video is None:
            print("❌ add_song: vídeo é None, retornando None")
            return None
            
        try:
            # Find all pregacao songs in the songs folder
            song_files = glob.glob("songs/pregacao*.mp3")
            
            if not song_files:
                print("⚠️ Nenhum arquivo de música encontrado na pasta songs/")
                return video
            
            # Select random song
            selected_song = random.choice(song_files)
            print(f"🎵 Adicionando música de fundo: {os.path.basename(selected_song)}")
            
            # Load the song
            if not os.path.exists(selected_song):
                print(f"⚠️ Arquivo de música não encontrado: {selected_song}")
                return video
            
            song_clip = AudioFileClip(selected_song)
            
            # Validate song clip
            if song_clip.duration <= 0:
                print(f"⚠️ Música com duração inválida: {song_clip.duration}")
                song_clip.close()
                return video
            
            print(f"✅ Música carregada - Duração: {song_clip.duration:.2f}s")
            
            # Set volume
            song_clip = song_clip.volumex(volume)
            
            # APLICAR EFEITOS DE ÁUDIO BASEADO NO ESTILO (ADICIONAR ESTAS LINHAS)
            if self.video_style == "cinematic":
                # Para estilo cinematográfico, adicionar eco leve
                song_clip = self.effects.audio_echo(song_clip, delay=0.1, decay=0.3)
            elif self.video_style == "vintage":
                # Para vintage, adicionar um pouco de ruído
                from moviepy.audio.fx.all import audio_normalize
                song_clip = audio_normalize(song_clip)
            
            song_clip = song_clip.volumex(volume)

            # If song is shorter than video, loop it
            video_duration = video.duration
            if song_clip.duration < video_duration:
                # Calculate how many times to repeat
                repeat_count = int(video_duration // song_clip.duration) + 1
                
                # Create repeated clips
                repeated_clips = []
                for i in range(repeat_count):
                    repeated_clips.append(song_clip)
                
                # Concatenate repeated clips
                song_clip = concatenate_audioclips(repeated_clips)
            
            # Trim to video duration
            song_clip = song_clip.subclip(0, video_duration)
            
            # Get existing audio
            existing_audio = video.audio
            
            # Validate existing audio
            if existing_audio is not None:
                if not hasattr(existing_audio, 'duration') or existing_audio.duration <= 0:
                    print("⚠️ Áudio existente inválido, ignorando")
                    existing_audio = None
            
            # Validate song clip
            if not hasattr(song_clip, 'duration') or song_clip.duration <= 0:
                print("⚠️ Clip de música inválido, pulando adição de música")
                song_clip.close()
                return video
            
            # Mix existing audio with background music
            try:
                if existing_audio is not None:
                    # Composite the audio tracks
                    final_audio = CompositeAudioClip([existing_audio, song_clip])
                else:
                    final_audio = song_clip
                
                # Validate final audio
                if final_audio is None or not hasattr(final_audio, 'duration') or final_audio.duration <= 0:
                    print("⚠️ Áudio final inválido, mantendo áudio original")
                    final_audio = existing_audio if existing_audio is not None else None
                    if final_audio is None:
                        return video
                
            except Exception as e:
                print(f"⚠️ Erro ao compor áudio: {e}")
                print("🔄 Mantendo áudio original")
                return video
            
            # Set the mixed audio to the video
            try:
                video_with_audio = video.set_audio(final_audio)
                if video_with_audio is not None:
                    print(f"✅ Música de fundo adicionada com sucesso")
                    return video_with_audio
                else:
                    print("⚠️ set_audio() retornou None, mantendo vídeo original")
                    return video
            except Exception as e:
                print(f"⚠️ Erro ao definir áudio no vídeo: {e}")
                print("🔄 Mantendo vídeo original")
                return video
            
        except Exception as e:
            print(f"❌ Erro ao adicionar música: {e}")
            # IMPORTANTE: SEMPRE retornar o vídeo original em caso de erro
            return video

    def _cleanup_temp_files(self):

        try:
            # Clean up temporary text image files
            temp_files = glob.glob("temp_text_*.png")
            removed_count = 0
            
            for temp_file in temp_files:
                try:
                    if os.path.exists(temp_file):
                        os.remove(temp_file)
                        removed_count += 1
                except Exception as e:
                    print(f"⚠️ Erro ao remover arquivo temporário {temp_file}: {e}")
            
            if removed_count > 0:
                print(f"🗑️ {removed_count} arquivos temporários removidos")
                
        except Exception as e:
            print(f"⚠️ Erro geral na limpeza de arquivos temporários: {e}")

    def generate_video(self, audio_path, audio_duration, output_path, text=None):

        print(f"🎬 Criando sequência de vídeo com duração {audio_duration:.2f} segundos...")
        
        # Create video sequence from random 4-second clips
        video = self.create_video_sequence(audio_duration)
        
        # Validate video sequence
        if video is None:
            raise ValueError("Failed to create video sequence")
        
        if not hasattr(video, 'duration') or video.duration <= 0:
            raise ValueError(f"Invalid video duration: {getattr(video, 'duration', 'None')}")
            
        print(f"✅ Sequência de vídeo criada: {video.duration:.2f}s")
        
        # Add audio to video
        print(f"🎵 Carregando áudio: {audio_path}")
        audio_clip = None
        try:
            if not os.path.exists(audio_path):
                raise FileNotFoundError(f"Arquivo de áudio não encontrado: {audio_path}")
            
            file_size = os.path.getsize(audio_path)
            if file_size < 100:  # Arquivo muito pequeno
                raise ValueError(f"Arquivo de áudio muito pequeno: {file_size} bytes")
            
            audio_clip = AudioFileClip(audio_path)
            
            # Validate audio clip
            if audio_clip.duration <= 0:
                raise ValueError(f"Duração do áudio inválida: {audio_clip.duration}")
            
            print(f"✅ Áudio carregado - Duração: {audio_clip.duration:.2f}s")
            
        except Exception as e:
            print(f"❌ Erro ao carregar áudio: {e}")
            # Create silent audio as fallback
            print("🔄 Criando áudio silencioso como fallback")
            try:
                audio_clip = AudioFileClip(audio_path)  # Try again, might work
                if audio_clip and audio_clip.duration > 0:
                    print(f"✅ Áudio de fallback carregado: {audio_clip.duration:.2f}s")
                else:
                    raise ValueError("Áudio de fallback inválido")
            except Exception as e2:
                print(f"❌ Erro no áudio de fallback: {e2}")
                # Create truly silent audio
                from moviepy.editor import AudioClip
                import numpy as np
                audio_clip = AudioClip(lambda t: np.zeros(2), duration=audio_duration)
                print(f"🔇 Criado áudio silencioso de {audio_duration:.2f}s")
        
        # Set audio to video (audio_clip should never be None now)
        if audio_clip is not None:
            try:
                video = video.set_audio(audio_clip)
                print("✅ Áudio definido no vídeo com sucesso")
            except Exception as e:
                print(f"⚠️ Erro ao definir áudio no vídeo: {e}")
        else:
            print("⚠️ Nenhum áudio válido disponível")

        # Add background music (VERIFICAR SE VÍDEO NÃO É NONE)
        if video is not None:
            video = self.add_song(video, volume=0.3)
            if video is None:
                raise ValueError("add_song() retornou None!")
        else:
            raise ValueError("Vídeo é None após adição de áudio")

        # APLICAR ESTILO DE VÍDEO (ADICIONAR ESTAS LINHAS)
        video = self.apply_video_style(video, text)

        # Add logo
        logo_path = f"images/logo-canal-{self.channel}.jpg"
        
        # Add logo
        logo_path = f"images/logo-canal-{self.channel}.jpg"
        if os.path.exists(logo_path):
            try:
                video = add_logo(video, logo_path, x_percent=0.45, y_percent=0.02, size_multiplier=0.8, opacity=0.7)
                print("✅ Logo adicionado com sucesso")
            except Exception as e:
                print(f"⚠️ Erro ao adicionar logo: {e}")
        else:
            print(f"⚠️ Logo não encontrado: {logo_path}")

        # Add subscribe image
        subscribe_image_path = "images/subscribe.png"
        if os.path.exists(subscribe_image_path):
            try:
                video = add_image(video, subscribe_image_path, x=0.2, y=0.7, size_multiplier=0.8, opacity=0.6)
                print("✅ Imagem de inscrição adicionada com sucesso")
            except Exception as e:
                print(f"⚠️ Erro ao adicionar imagem de inscrição: {e}")
        else:
            print(f"⚠️ Imagem de inscrição não encontrada: {subscribe_image_path}")

        # Add synchronized subtitles if text is provided
        if text:
            print("📝 Adicionando legendas sincronizadas...")
            try:
                video = self.add_synchronized_subtitles(video, audio_path)
                print(f"✅ Legendas adicionadas com sucesso")
            except Exception as e:
                print(f"⚠️ Erro ao adicionar legendas: {e}")
                # Continue without subtitles

        # Validate video before writing
        if video is None:
            raise ValueError("Video object is None - cannot write video file")

        # Additional validation
        try:
            # Check if video has required attributes
            if not hasattr(video, 'duration') or video.duration <= 0:
                raise ValueError(f"Video duration invalid: {getattr(video, 'duration', 'None')}")
            
            if not hasattr(video, 'size') or not video.size:
                raise ValueError(f"Video size invalid: {getattr(video, 'size', 'None')}")
                
            # Try to get a frame to ensure video is valid
            test_frame = video.get_frame(0)
            if test_frame is None:
                raise ValueError("Cannot get video frame - video may be corrupted")
                
        except Exception as e:
            print(f"❌ Validação do vídeo falhou: {e}")
            raise ValueError(f"Video validation failed: {e}")

        # Debug video properties
        print(f"🔍 Debug vídeo - Duração: {video.duration:.2f}s, Tamanho: {video.size}, FPS: {video.fps}")
        
        # Ensure video has valid audio
        if hasattr(video, 'audio') and video.audio is not None:
            print(f"🔍 Debug áudio - Duração: {video.audio.duration:.2f}s")
        else:
            print("⚠️ Vídeo não tem áudio válido")

        # Write final video
        print(f"🎬 Escrevendo vídeo final: {output_path}")
        
        # Force garbage collection and close any pending processes
        gc.collect()
        
        # Ensure output directory exists
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
        
        try:
            # Write with safe settings
            video.write_videofile(
                output_path, 
                codec="libx264", 
                fps=24, 
                verbose=False, 
                logger=None,
                audio_codec="aac",
                temp_audiofile=None,
                remove_temp=True,
                write_logfile=False,
                threads=1
            )
            print(f"✅ Video saved: {output_path}")
            
        except Exception as e:
            print(f"❌ Erro ao escrever vídeo: {e}")
            print("🔄 Tentando método alternativo...")
            try:
                # Try different codec
                temp_path = output_path.replace('.mp4', '_temp.mp4')
                video.write_videofile(
                    temp_path, 
                    codec="mpeg4", 
                    fps=24, 
                    verbose=False, 
                    logger=None,
                    audio_codec="mp3",
                    threads=1
                )
                
                if os.path.exists(temp_path):
                    os.replace(temp_path, output_path)
                    print(f"✅ Video saved (fallback method): {output_path}")
                else:
                    raise ValueError("Fallback method failed to create file")
                    
            except Exception as e2:
                print(f"❌ Erro no método alternativo: {e2}")
                raise e  # Raise original error
        
        finally:
            # Clean up clips
            try:
                video.close()
                if audio_clip:
                    audio_clip.close()
            except:
                pass
        
        # Verify output file was created successfully
        if os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            print(f"✅ Arquivo de vídeo criado: {file_size} bytes")
            if file_size < 1000:  # Less than 1KB is probably corrupted
                print("⚠️ Arquivo de vídeo muito pequeno - pode estar corrompido")
        else:
            print("❌ Arquivo de vídeo não foi criado!")
        
        # Clean up temporary text files
        self._cleanup_temp_files()
        
        return output_path

    def create_final_video(self, texts, output_video_path, output_folder=None):

        from voice_generator import VoiceGenerator
        
        try:
            # Generate audio from texts
            voice_gen = VoiceGenerator()
            full_text = " ".join(texts)
            
            # Save temporary audio in output folder if provided
            if output_folder:
                audio_path = os.path.join(output_folder, "temp_audio.wav")
            else:
                audio_path = "temp_audio.wav"
                
            audio_duration = voice_gen.generate_audio(full_text, audio_path)
            
            if audio_duration == 0:
                print("Failed to generate audio.")
                return

            # Generate video with the audio and subtitles
            self.generate_video(audio_path, audio_duration, output_video_path, text=full_text)
            
            # Clean up temporary audio file
            if os.path.exists(audio_path):
                os.remove(audio_path)
                
        except Exception as e:
            print(f"An error occurred while creating the video: {e}")