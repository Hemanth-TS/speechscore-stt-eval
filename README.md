# SpeechScore / STT Evaluation

![Tests](https://github.com/Hemanth-TS/speechscore-stt-eval/actions/workflows/tests.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.11%2B-3776AB)
![License](https://img.shields.io/badge/license-MIT-22c55e)

A transcript evaluation harness with word alignment, micro-averaged WER, CER and per-language breakdowns.

> **New portfolio demo · created 30 October 2026.** This is an original,
> AI-assisted implementation created for this portfolio. It is not a past
> client delivery, production deployment, or evidence of commercial results.
> All supplied data is synthetic. No popular project was copied or forked.

## Run in under a minute

Only Python 3.11 or later is required. No API keys, model downloads,
paid services or third-party Python packages are needed.

```sh
git clone https://github.com/Hemanth-TS/speechscore-stt-eval.git
cd speechscore-stt-eval
python speechscore.py
python -m unittest discover -s tests -v
```

## Metrics and interpretation

Word error rate is `(substitutions + deletions + insertions) / reference words`.
The corpus score sums counts before dividing (micro averaging). CER uses the
same edit distance on normalized characters with spaces removed. NFKC,
case folding and punctuation-to-space normalization are explicit and fixed.
An empty reference has an undefined rate (`null`); its insertions still count
in corpus totals. WER can exceed 100%. Latencies are **supplied measurements**,
reported with nearest-rank percentiles, not timings collected by this harness.

The supplied fixture has 3 word errors over 16 reference words: WER **0.1875**.
Inspect `segments[].alignment` to distinguish substitutions from insertions.

## Input contract

Provide a JSON array with unique string `id`, `reference`, `hypothesis`,
optional `language`, and optional nonnegative `latency_ms`. Run
`python speechscore.py path/to/transcripts.json`. Output is JSON on stdout;
redirect it to save a report. No audio or real patient data is included.

## Limits

This evaluates transcripts; it does not transcribe audio, compare live vendors,
measure acoustic quality or establish multilingual accuracy. Word tokenization
uses whitespace and is unsuitable for languages requiring segmentation.
The alignment matrix is quadratic and capped at two million cells per pair.
Punctuation normalization also splits contractions and decimal values.
The four toy records are fixtures, not a representative benchmark.


## Repository guide

- `speechscore.py`: implementation and command-line interface.
- `samples/`: fictional input fixtures; safe to edit and reuse.
- `tests/`: regression tests, including boundary cases.
- `.github/workflows/tests.yml`: automated Windows/Linux checks.
- [CHANGELOG.md](CHANGELOG.md): release notes.
- [CONTRIBUTING.md](CONTRIBUTING.md): development and bug-report guidance.

## Maintenance and provenance

Version **0.1.0** is an educational demo, with no production support commitment.
Changes should include a regression test and an entry in the changelog.
Algorithms are implemented directly in this repository; there are no vendored
models, third-party source files, proprietary assets or external datasets.
Badges show GitHub's current CI status; sample outputs are not independent benchmarks.

[Portfolio](https://hemanth-ts.github.io/) · [MIT license](LICENSE)
