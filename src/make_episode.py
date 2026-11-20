"""Create MP4 from an image and a narration audio file using FFmpeg."""
import argparse
import subprocess
from pathlib import Path

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", required=True)
    parser.add_argument("--audio", required=True)
    parser.add_argument("--out", default="episode.mp4")
    args = parser.parse_args()
    for value in (args.image, args.audio):
        if not Path(value).is_file():
            parser.error(f"Missing input: {value}")
    cmd = ["ffmpeg", "-y", "-loop", "1", "-framerate", "25",
           "-i", args.image, "-i", args.audio,
           "-vf", "scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2,format=yuv420p",
           "-c:v", "libx264", "-tune", "stillimage", "-c:a", "aac",
           "-b:a", "192k", "-shortest", "-movflags", "+faststart", args.out]
    subprocess.run(cmd, check=True)
    print("Created:", args.out)

if __name__ == "__main__":
    main()
