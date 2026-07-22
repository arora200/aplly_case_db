# Dataset: Caching Strategy for Read-Heavy API

## Case Reference
- **Case ID:** 6
- **Title:** Caching Strategy for Read-Heavy API
- **Difficulty:** Expert
- **Thinking Type:** Algorithmic

## Files in this folder

| File | Rows | Columns | Description |
|------|------|---------|-------------|
| traffic_pattern.csv | 4 | 3 | Read/write per hour block |
| latency_baseline.csv | 3 | 2 | p50/p95/p99 latency |
| design_constraints.csv | 6 | 2 | Budget, staleness, data change |

## Source
Synthetic API traffic data.

Seed: `aplly-2026-07-22` — deterministic, reproducible.
License: MIT