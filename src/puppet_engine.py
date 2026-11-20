"""Audio-reactive puppet animation: photo-preserving jaw warp, head movement and cuts.

No synthetic mouth is drawn. The mouth region is a feather-blended deformation of
the original portrait; exact coordinates can be calibrated in config/characters.json.
"""
import math
import subprocess
from array import array
from pathlib import Path
from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps

WIDTH, HEIGHT = 1280, 720
ORDER = ("bear", "journalist", "rock")
FPS = 12
PANEL_W, PANEL_H = 370, 340

def font(size):
    for path in ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "C:/Windows/Fonts/arialbd.ttf"):
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()

def amplitudes(audio_path):
    """Decode to mono PCM, returning 12 RMS envelopes per second."""
    proc = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(audio_path), "-f", "s16le",
         "-ac", "1", "-ar", "12000", "-"],
        capture_output=True, check=True
    )
    samples = array("h")
    samples.frombytes(proc.stdout)
    import sys
    if sys.byteorder != "little":
        samples.byteswap()
    block = 12000 // FPS
    values = []
    for pos in range(0, len(samples), block):
        chunk = samples[pos:pos+block]
        if not chunk:
            break
        energy = math.sqrt(sum(float(x)*x for x in chunk) / len(chunk)) / 32768.0
        values.append(energy)
    peak = sorted(values)[int(len(values)*0.94)] if values else 0
    peak = max(peak, 0.018)
    return [min(1.0, max(0.0, (v/peak-0.10)/0.90)) for v in values]

def load_portraits(root, chars):
    portraits = {}
    for key in ORDER:
        path = root / chars[key]["image"]
        if not path.is_file():
            raise FileNotFoundError(f"Missing puppet portrait: {path}")
        with Image.open(path) as original:
            portraits[key] = ImageOps.fit(
                original.convert("RGB"), (PANEL_W, PANEL_H),
                method=Image.Resampling.LANCZOS, centering=(0.5, 0.35)
            )
    return portraits

def jaw_warp(portrait, mouth, amount):
    """Feathered local lower-jaw movement, using only pixels from the photo."""
    if amount < 0.07:
        return portrait
    w, h = portrait.size
    mx = int(float(mouth[0])*w)
    my = int(float(mouth[1])*h)
    # Narrow region avoids distorting the whole head; can be tuned per puppet.
    radius_x = max(22, int(w*0.13))
    radius_y = max(17, int(h*0.09))
    left, top = max(0, mx-radius_x), max(0, my-radius_y)
    right, bottom = min(w, mx+radius_x), min(h, my+radius_y)
    if right-left < 8 or bottom-top < 8:
        return portrait
    patch = portrait.crop((left,top,right,bottom))
    pw, ph = patch.size
    # Pull the lower half down from the same source pixels.
    shift = min(11, max(1, int(amount*11)))
    split = ph//2
    upper = patch.crop((0,0,pw,split))
    lower = patch.crop((0,split,pw,ph))
    stretched = lower.resize((pw,ph-split+shift), Image.Resampling.BICUBIC)
    modified = Image.new("RGB", (pw,ph))
    modified.paste(upper,(0,0))
    modified.paste(stretched.crop((0,0,pw,ph-split)),(0,split))
    # Elliptical soft mask hides hard rectangular edges.
    mask = Image.new("L", (pw,ph),0)
    md = ImageDraw.Draw(mask)
    md.ellipse((4,3,pw-4,ph-3),fill=200)
    mask = mask.filter(ImageFilter.GaussianBlur(max(5,int(pw*.07))))
    out = portrait.copy()
    out.paste(modified,(left,top),mask)
    return out

def wrap(draw, text, face, width):
    lines = []
    current = ""
    for word in text.split():
        candidate = (current+" "+word).strip()
        if current and draw.textbbox((0,0),candidate,font=face)[2] > width:
            lines.append(current)
            current = word
        else:
            current = candidate
    if current:
        lines.append(current)
    return lines

