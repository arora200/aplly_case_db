"""Dump all case studies from DB to local JSON files for analysis."""

import sys, os, json, re
sys.path.insert(0, os.path.dirname(__file__))

from upload_case_studies import ConnectionManager, merge_config

class Args: pass
args = Args()
for a in ['force_ipv4','force_ipv6','force','retry_failed','reset_progress','publish','dry_run','max_retries','author_id','config']:
    setattr(args, a, None if a in ('config','author_id') else False)

db_config = merge_config(args)
cm = ConnectionManager(db_config, max_retries=3)
if not cm.connect():
    print("FAIL: could not connect")
    sys.exit(1)

cm.cursor.execute("SELECT COUNT(*) FROM case_studies")
total = cm.cursor.fetchone()[0]
print(f"Total: {total}")

cm.cursor.execute("SELECT * FROM case_studies ORDER BY id")
rows = cm.cursor.fetchall()
col_names = [d[0] for d in cm.cursor.description]

outdir = os.path.join(os.path.dirname(__file__), "..", "db_dump")
os.makedirs(outdir, exist_ok=True)

for row in rows:
    record = dict(zip(col_names, row))
    # serialize JSON-compatible
    for k, v in record.items():
        if isinstance(v, bytes):
            try:
                record[k] = v.decode("utf-8")
            except:
                record[k] = repr(v)
    fname = f"{record['id']:04d}-{record['slug'][:60] if record.get('slug') else record['title'][:60]}.json"
    # sanitize filename
    fname = re.sub(r'[<>:"/\\|?*]', '_', fname)
    fpath = os.path.join(outdir, fname)
    with open(fpath, "w", encoding="utf-8") as f:
        json.dump(record, f, ensure_ascii=False, indent=2, default=str)

print(f"Dumped {len(rows)} case studies to {outdir}")
cm.close()
