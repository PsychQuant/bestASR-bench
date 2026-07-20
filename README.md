# bestASR-bench

Community benchmark for Apple-silicon **local ASR backends** (WhisperKit, whisper.cpp, FluidAudio Parakeet / Paraformer / SenseVoice, mlx-audio) — measurements + corpus manifest + leaderboard.

Sibling of [bestASR](https://github.com/PsychQuant/bestASR), which measures how ASR backends actually perform on YOUR machine and routes to the best one.

## Layout

| Path | Contents |
|---|---|
| `measurements/*.jsonl` | Community-submitted measurement rows (`machine × backend × model × corpus → WER/CER, RTF, memory`), append-only via PR |
| `corpus/manifest.jsonl` | Canonical corpus manifest — identity hashes + license + attribution, pointing into the [bestasr-corpus](https://huggingface.co/datasets/PsychQuant/bestasr-corpus) HF dataset (audio never lives here) |
| `leaderboard/` | Auto-generated from measurements (median ± MAD, self-reported, N contributors) |
| `tools/` | CI validators + leaderboard generator |

## Contributing

- **Measurements** (low friction): `bestasr corpus pull` → `bestasr benchmark` → `bestasr bench submit` (opens a PR here). CI validates schema/ranges/known corpus SHAs.
- **Corpus** (reviewed): `bestasr corpus contribute` — license gate (CC0 / CC-BY / CC-BY-SA / public-domain / own-consented) + human review.

Schema source of truth: `BestASRKit` `Contribution/` types (CorpusManifestRow, CorpusLicense, ManifestValidator) in the bestASR repo.

## Trust model

Numbers are **self-reported** with rich provenance (machine, OS, app version, model revision, corpus SHA). CI adds statistical outlier flags for human review — transparency over pretended verification.
