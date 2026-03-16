import argparse
import csv
import math
import os
import statistics
from collections import Counter


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Inspect a CSV file and print a compact data quality report."
    )
    parser.add_argument("csv_file", help="Path to the CSV file to analyze.")
    parser.add_argument(
        "--preview-rows",
        type=int,
        default=5,
        help="Number of rows to show in the preview section.",
    )
    parser.add_argument(
        "--top-values",
        type=int,
        default=5,
        help="Number of common values to show for categorical columns.",
    )
    return parser.parse_args()


def is_missing(value: str) -> bool:
    return value is None or value.strip() == ""


def try_float(value: str) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def load_csv(path: str) -> tuple[list[str], list[dict[str, str]]]:
    encodings = ["utf-8-sig", "utf-16", "utf-16-le", "utf-16-be", "cp1252", "latin-1"]
    last_error: Exception | None = None

    for encoding in encodings:
        try:
            with open(path, "r", newline="", encoding=encoding) as handle:
                reader = csv.DictReader(handle)
                if not reader.fieldnames:
                    raise ValueError("CSV file does not contain a header row.")
                rows = list(reader)
                return reader.fieldnames, rows
        except UnicodeError as exc:
            last_error = exc

    if last_error is not None:
        raise ValueError(
            "Could not decode the CSV file. Tried: " + ", ".join(encodings)
        ) from last_error

    raise ValueError("CSV file could not be read.")


def profile_column(
    rows: list[dict[str, str]], column: str, top_values: int
) -> dict[str, object]:
    values = [row.get(column, "") for row in rows]
    non_missing = [value for value in values if not is_missing(value)]
    missing_count = len(values) - len(non_missing)

    numeric_values: list[float] = []
    numeric_like = True
    for value in non_missing:
        parsed = try_float(value)
        if parsed is None:
            numeric_like = False
            break
        numeric_values.append(parsed)

    if non_missing and numeric_like:
        return {
            "type": "numeric",
            "missing": missing_count,
            "distinct": len(set(non_missing)),
            "min": min(numeric_values),
            "max": max(numeric_values),
            "mean": statistics.fmean(numeric_values),
            "median": statistics.median(numeric_values),
        }

    counts = Counter(non_missing)
    return {
        "type": "categorical",
        "missing": missing_count,
        "distinct": len(counts),
        "top": counts.most_common(top_values),
    }


def format_number(value: float) -> str:
    if math.isfinite(value) and value.is_integer():
        return str(int(value))
    return f"{value:.2f}"


def print_preview(fieldnames: list[str], rows: list[dict[str, str]], preview_rows: int) -> None:
    print("Preview")
    print("-" * 72)
    print(" | ".join(fieldnames))
    for row in rows[:preview_rows]:
        print(" | ".join(str(row.get(name, "")) for name in fieldnames))
    print()


def print_summary(fieldnames: list[str], rows: list[dict[str, str]], top_values: int) -> None:
    print("Summary")
    print("-" * 72)
    print(f"Rows: {len(rows)}")
    print(f"Columns: {len(fieldnames)}")
    print()

    for column in fieldnames:
        profile = profile_column(rows, column, top_values)
        print(f"{column} [{profile['type']}]")
        print(f"  missing: {profile['missing']}")
        print(f"  distinct: {profile['distinct']}")
        if profile["type"] == "numeric":
            print(f"  min: {format_number(profile['min'])}")
            print(f"  max: {format_number(profile['max'])}")
            print(f"  mean: {format_number(profile['mean'])}")
            print(f"  median: {format_number(profile['median'])}")
        else:
            top = profile["top"]
            if top:
                print("  common values:")
                for value, count in top:
                    print(f"    {value}: {count}")
            else:
                print("  common values: none")
        print()


def main() -> int:
    args = parse_args()
    path = args.csv_file

    if not os.path.exists(path):
        print(f"File not found: {path}")
        return 1

    try:
        fieldnames, rows = load_csv(path)
    except Exception as exc:
        print(f"Failed to read CSV: {exc}")
        return 1

    print(f"CSV Analyzer Report: {os.path.basename(path)}")
    print("=" * 72)
    print_preview(fieldnames, rows, args.preview_rows)
    print_summary(fieldnames, rows, args.top_values)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
