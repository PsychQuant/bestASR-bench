#!/usr/bin/env python3
"""Mechanical measurement checks for bestASR-bench CI (stdlib only).

Validates every measurements/*.jsonl row:
  1. required keys present (MeasurementRow snake_case + denormalized
     contributor / chip / unified_memory_gb — see SUBMISSION_FORMAT.md)
  2. ranges: 0 <= error_rate <= 10, rtf > 0, peak_memory_gb >= 0 (0 = the
     probe could not capture peak memory for that backend — a legitimate
     bestASR measurement), unified_memory_gb > 0, metric_kind in {wer, cer}
  3. corpus_id exists in corpus/manifest.jsonl
  4. no duplicate rows repo-wide (bitwise-identical JSON)
Soft outlier flag (never fails CI): a row whose error_rate deviates from the
median of its (chip, model_id, corpus_id) group by > 3x MAD is printed as
"⚠ outlier" for human review — transparency over pretended verification.
Exit 0 when all hard checks pass; exit 1 otherwise.
"""
import glob
import json
import os
import statistics
import sys

REQUIRED = {
    "model_id", "corpus_id", "machine_id", "measured_at", "metric_kind",
    "error_rate", "rtf", "peak_memory_gb", "warmup_seconds", "app_version",
    "macos_version", "contributor", "chip", "unified_memory_gb",
}


def load_jsonl(path):
    with open(path, encoding="utf-8") as f:
        for lineno, line in enumerate(f, 1):
            line = line.strip()
            if line:
                yield lineno, line


def main():
    repo = sys.argv[1] if len(sys.argv) > 1 else "."
    manifest_ids = set()
    manifest_path = os.path.join(repo, "corpus", "manifest.jsonl")
    if os.path.exists(manifest_path):
        for _, line in load_jsonl(manifest_path):
            try:
                manifest_ids.add(json.loads(line)["corpus_id"])
            except (json.JSONDecodeError, KeyError):
                pass

    errors, seen, groups = [], {}, {}
    files = sorted(glob.glob(os.path.join(repo, "measurements", "*.jsonl")))
    total = 0
    for path in files:
        rel = os.path.relpath(path, repo)
        for lineno, line in load_jsonl(path):
            where = f"{rel}:{lineno}"
            try:
                row = json.loads(line)
            except json.JSONDecodeError as e:
                errors.append(f"{where}: malformed JSON ({e})")
                continue
            total += 1
            missing = REQUIRED - set(row)
            if missing:
                errors.append(f"{where}: missing keys {sorted(missing)}")
                continue
            # WER/CER legitimately exceed 1.0 on insertion-heavy garbage output
            # (e.g. an English-only backend on zh audio); 10 = sanity ceiling.
            if not (isinstance(row["error_rate"], (int, float)) and 0 <= row["error_rate"] <= 10):
                errors.append(f"{where}: error_rate out of [0,10]")
            if not (isinstance(row["rtf"], (int, float)) and row["rtf"] > 0):
                errors.append(f"{where}: rtf must be > 0")
            if not (isinstance(row["peak_memory_gb"], (int, float)) and row["peak_memory_gb"] >= 0):
                errors.append(f"{where}: peak_memory_gb must be >= 0")
            if not (isinstance(row["unified_memory_gb"], (int, float)) and row["unified_memory_gb"] > 0):
                errors.append(f"{where}: unified_memory_gb must be > 0")
            if row["metric_kind"] not in ("wer", "cer"):
                errors.append(f"{where}: metric_kind must be wer|cer")
            if manifest_ids and row["corpus_id"] not in manifest_ids:
                errors.append(f"{where}: corpus_id '{row['corpus_id']}' not in corpus/manifest.jsonl")
            canonical = json.dumps(row, sort_keys=True)
            if canonical in seen:
                errors.append(f"{where}: duplicate of {seen[canonical]}")
            else:
                seen[canonical] = where
            key = (row.get("chip"), row.get("model_id"), row.get("corpus_id"))
            groups.setdefault(key, []).append((where, row.get("error_rate")))

    # Soft outlier flags (never fail CI).
    for key, members in groups.items():
        vals = [v for _, v in members if isinstance(v, (int, float))]
        if len(vals) < 3:
            continue
        med = statistics.median(vals)
        mad = statistics.median(abs(v - med) for v in vals) or 1e-9
        for where, v in members:
            if isinstance(v, (int, float)) and abs(v - med) / mad > 3:
                print(f"⚠ outlier (human review): {where} error_rate={v} vs group median {med:.4f} {key}")

    if errors:
        for e in errors:
            print(f"✗ {e}", file=sys.stderr)
        return 1
    print(f"OK {total} rows across {len(files)} file(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
