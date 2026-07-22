# Aplly Case Study Datasets

Synthetic datasets for all Aplly.xyz case studies. Deterministically generated — same seed produces identical CSVs every time.

## Structure

```
datasets/
├── 001-capacity-planning/       # Case 1: Black Friday traffic estimation
│   ├── README.md
│   ├── monthly_traffic.csv
│   ├── server_specs.csv
│   └── black_friday_params.csv
├── 002-ticket-forecasting/      # Case 2: On-call ticket forecasting
└── ...                          # 39 case studies total
```

## Usage

```bash
pip install -r requirements.txt   # (none needed — pure Python stdlib)
python scripts/generate_all.py    # Regenerate all CSVs (reproducible)
python scripts/validate_schema.py # CI check — verify all CSVs match expected schemas
```

## Case to Dataset Mapping

| Case ID | Folder | Thinking Type |
|---------|--------|---------------|
| 1 | 001-capacity-planning | Computational |
| 2 | 002-ticket-forecasting | Analytical |
| ... | ... | ... |
| 39 | 039-executive-dashboard-kpi | Analytical |

Full mapping at [TUTORIAL_GUIDANCE_DESIGN.md](https://github.com/arora200/aplly_case_db/blob/main/TUTORIAL_GUIDANCE_DESIGN.md) (in companion repo).

## License

MIT — free to use, modify, and redistribute.
