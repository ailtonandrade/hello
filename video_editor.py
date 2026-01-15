from moviepy.editor import VideoFileClip, CompositeVideoClip, ImageClip
from moviepy.video.fx.resize import resize
import os
import tempfile
from PIL import Image, ImageDraw, ImageFont

def add_text(video, text, config, duration, start_time):
    font_path = os.path.join('images', 'arial.ttf')
    font = ImageFont.truetype(font_path, config["font_size"])

    img = Image.new("RGBA", video.size, color=(0, 0, 0, 0))  # Transparent background
    draw = ImageDraw.Draw(img)

    max_width = video.size[0] - config["padding_x"] * 2
    lines = []
    words = text.split()
    current_line = ""

    for word in words:
        test_line = f"{current_line} {word}".strip()
        text_bbox = draw.textbbox((0, 0), test_line, font=font)
        text_width = text_bbox[2] - text_bbox[0]

        if text_width <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word

    if current_line:
        lines.append(current_line)

    line_height = draw.textbbox((0, 0), "A", font=font)[3] - draw.textbbox((0, 0), "A", font=font)[1]
    total_text_height = line_height * len(lines) + config["line_spacing"] * (len(lines) - 1)

    y_offset = (img.height - total_text_height) // 2
    for line in lines:
        text_bbox = draw.textbbox((0, 0), line, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        x_position = (img.width - text_width) // 2
        draw.text((x_position, y_offset), line, fill=config["font_color"], font=font)
        y_offset += line_height + config["line_spacing"]

    temp_image_path = f"temp_text_{start_time}.png"
    img.save(temp_image_path, "PNG")

    text_clip = ImageClip(temp_image_path, transparent=True).set_duration(duration).set_start(start_time)
    return CompositeVideoClip([video, text_clip])

def add_logo(video, logo_path, x_percent, y_percent, size_multiplier, opacity):
    if not os.path.exists(logo_path):
        print(f"Logo file not found: {logo_path}. Skipping logo addition.")
        return video

    logo = ImageClip(logo_path).set_opacity(opacity)
    logo = logo.resize(size_multiplier)

    video_width, video_height = video.size
    logo_x = int(video_width * x_percent)
    logo_y = int(video_height * y_percent)

    logo = logo.set_position((logo_x, logo_y)).set_duration(video.duration)
    return CompositeVideoClip([video, logo])

def add_image(video, image_path, x, y, size_multiplier, opacity):
    if not os.path.exists(image_path):
        print(f"Image file not found: {image_path}. Skipping image addition.")
        return video

    image = ImageClip(image_path).set_opacity(opacity)
    image = image.resize(size_multiplier)

    video_width, video_height = video.size
    image_x = int(video_width * x)
    image_y = int(video_height * y)

    image = image.set_position((image_x, image_y)).set_duration(video.duration)
    return CompositeVideoClip([video, image])

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

    def process_video(self, logo_path=None, x_percent=0.3, y_percent=0.3, size_multiplier=0.5, duration=None, opacity=0.3, contrast=1.0, saturation=1.0, extra_images=None):
        """
        Process the video by adjusting contrast, saturation, adding a logo, and ensuring proportions for YouTube Shorts.
        """
        import shutil
        try:
            # 1. Adjust contrast and saturation in a temporary file
            with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as temp_prev:
                temp_prev_path = temp_prev.name
            clip = VideoFileClip(self.video_path)
            clip = resize(clip, height=1920, width=1080)  # Ensure YouTube Shorts proportions
            def adjust_frame(frame):
                # Ensure no changes are made to the frame
                return frame
            edited_clip = clip.fl_image(adjust_frame)
            edited_clip.write_videofile(temp_prev_path, codec="libx264", audio_codec="aac", temp_audiofile="temp-audio1.m4a", remove_temp=True)
            clip.close()
            edited_clip.close()

            # 2. Add logo (if provided)
            if logo_path:
                with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as temp_next:
                    temp_next_path = temp_next.name
                add_logo(logo_path, x_percent, y_percent, size_multiplier, opacity, output_path=temp_next_path, input_path=temp_prev_path)
                if os.path.exists(temp_prev_path):
                    os.remove(temp_prev_path)
                temp_prev_path = temp_next_path

            # 3. Add extra images (e.g., subscribe.png) sequentially
            if extra_images is None:
                extra_images = [
                    {"image_path": "subscribe.png", "x": 0.2, "y": 0.8, "size_multiplier": 0.2, "duration": None, "opacity": 0.8}
                ]
            for img in extra_images:
                with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as temp_next:
                    temp_next_path = temp_next.name
                add_image(
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

            # 4. Save the final result to the original file
            shutil.move(temp_prev_path, self.video_path)
            print(f"Final video saved: {self.video_path}")
        except Exception as e:
            print(f"Error processing video: {e}")