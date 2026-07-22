#!/usr/bin/env python3
"""
Deterministic, seed-based generator for all Aplly.xyz case-study datasets.
Same seed → identical CSVs every time. Reproducible by design.
"""

import csv, os, hashlib, json, textwrap, argparse, random
from datetime import datetime, timedelta
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DATASETS_DIR = REPO_ROOT / "datasets"
SHARED_DIR = REPO_ROOT / "shared"
SEED = "aplly-2026-07-22"  # fixed seed — change only when datasets must intentionally change

# ── helpers ──────────────────────────────────────────────────────────────

def _rng(seed_salt: str):
    """Deterministic RNG from global seed + case-specific salt."""
    h = hashlib.sha256(f"{SEED}:{seed_salt}".encode()).hexdigest()
    return random.Random(int(h[:16], 16))

def _write_csv(path: Path, rows: list[dict]):
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("")
        return
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

def _write_readme(case_folder: Path, title: str, case_id: int, difficulty: str,
                  thinking_type: str, files: list[dict], source_note: str):
    lines = [
        f"# Dataset: {title}",
        "",
        "## Case Reference",
        f"- **Case ID:** {case_id}",
        f"- **Title:** {title}",
        f"- **Difficulty:** {difficulty}",
        f"- **Thinking Type:** {thinking_type}",
        "",
        "## Files in this folder",
        "",
        "| File | Rows | Columns | Description |",
        "|------|------|---------|-------------|",
    ]
    for f in files:
        lines.append(f"| {f['name']} | {f['rows']} | {f['cols']} | {f['desc']} |")
    lines += [
        "",
        "## Source",
        source_note,
        "",
        f"Seed: `{SEED}` — deterministic, reproducible.",
        "License: MIT",
    ]
    (case_folder / "README.md").write_text("\n".join(lines), encoding="utf-8")


# ── COMPUTATIONAL: Case 01 — Capacity Planning: Black Friday ─────────────

def gen_001(out: Path):
    cid, title, folder = "001", "Capacity Planning for a Black Friday Traffic Spike", out / "001-capacity-planning"
    rng = _rng(cid)
    months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov"]
    base_req = 2000
    signups = 40000
    rows = []
    for i, m in enumerate(months):
        req = int(base_req + rng.uniform(-150, 250) + i * 30)
        signups += int(rng.uniform(500, 1500))
        rows.append({"Month": m, "Avg req/sec": req, "Cumulative Signups": signups})
    _write_csv(folder / "monthly_traffic.csv", rows)

    spec_rows = [
        {"Server Type": "Web Server", "Capacity (req/sec)": 250, "Current Count": 10},
        {"Server Type": "App Server", "Capacity (req/sec)": 300, "Current Count": 5},
        {"Server Type": "DB Server", "Capacity (req/sec)": 500, "Current Count": 2},
    ]
    _write_csv(folder / "server_specs.csv", spec_rows)

    _write_csv(folder / "black_friday_params.csv", [
        {"Parameter": "Last Year BF Peak (req/sec)", "Value": 14200},
        {"Parameter": "Last Year Nov Avg (req/sec)", "Value": 1850},
        {"Parameter": "YoY Signup Growth %", "Value": 35},
        {"Parameter": "Safety Margin %", "Value": 20},
        {"Parameter": "Server Budget Ceiling", "Value": 22},
    ])

    _write_readme(folder, title, 1, "Intermediate", "Computational", [
        {"name": "monthly_traffic.csv", "rows": 11, "cols": 3, "desc": "11 months of traffic data"},
        {"name": "server_specs.csv", "rows": 3, "cols": 3, "desc": "Server capacity and count"},
        {"name": "black_friday_params.csv", "rows": 5, "cols": 2, "desc": "Key parameters and constraints"},
    ], "Synthetic data based on typical e-commerce traffic patterns during Black Friday.")


# ── COMPUTATIONAL: Case 10 — Server Migration Cost Estimation ────────────

def gen_010(out: Path):
    cid, title, folder = "010", "Server Migration Cost Estimation", out / "010-server-migration-cost"
    rng = _rng(cid)

    servers = [
        ("DB-01","Database Primary",8,32,2000,150),
        ("DB-02","Database Replica",8,16,2000,100),
        ("WEB-01","Web Server",4,8,500,400),
        ("WEB-02","Web Server",4,8,500,400),
        ("WEB-03","Web Server",4,8,500,400),
        ("API-01","API Gateway",4,16,200,300),
        ("API-02","API Gateway",4,16,200,300),
        ("CACHE-01","Redis Cache",4,16,100,50),
        ("CACHE-02","Redis Cache",4,16,100,50),
        ("WORKER-01","Background Worker",8,16,500,200),
        ("WORKER-02","Background Worker",8,16,500,200),
        ("MONITOR-01","Monitoring",2,4,500,50),
    ]
    rows = []
    for sid, role, cpu, ram, stor, egr in servers:
        cost = cpu * 0.042 * 730 + ram * 0.014 * 730 + stor * 0.08 + egr * 0.09
        rows.append({"Server ID": sid, "Role": role, "vCPU": cpu, "RAM (GB)": ram,
                      "Storage (GB)": stor, "Monthly Egress (GB)": egr,
                      "Current On-Prem Cost ($/mo)": round(cost, 2)})
    _write_csv(folder / "server_inventory.csv", rows)

    _write_csv(folder / "cloud_pricing.csv", [
        {"Resource": "vCPU", "Rate ($)": 0.042, "Unit": "per hr"},
        {"Resource": "RAM", "Rate ($)": 0.014, "Unit": "per hr per GB"},
        {"Resource": "Storage", "Rate ($)": 0.08, "Unit": "per GB per month"},
        {"Resource": "Egress", "Rate ($)": 0.09, "Unit": "per GB"},
    ])
    _write_csv(folder / "migration_params.csv", [
        {"Parameter": "Migration Overhead Multiplier (first month)", "Value": 2.3},
        {"Parameter": "Hours per Month", "Value": 730},
    ])

    _write_readme(folder, title, 10, "Intermediate", "Computational", [
        {"name": "server_inventory.csv", "rows": 12, "cols": 7, "desc": "12 on-prem servers with specs and current cost"},
        {"name": "cloud_pricing.csv", "rows": 4, "cols": 2, "desc": "Cloud resource pricing table"},
        {"name": "migration_params.csv", "rows": 2, "cols": 2, "desc": "Overhead multiplier and hours"},
    ], "Synthetic data based on typical mid-size IT infrastructure migration scenarios.")


# ── COMPUTATIONAL: Case 13 — ICDS Food Budget ────────────────────────────

def gen_013(out: Path):
    cid, title, folder = "013", "Feeding a Family of 5: ICDS Food Budget Estimation", out / "013-food-budget-icds"
    _write_csv(folder / "family_composition.csv", [
        {"Member":"Father","Age":38,"Gender":"M","Category":"Adult male"},
        {"Member":"Mother","Age":35,"Gender":"F","Category":"Adult female"},
        {"Member":"Child 1","Age":10,"Gender":"F","Category":"Child (7-12)"},
        {"Member":"Child 2","Age":7,"Gender":"M","Category":"Child (4-7)"},
        {"Member":"Child 3","Age":4,"Gender":"F","Category":"Child (1-4)"},
    ])
    _write_csv(folder / "rda_daily_requirements.csv", [
        {"Food Group":"Cereals (rice/wheat)","Adult Male (g/ml)":350,"Adult Female (g/ml)":300,"Child (7-12) (g/ml)":250,"Child (4-7) (g/ml)":200,"Child (1-4) (g/ml)":150},
        {"Food Group":"Pulses (dal)","Adult Male (g/ml)":60,"Adult Female (g/ml)":55,"Child (7-12) (g/ml)":45,"Child (4-7) (g/ml)":40,"Child (1-4) (g/ml)":30},
        {"Food Group":"Vegetables (leafy + other)","Adult Male (g/ml)":200,"Adult Female (g/ml)":200,"Child (7-12) (g/ml)":175,"Child (4-7) (g/ml)":150,"Child (1-4) (g/ml)":100},
        {"Food Group":"Milk & milk products","Adult Male (g/ml)":200,"Adult Female (g/ml)":200,"Child (7-12) (g/ml)":300,"Child (4-7) (g/ml)":300,"Child (1-4) (g/ml)":300},
        {"Food Group":"Oils & fats","Adult Male (g/ml)":30,"Adult Female (g/ml)":25,"Child (7-12) (g/ml)":25,"Child (4-7) (g/ml)":20,"Child (1-4) (g/ml)":15},
        {"Food Group":"Fruits","Adult Male (g/ml)":100,"Adult Female (g/ml)":100,"Child (7-12) (g/ml)":100,"Child (4-7) (g/ml)":80,"Child (1-4) (g/ml)":60},
        {"Food Group":"Sugar & jaggery","Adult Male (g/ml)":30,"Adult Female (g/ml)":25,"Child (7-12) (g/ml)":25,"Child (4-7) (g/ml)":20,"Child (1-4) (g/ml)":15},
    ])
    _write_csv(folder / "market_rates.csv", [
        {"Food Group":"Cereals (rice)","Rate (₹/unit)":38,"Unit":"kg"},
        {"Food Group":"Cereals (wheat)","Rate (₹/unit)":32,"Unit":"kg"},
        {"Food Group":"Pulses (dal - toor/moong)","Rate (₹/unit)":115,"Unit":"kg"},
        {"Food Group":"Vegetables (mixed seasonal)","Rate (₹/unit)":45,"Unit":"kg"},
        {"Food Group":"Milk","Rate (₹/unit)":58,"Unit":"liter"},
        {"Food Group":"Oils & fats (refined)","Rate (₹/unit)":175,"Unit":"liter"},
        {"Food Group":"Fruits (seasonal)","Rate (₹/unit)":60,"Unit":"kg"},
        {"Food Group":"Sugar & jaggery","Rate (₹/unit)":42,"Unit":"kg"},
    ])
    _write_csv(folder / "budget_constants.csv", [
        {"Parameter":"Price Volatility Buffer","Value":15,"Unit":"%"},
        {"Parameter":"District Monthly Benchmark","Value":12000,"Unit":"₹"},
        {"Parameter":"Month Days","Value":30,"Unit":"days"},
    ])
    _write_readme(folder, title, 13, "Intermediate", "Computational", [
        {"name":"family_composition.csv","rows":5,"cols":4,"desc":"Family of 5"},
        {"name":"rda_daily_requirements.csv","rows":7,"cols":6,"desc":"Daily RDA per food group per person"},
        {"name":"market_rates.csv","rows":8,"cols":3,"desc":"Wholesale market rates"},
        {"name":"budget_constants.csv","rows":3,"cols":3,"desc":"Buffer, benchmark, days"},
    ], "Synthetic data based on ICMR RDA 2024 guidelines and typical Indian market rates.")


# ── COMPUTATIONAL: Case 14 — Data Center Power Cost ──────────────────────

