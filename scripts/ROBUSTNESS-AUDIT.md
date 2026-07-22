# Upload Script Robustness Audit

> Based on issues observed during the Jul 14 & Jul 22, 2026 upload sessions.

---

## 🔴 Critical — Data Loss or Silent Failure Risk

### 1. No connection retry

A single transient timeout kills the entire session. Today's upload failed on the first attempt (20s TCP timeout to IPv4) and would have never recovered without manual intervention.

```
Cannot connect: 2003: Can't connect to MySQL server on 'srv818.hstgr.io:3306'
```

**Fix:** Wrap `mysql.connector.connect()` in a retry loop with exponential backoff:
- Attempt 1: connect (2s timeout)
- Attempt 2: wait 2s, connect (5s timeout)
- Attempt 3: wait 4s, connect (10s timeout)
- Log each retry. Fail only after all 3 attempts.

---

### 2. No address-family fallback

The hostname resolves to both IPv4 (`76.13.88.5`) and IPv6 (`2a02:4780:13::34`). The connector tried IPv4 first (blocked by firewall) and timed out. Only IPv6 works.

**Fix:** Resolve hostname on startup, try each address family in order (IPv6 → IPv4), cache the working address for the session. Add a `--force-ipv4` / `--force-ipv6` override.

---

### 3. Checksum saved before DB commit confirmed

The checksums dictionary is updated in-memory at line 355 **inside the insert loop**, but only flushed to disk at line 357 **after all inserts complete**.

**Scenario A:** Script crashes between insert #15 and checksum save → checksums for 1–15 are lost → next run re-scans everything → existing records are re-detected by slug → triggers unnecessary UPDATEs (harmless but wasteful).

**Scenario B (worse):** Checksums are saved to disk, but DB inserts failed silently (as on Jul 14 — all 3 inserts failed with 1064 but counters said "3 inserted"). Files are now marked as "unchanged" and will NEVER be retried.

**Fix:**
- Only write checksums to disk for CONFIRMED successful inserts/updates
- Add a `--retry-failed` flag that re-processes files whose DB slug doesn't match the expected state
- Add a `failed_files` list in the checksums JSON to track known-bad files separately

---

### 4. No DB dialect detection

The Python MySQL Connector's `%(name)s` parameterized syntax works on MySQL but can fail on MariaDB with syntax error 1064.

```
[ERROR] Insert failed for 'Server Migration Cost Estimation':
  1064 (42000): ... syntax to use near '%(title)s, %(slug)s'
```

**Fix:** On connect, run `SELECT VERSION()` and detect MariaDB. If MariaDB, switch to positional `%s` placeholders with ordered tuple parameters instead of named `%(name)s` with dict.

---

## 🟠 High — Partial Failure or Data Quality Risk

### 5. Non-case-study .md files are scanned

The glob `*.md` catches everything, including MAPPING-REFERENCE.md, README.md, or any stray markdown file. Today it produced `Missing title in MAPPING-REFERENCE.md` — harmless but pollutes logs and wastes scan time.

**Fix:** Only process files matching the pattern `NN-*.md` (2-digit index prefix). Add `--force` flag to bypass this filter.

---

### 6. No file encoding fallback

`filepath.read_text(encoding="utf-8")` will raise `UnicodeDecodeError` on files with BOM marks, Windows cp1252 encoding, or mixed encodings.

**Fix:** Try in order: `utf-8` → `utf-8-sig` (handles BOM) → `cp1252` (common Windows encoding). Log which encoding was used.

---

### 7. No required-fields validation beyond title

Missing `overview`, `data_sources`, or `solution_frameworks` passes silently. A case with empty critical fields gets inserted into the DB.

**Fix:** Define `REQUIRED_FIELDS = {"title", "type", "difficulty", "overview", "data_sources", "solution_frameworks", "tags"}` and validate all before returning from `parse_case_file`.

---

### 8. Hardcoded `author_id = 1`

If the user with id=1 is ever deleted or repurposed, all cases become orphaned.

**Fix:** Make it a CLI argument (`--author-id`) with a default from an env var. Add a DB check that the author actually exists before inserting.

---

### 9. No connection health check during long insert loops

27 inserts take ~90 seconds. If the connection drops mid-batch (timeout, server restart), each subsequent insert fails individually. There's no automatic reconnection.

