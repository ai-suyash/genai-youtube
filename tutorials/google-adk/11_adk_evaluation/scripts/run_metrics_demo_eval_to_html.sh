#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

cd "${PROJECT_DIR}"

uv run adk eval finance_assistant \
  ./finance_assistant/metrics_demo_evalset_v1.evalset.json \
  --config_file_path ./finance_assistant/test_config.json \
  --print_detailed_results

uv run python ./scripts/render_eval_results_html.py \
  "./finance_assistant/.adk/eval_history/*.evalset_result.json" \
  --config ./finance_assistant/test_config.json \
  --output ./reports/eval_results_report.html
