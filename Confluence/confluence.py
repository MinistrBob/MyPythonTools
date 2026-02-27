#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Скачивает конкретное вложение со страницы Confluence без дополнительных данных.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Dict, Optional, Union

from settings import app_settings as appset

log = appset.log

try:
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
except Exception:  # pragma: no cover
    print("Не найден модуль requests. Установите: pip install requests", file=sys.stderr)
    raise


def _request_json(
    session: requests.Session,
    url: str,
    params: Optional[Dict[str, str]] = None,
    timeout: float = appset.timeout,
) -> Dict:
    log.info("Запрос JSON: %s params=%s", url, params)
    response = session.get(url, params=params, timeout=timeout)
    response.raise_for_status()
    return response.json()


def _get_attachment_by_title(
    session: requests.Session,
    base_url: str,
    page_id: str,
    title: str,
    timeout: float = appset.timeout,
) -> Dict:
    url = f"{base_url}/rest/api/content/{page_id}/child/attachment"
    data = _request_json(session, url, params={"filename": title}, timeout=timeout)
    results = data.get("results", [])
    for item in results:
        if item.get("title") == title:
            return item
    if results:
        return results[0]
    raise RuntimeError(f"Вложение не найдено: {title}")


def _download_attachment(
    session: requests.Session,
    base_url: str,
    attachment: Dict,
    out_path: Path,
    timeout: float = appset.timeout,
) -> Path:
    title = attachment.get("title") or "attachment"
    download_rel = attachment.get("_links", {}).get("download")
    if not download_rel:
        raise RuntimeError(f"Не найден download link для вложения: {title}")
    download_url = f"{base_url}{download_rel}"

    log.info("Скачивание вложения: %s", title)
    with session.get(download_url, stream=True, timeout=timeout) as response:
        response.raise_for_status()
        with open(out_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    f.write(chunk)
    log.info("Вложение сохранено: %s", out_path)
    return out_path


def build_session(
    username: str,
    password: str,
    verify: Union[bool, str],
    retries: int,
    backoff: float,
) -> requests.Session:
    log.info("Инициализация HTTP-сессии: user=%s", username)
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
    log.info("HTTP-сессия готова")
    return session


def main() -> int:
    log.info("Старт загрузки вложения Confluence")

    username = appset.username
    password = appset.password
    if not username or not password:
        log.error("Не заданы учетные данные Confluence. Заполните username/password в profiles.py.")
        return 1
    log.info("Используется пользователь: %s", username)

    output_path = Path.cwd() / appset.output_filename
    log.info("Файл сохранения: %s", output_path)

    if appset.insecure:
        verify_value: Union[bool, str] = False
        log.info("Проверка TLS отключена")
    elif appset.ca_bundle:
        verify_value = str(Path(appset.ca_bundle))
        log.info("Используется CA bundle: %s", verify_value)
    else:
        verify_value = True
        log.info("Проверка TLS включена")

    session = build_session(
        username,
        password,
        verify=verify_value,
        retries=appset.retries,
        backoff=appset.retry_backoff,
    )

    attachment = _get_attachment_by_title(
        session,
        appset.base_url,
        appset.page_id,
        appset.attachment_title,
        timeout=appset.timeout,
    )
    out_path = _download_attachment(
        session,
        appset.base_url,
        attachment,
        output_path,
        timeout=appset.timeout,
    )

    log.info("Сохранено вложение: %s", out_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