def gen_014(out: Path):
    cid, title, folder = "014", "Data Center Power Cost Estimation", out / "014-data-center-power-cost"
    rng = _rng(cid)

    tiers = {
        "Rack 1 — Web Tier": [
            ("WEB-01","Web Server",450,65),("WEB-02","Web Server",450,72),
            ("WEB-03","Web Server",450,58),("LB-01","Load Balancer",300,45),
            ("SW-01","Top-of-Rack Switch",150,80),("MON-01","Monitoring Appliance",200,30),
        ],
        "Rack 2 — Data Tier": [
            ("DB-01","Database Primary",800,85),("DB-02","Database Replica",800,60),
            ("STO-01","Storage Array",1200,70),("STO-02","Storage Array",1200,65),
            ("BACKUP-01","Backup Server",500,20),("BACKUP-02","Backup Server",500,15),
        ],
        "Rack 3 — App Tier": [
            ("APP-01","App Server",350,55),("APP-02","App Server",350,60),
            ("APP-03","App Server",350,50),("APP-04","App Server",350,45),
            ("SW-02","Top-of-Rack Switch",150,80),("FW-01","Firewall Appliance",250,40),
        ],
    }
    for rack_name, devices in tiers.items():
        rack_folder = folder / rack_name.replace(" — ","-").replace(" ","-").lower()
        rows = [{"Device ID": d[0], "Role": d[1], "Rated Wattage": d[2], "Utilization %": d[3]} for d in devices]
        _write_csv(rack_folder / "equipment.csv", rows)

    _write_csv(folder / "power_constants.csv", [
        {"Parameter":"PUE","Value":1.7},
        {"Parameter":"Electricity Tariff (₹/kWh)","Value":8.5},
        {"Parameter":"Days per Month","Value":30},
        {"Parameter":"Hours per Day","Value":24},
        {"Parameter":"Actual Bill This Month (₹)","Value":62400},
    ])
    _write_readme(folder, title, 14, "Intermediate", "Computational", [
        {"name":"web-tier/equipment.csv","rows":6,"cols":4,"desc":"Rack 1 web tier devices"},
        {"name":"data-tier/equipment.csv","rows":6,"cols":4,"desc":"Rack 2 data tier devices"},
        {"name":"app-tier/equipment.csv","rows":6,"cols":4,"desc":"Rack 3 app tier devices"},
        {"name":"power_constants.csv","rows":5,"cols":2,"desc":"PUE, tariff, days, actual bill"},
    ], "Synthetic data based on typical small data center power consumption.")


# ── COMPUTATIONAL: Case 24 — Product Category Profitability ──────────────

def gen_024(out: Path):
    cid, title, folder = "024", "Product Category Profitability Decomposition", out / "024-product-category-profitability"
    _write_csv(folder / "category_data.csv", [
        {"Category":"Electronics","Revenue (₹L)":350,"COGS (₹L)":280,"Floor Space (sq ft)":1500,"Staff Hours (%)":20},
        {"Category":"Grocery","Revenue (₹L)":200,"COGS (₹L)":170,"Floor Space (sq ft)":2000,"Staff Hours (%)":25},
        {"Category":"Apparel","Revenue (₹L)":180,"COGS (₹L)":108,"Floor Space (sq ft)":1800,"Staff Hours (%)":15},
        {"Category":"Home & Kitchen","Revenue (₹L)":140,"COGS (₹L)":98,"Floor Space (sq ft)":1500,"Staff Hours (%)":15},
        {"Category":"Beauty & Personal Care","Revenue (₹L)":120,"COGS (₹L)":84,"Floor Space (sq ft)":1200,"Staff Hours (%)":15},
        {"Category":"Books & Media","Revenue (₹L)":110,"COGS (₹L)":77,"Floor Space (sq ft)":1000,"Staff Hours (%)":10},
    ])
    _write_csv(folder / "overhead_pools.csv", [
        {"Overhead Item":"Rent","Total (₹L)":120,"Allocation Basis":"Floor space (%)"},
        {"Overhead Item":"Staffing","Total (₹L)":95,"Allocation Basis":"Staff hours (%)"},
        {"Overhead Item":"Utilities & Maintenance","Total (₹L)":45,"Allocation Basis":"Floor space (%)"},
    ])
    _write_readme(folder, title, 24, "Intermediate", "Computational", [
        {"name":"category_data.csv","rows":6,"cols":5,"desc":"6 product categories with revenue, COGS, space, staff"},
        {"name":"overhead_pools.csv","rows":3,"cols":3,"desc":"3 overhead cost pools with allocation basis"},
    ], "Synthetic data based on multi-category retail profitability analysis.")


# ── COMPUTATIONAL: Case 26 — Server Capacity Planning Projection ─────────

def gen_026(out: Path):
    cid, title, folder = "026", "12-Month Server Capacity Planning Projection", out / "026-server-capacity-projection"
    _write_csv(folder / "current_usage.csv", [
        {"Tier":"Web","Servers":5,"CPU Capacity (cores)":40,"Current CPU Usage (cores)":24,"CPU Util %":60,
         "RAM Capacity (GB)":64,"Current RAM Usage (GB)":38.4,"Storage Capacity (TB)":5,"Current Storage Used (TB)":2.5},
        {"Tier":"App","Servers":3,"CPU Capacity (cores)":24,"Current CPU Usage (cores)":15.6,"CPU Util %":65,
         "RAM Capacity (GB)":48,"Current RAM Usage (GB)":31.2,"Storage Capacity (TB)":2,"Current Storage Used (TB)":1.1},
        {"Tier":"DB","Servers":2,"CPU Capacity (cores)":32,"Current CPU Usage (cores)":22.4,"CPU Util %":70,
         "RAM Capacity (GB)":64,"Current RAM Usage (GB)":48,"Storage Capacity (TB)":10,"Current Storage Used (TB)":7},
    ])
    _write_csv(folder / "monthly_growth_rates.csv", [
        {"Tier":"Web","CPU Growth (%/mo)":3.5,"RAM Growth (%/mo)":4.0,"Storage Growth (%/mo)":5.0},
        {"Tier":"App","CPU Growth (%/mo)":2.5,"RAM Growth (%/mo)":3.0,"Storage Growth (%/mo)":3.5},
        {"Tier":"DB","CPU Growth (%/mo)":1.8,"RAM Growth (%/mo)":2.0,"Storage Growth (%/mo)":4.5},
    ])
    _write_csv(folder / "planning_params.csv", [
        {"Parameter":"Seasonal Peak Multiplier (Month 11, Web tier)","Value":1.8},
        {"Parameter":"Warning Threshold (%)","Value":80},
        {"Parameter":"Critical Threshold (%)","Value":90},
        {"Parameter":"Provisioning Lead Time (weeks)","Value":8},
    ])
    _write_readme(folder, title, 26, "Intermediate", "Computational", [
        {"name":"current_usage.csv","rows":3,"cols":10,"desc":"CPU, RAM, storage for Web/App/DB tiers"},
        {"name":"monthly_growth_rates.csv","rows":3,"cols":4,"desc":"Monthly growth per resource per tier"},
        {"name":"planning_params.csv","rows":4,"cols":2,"desc":"Seasonal peak, thresholds, lead time"},
    ], "Synthetic data based on typical server capacity planning in a growing SaaS company.")


# ── COMPUTATIONAL: Case 29 — FinOps Cost Decomposition ───────────────────

def gen_029(out: Path):
    cid, title, folder = "029", "FinOps Cost Decomposition", out / "029-finops-cost-decomposition"
    rng = _rng(cid)
    services = ["Compute","Storage","Database","Data Transfer","Networking","Other Services"]
    base = [4.5, 1.2, 2.1, 0.8, 0.6, 0.9]
    months = ["Apr","May","Jun","Jul","Aug","Sep"]
    rows = []
    for i, svc in enumerate(services):
        trend = [round(base[i] * (1 + 0.03 * j + rng.uniform(-0.05, 0.05)), 1) for j in range(6)]
        row = {"Service Category": svc}
        for j, m in enumerate(months):
            row[m] = trend[j]
        rows.append(row)
    # total row
    total = {"Service Category": "Total"}
    for j, m in enumerate(months):
        total[m] = round(sum(r[m] for r in rows), 1)
    rows.append(total)
    _write_csv(folder / "monthly_cloud_spend.csv", rows)

    _write_csv(folder / "finops_constants.csv", [
        {"Parameter":"Previous Year Sep Total (₹L)","Value":8.7},
        {"Parameter":"Current Sep Total (₹L)","Value":12.2},
        {"Parameter":"Q4 Budget (₹L)","Value":36.0},
        {"Parameter":"Single Category Threshold (%)","Value":50},
        {"Parameter":"November Compute Increase (%)","Value":15},
    ])
    _write_readme(folder, title, 29, "Intermediate", "Computational", [
        {"name":"monthly_cloud_spend.csv","rows":7,"cols":7,"desc":"6 service categories + total, Apr–Sep"},
        {"name":"finops_constants.csv","rows":5,"cols":2,"desc":"Budget, thresholds, projections"},
    ], "Synthetic cloud cost data based on typical growing SaaS infrastructure spend.")


# ── COMPUTATIONAL: Case 33 — Customer LTV Ranking ────────────────────────

def gen_033(out: Path):
    cid, title, folder = "033", "Customer Lifetime Value Ranking", out / "033-customer-ltv-ranking"
    rng = _rng(cid)
    customers = []
    for i in range(1, 11):
        cid_ = f"C{i:03d}"
        first = f"202{rng.randint(2,5)}-{rng.choice(['Jan','Mar','May','Jul','Sep','Nov'])}"
        last = f"2026-{rng.choice(['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct'])}"
        orders = rng.randint(3, 25)
        revenue = orders * rng.randint(800, 5000)
        customers.append({"Customer ID": cid_, "First Purchase": first, "Last Purchase": last,
                          "Total Orders": orders, "Total Revenue (₹)": revenue})
    customers.sort(key=lambda r: r["Customer ID"])
    _write_csv(folder / "customer_purchase_history.csv", customers)
    _write_csv(folder / "ltv_constants.csv", [
        {"Parameter":"Current Date","Value":"October 2026"},
        {"Parameter":"Churn Window (months)","Value":6},
        {"Parameter":"Campaign Budget (₹)","Value":1000000},
        {"Parameter":"Target Segment Size","Value":3},
    ])
    _write_readme(folder, title, 33, "Intermediate", "Computational", [
        {"name":"customer_purchase_history.csv","rows":10,"cols":5,"desc":"10 customers with purchase history"},
        {"name":"ltv_constants.csv","rows":4,"cols":2,"desc":"Date, churn rules, budget"},
    ], "Synthetic e-commerce customer data.")


# ── ALGORITHMIC: Case 04 — Fair On-Call Rotation ────────────────────────

def gen_004(out: Path):
    cid, title, folder = "004", "Fair On-Call Rotation", out / "004-fair-on-call-rotation"
    _write_csv(folder / "engineer_availability.csv", [
        {"Engineer":"A","Availability":"100%","Blackout Weeks":"None","Past-Quarter On-Call Count":4},
        {"Engineer":"B","Availability":"100%","Blackout Weeks":"None","Past-Quarter On-Call Count":5},
        {"Engineer":"C","Availability":"50%","Blackout Weeks":"None","Past-Quarter On-Call Count":3},
        {"Engineer":"D","Availability":"100%","Blackout Weeks":"Weeks 5-7","Past-Quarter On-Call Count":6},
        {"Engineer":"E","Availability":"100%","Blackout Weeks":"None","Past-Quarter On-Call Count":4},
        {"Engineer":"F","Availability":"100%","Blackout Weeks":"Weeks 9-10","Past-Quarter On-Call Count":2},
    ])
    _write_csv(folder / "schedule_constraints.csv", [
        {"Constraint":"Schedule Horizon (weeks)","Value":12},
        {"Constraint":"Max Consecutive On-Call Weeks","Value":1},
        {"Constraint":"Part-time Max (of 12 weeks)","Value":6},
    ])
    _write_readme(folder, title, 4, "Intermediate", "Algorithmic", [
        {"name":"engineer_availability.csv","rows":6,"cols":4,"desc":"6 engineers with availability and blackouts"},
        {"name":"schedule_constraints.csv","rows":3,"cols":2,"desc":"Hard scheduling constraints"},
    ], "Synthetic team scheduling data.")


# ── ALGORITHMIC: Case 05 — Silent Pipeline Failure ──────────────────────

