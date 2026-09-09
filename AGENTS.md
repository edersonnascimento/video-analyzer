# Video Analyzer Agent Guide

## Project Structure

Two setuptools packages in one repo:
- `video_analyzer/` — main video analysis tool (`video-analyzer` CLI)
- `video-analyzer-tune/` — DSPy MIPROv2 prompt optimizer (`video-analyzer-tune` CLI)

Both installable with `pip install -e .` from their respective directories.

## Setup Prerequisites

- Python 3.8+ (project requires it in setup.py, README says 3.11+)
- FFmpeg (required for audio extraction — `apt-get install ffmpeg` on Debian/Ubuntu)
- Ollama with a vision model **or** an OpenAI-compatible API key + URL

## Running

```bash
# Local analysis with Ollama (default client)
video-analyzer <video.mp4>

# Cloud analysis via OpenRouter
video-analyzer <video.mp4> --client openai_api --api-key KEY --api-url https://openrouter.ai/api/v1 --model meta-llama/llama-3.2-11b-vision-instruct:free

# Keep extracted frames for prompt tuning
video-analyzer <video.mp4> --keep-frames
```

Key CLI flags: `--client`, `--model`, `--api-key`, `--api-url`, `--whisper-model`, `--max-frames`, `--context-window`, `--start-stage` (1-3), `--log-level`, `--prompt`, `--output`.

## Configuration

Config is loaded from `config/config.json`, cascading over the packaged default. CLI args override config values. The `Config` class (`video_analyzer/config.py`) handles merging — see `update_from_args()` for which flags map to which config keys.

Default output: `output/analysis.json`. Intermediate artifacts (frames + audio) are placed in a per-run subfolder `output/<video_stem>/` and are cleaned up unless `--keep-frames` is set. The `--output` flag accepts either a full file path (e.g. `./results/my_video.json`) or a directory.

## Testing

No pytest or test runner configured. Tests are standalone scripts (e.g. `test_prompt_loading.py`) run directly with Python. The tune subpackage has a `tests/` directory but no `conftest.py` or test command — run them as `python -m pytest` only if you add your own configuration.

## Prompt Tuning Workflow

1. Run `video-analyzer <video> --keep-frames` to produce `output/analysis.json` + `output/<video_stem>/frames/`
2. Edit `frame_analyses[i].response` and `video_description.response` in the JSON to show ideal output
3. Create `training_data.json` with paths to each edited output directory
4. Run `video-analyzer-tune --training-data training_data.json --output-dir tuned_prompts/`
5. Point your main config's `prompt_dir` and `prompts` list at the tuned files

## Architecture Notes

The analyzer runs in 3 stages:
1. **Frame & Audio Extraction** — OpenCV for keyframes, Whisper for transcription (with confidence checks)
2. **Frame Analysis** — per-frame LLM calls with running context from previous frames (`{PREVIOUS_FRAMES}` token)
3. **Video Reconstruction** — combines all frame notes + transcript into final description

LLM clients are pluggable via the `clients/` package (Ollama or generic OpenAI-compatible API). The `VideoAnalyzer` class handles prompt templating and response parsing.

## Gotchas

- Audio transcription may fail silently — check `transcription_successful` in metadata
- Poor audio confidence triggers a warning but analysis continues with frames only
- The `{prompt}` token in prompts is replaced with `"I want to know {user_prompt}"` if a custom prompt is provided
- Frame analysis uses `num_predict` from `response_length.frame` (default 300); reconstruction uses `response_length.reconstruction` (default 1000). A `response_length.reasoning` budget can be added on top for reasoning models.
- Config keys are nested: audio settings live under `audio.*`, frames under `frames.*`, clients under `clients.*`
