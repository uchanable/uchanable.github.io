#!/usr/bin/env python3
"""Generate HTML table files from CSV data for the project page.

Reads CSV data from the github-repo and generates standalone HTML table
fragments that can be loaded via fetch() in the project page.

Usage:
    python generate_tables.py

Output:
    source/table/html/*.html files (table1.html through table19.html)
"""

import csv
import os
import re
import statistics
from pathlib import Path

REPO = Path(__file__).parent.parent.parent.parent / "github-repo"
FORCE_DIR = REPO / "data" / "force"
EDA_DIR = REPO / "data" / "eda"

# Analysis data paths (case-sensitive macOS paths)
ANALYSIS_BASE = Path(__file__).parent.parent.parent.parent.parent / "20_Experiment_RA-L" / "30_analysis" / "analysis_data"

OUT_DIR = Path(__file__).parent / "html"
OUT_DIR.mkdir(exist_ok=True)


def read_csv(path):
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def fmt(val, decimals=3):
    """Format a numeric string to given decimal places."""
    try:
        return f"{float(val):.{decimals}f}"
    except (ValueError, TypeError):
        return val


def fmt_p(val):
    """Format p-value."""
    try:
        p = float(val)
        if p < 0.001:
            return "&lt;.001"
        return f"{p:.3f}"
    except (ValueError, TypeError):
        return val


def sig_star(p_val):
    """Return significance star(s)."""
    try:
        p = float(p_val)
        if p < 0.001:
            return "***"
        elif p < 0.01:
            return "**"
        elif p < 0.05:
            return "*"
        return ""
    except (ValueError, TypeError):
        return ""


# ===========================================================================
# Table 1: Force combined results (ral_summary + paired_tests) — EXISTING
# ===========================================================================
def generate_table1():
    """Table 1: Force control performance (combined results)."""
    summary = read_csv(FORCE_DIR / "ral_summary.csv")
    paired = read_csv(FORCE_DIR / "advanced" / "paired_tests.csv")

    # Build paired test lookup: (direction, metric) -> row
    test_map = {}
    for r in paired:
        key = (r.get("direction", ""), r.get("dv", r.get("metric", "")))
        test_map[key] = r

    metrics = ["mean", "rmse", "mae", "cv", "delta_f", "avg_delta"]
    # Map from our metric key to the paired_tests CSV 'dv' column
    metric_to_dv = {
        "mean": "mean",
        "rmse": "rmse",
        "mae": "mae",
        "cv": "cv",
        "delta_f": "delta_f",
        "avg_delta": "avg_delta_mean",
    }
    metric_labels = {
        "mean": ("Mean (N)", 3),
        "rmse": ("RMSE (N)", 3),
        "mae": ("MAE (N)", 3),
        "cv": ("CV (%)", 3),
        "delta_f": ("&Delta;F (N)", 3),
        "avg_delta": ("MASD (N)", 3),
    }

    # summary has: direction, control, condition, mean_M, mean_SD, rmse_M, rmse_SD, etc.
    def get_summary(direction, control):
        for r in summary:
            if r["direction"] == direction and r["control"] == control:
                return r
        return {}

    html = ['<table class="gen-tbl">']
    html.append("<thead><tr>")
    html.append('<th>Metrics</th><th>FF+PID</th><th>PID</th><th>Statistic</th><th><em>p</em></th><th>Cohen\'s <em>d</em></th>')
    html.append("</tr></thead><tbody>")

    for dir_label, direction in [("Parallel Direction", "parallel"), ("Orthogonal Direction", "orthogonal")]:
        html.append(f'<tr class="section-row"><td colspan="6"><strong><em>{dir_label}</em></strong></td></tr>')

        ff = get_summary(direction, "ff_pid")
        pid = get_summary(direction, "pid_only")

        for m in metrics:
            label, dec = metric_labels[m]
            ff_m = fmt(ff.get(f"{m}_M", ""), dec)
            ff_s = fmt(ff.get(f"{m}_SD", ""), dec)
            pid_m = fmt(pid.get(f"{m}_M", ""), dec)
            pid_s = fmt(pid.get(f"{m}_SD", ""), dec)

            dv_key = metric_to_dv.get(m, m)
            test = test_map.get((direction, dv_key), {})
            test_type = test.get("test", "")
            stat_val = test.get("statistic", "")
            p_val = fmt_p(test.get("p_value", ""))
            d_val = fmt(test.get("cohens_d", test.get("effect_size", "")), 3)

            if test_type == "paired_t":
                stat_str = f"<em>t</em> = {fmt(stat_val, 3)}"
            elif test_type == "wilcoxon":
                stat_str = f"<em>W</em> = {fmt(stat_val, 1)}"
            else:
                stat_str = stat_val

            html.append(f"<tr><td>{label}</td>")
            html.append(f"<td>{ff_m} &plusmn; {ff_s}</td>")
            html.append(f"<td>{pid_m} &plusmn; {pid_s}</td>")
            html.append(f"<td>{stat_str}</td>")
            html.append(f"<td>{p_val}</td>")
            html.append(f"<td>{d_val}</td></tr>")

    html.append("</tbody></table>")
    html.append('<p class="tbl-fn">')
    html.append("Values are M &plusmn; SD. ")
    html.append("<em>t</em> = paired <em>t</em>-test; <em>W</em> = Wilcoxon signed-rank (Shapiro&ndash;Wilk, &alpha; = .05).")
    html.append("</p>")

    (OUT_DIR / "table1.html").write_text("\n".join(html), encoding="utf-8")
    print("Generated: table1.html")


# ===========================================================================
# Table 2: Sampling characteristics (hardcoded)
# ===========================================================================
def generate_table2():
    """Table 2: Sampling characteristics comparison."""
    html = ['<table class="gen-tbl">']
    html.append("<thead><tr>")
    html.append("<th>Characteristic</th><th>Parallel</th><th>Orthogonal</th>")
    html.append("</tr></thead><tbody>")

    rows = [
        ("Stroking distance", "~12 cm", "~2 cm"),
        ("Mean sample interval", "132.5 ms", "258.8 ms"),
        ("Mean points per cycle", "74.2", "10.8"),
        ("Force range", "0.214 N", "0.127 N"),
    ]
    for label, par, orth in rows:
        html.append(f"<tr><td>{label}</td><td>{par}</td><td>{orth}</td></tr>")

    html.append("</tbody></table>")
    html.append('<p class="tbl-fn">FF+PID condition, measured values.</p>')

    (OUT_DIR / "table2.html").write_text("\n".join(html), encoding="utf-8")
    print("Generated: table2.html")


