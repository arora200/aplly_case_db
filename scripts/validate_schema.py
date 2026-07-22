#!/usr/bin/env python3
"""
CI validation: checks every CSV file against its expected schema.
Run as: python scripts/validate_schema.py
Exits with code 1 if any validation fails.
"""

import csv, sys, json, re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DATASETS_DIR = REPO_ROOT / "datasets"

# Expected schemas: {path_suffix: [column_name, ...]}
# The path_suffix is relative to the dataset folder.
EXPECTED_SCHEMAS = {
    "001-capacity-planning/monthly_traffic.csv":
        ["Month", "Avg req/sec", "Cumulative Signups"],
    "001-capacity-planning/server_specs.csv":
        ["Server Type", "Capacity (req/sec)", "Current Count"],
    "001-capacity-planning/black_friday_params.csv":
        ["Parameter", "Value"],
    "002-ticket-forecasting/monthly_tickets.csv":
        ["Month", "Tickets Opened", "Tickets Closed", "Feature Launch", "Headcount"],
    "003-cloud-cost-runaway/cloud_service_costs.csv":
        ["Service", "Team", "Cost Now ($)", "Cost Last Mo ($)", "Usage Now", "Usage Last Mo"],
    "004-fair-on-call-rotation/engineer_availability.csv":
        ["Engineer", "Availability", "Blackout Weeks", "Past-Quarter On-Call Count"],
    "005-silent-pipeline-failure/sample_input.csv":
        ["order_id", "currency", "amount", "order_timestamp"],
    "006-caching-strategy/traffic_pattern.csv":
        ["Hour Block", "Reads/sec", "Writes/sec"],
    "007-incident-postmortem/log_excerpts.csv":
        ["Timestamp", "Level", "Source", "Message"],
    "008-vendor-tool-evaluation/vendor_comparison.csv":
        ["Vendor", "Price/mo ($)", "Feature Score (/10)", "Support SLA", "Integration Effort (days)"],
    "009-team-velocity-metrics/sprint_data.csv":
        ["Sprint", "Story Points", "Ticket Count", "Avg Ticket Size", "Bug Reopen Rate (%)", "Satisfaction (/10)"],
    "010-server-migration-cost/server_inventory.csv":
        ["Server ID", "Role", "vCPU", "RAM (GB)", "Storage (GB)", "Monthly Egress (GB)", "Current On-Prem Cost ($/mo)"],
    "011-log-rotation-debug/directory_state.csv":
        ["File", "Description"],
    "012-soc-alert-fatigue/weekly_soc_data.csv":
        ["Week", "Alerts Generated", "Alerts Suppressed", "Alerts Investigated", "True Positives", "MTTD (hrs)", "Escalations", "Missed Incidents"],
    "013-food-budget-icds/family_composition.csv":
        ["Member", "Age", "Gender", "Category"],
    "013-food-budget-icds/rda_daily_requirements.csv":
        ["Food Group", "Adult Male (g/ml)", "Adult Female (g/ml)", "Child (7-12) (g/ml)", "Child (4-7) (g/ml)", "Child (1-4) (g/ml)"],
    "013-food-budget-icds/market_rates.csv":
        ["Food Group", "Rate (₹/unit)", "Unit"],
    "014-data-center-power-cost/power_constants.csv":
        ["Parameter", "Value"],
    "015-retail-sales-decomposition/monthly_sales.csv":
        ["Year", "Month", "Sales (₹'000s)"],
    "016-diet-quality-index/scoring_rules.csv":
        ["Component", "Max Pts", "Rule"],
    "017-on-call-rotation-schedule/team_roster.csv":
        ["ID", "Name", "Shifts per week"],
    "018-sales-commission/product_lines.csv":
        ["Product Line", "Gross Margin (%)", "Commission Tier", "Typical Deal Size"],
    "019-nutrition-survey-skepticism/year1_survey.csv":
        ["Income Quartile", "Households Surveyed", "Avg Daily Calorie Intake (kcal)"],
    "020-sla-breach-postmortem/q3_incident_log.csv":
        ["ID", "Date", "Duration", "System", "Reported Cause", "Evidence Level"],
    "021-store-performance-diagnosis/store_performance.csv":
        ["Store", "Location Type", "Size (sq ft)", "Monthly Revenue (₹L)", "Profit Margin (%)", "Customer Satisfaction (%)", "Revenue per Sq Ft (₹)", "Employee Retention (%)"],
    "022-micronutrient-gap-audit/rda_thresholds.csv":
        ["Micronutrient", "RDA", "70% of RDA"],
    "023-log-incident-categorization/sample_logs.csv":
        ["ID", "Timestamp", "Log Level", "Source", "Message"],
    "024-product-category-profitability/category_data.csv":
        ["Category", "Revenue (₹L)", "COGS (₹L)", "Floor Space (sq ft)", "Staff Hours (%)"],
    "025-rda-compliance-threshold/rda_and_current_intake.csv":
        ["Nutrient", "RDA", "Current Avg Intake", "% of RDA (avg)"],
    "026-server-capacity-projection/current_usage.csv":
        ["Tier", "Servers", "CPU Capacity (cores)", "Current CPU Usage (cores)", "CPU Util %", "RAM Capacity (GB)", "Current RAM Usage (GB)", "Storage Capacity (TB)", "Current Storage Used (TB)"],
    "027-conversion-funnel/customer_sessions.csv":
        ["Session ID", "Customer", "Events", "Duration"],
    "028-school-meal-kpi/monthly_school_meal_data.csv":
        ["School", "Month", "Reported Enrollment", "School Days", "Meals Planned", "Meals Served", "Avg Daily Attendance"],
    "029-finops-cost-decomposition/monthly_cloud_spend.csv":
        ["Service Category", "Apr", "May", "Jun", "Jul", "Aug", "Sep"],
    "030-churn-classification/subscriber_history.csv":
        ["ID", "Plan", "Days Since Signup", "Last Login (day)", "Status", "Cancellation Event", "Failed Payments", "Support Tickets (last 60 days)"],
    "031-deficiency-hotspot-ranking/district_deficiency_data.csv":
        ["District", "Population (Lakhs)", "Iron Deficiency (%)", "Vitamin A Deficiency (%)", "Zinc Deficiency (%)", "Multi-Deficiency (%)"],
    "032-server-incident-ranking/q3_incidents.csv":
        ["Server ID", "Role", "Critical Incidents", "High Incidents", "Medium Incidents", "Total Incidents"],
    "033-customer-ltv-ranking/customer_purchase_history.csv":
        ["Customer ID", "First Purchase", "Last Purchase", "Total Orders", "Total Revenue (₹)"],
    "034-food-consumption-patterns/monthly_per_capita_consumption.csv":
        ["Food Group", "Urban High Income (kg/L)", "Urban Low Income (kg/L)", "Rural High Income (kg/L)", "Rural Low Income (kg/L)"],
    "035-incident-trend-analysis/incidents_2026.csv":
        ["Month", "Critical", "High", "Medium", "Total"],
    "036-sales-reconciliation/source1_online.csv":
        ["Record ID", "Date", "Customer", "Items", "Amount (₹)", "Status"],
    "037-rda-radar-chart-scaling/household_a_intake.csv":
        ["Nutrient", "RDA (adult female)", "Household A Intake", "Unit"],
    "038-rls-rule-design/teams_and_roles.csv":
        ["User ID", "Name", "Role", "Team"],
    "039-executive-dashboard-kpi/monthly_kpi_data.csv":
        ["Month", "Total Revenue (₹L)", "New Customers", "Avg Order Value (₹)", "Retention Rate (%)", "Sales Team Utilization (%)", "Profit Margin (%)"],
}

def validate():
    errors = []
    for path_suffix, expected_cols in EXPECTED_SCHEMAS.items():
        full_path = DATASETS_DIR / path_suffix
        if not full_path.exists():
            errors.append(f"MISSING: {path_suffix}")
            continue
        try:
            with open(full_path, newline="", encoding="utf-8") as f:
                reader = csv.reader(f)
                header = next(reader, [])
        except Exception as e:
            errors.append(f"READ ERROR: {path_suffix}: {e}")
            continue

        # Trim whitespace
        header = [c.strip() for c in header]
        if header != expected_cols:
            errors.append(f"SCHEMA MISMATCH: {path_suffix}")
            errors.append(f"  Expected: {expected_cols}")
            errors.append(f"  Got:      {header}")

    if errors:
        sys.stdout.reconfigure(encoding='utf-8')
        print(f"VALIDATION FAILED — {len(errors)} issue(s):")
        for e in errors:
            print(f"  {e}")
        sys.exit(1)
    else:
        sys.stdout.reconfigure(encoding='utf-8')
        print(f"VALIDATION PASSED — {len(EXPECTED_SCHEMAS)} schemas checked, 0 issues.")
        sys.exit(0)

if __name__ == "__main__":
    validate()
