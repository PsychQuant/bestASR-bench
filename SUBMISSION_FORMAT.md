# Submission format

## Measurements（`bestasr bench submit` 產生）

- **檔名**：`measurements/<UTC ISO-8601 basic, e.g. 20260718T093000Z>-<contributor>-<machine_id 前 12 碼>.jsonl` — 每次提交一檔，append-only（PR 不改既有檔）。
- **每列**（JSONL）= bestASR `MeasurementRow` 的 snake_case 欄位 **＋ 3 個 denormalize 欄**（讓 repo 檔自足、不需另查 machines 表）：

```json
{"model_id": "whisperkit|whisper|large-v3|default", "corpus_id": "abc123abc123",
 "machine_id": "0f3a…", "measured_at": "2026-07-18T09:30:00Z", "metric_kind": "cer",
 "error_rate": 0.129, "rtf": 0.14, "peak_memory_gb": 3.1, "warmup_seconds": 8.2,
 "app_version": "0.14.0", "macos_version": "26.0", "context_error_rate": null,
 "hf_revision": null,
 "contributor": "your-github-handle", "chip": "Apple M4 Max", "unified_memory_gb": 128}
```

- `corpus_id` 必須存在於 `corpus/manifest.jsonl`（只有對正典 corpus 的量測可比）。
- CI（`tools/validate_measurements.py`）做 schema / 值域 / corpus 存在 / 去重的硬檢查，＋ 3×MAD 離群**軟標記**（僅供人審，不擋）。

## Corpus manifest（`bestasr corpus contribute` 產生）

- `corpus/manifest.jsonl` 每列 = bestASR `CorpusManifestRow`（見 bestASR repo `Sources/BestASRKit/Contribution/CorpusManifest.swift`）。
- license ∈ `{CC0, CC-BY, CC-BY-SA, public-domain, own-consented}`；attribution 必填；音訊本體住 HF dataset `bestasr-corpus`，此 repo 只存 hash 與指標。
- CI（`tools/validate_manifest.py`）機械檢查；corpus PR 另需人工審（授權查核＋參考稿品質）。
