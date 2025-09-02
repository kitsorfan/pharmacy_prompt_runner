#!/usr/bin/env python3
import argparse
import datetime
import json
import os
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Callable, Sequence, Mapping

# Optional: dotenv for local dev
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

# ---- Tenacity (with safe fallbacks so type checkers don't complain) ----
try:
    from tenacity import retry, stop_after_attempt, wait_exponential, RetryError   # type: ignore
except Exception:
    def retry(*args: Any, **kwargs: Any) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        def _decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
            return fn
        return _decorator
    def stop_after_attempt(*args: Any, **kwargs: Any) -> Any:
        return None
    def wait_exponential(*args: Any, **kwargs: Any) -> Any:
        return None

import httpx  # explicit HTTP client for timeout/TLS control


# -------------------- Utilities & Logging --------------------

def now_iso() -> str:
    return datetime.datetime.now().isoformat(timespec="seconds")


class Logger:
    def __init__(self, enabled: bool = True):
        self.enabled = enabled

    def log(self, msg: str) -> None:
        if self.enabled:
            print(f"[{now_iso()}] {msg}", flush=True)


def read_textfile(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def read_tests(path: Path) -> List[str]:
    lines = [ln.strip() for ln in path.read_text(encoding="utf-8").splitlines()]
    return [ln for ln in lines if ln and not ln.startswith("#")]


def ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def preflight_check(http_client: httpx.Client, api_key: str, base_url: Optional[str], logger: Logger) -> None:
    url_root = (base_url.rstrip("/") if base_url else "https://api.openai.com")
    url = f"{url_root}/v1/models"
    headers = {"Authorization": f"Bearer {api_key}"}
    logger.log(f"Preflight: GET {url}")
    try:
        r = http_client.get(url, headers=headers)
        logger.log(f"Preflight: status {r.status_code}")
        if r.status_code >= 400:
            body = (r.text or "")[:300].replace("\n", " ")
            logger.log(f"Preflight: body (first 300 chars): {body}")
    except Exception as e:
        logger.log(f"Preflight: ERROR {type(e).__name__}: {e}")
        raise


# -------------------- OpenAI Client Wrapper --------------------

class OpenAIClientWrapper:
    """
    Default: uses **Chat Completions** (stable on Windows/corp networks).
    You can opt in to Responses API with --use-responses.
    HTTP/2 is disabled; timeouts are explicit; proxies come from env if set.
    """
    def __init__(
        self,
        api_key: Optional[str],
        base_url: Optional[str],
        timeout: float,
        insecure: bool,
        proxy: Optional[str],
        use_responses: bool,
        logger: Logger,
    ):
        self.logger = logger
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise RuntimeError("Missing API key. Set OPENAI_API_KEY or use --api-key.")
        self.base_url = base_url or os.getenv("OPENAI_BASE_URL")

        # If a proxy was provided, set env vars so httpx picks them up.
        if proxy:
            os.environ["HTTP_PROXY"] = proxy
            os.environ["HTTPS_PROXY"] = proxy
            self.logger.log(f"HTTP proxy set via env: {proxy}")

        # HTTP client: disable HTTP/2, set explicit timeouts, honor env proxies
        transport = httpx.HTTPTransport(http2=False, retries=2)
        self._httpx = httpx.Client(
            timeout=httpx.Timeout(connect=10.0, read=timeout, write=timeout, pool=timeout),
            verify=False if insecure else True,  # --insecure only for diagnosis
            transport=transport,
            trust_env=True,
        )
        self.logger.log(f"HTTP client ready (timeout={timeout}s, verify={'False' if insecure else 'True'}, http2=False)")

        # Build OpenAI client
        from openai import OpenAI  # type: ignore
        self._client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            http_client=self._httpx,
        )

        # Mode selection
        self._mode = "responses" if use_responses else "chat"
        self.logger.log(f"OpenAI mode: {self._mode}")

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=8))
    def run(self, model: str, system_prompt: str, user_input: str, max_tokens: int = 350) -> str:
        if self._mode == "responses":
            # Modern Responses API path
            try:
                self.logger.log("Calling Responses API...")
                rsp: Any = self._client.responses.create(  # type: ignore[attr-defined]
                    model=model,
                    input=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_input},
                    ],
                    max_output_tokens=max_tokens,
                )
                text = getattr(rsp, "output_text", None)
                if isinstance(text, str) and text.strip():
                    return text.strip()

                output_any = getattr(rsp, "output", None)
                output: Optional[Sequence[Any]] = output_any if isinstance(output_any, (list, tuple)) else None
                if output:
                    parts: List[str] = []
                    for item in output:
                        itype = getattr(item, "type", "")
                        content_any = getattr(item, "content", None)
                        content: Optional[Sequence[Any]] = content_any if isinstance(content_any, (list, tuple)) else None
                        if itype == "message" and content:
                            for c in content:
                                ctype = getattr(c, "type", "")
                                if ctype == "output_text":
                                    t = getattr(c, "text", "")
                                    if isinstance(t, str) and t:
                                        parts.append(t)
                    joined = "\n".join(parts).strip()
                    if joined:
                        return joined
                return "<no text>"
            except Exception as e:
                self.logger.log(f"Responses API failed ({type(e).__name__}): {e}. Falling back to Chat.")
                self._mode = "chat"

        # Legacy Chat Completions (default)
        try:
            self.logger.log("Calling Chat Completions API...")
            cc: Any = self._client.chat.completions.create(  # type: ignore[attr-defined]
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input},
                ],
                max_tokens=max_tokens,
            )
            choice0 = cc.choices[0]
            message = getattr(choice0, "message", None)
            content = getattr(message, "content", None)
            if isinstance(content, str) and content.strip():
                return content.strip()
            if isinstance(choice0, Mapping):
                msg = choice0.get("message", {})
                if isinstance(msg, Mapping):
                    cont = msg.get("content", "")
                    if isinstance(cont, str) and cont.strip():
                        return cont.strip()
            return "<no text>"
        except Exception as ex:
            raise RuntimeError(f"OpenAI request failed: {type(ex).__name__}: {ex}") from ex


