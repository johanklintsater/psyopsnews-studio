# Produce Episode — GitHub Actions

1. Open **Actions → Produce Episode → Run workflow**.
2. Wait for the job to complete.
3. Download the **psyopsnews-ep01** artifact (ZIP containing MP4).

## Real pilot assets
Upload `assets/bear.png` (your original puppet image) and `assets/ep01.wav` (narration audio) through GitHub's Add file → Upload files. Re-run the workflow.

Without these two files the workflow deliberately creates a **silent 10-second placeholder video** to verify FFmpeg and GitHub Actions. It does not generate speech or animate the puppet.

## Next integrations
Swedish text-to-speech, lip-sync, subtitles, opening graphics, scheduled publishing. YouTube publishing and 24/7 live streaming are not enabled by this workflow. Keep API credentials in GitHub Actions Secrets.
