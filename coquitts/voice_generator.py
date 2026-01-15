from __future__ import annotations  # Enables support for `|` type hints in Python 3.9
import os
import sys

# Add the local TTS repository to the Python path
sys.path.insert(0, "c:\\Users\\TOM\\DEVELOPER\\python\\hello\\TTS-local-dev")

from TTS.api import TTS  # Import after setting the path

def generate_voice(model_name, text, output_path, speaker_wav, language):
    try:
        # Initialize TTS model
        tts = TTS(model_name).to("cpu")

        # Generate and save the audio with voice cloning
        tts.tts_to_file(text=text, file_path=output_path, speaker_wav=speaker_wav, language=language)
        print(f"Voice generated and saved to {output_path}")
    except Exception as e:
        print(f"Error generating voice: {e}")

if __name__ == "__main__":
    selected_model = "tts_models/multilingual/multi-dataset/your_tts"
    speaker_audio = "my_voice.mp3"
    language_code = "pt-br"
    sample_text = "Viaje com bastante espaço. Dê um upgrade nas suas viagens diárias com mais espaço interno. Usufrua de um espaço ainda maior para se esticar com conforto. "
    output_file = "output_voice_pt_cv_vits.wav"
    
    generate_voice(selected_model, sample_text, output_file, speaker_audio, language_code)
    