# -------------------- Report --------------------

def build_html_report(rows: List[Dict[str, Any]], out_path: Path, logger: Logger) -> None:
    logger.log(f"Writing HTML report -> {out_path}")
    html = [
        "<html><head><meta charset='utf-8'><title>Pharmacy Prompt Report</title>",
        "<style>body{font-family:Arial,Helvetica,sans-serif;padding:20px;}"
        "table{border-collapse:collapse;width:100%;}"
        "th,td{border:1px solid #ddd;padding:8px;vertical-align:top;}"
        "th{background:#f5f5f5;text-align:left;}"
        "code{white-space:pre-wrap;}</style></head><body>",
        "<h1>Pharmacy Prompt Test Report</h1>",
        f"<p>Generated: {now_iso()}</p>",
        "<table><tr><th>#</th><th>User Input</th><th>Assistant Output</th></tr>",
    ]
    for i, r in enumerate(rows, 1):
        ui = r.get("user_input", "")
        ao = r.get("assistant_output", r.get("error", ""))
        html.append(f"<tr><td>{i}</td><td><code>{ui}</code></td><td><code>{ao}</code></td></tr>")
    html.append("</table></body></html>")
    out_path.write_text("\n".join(html), encoding="utf-8")
    logger.log("HTML report written.")


# -------------------- Main --------------------

