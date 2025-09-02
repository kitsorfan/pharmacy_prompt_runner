# Pharmacy Prompt Runner

A tiny, self-contained harness to **load your pharmacist prompt from a text file**, run a batch of **customer-style test inputs**, and **store results** for your submission.

## Quick Start

1) Install deps:
```bash
pip install openai python-dotenv tenacity
```

2) Put your API key in the environment (or `.env`):
```bash
export OPENAI_API_KEY=sk-...
# or create .env with: OPENAI_API_KEY=sk-...
```

3) Paste **your own prompt** into `prompt.txt` (do not use this repo to *create* the prompt).

4) Edit `tests.txt` with your test questions (one per line).

5) Run:
```bash
python run.py --model gpt-4o-mini
```

Outputs:
- `results/results.jsonl` — raw run logs (one JSON object per test)
- `results/report.html` — simple human-readable report you can screenshot
- `results/last_run_summary.json` — summary metrics and timestamps

> Tip: Add `--voice-mode` to see responses truncated to a "voice-friendly" length.
> Tip: Add `--max-tokens` to cap response length (default 350).

## Files

- `run.py` — main runner; reads `prompt.txt` & `tests.txt`, calls the API, writes results.
- `prompt.txt` — **your** pharmacist prompt text (system message).
- `tests.txt` — list of customer queries to simulate (10+ recommended).
- `results/` — outputs and artifacts.

## Notes

- This tool **does not** write or modify your prompt; it only *uses* the text you provide.
- If your SDK uses the newer **Responses API**, the runner will use it. If not available,
  it automatically falls back to classic **Chat Completions**.
