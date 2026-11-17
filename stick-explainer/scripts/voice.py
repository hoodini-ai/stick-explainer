"""Narration for one stick-explainer project.

Reads script.json, sends the joined narration to ElevenLabs once, writes voice.mp3 and words.json
(word timings). Never prints the API key. Refuses to pay twice for the same text.

  python voice.py <project> --dry-run
  python voice.py <project>
"""
import base64
import hashlib
import json
import os
import sys
import urllib.request
from pathlib import Path

MAX_CHARS = 700


def die(msg):
    print("STOP:", msg)
    sys.exit(1)


def load_key():
    # A key file, when named, wins over the environment variable (an old variable is a common trap).
    key = ""
    if os.environ.get("ELEVENLABS_KEY_FILE"):
        key = Path(os.environ["ELEVENLABS_KEY_FILE"]).read_text(encoding="utf-8-sig").strip().strip('"')
    if not key:
        key = os.environ.get("ELEVENLABS_API_KEY", "").strip()
    if not key:
        die("no key found. Set ELEVENLABS_API_KEY or ELEVENLABS_KEY_FILE (path to a text file with the key).")
    return key


def words_from_alignment(al):
    out, word, start, end = [], "", None, 0.0
    for c, s, e in zip(al["characters"], al["character_start_times_seconds"], al["character_end_times_seconds"]):
        if c.strip():
            if start is None:
                start = s
            word, end = word + c, e
        elif word:
            out.append({"w": word, "s": round(start, 3), "e": round(end, 3)})
            word, start = "", None
    if word:
        out.append({"w": word, "s": round(start, 3), "e": round(end, 3)})
    return out


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        die("usage: voice.py <project folder> [--dry-run]")
    proj = Path(args[0])
    script = json.loads((proj / "script.json").read_text(encoding="utf-8"))
    text = " ".join(s["text"].strip() for s in script["shots"])
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]
    print(f"characters: {len(text)} | pictures: {len(script['shots'])}")
    if len(text) > MAX_CHARS:
        die(f"narration is longer than {MAX_CHARS} characters. Shorten the script.")
    if "--dry-run" in sys.argv:
        return

    stamp = proj / "voice.hash"
    if (proj / "voice.mp3").exists() and stamp.exists() and stamp.read_text().strip() == digest:
        print("voice.mp3 already matches this text - nothing to pay, nothing done.")
        return

    voice = os.environ.get("ELEVENLABS_VOICE_ID", "").strip()
    if not voice:
        die("set ELEVENLABS_VOICE_ID to the voice you want to use.")
    model = os.environ.get("ELEVENLABS_MODEL", "eleven_multilingual_v2")
    req = urllib.request.Request(
        f"https://api.elevenlabs.io/v1/text-to-speech/{voice}/with-timestamps",
        data=json.dumps({"text": text, "model_id": model}).encode("utf-8"),
        headers={"xi-api-key": load_key(), "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            data = json.loads(r.read())
    except urllib.error.HTTPError as e:
        die(f"ElevenLabs answered {e.code}: {e.read().decode('utf-8', 'replace')[:300]}")

    (proj / "voice.mp3").write_bytes(base64.b64decode(data["audio_base64"]))
    words = words_from_alignment(data["alignment"])
    (proj / "words.json").write_text(json.dumps(words, ensure_ascii=False), encoding="utf-8")
    stamp.write_text(digest)
    print(f"done: voice.mp3, {len(words)} words, {words[-1]['e']:.1f} s")


if __name__ == "__main__":
    main()
