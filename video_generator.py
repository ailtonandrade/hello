import os
import random
import glob
from moviepy.editor import concatenate_videoclips, VideoFileClip, ColorClip, AudioFileClip, CompositeVideoClip, ImageClip, CompositeAudioClip, concatenate_audioclips
from video_editor import add_logo, add_image, add_text
from PIL import Image, ImageDraw, ImageFont
from faster_whisper import WhisperModel

class VideoGenerator:
    def __init__(self, theme="pregacao", screen_orientation="MOBILE", channel="parallelcuts", 
                 subtitle_font="arial.ttf", subtitle_font_size=50, subtitle_color="white", 
                 subtitle_words_per_line=1):
        self.theme = theme
        self.screen_orientation = screen_orientation
        self.channel = channel
        self.subtitle_font = subtitle_font
        self.subtitle_font_size = subtitle_font_size
        self.subtitle_color = subtitle_color
        self.subtitle_words_per_line = subtitle_words_per_line

    def get_video_size(self):
        return (1920, 1080) if self.screen_orientation == "DESKTOP" else (1080, 1920)

    def select_random_video(self):
        video_files = glob.glob(f"videos/{self.theme}*.mp4")
        if not video_files:
            print(f"No videos found for theme: {self.theme}. Using a blank background.")
            return None
        return random.choice(video_files)

    def create_video_sequence(self, duration):
        """
        Create a video sequence by taking 4 seconds from random videos until reaching the target duration.
        
        Args:
            duration (float): Target duration in seconds.
            
        Returns:
            VideoFileClip: Concatenated video sequence.
        """
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
        final_video = concatenate_videoclips(clips)
        
        # Trim to exact duration if needed
        if final_video.duration > duration:
            final_video = final_video.subclip(0, duration)
        
        return final_video

    def resize_and_crop(self, clip, target_size):
        """
        Resize and crop video clip to target dimensions, maintaining aspect ratio.
        
        Args:
            clip: VideoFileClip to resize
            target_size: Tuple (width, height) for target dimensions
            
        Returns:
            Resized and cropped VideoFileClip
        """
        target_width, target_height = target_size
        clip_width, clip_height = clip.size
        
        # Calculate scaling factor to fit target dimensions
        scale_width = target_width / clip_width
        scale_height = target_height / clip_height
        scale = max(scale_width, scale_height)
        
        # Resize clip
        resized_clip = clip.resize(scale)
        
        # Crop to target dimensions (center crop)
        current_width, current_height = resized_clip.size
        crop_x = (current_width - target_width) // 2
        crop_y = (current_height - target_height) // 2
        
        cropped_clip = resized_clip.crop(x1=crop_x, y1=crop_y, 
                                       x2=crop_x + target_width, 
                                       y2=crop_y + target_height)
        
        return cropped_clip

    def generate_word_timestamps(self, audio_path):
        """
        Generate precise word timestamps using Whisper.
        
        Args:
            audio_path (str): Path to the audio file
            
        Returns:
            list: List of tuples (word, start_time, end_time)
        """
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
        """
        Fallback method to estimate word timestamps when Whisper fails.
        
        Args:
            audio_path (str): Path to the audio file
            
        Returns:
            list: List of tuples (word, start_time, end_time)
        """
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
        """
        Add synchronized subtitles to the video using Whisper transcription.
        
        Args:
            video: VideoFileClip to add subtitles to
            audio_path (str): Path to the audio file
            
        Returns:
            VideoFileClip with subtitles
        """
        # Generate precise word timestamps using Whisper
        word_timestamps = self.generate_word_timestamps(audio_path)
        
        if not word_timestamps:
            print("⚠️ Não foi possível gerar timestamps das palavras")
            return video
        
        # Group words into subtitle segments
        subtitle_segments = []
        current_segment = []
        current_start = 0
        
        for word, start_time, end_time in word_timestamps:
            current_segment.append(word)
            
            if len(current_segment) == 1:
                current_start = start_time
            
            if len(current_segment) >= self.subtitle_words_per_line:
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
        
        # Add remaining words
        if current_segment:
            # Get the end time from the last word
            last_end_time = word_timestamps[-1][2] if word_timestamps else current_start + 1.0
            subtitle_text = " ".join(current_segment)
            duration = last_end_time - current_start
            
            subtitle_segments.append({
                'text': subtitle_text,
                'start_time': current_start,
                'duration': duration
            })
        
        print(f"📝 Criando {len(subtitle_segments)} segmentos de legenda")
        
        # Create text clips for each segment
        text_clips = []
        
        for segment in subtitle_segments:
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

            temp_image_path = f"temp_text_{segment['start_time']}.png"
            img.save(temp_image_path, "PNG")

            text_clip = ImageClip(temp_image_path, transparent=True).set_duration(segment['duration']).set_start(segment['start_time'])
            text_clips.append(text_clip)
        
        # Composite video with all text clips
        if text_clips:
            return CompositeVideoClip([video] + text_clips)
        else:
            return video

    def add_song(self, video, volume=0.3):
        """
        Add background music to the video from the songs folder.
        
        Args:
            video: VideoFileClip to add music to
            volume (float): Volume level for the background music (0.0 to 1.0)
            
        Returns:
            VideoFileClip with background music added
        """
        import glob
        
        # Find all pregacao songs in the songs folder
        song_files = glob.glob("songs/pregacao*.mp3")
        
        if not song_files:
            print("⚠️ Nenhum arquivo de música encontrado na pasta songs/")
            return video
        
        # Select random song
        selected_song = random.choice(song_files)
        print(f"🎵 Adicionando música de fundo: {os.path.basename(selected_song)}")
        
        try:
            # Load the song
            song_clip = AudioFileClip(selected_song)
            
            # Set volume
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
            
            # Mix existing audio with background music
            if existing_audio is not None:
                # Composite the audio tracks
                final_audio = CompositeAudioClip([existing_audio, song_clip])
            else:
                final_audio = song_clip
            
            # Set the mixed audio to the video
            video = video.set_audio(final_audio)
            
            # Clean up
            song_clip.close()
            
        except Exception as e:
            print(f"❌ Erro ao adicionar música: {e}")
        
        return video

    def _cleanup_temp_files(self):
        """
        Clean up temporary files created during video generation.
        """
        import glob
        
        # Clean up temporary text image files
        temp_files = glob.glob("temp_text_*.png")
        for temp_file in temp_files:
            try:
                os.remove(temp_file)
                print(f"🗑️ Arquivo temporário removido: {temp_file}")
            except Exception as e:
                print(f"⚠️ Erro ao remover arquivo temporário {temp_file}: {e}")

    def generate_video(self, audio_path, audio_duration, output_path, text=None):
        """
        Generate a video synchronized with the given audio.

        Args:
            audio_path (str): Path to the audio file.
            audio_duration (float): Duration of the audio in seconds.
            output_path (str): Path to save the generated video.
            text (str, optional): Text to display as synchronized subtitles.
        """
        print(f"🎬 Criando sequência de vídeo com duração {audio_duration:.2f} segundos...")
        
        # Create video sequence from random 4-second clips
        video = self.create_video_sequence(audio_duration)
        
        # Add audio to video
        audio_clip = AudioFileClip(audio_path)
        video = video.set_audio(audio_clip)

        # Add background music
        video = self.add_song(video, volume=0.3)

        # Add logo
        logo_path = f"images/logo-canal-{self.channel}.jpg"
        if os.path.exists(logo_path):
            video = add_logo(video, logo_path, x_percent=0.45, y_percent=0.02, size_multiplier=0.8, opacity=0.7)

        # Add subscribe image
        subscribe_image_path = "images/subscribe.png"
        if os.path.exists(subscribe_image_path):
            video = add_image(video, subscribe_image_path, x=0.2, y=0.7, size_multiplier=0.8, opacity=0.6)

        # Add synchronized subtitles if text is provided
        if text:
            print("📝 Adicionando legendas sincronizadas...")
            video = self.add_synchronized_subtitles(video, audio_path)

        # Write final video
        video.write_videofile(output_path, codec="libx264", fps=24)
        print(f"Video saved: {output_path}")
        
        # Clean up clips
        video.close()
        audio_clip.close()
        
        # Clean up temporary text files
        self._cleanup_temp_files()
        
        return output_path

    def create_final_video(self, texts, output_video_path, output_folder=None):
        """
        Main function to create the final video with audio generation.
        
        Args:
            texts (list): List of text segments.
            output_video_path (str): Path to save the final video.
            output_folder (str, optional): Folder to save temporary files.
        """
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