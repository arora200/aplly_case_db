"""Deep analytics on all 225 case studies — gap identification report."""

import json, os, re, glob, sys
from collections import Counter, defaultdict

DUMP_DIR = os.path.join(os.path.dirname(__file__), "..", "db_dump")
OUT_DIR = os.path.join(os.path.dirname(__file__), "..")

def load_all():
    files = sorted(glob.glob(os.path.join(DUMP_DIR, "*.json")))
    cases = []
    for f in files:
        with open(f, encoding="utf-8") as fh:
            cases.append(json.load(fh))
    return cases

def has_url(text):
    if not text:
        return False
    return bool(re.search(r'https?://[^\s,]+', str(text)))

def count_words(text):
    if not text:
        return 0
    return len(str(text).split())

def analyze(cases):
    report = []
    metrics = defaultdict(list)

    # ── Global counters ──
    total = len(cases)
    missing_data_sources = 0
    na_data_sources = 0
    empty_data_sources = 0
    
    missing_source = 0
    vague_source = 0
    url_source = 0
    
    missing_full_content = 0
    short_full_content = 0  # < 100 chars
    missing_solver_guidance = 0
    na_solver_guidance = 0
    missing_prereqs = 0
    missing_difficulty = 0
    beginner_ids = []
    
    missing_solution_frameworks = 0
    na_solution_frameworks = 0
    empty_frameworks = 0
    
    no_dataset_at_all = 0  # data_sources is NA/empty AND no dataset tables in content
    no_tutorial_link = 0  # no URL in solver_guidance, source, or full_content
    
    difficulty_dist = Counter()
    type_dist = Counter()
    category_dist = Counter()
    status_dist = Counter()
    
    # Per-case analysis
    case_issues = []

    for c in cases:
        cid = c["id"]
        title = c.get("title", "")
        slug = c.get("slug", "")
        issues = []
        
        # ── data_sources ──
        ds = c.get("data_sources")
        ds_str = str(ds).strip() if ds else ""
        has_ds_table = bool(re.search(r'\|.*\|.*\|', c.get("full_content", "") or ""))
        
        if not ds or ds_str == "" or ds_str == "None":
            empty_data_sources += 1
            no_dataset_at_all += 1
            issues.append("data_sources: empty/null")
        elif ds_str.upper() in ("NA", "N/A", "NOT APPLICABLE", "-"):
            na_data_sources += 1
            if not has_ds_table:
                no_dataset_at_all += 1
                issues.append("data_sources: NA (and no embedded dataset tables)")
            else:
                issues.append("data_sources: marked NA but has embedded tables (inconsistency)")
        elif count_words(ds_str) < 5:
            issues.append("data_sources: too short (%d words)" % count_words(ds_str))
        
        # ── source ──
        src = c.get("source")
        src_str = str(src).strip() if src else ""
        if not src or src_str == "" or src_str == "None":
            missing_source += 1
            issues.append("source: missing")
        elif has_url(src_str):
            url_source += 1
        elif src_str.upper() in ("NA", "N/A", "-"):
            vague_source += 1
            issues.append("source: NA/vague")
        else:
            # Check if it's a generic reference rather than a real tutorial/dataset link
            vague_patterns = [
                r'practice\s*set', r'interview\s*prep', r'case\s*repository',
                r'hbr', r'harvard\s*business', r'iim\s*ahmedabad', r'iim\s*bangalore',
                r'iim\s*calcutta', r'class\s*notes', r'textbook\s*reference',
                r'market\s*research', r'self[\s-]*study', r'university\s*course',
                r'online\s*article'
            ]
            src_lower = src_str.lower()
            if any(re.search(p, src_lower) for p in vague_patterns):
                vague_source += 1
                issues.append("source: generic reference (not a specific URL/tutorial): %s" % src_str[:80])
        
        # ── full_content ──
        fc = c.get("full_content") or ""
        fc_len = len(fc.strip())
        if fc_len < 50:
            missing_full_content += 1
            issues.append("full_content: essentially empty (%d chars)" % fc_len)
        elif fc_len < 500:
            short_full_content += 1
            issues.append("full_content: very short (%d chars)" % fc_len)
        
        # ── solver_guidance ──
        sg = c.get("solver_guidance")
        sg_str = str(sg).strip() if sg else ""
        if not sg or sg_str == "" or sg_str == "None":
            missing_solver_guidance += 1
            issues.append("solver_guidance: missing")
        elif sg_str.upper() in ("NA", "N/A", "-"):
            na_solver_guidance += 1
            issues.append("solver_guidance: NA")
        elif not has_url(sg_str) and count_words(sg_str) < 5:
            issues.append("solver_guidance: too short (recommended: include tutorial links)")
        
        # ── prerequisite_case_ids ──
        prereq = c.get("prerequisite_case_ids")
        prereq_str = str(prereq).strip() if prereq else ""
        if not prereq or prereq_str in ("", "None", "NULL", "[]"):
            missing_prereqs += 1
        
        # ── difficulty_level ──
        diff = c.get("difficulty_level")
        diff_str = str(diff).strip() if diff else ""
        if not diff or diff_str in ("", "None", "NULL", "0"):
            missing_difficulty += 1
            issues.append("difficulty_level: not set")
        else:
            difficulty_dist[diff_str] += 1
            if diff_str.lower() == "beginner":
                beginner_ids.append(cid)
        
        # ── solution_frameworks ──
        sf = c.get("solution_frameworks")
        sf_str = str(sf).strip() if sf else ""
        if not sf or sf_str == "" or sf_str == "None":
            missing_solution_frameworks += 1
            issues.append("solution_frameworks: missing")
        elif sf_str.upper() in ("NA", "N/A", "-"):
            na_solution_frameworks += 1
            issues.append("solution_frameworks: NA")
        
        # ── Links in full_content ──
        content_has_links = has_url(fc)
        
        # ── Overall tutorial link availability ──
        has_any_tutorial_link = has_url(sg_str) or has_url(src_str) or content_has_links
        if not has_any_tutorial_link:
            no_tutorial_link += 1
            issues.append("NO tutorial/reference link found anywhere")
        
        # ── Status ──
        status_dist[c.get("status", "unknown")] += 1
        
        # ── Category & type ──
        cat = c.get("case_category") or "unknown"
        category_dist[cat] += 1
        ct = c.get("case_type_id")
        type_dist[str(ct)] += 1
        
        # ── Collect per-case ──
        if issues:
            case_issues.append({
                "id": cid,
                "title": title,
                "slug": slug,
                "difficulty": diff_str,
                "data_sources": ds_str[:60] if ds_str else "",
                "source": src_str[:60] if src_str else "",
                "solver_guidance": sg_str[:80] if sg_str else "",
                "issues": issues,
                "issue_count": len(issues),
                "fc_len": fc_len,
            })
    
    # ── Report ──
    r = []
    r.append("# Case Study Quality Analysis Report")
    r.append("")
    r.append("**Generated:** automated analysis of %d case studies from DB\n" % total)
    r.append("---")
    r.append("")
    
    # Executive summary
    r.append("## Executive Summary")
    r.append("")
    severe_cases = [ci for ci in case_issues if ci["issue_count"] >= 4]
    r.append("| Metric | Count | %% of Total |")
    r.append("|---|---|---|")
    r.append("| Total case studies | %d | 100%% |" % total)
    r.append("| Cases with issues | %d | %.1f%% |" % (len(case_issues), len(case_issues)/total*100))
    r.append("| Cases with 4+ issues (critical) | %d | %.1f%% |" % (len(severe_cases), len(severe_cases)/total*100))
    r.append("| Missing/empty data_sources | %d | %.1f%% |" % (empty_data_sources + na_data_sources, (empty_data_sources + na_data_sources)/total*100))
    r.append("| Missing full_content | %d | %.1f%% |" % (missing_full_content, missing_full_content/total*100))
    r.append("| Missing/N/A solver_guidance | %d | %.1f%% |" % (missing_solver_guidance + na_solver_guidance, (missing_solver_guidance + na_solver_guidance)/total*100))
    r.append("| No tutorial link anywhere | %d | %.1f%% |" % (no_tutorial_link, no_tutorial_link/total*100))
    r.append("| Vague/generic source reference | %d | %.1f%% |" % (vague_source, vague_source/total*100))
    r.append("| Missing prereq chain | %d | %.1f%% |" % (missing_prereqs, missing_prereqs/total*100))
    r.append("")
    
    # Detailed section 1: Data Sources Gap
    r.append("---")
    r.append("## 1. Data Sources Gap")
    r.append("")
    r.append("This is the most critical gap. If a case study has no dataset, the solver cannot "
             "practice computational thinking. Two patterns were identified:")
    r.append("")
    r.append("### Pattern A: \"NA\" or Empty data_sources (no dataset at all)")
    r.append("")
    r.append("Cases marked `data_sources: NA` or left empty **and** without embedded dataset tables "
             "in `full_content`. These are effectively unsolvable for computational-thinking exercises "
             "unless the solver finds their own data — which beginners won't know how to do.")
    r.append("")
    # list them
    no_ds_cases = [ci for ci in case_issues if any("data_sources: NA (and no embedded" in i or "data_sources: empty/null" in i for i in ci["issues"])]
    r.append("**Count: %d case studies**" % len(no_ds_cases))
    r.append("")
    r.append("| ID | Title | data_sources | Source |")
    r.append("|---|---|---|---|")
    for ci in sorted(no_ds_cases, key=lambda x: x["id"]):
        src_short = ci["source"][:40] if ci["source"] else "—"
        ds_short = ci["data_sources"][:40] if ci["data_sources"] else "—"
        r.append("| %d | %s | %s | %s |" % (ci["id"], ci["title"][:45], ds_short, src_short))
    r.append("")
    
    # Pattern B: Vague source but no URL
    r.append("### Pattern B: Vague/Generic Source Reference (not a clickable URL)")
    r.append("")
    r.append("The `source` field references a generic repository or publication without a specific "
             "URL. A beginner cannot locate the actual dataset or reference material.")
    r.append("")
    vague_cases = [ci for ci in case_issues if any("source: generic reference" in i for i in ci["issues"])]
    r.append("**Count: %d case studies**" % len(vague_cases))
    r.append("")
    r.append("| ID | Title | Source |")
    r.append("|---|---|---|")
    for ci in sorted(vague_cases, key=lambda x: x["id"]):
        r.append("| %d | %s | %s |" % (ci["id"], ci["title"][:45], ci["source"][:50]))
    r.append("")
    
    # Section 2: Tutorial Link Gap
    r.append("---")
    r.append("## 2. Tutorial / Reference Link Gap")
    r.append("")
    r.append("A case study that provides no clickable URL in `source`, `solver_guidance`, or "
             "`full_content` leaves absolute beginners stranded — they have no path to learn the "
             "underlying concept before attempting the case.")
    r.append("")
    no_link_cases = [ci for ci in case_issues if any("NO tutorial/reference link" in i for i in ci["issues"])]
    r.append("**Count: %d case studies (%.1f%%)**" % (len(no_link_cases), len(no_link_cases)/total*100))
    r.append("")
    r.append("| ID | Title | Difficulty | Source | Solver Guidance |")
    r.append("|---|---|---|---|---|")
    for ci in sorted(no_link_cases, key=lambda x: x["id"]):
        r.append("| %d | %s | %s | %s | %s |" % (
            ci["id"], ci["title"][:40], ci.get("difficulty", "?"),
            ci["source"][:35] if ci["source"] else "—",
            ci["solver_guidance"][:35] if ci["solver_guidance"] else "—"
        ))
    r.append("")
    
    # Section 3: Solver Guidance Gap
    r.append("---")
    r.append("## 3. Solver Guidance / Tutorials Gap")
    r.append("")
    r.append("The `solver_guidance` field is meant to point beginners toward preparatory material. "
             "When it's \"NA\" or empty, the solver has no structured learning path.")
    r.append("")
    nosg_cases = [ci for ci in case_issues if any("solver_guidance: missing" in i or "solver_guidance: NA" in i for i in ci["issues"])]
    r.append("**Count: %d case studies (%.1f%%)**" % (len(nosg_cases), len(nosg_cases)/total*100))
    r.append("")
    r.append("| ID | Title | Difficulty | Solver Guidance |")
    r.append("|---|---|---|---|")
    for ci in sorted(nosg_cases, key=lambda x: x["id"]):
        r.append("| %d | %s | %s | %s |" % (ci["id"], ci["title"][:45], ci.get("difficulty", "?"), ci["solver_guidance"][:50]))
    r.append("")
    
    # Section 4: Full Content Gap
    r.append("---")
    r.append("## 4. Full Content Gap")
    r.append("")
    r.append("Cases where `full_content` is essentially empty (< 50 chars) or very short (< 500 chars).")
    r.append("These are scaffolding-only shells, not usable case studies.")
    r.append("")
    empty_fc = [ci for ci in case_issues if any("full_content: essentially empty" in i for i in ci["issues"])]
    short_fc = [ci for ci in case_issues if any("full_content: very short" in i for i in ci["issues"])]
    r.append("### 4a. Empty full_content (< 50 chars)")
    r.append("**Count: %d**" % len(empty_fc))
    r.append("")
    r.append("| ID | Title | Source |")
    r.append("|---|---|---|")
    for ci in sorted(empty_fc, key=lambda x: x["id"]):
        r.append("| %d | %s | %s |" % (ci["id"], ci["title"][:45], ci["source"][:50]))
    r.append("")
    r.append("### 4b. Very short full_content (50-500 chars)")
    r.append("**Count: %d**" % len(short_fc))
    r.append("")
    r.append("| ID | Title | FC Len | Source |")
    r.append("|---|---|---|---|")
    for ci in sorted(short_fc, key=lambda x: x["id"]):
        r.append("| %d | %s | %d | %s |" % (ci["id"], ci["title"][:45], ci["fc_len"], ci["source"][:50]))
    r.append("")
    
    # Section 5: Prerequisite Chain Gap
    r.append("---")
    r.append("## 5. Prerequisite Chain Gap")
    r.append("")
    r.append("Case studies without prerequisite IDs cannot guide a beginner through a progressive "
             "learning path. Only %d of %d cases set any prerequisites."
             % (total - missing_prereqs, total))
    r.append("")
    r.append("**Cases with missing prerequisites: %d (%.1f%%)**" % (missing_prereqs, missing_prereqs/total*100))
    r.append("")
    
    # Section 6: Difficulty Distribution
    r.append("---")
    r.append("## 6. Difficulty Distribution")
    r.append("")
    r.append("| Level | Count |")
    r.append("|---|---|")
    for level, count in sorted(difficulty_dist.items(), key=lambda x: -x[1]):
        r.append("| %s | %d |" % (level, count))
    r.append("")
    r.append("**Beginner case studies: %d**" % len(beginner_ids))
    r.append("")
    if beginner_ids:
        r.append("Beginner IDs: %s" % ", ".join(str(x) for x in sorted(beginner_ids)))
        r.append("")
    
    # Section 7: Status Distribution
    r.append("---")
    r.append("## 7. Publication Status")
    r.append("")
    r.append("| Status | Count |")
    r.append("|---|---|")
    for status, count in sorted(status_dist.items(), key=lambda x: -x[1]):
        r.append("| %s | %d |" % (status, count))
    r.append("")
    
    # Section 8: Category Distribution
    r.append("---")
    r.append("## 8. Category Distribution")
    r.append("")
    r.append("| Category | Count |")
    r.append("|---|---|")
    for cat, count in sorted(category_dist.items(), key=lambda x: -x[1]):
        r.append("| %s | %d |" % (cat, count))
    r.append("")
    
    # Section 9: Worst offenders (4+ issues)
    r.append("---")
    r.append("## 9. Critical Cases (4 or More Issues Each)")
    r.append("")
    r.append("These case studies need the most urgent attention — they fail on multiple quality "
             "dimensions simultaneously.")
    r.append("")
    for ci in sorted(severe_cases, key=lambda x: -x["issue_count"]):
        r.append("### Case #%d: %s" % (ci["id"], ci["title"]))
        r.append("")
        r.append("- **Difficulty:** %s" % ci.get("difficulty", "?"))
        for iss in ci["issues"]:
            r.append("- ❌ %s" % iss)
        r.append("")
    
    # Section 10: Gap Overlap Matrix
    r.append("---")
    r.append("## 10. Gap Overlap Matrix")
    r.append("")
    r.append("How many cases have multiple simultaneous gaps:")
    r.append("")
    
    overlap_counts = Counter()
    for ci in case_issues:
        overlap_counts[ci["issue_count"]] += 1
    
    r.append("| Number of Issues | Case Count |")
    r.append("|---|---|")
    for n in sorted(overlap_counts.keys()):
        bar = "█" * overlap_counts[n]
        r.append("| %d | %d %s |" % (n, overlap_counts[n], bar))
    r.append("")
    
    # Write the report
    report_text = "\n".join(r)
    report_path = os.path.join(OUT_DIR, "CASE_STUDY_QUALITY_REPORT.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_text)
    
    print("Report written to %s" % report_path)
    print("")
    print("=== Quick Stats ===")
    print("Total: %d" % total)
    print("Cases with issues: %d (%.1f%%)" % (len(case_issues), len(case_issues)/total*100))
    print("Critical (4+ issues): %d" % len(severe_cases))
    print("No dataset (NA/empty): %d" % (empty_data_sources + na_data_sources))
    print("No tutorial link: %d" % no_tutorial_link)
    print("No/NA solver guidance: %d" % (missing_solver_guidance + na_solver_guidance))
    print("Empty full_content: %d" % missing_full_content)
    print("Vague source: %d" % vague_source)
    print("No prereqs: %d" % missing_prereqs)
    print("Difficulty dist: %s" % dict(difficulty_dist))
    print("Status dist: %s" % dict(status_dist))

if __name__ == "__main__":
    cases = load_all()
    analyze(cases)
