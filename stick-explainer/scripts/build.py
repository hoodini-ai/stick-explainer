"""Cuts one stick-explainer video: every picture is shown while its sentence is spoken.

Needs ffmpeg on the PATH. Reads script.json, words.json, voice.mp3 and images/*.png from the project folder.

  python build.py <project>            -> final.mp4 (1920x1080) + check.jpg
  python build.py <project> --size 4k  -> 3840x2160
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

FPS = 30
PUSH = 0.07  # how far the slow push-in goes (7 %)
TAIL = 0.7   # seconds the last picture stays after the last word


def die(msg):
    print("STOP:", msg)
    sys.exit(1)


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        die("ffmpeg failed:\n" + r.stderr[-600:])


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        die("usage: build.py <project folder> [--size 4k]")
    proj = Path(args[0]).resolve()
    w, h = (3840, 2160) if "4k" in [a.lower() for a in sys.argv] else (1920, 1080)

    shots = json.loads((proj / "script.json").read_text(encoding="utf-8"))["shots"]
    words = json.loads((proj / "words.json").read_text(encoding="utf-8"))
    missing = [s["image"] for s in shots if not (proj / s["image"]).exists()]
    if missing:
        die("these pictures are missing: " + ", ".join(missing))

    # Start of each picture = start of its first spoken word.
    counts = [len(s["text"].split()) for s in shots]
    if sum(counts) != len(words):
        die(f"script has {sum(counts)} words but the voice has {len(words)}. Re-run voice.py after changing the text.")
    starts, i = [], 0
    for c in counts:
        starts.append(0.0 if i == 0 else words[i]["s"])
        i += c
    ends = starts[1:] + [words[-1]["e"] + TAIL]

    tmp = Path(tempfile.mkdtemp(prefix="stick_"))
    parts = []
    frame_at = 0
    for n, (s, a, b) in enumerate(zip(shots, starts, ends)):
        # whole frames, so picture cuts never drift away from the voice
        frames = max(1, round(b * FPS) - frame_at)
        frame_at += frames
        out = tmp / f"p{n:02d}.mp4"
        vf = (
            f"scale={w * 2}:{h * 2}:force_original_aspect_ratio=increase,crop={w * 2}:{h * 2},"
            f"zoompan=z='1+{PUSH}*on/{frames}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frames}:s={w}x{h}:fps={FPS},"
            "format=yuv420p"
        )
        run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(proj / s["image"]), "-vf", vf,
             "-frames:v", str(frames), "-c:v", "libx264", "-crf", "16", "-preset", "medium", str(out)])
        parts.append(out)
        print(f"picture {n + 1:02d}: {a:6.2f} s -> {b:6.2f} s  {s['image']}")

    lst = tmp / "list.txt"
    lst.write_text("".join(f"file '{p.as_posix()}'\n" for p in parts), encoding="utf-8")
    final = proj / "final.mp4"
    run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(lst), "-i", str(proj / "voice.mp3"),
         "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", str(final)])

    # one frame from the middle of every picture, as a contact sheet
    cols = 4
    rows = -(-len(shots) // cols)
    mids = [(a + b) / 2 for a, b in zip(starts, ends)]
    sel = "+".join(f"eq(n\\,{round(m * FPS)})" for m in mids)
    run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(final), "-vf",
         f"select='{sel}',setpts=N/FRAME_RATE/TB,scale=480:-1,tile={cols}x{rows}", "-frames:v", "1", str(proj / "check.jpg")])
    print(f"done: {final}  ({ends[-1]:.1f} s, {len(shots)} pictures, {w}x{h})")


if __name__ == "__main__":
    main()