def render_frame(chars, portraits, speaker, text, envelope, index, frame_count):
    img = Image.new("RGB",(WIDTH,HEIGHT),(12,16,30))
    d = ImageDraw.Draw(img)
    d.rectangle((0,0,WIDTH,88),fill=(24,30,52))
    d.text((38,17),"PSYOPSNEWS  |  TRE IDIOTER OCH EN MIKROFON",font=font(30),fill="white")
    d.text((1120,28),"SATIR",font=font(25),fill=(255,91,94))
    # Shot change at beginning and every ~5s: gentle push on the speaking puppet.
    for idx,key in enumerate(ORDER):
        x,y = 38+idx*413,115
        active = key == speaker
        d.rounded_rectangle((x-6,y-6,x+383,y+428),radius=14,
            fill=(64,38,47) if active else (25,29,43),
            outline=(255,78,83) if active else (67,73,93),
            width=6 if active else 2)
        photo = portraits[key]
        if active:
            mouth = chars[key].get("mouth",[0.5,0.48])
            photo = jaw_warp(photo,mouth,envelope)
            # Subtle nod and camera drift; no exaggerated cartoon movement.
            nod = int(2.5*math.sin(index*.27) + 2*envelope)
            zoom = 1.0 + 0.012*min(1.0,index/25.0)
            if zoom>1.001:
                nw,nh=int(PANEL_W*zoom),int(PANEL_H*zoom)
                photo=photo.resize((nw,nh),Image.Resampling.BILINEAR)
                photo=ImageOps.fit(photo,(PANEL_W,PANEL_H),centering=(0.5,0.42))
        else:
            nod=0
            photo=ImageEnhance.Brightness(photo).enhance(0.62)
        # Clip to panel to avoid image bleeding outside it.
        panel=Image.new("RGB",(PANEL_W,PANEL_H),(22,25,39))
        if nod>=0:
            panel.paste(photo.crop((0,0,PANEL_W,PANEL_H-nod)),(0,nod))
        else:
            panel.paste(photo.crop((0,-nod,PANEL_W,PANEL_H)),(0,0))
        img.paste(panel,(x,y))
        d.rectangle((x,y+340,x+370,y+415),fill=(34,37,56))
        d.text((x+12,y+357),chars[key]["name"],font=font(25),
               fill="white" if active else (165,165,176))
        if active:
            d.ellipse((x+335,y+365,x+355,y+385),fill=(250,70,76))
    d.rectangle((0,575,WIDTH,HEIGHT),fill=(14,21,37))
    d.rectangle((0,575,WIDTH,582),fill=(225,52,64))
    for j,line in enumerate(wrap(d,text,font(28),1180)[:3]):
        d.text((44,596+j*36),line,font=font(28),fill="white")
    # Speaking activity meter: a subtle broadcast element, not a fake mouth.
    bar_x = 45 + ORDER.index(speaker)*413
    d.rounded_rectangle((bar_x,551,bar_x+360,561),radius=4,fill=(45,47,62))
    d.rounded_rectangle((bar_x,551,bar_x+max(4,int(360*envelope)),561),
                        radius=4,fill=(255,81,88))
    return img

def encode_segment(audio_path, video_path, chars, portraits, speaker, text):
    values=amplitudes(audio_path)
    if not values:
        raise RuntimeError(f"No decoded audio: {audio_path}")
    # FFmpeg consumes raw RGB frames; audio stays in sync via -shortest.
    cmd=["ffmpeg","-y","-loglevel","error","-f","rawvideo","-pix_fmt","rgb24",
         "-s",f"{WIDTH}x{HEIGHT}","-r",str(FPS),"-i","pipe:0",
         "-i",str(audio_path),"-c:v","libx264","-preset","veryfast",
         "-pix_fmt","yuv420p","-c:a","aac","-b:a","160k","-ar","44100",
         "-ac","2","-shortest","-movflags","+faststart",str(video_path)]
    process=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
    try:
        for i,level in enumerate(values):
            frame=render_frame(chars,portraits,speaker,text,level,i,len(values))
            process.stdin.write(frame.tobytes())
        process.stdin.close()
        error=process.stderr.read().decode("utf-8",errors="replace")
        status=process.wait()
        if status:
            raise RuntimeError(f"FFmpeg render failed: {error[-1200:]}")
    except BaseException:
        if process.poll() is None:
            process.kill()
        process.wait()
        raise
