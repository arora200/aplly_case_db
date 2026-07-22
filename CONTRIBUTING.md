# Contributing

## Adding a new dataset

1. Add a generator function in `scripts/generate_all.py`
2. Add the expected schema to `scripts/validate_schema.py`
3. Run `python scripts/generate_all.py --cases NNN`
4. Run `python scripts/validate_schema.py`
5. Commit and push

## Modifying an existing dataset

1. Update the generator function in `generate_all.py`
2. If columns changed, update the schema in `validate_schema.py`
3. Regenerate: `python scripts/generate_all.py --cases NNN`
4. Re-validate: `python scripts/validate_schema.py`
5. Bump the seed date in `generate_all.py` (line: `SEED = "..."`)
6. Commit with message: `datasets(NNN): regenerate after column change`

## Rules

- All CSVs must be deterministically generated (same seed = same output)
- Every CSV must have a header row
- No binary files — CSVs only (UTF-8, LF line endings)
- Keep individual files under 1 MB; use GitHub Releases for larger files
