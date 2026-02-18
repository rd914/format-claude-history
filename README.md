# chformat

A command-line tool to convert a Claude Code history file to readable format.

## Usage

python3 chformat.py <history-file-name> [--trim NN]

where

<history-file-Rame>: path/filename of the Claude Code history file

[--trim NN]: display only the first NN words of each prompt

## Background

Claude Code creates a file with a history of every prompt it is given. It can be
interesting but it's hard to read because it's a JSON file, with one JSON object
per prompt and the entire object on one line. Also, the date and time are
represented by an integer timestamp in milliseconds after the Unix epoch.

This program converts the file into a human-readable format, optionally
truncating long prompts (some can be _very_ long, especially the "plans" written
by Claude for complex changes).

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

## Files

- MacOS: /home/<userid>/.claude/history.jsonl

- Microsoft Windows: /Users/<userid>/.claude/history.jsonl

## Requirements

Python 3.6+. No third-party dependencies.