def gen_005(out: Path):
    cid, title, folder = "005", "Debugging Silent Data Pipeline Failure", out / "005-silent-pipeline-failure"
    _write_csv(folder / "sample_input.csv", [
        {"order_id":"ORD-1001","currency":"EUR","amount":120.00,"order_timestamp":"2026-09-15 10:00:00"},
        {"order_id":"ORD-1002","currency":"EUR","amount":75.50,"order_timestamp":"2026-09-15 10:05:00"},
        {"order_id":"ORD-1003","currency":"USD","amount":50.00,"order_timestamp":"2026-09-15 10:10:00"},
    ])
    _write_csv(folder / "expected_vs_actual.csv", [
        {"order_id":"ORD-1001","expected_usd":130.20,"actual_usd":124.80},
        {"order_id":"ORD-1002","expected_usd":81.92,"actual_usd":78.52},
        {"order_id":"ORD-1003","expected_usd":50.00,"actual_usd":50.00},
    ])
    _write_csv(folder / "pipeline_params.csv", [
        {"Parameter":"Stale EUR Rate","Value":1.04},
        {"Parameter":"Fresh EUR Rate","Value":1.085},
    ])
    _write_readme(folder, title, 5, "Advanced", "Algorithmic", [
        {"name":"sample_input.csv","rows":3,"cols":4,"desc":"3 sample orders"},
        {"name":"expected_vs_actual.csv","rows":3,"cols":3,"desc":"Expected vs actual USD conversion"},
        {"name":"pipeline_params.csv","rows":2,"cols":2,"desc":"FX rates (stale and fresh)"},
    ], "Synthetic FX pipeline data.")


# ── ALGORITHMIC: Case 06 — Caching Strategy ─────────────────────────────

def gen_006(out: Path):
    cid, title, folder = "006", "Caching Strategy for Read-Heavy API", out / "006-caching-strategy"
    _write_csv(folder / "traffic_pattern.csv", [
        {"Hour Block":"00:00–06:00","Reads/sec":120,"Writes/sec":2},
        {"Hour Block":"06:00–12:00","Reads/sec":850,"Writes/sec":18},
        {"Hour Block":"12:00–18:00","Reads/sec":1200,"Writes/sec":24},
        {"Hour Block":"18:00–24:00","Reads/sec":950,"Writes/sec":20},
    ])
    _write_csv(folder / "latency_baseline.csv", [
        {"Metric":"p50 Latency (ms)","Value":180},
        {"Metric":"p95 Latency (ms)","Value":450},
        {"Metric":"p99 Latency (ms)","Value":900},
    ])
    _write_csv(folder / "design_constraints.csv", [
        {"Constraint":"Read/Write Ratio","Value":"~50:1"},
        {"Constraint":"Data Change Frequency","Value":"2-4 times/hour"},
        {"Constraint":"Hot Items Updated (%)","Value":5},
        {"Constraint":"Budget Ceiling ($/mo)","Value":1500},
        {"Constraint":"Staleness Tolerance (min)","Value":2},
        {"Constraint":"Staleness Coverage (%)","Value":95},
    ])
    _write_readme(folder, title, 6, "Expert", "Algorithmic", [
        {"name":"traffic_pattern.csv","rows":4,"cols":3,"desc":"Read/write per hour block"},
        {"name":"latency_baseline.csv","rows":3,"cols":2,"desc":"p50/p95/p99 latency"},
        {"name":"design_constraints.csv","rows":6,"cols":2,"desc":"Budget, staleness, data change"},
    ], "Synthetic API traffic data.")


# ── ALGORITHMIC: Case 11 — Log Rotation Debug ───────────────────────────

def gen_011(out: Path):
    cid, title, folder = "011", "Debugging Log Rotation Pipeline", out / "011-log-rotation-debug"
    _write_csv(folder / "directory_state.csv", [
        {"File":"app.log","Description":"Current day's log (growing, 12MB)"},
        {"File":"app-20260914.log.gz","Description":"7 days old (rotated Mon)"},
        {"File":"app-20260913.log.gz","Description":"8 days old"},
        {"File":"app-20260912.log.gz","Description":"9 days old"},
        {"File":"app-20260911.log.gz","Description":"10 days old"},
        {"File":"app-20260910.log.gz","Description":"11 days old"},
        {"File":"app-20260909.log.gz","Description":"12 days old"},
        {"File":"app-20260908.log.gz","Description":"13 days old"},
    ])
    _write_csv(folder / "rotation_config.csv", [
        {"Parameter":"Retention Days","Value":7},
        {"Parameter":"Cron Schedule","Value":"0 3 * * *"},
        {"Parameter":"Expected Archive Format","Value":"app-YYYYMMDD.log.gz (yesterday's date)"},
        {"Parameter":"Actual Archive Format (bug)","Value":"app-YYYYMMDD.log.gz (today's date)"},
    ])
    _write_readme(folder, title, 11, "Advanced", "Algorithmic", [
        {"name":"directory_state.csv","rows":8,"cols":2,"desc":"Log files before rotation"},
        {"name":"rotation_config.csv","rows":4,"cols":2,"desc":"Rotation settings and the bug"},
    ], "Synthetic log rotation scenario.")


# ── ALGORITHMIC: Case 16 — Diet Quality Index ───────────────────────────

def gen_016(out: Path):
    cid, title, folder = "016", "Diet Quality Index Scoring Algorithm", out / "016-diet-quality-index"
    _write_csv(folder / "scoring_rules.csv", [
        {"Component":"Diversity","Max Pts":30,"Rule":"Count food groups eaten (0-10) × 3"},
        {"Component":"Sufficiency","Max Pts":25,"Rule":"Min((fruit servings + veg servings) × 5, 25)"},
        {"Component":"Moderation","Max Pts":25,"Rule":"Start 25, −5 per discretionary serving, floor 0; zero if >5 discretionary"},
        {"Component":"Regularity","Max Pts":20,"Rule":"7 per meal eaten (max 3 meals = 21, capped at 20)"},
    ])
    _write_csv(folder / "food_groups.csv", [
        {"Group":"Cereals"},{"Group":"Pulses/Legumes"},{"Group":"Dark Leafy Vegetables"},
        {"Group":"Other Vegetables"},{"Group":"Fruits"},{"Group":"Milk/Dairy"},
        {"Group":"Eggs"},{"Group":"Meat/Fish/Poultry"},{"Group":"Nuts/Seeds"},{"Group":"Oils/Fats"},
    ])
    # Respondent meal data
    respondents = {
        "A-Ramesh": [
            ("Breakfast","Rice, dal, 1 egg","2 chapatis, dal, onion"),
            ("Lunch","Rice, fish curry, mixed veg","3 chapatis, potato curry, pickle"),
            ("Dinner","Rice, chicken curry, salad","2 chapatis, dal, ghee"),
            ("Snacks","Tea, 2 biscuits","Tea, samosa"),
        ],
        "B-Lakshmi": [
            ("Breakfast","Idli (3), sambar, coconut chutney","Poha, peanuts, tea"),
            ("Lunch","Rice, rasam, 2 veg, curd","Chapati (3), aloo gobi, salad"),
            ("Dinner","Rice, fish curry, 1 veg","1 chapati, dal, pickle"),
            ("Snacks","Coffee, 1 biscuit","Tea, namkeen"),
        ],
        "C-Priya": [
            ("Breakfast","Cornflakes with milk, apple","Bread (2) with butter, tea"),
            ("Lunch","Rice, rajma, salad, curd","Chapati (2), paneer bhurji, salad"),
            ("Dinner","Chapati (2), mixed veg, dal","Rice, sambar, 1 veg"),
            ("Snacks","Tea, 2 biscuits","Coffee, 1 cookie"),
        ],
    }
    for resp_name, meals in respondents.items():
        rows = [{"Meal": m[0], "Foods Consumed": m[1], "Servings": m[2]} for m in meals]
        _write_csv(folder / f"respondent_{resp_name}.csv", rows)

    _write_readme(folder, title, 16, "Intermediate", "Algorithmic", [
        {"name":"scoring_rules.csv","rows":4,"cols":3,"desc":"4 DQI components with rules"},
        {"name":"food_groups.csv","rows":10,"cols":1,"desc":"10 food groups for diversity count"},
        {"name":"respondent_A-Ramesh.csv","rows":4,"cols":3,"desc":"Meals for respondent A"},
        {"name":"respondent_B-Lakshmi.csv","rows":4,"cols":3,"desc":"Meals for respondent B"},
        {"name":"respondent_C-Priya.csv","rows":4,"cols":3,"desc":"Meals for respondent C"},
    ], "Synthetic nutrition survey data based on typical Indian diets.")


# ── ALGORITHMIC: Case 17 — On-Call Rotation Schedule ────────────────────

def gen_017(out: Path):
    cid, title, folder = "017", "Fair On-Call Rotation Schedule", out / "017-on-call-rotation-schedule"
    _write_csv(folder / "team_roster.csv", [
        {"ID":"E01","Name":"Arjun","Shifts per week":"All available"},
        {"ID":"E02","Name":"Bhavna","Shifts per week":"All available"},
        {"ID":"E03","Name":"Chen","Shifts per week":"All available"},
        {"ID":"E04","Name":"Deepa","Shifts per week":"All available"},
        {"ID":"E05","Name":"Eswar","Shifts per week":"All available"},
    ])
    _write_csv(folder / "week_calendar.csv", [
        {"Day":1,"Weekday":"Mon","Type":"Work"},
        {"Day":2,"Weekday":"Tue","Type":"Work"},
        {"Day":3,"Weekday":"Wed","Type":"Work"},
        {"Day":4,"Weekday":"Thu","Type":"Work"},
        {"Day":5,"Weekday":"Fri","Type":"Work"},
        {"Day":6,"Weekday":"Sat","Type":"Weekend"},
        {"Day":7,"Weekday":"Sun","Type":"Weekend"},
        {"Day":8,"Weekday":"Mon","Type":"Work"},
        {"Day":9,"Weekday":"Tue","Type":"Work"},
        {"Day":10,"Weekday":"Wed","Type":"Work"},
        {"Day":11,"Weekday":"Thu","Type":"Work"},
        {"Day":12,"Weekday":"Fri","Type":"Work"},
        {"Day":13,"Weekday":"Sat","Type":"Weekend"},
        {"Day":14,"Weekday":"Sun","Type":"Weekend"},
    ])
    _write_csv(folder / "schedule_rules.csv", [
        {"Rule":"Exactly 1 primary + 1 secondary per day","Type":"Hard"},
        {"Rule":"No consecutive primary days","Type":"Hard"},
        {"Rule":"At least 1 day zero duty per week","Type":"Hard"},
        {"Rule":"Primary/secondary counts per week differ by ≤1","Type":"Hard"},
        {"Rule":"Weekend primary rotates (max 1 per 5-week cycle)","Type":"Hard"},
        {"Rule":"Ideal per-person share: 5.6 assignments","Type":"Target"},
    ])
    _write_readme(folder, title, 17, "Advanced", "Algorithmic", [
        {"name":"team_roster.csv","rows":5,"cols":3,"desc":"5 engineers"},
        {"name":"week_calendar.csv","rows":14,"cols":3,"desc":"14-day calendar"},
        {"name":"schedule_rules.csv","rows":6,"cols":2,"desc":"Hard constraints and targets"},
    ], "Synthetic scheduling data.")


# ── ALGORITHMIC: Case 18 — Sales Commission ─────────────────────────────

