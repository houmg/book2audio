# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Book2Audio** — a Python tool that converts ebooks (EPUB, MOBI, AZW3, PDF, TXT) into audio/video output. It uses Microsoft Edge TTS for speech synthesis, generates SRT subtitles, and can produce MP4 videos with embedded subtitles.

## Essential Commands

```bash
# Install dependencies
pip install -r requirements.txt
pip install -e .          # development install, registers `book2audio` CLI entry point

# CLI usage
book2audio tts input.txt                     # generate TTS audio + subtitles
book2audio merge output/ book.mp3 book.srt   # merge segment audio/subtitles
book2audio video book.mp3 book.srt bg.jpg output.mp4  # generate video
book2audio all input.txt bg.jpg output.mp4   # full pipeline
book2audio config --list                     # show current config

# Run tests
python test_basic.py

# Build package
python setup.py sdist bdist_wheel
```

## Architecture

The project is organized as a Python package with a flat module structure. All modules live in the project root and are imported as a package (`book2audio.*`).

### Module Responsibilities

| Module | Purpose |
|--------|---------|
| `cli.py` | CLI entry point with argparse subcommands (`tts`, `merge`, `video`, `all`, `config`). Uses `asyncio.run()` for the TTS pipeline. |
| `config.py` | Singleton `Config` class wrapping `configparser`. Reads `config.ini`, exposes typed properties (voice, rate, segment_size, ffmpeg_path, etc.). Global instance: `config`. |
| `logger.py` | Sets up a global `logger` with both console and file handlers. Use `from .logger import logger`. |
| `extract_text.py` | Multi-format text extraction. Auto-detects format by extension. Returns `None` for unsupported formats — callers must handle this. |
| `tts.py` | `TTSGenerator` class. Wraps the `edge-tts` CLI via `asyncio.create_subprocess_exec`. Produces per-segment `.mp3` + `.srt` files. Parses Edge TTS JSON subtitle output to SRT format. |
| `audio_processor.py` | `AudioProcessor` class. Merges `part_*.mp3` files via `pydub` and re-times `part_*.srt` files with cumulative time offsets. |
| `video_generator.py` | `VideoGenerator` class. Uses FFmpeg subprocess to create MP4 with static background image and burned-in subtitles. |
| `utils.py` | Pure utility functions: text splitting by sentences, SRT time formatting/parsing, directory/file helpers. |

### Data Flow (full pipeline: `book2audio all`)

1. **Extract text** from ebook → `text` string
2. **Split text** into segments (~500-1000 chars each) via `split_text_by_sentences`
3. **TTS generation**: each segment → `output/part_XXXX.mp3` + `output/part_XXXX.srt`
4. **Merge**: all parts → `output/merged.mp3` + `output/merged.srt`
5. **Video**: merged audio + subtitles + background image → `output.mp4`

## System Dependencies

- **FFmpeg/ffprobe** — required for audio processing (pydub) and video generation. Paths configured in `config.ini` (currently set to WinGet-installed FFmpeg).
- **Internet connection** — Edge TTS is a cloud service.

## Key Details

- The package name is `book2audio` and the CLI entry point is `book2audio` (registered in `setup.py`).
- Output files use zero-padded naming: `part_0001.mp3`, `part_0002.mp3`, etc.
- `extract_text.py` uses optional imports — if a library isn't installed, the corresponding format returns `None` rather than crashing.
- `config.ini` uses `RawConfigParser` to avoid `%` interpolation issues with values like `+0%`.
- Tests are in `test_basic.py` — not pytest-based, just plain `asyncio.run()` with assertions.