def main() -> None:
    ap = argparse.ArgumentParser(description="Run batch tests against your pharmacist prompt.")
    ap.add_argument("--api-key", help="API key (or set OPENAI_API_KEY).")
    ap.add_argument("--base-url", help="Custom API base URL (optional).")
    ap.add_argument("--model", default="gpt-4o-mini", help="Model name or Azure deployment name")
    ap.add_argument("--prompt-file", default="prompt.txt")
    ap.add_argument("--tests-file", default="tests.txt")
    ap.add_argument("--outdir", default="results")
    ap.add_argument("--max-tokens", type=int, default=350)
    ap.add_argument("--voice-mode", action="store_true", help="Truncate long answers for voice UX.")
    ap.add_argument("--timeout", type=float, default=20.0, help="HTTP read/write timeout (seconds)")
    ap.add_argument("--insecure", action="store_true", help="Disable TLS verification (debug only)")
    ap.add_argument("--proxy", help="HTTP/HTTPS proxy URL; sets HTTP(S)_PROXY env for this run")
    ap.add_argument("--use-responses", action="store_true", help="Use Responses API instead of Chat")
    ap.add_argument("--quiet", action="store_true", help="Reduce console logs")
    args = ap.parse_args()

    logger = Logger(enabled=not args.quiet)
    logger.log("=== Pharmacy Prompt Runner starting ===")

    prompt_path = Path(args.prompt_file)
    tests_path = Path(args.tests_file)
    outdir = Path(args.outdir)
    ensure_dir(outdir)

    logger.log(f"Loading system prompt from: {prompt_path}")
    system_prompt = read_textfile(prompt_path)
    if not system_prompt.strip():
        raise RuntimeError(f"{prompt_path} is empty. Paste your pharmacist prompt there.")

    logger.log(f"Loading tests from: {tests_path}")
    test_inputs = read_tests(tests_path)
    if not test_inputs:
        raise RuntimeError(f"{tests_path} has no tests. Add one question per line.")
    logger.log(f"Loaded {len(test_inputs)} tests.")

    logger.log("Constructing OpenAI client...")
    client = OpenAIClientWrapper(
        api_key=args.api_key,
        base_url=args.base_url,
        timeout=args.timeout,
        insecure=args.insecure,
        proxy=args.proxy,
        use_responses=args.use_responses,
        logger=logger,
    )

    logger.log("Running preflight connectivity check...")
    preflight_check(client._httpx, client.api_key, client.base_url, logger)  # type: ignore[attr-defined]

    results_path = outdir / "results.jsonl"
    report_path = outdir / "report.html"
    summary_path = outdir / "last_run_summary.json"

    rows: List[Dict[str, Any]] = []
    started = time.time()

    logger.log("=== Beginning test run ===")
    for idx, q in enumerate(test_inputs, 1):
        logger.log(f"[{idx}/{len(test_inputs)}] Sending query: {q[:80]}{'...' if len(q)>80 else ''}")
        try:
            answer = client.run(
                model=args.model,
                system_prompt=system_prompt,
                user_input=q,
                max_tokens=args.max_tokens,
            )
            if args.voice_mode and isinstance(answer, str) and len(answer) > 600:
                answer = answer[:600].rstrip() + "…"
            record: Dict[str, Any] = {
                "index": idx,
                "timestamp": now_iso(),
                "model": args.model,
                "user_input": q,
                "assistant_output": answer,
            }
            logger.log(f"[{idx}] OK (len={len(answer) if isinstance(answer, str) else 'n/a'})")
        except Exception as e:
            # Unwrap Tenacity's RetryError to show the real cause
            if isinstance(e, RetryError) and e.last_attempt:
                root = e.last_attempt.exception()
                root_msg = f"{type(root).__name__}: {root}"
                errmsg = f"RetryError after {e.last_attempt.attempt_number} attempts | root: {root_msg}"
            else:
                errmsg = f"{type(e).__name__}: {e}"

            record = {
                "index": idx,
                "timestamp": now_iso(),
                "model": args.model,
                "user_input": q,
                "error": errmsg,
            }
            logger.log(f"[{idx}] ERROR: {errmsg}")

        rows.append(record)

    # Write JSONL
    logger.log(f"Writing JSONL results -> {results_path}")
    with results_path.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    logger.log("JSONL written.")

    # Write HTML
    build_html_report(rows, report_path, logger)

    # Write summary
    took = time.time() - started
    summary: Dict[str, Any] = {
        "started": now_iso(),
        "num_tests": len(rows),
        "num_errors": sum(1 for r in rows if "error" in r),
        "results_path": str(results_path),
        "report_path": str(report_path),
        "took_seconds": round(took, 2),
        "model": args.model,
        "mode": "responses" if args.use_responses else "chat",
    }
    logger.log(f"Writing summary -> {summary_path}")
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    logger.log("Summary written.")

    logger.log("=== Done ===")
    print(f"Wrote: {results_path}")
    print(f"Wrote: {report_path}")
    print(f"Wrote: {summary_path}")


if __name__ == "__main__":
    main()
