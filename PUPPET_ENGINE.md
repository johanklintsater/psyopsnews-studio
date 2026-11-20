# PSYOPSNEWS Studio v0.4 — Puppet Engine

A three-puppet, audio-reactive video podcast producer running in GitHub Actions.

## Features
- Three characters from `config/characters.json` and `assets/*.png`
- ElevenLabs TTS with voice selection through optional GitHub secrets
- Per-frame volume envelope from decoded audio (12 FPS)
- Subtle head nod, slow camera push, active speaker lighting, audio meter
- Local, feather-blended lower-face image deformation for jaw movement
- Animated MP4 assembled by FFmpeg, downloadable from GitHub Actions artifacts
- Offline smoke test before paid API calls

## Run
Open [the workflow](https://github.com/johanklintsater/psyopsnews-studio/actions/workflows/produce-podcast.yml), choose **Run workflow**, and download the MP4 artifact.

The `ELEVENLABS_API_KEY` GitHub Actions secret needs Text to Speech permission. If voice IDs are not set, it also needs Voices Read permission.

Optional voice ID secrets:
- `ELEVENLABS_VOICE_BEAR`
- `ELEVENLABS_VOICE_JOURNALIST`
- `ELEVENLABS_VOICE_ROCK`

The JSON dialogue file is `episodes/podcast_pilot.json`. The environment variable `PSYOPSNEWS_EPISODE` can point to another JSON episode inside the repository.

## Mouth calibration
The `mouth` coordinates in `config/characters.json` are **normalized coordinates** (0–1) relative to each cropped portrait panel (370×340), **not** the original full-resolution image. The initial values are estimates, and need visual calibration on actual video.

For example, `"mouth": [0.50, 0.48]` sets the center of the deformation area at 50% of portrait width and 48% of portrait height.

This engine does **not** yet do phoneme-accurate lip sync or detect eyes. It deforms existing portrait pixels in sync with audio volume, which is safer than drawing a generic oval mouth but may still look strange with a closed-mouth photo. For realistic lip sync, provide separate open/closed mouth artwork or face rig layers, plus timing/phoneme data. It does not invent a convincing mouth interior.

## Local offline smoke test
Requires Python, Pillow and FFmpeg:

```bash
python -m pip install Pillow
PYTHONPATH=src python -m unittest discover -s tests -p 'test_puppet_engine.py' -v
```

The test creates synthetic portraits and tone audio and does not call ElevenLabs.

## Costs and publishing
Each real workflow run calls ElevenLabs for every dialogue line and may consume paid credits. The workflow does not auto-publish to YouTube. Inspect and approve rendered episodes before publishing, and label fictional/satirical content clearly.
