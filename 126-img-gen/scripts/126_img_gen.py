#!/usr/bin/env python3
"""Generate/edit images with 126 API and save the first result locally."""

from __future__ import annotations

import argparse
import base64
import json
import mimetypes
import os
import socket
import sys
import time
import uuid
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin
from urllib.request import Request, urlopen


DEFAULT_BASE_URL = "https://chx126.xyz/v1"
DEFAULT_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) 126-img-gen/1.0"
RETRY_ATTEMPTS = 4


def default_headers(api_key: str, content_type: str | None = None) -> dict[str, str]:
    headers = {
        "Authorization": f"Bearer {api_key}",
        "User-Agent": DEFAULT_USER_AGENT,
        "Accept": "application/json",
    }
    if content_type:
        headers["Content-Type"] = content_type
    return headers


def should_retry_http(status_code: int) -> bool:
    return status_code in {408, 409, 425, 429} or 500 <= status_code <= 599


def sleep_before_retry(attempt: int) -> None:
    time.sleep(min(2**attempt, 8))


def error_message(exc: BaseException) -> str:
    if isinstance(exc, URLError) and exc.reason:
        return str(exc.reason)
    return str(exc)


def env_api_key() -> str | None:
    for name in ("ONE_TWO_SIX_API_KEY", "126_API_KEY", "OPENAI_API_KEY"):
        value = os.getenv(name)
        if value:
            return value
    return None


def clean_base_url(base_url: str) -> str:
    return base_url.rstrip("/") + "/"


def request_json(
    method: str,
    url: str,
    api_key: str,
    payload: dict[str, Any] | None = None,
    extra_headers: dict[str, str] | None = None,
) -> dict[str, Any]:
    data = None
    headers = default_headers(api_key)
    if payload is not None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        headers["Content-Type"] = "application/json"
    if extra_headers:
        headers.update(extra_headers)
    last_error: BaseException | None = None
    for attempt in range(RETRY_ATTEMPTS):
        req = Request(url, data=data, headers=headers, method=method)
        try:
            with urlopen(req, timeout=120) as resp:
                text = resp.read().decode("utf-8")
                return json.loads(text)
        except HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            last_error = RuntimeError(f"HTTP {exc.code}: {body}")
            if attempt < RETRY_ATTEMPTS - 1 and should_retry_http(exc.code):
                sleep_before_retry(attempt)
                continue
            raise last_error from exc
        except (URLError, TimeoutError, socket.timeout) as exc:
            last_error = exc
            if attempt < RETRY_ATTEMPTS - 1:
                sleep_before_retry(attempt)
                continue
            raise RuntimeError(f"request failed: {error_message(exc)}") from exc
    raise RuntimeError(f"request failed: {error_message(last_error or RuntimeError('unknown error'))}")


def request_multipart(
    url: str,
    api_key: str,
    fields: dict[str, str],
    files: list[tuple[str, Path]],
) -> dict[str, Any]:
    boundary = "----126ImgGen" + uuid.uuid4().hex
    chunks: list[bytes] = []

    for name, value in fields.items():
        chunks.append(f"--{boundary}\r\n".encode())
        chunks.append(f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode())
        chunks.append(str(value).encode("utf-8"))
        chunks.append(b"\r\n")

    for name, path in files:
        content_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        chunks.append(f"--{boundary}\r\n".encode())
        chunks.append(
            (
                f'Content-Disposition: form-data; name="{name}"; '
                f'filename="{path.name}"\r\n'
                f"Content-Type: {content_type}\r\n\r\n"
            ).encode()
        )
        chunks.append(path.read_bytes())
        chunks.append(b"\r\n")

    chunks.append(f"--{boundary}--\r\n".encode())
    body = b"".join(chunks)
    last_error: BaseException | None = None
    for attempt in range(RETRY_ATTEMPTS):
        req = Request(
            url,
            data=body,
            headers=default_headers(api_key, f"multipart/form-data; boundary={boundary}"),
            method="POST",
        )
        try:
            with urlopen(req, timeout=180) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except HTTPError as exc:
            body_text = exc.read().decode("utf-8", errors="replace")
            last_error = RuntimeError(f"HTTP {exc.code}: {body_text}")
            if attempt < RETRY_ATTEMPTS - 1 and should_retry_http(exc.code):
                sleep_before_retry(attempt)
                continue
            raise last_error from exc
        except (URLError, TimeoutError, socket.timeout) as exc:
            last_error = exc
            if attempt < RETRY_ATTEMPTS - 1:
                sleep_before_retry(attempt)
                continue
            raise RuntimeError(f"request failed: {error_message(exc)}") from exc
    raise RuntimeError(f"request failed: {error_message(last_error or RuntimeError('unknown error'))}")


def download_url(url: str, out_path: Path) -> None:
    last_error: BaseException | None = None
    for attempt in range(RETRY_ATTEMPTS):
        req = Request(url, headers={"User-Agent": DEFAULT_USER_AGENT})
        try:
            with urlopen(req, timeout=180) as resp:
                out_path.write_bytes(resp.read())
                return
        except HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            last_error = RuntimeError(f"HTTP {exc.code}: {body}")
            if attempt < RETRY_ATTEMPTS - 1 and should_retry_http(exc.code):
                sleep_before_retry(attempt)
                continue
            raise last_error from exc
        except (URLError, TimeoutError, socket.timeout) as exc:
            last_error = exc
            if attempt < RETRY_ATTEMPTS - 1:
                sleep_before_retry(attempt)
                continue
            raise RuntimeError(f"download failed: {error_message(exc)}") from exc
    raise RuntimeError(f"download failed: {error_message(last_error or RuntimeError('unknown error'))}")


