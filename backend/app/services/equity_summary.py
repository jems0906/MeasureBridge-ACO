from collections import defaultdict


def equity_summary(rows: list[dict], dimension: str, minimum: int = 11) -> dict:
    groups = defaultdict(list)
    for row in rows:
        groups[row["record"][dimension]].append(row)
    any_small = any(len(group) < minimum for group in groups.values())
    output = []
    for label, group in sorted(groups.items()):
        suppressed = any_small
        denominator = sum(row["result"]["eligible"] for row in group)
        numerator = sum(row["result"]["status"] == "met" for row in group)
        output.append({
            "label": label, "suppressed": suppressed,
            "population": None if suppressed else len(group),
            "denominator": None if suppressed else denominator,
            "numerator": None if suppressed else numerator,
            "missingness": None if suppressed else sum(row["record"]["documentation_status"] == "not_documented" for row in group),
            "unresolved": None if suppressed else sum(row["result"]["status"] == "unresolved" for row in group),
            "rate": None if suppressed or not denominator else round(100 * numerator / denominator, 2),
        })
    return {"dimension": dimension, "minimum_cell": minimum, "complementary_suppression": any_small, "groups": output}