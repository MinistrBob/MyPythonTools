#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Скачивает HTML страницы Confluence и все вложения (attachments) без конвертации.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from getpass import getpass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Union
from settings import app_settings as appset

try:
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
except Exception as exc:  # pragma: no cover
    print("Не найден модуль requests. Установите: pip install requests", file=sys.stderr)
    raise


def _request_json(
    session: requests.Session,
    url: str,
    params: Optional[Dict[str, str]] = None,
    timeout: float = appset.timeout,
) -> Dict:
    response = session.get(url, params=params, timeout=timeout)
    response.raise_for_status()
    return response.json()


def _iter_attachments(
    session: requests.Session,
    base_url: str,
    page_id: str,
    timeout: float = appset.timeout,
) -> Iterable[Dict]:
    start = 0
    limit = 50
    while True:
        url = f"{base_url}/rest/api/content/{page_id}/child/attachment"
        data = _request_json(
            session,
            url,
            params={"start": str(start), "limit": str(limit)},
            timeout=timeout,
        )
        results = data.get("results", [])
        for item in results:
            yield item
        if not data.get("_links", {}).get("next"):
            break
        start += limit


def _download_attachment(
    session: requests.Session,
    base_url: str,
    attachment: Dict,
    out_dir: Path,
    timeout: float = appset.timeout,
) -> Path:
    title = attachment.get("title") or "attachment"
    safe_name = title.replace("/", "_").replace("\\", "_")
    download_rel = attachment.get("_links", {}).get("download")
    if not download_rel:
        raise RuntimeError(f"Не найден download link для вложения: {title}")
    download_url = f"{base_url}{download_rel}"
    out_path = out_dir / safe_name

    with session.get(download_url, stream=True, timeout=timeout) as response:
        response.raise_for_status()
        with open(out_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    f.write(chunk)
    return out_path


def _save_page_html(
    session: requests.Session,
    base_url: str,
    page_id: str,
    out_dir: Path,
    timeout: float = appset.timeout,
) -> Path:
    url = f"{base_url}/rest/api/content/{page_id}"
    data = _request_json(session, url, params={"expand": "body.storage"}, timeout=timeout)
    html = data.get("body", {}).get("storage", {}).get("value", "")
    out_path = out_dir / f"page_{page_id}.html"
    out_path.write_text(html, encoding="utf-8")
    return out_path


def _save_metadata(data: Dict, out_dir: Path, page_id: str) -> Path:
    out_path = out_dir / f"page_{page_id}_meta.json"
    out_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return out_path


def build_session(
    username: str,
    password: str,
    verify: Union[bool, str],
    retries: int,
    backoff: float,
) -> requests.Session:
    session = requests.Session()
    session.auth = (username, password)
    session.verify = verify
    session.headers.update({"Accept": "application/json"})

    retry = Retry(
        total=retries,
        connect=retries,
        read=retries,
        status=retries,
        backoff_factor=backoff,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"],
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Скачивание страницы Confluence и вложений")
    parser.add_argument("--base-url", default=appset.base_url, help="Базовый URL Confluence")
    parser.add_argument("--page-id", default=appset.page_id, help="ID страницы")
    parser.add_argument("--out", default=appset.out, help="Каталог для сохранения")
    parser.add_argument("--username", default=appset.username, help="Логин Confluence")
    parser.add_argument("--password", default=appset.password, help="Пароль Confluence")
    parser.add_argument("--insecure", action="store_true", help="Отключить проверку TLS сертификата")
    parser.add_argument(
        "--ca-bundle",
        default=appset.ca_bundle,
        help="Путь к CA bundle (PEM/CRT) для проверки TLS",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=appset.timeout,
        help="Таймаут запроса (секунды)",
    )
    parser.add_argument(
        "--retries",
        type=int,
        default=appset.retries,
        help="Количество повторов при сетевых ошибках",
    )
    parser.add_argument(
        "--retry-backoff",
        type=float,
        default=appset.retry_backoff,
        help="Backoff-фактор для повторов",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    username = args.username
    password = args.password
    if not username:
        username = input("Confluence login: ").strip()
    if not password:
        password = getpass("Confluence password: ")

    out_dir = Path(__file__).parent / args.out
    out_dir.mkdir(parents=True, exist_ok=True)

    if args.insecure or appset.insecure:
        verify_value: Union[bool, str] = False
    elif args.ca_bundle:
        verify_value = str(Path(args.ca_bundle))
    else:
        verify_value = True

    session = build_session(
        username,
        password,
        verify=verify_value,
        retries=args.retries,
        backoff=args.retry_backoff,
    )

    page_url = f"{args.base_url}/rest/api/content/{args.page_id}"
    page_data = _request_json(
        session,
        page_url,
        params={"expand": "body.storage"},
        timeout=args.timeout,
    )

    page_html_path = _save_page_html(
        session,
        args.base_url,
        args.page_id,
        out_dir,
        timeout=args.timeout,
    )
    meta_path = _save_metadata(page_data, out_dir, args.page_id)

    attachments_dir = out_dir / "attachments"
    attachments_dir.mkdir(parents=True, exist_ok=True)

    downloaded: List[Path] = []
    for attachment in _iter_attachments(
        session,
        args.base_url,
        args.page_id,
        timeout=args.timeout,
    ):
        downloaded.append(
            _download_attachment(
                session,
                args.base_url,
                attachment,
                attachments_dir,
                timeout=args.timeout,
            )
        )

    print(f"Сохранен HTML: {page_html_path}")
    print(f"Сохранены метаданные: {meta_path}")
    print(f"Скачано вложений: {len(downloaded)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
