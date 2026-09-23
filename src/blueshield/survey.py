"""Descriptive checks of source aggregates; no respondent data or inference."""
from __future__ import annotations

import csv
import json
from collections import defaultdict
from decimal import Decimal, InvalidOperation
from pathlib import Path
from statistics import median


def read_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def positive_integer(value, name: str) -> int:
    try:
        parsed = Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(f"{name} must be a positive integer") from exc
    if not parsed.is_finite() or parsed <= 0 or parsed != parsed.to_integral_value():
        raise ValueError(f"{name} must be a positive integer")
    return int(parsed)


def count_value(value, denominator: int) -> int:
    try:
        parsed = Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError("count must be a nonnegative integer") from exc
    if not parsed.is_finite() or parsed < 0 or parsed > denominator or parsed != parsed.to_integral_value():
        raise ValueError("count must be an integer within its denominator")
    return int(parsed)


def percentage(value) -> Decimal:
    try:
        result = Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError("percentage must be finite and within 0..100") from exc
    if not result.is_finite() or not Decimal(0) <= result <= Decimal(100):
        raise ValueError("percentage must be finite and within 0..100")
    return result


def audit_demographics(rows: list[dict]) -> dict:
    groups = defaultdict(list)
    output = []
    seen = set()
    for row in rows:
        key = (row["group"], row["category"])
        if key in seen:
            raise ValueError(f"duplicate demographic category: {key}")
        seen.add(key)
        denominator = positive_integer(row["denominator"], "denominator")
        count = count_value(row["count"], denominator)
        record = {**row, "count": count, "denominator": denominator,
                  "calculated_pct": float(Decimal(count) / denominator * 100)}
        groups[row["group"]].append(record)
        output.append(record)
    summaries = {}
    for group, entries in groups.items():
        denominators = {entry["denominator"] for entry in entries}
        if len(denominators) != 1:
            raise ValueError(f"inconsistent denominator in demographic group {group}")
        denominator = denominators.pop()
        total = sum(entry["count"] for entry in entries)
        summaries[group] = {"count_total": total, "stated_denominator": denominator,
                            "reconciles": total == denominator}
    discipline_counts = [entry["count"] for entry in groups.get("discipline", [])]
    return {"rows": output, "groups": summaries,
            "discipline_count_median": median(discipline_counts) if discipline_counts else None,
            "median_interpretation": "Median of five category sizes, not a participant-level outcome."}


def audit_perceptions(rows: list[dict]) -> list[dict]:
    output = []
    seen = set()
    for row in rows:
        if row["item"] in seen:
            raise ValueError("duplicate perception item")
        seen.add(row["item"])
        denominator = positive_integer(row["assumed_denominator"], "assumed_denominator")
        very, somewhat = percentage(row["very_pct"]), percentage(row["somewhat_pct"])
        total = very + somewhat
        if total > 100:
            raise ValueError("favorable components exceed 100 percent")
        equivalent = total * denominator / 100
        compatible = equivalent == equivalent.to_integral_value()
        output.append({**row, "very_pct": float(very), "somewhat_pct": float(somewhat),
                       "assumed_denominator": denominator, "favorable_pct": float(total),
                       "conditional_count_equivalent": int(equivalent) if compatible else float(equivalent),
                       "compatible_with_integer_count": compatible,
                       "count_status": "conditional_arithmetic_not_verified_observed_count"})
    return output


def audit_interviews(rows: list[dict]) -> list[dict]:
    output = []
    for row in rows:
        denominator = positive_integer(row["denominator"], "denominator")
        count = count_value(row["count"], denominator)
        output.append({**row, "count": count, "denominator": denominator,
                       "calculated_pct": float(Decimal(count) / denominator * 100)})
    return output


def audit_survey(data_dir: Path) -> dict:
    metadata = json.loads((data_dir / "metadata.json").read_text(encoding="utf-8"))
    impact = json.loads((data_dir / "impact_discrepancy.json").read_text(encoding="utf-8"))
    if impact.get("exclude_from_analysis") is not True or impact.get("selected_distribution") is not None:
        raise ValueError("unresolved impact item must remain excluded with no selected distribution")
    return {"status": "descriptive_aggregate_audit_not_inferential_analysis",
            "metadata": metadata,
            "demographics": audit_demographics(read_csv(data_dir / "demographics.csv")),
            "perceptions": audit_perceptions(read_csv(data_dir / "perceptions.csv")),
            "interviews": {"rows": audit_interviews(read_csv(data_dir / "interview_summaries.csv")),
                           "interpretation": "Distinct prompts/categories may overlap; no combined prevalence, coding reliability or saturation is inferred."},
            "excluded_items": ["anticipated_impact"], "impact_discrepancy": impact,
            "inference_performed": False, "respondent_records_generated": False}