# ===========================================================================
# Table 3: MASD stats by direction (from paired_tests, avg_delta_mean rows)
# ===========================================================================
def generate_table3():
    """Table 3: MASD statistical test results by direction."""
    paired = read_csv(FORCE_DIR / "advanced" / "paired_tests.csv")

    html = ['<table class="gen-tbl">']
    html.append("<thead><tr>")
    html.append("<th>Direction</th><th>Test</th><th>Statistic</th><th><em>p</em>-value</th><th>Cohen's <em>d</em></th>")
    html.append("</tr></thead><tbody>")

    for direction, dir_label in [("parallel", "Parallel"), ("orthogonal", "Orthogonal")]:
        for r in paired:
            if r["direction"] == direction and r["dv"] == "avg_delta_mean":
                test_type = r["test"]
                stat = fmt(r["statistic"], 3)
                p = fmt_p(r["p_value"])
                d = fmt(r["cohens_d"], 3)
                test_label = "paired <em>t</em>" if test_type == "paired_t" else "<em>W</em>"
                html.append(f"<tr><td>{dir_label}</td><td>{test_label}</td><td>{stat}</td><td>{p}</td><td>{d}</td></tr>")

    html.append("</tbody></table>")
    html.append('<p class="tbl-fn">')
    html.append("Both directions show significantly smoother force delivery under FF+PID. ")
    html.append("The larger effect in orthogonal (<em>d</em> = &minus;1.433) indicates that FF compensation is particularly effective at reducing rapid force fluctuations in the short-stroke condition.")
    html.append("</p>")

    (OUT_DIR / "table3.html").write_text("\n".join(html), encoding="utf-8")
    print("Generated: table3.html")


# ===========================================================================
# Table 4: Hysteresis (delta_f) from paired_tests + RMSE inflation info
# ===========================================================================
def generate_table4():
    """Table 4: Forward/Backward Hysteresis Analysis."""
    paired = read_csv(FORCE_DIR / "advanced" / "paired_tests.csv")
    summary = read_csv(FORCE_DIR / "ral_summary.csv")

    def get_summary_val(direction, control, metric):
        for r in summary:
            if r["direction"] == direction and r["control"] == control:
                return r.get(f"{metric}_M", ""), r.get(f"{metric}_SD", "")
        return "", ""

    html = ['<table class="gen-tbl">']
    html.append("<thead><tr>")
    html.append("<th>Direction</th><th>FF+PID</th><th>PID</th><th>Test</th><th><em>p</em></th><th><em>d</em></th>")
    html.append("</tr></thead>")
    html.append("<tbody>")

    for direction, dir_label in [("parallel", "Parallel"), ("orthogonal", "Orthogonal")]:
        for r in paired:
            if r["direction"] == direction and r["dv"] == "delta_f":
                ff_m, ff_s = get_summary_val(direction, "ff_pid", "delta_f")
                pid_m, pid_s = get_summary_val(direction, "pid_only", "delta_f")
                test_type = r["test"]
                p = fmt_p(r["p_value"])
                d = fmt(r["cohens_d"], 3)
                if test_type == "wilcoxon":
                    test_str = "<em>W</em>"
                else:
                    test_str = "<em>t</em>"
                html.append(f"<tr><td>{dir_label}</td>")
                html.append(f"<td>{fmt(ff_m, 3)} &plusmn; {fmt(ff_s, 3)}</td>")
                html.append(f"<td>{fmt(pid_m, 3)} &plusmn; {fmt(pid_s, 3)}</td>")
                html.append(f"<td>{test_str}</td><td>{p}</td><td>{d}</td></tr>")

    html.append("</tbody></table>")
    html.append('<p class="tbl-fn">')
    html.append("&Delta;F = |<span style=\"text-decoration:overline\">F</span><sub>forward</sub> &minus; <span style=\"text-decoration:overline\">F</span><sub>backward</sub>| (units: N). M &plusmn; SD. ")
    html.append("<em>t</em> = paired <em>t</em>-test; <em>W</em> = Wilcoxon signed-rank; <em>d</em> = Cohen's <em>d</em>.")
    html.append("</p>")

    (OUT_DIR / "table4.html").write_text("\n".join(html), encoding="utf-8")
    print("Generated: table4.html")


# ===========================================================================
# Table 5: Variance Decomposition — EXISTING
# ===========================================================================
def generate_table5():
    """Table 5: Variance Decomposition."""
    rows = read_csv(FORCE_DIR / "advanced" / "variance_decomposition.csv")

    html = ['<table class="gen-tbl">']
    html.append("<thead><tr>")
    html.append("<th>Condition</th><th>Between-P SD</th><th>Within-P SD</th><th>Ratio</th>")
    html.append("</tr></thead><tbody>")

    for r in rows:
        cond = r.get("condition", f"{r.get('direction','')} {r.get('control','')}")
        b = fmt(r.get("between_sd", ""), 3)
        w = fmt(r.get("within_sd", ""), 3)
        ratio = fmt(r.get("ratio", ""), 3)
        html.append(f"<tr><td>{cond}</td><td>{b}</td><td>{w}</td><td>{ratio}</td></tr>")

    html.append("</tbody></table>")
    html.append('<p class="tbl-fn">Between-P SD = SD of 20 participants\' mean RMSE. Within-P SD = mean of each participant\'s 10-cycle RMSE SD. Ratio = Between/Within.</p>')

    (OUT_DIR / "table5.html").write_text("\n".join(html), encoding="utf-8")
    print("Generated: table5.html")


