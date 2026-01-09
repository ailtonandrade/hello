from moviepy.editor import VideoFileClip
import cv2
import numpy as np

class VideoEditor:
    def __init__(self, video_path):
        self.video_path = video_path

    def adjust_contrast_and_saturation(self, contrast=1.2, saturation=1.2):
        """
        Adjust the contrast and saturation of the video using OpenCV.

        :param contrast: Multiplier for contrast adjustment.
        :param saturation: Multiplier for saturation adjustment.
        """
        try:
            # Load the video file
            cap = cv2.VideoCapture(self.video_path)
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(self.video_path, fourcc, cap.get(cv2.CAP_PROP_FPS),
                                  (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))))

            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break

                # Convert to HSV to adjust saturation
                hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV).astype(np.float32)
                hsv[..., 1] *= saturation  # Adjust saturation
                hsv[..., 1] = np.clip(hsv[..., 1], 0, 255)

                # Convert back to BGR and adjust contrast
                frame = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)
                frame = np.clip(contrast * frame, 0, 255).astype(np.uint8)

                out.write(frame)

            cap.release()
            out.release()
            print(f"Video edited and saved: {self.video_path}")
        except Exception as e:
            print(f"Error editing video: {e}")

    def add_logo(self, logo_path, x_percent=0.5, y_percent=0.5, size_multiplier=1.0, duration=None):
        """
        Add a logo to the video.

        :param logo_path: Path to the logo image.
        :param x_percent: Horizontal position as a percentage of the video width.
        :param y_percent: Vertical position as a percentage of the video height.
        :param size_multiplier: Multiplier for resizing the logo.
        :param duration: Duration for which the logo should appear (None for entire video).
        """
        try:
            # Load the video file
            cap = cv2.VideoCapture(self.video_path)
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(self.video_path, fourcc, cap.get(cv2.CAP_PROP_FPS),
                                  (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))))

            # Load and resize the logo
            logo = cv2.imread(logo_path, cv2.IMREAD_UNCHANGED)
            logo_height, logo_width = logo.shape[:2]
            logo = cv2.resize(logo, (int(logo_width * size_multiplier), int(logo_height * size_multiplier)))

            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break

                # Calculate logo position
                x_offset = int(x_percent * frame.shape[1])
                y_offset = int(y_percent * frame.shape[0])

                # Overlay the logo on the frame
                for c in range(0, 3):
                    frame[y_offset:y_offset + logo.shape[0], x_offset:x_offset + logo.shape[1], c] = (
                        logo[..., c] * (logo[..., 3] / 255.0) +
                        frame[y_offset:y_offset + logo.shape[0], x_offset:x_offset + logo.shape[1], c] *
                        (1.0 - logo[..., 3] / 255.0)
                    )

                out.write(frame)

            cap.release()
            out.release()
            print(f"Logo added and video saved: {self.video_path}")
        except Exception as e:
            print(f"Error adding logo: {e}")

    def process_video(self, logo_path=None, x_percent=0.5, y_percent=0.5, size_multiplier=1.0, duration=None):
        """
        Process the video by adjusting contrast, saturation, and optionally adding a logo.

        :param logo_path: Path to the logo image (optional).
        :param x_percent: Horizontal position as a percentage of the video width (for logo).
        :param y_percent: Vertical position as a percentage of the video height (for logo).
        :param size_multiplier: Multiplier for resizing the logo.
        :param duration: Duration for which the logo should appear (None for entire video).
        """
        # Adjust contrast and saturation
        self.adjust_contrast_and_saturation()

        # Add logo if logo_path is provided
        if logo_path:
            self.add_logo(logo_path, x_percent, y_percent, size_multiplier, duration)