**Fix:** Call `conn.ping(reconnect=True)` every 5 inserts. If ping fails, attempt reconnection (use the retry logic from #1). Log each reconnection.

---

## 🟡 Medium — Incorrect Behaviour or Poor UX

### 10. Error counters are misleading

The summary `inserted_count` counts **attempts**, not successes. On Jul 14, the log said "3 inserted, 0 updated, 3 errors" when actually 0 inserts succeeded.

```
Session: +445 pts | 3 inserted, 0 updated, 3 errors
```

The `session_points` (+445) also doesn't match: 3 × 50 + 3 × (-10) = 120, not 445. The score is carried over from a previous session's baseline.

**Fix:** Track actual inserted/updated counts from `cursor.rowcount` and `cursor.lastrowid`. Only increment counters on confirmed DB success.

---

### 11. No progress persistence

If the script is killed mid-batch (Ctrl+C, power failure, timeout), the next run re-scans everything from scratch. With 200+ files, this wastes time.

**Fix:** Write a `_progress.json` checkpoint after each successful insert/update containing the last processed file index. On restart, skip already-processed files. Add `--reset-progress` to clear the checkpoint.

---

### 12. No content size check

The `full_content` field holds the entire markdown file. If a case exceeds MySQL's `max_allowed_packet` (default 64MB, often 16MB on shared hosts), the insert fails with a cryptic packet-size error.

**Fix:** On connect, read `SHOW VARIABLES LIKE 'max_allowed_packet'`. Before each insert, check `len(full_content)` against 80% of this limit and log a warning if approaching.

---

### 13. Slug collision risk

`slugify()` strips special characters and truncates to 240 chars. Two different titles could produce the same slug (e.g., "Data Center Power" and "Data Center Power!").

**Fix:** Append a 4-character hex hash of the original title to the slug to guarantee uniqueness.

---

### 14. No pre-scan validation summary

The user gets no overview of what will happen before the insert loop starts. They must run `--dry-run` separately to see pending operations.

**Fix:** After scanning, print a summary table:
```
Files found:      40
  - New:          27
  - Changed:       0
  - Unchanged:    12
  - Parse errors:  1 (MAPPING-REFERENCE.md)
```

---

## 🟢 Low — Nice-to-Have

### 15. Webhook failure has no retry

`fire_webhook` catches all exceptions and logs a warning. If the webhook endpoint is temporarily down, the notification is lost permanently.

**Fix:** Add 1 retry with 2s delay before giving up.

---

### 16. No log rotation

Log files accumulate indefinitely in `logs/`. After 2 weeks there are 15 files.

**Fix:** On startup, clean logs older than 30 days. Or switch to a rotating file handler (e.g., `RotatingFileHandler` with max 10MB per file, keep 5 backups).

---

### 17. No `--force` mode

There's no way to force re-upload of all files (ignoring checksums). Useful after a schema migration, content policy change, or re-indexing.

**Fix:** Add `--force` that skips checksum comparison and processes every file as "changed."

---

### 18. DB credentials are hardcoded

Switching between staging, production, or a local dev DB requires editing `upload_case_studies.py`.

**Fix:** Accept DB config from environment variables (`DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASS`) or a `--config <file.json>` argument, with hardcoded values as fallback.

---

## Summary: Proposed CL Interface

```
Plato the Archivist — Keeper of the Case Study Vault

Usage:
  python upload_case_studies.py [--publish] [--dry-run]
                                [--force] [--retry-failed]
                                [--author-id INT]
                                [--webhook URL]
                                [--config FILE]
                                [--force-ipv4 | --force-ipv6]
                                [--max-retries N]
                                [--reset-progress]

Options:
  --publish         Set status to Published instead of Draft
  --dry-run         Scan and report only, no DB writes
  --force           Re-upload all files regardless of checksums
  --retry-failed    Retry files from the failed-files list
  --author-id INT   Override default author (default: 1)
  --config FILE     JSON file with DB config
  --force-ipv4      Use IPv4 only for DB connection
  --force-ipv6      Use IPv6 only for DB connection
  --max-retries N   Max connection retries (default: 3)
  --reset-progress  Clear progress checkpoint and re-scan all
```

---

## Layer Architecture (v2)

```
┌─────────────────────────────────────────────┐
│               CLI / argparse                 │
├─────────────────────────────────────────────┤
│            Orchestrator (main)               │
│   - validation summary                      │
│   - progress checkpointing                  │
│   - score tracking                          │
├─────────────────────────────────────────────┤
│            Connection Manager               │
│   - DNS resolution + address family fallback│
│   - exponential backoff retry               │
│   - dialect detection (MySQL vs MariaDB)    │
│   - periodic ping + auto-reconnect          │
│   - max_allowed_packet check                │
├─────────────────────────────────────────────┤
│              Case Scanner                   │
│   - file whitelist (NN-*.md)               │
│   - encoding fallback                       │
│   - required-fields validation              │
│   - slug dedup with hash suffix             │
├─────────────────────────────────────────────┤
│             DB Operations                   │
│   - dialect-safe parameterized queries      │
│   - insert / update with error isolation    │
│   - failed-files tracking                   │
├─────────────────────────────────────────────┤
│              Persistence                    │
│   - checksums (only on success)            │
│   - progress checkpoint                    │
│   - failed-files list                      │
│   - log rotation                           │
└─────────────────────────────────────────────┘
```
