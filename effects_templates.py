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