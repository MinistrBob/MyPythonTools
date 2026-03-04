import json
import sys
from datetime import date
from html.parser import HTMLParser
from pathlib import Path
from typing import Any


class ConfluenceTableParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._in_target_table = False
        self._table_found = False
        self._in_row = False
        self._in_cell = False
        self._current_row: list[str] = []
        self._current_cell_parts: list[str] = []
        self.rows: list[list[str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "table" and not self._table_found:
            attrs_dict = dict(attrs)
            class_value = attrs_dict.get("class", "") or ""
            if "confluenceTable" in class_value:
                self._in_target_table = True
                self._table_found = True
            return

        if not self._in_target_table:
            return

        if tag == "tr":
            self._in_row = True
            self._current_row = []
            return

        if tag in {"td", "th"}:
            self._in_cell = True
            self._current_cell_parts = []
            return

        if tag == "br" and self._in_cell:
            self._current_cell_parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if not self._in_target_table:
            return

        if tag in {"td", "th"} and self._in_cell:
            raw_text = "".join(self._current_cell_parts)
            normalized = raw_text.replace("\xa0", " ").strip()
            self._current_row.append(normalized)
            self._current_cell_parts = []
            self._in_cell = False
            return

        if tag == "tr" and self._in_row:
            if self._current_row:
                self.rows.append(self._current_row)
            self._current_row = []
            self._in_row = False
            return

        if tag == "table" and self._in_target_table:
            self._in_target_table = False

    def handle_data(self, data: str) -> None:
        if self._in_cell:
            self._current_cell_parts.append(data)


def extract_html_content(data: dict[str, Any]) -> str:
    return data["data"]["htmlContent"][0]["html"]


def parse_confluence_table(html: str) -> list[dict[str, Any]]:
    parser = ConfluenceTableParser()
    parser.feed(html)

    if not parser.rows:
        return []

    headers = [header.strip() for header in parser.rows[0]]
    header_map = {
        "ФИО": "fio",
        "День рождения": "date1",
        "Для сортировки по дате": "date2",
        "Имя в telegram": "telegram",
        "Компания": "company",
    }
    items: list[dict[str, Any]] = []

    for row in parser.rows[1:]:
        row_cells = row + [""] * max(0, len(headers) - len(row))
        record: dict[str, Any] = {}

        for header, cell in zip(headers, row_cells, strict=False):
            if header == "№":
                continue

            output_key = header_map.get(header)
            if not output_key:
                continue

            if output_key == "company":
                parts = [part.strip() for part in cell.split("\n") if part.strip()]
                record[output_key] = parts if len(parts) > 1 else (parts[0] if parts else "")
            else:
                record[output_key] = cell.strip()

        items.append(record)

    return items


def main() -> int:
    source_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("db.ssc")

    try:
        with source_path.open("r", encoding="utf-8") as file:
            payload = json.load(file)
    except FileNotFoundError:
        print(f"Файл не найден: {source_path}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as exc:
        print(f"Некорректный JSON в файле {source_path}: {exc}", file=sys.stderr)
        return 1

    try:
        html = extract_html_content(payload)
    except (KeyError, IndexError, TypeError) as exc:
        print(
            f"Не удалось извлечь data.htmlContent[0].html из {source_path}: {exc}",
            file=sys.stderr,
        )
        return 1

    table_data = parse_confluence_table(html)
    today_key = date.today().strftime("%m-%d")
    today_birthdays = [row for row in table_data if row.get("date2") == today_key]
    print(today_birthdays)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