# ===========================================================================
# Table 6: ICC results — EXISTING
# ===========================================================================
def generate_table6():
    """Table 6: ICC results."""
    rows = read_csv(FORCE_DIR / "advanced" / "icc_results.csv")

    html = ['<table class="gen-tbl">']
    html.append("<thead><tr>")
    html.append("<th>Condition</th><th>ICC</th><th>95% CI</th><th><em>p</em></th><th>Reliability</th>")
    html.append("</tr></thead><tbody>")

    for r in rows:
        cond = r.get("condition", f"{r.get('direction','')} {r.get('control','')}")
        icc = fmt(r.get("icc_value", r.get("icc", "")), 3)
        ci_lo = fmt(r.get("ci95_lower", r.get("ci_lower", "")), 2)
        ci_hi = fmt(r.get("ci95_upper", r.get("ci_upper", "")), 2)
        p = fmt_p(r.get("p_value", ""))

        try:
            icc_f = float(r.get("icc_value", r.get("icc", "0")))
            if icc_f > 0.9:
                rel = "Excellent"
            elif icc_f > 0.75:
                rel = "Good"
            elif icc_f > 0.5:
                rel = "Moderate"
            else:
                rel = "Poor"
        except ValueError:
            rel = ""

        html.append(f"<tr><td>{cond}</td><td>{icc}</td><td>[{ci_lo}, {ci_hi}]</td><td>{p}</td><td>{rel}</td></tr>")

    html.append("</tbody></table>")

    (OUT_DIR / "table6.html").write_text("\n".join(html), encoding="utf-8")
    print("Generated: table6.html")


# ===========================================================================
# Table 7: Cycle Trend Distribution
# ===========================================================================
def generate_table7():
    """Table 7: Cycle Trend Distribution (overall + by condition)."""
    rows = read_csv(FORCE_DIR / "advanced" / "cycle_trend.csv")

    # Overall counts
    improving = sum(1 for r in rows if r["trend"] == "improving")
    stable = sum(1 for r in rows if r["trend"] == "stable")
    worsening = sum(1 for r in rows if r["trend"] == "worsening")
    total = len(rows)

    html = ['<table class="gen-tbl">']

    # Part (a): Overall Summary
    html.append("<thead><tr>")
    html.append('<th colspan="3"><strong>(a) Overall Summary (<em>N</em> = 80)</strong></th>')
    html.append("</tr><tr>")
    html.append("<th>Trend</th><th>Count</th><th>Proportion</th>")
    html.append("</tr></thead><tbody>")
    html.append(f'<tr><td>Improving (&rho; &lt; &minus;0.3)</td><td>{improving}</td><td>{improving*100//total}%</td></tr>')
    html.append(f'<tr><td>Stable (&minus;0.3 &le; &rho; &le; 0.3)</td><td>{stable}</td><td>{stable*100//total}%</td></tr>')
    html.append(f'<tr><td>Worsening (&rho; &gt; 0.3)</td><td>{worsening}</td><td>{worsening*100//total}%</td></tr>')
    html.append("</tbody></table>")

    # Part (b): By condition
    html.append('<table class="gen-tbl" style="margin-top:12px">')
    html.append("<thead><tr>")
    html.append('<th colspan="5"><strong>(b) Breakdown by Condition</strong></th>')
    html.append("</tr><tr>")
    html.append("<th>Condition</th><th>Impr.</th><th>Wors.</th><th>Stable</th><th>Mean &rho;</th>")
    html.append("</tr></thead><tbody>")

    conditions = [
        ("Par. FF+PID", "parallel", "ff_pid"),
        ("Par. PID", "parallel", "pid_only"),
        ("Orth. FF+PID", "orthogonal", "ff_pid"),
        ("Orth. PID", "orthogonal", "pid_only"),
    ]

    for label, direction, control in conditions:
        sub = [r for r in rows if r["direction"] == direction and r["control"] == control]
        imp = sum(1 for r in sub if r["trend"] == "improving")
        wor = sum(1 for r in sub if r["trend"] == "worsening")
        stb = sum(1 for r in sub if r["trend"] == "stable")
        mean_rho = statistics.mean([float(r["rho"]) for r in sub])
        sign = "+" if mean_rho >= 0 else "&minus;"
        html.append(f"<tr><td>{label}</td><td>{imp}</td><td>{'<strong>' + str(wor) + '</strong>' if wor >= 10 else str(wor)}</td><td>{stb}</td><td>{sign}{abs(mean_rho):.3f}</td></tr>")

    html.append(f'<tr style="border-top:2px solid var(--text)"><td><strong>Total</strong></td><td><strong>{improving}</strong></td><td><strong>{worsening}</strong></td><td><strong>{stable}</strong></td><td>&mdash;</td></tr>')
    html.append("</tbody></table>")

    (OUT_DIR / "table7.html").write_text("\n".join(html), encoding="utf-8")
    print("Generated: table7.html")


# ===========================================================================
# Table 8: Spearman rho frequency distribution
# ===========================================================================
def generate_table8():
    """Table 8: Spearman rho frequency distribution."""
    rows = read_csv(FORCE_DIR / "advanced" / "cycle_trend.csv")
    rho_vals = [float(r["rho"]) for r in rows]

    # Define bins from -1.0 to 1.0 in 0.1 steps
    bins = []
    for i in range(20):
        lo = -1.0 + i * 0.1
        hi = lo + 0.1
        bins.append((lo, hi))

    html = ['<table class="gen-tbl">']
    html.append("<thead><tr>")
    html.append("<th>Bin</th><th>Count</th><th>Category</th>")
    html.append("</tr></thead><tbody>")

    improving_total = 0
    stable_total = 0
    worsening_total = 0

    for lo, hi in bins:
        if abs(hi - 1.0) < 1e-9:
            # Last bin: include 1.0
            count = sum(1 for v in rho_vals if lo <= v <= hi)
        else:
            count = sum(1 for v in rho_vals if lo <= v < hi)

        if hi <= -0.3 + 1e-9:
            cat = "Improving"
            improving_total += count
        elif lo >= 0.3 - 1e-9:
            cat = "Worsening"
            worsening_total += count
        else:
            cat = "Stable"
            stable_total += count

        # Format bin labels
        if abs(lo - (-1.0)) < 1e-9:
            lo_str = "[&minus;1.0"
        elif lo < 0:
            lo_str = f"[&minus;{abs(lo):.1f}"
        elif abs(lo) < 1e-9:
            lo_str = "[0.0"
        else:
            lo_str = f"[{lo:.1f}"

        if abs(hi - 1.0) < 1e-9:
            hi_str = "1.0]"
        elif hi < 0:
            hi_str = f"&minus;{abs(hi):.1f})"
        elif abs(hi) < 1e-9:
            hi_str = "0.0)"
        else:
            hi_str = f"{hi:.1f})"

        html.append(f"<tr><td>{lo_str}, {hi_str}</td><td>{count}</td><td>{cat}</td></tr>")

    html.append(f'<tr style="border-top:2px solid var(--text)"><td><strong>Total</strong></td><td><strong>{len(rho_vals)}</strong></td><td>Impr. {improving_total} / Stable {stable_total} / Wors. {worsening_total}</td></tr>')
    html.append("</tbody></table>")

    (OUT_DIR / "table8.html").write_text("\n".join(html), encoding="utf-8")
    print("Generated: table8.html")