def gen_018(out: Path):
    cid, title, folder = "018", "Tiered Sales Commission Structure", out / "018-sales-commission"
    _write_csv(folder / "product_lines.csv", [
        {"Product Line":"Software X","Gross Margin (%)":75,"Commission Tier":"High-margin","Typical Deal Size":"₹10L–₹15L"},
        {"Product Line":"SaaS Y","Gross Margin (%)":60,"Commission Tier":"Medium-margin","Typical Deal Size":"₹5L–₹10L"},
        {"Product Line":"IT Hardware Z","Gross Margin (%)":25,"Commission Tier":"Low-margin","Typical Deal Size":"₹20L–₹30L"},
    ])
    reps_data = [
        ("Priya","X",2,1200000),("Priya","Y",3,800000),("Priya","Z",1,2500000),
        ("Raj","X",1,1200000),("Raj","Y",2,800000),("Raj","Z",3,2500000),
        ("Meena","X",0,1200000),("Meena","Y",1,800000),("Meena","Z",0,2500000),
        ("Arun","X",3,1200000),("Arun","Y",1,800000),("Arun","Z",2,2500000),
        ("Sita","X",1,1200000),("Sita","Y",2,800000),("Sita","Z",1,2500000),
    ]
    _write_csv(folder / "monthly_sales.csv", [
        {"Rep":r[0],"Product":r[1],"Units Sold":r[2],"Revenue per Unit (₹)":r[3],"Total Revenue (₹)":r[2]*r[3]}
        for r in reps_data
    ])
    _write_csv(folder / "commission_rules.csv", [
        {"Rule":"Base Commission","Value":"3% of total monthly revenue"},
        {"Rule":"High-Margin Mix Bonus (≥40% high-margin)","Value":"1.5x multiplier"},
        {"Rule":"Medium-Margin Mix Bonus (≥25% but <40%)","Value":"1.25x multiplier"},
        {"Rule":"Low-Margin Mix Bonus (<25%)","Value":"1.0x multiplier"},
        {"Rule":"Monthly Commission Cap","Value":"₹2,00,000"},
        {"Rule":"Comparison Baseline","Value":"Flat 4% commission"},
    ])
    _write_readme(folder, title, 18, "Intermediate", "Algorithmic", [
        {"name":"product_lines.csv","rows":3,"cols":4,"desc":"3 product lines with margins"},
        {"name":"monthly_sales.csv","rows":15,"cols":5,"desc":"5 reps × 3 products"},
        {"name":"commission_rules.csv","rows":6,"cols":2,"desc":"Commission structure"},
    ], "Synthetic sales data.")


# ── ALGORITHMIC: Case 23 — Log Incident Categorization ──────────────────

def gen_023(out: Path):
    cid, title, folder = "023", "Server Log Incident Categorization", out / "023-log-incident-categorization"
    rng = _rng(cid)
    samples = [
        ("L01","09:15:22","ERROR","auth-service","Auth fail for user admin: invalid token"),
        ("L02","09:17:05","WARN","api-gateway","Rate limit approaching for client 10.0.1.50"),
        ("L03","09:22:01","CRITICAL","db-primary","Connection pool exhausted — connections: 198/200"),
        ("L04","09:30:44","ERROR","web-server","File not found: /etc/nginx/ssl/cert.pem"),
        ("L05","09:35:12","CRITICAL","payment-svc","Health check fail on endpoint /health — 502 Bad Gateway"),
        ("L06","09:41:30","WARN","cache-cluster","Memory usage 85% — threshold 80%"),
        ("L07","09:48:15","ERROR","auth-service","Null reference on user session deserialization"),
        ("L08","09:52:03","CRITICAL","web-server","Service unreachable from load balancer — 503"),
        ("L09","09:58:44","WARN","api-gateway","SSL certificate will expire in 7 days"),
        ("L10","10:05:22","ERROR","order-svc","Business logic violation: negative quantity (-2)"),
        ("L11","10:12:01","CRITICAL","db-primary","Connection refused on replica 10.0.2.15:3306"),
        ("L12","10:18:33","WARN","web-server","CPU temperature 78°C — warning threshold 75°C"),
        ("L13","10:25:10","ERROR","search-svc","Missing env variable: ELASTICSEARCH_URL"),
        ("L14","10:30:45","CRITICAL","payment-svc","Fraud detection service timeout (>30s)"),
        ("L15","10:35:22","ERROR","user-svc","Invalid parameter: age = -5 in create_user"),
    ]
    _write_csv(folder / "sample_logs.csv", [
        {"ID":s[0],"Timestamp":s[1],"Log Level":s[2],"Source":s[3],"Message":s[4]} for s in samples
    ])
    _write_csv(folder / "category_keywords.csv", [
        {"Category":"Security","Trigger Keywords":"auth fail, unauthorized, ssl, certificate, invalid token, block, suspicious, rate limit"},
        {"Category":"Performance","Trigger Keywords":"slow, timeout, cpu, memory, threshold exceed, pool exhaust, latency"},
        {"Category":"Availability","Trigger Keywords":"unreachable, health check fail, 502, 503, down, refused connection"},
        {"Category":"Configuration","Trigger Keywords":"file not found, missing, env variable, not set, wrong param, version mismatch"},
        {"Category":"Application","Trigger Keywords":"null reference, invalid, business logic, contract violation, negative, exception"},
        {"Category":"Unknown","Trigger Keywords":"(default — no match)"},
    ])
    _write_readme(folder, title, 23, "Intermediate", "Algorithmic", [
        {"name":"sample_logs.csv","rows":15,"cols":5,"desc":"15 log entries with varying severity"},
        {"name":"category_keywords.csv","rows":6,"cols":2,"desc":"Category→keyword mapping"},
    ], "Synthetic server log data based on typical production incidents.")


# ── ALGORITHMIC: Case 27 — Conversion Funnel ────────────────────────────

def gen_027(out: Path):
    cid, title, folder = "027", "E-Commerce Conversion Funnel", out / "027-conversion-funnel"
    _write_csv(folder / "customer_sessions.csv", [
        {"Session ID":"S01","Customer":"C001","Events":"/ → /products/mobiles → /cart → /checkout → /order/confirm","Duration":"12 min"},
        {"Session ID":"S02","Customer":"C002","Events":"/ → /products/laptops → /products/laptop-123 → /cart → /checkout → /order/confirm","Duration":"18 min"},
        {"Session ID":"S03","Customer":"C003","Events":"/ → /products/mobiles → /cart → /checkout → /order/confirm","Duration":"8 min"},
        {"Session ID":"S04a","Customer":"C004","Events":"/ → /search?q=headphones → /products/headphones-x → /cart","Duration":"5 min"},
        {"Session ID":"S04b","Customer":"C004","Events":"/home → /cart → /checkout → /order/confirm","Duration":"3 min"},
        {"Session ID":"S05","Customer":"C005","Events":"/ → /products/home → /products/sofa → /cart","Duration":"15 min"},
        {"Session ID":"S06","Customer":"C006","Events":"/ → /products/mobiles → /products/phone-a","Duration":"4 min"},
        {"Session ID":"S07","Customer":"C007","Events":"/ → /products/laptops → /products/laptop-456 → /cart → /checkout","Duration":"20 min"},
        {"Session ID":"S08","Customer":"C008","Events":"/ → /products/books","Duration":"2 min"},
        {"Session ID":"S09","Customer":"C009","Events":"/bag → /checkout → /order/confirm","Duration":"6 min"},
        {"Session ID":"S10a","Customer":"C010","Events":"/ → /products/shoes → /products/shoe-789 → /cart → /checkout","Duration":"11 min"},
        {"Session ID":"S10b","Customer":"C010","Events":"/ → /order/confirm","Duration":"2 min"},
    ])
    _write_csv(folder / "page_type_reference.csv", [
        {"Page URL Pattern":"/, /home, /index","Type":"Homepage"},
        {"Page URL Pattern":"/products/*, /category/*","Type":"Product page"},
        {"Page URL Pattern":"/cart, /bag","Type":"Cart page"},
        {"Page URL Pattern":"/checkout*, /payment*","Type":"Checkout page"},
        {"Page URL Pattern":"/order/confirm*","Type":"Order confirmation page"},
        {"Page URL Pattern":"/blog/*, /about, /contact","Type":"Non-product page"},
        {"Page URL Pattern":"/search?q=*","Type":"Search results page"},
    ])
    _write_readme(folder, title, 27, "Intermediate", "Algorithmic", [
        {"name":"customer_sessions.csv","rows":12,"cols":4,"desc":"10 customers' sessions including multi-session"},
        {"name":"page_type_reference.csv","rows":7,"cols":2,"desc":"URL pattern to funnel stage mapping"},
    ], "Synthetic e-commerce session data.")


# ── ALGORITHMIC: Case 30 — Churn Classification ─────────────────────────

def gen_030(out: Path):
    cid, title, folder = "030", "Subscription Churn Classification", out / "030-churn-classification"
    _write_csv(folder / "subscriber_history.csv", [
        {"ID":"S01","Plan":"Premium","Days Since Signup":365,"Last Login (day)":363,"Status":"Active","Cancellation Event":"None","Failed Payments":0,"Support Tickets (last 60 days)":"0"},
        {"ID":"S02","Plan":"Basic","Days Since Signup":240,"Last Login (day)":238,"Status":"Active","Cancellation Event":"None","Failed Payments":1,"Support Tickets (last 60 days)":"1 — Billing question"},
        {"ID":"S03","Plan":"Pro","Days Since Signup":180,"Last Login (day)":50,"Status":"Active","Cancellation Event":"None","Failed Payments":0,"Support Tickets (last 60 days)":"0"},
        {"ID":"S04","Plan":"Free Trial","Days Since Signup":30,"Last Login (day)":29,"Status":"Active","Cancellation Event":"None","Failed Payments":0,"Support Tickets (last 60 days)":"0"},
        {"ID":"S05","Plan":"Premium","Days Since Signup":300,"Last Login (day)":0,"Status":"Cancelled","Cancellation Event":"User cancelled via portal — reason: Too expensive","Failed Payments":1,"Support Tickets (last 60 days)":"2 — Price complaint, cancellation request"},
        {"ID":"S06","Plan":"Basic","Days Since Signup":200,"Last Login (day)":195,"Status":"Suspended","Cancellation Event":"Payment failed after 3 retries","Failed Payments":3,"Support Tickets (last 60 days)":"1 — Payment declined"},
        {"ID":"S07","Plan":"Basic","Days Since Signup":150,"Last Login (day)":5,"Status":"Active","Cancellation Event":"None","Failed Payments":0,"Support Tickets (last 60 days)":"0"},
        {"ID":"S08","Plan":"Premium","Days Since Signup":400,"Last Login (day)":20,"Status":"Active","Cancellation Event":"None","Failed Payments":0,"Support Tickets (last 60 days)":"1 — Feature request"},
        {"ID":"S09","Plan":"Basic","Days Since Signup":90,"Last Login (day)":1,"Status":"Deleted","Cancellation Event":"Account deleted by user","Failed Payments":0,"Support Tickets (last 60 days)":"0"},
        {"ID":"S10","Plan":"Pro","Days Since Signup":500,"Last Login (day)":120,"Status":"Active","Cancellation Event":"None","Failed Payments":0,"Support Tickets (last 60 days)":"0"},
        {"ID":"S11","Plan":"Free Trial","Days Since Signup":14,"Last Login (day)":10,"Status":"Expired","Cancellation Event":"Trial period ended","Failed Payments":0,"Support Tickets (last 60 days)":"0"},
        {"ID":"S12","Plan":"Premium","Days Since Signup":365,"Last Login (day)":360,"Status":"Active","Cancellation Event":"None","Failed Payments":0,"Support Tickets (last 60 days)":"3 — Multiple support requests"},
    ])
    _write_csv(folder / "churn_constants.csv", [
        {"Parameter":"Current Day","Value":365},
        {"Parameter":"Silent Churn Threshold (days)","Value":90},
        {"Parameter":"Payment Retry Attempts","Value":3},
        {"Parameter":"Payment Retry Window (days)","Value":7},
        {"Parameter":"Inactivity Auto-Cancel (days)","Value":180},
        {"Parameter":"Monthly Active Subscribers","Value":5000},
        {"Parameter":"Average Revenue per Subscriber (₹/mo)","Value":2400},
        {"Parameter":"Board Reported Churn Rate (%)","Value":2},
    ])
    _write_readme(folder, title, 30, "Intermediate", "Algorithmic", [
        {"name":"subscriber_history.csv","rows":12,"cols":8,"desc":"12 subscriber records"},
        {"name":"churn_constants.csv","rows":8,"cols":2,"desc":"Churn detection parameters"},
    ], "Synthetic subscription data.")


# ── ALGORITHMIC: Case 32 — Incident Ranking ─────────────────────────────

