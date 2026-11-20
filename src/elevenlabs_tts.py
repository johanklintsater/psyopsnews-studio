"""ElevenLabs text-to-speech for PSYOPSNEWS. Requires GitHub Actions secret."""
import json
import os
import urllib.error
import urllib.request

API="https://api.elevenlabs.io/v1"
ENV_IDS={"bear":"ELEVENLABS_VOICE_BEAR","journalist":"ELEVENLABS_VOICE_JOURNALIST","rock":"ELEVENLABS_VOICE_ROCK"}
def request(url,payload=None):
    key=os.environ.get("ELEVENLABS_API_KEY","").strip()
    if not key:
        raise RuntimeError("ELEVENLABS_API_KEY is missing from GitHub Actions secrets.")
    data=None if payload is None else json.dumps(payload,ensure_ascii=False).encode("utf-8")
    headers={"xi-api-key":key,"Accept":"application/json" if payload is None else "audio/mpeg"}
    if payload is not None:headers["Content-Type"]="application/json"
    req=urllib.request.Request(url,data=data,headers=headers,method="GET" if payload is None else "POST")
    try:
        with urllib.request.urlopen(req,timeout=90) as response:return response.read()
    except urllib.error.HTTPError as exc:
        # Do not echo authorization headers or API key.
        body=exc.read(500).decode("utf-8",errors="replace")
        raise RuntimeError(f"ElevenLabs HTTP {exc.code}: {body}") from None
def choose_voices():
    """Use configured voice IDs directly; only list voices when needed."""
    chosen={}
    used=set()
    for speaker in ("bear","journalist","rock"):
        override=os.environ.get(ENV_IDS[speaker],"").strip()
        if override:
            chosen[speaker]=override
            used.add(override)
    if len(chosen)==3:
        print("Using three configured ElevenLabs voice IDs (no voices_read permission needed).")
        return chosen
    try:
        voices=json.loads(request(API+"/voices")).get("voices",[])
    except RuntimeError as exc:
        if "voices_read" in str(exc):
            missing=[ENV_IDS[s] for s in ("bear","journalist","rock") if s not in chosen]
            raise RuntimeError(
                "ElevenLabs API key lacks voices_read permission. "
                "Either enable 'Voices: Read' for this API key in ElevenLabs, "
                "or set all three GitHub Actions secrets: "
                +", ".join(missing)
                +". Text-to-Speech permission is also required."
            ) from None
        raise
    available=[v for v in voices if v.get("voice_id")]
    if not available:
        raise RuntimeError("No ElevenLabs voices available to this API key.")
    for speaker in ("bear","journalist","rock"):
        if speaker in chosen:
            continue
        prefer="female" if speaker=="rock" else "male"
        candidates=[v for v in available if str(v.get("labels",{}).get("gender","")).lower()==prefer and v["voice_id"] not in used]
        candidates += [v for v in available if v["voice_id"] not in used]
        if not candidates:
            raise RuntimeError("Three distinct voices not available; configure voice IDs using GitHub Secrets.")
        chosen[speaker]=candidates[0]["voice_id"]
        used.add(chosen[speaker])
    for speaker in chosen:
        print(f"Selected ElevenLabs voice for {speaker} (ID hidden)")
    return chosen

def synthesize(text,voice_id,target):
    model=os.environ.get("ELEVENLABS_MODEL_ID","eleven_multilingual_v2")
    payload={"text":text,"model_id":model,"voice_settings":{"stability":0.45,"similarity_boost":0.75}}
    audio=request(API+"/text-to-speech/"+voice_id+"?output_format=mp3_44100_128",payload)
    if len(audio)<500:raise RuntimeError("ElevenLabs returned unexpectedly short audio.")
    target.write_bytes(audio)
