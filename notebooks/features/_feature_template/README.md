# Historical Feature Notebook Template

This folder preserves the public-product-era research-to-software package. Do
not copy it for normal new UPL work. Start practical cases from:

```text
cases/_case_template/
```

The historical naming pattern was:

```text
feature_02_card_trends
feature_03_home_advantage
feature_04_official_cards
```

The notebook, research brief, and product plan remain useful when maintaining
Goal Timing or studying how the earlier Postgres -> FastAPI -> React promotion
path worked.

New practical cases instead close with a case contract, reproducible notebook,
meaningful checks, standalone report, deliberate outputs, and limitations.
They do not require `product_plan.md` or software promotion.

For data access, start from cleaned Postgres `staging.*` tables unless you have
a specific reason to debug raw source data. See
`docs/FEATURE_PROMOTION_WORKFLOW.md` for the full rule. If the metric becomes stable
or reusable, use that same workflow doc to decide whether it should stay a direct
query or become an `analytics.*` view.

Folder shape:

```text
feature_xx_short_name/
  README.md
  analysis.ipynb
  research_brief.md
  product_plan.md
  outputs/
```

For separately approved maintenance or promotion of a historical feature,
update:

- `research_brief.md` with the football question, finding, metrics, and caveats.
- `product_plan.md` with what you want the product to do and the readiness
  checklist.
- `docs/FEATURE_PROMOTION_WORKFLOW.md` with the current lifecycle status.

After promotion, keep using `product_plan.md` for change requests. The AI agent
should treat these markdown files as the source of truth, then use the notebook
for evidence and implementation detail.
