#!/usr/bin/env python3
"""Render ADK evalset result JSON files into an ADK-style HTML report."""

from __future__ import annotations

import argparse
import glob
import html
import json
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any

PASS_STATUS = 1
FAIL_STATUS = 2


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Render ADK eval result JSON file(s) into a styled HTML report."
    )
    parser.add_argument(
        "input",
        nargs="?",
        default=None,
        help=(
            "Optional input path/glob. Supports a JSON file, directory, or glob. "
            "If omitted, uses latest finance_assistant/.adk/eval_history/*.evalset_result.json."
        ),
    )
    parser.add_argument(
        "-o",
        "--output",
        default="reports/eval_results_report.html",
        help="Output HTML path (default: reports/eval_results_report.html)",
    )
    parser.add_argument(
        "--config",
        default=None,
        help="Optional config JSON path. Metric names from criteria are shown in report.",
    )
    return parser.parse_args()


def collect_input_files(input_arg: str | None) -> list[Path]:
    if input_arg is None:
        default_glob = "finance_assistant/.adk/eval_history/*.evalset_result.json"
        matches = sorted(glob.glob(default_glob), key=lambda p: Path(p).stat().st_mtime)
        if not matches:
            raise FileNotFoundError(
                "No eval result files found at default path: "
                f"{default_glob}. Pass an explicit input path."
            )
        return [Path(matches[-1])]

    path = Path(input_arg)
    if path.is_file():
        return [path]
    if path.is_dir():
        files = sorted(path.glob("*.evalset_result.json"), key=lambda p: p.stat().st_mtime)
        if files:
            return files
        files = sorted(path.glob("*.json"), key=lambda p: p.stat().st_mtime)
        if files:
            return files
        raise FileNotFoundError(f"No JSON files found in directory: {path}")

    matches = sorted(glob.glob(input_arg), key=lambda p: Path(p).stat().st_mtime)
    if matches:
        return [Path(p) for p in matches]

    raise FileNotFoundError(f"Input not found: {input_arg}")


def status_label(status: Any) -> str:
    if status == PASS_STATUS:
        return "PASS"
    if status == FAIL_STATUS:
        return "FAIL"
    return f"UNKNOWN({status})"


def configured_metrics(config_path: str | None) -> list[str]:
    if not config_path:
        return []
    p = Path(config_path).expanduser()
    if not p.is_file():
        return []
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []
    criteria = data.get("criteria")
    if not isinstance(criteria, dict):
        return []
    return sorted(str(name) for name in criteria.keys())


def extract_text(invocation: dict[str, Any] | None) -> str:
    if not invocation:
        return ""
    parts = ((invocation.get("final_response") or {}).get("parts") or [])
    texts: list[str] = []
    for part in parts:
        if isinstance(part, dict) and part.get("text"):
            texts.append(str(part["text"]))
    return "\n".join(texts).strip()


def extract_tool_calls(invocation: dict[str, Any] | None) -> list[str]:
    if not invocation:
        return []
    calls: list[str] = []
    events = ((invocation.get("intermediate_data") or {}).get("invocation_events") or [])
    for event in events:
        content = (event or {}).get("content") or {}
        for part in content.get("parts") or []:
            call = (part or {}).get("function_call")
            if call:
                args = json.dumps(call.get("args", {}), ensure_ascii=True, sort_keys=True)
                calls.append(f"{call.get('name', 'unknown')}({args})")
    return calls


def normalize_metrics(metrics: list[dict[str, Any]] | None, scope: str) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for metric in metrics or []:
        out.append(
            {
                "scope": scope,
                "metric_name": metric.get("metric_name", "unknown"),
                "score": metric.get("score", "n/a"),
                "threshold": metric.get("threshold", "n/a"),
                "status": status_label(metric.get("eval_status")),
            }
        )
    return out