# ===========================================================================
# Table 9: X-Axis Drift (from master CSVs)
# ===========================================================================
def generate_table9():
    """Table 9: X-Axis Drift Analysis for the Parallel FF+PID Condition."""
    master_dir = FORCE_DIR / "master"
    cycle_trend = read_csv(FORCE_DIR / "advanced" / "cycle_trend.csv")

    # Build rho lookup for parallel ff_pid
    rho_map = {}
    for r in cycle_trend:
        if r["direction"] == "parallel" and r["control"] == "ff_pid":
            rho_map[r["participant"]] = (float(r["rho"]), r["trend"])

    # Compute X drift per participant for parallel ff_pid
    participants = []
    cycle_x_sums = {c: [] for c in range(1, 11)}

    for pid in [f"S{i:02d}" for i in range(1, 21)]:
        master_path = master_dir / f"{pid}_master.csv"
        if not master_path.exists():
            continue
        master = read_csv(master_path)

        # Filter: parallel, ff_pid, steady state
        par_ff = [r for r in master
                  if r["direction"] == "parallel"
                  and r["control"] == "ff_pid"
                  and r["label_steady"] == "1"]

        if not par_ff:
            continue

        # Get mean X per cycle
        cycle_means = {}
        for r in par_ff:
            c = int(r["cycle"])
            x = float(r["pos_x_cm"])
            cycle_means.setdefault(c, []).append(x)

        cycle_avg = {c: statistics.mean(vals) for c, vals in cycle_means.items()}
        for c in range(1, 11):
            if c in cycle_avg:
                cycle_x_sums[c].append(cycle_avg[c])

        # X drift = mean X in last cycle - mean X in first cycle
        if 1 in cycle_avg and 10 in cycle_avg:
            x_drift = cycle_avg[10] - cycle_avg[1]
        else:
            x_drift = 0

        rho, trend = rho_map.get(pid, (0, "stable"))
        trend_short = {"improving": "impr.", "worsening": "wors.", "stable": "stable"}.get(trend, trend)
        participants.append((pid, x_drift, rho, trend_short))

    # Part (a): Per-Participant Data — 3 columns across
    html = ['<table class="gen-tbl">']
    html.append("<thead><tr>")
    html.append('<th colspan="12"><strong>(a) Per-Participant Data</strong></th>')
    html.append("</tr><tr>")
    for _ in range(3):
        html.append("<th>ID</th><th>X drift (cm)</th><th>RMSE &rho;</th><th>Trend</th>")
    html.append("</tr></thead><tbody>")

    # Arrange in 3 columns (7+7+6)
    col1 = participants[0:7]
    col2 = participants[7:14]
    col3 = participants[14:20]

    for i in range(7):
        html.append("<tr>")
        for col in [col1, col2, col3]:
            if i < len(col):
                pid, xd, rho, trend = col[i]
                sign = "+" if rho >= 0 else "&minus;"
                html.append(f"<td>{pid}</td><td>{xd:.2f}</td><td>{sign}{abs(rho):.2f}</td><td>{trend}</td>")
            else:
                html.append("<td></td><td></td><td></td><td></td>")
        html.append("</tr>")

    html.append("</tbody></table>")

    # Part (b): Trend Group Comparison
    html.append('<table class="gen-tbl" style="margin-top:12px">')
    html.append("<thead><tr>")
    html.append('<th colspan="3"><strong>(b) Trend Group Comparison</strong></th>')
    html.append("</tr><tr>")
    html.append("<th>Trend Group</th><th>Mean X drift (cm)</th><th><em>n</em></th>")
    html.append("</tr></thead><tbody>")

    for trend_name in ["impr.", "wors.", "stable"]:
        group = [p for p in participants if p[3] == trend_name]
        if group:
            mean_drift = statistics.mean([p[1] for p in group])
            html.append(f"<tr><td>{'Improving' if trend_name == 'impr.' else 'Worsening' if trend_name == 'wors.' else 'Stable'}</td><td>{mean_drift:.3f}</td><td>{len(group)}</td></tr>")

    html.append("</tbody></table>")

    # Part (c): Cycle-by-Cycle Grand Average X Position
    html.append('<table class="gen-tbl" style="margin-top:12px">')
    html.append("<thead><tr>")
    html.append('<th colspan="6"><strong>(c) Cycle-by-Cycle Grand Average X Position (<em>N</em>=20)</strong></th>')
    html.append("</tr><tr>")
    for c in range(1, 6):
        html.append(f"<th>Cycle {c}</th>")
    html.append("<th></th>")
    html.append("</tr></thead><tbody><tr>")
    for c in range(1, 6):
        if cycle_x_sums[c]:
            mean_x = statistics.mean(cycle_x_sums[c])
            html.append(f"<td>{mean_x:.2f}</td>")
        else:
            html.append("<td>&mdash;</td>")
    html.append("<td></td></tr></tbody></table>")

    html.append('<table class="gen-tbl" style="margin-top:4px">')
    html.append("<thead><tr>")
    for c in range(6, 11):
        html.append(f"<th>Cycle {c}</th>")
    html.append("<th></th>")
    html.append("</tr></thead><tbody><tr>")
    for c in range(6, 11):
        if cycle_x_sums[c]:
            mean_x = statistics.mean(cycle_x_sums[c])
            html.append(f"<td>{mean_x:.2f}</td>")
        else:
            html.append("<td>&mdash;</td>")
    html.append("<td></td></tr></tbody></table>")

    html.append('<p class="tbl-fn">')
    html.append("Kruskal&ndash;Wallis test (trend group vs. X drift): <em>H</em> = 3.34, <em>p</em> = 0.188 (n.s.). ")
    html.append("X drift vs. RMSE &rho; correlation: Spearman &rho; = &minus;0.37, <em>p</em> = 0.113 (n.s.). ")
    html.append("X drift was universal across all 20 participants (range: &minus;0.96 to &minus;1.53 cm), progressing linearly at ~0.135 cm/cycle. ")
    html.append("Worsening is statistically significant (Wilcoxon <em>p</em> = 0.0002) but practically negligible (within-participant SD = 0.002 N, 0.5% of target force).")
    html.append("</p>")

    (OUT_DIR / "table9.html").write_text("\n".join(html), encoding="utf-8")
    print("Generated: table9.html")


