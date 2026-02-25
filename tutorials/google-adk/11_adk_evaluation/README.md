# Tutorial 11: ADK Evaluation Workflow

This tutorial uses:
- evalset created in ADK Web UI and saved under `finance_assistant/`
- eval config saved under `finance_assistant/`

## 1. Setup Environment (uv)
From `tutorials/google-adk/11_adk_evaluation`:

```bash
uv sync
```

Ensure credentials are set in:
- `finance_assistant/.env`

## 2. (Optional) Create/Update Evalset in ADK Web UI
From `tutorials/google-adk/11_adk_evaluation`:

```bash
uv run adk web
```

In the Web UI:
1. Select app `finance_assistant`.
2. Create/update your evalset.
3. Save evalset file in `finance_assistant/`.

## 2.1 Web UI Prompt Script (for building evalset)
Use these prompts to build `metrics_demo_evalset_v1` in ADK Web UI.

| Tool | Scenario Type | Eval Case ID | Prompt |
|---|---|---|---|
| `calculate_compound_interest` | Happy | `ci_happy_annual_10y` | If I invest $15,000 at 0.07 annual interest for 10 years, how much will I have and how much interest will I earn? |
| `calculate_compound_interest` | Negative | `ci_negative_invalid_rate` | If I invest $10,000 at an annual rate of 1.2 (120%) for 5 years, what will I get? |
| `calculate_loan_payment` | Happy | `lp_happy_mortgage_30y` | For a $300,000 loan at 0.045 annual rate over 30 years, what is my monthly payment, total paid, and total interest? |
| `calculate_loan_payment` | Negative | `lp_negative_invalid_term` | For a $120,000 loan at 0.06 annual rate over 0 years, what is the payment? |
| `calculate_monthly_savings` | Happy | `ms_happy_goal_50k_3y` | How much should I save monthly to reach $50,000 in 3 years at 0.05 annual return? |
| `calculate_monthly_savings` | Negative | `ms_negative_invalid_target` | How much should I save monthly to reach $0 in 4 years at 0.05 annual return? |

## 3. Run ADK Eval CLI on Evalset
From `tutorials/google-adk/11_adk_evaluation`:

```bash
uv run adk eval finance_assistant \
  ./finance_assistant/metrics_demo_evalset_v1.evalset.json \
  --config_file_path ./finance_assistant/test_config.json \
  --print_detailed_results
```

## 4. Render HTML Report
From `tutorials/google-adk/11_adk_evaluation`:

```bash
uv run python ./scripts/render_eval_results_html.py \
  "./finance_assistant/.adk/eval_history/*.evalset_result.json" \
  --config ./finance_assistant/test_config.json \
  --output ./reports/eval_results_report.html
```

Open:
- `reports/eval_results_report.html`

## 5. One-Command Demo Flow (Eval + HTML)
From `tutorials/google-adk/11_adk_evaluation`:

```bash
./scripts/run_metrics_demo_eval_to_html.sh
```