def gen_032(out: Path):
    cid, title, folder = "032", "Server Incident Ranking", out / "032-server-incident-ranking"
    _write_csv(folder / "q3_incidents.csv", [
        {"Server ID":"WEB-01","Role":"Web Server","Critical Incidents":2,"High Incidents":5,"Medium Incidents":8,"Total Incidents":15},
        {"Server ID":"WEB-02","Role":"Web Server","Critical Incidents":0,"High Incidents":3,"Medium Incidents":6,"Total Incidents":9},
        {"Server ID":"WEB-03","Role":"Web Server","Critical Incidents":1,"High Incidents":4,"Medium Incidents":10,"Total Incidents":15},
        {"Server ID":"WEB-04","Role":"Web Server","Critical Incidents":3,"High Incidents":6,"Medium Incidents":5,"Total Incidents":14},
        {"Server ID":"APP-01","Role":"App Server","Critical Incidents":0,"High Incidents":2,"Medium Incidents":4,"Total Incidents":6},
        {"Server ID":"APP-02","Role":"App Server","Critical Incidents":1,"High Incidents":1,"Medium Incidents":3,"Total Incidents":5},
        {"Server ID":"DB-01","Role":"Database Server","Critical Incidents":2,"High Incidents":3,"Medium Incidents":2,"Total Incidents":7},
        {"Server ID":"DB-02","Role":"Database Server","Critical Incidents":0,"High Incidents":1,"Medium Incidents":1,"Total Incidents":2},
    ])
    _write_csv(folder / "scoring_formulas.csv", [
        {"Formula":"Primary","Critical Weight":5,"High Weight":3,"Medium Weight":1,"Tie Rule":"More critical"},
        {"Formula":"Sensitivity Check","Critical Weight":10,"High Weight":4,"Medium Weight":1,"Tie Rule":"More critical"},
    ])
    _write_readme(folder, title, 32, "Intermediate", "Algorithmic", [
        {"name":"q3_incidents.csv","rows":8,"cols":6,"desc":"8 servers with incident counts"},
        {"name":"scoring_formulas.csv","rows":2,"cols":4,"desc":"Primary and sensitivity scoring"},
    ], "Synthetic incident management data.")


# ── ALGORITHMIC: Case 36 — Sales Reconciliation ─────────────────────────

def gen_036(out: Path):
    cid, title, folder = "036", "Sales Data Reconciliation", out / "036-sales-reconciliation"
    _write_csv(folder / "source1_online.csv", [
        {"Record ID":"ON-01","Date":"15-Sep","Customer":"Ananya Sharma","Items":"Bluetooth Speaker × 1","Amount (₹)":2499,"Status":"Delivered"},
        {"Record ID":"ON-02","Date":"16-Sep","Customer":"Ravi Kumar","Items":"Yoga Mat × 2","Amount (₹)":1598,"Status":"Delivered"},
        {"Record ID":"ON-03","Date":"16-Sep","Customer":"Priya Singh","Items":"Desk Lamp × 1","Amount (₹)":3499,"Status":"Shipped"},
        {"Record ID":"ON-04","Date":"17-Sep","Customer":"Ananya Sharma","Items":"Phone Case × 2","Amount (₹)":998,"Status":"Delivered"},
    ])
    _write_csv(folder / "source2_pos.csv", [
        {"Record ID":"POS-01","Date":"15-Sep","Customer":"Walk-in Customer","Payment Method":"Credit Card","Amount (₹)":2300},
        {"Record ID":"POS-02","Date":"16-Sep","Customer":"Walk-in Customer","Payment Method":"UPI","Amount (₹)":1500},
        {"Record ID":"POS-03","Date":"16-Sep","Customer":"Ananya Sharma","Payment Method":"Debit Card","Amount (₹)":2499},
        {"Record ID":"POS-04","Date":"17-Sep","Customer":"Ravi Kumar","Payment Method":"Cash","Amount (₹)":1600},
        {"Record ID":"POS-05","Date":"17-Sep","Customer":"Walk-in Customer","Payment Method":"UPI","Amount (₹)":1000},
    ])
    _write_csv(folder / "source3_distributor.csv", [
        {"Record ID":"DIST-01","Date":"14-Sep","Distributor":"TechDistrib Co.","Invoice Ref":"INV-9012","Amount (₹)":45000,"Paid":"Yes"},
        {"Record ID":"DIST-02","Date":"15-Sep","Distributor":"HomeGoods Distributors","Invoice Ref":"INV-9015","Amount (₹)":32000,"Paid":"Yes"},
        {"Record ID":"DIST-03","Date":"17-Sep","Distributor":"TechDistrib Co.","Invoice Ref":"INV-9018","Amount (₹)":28000,"Paid":"No"},
        {"Record ID":"DIST-04","Date":"17-Sep","Distributor":"MegaMart Wholesale","Invoice Ref":"INV-9020","Amount (₹)":15000,"Paid":"No"},
    ])
    _write_csv(folder / "reconciliation_rules.csv", [
        {"Rule":"Online-POS Match Tolerance (₹)","Value":100},
        {"Rule":"Distributor Match Tolerance (₹)","Value":500},
        {"Rule":"Online Amount Includes","Value":"GST + delivery"},
        {"Rule":"POS Amount Includes","Value":"GST, no delivery"},
        {"Rule":"Distributor Amount","Value":"Wholesale, ex-GST"},
    ])
    _write_readme(folder, title, 36, "Advanced", "Algorithmic", [
        {"name":"source1_online.csv","rows":4,"cols":6,"desc":"Online store orders"},
        {"name":"source2_pos.csv","rows":5,"cols":5,"desc":"POS system transactions"},
        {"name":"source3_distributor.csv","rows":4,"cols":6,"desc":"Distributor invoices"},
        {"name":"reconciliation_rules.csv","rows":5,"cols":2,"desc":"Matching rules and exclusions"},
    ], "Synthetic multi-source sales data.")


# ── ALGORITHMIC: Case 38 — Row-Level Security ───────────────────────────

def gen_038(out: Path):
    cid, title, folder = "038", "Row-Level Security Rules", out / "038-rls-rule-design"
    _write_csv(folder / "teams_and_roles.csv", [
        {"User ID":"U01","Name":"Amit","Role":"Member","Team":"Infra"},
        {"User ID":"U02","Name":"Bhavana","Role":"Member","Team":"Security"},
        {"User ID":"U03","Name":"Chen","Role":"Manager","Team":"Infra"},
        {"User ID":"U04","Name":"Deepali","Role":"Manager","Team":"Security"},
        {"User ID":"U05","Name":"Eswar","Role":"Director","Team":"IT"},
        {"User ID":"U06","Name":"Fatima","Role":"Director","Team":"Security"},
        {"User ID":"U07","Name":"Gaurav","Role":"Member","Team":"DevOps"},
        {"User ID":"U08","Name":"Hema","Role":"Member","Team":"Database"},
    ])
    _write_csv(folder / "incident_records.csv", [
        {"Record ID":"R01","Description":"EC2 instance unreachable","Owner Team":"Infra","Tagged Teams":"DevOps","Severity":"Critical"},
        {"Record ID":"R02","Description":"SSL certificate expired","Owner Team":"Security","Tagged Teams":"Infra, DevOps","Severity":"High"},
        {"Record ID":"R03","Description":"DB connection pool exhausted","Owner Team":"Database","Tagged Teams":"Infra","Severity":"Critical"},
        {"Record ID":"R04","Description":"Employee phishing simulation results","Owner Team":"Security","Tagged Teams":"","Severity":"Medium"},
        {"Record ID":"R05","Description":"Load balancer config drift","Owner Team":"DevOps","Tagged Teams":"Infra","Severity":"High"},
        {"Record ID":"R06","Description":"Network switch firmware outdated","Owner Team":"Network","Tagged Teams":"Infra","Severity":"Low"},
        {"Record ID":"R07","Description":"IAM policy violation — root activity","Owner Team":"Security","Tagged Teams":"IT","Severity":"Critical"},
        {"Record ID":"R08","Description":"Production deployment failed","Owner Team":"DevOps","Tagged Teams":"","Severity":"High"},
        {"Record ID":"R09","Description":"Database backup failure","Owner Team":"Database","Tagged Teams":"IT","Severity":"Critical"},
        {"Record ID":"R10","Description":"Firewall rule exception request","Owner Team":"Security","Tagged Teams":"Network","Severity":"Medium"},
    ])
    _write_readme(folder, title, 38, "Advanced", "Algorithmic", [
        {"name":"teams_and_roles.csv","rows":8,"cols":4,"desc":"8 users with roles and teams"},
        {"name":"incident_records.csv","rows":10,"cols":5,"desc":"10 incident records with owners and tags"},
    ], "Synthetic RBAC scenario data.")


# ── ANALYTICAL: Case 02 — On-Call Ticket Forecasting ────────────────────

def gen_002(out: Path):
    cid, title, folder = "002", "On-Call Ticket Volume Forecasting", out / "002-ticket-forecasting"
    rng = _rng(cid)
    rows = []
    for i, m in enumerate(["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct"]):
        opened = int(120 + i * 5 + rng.uniform(-15, 15))
        closed = int(opened * (0.85 + rng.uniform(-0.05, 0.1)))
        launch = "Yes" if m in ["Feb","Jun"] else "No"
        hc = 5 + (1 if i >= 5 else 0)
        rows.append({"Month":m,"Tickets Opened":opened,"Tickets Closed":closed,"Feature Launch":launch,"Headcount":hc})
    _write_csv(folder / "monthly_tickets.csv", rows)
    _write_readme(folder, title, 2, "Beginner", "Analytical", [
        {"name":"monthly_tickets.csv","rows":10,"cols":5,"desc":"10 months of ticket data"},
    ], "Synthetic support ticket data.")


# ── ANALYTICAL: Case 03 — Cloud Cost Runaway ────────────────────────────

def gen_003(out: Path):
    cid, title, folder = "003", "Cloud Cost Runaway Diagnosis", out / "003-cloud-cost-runaway"
    rng = _rng(cid)
    services = [
        ("EC2","Platform"), ("S3","Platform"), ("RDS","Data"), ("Lambda","Growth"),
        ("CloudFront","Platform"), ("ElastiCache","Data"), ("SageMaker","ML"),
        ("EKS","Platform"), ("SQS","Growth"), ("DynamoDB","Data"),
        ("Redshift","Data"), ("API Gateway","Growth"), ("VPC NAT Gateway","Platform"),
        ("Glue","Data"), ("Kinesis","Growth"), ("Athena","Data"),
        ("Step Functions","Growth"), ("Elastic Beanstalk","Platform"),
        ("Route53","Platform"), ("Secrets Manager","Security"),
    ]
    rows = []
    for svc, team in services:
        now_cost = int(rng.uniform(100, 5000))
        last_cost = int(now_cost * (0.7 + rng.uniform(-0.1, 0.3)))
        now_usage = int(rng.uniform(100, 10000))
        last_usage = int(now_usage * (0.8 + rng.uniform(-0.1, 0.2)))
        rows.append({"Service":svc,"Team":team,"Cost Now ($)":now_cost,"Cost Last Mo ($)":last_cost,
                      "Usage Now":now_usage,"Usage Last Mo":last_usage})
    _write_csv(folder / "cloud_service_costs.csv", rows)
    _write_readme(folder, title, 3, "Advanced", "Analytical", [
        {"name":"cloud_service_costs.csv","rows":20,"cols":6,"desc":"20 services across 4 teams"},
    ], "Synthetic cloud cost data.")


# ── ANALYTICAL: Case 07 — Incident Postmortem ──────────────────────────

