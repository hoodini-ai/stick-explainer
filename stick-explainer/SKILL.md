---
name: stick-explainer
description: Make a short (30 to 45 seconds) stick-figure explainer video from one topic - script, voice-over, image prompts, and the final cut. Use when the user says "/stick-explainer", "make a stick figure explainer", or names a topic for a short hand-drawn explainer video.
argument-hint: "[topic]"
---

# Stick Explainer - one topic in, one short video out

Input from the user: $ARGUMENTS

You are writer, director and editor for ONE short explainer video in a simple hand-drawn stick-figure style:
flat coloured backgrounds, one clear idea per picture, a calm narrator. Target length 30-45 seconds, never longer.
This is a small demo pipeline. Keep it small: do not turn it into a 10-minute documentary.

Everything for one video lives in one project folder: `videos/<short-name>/` inside the current working directory.
The helper scripts are in the `scripts/` folder next to this file. Call them with the absolute path of that folder.

## Budget rules (never break these)

- At most **12 images** and at most **700 characters** of narration per video.
- Before every paid step (voice, images) say what it will cost in characters or images and wait for a yes.
- Never generate the voice twice for the same text. `voice.py` refuses to re-run unless the text changed.
- Never regenerate an image that is already in `images/` unless the user asks for that picture again.
- If something fails twice, stop and tell the user. Do not retry in a loop.

## Step 1 - Ask (once, at most 3 questions)

Use one question round. Skip any question the user already answered in their message.

1. **Topic** - what should the video explain? (If none: offer three "what did people do before X" / "why do we X" ideas.)
2. **The figure** - plain round head / with a small detail (hair tuft, hat, glasses, scarf) / their own description.
3. **Colours** - warm paper tones / dark night tones / bright comic colours / their own.

Write the answers into `videos/<short-name>/style.md` as one reusable **style block** (4-6 lines) that describes
the figure and the look in words. Every image prompt later starts with this exact block, so the figure stays the same.
Make the look your own. Do not copy the character, thumbnails or drawings of an existing channel.

## Step 2 - Script

Write 70-100 words, 8-12 short sentences, in the language the user writes in:

1. Hook: speak to the viewer ("Tonight you will...") or open with a surprising number.
2. Three facts, each one sentence long, each one checkable. Look facts up if you are not sure. No invented numbers.
3. One turn ("But here is the strange part...").
4. End with a question to the viewer.

Rules for speakable text: write numbers as words, no brackets, no abbreviations, no emoji.
Show the script and wait for approval. Change it until the user says yes.

## Step 3 - Shot list

One picture per sentence (two short sentences may share one). Save `videos/<short-name>/script.json`:

```json
{
  "title": "What did people do before alarm clocks?",
  "shots": [
    { "text": "Tonight you will set an alarm.", "image": "images/01.png", "prompt": "..." }
  ]
}
```

- `text` is the exact narration for that picture. All `text` fields joined with spaces are the full narration.
- `prompt` = the style block + one sentence saying what is in the picture. One idea per picture, big and centred,
  no text in the picture unless it is one or two large words, 16:9.
- Also write all prompts into `prompts.md`, numbered, ready to copy.

## Step 4 - Voice (paid)

```
python <scripts>/voice.py videos/<short-name> --dry-run     # shows characters, costs nothing
python <scripts>/voice.py videos/<short-name>               # makes voice.mp3 + words.json
```

The script reads the key from the environment variable `ELEVENLABS_API_KEY` (or the file named in
`ELEVENLABS_KEY_FILE`) and the voice from `ELEVENLABS_VOICE_ID`. Never ask the user to paste a key into the chat,
never print it. If the key is missing, tell the user which variable to set and stop.
Tell the user: a free ElevenLabs plan does not allow commercial use without attribution.

## Step 5 - Images

Ask once: **"How do you make your pictures?"** and follow that path. `prompts.md` is written for all of them.

- **Google AI Studio** (image model, e.g. Nano Banana): one chat, aspect ratio 16:9. Paste prompt 01, then for every
  further picture send "Same drawing style and same character as before. Scene: ...". Download each result.
- **ChatGPT**: same idea - one chat, one picture after the other, always asking for the same style and character.
- **API key** (Google or OpenAI): only if the user already has a key and billing set up. Not automated in this
  version of the skill - tell the user so, and use one of the two ways above.

Save the results as `images/01.png`, `images/02.png`, ... in the project folder. If you can drive the browser yourself,
do it; otherwise the user does it and tells you when the files are there.

Generate picture 01 first and show it. Only when the user likes the figure, do the rest.
Image models sometimes drop a detail (a missing mouth, a wrong hat). Look at every picture; redo a single
picture with a short correction ("same picture, but add a small mouth") instead of starting over.

## Step 6 - Build

```
python <scripts>/build.py videos/<short-name>               # 1920x1080
python <scripts>/build.py videos/<short-name> --size 4k     # 3840x2160
```

Each picture is shown exactly while its sentence is spoken, with a slow push-in and hard cuts.
Output: `videos/<short-name>/final.mp4` and `check.jpg` (one frame per picture).

## Step 7 - Check and report

Look at `check.jpg`. Is every picture the right one for its sentence, is the figure the same everywhere?
You cannot hear the audio - say so, and ask the user to judge the voice.
Report in four lines: length, number of pictures, characters spoken, what is still rough.