# ===========================================================================
# Table 10: Forward/Backward X displacement per half-cycle
# ===========================================================================
def generate_table10():
    """Table 10: Forward/Backward X-Axis Displacement per Half-Cycle."""
    # Hardcode from supplementary Table S10 — computed from master CSVs
    data = [
        ("Par. FF+PID", "+0.063", "&minus;0.193", "3.07", "&minus;0.130"),
        ("Par. PID", "+0.051", "&minus;0.189", "3.70", "&minus;0.138"),
        ("Orth. FF+PID", "+0.019", "&minus;0.041", "2.16", "&minus;0.022"),
        ("Orth. PID", "+0.015", "&minus;0.041", "2.73", "&minus;0.026"),
    ]

    html = ['<table class="gen-tbl">']
    html.append("<thead><tr>")
    html.append("<th>Condition</th><th>FWD mean (cm)</th><th>BWD mean (cm)</th><th>|BWD|/|FWD| ratio</th><th>Net/cycle (cm)</th>")
    html.append("</tr></thead><tbody>")

    for cond, fwd, bwd, ratio, net in data:
        html.append(f"<tr><td>{cond}</td><td>{fwd}</td><td>{bwd}</td><td>{ratio}</td><td>{net}</td></tr>")

    html.append("</tbody></table>")
    html.append('<p class="tbl-fn">')
    html.append("100% of backward half-cycles exhibited negative &Delta;X; forward half-cycles were positive in nearly all cases. ")
    html.append("Asymmetric |BWD|/|FWD| ratio &asymp; 3 produces net negative drift per cycle.")
    html.append("</p>")

    (OUT_DIR / "table10.html").write_text("\n".join(html), encoding="utf-8")
    print("Generated: table10.html")


# ===========================================================================
# Table 11: BWD[0] angles (hardcoded from supplementary)
# ===========================================================================
def generate_table11():
    """Table 11: Per-participant BWD[0] turnaround angles."""
    data = [
        ("S08", "29.50", "Minimum"),
        ("S11", "33.71", ""),
        ("S01", "36.09", ""),
        ("S09", "36.10", ""),
        ("S04", "36.80", ""),
        ("S05", "44.14", ""),
        ("S13", "45.24", ""),
        ("S02", "45.62", "T12 recalibration"),
        ("S03", "51.39", ""),
        ("S10", "51.26", ""),
        ("S15", "60.64", ""),
        ("S06", "63.30", ""),
        ("S17", "68.73", ""),
        ("S12", "69.75", "Outlier"),
        ("S14", "70.89", "Outlier (manual direction correction)"),
        ("S07", "72.64", ""),
        ("S20", "76.08", ""),
        ("S19", "82.69", ""),
        ("S16", "86.80", "Outlier"),
        ("S18", "110.00", "Outlier (MAX_MOTOR_ANGLE reached)"),
    ]

    html = ['<table class="gen-tbl">']
    html.append("<thead><tr>")
    html.append("<th>Participant</th><th>BWD[0] (&deg;)</th><th>Notes</th>")
    html.append("</tr></thead><tbody>")

    for pid, angle, notes in data:
        html.append(f"<tr><td>{pid}</td><td>{angle}</td><td>{notes}</td></tr>")

    html.append("</tbody></table>")
    html.append('<p class="tbl-fn">')
    html.append("Mean = 58.6&deg;, Median = 56.0&deg;, SD = 20.7&deg;, Range = 29.5&deg;&ndash;110.0&deg;.")
    html.append("</p>")

    (OUT_DIR / "table11.html").write_text("\n".join(html), encoding="utf-8")
    print("Generated: table11.html")


# ===========================================================================
# Table 12: BWD[0] correlation (hardcoded from supplementary)
# ===========================================================================
def generate_table12():
    """Table 12: Correlation between BWD[0] angle and parallel RMSE."""
    html = ['<table class="gen-tbl">']
    html.append("<thead><tr>")
    html.append("<th>Condition</th><th>Pearson <em>r</em></th><th><em>p</em></th><th>Spearman <em>r</em></th><th><em>p</em></th>")
    html.append("</tr></thead><tbody>")

    html.append('<tr><td>FF+PID</td><td><strong>0.606</strong></td><td><strong>0.005</strong></td><td><strong>0.662</strong></td><td><strong>0.002</strong></td></tr>')
    html.append('<tr><td>PID-only</td><td>0.438</td><td>0.053</td><td>0.492</td><td>0.028</td></tr>')

    html.append("</tbody></table>")

    (OUT_DIR / "table12.html").write_text("\n".join(html), encoding="utf-8")
    print("Generated: table12.html")


# ===========================================================================
# Table 13: BWD[0] impact assessment (hardcoded from supplementary)
# ===========================================================================
def generate_table13():
    """Table 13: RMSE comparison: BWD[0] outliers vs remaining participants."""
    html = ['<table class="gen-tbl">']
    html.append("<thead><tr>")
    html.append("<th>Metric</th><th>Outliers (<em>n</em>=4)</th><th>Others (<em>n</em>=16)</th>")
    html.append("</tr></thead><tbody>")

    html.append("<tr><td>FF+PID RMSE (N)</td><td>0.073</td><td>0.064</td></tr>")
    html.append("<tr><td>PID RMSE (N)</td><td>0.089</td><td>0.079</td></tr>")

    html.append("</tbody></table>")

    (OUT_DIR / "table13.html").write_text("\n".join(html), encoding="utf-8")
    print("Generated: table13.html")


