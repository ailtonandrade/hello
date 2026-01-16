"""
config.py - Configurações do sistema
"""

import json
import os

class Config:
    def __init__(self, config_file="config.json"):
        self.config_file = config_file
        self.default_config = {
            "channel": "parallelcuts",
            "theme": "pregacao",
            "max_cpu_percent": 40,
            "enable_memory_optimization": True,
            "voice_settings": {
                "name": "pm_santa",
                "speed": 0.6,
                "pitch": 1.0,
                "volume": 1.0
            },
            "video_settings": {
                "subtitle_words_per_line": 6,
                "subtitle_one_word_at_a_time": False,
                "subtitle_font_size": 70,
                "video_style": "simple",
                "screen_orientation": "MOBILE"
            }
        }
        self.config = self.load_config()
    
    def load_config(self):
        """Carrega configurações do arquivo ou usa padrão."""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️ Erro ao carregar configurações: {e}")
        
        return self.default_config
    
    def save_config(self):
        """Salva configurações no arquivo."""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            print(f"✅ Configurações salvas: {self.config_file}")
        except Exception as e:
            print(f"❌ Erro ao salvar configurações: {e}")
    
    def update_config(self, section, key, value):
        """Atualiza uma configuração específica."""
        if section in self.config:
            self.config[section][key] = value
        else:
            self.config[section] = {key: value}
        
        self.save_config()
    
    def get(self, section, key, default=None):
        """Obtém uma configuração."""
        return self.config.get(section, {}).get(key, default)

# Instância global
config = Config()

# Atalhos para configurações comuns
CHANNEL = config.get("", "channel", "parallelcuts")
THEME = config.get("", "theme", "pregacao")
MAX_PERCENT_USAGE_CPU = config.get("", "max_cpu_percent", 40)
ENABLE_MEMORY_OPTIMIZATION = config.get("", "enable_memory_optimization", True)

# Configurações de voz
VOICE_NAME = config.get("voice_settings", "name", "pm_santa")
VOICE_SPEED = config.get("voice_settings", "speed", 1.0)
VOICE_PITCH = config.get("voice_settings", "pitch", 1.0)
VOICE_VOLUME = config.get("voice_settings", "volume", 1.0)

# Configurações de vídeo
SUBTITLE_WORDS_PER_LINE = config.get("video_settings", "subtitle_words_per_line", 6)
SUBTITLE_ONE_WORD_AT_A_TIME = config.get("video_settings", "subtitle_one_word_at_a_time", False)
SUBTITLE_FONT_SIZE = config.get("video_settings", "subtitle_font_size", 70)
VIDEO_STYLE = config.get("video_settings", "video_style", "simple")
SCREEN_ORIENTATION = config.get("video_settings", "screen_orientation", "MOBILE")