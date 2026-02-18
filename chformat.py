#!/usr/bin/env python3
"""
Convert a JSON file of records to human-readable output.

Each record must have:
  "timestamp" - Unix time in milliseconds
  "display"   - text to display

Handles malformed JSON (missing outer brackets, trailing commas, NDJSON, etc.)
"""

import sys
import argparse
import json
import re
import textwrap
import shutil
from datetime import datetime


def parse_timestamp(ts_ms):
    """Convert a millisecond epoch timestamp to yyyy-mm-dd hh:mi:ss.mmm."""
    ts_ms = int(ts_ms)
    dt = datetime.fromtimestamp(ts_ms / 1000.0)
    ms = ts_ms % 1000
    return dt.strftime("%Y-%m-%d %H:%M:%S") + f".{ms:03d}"


def trim_words(text, max_words):
    """Return text truncated to max_words words, with '...' appended if trimmed."""
    words = text.split()
    if len(words) <= max_words:
        return text
    return " ".join(words[:max_words]) + "..."


def format_record(record, term_width, trim=None):
    """Return a formatted string for one record."""
    ts_str = parse_timestamp(record.get("timestamp", 0))
    display = str(record.get("display", ""))

    if trim is not None:
        display = trim_words(display, trim)

    separator = "  "
    indent = " " * (len(ts_str) + len(separator))
    text_width = max(term_width - len(indent), 20)

    lines = textwrap.wrap(display, width=text_width) if display.strip() else [""]

    result = f"{ts_str}{separator}{lines[0]}"
    for line in lines[1:]:
        result += f"\n{indent}{line}"
    return result


def extract_records(text):
    """
    Try several strategies to extract a list of dicts from potentially
    malformed JSON text.
    """
    # 1. Try parsing as-is (valid JSON array or single object).
    try:
        data = json.loads(text)
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            return [data]
    except json.JSONDecodeError:
        pass

    # 2. Wrap in [ ] after stripping a trailing comma — handles files that
    #    are "almost" a JSON array (missing the outer brackets, or having a
    #    trailing comma after the last element).
    try:
        data = json.loads("[" + text.strip().rstrip(",") + "]")
        if isinstance(data, list):
            return data
    except json.JSONDecodeError:
        pass

    # 3. Newline-delimited JSON (NDJSON / JSON Lines), optionally with
    #    trailing commas on each line.
    records = []
    for line in text.splitlines():
        line = line.strip().rstrip(",")
        if not line:
            continue
        try:
            obj = json.loads(line)
            if isinstance(obj, dict):
                records.append(obj)
        except json.JSONDecodeError:
            pass
    if records:
        return records

    # 4. Last resort: scan the raw text for balanced JSON objects.
    records = []
    decoder = json.JSONDecoder()
    pos = 0
    while pos < len(text):
        match = re.search(r"\{", text[pos:])
        if not match:
            break
        start = pos + match.start()
        try:
            obj, end = decoder.raw_decode(text, start)
            if isinstance(obj, dict):
                records.append(obj)
            pos = end
        except json.JSONDecodeError:
            pos = start + 1

    return records


def main():
    parser = argparse.ArgumentParser(description="Display JSON records in human-readable format.")
    parser.add_argument("file", help="JSON file to read")
    parser.add_argument("--trim", type=int, metavar="N",
                        help="Truncate display text to N words, appending '...' if trimmed")
    args = parser.parse_args()

    filename = args.file

    try:
        with open(filename, "r", encoding="utf-8") as f:
            text = f.read()
    except FileNotFoundError:
        print(f"Error: '{filename}' not found.", file=sys.stderr)
        sys.exit(1)
    except OSError as e:
        print(f"Error reading '{filename}': {e}", file=sys.stderr)
        sys.exit(1)

    records = extract_records(text)

    if not records:
        print("No JSON records found.", file=sys.stderr)
        sys.exit(1)

    term_width = shutil.get_terminal_size((120, 24)).columns

    for i, record in enumerate(records):
        if i > 0:
            print()
        print(format_record(record, term_width, trim=args.trim))


if __name__ == "__main__":
    main()
