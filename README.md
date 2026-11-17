# stick-explainer

A small Claude skill that turns one topic into a short (30 to 45 seconds) stick-figure explainer video:
script, voice-over, image prompts and the final cut.

It is the skill from the Hoodini AI video. It is a demo pipeline on purpose: short videos, a hard budget,
and it asks before every step that costs money.

## What you need

- **Claude Code** (part of a paid Claude plan)
- **Python 3.10+** (no extra packages) and **ffmpeg** on your PATH
- **An ElevenLabs account** for the voice (the free plan works for testing, but does not allow commercial use)
- **A way to make pictures**: Google AI Studio or ChatGPT. The skill writes the prompts; you (or Claude in your
  browser) generate the pictures.

Nothing here is free end to end. The video walks through the real monthly costs.

## Install

Copy the `stick-explainer` folder into your skills folder:

- for one project: `<your project>/.claude/skills/stick-explainer`
- for all projects: `~/.claude/skills/stick-explainer`

Then set two environment variables for the voice:

```
ELEVENLABS_API_KEY   your ElevenLabs key (or ELEVENLABS_KEY_FILE = path to a text file holding the key)
ELEVENLABS_VOICE_ID  the voice you want to use
```

Never paste a key into a chat.

## Use

In Claude Code:

```
/stick-explainer what did people do before alarm clocks?
```

Claude asks up to three questions (topic, figure, colours), writes the script, waits for your yes, makes the
voice, hands you the image prompts, and builds `final.mp4` once the pictures are in the folder.

## What is in here

```
stick-explainer/
  SKILL.md           the instructions Claude follows
  scripts/voice.py   voice-over with word timings (ElevenLabs)
  scripts/build.py   the cut: one picture per sentence, slow push-in (ffmpeg)
```

Read all three before you run them. They are short.

## Please make it your own

Do not copy the character or the drawings of an existing channel, and do not mass-produce videos with this.
Check every fact and every picture yourself: image models drop details, and language models get things wrong.

## Licence

MIT, see `LICENSE`.
