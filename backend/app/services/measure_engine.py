from datetime import date


def evaluate(record: dict, specification: dict) -> dict:
    population = specification["population_rules"]
    numerator = specification["numerator_logic"]
    start = date.fromisoformat(population["period_start"])
    end = date.fromisoformat(population["period_end"])

    def result(status: str, reason: str, category: str, eligible: bool = False) -> dict:
        return {
            "patient_id": record["patient_id"], "status": status, "reason": reason,
            "category": category, "eligible": eligible,
            "rule_id": specification["id"], "rule_version": specification["version"],
            "source_row": record.get("source_row"), "source_fixture": record.get("source_fixture"),
        }

    try:
        birth = date.fromisoformat(record["date_of_birth"])
        encounter = date.fromisoformat(record["encounter_date"])
        if record.get("hypertension") is None or record.get("hospice") is None:
            raise ValueError("Unknown eligibility")
    except (ValueError, TypeError, KeyError):
        return result("unresolved", "Eligibility fields are missing or unknown", "eligibility_question")
    age = end.year - birth.year - ((end.month, end.day) < (birth.month, birth.day))
    if birth > encounter:
        return result("unresolved", "Birth date is after encounter", "eligibility_question")
    if record["hospice"]:
        return result("excluded", "Explicit hospice exclusion", "excluded")
    if not population["minimum_age"] <= age <= population["maximum_age"]:
        return result("excluded", f"Age {age} outside eligible range", "excluded")
    if not start <= encounter <= end or not record["hypertension"]:
        return result("excluded", "No qualifying encounter or condition in period", "excluded")
    status = record.get("documentation_status")
    categories = {"not_documented": "missing_documentation", "not_completed": "true_care_gap", "patient_declined": "patient_preference"}
    if status in categories:
        return result("not_met", status.replace("_", " ").capitalize(), categories[status], True)
    try:
        observation = date.fromisoformat(record["observation_date"])
        systolic, diastolic = float(record["systolic"]), float(record["diastolic"])
        valid = (
            status == numerator["status"] and start <= observation <= min(end, encounter)
            and numerator["systolic_range"][0] <= systolic <= numerator["systolic_range"][1]
            and numerator["diastolic_range"][0] <= diastolic <= numerator["diastolic_range"][1]
            and systolic > diastolic and record.get("units") == numerator["units"]
        )
    except (TypeError, ValueError, KeyError):
        valid = False
    if not valid:
        return result("unresolved", "Completed status has missing or invalid observation fields", "data_pipeline_defect", True)
    return result("met", "Eligible; required assessment documentation is complete", "complete", True)


def summarize(results: list[dict]) -> dict:
    denominator = sum(item["eligible"] for item in results)
    numerator = sum(item["status"] == "met" for item in results)
    return {
        "total": len(results), "denominator": denominator, "numerator": numerator,
        "rate": round(100 * numerator / denominator, 2) if denominator else None,
        "excluded": sum(item["status"] == "excluded" for item in results),
        "unresolved": sum(item["status"] == "unresolved" for item in results),
        "not_met": sum(item["status"] == "not_met" for item in results),
        "eligibility_questions": sum(item["category"] == "eligibility_question" for item in results),
    }