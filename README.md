# chformat

A command-line tool that converts a JSON file of timestamped records into a
human-readable, word-wrapped format.

## Input format

Each record must be a JSON object with two fields:

| Field | Type | Description |
|-------|------|-------------|
| `timestamp` | integer | Unix time in **milliseconds** |
| `display` | string | Text to display |

The file can be a valid JSON array, a single JSON object, newline-delimited
JSON (NDJSON), or any of these with missing outer brackets or trailing commas.

## Output format

Each record is printed as a single block: the timestamp on the left, with the
display text word-wrapped and aligned to the right of it. Records are separated
by a blank line.

```
2024-03-15 09:22:11.043  First line of the display text, which may be
                         long enough to wrap onto subsequent lines that
                         are indented to align with the first line.

2024-03-15 09:22:14.801  Another record.
```

The text wraps to fit the terminal width.

## Usage

```
python3 chformat.py [--trim N] <file>
```

### Options

| Option | Description |
|--------|-------------|
| `--trim N` | Truncate display text to N words, appending `...` if trimmed |

### Examples

```bash
# Display all records
python3 chformat.py history.json

# Show only the first 20 words of each record's display text
python3 chformat.py --trim 20 history.json
```

## Requirements

Python 3.6+. No third-party dependencies.