# ===========================================================================
# Table 14: Questionnaire (from questionnaire_descriptive + wilcoxon)
# ===========================================================================
def generate_table14():
    """Table 14: Perceptual Questionnaire Results."""
    # Try both possible paths for analysis data
    q_desc_path = None
    q_wilc_path = None

    for base in [ANALYSIS_BASE,
                 Path(__file__).resolve().parent.parent.parent.parent.parent / "20_Experiment_RA-L" / "30_analysis" / "analysis_data"]:
        p1 = base / "questionnaire" / "questionnaire_descriptive.csv"
        p2 = base / "questionnaire" / "questionnaire_wilcoxon.csv"
        if p1.exists():
            q_desc_path = p1
            q_wilc_path = p2
            break

    if q_desc_path is None:
        # Fallback: try case-insensitive search
        import glob
        candidates = glob.glob(str(Path(__file__).resolve().parents[4]) + "/**/questionnaire_descriptive.csv", recursive=True)
        if candidates:
            q_desc_path = Path(candidates[0])
            q_wilc_path = q_desc_path.parent / "questionnaire_wilcoxon.csv"

    desc = read_csv(q_desc_path)
    wilc = read_csv(q_wilc_path)

    # Build lookup for descriptive: (direction, control, scale) -> row
    desc_map = {}
    for r in desc:
        key = (r["direction"], r["control"], r["scale"])
        desc_map[key] = r

    # Build lookup for wilcoxon: (direction, scale) -> row
    wilc_map = {}
    for r in wilc:
        key = (r["direction"], r["scale"])
        wilc_map[key] = r

    html = ['<table class="gen-tbl">']
    html.append("<thead><tr>")
    html.append("<th rowspan='2'>Direction</th><th rowspan='2'>Scale</th>")
    html.append("<th colspan='2'>FF+PID</th><th colspan='2'>PID</th>")
    html.append("<th colspan='3'>Wilcoxon Test</th>")
    html.append("</tr><tr>")
    html.append("<th>Mdn [IQR]</th><th>M &plusmn; SD</th>")
    html.append("<th>Mdn [IQR]</th><th>M &plusmn; SD</th>")
    html.append("<th><em>W</em></th><th><em>p</em></th><th><em>r</em></th>")
    html.append("</tr></thead><tbody>")

    for direction, dir_label in [("parallel", "Parallel"), ("orthogonal", "Orthogonal")]:
        first = True
        for scale in ["comfort", "naturalness", "consistency"]:
            ff = desc_map.get((direction, "ff_pid", scale), {})
            pid = desc_map.get((direction, "pid_only", scale), {})
            w = wilc_map.get((direction, scale), {})

            ff_mdn = ff.get("median", "")
            ff_iqr = w.get("ff_pid_iqr", f"{ff.get('q1', '')}&ndash;{ff.get('q3', '')}")
            ff_mean = fmt(ff.get("mean", ""), 2)
            ff_sd = fmt(ff.get("sd", ""), 2)

            pid_mdn = pid.get("median", "")
            pid_iqr = w.get("pid_iqr", f"{pid.get('q1', '')}&ndash;{pid.get('q3', '')}")
            pid_mean = fmt(pid.get("mean", ""), 2)
            pid_sd = fmt(pid.get("sd", ""), 2)

            w_stat = w.get("W_statistic", "")
            p_val = fmt(w.get("p_value", ""), 3)
            r_eff = fmt(w.get("r_effect", ""), 3)

            # Add dagger for marginal significance
            dagger = ""
            try:
                if 0.05 < float(w.get("p_value", "1")) < 0.10:
                    dagger = '<sup>&dagger;</sup>'
            except ValueError:
                pass

            scale_label = scale.capitalize()

            if first:
                html.append(f'<tr class="section-row"><td colspan="9"><strong><em>{dir_label}</em></strong></td></tr>')
                first = False

            html.append(f"<tr><td></td><td>{scale_label}</td>")
            html.append(f"<td>{ff_mdn} [{ff_iqr}]</td><td>{ff_mean} &plusmn; {ff_sd}</td>")
            html.append(f"<td>{pid_mdn} [{pid_iqr}]</td><td>{pid_mean} &plusmn; {pid_sd}</td>")
            html.append(f"<td>{fmt(w_stat, 1)}</td><td>{p_val}</td><td>{r_eff}{dagger}</td></tr>")

    html.append("</tbody></table>")
    html.append('<p class="tbl-fn">')
    html.append("Mdn = Median; IQR = Interquartile Range [Q1&ndash;Q3]; <em>r</em> = <em>Z</em>/&radic;<em>N</em> (effect size). ")
    html.append("<sup>&dagger;</sup>Marginal trend (<em>p</em> = 0.081, medium effect <em>r</em> = 0.39). ")
    html.append("The absence of differences in subjective evaluation despite significant objective force improvements suggests that the sub-hundred millinewton-level control differences are below the human tactile detection threshold.")
    html.append("</p>")

    (OUT_DIR / "table14.html").write_text("\n".join(html), encoding="utf-8")
    print("Generated: table14.html")


# ===========================================================================
# Table 15: EDA Parallel (from eda_paired_tests + eda_features)
# ===========================================================================
def generate_table15():
    """Table 15: EDA Results, Parallel Direction."""
    eda_tests_path = None
    for base in [ANALYSIS_BASE,
                 Path(__file__).resolve().parent.parent.parent.parent.parent / "20_Experiment_RA-L" / "30_analysis" / "analysis_data"]:
        p = base / "eda" / "eda_paired_tests.csv"
        if p.exists():
            eda_tests_path = p
            break

    if eda_tests_path is None:
        import glob
        candidates = glob.glob(str(Path(__file__).resolve().parents[4]) + "/**/eda_paired_tests.csv", recursive=True)
        if candidates:
            eda_tests_path = Path(candidates[0])

    eda_tests = read_csv(eda_tests_path)

    # Also compute SCR AUC from eda_features (not in paired tests, need manual computation)
    eda_features = read_csv(EDA_DIR / "eda_features.csv")

    metric_labels = {
        "scl_mean": "SCL Mean (&mu;S)",
        "scl_sd": "SCL SD (&mu;S)",
        "scl_range": "SCL Range (&mu;S)",
        "scl_auc": "SCL AUC (&mu;S&middot;s)",
        "scr_amplitude": "SCR Amp. (&mu;S)",
        "scr_count": "SCR Count",
    }

    html = ['<table class="gen-tbl">']
    html.append("<thead><tr>")
    html.append("<th>Metric</th><th>FF+PID</th><th>PID</th><th><em>p</em></th><th><em>d</em></th>")
    html.append("</tr></thead><tbody>")

    for r in eda_tests:
        if r["direction"] != "parallel":
            continue
        dv = r["dv"]
        label = metric_labels.get(dv, dv)

        ff_m = fmt(r["ff_pid_mean"], 2) if dv != "scr_count" else fmt(r["ff_pid_mean"], 1)
        ff_s = fmt(r["ff_pid_sd"], 2) if dv != "scr_count" else fmt(r["ff_pid_sd"], 1)
        pid_m = fmt(r["pid_mean"], 2) if dv != "scr_count" else fmt(r["pid_mean"], 1)
        pid_s = fmt(r["pid_sd"], 2) if dv != "scr_count" else fmt(r["pid_sd"], 1)

        # For AUC, round to integers
        if "auc" in dv:
            ff_m = fmt(r["ff_pid_mean"], 0)
            ff_s = fmt(r["ff_pid_sd"], 0)
            pid_m = fmt(r["pid_mean"], 0)
            pid_s = fmt(r["pid_sd"], 0)

        p = fmt_p(r["p_value"])
        d = fmt(r["cohens_d"], 3)

        html.append(f"<tr><td>{label}</td>")
        html.append(f"<td>{ff_m} &plusmn; {ff_s}</td>")
        html.append(f"<td>{pid_m} &plusmn; {pid_s}</td>")
        html.append(f"<td>{p}</td><td>{d}</td></tr>")

    html.append("</tbody></table>")
    html.append('<p class="tbl-fn">')
    html.append("Test selection: Shapiro&ndash;Wilk normality test on difference scores; <em>t</em> = paired <em>t</em>-test, <em>W</em> = Wilcoxon. ")
    html.append("SCL = tonic component (raw signal); SCR = phasic component (bandpass filtered 0.05&ndash;3.0 Hz). ")
    html.append("<em>n</em> = 19; S18 excluded. No significant differences (all <em>p</em> &gt; 0.4, |<em>d</em>| &lt; 0.2).")
    html.append("</p>")

    (OUT_DIR / "table15.html").write_text("\n".join(html), encoding="utf-8")
    print("Generated: table15.html")


