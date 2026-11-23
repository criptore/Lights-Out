# Setup: reproduce the results step by step

This guide takes you from a fresh clone to the numbers and figures of the report. It takes about 5 minutes,
plus 2 to 5 minutes for the notebooks to run. You need no GPU and no extra download: the data is already in
[`data/`](data/).

## 1. What you need

- **Python 3.12 or newer** for the exact versions (we tested with Python 3.13). Python 3.11 also works with the
  loose `requirements.txt`. Check with `python3 --version` (`py --version` on Windows).
- **Git**, to clone the repository.
- About **500 MB** of free disk space for the virtual environment.
- Optional, only to rebuild the two-column PDF: **pandoc** and a **LaTeX** distribution with `IEEEtran`
  (TeX Live or MacTeX). See step 6.

## 2. Get the code

```bash
git clone https://github.com/criptore/Lights-Out.git
cd Lights-Out
```

All the commands below are run from this folder (the repository root) unless the step says otherwise.

## 3. Create a virtual environment

A virtual environment keeps the project's packages apart from the rest of your computer.

macOS / Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows (PowerShell):

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
```

Your prompt should now start with `(.venv)`. The `.venv/` folder is ignored by git.

## 4. Install the packages

Two files list the packages:

| File | Content | When to use it |
|---|---|---|
| [`requirements-lock.txt`](requirements-lock.txt) | The exact version of every package, from the environment we used to run all four notebooks | To get the same numbers as the report (recommended) |
| [`requirements.txt`](requirements.txt) | The direct dependencies with minimum versions | If an exact version does not install on your machine |

```bash
python -m pip install --upgrade pip
pip install -r requirements-lock.txt
```

Check that the main packages are there:

```bash
python -c "import sklearn, pandas, matplotlib; print(sklearn.__version__, pandas.__version__, matplotlib.__version__)"
```

You should see `1.9.1 3.1.1 3.11.2`.

If `pip install -r requirements-lock.txt` fails (for example on Python 3.11, since the pinned NumPy and SciPy need
3.12 or newer), use `pip install -r requirements.txt` instead. The notebooks still run, but the third decimal of some
scores can move (see step 7).

## 5. Run the notebooks

The notebooks must run **in order**, because `04_report_figures` reads the results saved by `02` and `03`.

```bash
cd notebooks
for nb in 0*.ipynb; do
  jupyter nbconvert --to notebook --execute --inplace "$nb"
done
cd ..
```

On Windows (PowerShell), replace the loop with:

```powershell
cd notebooks
Get-ChildItem 0*.ipynb | ForEach-Object { jupyter nbconvert --to notebook --execute --inplace $_.Name }
cd ..
```

| Notebook | What it does | Time (laptop) | Writes |
|---|---|---|---|
| `01_eda` | Explores the data (Part II) | < 1 min | figures shown in the notebook |
| `02_classifier` | Trains and tests the major-outage classifier | 1 to 5 min | `results/classifier_*`, `figures/classifier_*.png` |
| `03_regression` | Trains and tests the restoration-time regression | about 1 min | `results/regression_*`, `figures/regression_*.png` |
| `04_report_figures` | Redraws every figure of the report from the saved results, without retraining | < 1 min | `figures/*.png` |

You can also open them one by one in Jupyter or VS Code and use *Run All*. Pick the `.venv` Python as the kernel.
`--inplace` overwrites the notebooks with the new outputs: use `git restore notebooks/` to go back to the committed
versions.

## 6. Optional: rebuild the two-column PDF

The IEEE version of the report is built from `README.md`. This needs `pandoc`, `pdflatex` and the `IEEEtran` class
on top of the Python environment above.

```bash
python3 report/build.py . report
cd report
pdflatex lights-out-ieee.tex
pdflatex lights-out-ieee.tex   # a second time, for the references
cd ..
```

## 7. Check that you get the same results

All random steps use seed 0 (the storm split with `GroupShuffleSplit`, the cross-validation folds and the models),
so a run gives the same numbers every time.

After step 5, compare the result files with the committed ones:

```bash
git status results/
git diff --stat results/
```

With `requirements-lock.txt` on Python 3.13, every table of the report comes out the same. Some files can still
show a diff in the last digits of a few floats (for example `results/regression_summary.json`), because the
order of floating-point operations depends on the processor and on the number of threads. These differences are
far below the precision shown in the report (one or three decimals).

The figures (`figures/*.png`) can differ by a few pixels for the same reason, or because of the fonts installed on
your machine.

## 8. Common problems

| Problem | Fix |
|---|---|
| `jupyter: command not found` | The virtual environment is not active: run the `activate` command of step 3 again. |
| `No module named sklearn` in a notebook | The notebook uses another Python. Choose the `.venv` kernel, or run `python -m ipykernel install --user --name lights-out` and pick `lights-out`. |
| `FileNotFoundError: ../data/...` | Run the notebooks from the `notebooks/` folder, as in step 5. |
| `04_report_figures` fails on a missing file in `results/` | Run `02_classifier` and `03_regression` first. |
| Activate.ps1 is blocked on Windows | Run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once, then activate again. |
| Looking for `county_daily.csv` | Not needed: no notebook uses it. The 3 GB file is in the full dataset on Zenodo (DOI [10.5281/zenodo.23010005](https://doi.org/10.5281/zenodo.23010005)). |
