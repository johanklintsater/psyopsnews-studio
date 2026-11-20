"""Smoke test for Puppet Engine. No ElevenLabs API calls or credits."""
import math
import subprocess
import tempfile
import unittest
from pathlib import Path
from PIL import Image, ImageDraw
from puppet_engine import amplitudes, encode_segment, jaw_warp, render_frame, ORDER

class PuppetEngineTests(unittest.TestCase):
    def test_photo_preserving_warp(self):
        photo=Image.new("RGB",(370,340),(130,85,60))
        ImageDraw.Draw(photo).ellipse((170,150,210,174),fill=(50,22,15))
        original=photo.tobytes()
        self.assertEqual(jaw_warp(photo,[.5,.48],0).tobytes(),original)
        self.assertNotEqual(jaw_warp(photo,[.5,.48],1).tobytes(),original)
    def test_render_and_encode(self):
        chars={k:{"name":k,"mouth":[.5,.48]} for k in ORDER}
        portraits={k:Image.new("RGB",(370,340),(100,75,65)) for k in ORDER}
        frame=render_frame(chars,portraits,"bear","Ett test av podden.",.6,1,12)
        self.assertEqual(frame.size,(1280,720))
        with tempfile.TemporaryDirectory() as td:
            audio=Path(td)/"test.wav"
            video=Path(td)/"test.mp4"
            subprocess.run(["ffmpeg","-y","-v","error","-f","lavfi",
                "-i","sine=frequency=440:duration=0.55","-ar","44100",str(audio)],check=True)
            self.assertGreater(len(amplitudes(audio)),3)
            encode_segment(audio,video,chars,portraits,"bear","Ett test.",)
            self.assertGreater(video.stat().st_size,1000)

if __name__=="__main__":
    unittest.main()