# ===========================================================================
# Table 16: EDA Orthogonal
# ===========================================================================
def generate_table16():
    """Table 16: EDA Results, Orthogonal Direction."""
    eda_tests_path = None
    for base in [ANALYSIS_BASE,
                 Path(__file__).resolve().parent.parent.parent.parent.parent / "20_Experiment_RA-L" / "30_analysis" / "analysis_data"]:
        p = base / "eda" / "eda_paired_tests.csv"
        if p.exists():
            eda_tests_path = p
            break

    if eda_tests_path is None:
        import glob
        candidates = glob.glob(str(Path(__file__).resolve().parents[4]) + "/**/eda_paired_tests.csv", recursive=True)
        if candidates:
            eda_tests_path = Path(candidates[0])

    eda_tests = read_csv(eda_tests_path)

    metric_labels = {
        "scl_mean": "SCL Mean (&mu;S)",
        "scl_sd": "SCL SD (&mu;S)",
        "scl_range": "SCL Range (&mu;S)",
        "scl_auc": "SCL AUC (&mu;S&middot;s)",
        "scr_amplitude": "SCR Amp. (&mu;S)",
        "scr_count": "SCR Count",
    }

    html = ['<table class="gen-tbl">']
    html.append("<thead><tr>")
    html.append("<th>Metric</th><th>FF+PID</th><th>PID</th><th><em>p</em></th><th><em>d</em></th>")
    html.append("</tr></thead><tbody>")

    for r in eda_tests:
        if r["direction"] != "orthogonal":
            continue
        dv = r["dv"]
        label = metric_labels.get(dv, dv)

        ff_m = fmt(r["ff_pid_mean"], 2) if dv != "scr_count" else fmt(r["ff_pid_mean"], 1)
        ff_s = fmt(r["ff_pid_sd"], 2) if dv != "scr_count" else fmt(r["ff_pid_sd"], 1)
        pid_m = fmt(r["pid_mean"], 2) if dv != "scr_count" else fmt(r["pid_mean"], 1)
        pid_s = fmt(r["pid_sd"], 2) if dv != "scr_count" else fmt(r["pid_sd"], 1)

        if "auc" in dv:
            ff_m = fmt(r["ff_pid_mean"], 0)
            ff_s = fmt(r["ff_pid_sd"], 0)
            pid_m = fmt(r["pid_mean"], 0)
            pid_s = fmt(r["pid_sd"], 0)

        p = fmt_p(r["p_value"])
        d = fmt(r["cohens_d"], 3)

        # Bold significant rows
        is_sig = r.get("significant", "False") == "True"

        html.append(f"<tr><td>{label}</td>")
        html.append(f"<td>{ff_m} &plusmn; {ff_s}</td>")
        html.append(f"<td>{pid_m} &plusmn; {pid_s}</td>")
        if is_sig:
            html.append(f"<td><strong>{p}</strong></td><td><strong>{d}</strong></td></tr>")
        else:
            html.append(f"<td>{p}</td><td>{d}</td></tr>")

    html.append("</tbody></table>")
    html.append('<p class="tbl-fn">')
    html.append("Test selection as in Table 15. <em>n</em> = 19; S18 excluded. ")
    html.append("The significant SCL differences (|<em>d</em>| = 0.636&ndash;0.787) align with the variance decomposition findings: orthogonal PID had the highest within-participant SD (0.010 N).")
    html.append("</p>")

    (OUT_DIR / "table16.html").write_text("\n".join(html), encoding="utf-8")
    print("Generated: table16.html")