def load_rows(files: list[Path]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for file in files:
        data = json.loads(file.read_text(encoding="utf-8"))
        eval_set_id = data.get("eval_set_id", "")
        for case in data.get("eval_case_results") or []:
            inv_results = case.get("eval_metric_result_per_invocation") or []
            first_inv = inv_results[0] if inv_results else {}
            actual_inv = first_inv.get("actual_invocation") or {}
            expected_inv = first_inv.get("expected_invocation") or {}

            rows.append(
                {
                    "source_name": file.name,
                    "eval_set_id": case.get("eval_set_id") or eval_set_id,
                    "eval_id": case.get("eval_id", ""),
                    "status": status_label(case.get("final_eval_status")),
                    "metrics": normalize_metrics(
                        case.get("overall_eval_metric_results") or [], "overall"
                    )
                    + normalize_metrics(first_inv.get("eval_metric_results") or [], "invocation"),
                    "actual_calls": extract_tool_calls(actual_inv),
                    "expected_calls": extract_tool_calls(expected_inv),
                    "actual_response": extract_text(actual_inv),
                    "expected_response": extract_text(expected_inv),
                }
            )
    return rows


def metric_usage(rows: list[dict[str, Any]]) -> Counter:
    counter: Counter = Counter()
    for row in rows:
        for metric in row.get("metrics", []):
            counter[metric.get("metric_name", "unknown")] += 1
    return counter


def make_html(rows: list[dict[str, Any]], input_files: list[Path], config_metrics_list: list[str]) -> str:
    pass_count = sum(1 for r in rows if r["status"] == "PASS")
    fail_count = sum(1 for r in rows if r["status"] == "FAIL")
    unknown_count = len(rows) - pass_count - fail_count
    pass_rate = (pass_count / len(rows) * 100.0) if rows else 0.0

    used_metric_counts = metric_usage(rows)
    used_metric_chips = "".join(
        f"<span class='metric-chip'><code>{html.escape(name)}</code> {count}</span>"
        for name, count in used_metric_counts.most_common()
    ) or "<span class='muted'>(none)</span>"

    configured_metric_chips = "".join(
        f"<span class='metric-chip'><code>{html.escape(name)}</code></span>"
        for name in config_metrics_list
    ) or "<span class='muted'>(none)</span>"

    rows_json = json.dumps(rows, ensure_ascii=True).replace("</", "<\\/")
    input_sources = "\n".join(f"- {str(path)}" for path in input_files)

    template = """<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>ADK Eval Results Report</title>
  <style>
    :root {
      --bg: #f5f8fd;
      --panel: #ffffff;
      --muted: #64748b;
      --text: #10243f;
      --line: #d8e2f0;
      --accent: #2563eb;
      --pass-bg: #dcfce7;
      --pass-fg: #166534;
      --fail-bg: #fee2e2;
      --fail-fg: #991b1b;
      --unknown-bg: #fef3c7;
      --unknown-fg: #92400e;
      --shadow: 0 10px 25px rgba(30, 41, 59, 0.08);
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      background: radial-gradient(circle at 0% 0%, #dbeafe 0%, var(--bg) 42%);
      color: var(--text);
      font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif;
    }
    .page { max-width: 1380px; margin: 0 auto; padding: 16px; }
    .top { background: var(--panel); border: 1px solid var(--line); border-radius: 12px; padding: 12px; box-shadow: var(--shadow); margin-bottom: 12px; }
    .title { font-size: 1.2rem; font-weight: 700; margin: 0; }
    .subtitle { margin-top: 4px; color: var(--muted); font-size: 0.9rem; }
    .stats { display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 10px; margin-top: 10px; }
    .stat { border: 1px solid var(--line); border-radius: 10px; padding: 8px; background: #f8fbff; }
    .stat .k { font-size: 0.78rem; color: var(--muted); }
    .stat .v { font-weight: 700; margin-top: 2px; }
    .chips { margin-top: 10px; }
    .metric-chip { display: inline-block; border: 1px solid var(--line); border-radius: 999px; padding: 3px 8px; margin: 0 6px 6px 0; background: #f8fbff; font-size: 0.82rem; }

    .layout { display: grid; grid-template-columns: 360px 1fr; gap: 12px; min-height: 70vh; }
    .pane { background: var(--panel); border: 1px solid var(--line); border-radius: 12px; box-shadow: var(--shadow); }

    .left-head { padding: 10px; border-bottom: 1px solid var(--line); }
    .search { width: 100%; border: 1px solid var(--line); border-radius: 8px; padding: 8px; }
    .filters { display: flex; gap: 6px; margin-top: 8px; flex-wrap: wrap; }
    .btn { border: 1px solid var(--line); border-radius: 999px; padding: 4px 9px; background: #fff; font-size: 0.8rem; cursor: pointer; }
    .btn.active { background: #dbeafe; border-color: #93c5fd; }
    .case-list { max-height: calc(70vh - 60px); overflow: auto; padding: 8px; }
    .case-item { border: 1px solid var(--line); border-radius: 10px; padding: 8px; margin-bottom: 8px; cursor: pointer; background: #fff; }
    .case-item.active { border-color: var(--accent); background: #eff6ff; }
    .case-row { display: flex; justify-content: space-between; align-items: center; gap: 8px; }
    .case-id { font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, Liberation Mono, monospace; font-size: 0.82rem; }
    .badge { border-radius: 999px; padding: 2px 8px; font-size: 0.72rem; font-weight: 700; }
    .pass { background: var(--pass-bg); color: var(--pass-fg); }
    .fail { background: var(--fail-bg); color: var(--fail-fg); }
    .unknown { background: var(--unknown-bg); color: var(--unknown-fg); }
    .meta { color: var(--muted); font-size: 0.76rem; margin-top: 4px; }

    .right { padding: 12px; overflow: auto; }
    .empty { color: var(--muted); }
    .detail-head { display: flex; justify-content: space-between; align-items: center; gap: 12px; border-bottom: 1px solid var(--line); padding-bottom: 10px; }
    .detail-title { font-size: 1rem; font-weight: 700; }
    .detail-sub { color: var(--muted); font-size: 0.83rem; margin-top: 4px; }

    .invocations { margin-top: 10px; }
    .inv-chip { position: relative; display: inline-block; border: 1px solid var(--line); border-radius: 999px; background: #eef2ff; color: #3730a3; padding: 4px 10px; font-size: 0.8rem; cursor: default; }
    .inv-pop { display: none; position: absolute; left: 0; top: 30px; z-index: 9; width: min(820px, 88vw); border: 1px solid var(--line); border-radius: 10px; background: #fff; box-shadow: 0 16px 40px rgba(0, 0, 0, 0.16); padding: 10px; }
    .inv-chip:hover .inv-pop { display: block; }
    .pop-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
    .pop-title { font-size: 0.78rem; font-weight: 700; margin-bottom: 3px; }

    .section-title { font-size: 0.86rem; font-weight: 700; margin: 12px 0 6px; }
    .metrics-table { width: 100%; border-collapse: collapse; }
    .metrics-table th, .metrics-table td { border-bottom: 1px solid var(--line); padding: 7px; text-align: left; font-size: 0.82rem; vertical-align: top; }
    .metrics-table th { background: #f8fbff; }
    pre { margin: 0; border: 1px solid var(--line); border-radius: 8px; background: #f8fbff; padding: 8px; font-size: 0.8rem; white-space: pre-wrap; word-break: break-word; max-height: 280px; overflow: auto; }
    .compare { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
    code { font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, Liberation Mono, monospace; }

    .foot { margin-top: 10px; color: var(--muted); font-size: 0.8rem; }

    @media (max-width: 1100px) {
      .layout { grid-template-columns: 1fr; }
      .case-list { max-height: 260px; }
    }
    @media (max-width: 760px) {
      .stats { grid-template-columns: repeat(2, minmax(0, 1fr)); }
      .compare, .pop-grid { grid-template-columns: 1fr; }
      .inv-pop { width: min(540px, 92vw); }
    }
  </style>
</head>
<body>
  <div class=\"page\">
    <section class=\"top\">
      <h1 class=\"title\">ADK Eval Results</h1>
      <div class=\"subtitle\">Generated __GENERATED__. ADK-style list/detail view with hoverable invocation previews.</div>
      <div class=\"stats\">
        <div class=\"stat\"><div class=\"k\">Total Cases</div><div class=\"v\">__TOTAL__</div></div>
        <div class=\"stat\"><div class=\"k\">Pass</div><div class=\"v\" style=\"color:var(--pass-fg);\">__PASS__</div></div>
        <div class=\"stat\"><div class=\"k\">Fail</div><div class=\"v\" style=\"color:var(--fail-fg);\">__FAIL__</div></div>
        <div class=\"stat\"><div class=\"k\">Unknown</div><div class=\"v\" style=\"color:var(--unknown-fg);\">__UNKNOWN__</div></div>
        <div class=\"stat\"><div class=\"k\">Pass Rate</div><div class=\"v\">__PASS_RATE__</div></div>
      </div>
      <div class=\"chips\"><strong style=\"font-size:0.82rem; color: var(--muted);\">Configured Metrics:</strong> __CONFIG_METRICS__</div>
      <div class=\"chips\"><strong style=\"font-size:0.82rem; color: var(--muted);\">Metrics Observed In Results:</strong> __USED_METRICS__</div>
    </section>

    <section class=\"layout\">
      <aside class=\"pane\">
        <div class=\"left-head\">
          <input id=\"search\" class=\"search\" placeholder=\"Search eval_id\" />
          <div class=\"filters\">
            <button class=\"btn active\" data-filter=\"ALL\">All</button>
            <button class=\"btn\" data-filter=\"PASS\">Pass</button>
            <button class=\"btn\" data-filter=\"FAIL\">Fail</button>
            <button class=\"btn\" data-filter=\"UNKNOWN\">Unknown</button>
          </div>
        </div>
        <div id=\"caseList\" class=\"case-list\"></div>
      </aside>

      <main class=\"pane right\" id=\"detailPane\">
        <div class=\"empty\">Select an eval case from the left panel.</div>
      </main>
    </section>

    <details class=\"foot\">
      <summary>Input Files</summary>
      <pre>__SOURCES__</pre>
    </details>
  </div>

  <script id=\"rows-data\" type=\"application/json\">__ROWS_JSON__</script>
  <script>
    const rows = JSON.parse(document.getElementById('rows-data').textContent || '[]');
    const listEl = document.getElementById('caseList');
    const detailEl = document.getElementById('detailPane');
    const searchEl = document.getElementById('search');
    const filterButtons = Array.from(document.querySelectorAll('.btn[data-filter]'));

    let activeFilter = 'ALL';
    let selectedIndex = rows.length ? 0 : -1;

    function esc(s) {
      if (s === null || s === undefined) return '';
      return String(s)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
    }

    function rowClass(status) {
      if (status === 'PASS') return 'pass';
      if (status === 'FAIL') return 'fail';
      return 'unknown';
    }

    function filteredRowsWithIndex() {
      const q = (searchEl.value || '').toLowerCase().trim();
      return rows
        .map((r, i) => ({ row: r, originalIndex: i }))
        .filter(({ row }) => {
          const statusMatch = activeFilter === 'ALL' || row.status === activeFilter;
          const text = `${row.eval_id} ${row.eval_set_id} ${row.source_name}`.toLowerCase();
          const textMatch = !q || text.includes(q);
          return statusMatch && textMatch;
        });
    }

    function renderCaseList() {
      const filtered = filteredRowsWithIndex();
      if (!filtered.length) {
        listEl.innerHTML = '<div class="empty">No matching cases.</div>';
        detailEl.innerHTML = '<div class="empty">No case selected.</div>';
        return;
      }

      if (!filtered.some((item) => item.originalIndex === selectedIndex)) {
        selectedIndex = filtered[0].originalIndex;
      }

      listEl.innerHTML = filtered.map(({ row, originalIndex }, idx) => `
        <article class="case-item ${originalIndex === selectedIndex ? 'active' : ''}" data-index="${originalIndex}">
          <div class="case-row">
            <span class="case-id">[${idx + 1}] ${esc(row.eval_id)}</span>
            <span class="badge ${rowClass(row.status)}">${esc(row.status)}</span>
          </div>
          <div class="meta">set: ${esc(row.eval_set_id)}</div>
          <div class="meta">file: ${esc(row.source_name)}</div>
        </article>
      `).join('');

      Array.from(listEl.querySelectorAll('.case-item')).forEach((el) => {
        el.addEventListener('click', () => {
          selectedIndex = Number(el.getAttribute('data-index'));
          renderCaseList();
          renderDetail();
        });
      });

      renderDetail();
    }

    function metricRows(metrics) {
      if (!metrics || !metrics.length) {
        return '<tr><td colspan="5" class="empty">No metrics for this case.</td></tr>';
      }
      return metrics.map((m) => `
        <tr>
          <td><code>${esc(m.metric_name)}</code></td>
          <td>${esc(m.scope)}</td>
          <td>${esc(m.score)}</td>
          <td>${esc(m.threshold)}</td>
          <td><span class="badge ${rowClass(m.status)}">${esc(m.status)}</span></td>
        </tr>
      `).join('');
    }

    function asText(items) {
      return items && items.length ? items.join('\\\\n') : '(none)';
    }

    function renderDetail() {
      if (selectedIndex < 0 || !rows[selectedIndex]) {
        detailEl.innerHTML = '<div class="empty">No case selected.</div>';
        return;
      }
      const row = rows[selectedIndex];
      detailEl.innerHTML = `
        <header class="detail-head">
          <div>
            <div class="detail-title"><code>${esc(row.eval_id)}</code></div>
            <div class="detail-sub">Eval set: <code>${esc(row.eval_set_id)}</code> | Source: <code>${esc(row.source_name)}</code></div>
          </div>
          <span class="badge ${rowClass(row.status)}">${esc(row.status)}</span>
        </header>

        <section class="invocations">
          <div class="section-title">Invocations</div>
          <span class="inv-chip">Invocation 1
            <span class="inv-pop">
              <div class="section-title" style="margin-top:0;">Expected vs Actual (Hover Preview)</div>
              <div class="pop-grid">
                <div>
                  <div class="pop-title">Expected Tool Calls</div>
                  <pre>${esc(asText(row.expected_calls))}</pre>
                </div>
                <div>
                  <div class="pop-title">Actual Tool Calls</div>
                  <pre>${esc(asText(row.actual_calls))}</pre>
                </div>
                <div>
                  <div class="pop-title">Expected Response</div>
                  <pre>${esc(row.expected_response || '(empty)')}</pre>
                </div>
                <div>
                  <div class="pop-title">Actual Response</div>
                  <pre>${esc(row.actual_response || '(empty)')}</pre>
                </div>
              </div>
            </span>
          </span>
        </section>

        <section>
          <div class="section-title">Metrics Used</div>
          <table class="metrics-table">
            <thead>
              <tr><th>Metric</th><th>Scope</th><th>Score</th><th>Threshold</th><th>Status</th></tr>
            </thead>
            <tbody>${metricRows(row.metrics)}</tbody>
          </table>
        </section>

        <section class="compare" style="margin-top:10px;">
          <div>
            <div class="section-title">Expected Tool Calls</div>
            <pre>${esc(asText(row.expected_calls))}</pre>
          </div>
          <div>
            <div class="section-title">Actual Tool Calls</div>
            <pre>${esc(asText(row.actual_calls))}</pre>
          </div>
        </section>

        <section class="compare" style="margin-top:10px;">
          <div>
            <div class="section-title">Expected Final Response</div>
            <pre>${esc(row.expected_response || '(empty)')}</pre>
          </div>
          <div>
            <div class="section-title">Actual Final Response</div>
            <pre>${esc(row.actual_response || '(empty)')}</pre>
          </div>
        </section>
      `;
    }

    filterButtons.forEach((button) => {
      button.addEventListener('click', () => {
        activeFilter = button.dataset.filter || 'ALL';
        filterButtons.forEach((b) => b.classList.remove('active'));
        button.classList.add('active');
        renderCaseList();
      });
    });

    searchEl.addEventListener('input', function () { renderCaseList(); });
    try {
      renderCaseList();
    } catch (e) {
      detailEl.innerHTML = '<div class="empty">Failed to render report UI. Check browser console.</div>';
      throw e;
    }
  </script>
</body>
</html>
"""

    return (
        template.replace("__GENERATED__", html.escape(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        .replace("__TOTAL__", str(len(rows)))
        .replace("__PASS__", str(pass_count))
        .replace("__FAIL__", str(fail_count))
        .replace("__UNKNOWN__", str(unknown_count))
        .replace("__PASS_RATE__", f"{pass_rate:.1f}%")
        .replace("__CONFIG_METRICS__", configured_metric_chips)
        .replace("__USED_METRICS__", used_metric_chips)
        .replace("__SOURCES__", html.escape(input_sources))
        .replace("__ROWS_JSON__", rows_json)
    )


def main() -> int:
    args = parse_args()
    input_files = collect_input_files(args.input)
    rows = load_rows(input_files)
    config_metric_names = configured_metrics(args.config)

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(make_html(rows, input_files, config_metric_names), encoding="utf-8")

    print(f"Wrote report: {out_path}")
    print(f"Input files: {len(input_files)}")
    print(f"Eval cases: {len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
