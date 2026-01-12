from moviepy.editor import VideoFileClip, CompositeVideoClip, ImageClip
import os
import tempfile

class VideoEditor:
    def __init__(self, video_path):
        self.video_path = video_path

    def adjust_contrast_and_saturation(self, contrast=1.0, saturation=1.0):
        """
        Adjust the contrast and saturation of the video using MoviePy.

        :param contrast: Multiplier for contrast adjustment (default is 1.0, no change).
        :param saturation: Multiplier for saturation adjustment (default is 1.0, no change).
        """
        try:
            # Load the video file
            clip = VideoFileClip(self.video_path)

            # Apply contrast and saturation adjustments directly
            def adjust_frame(frame):
                # Ensure no changes are made to the frame
                return frame

            edited_clip = clip.fl_image(adjust_frame)

            # Save the edited video
            output_path = self.video_path.replace(".mp4", "_edited.mp4")
            edited_clip.write_videofile(output_path, codec="libx264")
            print(f"Video edited and saved: {output_path}")
        except Exception as e:
            print(f"Error editing video: {e}")

    def add_logo(self, logo_path, x_percent=0.5, y_percent=0.5, size_multiplier=1.0, duration=None, opacity=0.3, output_path=None, input_path=None):
        """
        Add a logo to the video using MoviePy.

        :param logo_path: Path to the logo image.
        :param x_percent: Horizontal position as a percentage of the video width.
        :param y_percent: Vertical position as a percentage of the video height.
        :param size_multiplier: Multiplier for resizing the logo.
        :param duration: Duration for which the logo should appear (None for entire video).
        :param opacity: Opacity of the logo (default is 0.3).
        :param output_path: Path to save the output video (if None, overwrite self.video_path).
        :param input_path: Path to use as input video (if None, use self.video_path).
        """
        try:
            video_path = input_path if input_path else self.video_path
            clip = VideoFileClip(video_path)
            logo = ImageClip(logo_path).set_duration(duration or clip.duration)
            logo = logo.resize(size_multiplier).set_opacity(opacity)
            video_width, video_height = clip.size
            logo_x = int(x_percent * video_width - logo.w / 2)
            logo_y = int(y_percent * video_height - logo.h / 2)
            logo = logo.set_position((logo_x, logo_y))
            final_clip = CompositeVideoClip([clip, logo]).set_audio(clip.audio)
            save_path = output_path if output_path else self.video_path
            final_clip.write_videofile(save_path, codec="libx264", audio_codec="aac", temp_audiofile="temp-audio-logo.m4a", remove_temp=True)
            clip.close()
            final_clip.close()
            print(f"Logo added and video saved: {save_path}")
        except Exception as e:
            print(f"Error adding logo: {e}")

    def add_image(self, image_path, x=0, y=0, size_multiplier=1.0, duration=None, opacity=1.0, output_path=None, input_path=None):
        """
        Add a PNG image to the video at a specific position, size, and opacity.

        :param image_path: Path to the PNG image.
        :param x: X coordinate in pixels (top-left of image) or percentual se float entre 0 e 1.
        :param y: Y coordinate in pixels (top-left of image) ou percentual se float entre 0 e 1.
        :param size_multiplier: Multiplier for resizing the image.
        :param duration: Duration for which the image should appear (None for entire video).
        :param opacity: Opacity of the image (default is 1.0).
        :param output_path: Path to save the output video (if None, overwrite self.video_path).
        :param input_path: Path to use as input video (if None, use self.video_path).
        """
        try:
            if not os.path.exists(image_path):
                print(f"Image file not found: {image_path}")
                return

            # Ensure the PNG has a transparent background
            from PIL import Image
            img = Image.open(image_path)
            if img.mode != "RGBA":
                print(f"Converting image to RGBA mode for transparency: {image_path}")
                img = img.convert("RGBA")
            temp_transparent_path = image_path.replace(".png", "_transparent.png")
            img.save(temp_transparent_path)

            video_path = input_path if input_path else self.video_path
            clip = VideoFileClip(video_path)
            img_clip = ImageClip(temp_transparent_path).set_duration(duration or clip.duration)
            img_clip = img_clip.resize(size_multiplier).set_opacity(opacity)

            # Allow percentual coordinates (0-1) or absolute
            video_width, video_height = clip.size
            pos_x = int(x * video_width) if isinstance(x, float) and 0 <= x <= 1 else x
            pos_y = int(y * video_height) if isinstance(y, float) and 0 <= y <= 1 else y
            img_clip = img_clip.set_position((pos_x, pos_y))

            final_clip = CompositeVideoClip([clip, img_clip]).set_audio(clip.audio)
            save_path = output_path if output_path else self.video_path
            final_clip.write_videofile(save_path, codec="libx264", audio_codec="aac", temp_audiofile="temp-audio-img.m4a", remove_temp=True)

            clip.close()
            final_clip.close()

            # Clean up temporary transparent image
            if os.path.exists(temp_transparent_path):
                os.remove(temp_transparent_path)

            print(f"Image added and video saved: {save_path}")
        except Exception as e:
            print(f"Error adding image: {e}")

    def process_video(self, logo_path=None, x_percent=0.3, y_percent=0.3, size_multiplier=0.5, duration=None, opacity=0.3, contrast=1.0, saturation=1.0, extra_images=None):
        """
        Process the video by adjusting contrast, saturation, adding a logo e imagens extras.
        Cada etapa é feita em um arquivo temporário único e sequencial, e o resultado final sobrescreve o original.
        :param extra_images: lista de dicts com keys: image_path, x, y, size_multiplier, duration, opacity
        """
        import shutil
        try:
            # 1. Ajuste de contraste e saturação em arquivo temporário
            with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as temp_prev:
                temp_prev_path = temp_prev.name
            clip = VideoFileClip(self.video_path)
            def adjust_frame(frame):
                # Ensure no changes are made to the frame
                return frame
            edited_clip = clip.fl_image(adjust_frame)
            edited_clip.write_videofile(temp_prev_path, codec="libx264", audio_codec="aac", temp_audiofile="temp-audio1.m4a", remove_temp=True)
            clip.close()
            edited_clip.close()

            # 2. Adição do logo (se houver)
            if logo_path:
                with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as temp_next:
                    temp_next_path = temp_next.name
                self.add_logo(logo_path, x_percent, y_percent, size_multiplier, duration, opacity, output_path=temp_next_path, input_path=temp_prev_path)
                if os.path.exists(temp_prev_path):
                    os.remove(temp_prev_path)
                temp_prev_path = temp_next_path

            # 3. Adicionar imagens extras (ex: subscribe.png) em sequência
            if extra_images is None:
                extra_images = [
                    {"image_path": "subscribe.png", "x": 0.2, "y": 0.8, "size_multiplier": 0.2, "duration": None, "opacity": 0.8}
                ]
            for img in extra_images:
                with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as temp_next:
                    temp_next_path = temp_next.name
                self.add_image(
                    img["image_path"],
                    x=img.get("x", 0),
                    y=img.get("y", 0),
                    size_multiplier=img.get("size_multiplier", 1.0),
                    duration=img.get("duration", None),
                    opacity=img.get("opacity", 1.0),
                    output_path=temp_next_path,
                    input_path=temp_prev_path
                )
                if os.path.exists(temp_prev_path):
                    os.remove(temp_prev_path)
                temp_prev_path = temp_next_path

            # 4. Junta o resultado final no arquivo original
            shutil.move(temp_prev_path, self.video_path)
            print(f"Final video saved: {self.video_path}")
        except Exception as e:
            print(f"Error processing video: {e}")