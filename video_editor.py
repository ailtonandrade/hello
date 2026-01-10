from moviepy.editor import VideoFileClip, CompositeVideoClip, ImageClip
import os
import tempfile

class VideoEditor:
    def __init__(self, video_path):
        self.video_path = video_path

    def adjust_contrast_and_saturation(self, contrast=1.2, saturation=1.2):
        """
        Adjust the contrast and saturation of the video using MoviePy.

        :param contrast: Multiplier for contrast adjustment.
        :param saturation: Multiplier for saturation adjustment.
        """
        try:
            # Load the video file
            clip = VideoFileClip(self.video_path)

            # Apply contrast and saturation adjustments
            def adjust_frame(frame):
                frame = frame * contrast  # Adjust contrast
                frame = frame ** (1 / saturation)  # Adjust saturation
                return frame.clip(0, 255).astype("uint8")

            edited_clip = clip.fl_image(adjust_frame)

            # Save the edited video
            output_path = self.video_path.replace(".mp4", "_edited.mp4")
            edited_clip.write_videofile(output_path, codec="libx264")
            print(f"Video edited and saved: {output_path}")
        except Exception as e:
            print(f"Error editing video: {e}")

    def add_logo(self, logo_path, x_percent=0.5, y_percent=0.5, size_multiplier=1.0, duration=None, opacity=0.3):
        """
        Add a logo to the video using MoviePy.

        :param logo_path: Path to the logo image.
        :param x_percent: Horizontal position as a percentage of the video width.
        :param y_percent: Vertical position as a percentage of the video height.
        :param size_multiplier: Multiplier for resizing the logo.
        :param duration: Duration for which the logo should appear (None for entire video).
        :param opacity: Opacity of the logo (default is 0.3).
        """
        try:
            # Load the video file
            clip = VideoFileClip(self.video_path)

            # Load and resize the logo
            logo = ImageClip(logo_path).set_duration(duration or clip.duration)
            logo = logo.resize(size_multiplier).set_opacity(opacity)

            # Calculate logo position
            video_width, video_height = clip.size
            logo_x = int(x_percent * video_width - logo.w / 2)
            logo_y = int(y_percent * video_height - logo.h / 2)
            logo = logo.set_position((logo_x, logo_y))

            # Overlay the logo on the video
            final_clip = CompositeVideoClip([clip, logo])

            # Save the video with the logo
            output_path = self.video_path.replace(".mp4", "_with_logo.mp4")
            final_clip.write_videofile(output_path, codec="libx264")
            print(f"Logo added and video saved: {output_path}")
        except Exception as e:
            print(f"Error adding logo: {e}")

    def process_video(self, logo_path=None, x_percent=0.3, y_percent=0.3, size_multiplier=0.5, duration=None, opacity=0.3, contrast=1.2, saturation=1.2):
        """
        Process the video by adjusting contrast, saturation, and optionally adding a logo.
        All changes are applied directly to the original file, overwriting it.

        :param logo_path: Path to the logo image (optional).
        :param x_percent: Horizontal position as a percentage of the video width (for logo).
        :param y_percent: Vertical position as a percentage of the video height (for logo).
        :param size_multiplier: Multiplier for resizing the logo.
        :param duration: Duration for which the logo should appear (None for entire video).
        :param opacity: Opacity of the logo (default is 0.3).
        :param contrast: Contrast multiplier.
        :param saturation: Saturation multiplier.
        """
        try:
            # 1. Ajuste de contraste e saturação em arquivo temporário
            with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as temp1:
                temp1_path = temp1.name
            clip = VideoFileClip(self.video_path)
            def adjust_frame(frame):
                frame = frame * contrast
                frame = frame ** (1 / saturation)
                return frame.clip(0, 255).astype("uint8")
            edited_clip = clip.fl_image(adjust_frame)
            edited_clip.write_videofile(temp1_path, codec="libx264", audio_codec="aac", temp_audiofile="temp-audio1.m4a", remove_temp=True)
            clip.close()
            edited_clip.close()

            # 2. Adição do logo em outro arquivo temporário (ou sobrescreve o original se não houver logo)
            with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as temp2:
                temp2_path = temp2.name
            clip2 = VideoFileClip(temp1_path)
            if logo_path:
                logo = ImageClip(logo_path).set_duration(clip2.duration)
                logo = logo.resize(size_multiplier).set_opacity(opacity)
                video_width, video_height = clip2.size
                logo_x = int(x_percent * video_width - logo.w / 2)
                logo_y = int(y_percent * video_height - logo.h / 2)
                logo = logo.set_position((logo_x, logo_y))
                final_clip = CompositeVideoClip([clip2, logo]).set_audio(clip2.audio)
            else:
                final_clip = clip2
            final_clip.write_videofile(self.video_path, codec="libx264", audio_codec="aac", temp_audiofile="temp-audio2.m4a", remove_temp=True)
            clip2.close()
            final_clip.close()

            # Limpeza dos arquivos temporários
            if os.path.exists(temp1_path):
                os.remove(temp1_path)
            if os.path.exists(temp2_path):
                os.remove(temp2_path)
            print(f"Final video saved: {self.video_path}")
        except Exception as e:
            print(f"Error processing video: {e}")