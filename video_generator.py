import os
import gc
import subprocess
import shutil
import random
import glob
import numpy as np
import json
import re
import unicodedata

from rapidfuzz import fuzz

from moviepy.editor import (
    concatenate_videoclips,
    VideoFileClip,
    ColorClip,
    AudioFileClip,
    CompositeVideoClip,
    ImageClip,
    CompositeAudioClip,
    concatenate_audioclips
)

from PIL import Image, ImageDraw, ImageFont


class VideoGenerator:
    def __init__(
        self,
        theme="universe_sleep_shorts",
        channel="parallelcuts",
        zoom_strength=0.015,
        grain_intensity=0.08,
        vignette_intensity=0.9,
        screen_orientation="MOBILE",
        subtitle_font="lilita.ttf",
        subtitle_font_size=50,
        subtitle_words_per_line=3,
        video_style="simple",
        optimize_memory=True
    ):
        self.theme = theme
        self.channel = channel
        self.zoom_strength = zoom_strength
        self.grain_intensity = grain_intensity
        self.vignette_intensity = vignette_intensity
        self.screen_orientation = screen_orientation
        self.subtitle_font = subtitle_font
        self.subtitle_font_size = subtitle_font_size
        self.subtitle_words_per_line = subtitle_words_per_line
        self.video_style = video_style
        self.optimize_memory = optimize_memory
        self.effects = VideoEffects()
        self.whisper_model = None

    def get_video_size(self):
        return (720, 1280) if self.screen_orientation == "MOBILE" else (1920, 1080)

    def get_recent_videos(theme, limit=None):
        files = glob.glob(f"videos/{theme}*.mp4")
        files.sort(key=os.path.getmtime, reverse=True)  # 🔥 mais novos primeiro
        return files[:limit] if limit else files
    
    def apply_overlay(self, base_video, opacity=0.4):
        """
        Aplica um overlay visual contínuo sobre o vídeo base.
        O overlay é aplicado UMA única vez, após o concatenate.
        """

        overlay_files = glob.glob("./overlays/*.mp4")

        if not overlay_files:
            print("⚠️ Nenhum overlay encontrado, pulando overlay.")
            return base_video

        overlay_path = random.choice(overlay_files)

        try:
            overlay = VideoFileClip(str(overlay_path), audio=False)

            # 🔁 garante que o overlay dure o vídeo inteiro
            overlay = overlay.loop(duration=base_video.duration)

            # 📐 garante mesmo tamanho
            overlay = overlay.resize(base_video.size)

            # 🎚️ controla força do efeito
            overlay = overlay.set_opacity(opacity)

            # 🎬 composição final
            final = CompositeVideoClip(
                [base_video, overlay],
                size=base_video.size
            )

            return final

        except Exception as e:
            print(f"⚠️ Erro ao aplicar overlay: {e}")
            return base_video


    def create_video_sequence(self, duration):
        """Cria sequência de vídeos de fundo usando os mais recentes, porém embaralhados."""
        video_files = glob.glob(f"videos/{self.theme}*.mp4")

        if not video_files:
            blank_clip = ColorClip(size=self.get_video_size(), color=(0, 0, 0))
            return blank_clip.set_duration(duration)

        # 🔥 filtra só os vídeos do tema
        video_files = [
            vf for vf in video_files
            if os.path.basename(vf).startswith(self.theme)
        ]

        if not video_files:
            blank_clip = ColorClip(size=self.get_video_size(), color=(0, 0, 0))
            return blank_clip.set_duration(duration)

        # 🔥 ordena do mais recente pro mais antigo
        video_files.sort(key=os.path.getmtime, reverse=True)

        # 🔥 limita aos mais recentes (ajuste como quiser)
        MAX_RECENT = 50
        recent_videos = video_files[:MAX_RECENT]

        # 🔥 embaralha os recentes
        random.shuffle(recent_videos)

        segments = []
        source_clips = []
        total_duration = 0
        target_size = self.get_video_size()

        idx = 0
        max_clip_len = 4.0

        while total_duration < duration:
            video_path = recent_videos[idx % len(recent_videos)]
            idx += 1

            try:
                clip = VideoFileClip(video_path, audio=False)
                clip = clip.resize(target_size)

                clip_duration = min(max_clip_len, duration - total_duration)

                clip_segment = clip.subclip(0, clip_duration)

                source_clips.append(clip)
                segments.append(clip_segment)
                total_duration += clip_duration

            except Exception as e:
                print(f"⚠️ Erro ao ler vídeo {video_path}: {e}")
                blank_clip = ColorClip(size=target_size, color=(0, 0, 0))
                blank_clip = blank_clip.set_duration(
                    min(max_clip_len, duration - total_duration)
                )
                segments.append(blank_clip)
                total_duration += blank_clip.duration

        if not segments:
            return ColorClip(size=target_size, color=(0, 0, 0)).set_duration(duration)

        try:
            final_video = concatenate_videoclips(segments)

            if final_video.duration > duration:
                final_video = final_video.subclip(0, duration)

            # 🔥 overlay aplicado uma única vez (correto)
            final_video = self.apply_overlay(final_video)

            for sc in source_clips:
                try:
                    if hasattr(sc, "reader") and sc.reader:
                        sc.reader.close()
                except Exception:
                    pass

            return final_video

        except Exception as e:
            print(f"⚠️ Erro ao concatenar vídeos: {e}")
            return ColorClip(size=target_size, color=(0, 0, 0)).set_duration(duration)

    def _load_whisper(self):
        """Carrega modelo Whisper se necessário."""
        if self.whisper_model is None:
            try:
                from faster_whisper import WhisperModel
                self.whisper_model = WhisperModel(
                    "tiny", device="cpu", compute_type="int8"
                )
            except ImportError:
                print("⚠️ Whisper não instalado. Use: pip install faster-whisper")
                self.whisper_model = None
        return self.whisper_model

    def clean_text(self, text):
        if not text:
            return ""

        text = text.replace("\n", " ").replace("\r", " ")
        text = re.sub(r"\s+", " ", text).strip()
        text = re.sub(r"^\s*\d+\s+", "", text)
        text = re.sub(r"\.(\s|$)", "... ", text)
        text = re.sub(r"\b[pP]onto\b", "", text)
        text = re.sub(r"\s+", " ", text).strip()

        return text

    def normalize(self, s: str) -> str:
        s = s.lower()
        s = unicodedata.normalize("NFD", s)
        s = "".join(c for c in s if unicodedata.category(c) != "Mn")
        return re.sub(r"[^\w]", "", s)

    def refine_words_python(self, words, text_base, max_window=4, min_score=80):
        if not words or not text_base:
            return words

        base_tokens = re.findall(r"\w+", text_base, re.UNICODE)
        base_norm = [self.normalize(w) for w in base_tokens]

        cursor = 0

        for w in words:
            original = w["text"]
            norm_word = self.normalize(original)

            best_idx = None
            best_score = 0

            start = max(0, cursor - max_window)
            end = min(len(base_tokens), cursor + max_window + 1)

            for i in range(start, end):
                score = fuzz.ratio(norm_word, base_norm[i])
                if score > best_score:
                    best_score = score
                    best_idx = i

            if best_idx is not None and best_score >= min_score:
                w["text"] = base_tokens[best_idx]
                cursor = best_idx + 1
            else:
                w["text"] = original

        return words

    def transcribe_audio(self, audio_path, text_base):
        """Transcreve áudio e retorna palavras com timestamps."""
        model = self._load_whisper()
        if not model:
            return []

        try:
            segments, _ = model.transcribe(
                audio_path, word_timestamps=True, beam_size=1
            )

            words = []
            for segment in segments:
                for word in segment.words:
                    words.append({
                        "text": word.word.strip(),
                        "start": word.start,
                        "end": word.end,
                        "duration": word.end - word.start
                    })

            return self.refine_words_python(words, text_base)

        except Exception as e:
            print(f"❌ Erro na transcrição: {e}")
            return []
        
    def _create_subtitle_clip(self, segment, video_size, font_color, x_pos=0.5, y_pos=0.8):
        """Cria UMA legenda individual."""
        try:
            img = Image.new("RGBA", video_size, (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)

            font_path = os.path.join("images", self.subtitle_font)
            if os.path.exists(font_path):
                font = ImageFont.truetype(font_path, self.subtitle_font_size)
            else:
                font = ImageFont.load_default()

            text_bbox = draw.textbbox((0, 0), segment["text"], font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]

            if isinstance(x_pos, float):
                x = int(video_size[0] * x_pos - text_width / 2)
            else:
                x = x_pos

            if isinstance(y_pos, float):
                y = int(video_size[1] * y_pos - text_height / 2)
            else:
                y = y_pos

            shadow_offset = 2
            draw.text(
                (x + shadow_offset, y + shadow_offset),
                segment["text"],
                fill=(0, 0, 0, 100),
                font=font
            )

            draw.text(
                (x, y),
                segment["text"],
                fill=font_color,
                font=font
            )

            img_array = np.array(img)
            duration = max(segment["duration"], 0.1)

            if img_array.shape[2] == 4:
                rgb = img_array[..., :3]
                alpha = (img_array[..., 3] / 255.0).astype("float32")

                clip = ImageClip(rgb)\
                    .set_duration(duration)\
                    .set_start(segment["start"])

                try:
                    mask_clip = ImageClip(alpha)\
                        .set_duration(duration)\
                        .set_start(segment["start"])\
                        .set_is_mask(True)

                    clip = clip.set_mask(mask_clip)
                except Exception:
                    clip = ImageClip(
                        img_array,
                        transparent=True,
                        duration=duration
                    ).set_start(segment["start"])
            else:
                clip = ImageClip(
                    img_array,
                    transparent=True,
                    duration=duration
                ).set_start(segment["start"])

            clip = clip.fadein(0.2).fadeout(0.2)
            return clip

        except Exception as e:
            print(f"⚠️ Erro na legenda: {e}")
            return None

    def create_subtitle_clips(self, words, video_size, font_color, x_pos=0.5, y_pos=0.8):
        """Cria VÁRIAS legendas sincronizadas."""
        if not words:
            return []

        clips = []
        current_line = []
        current_start = 0

        for i, word in enumerate(words):
            current_line.append(word["text"])

            if len(current_line) == 1:
                current_start = word["start"]

            should_create = (
                len(current_line) >= self.subtitle_words_per_line
                or i == len(words) - 1
                or word["end"] - current_start > 3.0
            )

            if should_create and current_line:
                segment = {
                    "text": " ".join(current_line),
                    "start": current_start,
                    "duration": word["end"] - current_start
                }

                clip = self._create_subtitle_clip(
                    segment,
                    video_size,
                    font_color,
                    x_pos=x_pos,
                    y_pos=y_pos
                )

                if clip:
                    clips.append(clip)

                current_line = []
                current_start = word["end"]

        return clips

    def add_synchronized_subtitles(self, video, text_base, audio_path, font_color, x_pos=0.5, y_pos=0.8):
        """Adiciona legendas sincronizadas com a fala."""
        if not audio_path or not os.path.exists(audio_path):
            return video

        print("📝 Transcrevendo áudio...")
        words = self.transcribe_audio(audio_path, text_base)

        if not words:
            return video

        print(f"🎬 Criando {len(words)} legendas...")
        subtitle_clips = self.create_subtitle_clips(
            words,
            video.size,
            font_color,
            x_pos=x_pos,
            y_pos=y_pos
        )

        if not subtitle_clips:
            return video

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
                img_clip = img_clip.resize(height=150)

                x_pos = int(video.size[0] * 0.3)
                y_pos = int(video.size[1] * 0.8)

                img_clip = img_clip.set_position((x_pos, y_pos))
                img_clip = img_clip.set_opacity(0.7)

                return CompositeVideoClip([video, img_clip])
            except Exception as e:
                print(f"⚠️ Erro ao adicionar subscribe: {e}")

        return video

    def add_image(self, video, image_path, x_pos=0.3, y_pos=0.8, height=None, width=None, opacity=0.7):
        if not os.path.exists(image_path):
            print(f"⚠️ Imagem não encontrada: {image_path}")
            return video

        try:
            img_clip = ImageClip(image_path, duration=video.duration)

            if height:
                img_clip = img_clip.resize(height=height)
            elif width:
                img_clip = img_clip.resize(width=width)
            else:
                max_height = video.size[1] // 4
                if img_clip.h > max_height:
                    img_clip = img_clip.resize(height=max_height)

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
            print(f"⚠️ Arquivo de áudio não encontrado: {audio_path}")
            return video

        try:
            print(f"🎵 Adicionando áudio de voz: {os.path.basename(audio_path)}")
            voice_audio = AudioFileClip(audio_path)
            
            # CORREÇÃO: Garantir que o áudio não seja mais longo que o vídeo
            if voice_audio.duration > video.duration:
                print(f"⚠️ Áudio ({voice_audio.duration:.2f}s) mais longo que vídeo ({video.duration:.2f}s). Cortando...")
                voice_audio = voice_audio.subclip(0, video.duration)
            elif voice_audio.duration < video.duration:
                print(f"⚠️ Vídeo ({video.duration:.2f}s) mais longo que áudio ({voice_audio.duration:.2f}s). Ajustando...")
                # Cortar vídeo para duração do áudio
                video = video.subclip(0, voice_audio.duration)
            
            video = video.set_audio(voice_audio)
            print(f"✅ Áudio de voz adicionado (áudio: {voice_audio.duration:.2f}s, vídeo: {video.duration:.2f}s)")
            return video
        except Exception as e:
            print(f"⚠️ Erro ao adicionar voz: {e}")
            return video

    def add_background_music(self, video, audio_duration):
        """Adiciona música de fundo ao vídeo."""
        try:
            music_files = glob.glob(f"songs/{self.theme}*.mp3")
            if not music_files:
                music_files = glob.glob("songs/*.mp3")

            if not music_files:
                print("🎵 Nenhuma música de fundo encontrada")
                return video

            music_path = random.choice(music_files)
            print(f"🎵 Adicionando música: {os.path.basename(music_path)}")

            music_clip = AudioFileClip(music_path)

            # CORREÇÃO: Usar a duração real do vídeo, não do parâmetro
            video_duration = video.duration
            
            if music_clip.duration < video_duration:
                repeat_count = int(video_duration // music_clip.duration) + 1
                music_clips = [music_clip] * repeat_count
                music_clip = concatenate_audioclips(music_clips)

            music_clip = music_clip.subclip(0, video_duration)
            music_clip = music_clip.volumex(0.3)

            if video.audio:
                base_audio = video.audio
                try:
                    # CORREÇÃO: Garantir que ambos tenham a mesma duração
                    base_audio = base_audio.subclip(0, video_duration)
                    music_clip = music_clip.subclip(0, video_duration)
                    
                    final_audio = CompositeAudioClip(
                        [base_audio, music_clip]
                    ).set_duration(video_duration)
                except Exception as e:
                    print(f"⚠️ Erro ao sincronizar áudio: {e}")
                    # Fallback: usar apenas o áudio base
                    final_audio = base_audio.set_duration(video_duration)
            else:
                final_audio = music_clip.set_duration(video_duration)

            video = video.set_audio(final_audio)
            print(f"✅ Música de fundo adicionada (duração: {video_duration:.2f}s)")
            return video

        except Exception as e:
            print(f"⚠️ Erro na música de fundo: {e}")
            return video

    def apply_video_effects(self, video):
        """Aplica efeitos visuais baseados no estilo."""

        #video = self.effects.apply_vignette(video, intensity=6)

        #video = self.effects.apply_zoom_effect(video, strength=4)
        
        #video = self.effects.apply_film_grain(video, intensity=4)

        return video

    def generate_video(self, audio_path, font_color, audio_duration, output_path, text=None):
        """Gera vídeo final."""
        video = None

        try:
            print("🎬 Iniciando geração do vídeo...")

            if os.path.exists(audio_path):
                voice_audio = AudioFileClip(audio_path)
                actual_audio_duration = voice_audio.duration
                voice_audio.close()
                print(f"📊 Duração do áudio: {actual_audio_duration:.2f}s")
            else:
                actual_audio_duration = audio_duration
                print(f"📊 Duração fornecida: {actual_audio_duration:.2f}s")

            print("1/7 Criando sequência de vídeo...")
            video = self.create_video_sequence(actual_audio_duration)

            try:
                video = video.set_duration(actual_audio_duration)
            except Exception:
                pass

            print(f"📊 Duração do vídeo criado: {video.duration:.2f}s")

            print("2/7 Adicionando áudio de voz...")
            video = self.add_voice_audio(video, audio_path)

            print("3/7 Adicionando música de fundo...")
            video = self.add_background_music(video, actual_audio_duration)

            print("5/7 Adicionando legendas sincronizadas...")
            if self.screen_orientation == "MOBILE":
                video = self.add_synchronized_subtitles(
                    video,
                    text,
                    audio_path,
                    font_color,
                    x_pos=0.5,
                    y_pos=0.65 if self.screen_orientation == "MOBILE" else 0.85
                )
                

            print("6/7 Adicionando logo...")
            logo_path = f"images/logo-canal-{self.channel}.jpg"
            if os.path.exists(logo_path):
                video = self.add_image(
                    video,
                    logo_path,
                    x_pos=0.45 if self.screen_orientation == "MOBILE" else 0.2,
                    y_pos=0.2 if self.screen_orientation == "MOBILE" else 0.2,
                    height=100,
                    opacity=0.7
                )

            print("7/7 Adicionando subscribe...")
            subscribe_path = "images/subscribe.png"
            if os.path.exists(subscribe_path):
                video = self.add_image(
                    video,
                    subscribe_path,
                    x_pos=0.2,
                    y_pos=0.8 if self.screen_orientation == "MOBILE" else 0.9,
                    height=50,
                    opacity=0.4
                )

            output_dir = os.path.dirname(output_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)

            print(f"💾 Salvando vídeo final ({video.duration:.2f}s)...")
            success = self.save_with_cpu(video, output_path)

            if success:
                print(f"✅ Vídeo salvo: {output_path}")
                return output_path
            else:
                print(f"❌ Falha ao salvar vídeo: {output_path}")
                return None

        except Exception as e:
            print(f"❌ Erro ao gerar vídeo: {e}")
            import traceback
            traceback.print_exc()
            raise

        finally:
            if video:
                video.close()

    def save_with_cpu(self, video, output_path):
        """Fallback para CPU."""
        try:
            print("🖥️ Usando CPU para encoding...")

            if not video.audio:
                from moviepy.editor import AudioClip
                silence = AudioClip(
                    make_frame=lambda t: 0,
                    duration=video.duration,
                    fps=44100
                )
                video = video.set_audio(silence)

            video.write_videofile(
                output_path,
                fps=24,
                codec="libx264",
                audio_codec="aac",
                verbose=False,
                threads=8,
                preset="ultrafast",
                ffmpeg_params=[
                    "-crf", "30",
                    "-tune", "fastdecode",
                    "-movflags", "+faststart",
                    "-g", "48",
                    "-keyint_min", "24",
                    "-sc_threshold", "0"
                ]
            )
            return True

        except Exception as e:
            print(f"❌ Erro com CPU: {e}")
            return False


class VideoEffects:
    def __init__(self):
        pass

    def apply_vignette(self, clip, intensity=0.6):
        w, h = clip.size
        X, Y = np.ogrid[:h, :w]

        mask = 1.0 - intensity * np.sqrt(
            (X - h / 2.0) ** 2 + (Y - w / 2.0) ** 2
        ) / np.sqrt((h / 2.0) ** 2 + (w / 2.0) ** 2)

        mask = np.maximum(mask, 0)
        mask = np.dstack([mask, mask, mask])

        return clip.fl_image(lambda frame: (frame * mask).astype("uint8"))

    def apply_sepia(self, clip, intensity=0.7):
        sepia_filter = np.array([
            [0.393, 0.769, 0.189],
            [0.349, 0.686, 0.168],
            [0.272, 0.534, 0.131]
        ])

        def apply_sepia_filter(frame):
            return np.clip(
                frame.dot(sepia_filter.T) * intensity + frame * (1 - intensity),
                0,
                255
            ).astype("uint8")

        return clip.fl_image(apply_sepia_filter)

    def apply_zoom_effect(self, clip, strength=0.015):
        """Aplica efeito de zoom suave (Ken Burns effect)."""
        def zoom_func(get_frame, t):
            frame = get_frame(t)
            zoom_factor = 1 + strength * np.sin(2 * np.pi * t / clip.duration)
            
            h, w = frame.shape[:2]
            new_h = int(h / zoom_factor)
            new_w = int(w / zoom_factor)
            
            y_start = (h - new_h) // 2
            x_start = (w - new_w) // 2
            
            cropped = frame[y_start:y_start+new_h, x_start:x_start+new_w]
            return np.array(Image.fromarray(cropped).resize((w, h), Image.LANCZOS))
        
        return clip.fl(zoom_func, apply_to=['mask', 'video'])

    def apply_film_grain(self, clip, intensity=0.03):
        """Adiciona grão de filme ao vídeo."""
        def add_grain(frame):
            noise = np.random.randn(*frame.shape) * 255 * intensity
            return np.clip(frame + noise, 0, 255).astype('uint8')
        
        return clip.fl_image(add_grain)