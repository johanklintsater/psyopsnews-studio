"""PSYOPSNEWS v0.2: Swedish TTS, stylized mouth motion, studio and intro.
Requires: edge-tts, pillow, ffmpeg, ffprobe.
Dialects are script cues, not guaranteed authentic regional speech.
"""
import asyncio
import json
import math
import subprocess
import tempfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import edge_tts

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output"
OUT.mkdir(exist_ok=True)
W,H,FPS = 1280,720,12
def cmd(*args):
    subprocess.run(list(args), check=True)
def font(size):
    for p in ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf","C:/Windows/Fonts/arialbd.ttf"]:
        if Path(p).exists(): return ImageFont.truetype(p,size)
    return ImageFont.load_default()
def base(character):
    bg=Image.new("RGB",(W,H),(12,17,31))
    d=ImageDraw.Draw(bg)
    for x in range(0,W,80): d.line((x,0,x,H),fill=(20,32,55),width=2)
    d.rectangle((0,0,W,90),fill=(9,12,25))
    d.text((42,20),"PSYOPSNEWS 24/7",font=font(46),fill=(242,242,246))
    d.text((970,31),"SATIR",font=font(30),fill=(255,76,79))
    d.rectangle((0,610,W,H),fill=(12,22,42))
    d.rectangle((0,610,W,620),fill=(204,39,50))
    d.text((40,636),character["name"].upper()+"  •  "+character["dialect"].upper(),font=font(29),fill="white")
    p=ROOT/character["image"]
    if p.exists():
        person=Image.open(p).convert("RGB")
        person.thumbnail((730,500))
        bg.paste(person,((W-person.width)//2,104))
        # Mouth overlay is deliberately simple, not accurate phoneme lip-sync.
        center=((W-person.width)//2+int(person.width*character["mouth"][0]),
                104+int(person.height*character["mouth"][1]))
    else:
        d=ImageDraw.Draw(bg)
        d.ellipse((460,145,820,545),fill=(192,146,105))
        d.ellipse((548,295,575,318),fill=(15,15,20))
        d.ellipse((704,295,731,318),fill=(15,15,20))
        center=(640,420)
        d.text((430,540),"UPLOAD "+character["image"],font=font(21),fill="white")
    return bg,center
def duration(path):
    r=subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","default=noprint_wrappers=1:nokey=1",str(path)],capture_output=True,text=True,check=True)
    return float(r.stdout.strip())
def render_scene(character,audio,dest):
    bg,center=base(character)
    seconds=duration(audio)
    # Get audio amplitude in 100ms chunks, drives mouth openness.
    pcm=subprocess.run(["ffmpeg","-v","error","-i",str(audio),"-ac","1","-ar","12000","-f","s16le","-"],capture_output=True,check=True).stdout
    import array
    samples=array.array("h");samples.frombytes(pcm[:len(pcm)//2*2])
    with tempfile.TemporaryDirectory() as tmp:
        folder=Path(tmp)
        for i in range(max(1,math.ceil(seconds*FPS))):
            frame=bg.copy();d=ImageDraw.Draw(frame)
            start=int(i/FPS*12000);window=samples[start:start+1000]
            amp=(sum(abs(v) for v in window)/max(1,len(window)))/32768
            opening=int(3+min(1,amp*13)*28)
            x,y=center
            d.ellipse((x-31,y-5,x+31,y+opening),fill=(34,8,15),outline=(110,48,42),width=3)
            frame.save(folder/f"{i:05d}.jpg",quality=84)
        cmd("ffmpeg","-y","-loglevel","error","-framerate",str(FPS),"-i",str(folder/"%05d.jpg"),"-i",str(audio),"-c:v","libx264","-preset","veryfast","-pix_fmt","yuv420p","-c:a","aac","-b:a","160k","-shortest",str(dest))
async def main():
    chars=json.loads((ROOT/"config/characters.json").read_text(encoding="utf-8"))
    lines=json.loads((ROOT/"episodes/ep01_dialogue.json").read_text(encoding="utf-8"))
    segments=[]
    with tempfile.TemporaryDirectory() as tmp:
        work=Path(tmp)
        for n,line in enumerate(lines):
            char=chars[line["speaker"]]
            audio=work/f"{n:02}.mp3"
            await edge_tts.Communicate(line["text"],char["voice"]).save(str(audio))
            video=work/f"{n:02}.mp4"
            render_scene(char,audio,video)
            segments.append(video)
        listing=work/"segments.txt"
        listing.write_text("".join("file '"+str(p)+"'\n" for p in segments),encoding="utf-8")
        joined=work/"joined.mp4"
        cmd("ffmpeg","-y","-loglevel","error","-f","concat","-safe","0","-i",str(listing),"-c","copy",str(joined))
        # Intro slate + synthesized sting (original tone, not copyrighted music)
        intro=work/"intro.mp4"
        cmd("ffmpeg","-y","-loglevel","error","-f","lavfi","-i","color=c=0x0a1020:s=1280x720:r=12:d=2","-f","lavfi","-i","sine=frequency=110:duration=2","-vf","drawtext=text='PSYOPSNEWS 24/7 - SATIR':fontcolor=white:fontsize=52:x=(w-text_w)/2:y=(h-text_h)/2","-c:v","libx264","-pix_fmt","yuv420p","-c:a","aac","-shortest",str(intro))
        final=OUT/"psyopsnews_ep01_v02.mp4"
        cmd("ffmpeg","-y","-loglevel","error","-i",str(intro),"-i",str(joined),"-filter_complex","[0:v][0:a][1:v][1:a]concat=n=2:v=1:a=1[v][a]","-map","[v]","-map","[a]","-c:v","libx264","-preset","veryfast","-pix_fmt","yuv420p","-c:a","aac",str(final))
        print("Created:",final)
if __name__=="__main__": asyncio.run(main())