def source_label(value: str) -> str:
    if value.startswith("data:"):
        return "data_url"
    return value


def save_data_url(data_url: str, out_path: Path) -> None:
    if "," in data_url:
        _, encoded = data_url.split(",", 1)
    else:
        encoded = data_url
    out_path.write_bytes(base64.b64decode(encoded))


def save_first_result(result: dict[str, Any], out_path: Path) -> str:
    data = result.get("data")
    if isinstance(data, list) and data:
        item = data[0]
        if isinstance(item, dict):
            if item.get("url"):
                url = str(item["url"])
                download_url(url, out_path)
                return source_label(url)
            if item.get("b64_json"):
                save_data_url(str(item["b64_json"]), out_path)
                return "b64_json"
    if result.get("url"):
        url = str(result["url"])
        download_url(url, out_path)
        return source_label(url)
    raise RuntimeError("no image URL or b64_json found in response")


def image2_generation(args: argparse.Namespace, api_key: str, base_url: str) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "model": args.model or "image2",
        "prompt": args.prompt,
        "n": args.n,
        "size": args.size,
        "response_format": args.response_format,
    }
    for optional in ("quality", "style"):
        value = getattr(args, optional)
        if value:
            payload[optional] = value
    return request_json("POST", urljoin(base_url, "images/generations"), api_key, payload)


def image2_edit(args: argparse.Namespace, api_key: str, base_url: str) -> dict[str, Any]:
    if not args.image:
        raise RuntimeError("--image is required for --mode image2-edit")
    image_path = Path(args.image)
    if not image_path.exists():
        raise RuntimeError(f"image not found: {image_path}")
    fields = {
        "model": args.model or "image2",
        "prompt": args.prompt,
        "n": str(args.n),
        "size": args.size,
        "response_format": args.response_format,
    }
    files = [("image", image_path)]
    if args.mask:
        mask_path = Path(args.mask)
        if not mask_path.exists():
            raise RuntimeError(f"mask not found: {mask_path}")
        files.append(("mask", mask_path))
    return request_multipart(urljoin(base_url, "images/edits"), api_key, fields, files)


def gpt_image_task(args: argparse.Namespace, api_key: str, base_url: str) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "model": args.model or "gpt-image-2",
        "prompt": args.prompt,
    }
    if args.aspect_ratio:
        payload["aspect_ratio"] = args.aspect_ratio
    if args.ref_image:
        payload["images"] = args.ref_image

    created = request_json("POST", urljoin(base_url, "videos"), api_key, payload)
    task_id = created.get("id") or created.get("task_id")
    if not task_id:
        raise RuntimeError(f"no task id in response: {json.dumps(created, ensure_ascii=False)}")

    deadline = time.time() + args.timeout
    while time.time() < deadline:
        status = request_json("GET", urljoin(base_url, f"videos/{task_id}"), api_key)
        state = status.get("status")
        if state == "completed":
            return status
        if state == "failed":
            raise RuntimeError(f"task failed: {json.dumps(status, ensure_ascii=False)}")
        print(f"task {task_id}: {state or 'unknown'}", file=sys.stderr)
        time.sleep(args.poll_interval)
    raise RuntimeError(f"task timed out after {args.timeout}s: {task_id}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate/edit images with 126 API.")
    parser.add_argument("--mode", choices=["image2", "image2-edit", "gpt-image-2"], required=True)
    parser.add_argument("--prompt", required=True)
    parser.add_argument("--out", default="126-image.png", help="output image path")
    parser.add_argument("--api-key", default=env_api_key())
    parser.add_argument("--base-url", default=os.getenv("ONE_TWO_SIX_BASE_URL", DEFAULT_BASE_URL))
    parser.add_argument("--model", help="image2, gpt-image-2, gpt-image-2-2K, or gpt-image-2-4K")
    parser.add_argument("--size", default="1024x1024")
    parser.add_argument("--n", type=int, default=1)
    parser.add_argument("--response-format", default="url", choices=["url", "b64_json"])
    parser.add_argument("--quality")
    parser.add_argument("--style")
    parser.add_argument("--image", help="source image for image2-edit")
    parser.add_argument("--mask", help="optional mask image for image2-edit")
    parser.add_argument("--aspect-ratio", default="auto")
    parser.add_argument("--ref-image", action="append", help="reference image URL or Data URL for gpt-image-2")
    parser.add_argument("--poll-interval", type=float, default=3.0)
    parser.add_argument("--timeout", type=float, default=300.0)
    parser.add_argument("--print-json", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if not args.api_key:
        print("Missing API key. Set ONE_TWO_SIX_API_KEY or pass --api-key.", file=sys.stderr)
        return 2

    base_url = clean_base_url(args.base_url)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        if args.mode == "image2":
            result = image2_generation(args, args.api_key, base_url)
        elif args.mode == "image2-edit":
            result = image2_edit(args, args.api_key, base_url)
        else:
            result = gpt_image_task(args, args.api_key, base_url)

        source = save_first_result(result, out_path)
        print(f"saved: {out_path}")
        print(f"source: {source}")
        if args.print_json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
