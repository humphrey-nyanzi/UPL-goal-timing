<!-- Generated/updated by GitHub Copilot assistant -->
# Repository-specific Copilot / AI Agent Instructions

Purpose: Short, actionable guidance so AI coding agents can be immediately useful in this repository.

**Big Picture**
- **Primary structure:** This repo is notebook-driven data work — the root contains analysis notebooks (`scraping.ipynb`, `cleaning.ipynb`, `analysis.ipynb`) and multiple CSV datasets (`upl_goals_*.csv`).
- **Data flow (inferred from filenames):** `scraping.ipynb` collects raw data -> `cleaning.ipynb` transforms into `*_cleaned.csv` -> `analysis.ipynb` produces final outputs (`*_final.csv`) and figures.

**What to edit and why**
- Prefer editing the notebook that owns a step: change scraping logic in `scraping.ipynb`, cleaning rules in `cleaning.ipynb`, and aggregation/plots in `analysis.ipynb`.
- When you change a notebook that writes a CSV, update the corresponding CSV file in the repo root (e.g., modifying `cleaning.ipynb` should produce `upl_goals_2019_2025_cleaned.csv`).
- Filenames follow a pattern: `upl_goals_<startYear>_<endYear>[_suffix].csv` with common suffixes `_cleaned` and `_final`. Keep that pattern when adding new datasets.

**Developer workflows / commands**
- Open and iterate locally with Jupyter: `jupyter lab` or `jupyter notebook` from the repo root.
- Export or share results: `jupyter nbconvert --to html analysis.ipynb` to generate a readable HTML snapshot.
- To clear outputs before committing: `jupyter nbconvert --clear-output --inplace <notebook.ipynb>` (recommended to keep diffs small).

**Conventions and patterns observed**
- Notebooks are the primary source of truth and typically contain both code and narrative steps. Changes that affect downstream CSVs must be reflected by committing the updated CSV(s).
- No package manifest, tests, or build system detected; assume the environment is ad-hoc. Check notebook top cells for `pip`/`conda` setup instructions or imports.

**Safety and secrets**
- Inspect the top cells of `scraping.ipynb` for API keys, tokens, or credentials before executing. Do not add secrets to tracked notebooks — use environment variables and document them in a separate `README` or `.env` (not present currently).

**When merging or refactoring**
- If you convert notebook logic to scripts (recommended for reproducibility), keep the notebooks as lightweight orchestration/analysis and place reusable code in a new `scripts/` or `src/` folder. Update notebooks to import those scripts.
- If a file with the same dataset name exists, prefer creating a new versioned file (e.g., `upl_goals_2019_2025_cleaned_v2.csv`) rather than silently overwriting without provenance.

**What an AI agent should do first (checklist)**
- Open `scraping.ipynb`, `cleaning.ipynb`, and `analysis.ipynb` to confirm the pipeline and identify where to make changes.
- Search for dataset filenames (e.g., `upl_goals_2019_2025_cleaned.csv`) and link them to the notebook that produces/consumes them.
- Run notebooks interactively before proposing or committing transformations. If long-running, document inputs and expected outputs in the notebook metadata or a short `README`.

**Examples from this repo**
- Update example: change cleaning rules in `cleaning.ipynb` -> regenerate `upl_goals_2019_2025_cleaned.csv` -> update `analysis.ipynb` if aggregations change.
- Snapshot example: use `jupyter nbconvert --to html analysis.ipynb` to produce an analysis snapshot for review.

If anything here is unclear or you want the instructions more prescriptive (for example: recommended Python environment, dependency file, or an automated run command), tell me which parts to expand and I will iterate.
