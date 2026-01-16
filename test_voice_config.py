#!/usr/bin/env python3
"""
Voice Configuration Test Script
Demonstrates the new voice customization features
"""

from voice_generator import VoiceGenerator
import os

def test_voice_configurations():
    """Test different voice configurations"""

    # Test configurations
    configs = [
        {"speed": 0.8, "pitch": 0.9, "volume": 1.0, "desc": "Slow, deep voice"},
        {"speed": 1.2, "pitch": 1.1, "volume": 1.2, "desc": "Fast, high-pitched voice"},
        {"speed": 1.0, "pitch": 1.0, "volume": 0.8, "desc": "Normal speed, quiet voice"},
        {"speed": 1.5, "pitch": 0.8, "volume": 1.5, "desc": "Very fast, low-pitched, loud voice"}
    ]

    test_text = "This is a demonstration of voice configuration features."

    print("Voice Configuration Test")
    print("=" * 50)

    for i, config in enumerate(configs, 1):
        print(f"\nTest {i}: {config['desc']}")
        print(f"Speed: {config['speed']}x, Pitch: {config['pitch']}x, Volume: {config['volume']}x")

        # Create voice generator with specific config
        voice_gen = VoiceGenerator(
            speed=config['speed'],
            pitch=config['pitch'],
            volume=config['volume']
        )

        # Generate audio
        filename = f"test_voice_{i}.wav"
        try:
            audio_path = voice_gen.generate_audio(test_text, filename)
            if os.path.exists(audio_path):
                file_size = os.path.getsize(audio_path)
                print(f"✓ Audio generated successfully: {filename} ({file_size} bytes)")
            else:
                print(f"✗ Audio file not created: {filename}")
        except Exception as e:
            print(f"✗ Error generating audio: {e}")

def test_voice_methods():
    """Test the new utility methods"""

    print("\n\nVoice Methods Test")
    print("=" * 50)

    voice_gen = VoiceGenerator()

    # Test get_available_voices
    print("\nTesting get_available_voices():")
    try:
        voices = voice_gen.get_available_voices()
        print(f"Found {len(voices)} available voices")
        if voices:
            print(f"Sample voices: {voices[:3]}")
    except Exception as e:
        print(f"Error getting voices: {e}")

    # Test set_voice_config
    print("\nTesting set_voice_config():")
    try:
        voice_gen.set_voice_config(speed=1.3, pitch=0.95, volume=1.1)
        print(f"Configuration set - Speed: {voice_gen.speed}, Pitch: {voice_gen.pitch}, Volume: {voice_gen.volume}")
    except Exception as e:
        print(f"Error setting config: {e}")

    # Test test_voice
    print("\nTesting test_voice():")
    try:
        result = voice_gen.test_voice("Hello world!")
        if result:
            print("✓ Voice test successful")
        else:
            print("✗ Voice test failed")
    except Exception as e:
        print(f"Error testing voice: {e}")

if __name__ == "__main__":
    test_voice_configurations()
    test_voice_methods()

    # Clean up test files
    print("\nCleaning up test files...")
    for i in range(1, 5):
        filename = f"test_voice_{i}.wav"
        if os.path.exists(filename):
            os.remove(filename)
            print(f"Removed {filename}")

    print("\nTest completed!")