import os
import random
import glob
from moviepy.editor import concatenate_videoclips, VideoFileClip, ColorClip, AudioFileClip
from video_editor import add_logo, add_image, add_text

class VideoGenerator:
    def __init__(self, theme="pregacao", screen_orientation="MOBILE", channel="parallelcuts", 
                 subtitle_font="arial.ttf", subtitle_font_size=50, subtitle_color="white", 
                 subtitle_words_per_line=3):
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

    def generate_word_timestamps(self, text, audio_duration):
        """
        Generate timestamps for each word in the text based on audio duration.
        
        Args:
            text (str): The text to synchronize
            audio_duration (float): Total duration of the audio
            
        Returns:
            list: List of tuples (word, start_time, end_time)
        """
        words = text.split()
        if not words:
            return []
        
        # Calculate time per word (simple approach)
        time_per_word = audio_duration / len(words)
        
        timestamps = []
        current_time = 0
        
        for word in words:
            start_time = current_time
            end_time = current_time + time_per_word
            timestamps.append((word, start_time, end_time))
            current_time = end_time
        
        return timestamps

    def add_synchronized_subtitles(self, video, text, audio_duration):
        """
        Add synchronized subtitles to the video.
        
        Args:
            video: VideoFileClip to add subtitles to
            text (str): Text to display as subtitles
            audio_duration (float): Duration of the audio
            
        Returns:
            VideoFileClip with subtitles
        """
        timestamps = self.generate_word_timestamps(text, audio_duration)
        
        if not timestamps:
            return video
        
        # Group words into subtitle segments
        subtitle_segments = []
        current_segment = []
        current_start = 0
        current_end = 0
        
        for word, start_time, end_time in timestamps:
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
            subtitle_text = " ".join(current_segment)
            duration = audio_duration - current_start
            
            subtitle_segments.append({
                'text': subtitle_text,
                'start_time': current_start,
                'duration': duration
            })
        
        # Add subtitle clips to video
        subtitle_clips = []
        
        for segment in subtitle_segments:
            # Create text configuration
            config = {
                "font_size": self.subtitle_font_size,
                "font_color": self.subtitle_color,
                "padding_x": 20,
                "padding_y": 20,
                "line_spacing": 10
            }
            
            # Add subtitle using the existing add_text function
            video_with_subtitle = add_text(
                video, 
                segment['text'], 
                config, 
                segment['duration'], 
                segment['start_time']
            )
            
            subtitle_clips.append(video_with_subtitle)
        
        # If no subtitles were added, return original video
        if not subtitle_clips:
            return video
        
        # Composite all subtitle clips
        final_video = video
        for subtitle_clip in subtitle_clips:
            final_video = CompositeVideoClip([final_video, subtitle_clip])
        
        return final_video

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
            video = self.add_synchronized_subtitles(video, text, audio_duration)

        # Write final video
        video.write_videofile(output_path, codec="libx264", fps=24)
        print(f"Video saved: {output_path}")
        
        # Clean up clips
        video.close()
        audio_clip.close()
        
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

            # Generate video with the audio
            self.generate_video(audio_path, audio_duration, output_video_path)
            
            # Clean up temporary audio file
            if os.path.exists(audio_path):
                os.remove(audio_path)
                
        except Exception as e:
            print(f"An error occurred while creating the video: {e}")