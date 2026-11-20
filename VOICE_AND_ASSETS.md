# PSYOPSNEWS Studio v0.2

## Voices
- Cykelhjälmen: Swedish male voice (sv-SE-MattiasNeural); Stockholm-style slang in the script.
- Journalisten: Swedish male voice (sv-SE-MattiasNeural); Småland-style dialogue cues.
- Rockbruden: Swedish female voice (sv-SE-SofieNeural); broad Stockholm slang.

**Important:** Edge TTS provides Swedish voices, not guaranteed authentic Stockholm or Småland accents. The two male characters currently use the same synthesized voice, with different dialogue styles. Distinct regional voice performances require a capable provider or recorded voice acting.

## Puppet images
Upload exactly these three images through GitHub's **Add file → Upload files**, inside the `assets` directory:
- `assets/bear.png`
- `assets/journalist.png`
- `assets/rock.png`

The workflow can run without images, but uses generic placeholder heads. Adjust `mouth` normalized coordinates in `config/characters.json` if the simple animated mouth appears in the wrong location.

## Run
GitHub → Actions → **Produce Episode v0.2 (voices and puppets)** → Run workflow.
Download `psyopsnews-ep01-v02` from the successful run's Artifacts.

## Current limitations
This is a first-pass 2D mouth-opening animation driven by audio volume, **not phoneme-accurate lip-sync**. It produces a studio backdrop, short title slate, Swedish speech and a composed MP4. Online TTS requires network access and may fail if the external service is unavailable. No YouTube upload or livestream is included.