def gen_007(out: Path):
    cid, title, folder = "007", "Incident Postmortem — Incomplete Logs", out / "007-incident-postmortem"
    _write_csv(folder / "log_excerpts.csv", [
        {"Timestamp":"09:58:12","Level":"INFO","Source":"web-server","Message":"Request served: GET /api/orders — 200 OK"},
        {"Timestamp":"10:00:03","Level":"WARN","Source":"api-gateway","Message":"Response time 3200ms — threshold 2000ms"},
        {"Timestamp":"10:02:15","Level":"ERROR","Source":"payment-svc","Message":"Timeout connecting to payment processor"},
        {"Timestamp":"10:05:00","Level":"CRITICAL","Source":"db-primary","Message":"Connection pool exhaustion — active: 200/200"},
        {"Timestamp":"— GAP —","Level":"","Source":"","Message":"10:05 to 10:20 — no logs recorded"},
        {"Timestamp":"10:20:01","Level":"INFO","Source":"web-server","Message":"Health check endpoint returning 200"},
        {"Timestamp":"10:25:33","Level":"ERROR","Source":"payment-svc","Message":"Retry queue depth: 1500 messages"},
        {"Timestamp":"10:30:12","Level":"CRITICAL","Source":"db-primary","Message":"Replica lag: 45 seconds"},
        {"Timestamp":"10:35:44","Level":"WARN","Source":"api-gateway","Message":"Circuit breaker opened for payment-svc"},
        {"Timestamp":"10:40:02","Level":"INFO","Source":"deploy-svc","Message":"Rollback initiated — build #4471"},
    ])
    _write_csv(folder / "deploy_log.csv", [
        {"Timestamp":"06-Sep 09:30","Level":"INFO","Message":"Build #4471 deployed to staging"},
        {"Timestamp":"08-Sep 14:00","Level":"WARN","Message":"Build #4471 auto-promoted to production"},
        {"Timestamp":"08-Sep 15:30","Level":"CRITICAL","Message":"Build #4471 rolled back from production"},
    ])
    _write_readme(folder, title, 7, "Advanced", "Analytical", [
        {"name":"log_excerpts.csv","rows":10,"cols":4,"desc":"Timeline with 15-min log gap"},
        {"name":"deploy_log.csv","rows":3,"cols":3,"desc":"Deployment timeline"},
    ], "Synthetic incident timeline data.")


# ── ANALYTICAL: Case 08 — Vendor Tool Evaluation ────────────────────────

def gen_008(out: Path):
    cid, title, folder = "008", "Vendor Tool Evaluation", out / "008-vendor-tool-evaluation"
    _write_csv(folder / "vendor_comparison.csv", [
        {"Vendor":"A","Price/mo ($)":5000,"Feature Score (/10)":8,"Support SLA":"4-hour response","Integration Effort (days)":14},
        {"Vendor":"B","Price/mo ($)":3500,"Feature Score (/10)":6,"Support SLA":"8-hour response","Integration Effort (days)":7},
        {"Vendor":"C","Price/mo ($)":7000,"Feature Score (/10)":9,"Support SLA":"1-hour response","Integration Effort (days)":21},
    ])
    _write_csv(folder / "stakeholder_priorities.csv", [
        {"Stakeholder":"Engineering","Priority":"Features (9/10 min viable)"},
        {"Stakeholder":"Finance","Priority":"Cost (< $4500/mo)"},
        {"Stakeholder":"Operations","Priority":"Support SLA (< 4-hour response)"},
    ])
    _write_readme(folder, title, 8, "Intermediate", "Analytical", [
        {"name":"vendor_comparison.csv","rows":3,"cols":5,"desc":"3 vendors with price, score, SLA, effort"},
        {"name":"stakeholder_priorities.csv","rows":3,"cols":2,"desc":"3 stakeholder criteria"},
    ], "Synthetic vendor evaluation data.")


# ── ANALYTICAL: Case 09 — Team Velocity Metrics ─────────────────────────

def gen_009(out: Path):
    cid, title, folder = "009", "Team Velocity Metrics", out / "009-team-velocity-metrics"
    _write_csv(folder / "sprint_data.csv", [
        {"Sprint":1,"Story Points":85,"Ticket Count":12,"Avg Ticket Size":7.1,"Bug Reopen Rate (%)":8,"Satisfaction (/10)":7.2},
        {"Sprint":2,"Story Points":92,"Ticket Count":15,"Avg Ticket Size":6.1,"Bug Reopen Rate (%)":5,"Satisfaction (/10)":7.5},
        {"Sprint":3,"Story Points":110,"Ticket Count":22,"Avg Ticket Size":5.0,"Bug Reopen Rate (%)":3,"Satisfaction (/10)":7.8},
        {"Sprint":4,"Story Points":105,"Ticket Count":28,"Avg Ticket Size":3.8,"Bug Reopen Rate (%)":2,"Satisfaction (/10)":8.0},
        {"Sprint":5,"Story Points":115,"Ticket Count":35,"Avg Ticket Size":3.3,"Bug Reopen Rate (%)":1,"Satisfaction (/10)":8.2},
        {"Sprint":6,"Story Points":108,"Ticket Count":40,"Avg Ticket Size":2.7,"Bug Reopen Rate (%)":1,"Satisfaction (/10)":8.1},
    ])
    _write_readme(folder, title, 9, "Intermediate", "Analytical", [
        {"name":"sprint_data.csv","rows":6,"cols":6,"desc":"6 sprints of team metrics"},
    ], "Synthetic agile team data.")


# ── ANALYTICAL: Case 12 — SOC Alert Fatigue ─────────────────────────────

def gen_012(out: Path):
    cid, title, folder = "012", "SOC Analyst Alert Fatigue", out / "012-soc-alert-fatigue"
    rng = _rng(cid)
    rows = []
    for w in range(1, 13):
        week = f"Q1-W{w}" if w <= 6 else f"Q2-W{w-6}"
        alerts = int(800 + rng.uniform(-100, 200) + w * 20)
        suppressed = int(alerts * (0.3 + rng.uniform(-0.05, 0.1)))
        investigated = alerts - suppressed
        tp = int(investigated * (0.05 + rng.uniform(-0.02, 0.05)))
        mttd = round(3.5 + rng.uniform(-1, 2) - w * 0.1, 1)
        esc = int(tp * (0.3 + rng.uniform(-0.1, 0.1)))
        missed = max(0, int(tp * rng.uniform(0.1, 0.3)))
        rows.append({"Week":week,"Alerts Generated":alerts,"Alerts Suppressed":suppressed,
                      "Alerts Investigated":investigated,"True Positives":tp,"MTTD (hrs)":mttd,
                      "Escalations":esc,"Missed Incidents":missed})
    _write_csv(folder / "weekly_soc_data.csv", rows)
    _write_readme(folder, title, 12, "Advanced", "Analytical", [
        {"name":"weekly_soc_data.csv","rows":12,"cols":8,"desc":"12 weeks of SOC metrics"},
    ], "Synthetic SOC alert data.")


# ── ANALYTICAL: Case 15 — Retail Sales Decomposition ────────────────────

def gen_015(out: Path):
    cid, title, folder = "015", "Retail Sales Trend Decomposition", out / "015-retail-sales-decomposition"
    rng = _rng(cid)
    months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    rows = []
    for yr in [2024, 2025]:
        for i, m in enumerate(months):
            base = 450 if yr == 2024 else 520
            seasonal = 1.0 + 0.3 * (i == 11) + 0.2 * (i == 0) + 0.15 * (i == 5 or i == 6) - 0.1 * (i == 2 or i == 8)
            val = int(base * seasonal * 1000 + rng.uniform(-30000, 30000))
            rows.append({"Year":yr,"Month":m,"Sales (₹'000s)":val})
    # 2026 partial (Jan–Feb)
    for i, m in enumerate(["Jan","Feb"]):
        val = int(570 * (1.0 + 0.2 * (i == 0)) * 1000 + rng.uniform(-30000, 30000))
        rows.append({"Year":2026,"Month":m,"Sales (₹'000s)":val})
    _write_csv(folder / "monthly_sales.csv", rows)
    _write_readme(folder, title, 15, "Intermediate", "Analytical", [
        {"name":"monthly_sales.csv","rows":26,"cols":3,"desc":"26 months (2024–2026 Feb)"},
    ], "Synthetic retail sales data with seasonal pattern.")


# ── ANALYTICAL: Case 19 — Nutrition Survey Simpson's Paradox ────────────

def gen_019(out: Path):
    cid, title, folder = "019", "Nutrition Survey Metric Skepticism", out / "019-nutrition-survey-skepticism"
    _write_csv(folder / "year1_survey.csv", [
        {"Income Quartile":"Q1 (Lowest)","Households Surveyed":400,"Avg Daily Calorie Intake (kcal)":1850},
        {"Income Quartile":"Q2","Households Surveyed":300,"Avg Daily Calorie Intake (kcal)":2100},
        {"Income Quartile":"Q3","Households Surveyed":200,"Avg Daily Calorie Intake (kcal)":2450},
        {"Income Quartile":"Q4 (Highest)","Households Surveyed":100,"Avg Daily Calorie Intake (kcal)":2800},
        {"Income Quartile":"Total/Avg","Households Surveyed":1000,"Avg Daily Calorie Intake (kcal)":2150},
    ])
    _write_csv(folder / "year2_survey.csv", [
        {"Income Quartile":"Q1 (Lowest)","Households Surveyed":150,"Avg Daily Calorie Intake (kcal)":1900},
        {"Income Quartile":"Q2","Households Surveyed":200,"Avg Daily Calorie Intake (kcal)":2150},
        {"Income Quartile":"Q3","Households Surveyed":300,"Avg Daily Calorie Intake (kcal)":2400},
        {"Income Quartile":"Q4 (Highest)","Households Surveyed":350,"Avg Daily Calorie Intake (kcal)":2700},
        {"Income Quartile":"Total/Avg","Households Surveyed":1000,"Avg Daily Calorie Intake (kcal)":2350},
    ])
    _write_csv(folder / "survey_constants.csv", [
        {"Parameter":"RDA Minimum (kcal/adult equivalent/day)","Value":2100},
    ])
    _write_readme(folder, title, 19, "Advanced", "Analytical", [
        {"name":"year1_survey.csv","rows":5,"cols":3,"desc":"Year 1 — Q1 overrepresented"},
        {"name":"year2_survey.csv","rows":5,"cols":3,"desc":"Year 2 — Q4 overrepresented"},
        {"name":"survey_constants.csv","rows":1,"cols":2,"desc":"RDA threshold"},
    ], "Synthetic nutrition survey data designed to demonstrate Simpson's Paradox.")


# ── ANALYTICAL: Case 20 — SLA Breach Postmortem ─────────────────────────

def gen_020(out: Path):
    cid, title, folder = "020", "SLA Breach Postmortem", out / "020-sla-breach-postmortem"
    _write_csv(folder / "q3_incident_log.csv", [
        {"ID":"INC-01","Date":"2026-07-12","Duration":"1h 45m","System":"Payment Gateway","Reported Cause":"Database connection pool exhaustion","Evidence Level":"Confirmed"},
        {"ID":"INC-02","Date":"2026-08-05","Duration":"35m","System":"CDN","Reported Cause":"Origin server SSL cert expired","Evidence Level":"Confirmed"},
        {"ID":"INC-03","Date":"2026-08-22","Duration":"2h 10m","System":"Core API","Reported Cause":"Memory leak after deployment","Evidence Level":"Partial"},
        {"ID":"INC-04","Date":"2026-09-18","Duration":"1h 00m","System":"Search Service","Reported Cause":"Unknown — logs unavailable","Evidence Level":"Speculative"},
    ])
    _write_csv(folder / "q3_deployment_timeline.csv", [
        {"Date":"2026-07-05","Change":"New payment provider integration","System":"Payment Gateway","Rollback?":"No"},
        {"Date":"2026-07-10","Change":"CDN config update — SSL cert renewal","System":"CDN","Rollback?":"No"},
        {"Date":"2026-07-28","Change":"API v2.1 deployment","System":"Core API","Rollback?":"Yes"},
        {"Date":"2026-08-04","Change":"Cache invalidation fix","System":"CDN","Rollback?":"No"},
        {"Date":"2026-08-15","Change":"Memory optimization patch","System":"Core API","Rollback?":"No"},
        {"Date":"2026-09-01","Change":"Search index rebuild","System":"Search Service","Rollback?":"No"},
        {"Date":"2026-09-15","Change":"Database failover test","System":"Database","Rollback?":"N/A"},
    ])
    _write_csv(folder / "sla_constants.csv", [
        {"Parameter":"SLA Target (%)","Value":99.9},
        {"Parameter":"SLA Tolerance (min/month)","Value":43},
        {"Parameter":"Q3 Actual Uptime (%)","Value":98.7},
        {"Parameter":"Q3 Total Downtime","Value":"5h 30m"},
        {"Parameter":"Penalty per 0.1% below (₹L)","Value":12},
    ])
    _write_readme(folder, title, 20, "Advanced", "Analytical", [
        {"name":"q3_incident_log.csv","rows":4,"cols":6,"desc":"4 incidents with evidence confidence"},
        {"name":"q3_deployment_timeline.csv","rows":7,"cols":4,"desc":"7 deployments"},
        {"name":"sla_constants.csv","rows":5,"cols":2,"desc":"SLA targets and penalties"},
    ], "Synthetic SLA breach scenario.")