# ===========================================================================
# Table 17: Power analysis force (from tab_power_analysis.tex data)
# ===========================================================================
def generate_table17():
    """Table 17: Post-hoc Power Analysis for All Force Control Metrics."""
    # Data from the LaTeX table / power_analysis_new.md
    data = [
        ("Parallel", "Mean", "<em>t</em>", "0.883", "0.977", "11", "17"),
        ("Parallel", "RMSE", "<em>W</em>", "&minus;1.749", "&gt;0.999", "3", "5"),
        ("Parallel", "MAE", "<em>t</em>", "&minus;1.670", "&gt;0.999", "3", "5"),
        ("Parallel", "CV", "<em>t</em>", "&minus;2.476", "&gt;0.999", "2", "3"),
        ("Parallel", "&Delta;F", "<em>W</em>", "&minus;1.047", "0.997", "8", "12"),
        ("Parallel", "MASD", "<em>t</em>", "&minus;0.857", "0.969", "11", "18"),
        ("Orthogonal", "Mean", "<em>t</em>", "0.676", "0.856", "18", "29"),
        ("Orthogonal", "RMSE", "<em>W</em>", "&minus;1.271", "&gt;0.999", "5", "9"),
        ("Orthogonal", "MAE", "<em>t</em>", "&minus;1.452", "&gt;0.999", "4", "7"),
        ("Orthogonal", "CV", "<em>W</em>", "&minus;1.130", "&gt;0.999", "7", "11"),
        ("Orthogonal", "&Delta;F", "<em>t</em>", "0.019", "&mdash;", "&mdash;", "&mdash;"),
        ("Orthogonal", "MASD", "<em>t</em>", "&minus;1.433", "&gt;0.999", "4", "7"),
    ]

    html = ['<table class="gen-tbl">']
    html.append("<thead><tr>")
    html.append("<th>Direction</th><th>Metric</th><th>Test</th><th>Cohen's <em>d</em></th><th>Power (<em>n</em>=20)</th><th><em>n</em> for 80%</th><th><em>n</em> for 95%</th>")
    html.append("</tr></thead><tbody>")

    prev_dir = ""
    for direction, metric, test, d, power, n80, n95 in data:
        if direction != prev_dir and prev_dir:
            html.append(f'<tr><td colspan="7" style="border-bottom:1px solid var(--border);padding:0"></td></tr>')
        prev_dir = direction
        html.append(f"<tr><td>{direction}</td><td>{metric}</td><td>{test}</td><td>{d}</td><td>{power}</td><td>{n80}</td><td>{n95}</td></tr>")

    html.append("</tbody></table>")
    html.append('<p class="tbl-fn">')
    html.append("Power calculated as &Phi;(|<em>d</em>|&radic;<em>n</em> &minus; <em>z</em><sub>&alpha;/2</sub>). ")
    html.append("<em>t</em> = paired <em>t</em>-test; <em>W</em> = Wilcoxon signed-rank test. ")
    html.append("All significant metrics achieved power &gt; 0.85. ")
    html.append("Orthogonal &Delta;F (<em>d</em> = 0.019): no effect, excluded from power calculation.")
    html.append("</p>")

    (OUT_DIR / "table17.html").write_text("\n".join(html), encoding="utf-8")
    print("Generated: table17.html")


# ===========================================================================
# Table 18: Power questionnaire (hardcoded from supplementary)
# ===========================================================================
def generate_table18():
    """Table 18: Post-hoc Power Analysis, Perceptual Questionnaire."""
    data = [
        ("Parallel", "Comfort", "0.335", "Medium (n.s.)"),
        ("Parallel", "Naturalness", "0.296", "Small&ndash;medium (n.s.)"),
        ("Parallel", "Consistency", "0.090", "Negligible (n.s.)"),
        ("Orthogonal", "Comfort", "0.062", "Negligible (n.s.)"),
        ("Orthogonal", "Naturalness", "0.198", "Small (n.s.)"),
        ("Orthogonal", "Consistency", "0.390", "Medium (<em>p</em> = 0.081, trend)"),
    ]

    html = ['<table class="gen-tbl">']
    html.append("<thead><tr>")
    html.append("<th>Direction</th><th>Scale</th><th><em>r</em></th><th>Interpretation</th>")
    html.append("</tr></thead><tbody>")

    prev_dir = ""
    for direction, scale, r, interp in data:
        if direction != prev_dir and prev_dir:
            html.append(f'<tr><td colspan="4" style="border-bottom:1px solid var(--border);padding:0"></td></tr>')
        prev_dir = direction
        html.append(f"<tr><td>{direction}</td><td>{scale}</td><td>{r}</td><td>{interp}</td></tr>")

    html.append("</tbody></table>")
    html.append('<p class="tbl-fn">')
    html.append("n.s. = not significant (<em>p</em> &gt; 0.05). ")
    html.append("Effect sizes are small (<em>r</em> &lt; 0.4), confirming that non-significant results are attributable to genuinely minimal differences in subjective evaluation, not to insufficient statistical power.")
    html.append("</p>")

    (OUT_DIR / "table18.html").write_text("\n".join(html), encoding="utf-8")
    print("Generated: table18.html")


# ===========================================================================
# Table 19: Power EDA (hardcoded from supplementary)
# ===========================================================================
def generate_table19():
    """Table 19: Post-hoc Power Analysis, EDA."""
    data = [
        ("Orthogonal", "SCL Mean", "0.748", "0.869", "17"),
        ("Orthogonal", "SCL SD", "0.650", "0.764", "21"),
        ("Orthogonal", "SCL Range", "0.636", "0.746", "22"),
        ("Orthogonal", "SCL AUC", "0.787", "0.900", "15"),
        ("Orthogonal", "SCR Amp.", "0.122", "0.080", "&mdash;"),
        ("Orthogonal", "SCR Count", "0.363", "0.322", "62"),
        ("Orthogonal", "SCR AUC", "0.232", "0.134", "&mdash;"),
        ("Parallel", "All SCL/SCR", "&lt;0.2", "&lt;0.10", "&mdash;"),
    ]

    html = ['<table class="gen-tbl">']
    html.append("<thead><tr>")
    html.append("<th>Direction</th><th>Metric</th><th>|<em>d</em>|</th><th>Power</th><th><em>n</em><sub>80%</sub></th>")
    html.append("</tr></thead><tbody>")

    prev_dir = ""
    for direction, metric, d, power, n80 in data:
        if direction != prev_dir and prev_dir:
            html.append(f'<tr><td colspan="5" style="border-bottom:1px solid var(--border);padding:0"></td></tr>')
        prev_dir = direction
        html.append(f"<tr><td>{direction}</td><td>{metric}</td><td>{d}</td><td>{power}</td><td>{n80}</td></tr>")

    html.append("</tbody></table>")
    html.append('<p class="tbl-fn">')
    html.append("<em>n</em><sub>80%</sub>: minimum <em>n</em> for 80% power. ")
    html.append("Dashes indicate negligible effect sizes for which power analysis is not meaningful. ")
    html.append("<em>n</em> = 19; S18 excluded.")
    html.append("</p>")

    (OUT_DIR / "table19.html").write_text("\n".join(html), encoding="utf-8")
    print("Generated: table19.html")


# ===========================================================================
# Main
# ===========================================================================
if __name__ == "__main__":
    generate_table1()
    generate_table2()
    generate_table3()
    generate_table4()
    generate_table5()
    generate_table6()
    generate_table7()
    generate_table8()
    generate_table9()
    generate_table10()
    generate_table11()
    generate_table12()
    generate_table13()
    generate_table14()
    generate_table15()
    generate_table16()
    generate_table17()
    generate_table18()
    generate_table19()
    print(f"\nAll 19 tables saved to: {OUT_DIR}")
