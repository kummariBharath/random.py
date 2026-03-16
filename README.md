# CSV Analyzer

This folder now contains a small CSV analysis tool that runs with the Python standard library only.

## Run

```powershell
python dashboard.py sample_sales.csv
```

## What it does

- prints a preview of the data
- reports row and column counts
- detects numeric vs categorical columns
- shows missing values, distinct counts, and basic statistics

## Options

```powershell
python dashboard.py sample_sales.csv --preview-rows 3 --top-values 3
```
