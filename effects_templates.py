"""
📦 TEMPLATES DE EFEITOS PARA MOVIEPY
Efeitos prontos para usar em seus vídeos - como um canivete suíço de edição!

🎨 Tipos de templates:
1. Transições entre cenas
2. Efeitos de texto animados
3. Overlays e filtros
4. Animações de entrada/saída
"""

import numpy as np
from moviepy.editor import *
from PIL import Image, ImageDraw, ImageFont
import os

class VideoEffects:
    def __init__(self):
        self.screen_orientation = "MOBILE"
    
    def get_video_size(self):
        """Retorna tamanho do vídeo baseado na orientação."""
        return (1080, 1920) if self.screen_orientation == "MOBILE" else (1920, 1080)
    
    # ============================================================================
    # 🎬 TEMPLATES DE TRANSIÇÃO ENTRE CENAS
    # ============================================================================
    
    def transition_fade(self, clip1, clip2, duration=1.0):
        """
        Transição suave de fade entre dois clips.
        
        Args:
            clip1: Clip que está saindo
            clip2: Clip que está entrando
            duration: Duração da transição em segundos
            
        Returns:
            CompositeVideoClip com a transição
        """
        return CompositeVideoClip([
            clip1.set_start(0),
            clip2.set_start(clip1.duration - duration).crossfadein(duration)
        ])
    
    def transition_slide(self, clip1, clip2, direction="right", duration=1.0):
        """
        Transição de slide (deslizamento).
        
        Args:
            clip1: Clip atual
            clip2: Próximo clip
            direction: 'right', 'left', 'up', 'down'
            duration: Duração da transição
            
        Returns:
            CompositeVideoClip com slide
        """
        w, h = self.get_video_size()
        
        # Posições baseadas na direção
        if direction == "right":
            positions = lambda t: (int(-w * t/duration), 0) if t < duration else (0, 0)
        elif direction == "left":
            positions = lambda t: (int(w * t/duration), 0) if t < duration else (0, 0)
        elif direction == "up":
            positions = lambda t: (0, int(h * t/duration)) if t < duration else (0, 0)
        else:  # down
            positions = lambda t: (0, int(-h * t/duration)) if t < duration else (0, 0)
        
        # Criar composição
        clip2_with_position = clip2.set_position(positions).set_start(clip1.duration - duration)
        
        return CompositeVideoClip([
            clip1.set_start(0),
            clip2_with_position
        ]).subclip(0, clip1.duration + clip2.duration)
    
    def transition_zoom(self, clip1, clip2, zoom_factor=1.5, duration=1.0):
        """
        Transição com zoom no final do clip1 e zoom out no início do clip2.
        
        Args:
            clip1: Clip atual
            clip2: Próximo clip
            zoom_factor: Fator de zoom (ex: 1.5 = 150%)
            duration: Duração da transição
            
        Returns:
            CompositeVideoClip com efeito de zoom
        """
        # Clip1 faz zoom in
        clip1_zoomed = clip1.fl_time(lambda t: t)
        clip1_zoomed = clip1_zoomed.resize(lambda t: 1 + (zoom_factor - 1) * t / duration)
        
        # Clip2 começa com zoom out
        clip2_zoomed = clip2.fl_time(lambda t: t)
        clip2_zoomed = clip2_zoomed.resize(lambda t: zoom_factor - (zoom_factor - 1) * t / duration)
        
        return concatenate_videoclips([
            clip1_zoomed.subclip(0, clip1.duration),
            clip2_zoomed.set_start(clip1.duration - duration)
        ])
    
    # ============================================================================
    # ✨ TEMPLATES DE TEXTO ANIMADO
    # ============================================================================
    
    def text_template_typing(self, text, duration=3.0, font_size=60, font_color="white", 
                            bg_color=None, position=("center", "center")):
        """
        Efeito de texto sendo digitado (typewriter).
        
        Args:
            text: Texto a ser exibido
            duration: Duração total da animação
            font_size: Tamanho da fonte
            font_color: Cor do texto
            bg_color: Cor do fundo (None = transparente)
            position: Posição (x, y) ou ('center', 'center')
            
        Returns:
            TextClip com efeito de digitação
        """
        # Criar texto com efeito de digitação
        fps = 24
        total_frames = int(duration * fps)
        
        # Determinar velocidade de digitação
        chars_per_second = len(text) / duration
        
        frames = []
        for i in range(total_frames):
            t = i / fps
            chars_to_show = min(len(text), int(t * chars_per_second))
            partial_text = text[:chars_to_show] + "█"  # Cursor piscando
            
            # Criar imagem do texto
            img = Image.new("RGBA", self.get_video_size(), color=(0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            
            try:
                font = ImageFont.truetype("lilita.ttf", font_size)
            except:
                font = ImageFont.load_default()
            
            # Centralizar texto
            text_bbox = draw.textbbox((0, 0), partial_text, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
            
            x = (self.get_video_size()[0] - text_width) // 2
            y = (self.get_video_size()[1] - text_height) // 2
            
            if bg_color:
                # Adicionar fundo
                padding = 20
                draw.rectangle(
                    [x-padding, y-padding, x+text_width+padding, y+text_height+padding],
                    fill=bg_color
                )
            
            draw.text((x, y), partial_text, fill=font_color, font=font)
            
            # Converter para numpy array
            frames.append(np.array(img))
        
        return ImageSequenceClip(frames, fps=fps)
    
    def text_template_fade_in_out(self, text, duration=5.0, font_size=60, font_color="white", 
                                    position=("center", "center")):
            """Cria texto SEM ImageMagick usando PIL."""

            
            # Cria imagem com texto
            width, height = self.get_video_size()
            img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            
            try:
                font = ImageFont.truetype("lilita.ttf", font_size)
            except:
                font = ImageFont.load_default()
            
            # Calcula posição
            if position[0] == "center":
                # Centraliza
                text_bbox = draw.textbbox((0, 0), text, font=font)
                text_width = text_bbox[2] - text_bbox[0]
                text_height = text_bbox[3] - text_bbox[1]
                x = (width - text_width) // 2
                y = (height - text_height) // 2
            else:
                x, y = position
            
            # Desenha texto
            draw.text((x, y), text, fill=font_color, font=font)
            
            # Converte para array numpy
            img_array = np.array(img)
            
            # Cria ImageClip
            text_clip = ImageClip(img_array, transparent=True).set_duration(duration)
            
            # ADICIONE ESTA PARTE PARA FADE IN/OUT
            fade_duration = 0.5  # 0.5 segundos para fade
            text_clip = text_clip.crossfadein(fade_duration).crossfadeout(fade_duration)
            
            return text_clip
    
    def text_template_glitch(self, text, duration=3.0, font_size=60, font_color="white", 
                            intensity=0.1, position=("center", "center")):
        """
        Efeito de texto glitch (distorção digital).
        
        Args:
            text: Texto a ser exibido
            duration: Duração total
            font_size: Tamanho da fonte
            font_color: Cor do texto
            intensity: Intensidade do glitch (0.0 a 1.0)
            position: Posição
            
        Returns:
            TextClip com efeito glitch
        """
        fps = 24
        frames_needed = int(duration * fps)
        
        # Criar frames com efeito glitch
        frames = []
        for i in range(frames_needed):
            img = Image.new("RGBA", self.get_video_size(), color=(0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            
            try:
                font = ImageFont.truetype("lilita.ttf", font_size)
            except:
                font = ImageFont.load_default()
            
            # Aplicar offset aleatório para efeito glitch
            glitch_x = int(np.random.normal(0, intensity * 10))
            glitch_y = int(np.random.normal(0, intensity * 5))
            
            # Desenhar texto com cores aleatórias para alguns pixels
            text_bbox = draw.textbbox((0, 0), text, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
            
            x = (self.get_video_size()[0] - text_width) // 2 + glitch_x
            y = (self.get_video_size()[1] - text_height) // 2 + glitch_y
            
            # Texto principal
            draw.text((x, y), text, fill=font_color, font=font)
            
            # Adicionar "fantasma" do texto com cor diferente para efeito glitch
            if np.random.random() < intensity:
                ghost_color = "#00FFFF" if np.random.random() > 0.5 else "#FF00FF"
                ghost_x = x + np.random.randint(-5, 5)
                ghost_y = y + np.random.randint(-3, 3)
                draw.text((ghost_x, ghost_y), text, fill=ghost_color, font=font, alpha=0.3)
            
            frames.append(np.array(img))
        
        return ImageSequenceClip(frames, fps=fps)
    
    # ============================================================================
    # 🎨 TEMPLATES DE OVERLAYS E FILTROS
    # ============================================================================
    
    def overlay_vignette(self, clip, intensity=0.7):
        """
        Adiciona efeito vinheta (escurecimento nas bordas).
        
        Args:
            clip: Clip de vídeo
            intensity: Intensidade do efeito (0.0 a 1.0)
            
        Returns:
            Clip com vinheta
        """
        w, h = clip.size
        
        # Criar máscara de vinheta
        X, Y = np.ogrid[:h, :w]
        mask = 1.0 - intensity * np.sqrt((X - h/2.0)**2 + (Y - w/2.0)**2) / np.sqrt((h/2.0)**2 + (w/2.0)**2)
        mask = np.maximum(mask, 0)
        mask = np.dstack([mask, mask, mask])  # RGB
        
        # Aplicar máscara
        vignette_clip = clip.fl_image(lambda frame: (frame * mask).astype('uint8'))
        
        return vignette_clip
    
    def overlay_film_grain(self, clip, intensity=0.05):
        """
        Adiciona grão de filme (film grain).
        
        Args:
            clip: Clip de vídeo
            intensity: Intensidade do grão (0.0 a 0.2)
            
        Returns:
            Clip com grão de filme
        """
        def add_grain(get_frame, t):
            frame = get_frame(t)
            # Adicionar ruído aleatório
            grain = np.random.normal(0, intensity * 255, frame.shape).astype('int16')
            result = np.clip(frame.astype('int16') + grain, 0, 255).astype('uint8')
            return result
        
        return clip.fl(add_grain)
    
    def overlay_color_filter(self, clip, filter_type="sepia", intensity=0.7):
        """
        Aplica filtro de cor ao vídeo.
        
        Args:
            clip: Clip de vídeo
            filter_type: Tipo de filtro ('sepia', 'grayscale', 'vintage', 'cool', 'warm')
            intensity: Intensidade do filtro (0.0 a 1.0)
            
        Returns:
            Clip com filtro aplicado
        """
        def apply_filter(get_frame, t):
            frame = get_frame(t).astype('float32')
            
            if filter_type == "sepia":
                # Matriz de transformação sepia
                sepia_filter = np.array([
                    [0.393, 0.769, 0.189],
                    [0.349, 0.686, 0.168],
                    [0.272, 0.534, 0.131]
                ])
                filtered = frame.dot(sepia_filter.T)
                
            elif filter_type == "grayscale":
                # Converter para escala de cinza
                gray = np.dot(frame[..., :3], [0.2989, 0.5870, 0.1140])
                filtered = np.stack([gray, gray, gray], axis=-1)
                
            elif filter_type == "vintage":
                # Filtro vintage (amarelado)
                filtered = frame * np.array([1.1, 1.0, 0.9])
                # Adicionar vinheta
                h, w = filtered.shape[:2]
                X, Y = np.ogrid[:h, :w]
                vignette = 1.0 - 0.6 * np.sqrt((X - h/2.0)**2 + (Y - w/2.0)**2) / np.sqrt((h/2.0)**2 + (w/2.0)**2)
                vignette = np.maximum(vignette, 0.3)
                filtered = filtered * vignette[..., np.newaxis]
                
            elif filter_type == "cool":
                # Filtro frio (azulado)
                filtered = frame * np.array([0.9, 1.0, 1.1])
                
            elif filter_type == "warm":
                # Filtro quente (avermelhado)
                filtered = frame * np.array([1.1, 1.0, 0.9])
                
            else:
                filtered = frame
            
            # Misturar com original baseado na intensidade
            result = (1 - intensity) * frame + intensity * filtered
            return np.clip(result, 0, 255).astype('uint8')
        
        return clip.fl(apply_filter)
    
    # ============================================================================
    # 🎭 TEMPLATES DE ANIMAÇÃO DE ENTRADA/SAÍDA
    # ============================================================================
    
    def animation_bounce_in(self, clip, direction="bottom", duration=0.5):
        """
        Animação de entrada com "bounce" (quicando).
        
        Args:
            clip: Clip a ser animado
            direction: Direção de entrada ('top', 'bottom', 'left', 'right')
            duration: Duração da animação
            
        Returns:
            Clip com animação
        """
        w, h = clip.size
        
        if direction == "top":
            start_pos = (0, -h)
        elif direction == "bottom":
            start_pos = (0, h)
        elif direction == "left":
            start_pos = (-w, 0)
        else:  # right
            start_pos = (w, 0)
        
        # Função de posição com bounce
        def bounce_position(t):
            if t < duration:
                # Fórmula de bounce
                progress = t / duration
                bounce = np.sin(progress * np.pi * 3) * np.exp(-progress * 3)
                
                if direction in ["top", "bottom"]:
                    y_offset = start_pos[1] * (1 - progress) + bounce * 50
                    return (0, int(y_offset))
                else:
                    x_offset = start_pos[0] * (1 - progress) + bounce * 50
                    return (int(x_offset), 0)
            else:
                return (0, 0)
        
        return clip.set_position(bounce_position)
    
    def animation_zoom_in(self, clip, start_scale=0.3, duration=0.5):
        """
        Animação de entrada com zoom in.
        
        Args:
            clip: Clip a ser animado
            start_scale: Escala inicial (ex: 0.3 = 30% do tamanho)
            duration: Duração da animação
            
        Returns:
            Clip com animação de zoom
        """
        def zoom_effect(get_frame, t):
            if t < duration:
                progress = t / duration
                # Suavizar com ease-out
                scale = start_scale + (1 - start_scale) * (1 - (1 - progress)**3)
            else:
                scale = 1.0
            
            frame = get_frame(t)
            h, w = frame.shape[:2]
            
            # Calcular novo tamanho
            new_h, new_w = int(h * scale), int(w * scale)
            
            # Redimensionar
            if new_h > 0 and new_w > 0:
                from PIL import Image
                img = Image.fromarray(frame)
                img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
                
                # Centralizar na tela
                result = Image.new("RGB", (w, h), (0, 0, 0))
                paste_x = (w - new_w) // 2
                paste_y = (h - new_h) // 2
                result.paste(img, (paste_x, paste_y))
                
                return np.array(result)
            else:
                return frame
        
        return clip.fl(zoom_effect)
    
    # ============================================================================
    # 🎵 TEMPLATES DE EFEITOS DE ÁUDIO
    # ============================================================================
    
    def audio_fade_in_out(self, audio_clip, fade_duration=1.0):
        """
        Adiciona fade in e fade out ao áudio.
        
        Args:
            audio_clip: Clip de áudio
            fade_duration: Duração do fade em segundos
            
        Returns:
            AudioClip com fade
        """
        return audio_clip.audio_fadein(fade_duration).audio_fadeout(fade_duration)
    
    def audio_echo(self, audio_clip, delay=0.3, decay=0.5):
        """
        Adiciona efeito de eco ao áudio.
        
        Args:
            audio_clip: Clip de áudio
            delay: Atraso do eco em segundos
            decay: Quanto o eco decai (0.0 a 1.0)
            
        Returns:
            AudioClip com eco
        """
        # Criar cópia atrasada
        delayed = audio_clip.set_start(delay).volumex(decay)
        
        # Misturar com original
        return CompositeAudioClip([audio_clip, delayed])
    
    # ============================================================================
    # 🚀 TEMPLATES PRONTOS PARA USO (COMBINAÇÕES)
    # ============================================================================
    
    def template_instagram_story(self, video_clip, text="", music_path=None):
        """
        Template completo para Instagram Stories.
        
        Args:
            video_clip: Clip de vídeo
            text: Texto para overlay
            music_path: Caminho para música de fundo
            
        Returns:
            Clip pronto para Instagram
        """
        # 1. Aplicar filtro vintage
        clip = self.overlay_color_filter(video_clip, "vintage", 0.3)
        
        # 2. Adicionar vinheta
        clip = self.overlay_vignette(clip, 0.4)
        
        # 3. Adicionar texto com animação
        if text:
            text_clip = self.text_template_fade_in_out(
                text, 
                duration=video_clip.duration,
                font_size=70,
                font_color="white",
                position=("center", 0.8)  # Parte inferior
            )
            clip = CompositeVideoClip([clip, text_clip])
        
        # 4. Adicionar música se fornecida
        if music_path and os.path.exists(music_path):
            music = AudioFileClip(music_path)
            # Ajustar duração da música
            if music.duration > clip.duration:
                music = music.subclip(0, clip.duration)
            else:
                music = music.loop(duration=clip.duration)
            
            # Adicionar fade à música
            music = self.audio_fade_in_out(music, 1.0)
            clip = clip.set_audio(music)
        
        return clip
    
    def template_tiktok_video(self, video_clip, caption="", effect="zoom"):
        """
        Template para vídeos estilo TikTok.
        
        Args:
            video_clip: Clip de vídeo
            caption: Legenda/caption
            effect: Efeito principal ('zoom', 'bounce', 'glitch')
            
        Returns:
            Clip estilo TikTok
        """
        # Aplicar efeito escolhido
        if effect == "zoom":
            clip = self.animation_zoom_in(video_clip, start_scale=0.8, duration=0.3)
        elif effect == "bounce":
            clip = self.animation_bounce_in(video_clip, direction="bottom", duration=0.5)
        elif effect == "glitch" and caption:
            # Adicionar texto com glitch
            text_clip = self.text_template_glitch(
                caption,
                duration=video_clip.duration,
                font_size=50,
                font_color="#00FFFF",
                intensity=0.2
            )
            clip = CompositeVideoClip([video_clip, text_clip])
        else:
            clip = video_clip
        
        # Adicionar vinheta leve
        clip = self.overlay_vignette(clip, 0.2)
        
        # Adicionar grão de filme sutil
        clip = self.overlay_film_grain(clip, 0.02)
        
        return clip
    
    def template_cinematic(self, video_clip, title="", subtitle=""):
        """
        Template para vídeos com estilo cinematográfico.
        
        Args:
            video_clip: Clip de vídeo
            title: Título principal
            subtitle: Subtítulo
            
        Returns:
            Clip com estilo cinematográfico
        """
        # 1. Aplicar filtro cinematográfico (cinza com toque azul)
        clip = self.overlay_color_filter(video_clip, "cool", 0.4)
        
        # 2. Vinheta forte
        clip = self.overlay_vignette(clip, 0.6)
        
        # 3. Adicionar título e subtítulo
        clips = [clip]
        
        if title:
            title_clip = self.text_template_fade_in_out(
                title,
                duration=min(4, video_clip.duration),
                font_size=80,
                font_color="white",
                position=("center", "center")
            )
            clips.append(title_clip)
        
        if subtitle:
            subtitle_clip = self.text_template_fade_in_out(
                subtitle,
                duration=min(3, video_clip.duration),
                font_size=50,
                font_color="#AAAAAA",
                position=("center", 0.65)  # Abaixo do título
            ).set_start(0.5 if title else 0)  # Delay se tiver título
            clips.append(subtitle_clip)
        
        if len(clips) > 1:
            clip = CompositeVideoClip(clips)
        
        return clip