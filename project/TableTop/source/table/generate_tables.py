#!/usr/bin/env python3
"""Generate HTML table files from CSV data for the project page.

Reads CSV data from the github-repo and generates standalone HTML table
fragments that can be loaded via fetch() in the project page.

Usage:
    python generate_tables.py

Output:
    source/table/html/*.html files
"""

import csv
from pathlib import Path

REPO = Path(__file__).parent.parent.parent.parent / "github-repo"
FORCE_DIR = REPO / "data" / "force"
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


if __name__ == "__main__":
    generate_table1()
    generate_table5()
    generate_table6()
    print(f"\nAll tables saved to: {OUT_DIR}")
