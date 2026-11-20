"""PSYOPSNEWS Studio: three-puppet audio-reactive podcast renderer."""
import json
import os
import subprocess
import tempfile
from pathlib import Path

from elevenlabs_tts import choose_voices, synthesize
from puppet_engine import load_portraits, encode_segment

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output"
OUT.mkdir(exist_ok=True)

def run(*args):
    subprocess.run([str(x) for x in args], check=True)

def main():
    chars = json.loads((ROOT / "config/characters.json").read_text(encoding="utf-8"))
    episode = os.environ.get("PSYOPSNEWS_EPISODE", "episodes/podcast_pilot.json")
    episode_path = (ROOT / episode).resolve()
    if ROOT not in episode_path.parents:
        raise ValueError("Episode must be within the repository.")
    dialogue = json.loads(episode_path.read_text(encoding="utf-8"))
    if not isinstance(dialogue,list) or not dialogue:
        raise ValueError("Episode must contain a non-empty JSON list.")
    for index, line in enumerate(dialogue):
        if line.get("speaker") not in chars or not isinstance(line.get("text"),str):
            raise ValueError(f"Invalid dialogue line {index}")
    portraits = load_portraits(ROOT, chars)
    voices = choose_voices()
    with tempfile.TemporaryDirectory() as td:
        work = Path(td)
        segments = []
        for i, line in enumerate(dialogue):
            speaker = line["speaker"]
            audio = work / f"{i:03}.mp3"
            synthesize(line["text"], voices[speaker], audio)
            video = work / f"{i:03}.mp4"
            encode_segment(audio,video,chars,portraits,speaker,line["text"])
            segments.append(video)
            print(f"Rendered {i+1}/{len(dialogue)}: {speaker}",flush=True)
        listing = work / "segments.txt"
        listing.write_text("".join(f"file '{p}'\n" for p in segments), encoding="utf-8")
        final = OUT / "psyopsnews_podcast_pilot.mp4"
        run("ffmpeg","-y","-loglevel","error","-f","concat","-safe","0",
            "-i",listing,"-c","copy",final)
        print("Created:",final)

if __name__ == "__main__":
    main()
