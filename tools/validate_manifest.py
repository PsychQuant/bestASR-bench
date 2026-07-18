#!/usr/bin/env python3
"""Mechanical corpus-manifest checks for bestASR-bench CI.

Mirror of BestASRKit ManifestValidator (Sources/BestASRKit/Contribution/
ManifestValidator.swift) — keep the two in sync. Rules:
  1. license ∈ allow-list {CC0, CC-BY, CC-BY-SA, public-domain, own-consented}
  2. attribution is non-blank
  3. audio_sha256 / reference_sha256 are 64 hex chars
  4. corpus_id is unique across rows
JSONL: one row per line, blank lines skipped. Exit 0 + "OK <N> rows" when
clean; exit 1 with one line per error otherwise.
"""
import json
import sys

ALLOWED_LICENSES = {"CC0", "CC-BY", "CC-BY-SA", "public-domain", "own-consented"}
REQUIRED_KEYS = {
    "corpus_id", "name", "language", "audio_sha256", "reference_sha256",
    "duration", "license", "attribution", "contributor",
    "reference_provenance", "hf_audio_path", "hf_reference_path",
}


def is_hex64(s):
    return isinstance(s, str) and len(s) == 64 and all(c in "0123456789abcdefABCDEF" for c in s)


def validate(path):
    errors = []
    seen = set()
    rows = 0
    with open(path, encoding="utf-8") as f:
        for lineno, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as e:
                errors.append(f"line {lineno}: malformed JSON ({e})")
                continue
            rows += 1
            cid = row.get("corpus_id", f"<line {lineno}>")
            missing = REQUIRED_KEYS - set(row)
            if missing:
                errors.append(f"{cid}: missing keys {sorted(missing)}")
            if row.get("license") not in ALLOWED_LICENSES:
                errors.append(f"{cid}: license '{row.get('license')}' not in allow-list")
            if not str(row.get("attribution", "")).strip():
                errors.append(f"{cid}: attribution is empty")
            if not is_hex64(row.get("audio_sha256")):
                errors.append(f"{cid}: audio_sha256 is not 64 hex chars")
            if not is_hex64(row.get("reference_sha256")):
                errors.append(f"{cid}: reference_sha256 is not 64 hex chars")
            if cid in seen:
                errors.append(f"{cid}: duplicate corpus_id")
            seen.add(cid)
    return rows, errors


def main():
    if len(sys.argv) != 2:
        print("usage: validate_manifest.py <manifest.jsonl>", file=sys.stderr)
        return 2
    rows, errors = validate(sys.argv[1])
    if errors:
        for e in errors:
            print(f"✗ {e}", file=sys.stderr)
        return 1
    print(f"OK {rows} rows")
    return 0


if __name__ == "__main__":
    sys.exit(main())