# ── ANALYTICAL: Case 21 — Store Performance Diagnosis ───────────────────

def gen_021(out: Path):
    cid, title, folder = "021", "Store Performance Diagnosis", out / "021-store-performance-diagnosis"
    _write_csv(folder / "store_performance.csv", [
        {"Store":"A","Location Type":"Mall","Size (sq ft)":2500,"Monthly Revenue (₹L)":45,"Profit Margin (%)":15,"Customer Satisfaction (%)":88,"Revenue per Sq Ft (₹)":180,"Employee Retention (%)":75},
        {"Store":"B","Location Type":"High Street","Size (sq ft)":1800,"Monthly Revenue (₹L)":38,"Profit Margin (%)":12,"Customer Satisfaction (%)":82,"Revenue per Sq Ft (₹)":211,"Employee Retention (%)":65},
        {"Store":"C","Location Type":"Small Town","Size (sq ft)":1200,"Monthly Revenue (₹L)":52,"Profit Margin (%)":18,"Customer Satisfaction (%)":92,"Revenue per Sq Ft (₹)":433,"Employee Retention (%)":90},
        {"Store":"D","Location Type":"Mall","Size (sq ft)":3000,"Monthly Revenue (₹L)":55,"Profit Margin (%)":10,"Customer Satisfaction (%)":75,"Revenue per Sq Ft (₹)":183,"Employee Retention (%)":55},
        {"Store":"E","Location Type":"High Street","Size (sq ft)":1500,"Monthly Revenue (₹L)":48,"Profit Margin (%)":20,"Customer Satisfaction (%)":90,"Revenue per Sq Ft (₹)":320,"Employee Retention (%)":85},
        {"Store":"F","Location Type":"Small Town","Size (sq ft)":900,"Monthly Revenue (₹L)":42,"Profit Margin (%)":22,"Customer Satisfaction (%)":95,"Revenue per Sq Ft (₹)":467,"Employee Retention (%)":95},
        {"Store":"G","Location Type":"Mall","Size (sq ft)":2200,"Monthly Revenue (₹L)":35,"Profit Margin (%)":8,"Customer Satisfaction (%)":70,"Revenue per Sq Ft (₹)":159,"Employee Retention (%)":50},
        {"Store":"H","Location Type":"High Street","Size (sq ft)":1600,"Monthly Revenue (₹L)":40,"Profit Margin (%)":14,"Customer Satisfaction (%)":80,"Revenue per Sq Ft (₹)":250,"Employee Retention (%)":70},
    ])
    _write_csv(folder / "industry_benchmarks.csv", [
        {"Metric":"Average Profit Margin (%)","Industry Value":12},
        {"Metric":"Average Employee Retention (%)","Industry Value":70},
    ])
    _write_readme(folder, title, 21, "Intermediate", "Analytical", [
        {"name":"store_performance.csv","rows":8,"cols":8,"desc":"8 stores with multiple metrics"},
        {"name":"industry_benchmarks.csv","rows":2,"cols":2,"desc":"Benchmark data"},
    ], "Synthetic retail store performance data.")


# ── ANALYTICAL: Case 22 — Micronutrient Gap Data Quality ────────────────

def gen_022(out: Path):
    cid, title, folder = "022", "Micronutrient Gap Data Quality Audit", out / "022-micronutrient-gap-audit"
    _write_csv(folder / "rda_thresholds.csv", [
        {"Micronutrient":"Iron","RDA":"9 mg","70% of RDA":"6.3 mg"},
        {"Micronutrient":"Vitamin A","RDA":"600 mcg RAE","70% of RDA":"420 mcg RAE"},
        {"Micronutrient":"Zinc","RDA":"8 mg","70% of RDA":"5.6 mg"},
    ])
    _write_csv(folder / "intake_by_zone.csv", [
        {"Zone":"North","Method":"A (Standardized)","Sample Size":500,"Avg Iron (mg)":8.5,"Avg Vit A (mcg RAE)":520,"Avg Zinc (mg)":7.2},
        {"Zone":"South","Method":"B (Visual Photo)","Sample Size":500,"Avg Iron (mg)":6.8,"Avg Vit A (mcg RAE)":390,"Avg Zinc (mg)":5.8},
        {"Zone":"Combined","Method":"Mixed","Sample Size":1000,"Avg Iron (mg)":7.65,"Avg Vit A (mcg RAE)":455,"Avg Zinc (mg)":6.5},
    ])
    _write_csv(folder / "deficiency_distribution.csv", [
        {"Micronutrient":"Iron","Zone North (%)":28,"Zone South (%)":52},
        {"Micronutrient":"Vitamin A","Zone North (%)":32,"Zone South (%)":48},
        {"Micronutrient":"Zinc","Zone North (%)":30,"Zone South (%)":50},
    ])
    _write_csv(folder / "audit_constants.csv", [
        {"Parameter":"Method B Correction Factor","Value":1.25},
        {"Parameter":"Method B Variance (±%)","Value":5},
        {"Parameter":"Supplementation Programme Cost (₹Cr)","Value":2.4},
        {"Parameter":"Previous Year Prevalence (Method A only, %)","Value":26},
    ])
    _write_readme(folder, title, 22, "Advanced", "Analytical", [
        {"name":"rda_thresholds.csv","rows":3,"cols":3,"desc":"RDA thresholds for 3 micronutrients"},
        {"name":"intake_by_zone.csv","rows":3,"cols":6,"desc":"Intake by zone and method"},
        {"name":"deficiency_distribution.csv","rows":3,"cols":3,"desc":"% below threshold by zone"},
        {"name":"audit_constants.csv","rows":4,"cols":2,"desc":"Correction factor and costs"},
    ], "Synthetic nutrition survey data with methodology bias.")


# ── ANALYTICAL: Case 25 — RDA Compliance Threshold Critique ─────────────

def gen_025(out: Path):
    cid, title, folder = "025", "RDA Compliance Threshold Critique", out / "025-rda-compliance-threshold"
    _write_csv(folder / "rda_and_current_intake.csv", [
        {"Nutrient":"Energy (kcal)","RDA":2100,"Current Avg Intake":1850,"% of RDA (avg)":88},
        {"Nutrient":"Protein (g)","RDA":60,"Current Avg Intake":48,"% of RDA (avg)":80},
        {"Nutrient":"Iron (mg)","RDA":9,"Current Avg Intake":7.2,"% of RDA (avg)":80},
        {"Nutrient":"Vitamin A (mcg RAE)","RDA":600,"Current Avg Intake":450,"% of RDA (avg)":75},
        {"Nutrient":"Calcium (mg)","RDA":1000,"Current Avg Intake":720,"% of RDA (avg)":72},
    ])
    _write_csv(folder / "household_energy_distribution.csv", [
        {"Intake Band (kcal)":"< 1,050","% of RDA":"< 50%","Households":45},
        {"Intake Band (kcal)":"1,050–1,260","% of RDA":"50–60%","Households":78},
        {"Intake Band (kcal)":"1,260–1,470","% of RDA":"60–70%","Households":130},
        {"Intake Band (kcal)":"1,470–1,680","% of RDA":"70–80%","Households":205},
        {"Intake Band (kcal)":"1,680–2,100","% of RDA":"80–100%","Households":312},
        {"Intake Band (kcal)":"> 2,100","% of RDA":"> 100%","Households":230},
    ])
    _write_csv(folder / "dashboard_constants.csv", [
        {"Parameter":"Current Compliance Threshold (% of RDA)","Value":70},
        {"Parameter":"Dashboard Headline","Value":"82% of households are RDA-compliant"},
        {"Parameter":"Total Households Surveyed","Value":1000},
        {"Parameter":"Supplementary Nutrition Budget (₹Cr)","Value":1.8},
    ])
    _write_readme(folder, title, 25, "Intermediate", "Analytical", [
        {"name":"rda_and_current_intake.csv","rows":5,"cols":4,"desc":"5 nutrients — RDA vs intake"},
        {"name":"household_energy_distribution.csv","rows":6,"cols":3,"desc":"Distribution of households by intake band"},
        {"name":"dashboard_constants.csv","rows":4,"cols":2,"desc":"Threshold, headline, budget"},
    ], "Synthetic nutrition compliance data.")


# ── ANALYTICAL: Case 28 — School Meal KPI ───────────────────────────────

def gen_028(out: Path):
    cid, title, folder = "028", "School Meal KPI Deep-Dive", out / "028-school-meal-kpi"
    rng = _rng(cid)
    schools = ["GPS North","GPS South","GHS East","GHS West","KPS Central","KPS Town"]
    months = ["Jul","Aug","Sep"]
    rows = []
    for s in schools:
        enrolled = {"GPS North":400,"GPS South":350,"GHS East":250,"GHS West":200,"KPS Central":500,"KPS Town":300}[s]
        for m in months:
            days = {"Jul":22,"Aug":21,"Sep":22}[m]
            planned = enrolled * days
            attendance_pct = {"GPS North":0.88,"GPS South":0.82,"GHS East":0.75,"GHS West":0.70,"KPS Central":0.92,"KPS Town":0.85}[s]
            attendance = int(enrolled * attendance_pct)
            meals = int(attendance * days * (0.95 + rng.uniform(-0.02, 0.03)))
            rows.append({"School":s,"Month":m,"Reported Enrollment":enrolled,"School Days":days,
                          "Meals Planned":planned,"Meals Served":meals,"Avg Daily Attendance":attendance})
    _write_csv(folder / "monthly_school_meal_data.csv", rows)
    _write_csv(folder / "kpi_constants.csv", [
        {"Parameter":"Dashboard KPI Formula","Value":"Coverage = Meals Served / Meals Planned × 100"},
        {"Parameter":"Target Coverage (%)","Value":90},
    ])
    _write_readme(folder, title, 28, "Advanced", "Analytical", [
        {"name":"monthly_school_meal_data.csv","rows":18,"cols":7,"desc":"6 schools × 3 months"},
        {"name":"kpi_constants.csv","rows":2,"cols":2,"desc":"KPI formula and target"},
    ], "Synthetic school meal data with phantom enrollment bias.")


# ── ANALYTICAL: Case 31 — Deficiency Hotspot Ranking ────────────────────

def gen_031(out: Path):
    cid, title, folder = "031", "Deficiency Hotspot Ranking", out / "031-deficiency-hotspot-ranking"
    rng = _rng(cid)
    districts = ["Guntur","Nalgonda","Warangal","Khammam","Kurnool","Prakasam","Srikakulam","Vizianagaram"]
    rows = []
    for d in districts:
        pop = round(rng.uniform(15, 45), 1)
        iron = int(rng.uniform(20, 55))
        vita = int(rng.uniform(15, 50))
        zinc = int(rng.uniform(18, 45))
        multi = int((iron + vita + zinc) / 3 * rng.uniform(0.3, 0.6))
        rows.append({"District":d,"Population (Lakhs)":pop,"Iron Deficiency (%)":iron,
                      "Vitamin A Deficiency (%)":vita,"Zinc Deficiency (%)":zinc,"Multi-Deficiency (%)":multi})
    _write_csv(folder / "district_deficiency_data.csv", rows)
    _write_csv(folder / "funding_constants.csv", [
        {"Parameter":"Total Intervention Fund (₹Cr)","Value":3},
        {"Parameter":"Allocation Rule","Value":"Top 3: 50%, 30%, 20%"},
        {"Parameter":"Previous Year Basis","Value":"Iron deficiency alone"},
    ])
    _write_readme(folder, title, 31, "Advanced", "Analytical", [
        {"name":"district_deficiency_data.csv","rows":8,"cols":6,"desc":"8 districts with multiple deficiency metrics"},
        {"name":"funding_constants.csv","rows":3,"cols":2,"desc":"Funding rules"},
    ], "Synthetic public health data.")


