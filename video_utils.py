from moviepy.editor import concatenate_videoclips

def create_video_with_clips(video_clips, duration):
    """Concatenate video clips and trim to the specified duration."""
    return concatenate_videoclips(video_clips).subclip(0, duration)

def save_final_video(video, output_path, audio_path):
    """Save the final video with the specified audio."""
    video.write_videofile(output_path, codec="libx264", audio=audio_path, fps=24)
    print(f"Final video saved to {output_path}")