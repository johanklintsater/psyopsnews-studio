"""PSYOPSNEWS panel pilot: three puppets, no fake mouth overlays."""
import asyncio
import json
import subprocess
import tempfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps
import edge_tts

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"output"
OUT.mkdir(exist_ok=True)
W,H=1280,720
ORDER=["bear","journalist","rock"]
def run(*args):
    subprocess.run([str(x) for x in args],check=True)
def font(size):
    for p in ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf","C:/Windows/Fonts/arialbd.ttf"]:
        if Path(p).exists():return ImageFont.truetype(p,size)
    return ImageFont.load_default()
def frame(chars,speaker,text):
    img=Image.new("RGB",(W,H),(12,16,30))
    d=ImageDraw.Draw(img)
    d.rectangle((0,0,W,88),fill=(24,30,52))
    d.text((38,17),"PSYOPSNEWS  |  TRE IDIOTER OCH EN MIKROFON",font=font(30),fill="white")
    d.text((1120,28),"SATIR",font=font(25),fill=(255,91,94))
    for idx,key in enumerate(ORDER):
        x=38+idx*413
        y=115
        active=key==speaker
        d.rounded_rectangle((x-6,y-6,x+383,y+428),radius=14,fill=(64,38,47) if active else (25,29,43),outline=(255,78,83) if active else (67,73,93),width=6 if active else 2)
        path=ROOT/chars[key]["image"]
        if path.exists():
            person=Image.open(path).convert("RGB")
            person=ImageOps.fit(person,(370,340),method=Image.Resampling.LANCZOS,centering=(0.5,0.35))
            if not active:
                from PIL import ImageEnhance
                person=ImageEnhance.Brightness(person).enhance(0.55)
            img.paste(person,(x,y))
        else:
            d.text((x+25,y+150),"BILD SAKNAS",font=font(24),fill="white")
        d.rectangle((x,y+340,x+370,y+415),fill=(34,37,56))
        d.text((x+12,y+357),chars[key]["name"],font=font(25),fill="white" if active else (165,165,176))
        if active:
            d.ellipse((x+335,y+365,x+355,y+385),fill=(250,70,76))
    d.rectangle((0,575,W,H),fill=(14,21,37))
    d.rectangle((0,575,W,582),fill=(225,52,64))
    # Wrap dialogue without drawing any false mouth onto the portraits.
    words=text.split()
    lines=[];current=""
    for word in words:
        trial=(current+" "+word).strip()
        if d.textbbox((0,0),trial,font=font(28))[2]>1180 and current:
            lines.append(current);current=word
        else:current=trial
    if current:lines.append(current)
    for i,line in enumerate(lines[:3]):
        d.text((44,596+i*36),line,font=font(28),fill="white")
    return img
async def main():
    chars=json.loads((ROOT/"config/characters.json").read_text(encoding="utf-8"))
    dialogue=json.loads((ROOT/"episodes/podcast_pilot.json").read_text(encoding="utf-8"))
    with tempfile.TemporaryDirectory() as td:
        work=Path(td)
        segments=[]
        for i,line in enumerate(dialogue):
            speaker=line["speaker"]
            audio=work/f"{i:03}.mp3"
            await edge_tts.Communicate(line["text"],chars[speaker]["voice"]).save(str(audio))
            still=work/f"{i:03}.png"
            frame(chars,speaker,line["text"]).save(still)
            video=work/f"{i:03}.mp4"
            run("ffmpeg","-y","-loglevel","error","-loop","1","-framerate","12","-i",still,"-i",audio,"-c:v","libx264","-preset","veryfast","-tune","stillimage","-pix_fmt","yuv420p","-c:a","aac","-b:a","160k","-ar","44100","-ac","2","-shortest","-movflags","+faststart",video)
            segments.append(video)
        listing=work/"segments.txt"
        listing.write_text("".join(f"file '{p}'\n" for p in segments),encoding="utf-8")
        final=OUT/"psyopsnews_podcast_pilot.mp4"
        run("ffmpeg","-y","-loglevel","error","-f","concat","-safe","0","-i",listing,"-c","copy",final)
        print("Created:",final)
if __name__=="__main__":asyncio.run(main())