# ── ANALYTICAL: Case 34 — Food Consumption Patterns ─────────────────────

def gen_034(out: Path):
    cid, title, folder = "034", "Food Consumption Pattern Analysis", out / "034-food-consumption-patterns"
    _write_csv(folder / "monthly_per_capita_consumption.csv", [
        {"Food Group":"Cereals","Urban High Income (kg/L)":15.2,"Urban Low Income (kg/L)":12.8,"Rural High Income (kg/L)":18.5,"Rural Low Income (kg/L)":14.2},
        {"Food Group":"Pulses","Urban High Income (kg/L)":3.5,"Urban Low Income (kg/L)":2.2,"Rural High Income (kg/L)":4.1,"Rural Low Income (kg/L)":2.8},
        {"Food Group":"Vegetables","Urban High Income (kg/L)":12.0,"Urban Low Income (kg/L)":8.5,"Rural High Income (kg/L)":10.5,"Rural Low Income (kg/L)":7.5},
        {"Food Group":"Fruits","Urban High Income (kg/L)":8.5,"Urban Low Income (kg/L)":3.2,"Rural High Income (kg/L)":5.5,"Rural Low Income (kg/L)":2.0},
        {"Food Group":"Milk","Urban High Income (kg/L)":18.0,"Urban Low Income (kg/L)":8.0,"Rural High Income (kg/L)":12.0,"Rural Low Income (kg/L)":6.5},
        {"Food Group":"Meat & Fish","Urban High Income (kg/L)":6.5,"Urban Low Income (kg/L)":3.5,"Rural High Income (kg/L)":4.0,"Rural Low Income (kg/L)":1.5},
        {"Food Group":"Eggs","Urban High Income (kg/L)":1.2,"Urban Low Income (kg/L)":0.6,"Rural High Income (kg/L)":0.8,"Rural Low Income (kg/L)":0.3},
        {"Food Group":"Oils & Fats","Urban High Income (kg/L)":2.5,"Urban Low Income (kg/L)":1.8,"Rural High Income (kg/L)":3.0,"Rural Low Income (kg/L)":2.2},
        {"Food Group":"Sugar & Jaggery","Urban High Income (kg/L)":2.0,"Urban Low Income (kg/L)":1.5,"Rural High Income (kg/L)":2.2,"Rural Low Income (kg/L)":1.8},
        {"Food Group":"Spices & Condiments","Urban High Income (kg/L)":0.8,"Urban Low Income (kg/L)":0.6,"Rural High Income (kg/L)":0.9,"Rural Low Income (kg/L)":0.7},
    ])

    _write_csv(folder / "survey_group_sizes.csv", [
        {"Group":"Urban High Income","Households Sampled":250},
        {"Group":"Urban Low Income","Households Sampled":250},
        {"Group":"Rural High Income","Households Sampled":250},
        {"Group":"Rural Low Income","Households Sampled":250},
    ])
    _write_csv(folder / "consumption_constants.csv", [
        {"Parameter":"RDA Minimum (kg/capita/month)","Value":14.5},
        {"Parameter":"Urban Average (kg)","Value":22.4},
        {"Parameter":"Rural Average (kg)","Value":18.4},
        {"Parameter":"Urban-Rural Gap (%)","Value":22},
    ])
    _write_readme(folder, title, 34, "Intermediate", "Analytical", [
        {"name":"monthly_per_capita_consumption.csv","rows":10,"cols":5,"desc":"10 food groups × 4 demographic groups"},
        {"name":"survey_group_sizes.csv","rows":4,"cols":2,"desc":"Sample sizes per group"},
        {"name":"consumption_constants.csv","rows":4,"cols":2,"desc":"RDA minimum and averages"},
    ], "Synthetic food consumption survey data based on NSSO patterns.")


# ── ANALYTICAL: Case 35 — Incident Trend Analysis ───────────────────────

def gen_035(out: Path):
    cid, title, folder = "035", "Incident Trend Analysis", out / "035-incident-trend-analysis"
    rng = _rng(cid)
    months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    rows_2026 = []
    for i, m in enumerate(months):
        crit = int(rng.uniform(1, 6))
        high = int(rng.uniform(5, 15))
        med = int(rng.uniform(8, 25))
        rows_2026.append({"Month":m,"Critical":crit,"High":high,"Medium":med,"Total":crit+high+med})
    _write_csv(folder / "incidents_2026.csv", rows_2026)
    _write_csv(folder / "incidents_2025.csv", [
        {"Month":m,"Total":rng.randint(25, 60)} for m, rng in zip(months, [_rng(f"{cid}-2025-{i}") for i in range(12)])
    ])
    _write_csv(folder / "trend_constants.csv", [
        {"Parameter":"New Monitoring System Deployed","Value":"July 1, 2026"},
        {"Parameter":"System Cost (₹L)","Value":35},
        {"Parameter":"NOC Manager's Claim","Value":"30% reduction"},
    ])
    _write_readme(folder, title, 35, "Intermediate", "Analytical", [
        {"name":"incidents_2026.csv","rows":12,"cols":5,"desc":"2026 monthly incidents by severity"},
        {"name":"incidents_2025.csv","rows":12,"cols":2,"desc":"2025 monthly totals"},
        {"name":"trend_constants.csv","rows":3,"cols":2,"desc":"Context parameters"},
    ], "Synthetic incident trend data.")


# ── ANALYTICAL: Case 37 — RDA Radar Chart Scaling ───────────────────────

def gen_037(out: Path):
    cid, title, folder = "037", "RDA Radar Chart Scaling", out / "037-rda-radar-chart-scaling"
    nutrients = [
        ("Energy",2100,1850,"kcal"),
        ("Protein",60,48,"g"),
        ("Iron",9,7.2,"mg"),
        ("Vitamin A",600,450,"mcg RAE"),
        ("Calcium",1000,720,"mg"),
        ("Vitamin C",80,55,"mg"),
        ("Fiber",30,22,"g"),
    ]
    _write_csv(folder / "household_a_intake.csv", [
        {"Nutrient":n[0],"RDA (adult female)":n[1],"Household A Intake":n[2],"Unit":n[3]} for n in nutrients
    ])
    # Household B — different pattern (high in some, low in others)
    b_vals = [1950, 52, 6.5, 520, 680, 70, 25]
    _write_csv(folder / "household_b_intake.csv", [
        {"Nutrient":n[0],"RDA (adult female)":n[1],"Household B Intake":b_vals[i],"Unit":n[3]} for i, n in enumerate(nutrients)
    ])
    _write_csv(folder / "chart_constants.csv", [
        {"Parameter":"RDA Cap for Visual Consistency (%)","Value":150},
        {"Parameter":"Axis Scaling","Value":"Independent axes allowed"},
    ])
    _write_readme(folder, title, 37, "Advanced", "Analytical", [
        {"name":"household_a_intake.csv","rows":7,"cols":4,"desc":"Household A — moderate, balanced"},
        {"name":"household_b_intake.csv","rows":7,"cols":4,"desc":"Household B — uneven pattern"},
        {"name":"chart_constants.csv","rows":2,"cols":2,"desc":"Scaling rules"},
    ], "Synthetic nutrition data for visualization bias analysis.")


# ── ANALYTICAL: Case 39 — Executive Dashboard KPI Redundancy ────────────

def gen_039(out: Path):
    cid, title, folder = "039", "Executive Dashboard KPI Redundancy", out / "039-executive-dashboard-kpi"
    rng = _rng(cid)
    months = ["Apr","May","Jun","Jul","Aug","Sep"]
    rows = []
    for m in months:
        i = months.index(m)
        revenue = round(120 + i * 8 + rng.uniform(-3, 5), 1)
        new_cust = int(180 + i * 12 + rng.uniform(-10, 15))
        aov_values = [2100, 1900, 2450, 1800, 2600, 2000]
        retention = int(72 + i * 1.5 + rng.uniform(-2, 3))
        utilization = int(68 + i * 2 + rng.uniform(-3, 5))
        profit = round(8.5 + i * 0.5 + rng.uniform(-0.5, 0.8), 1)
        rows.append({"Month":m,"Total Revenue (₹L)":revenue,"New Customers":new_cust,
                      "Avg Order Value (₹)":aov_values[i],"Retention Rate (%)":retention,
                      "Sales Team Utilization (%)":utilization,"Profit Margin (%)":profit})
    _write_csv(folder / "monthly_kpi_data.csv", rows)
    _write_csv(folder / "kpi_definitions.csv", [
        {"KPI":"Total Revenue","Formula":"Sum of all sales","Dimension":"Growth"},
        {"KPI":"New Customers","Formula":"Count of first-time buyers","Dimension":"Acquisition"},
        {"KPI":"Avg Order Value","Formula":"Total Revenue / Total Orders","Dimension":"Spending depth"},
        {"KPI":"Retention Rate","Formula":"Repeat customers / total customers","Dimension":"Loyalty"},
        {"KPI":"Sales Team Utilization","Formula":"Billable hours / available hours","Dimension":"Activity"},
        {"KPI":"Profit Margin","Formula":"(Revenue − COGS − Overhead) / Revenue","Dimension":"Efficiency"},
    ])
    _write_readme(folder, title, 39, "Intermediate", "Analytical", [
        {"name":"monthly_kpi_data.csv","rows":6,"cols":7,"desc":"6 months of 6 KPIs"},
        {"name":"kpi_definitions.csv","rows":6,"cols":3,"desc":"KPI formulas and dimensions"},
    ], "Synthetic executive dashboard data.")


# ── MAIN ─────────────────────────────────────────────────────────────────

GENERATORS = {
    "001": gen_001, "002": gen_002, "003": gen_003, "004": gen_004,
    "005": gen_005, "006": gen_006, "007": gen_007, "008": gen_008,
    "009": gen_009, "010": gen_010, "011": gen_011, "012": gen_012,
    "013": gen_013, "014": gen_014, "015": gen_015, "016": gen_016,
    "017": gen_017, "018": gen_018, "019": gen_019, "020": gen_020,
    "021": gen_021, "022": gen_022, "023": gen_023, "024": gen_024,
    "025": gen_025, "026": gen_026, "027": gen_027, "028": gen_028,
    "029": gen_029, "030": gen_030, "031": gen_031, "032": gen_032,
    "033": gen_033, "034": gen_034, "035": gen_035, "036": gen_036,
    "037": gen_037, "038": gen_038, "039": gen_039,
}

def main():
    global SEED
    parser = argparse.ArgumentParser(description="Generate all Aplly.xyz case-study datasets")
    parser.add_argument("--seed", default=SEED, help="Random seed for reproducibility")
    parser.add_argument("--output", type=Path, default=DATASETS_DIR, help="Output directory")
    parser.add_argument("--cases", nargs="+", default=None, help="Specific case IDs to generate (e.g., 001 013)")
    args = parser.parse_args()
    SEED = args.seed

    to_generate = args.cases or sorted(GENERATORS.keys())
    for cid in to_generate:
        if cid not in GENERATORS:
            print(f"WARNING: Unknown case {cid}, skipping")
            continue
        print(f"Generating case {cid}...")
        GENERATORS[cid](args.output)
    print(f"Done. Generated {len(to_generate)} datasets in {args.output}")

if __name__ == "__main__":
    main()
