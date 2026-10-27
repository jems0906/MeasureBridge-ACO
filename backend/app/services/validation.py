import csv
import io
import re
from datetime import date


FIELDS = ["patient_id", "name", "date_of_birth", "encounter_date", "facility_type", "access_barrier", "hypertension", "hospice", "documentation_status", "observation_date", "systolic", "diastolic", "units"]
STATUSES = {"completed", "not_documented", "not_completed", "patient_declined"}


def parse_csv(content: str, existing: set[str], filename: str) -> tuple[list[dict], list[dict]]:
    reader = csv.DictReader(io.StringIO(content.lstrip("\ufeff")), strict=True)
    accepted, errors = [], []
    if not reader.fieldnames or len(reader.fieldnames) != len(FIELDS) or set(reader.fieldnames) != set(FIELDS):
        return [], [{"row": 1, "patient_id": None, "message": "Header must contain exactly: " + ", ".join(FIELDS)}]
    seen = set(existing)
    try:
        for row in reader:
            line = reader.line_num
            identifier = row.get("patient_id", "")
            try:
                if None in row or any(value is None for value in row.values()):
                    raise ValueError("Incorrect number of columns")
                row = {key: value.strip() for key, value in row.items()}
                identifier = row["patient_id"]
                if not re.fullmatch(r"SYN-[0-9]{3,6}", identifier):
                    raise ValueError("Only fictional IDs SYN-### through SYN-###### are accepted")
                if identifier in seen:
                    raise ValueError("Duplicate patient_id (file or existing population)")
                seen.add(identifier)
                if not row["name"].startswith("Fictional ") or len(row["name"]) > 120:
                    raise ValueError("Name must be labeled Fictional and at most 120 characters")
                if row["facility_type"] not in {"Community", "Assisted living", "Skilled nursing"}:
                    raise ValueError("Unknown facility_type")
                if row["access_barrier"] not in {"none", "transport", "language"}:
                    raise ValueError("Unknown access_barrier")
                if row["documentation_status"] not in STATUSES:
                    raise ValueError("Unknown documentation_status")
                for field in ("date_of_birth", "encounter_date", "observation_date"):
                    row[field] = date.fromisoformat(row[field]).isoformat() if row[field] else None
                for field in ("hypertension", "hospice"):
                    if row[field] not in {"true", "false", ""}:
                        raise ValueError(f"{field} must be true, false, or blank (unresolved)")
                    row[field] = {"true": True, "false": False, "": None}[row[field]]
                for field, lower, upper in (("systolic", 50, 300), ("diastolic", 30, 200)):
                    value = float(row[field]) if row[field] else None
                    if value is not None and not lower <= value <= upper:
                        raise ValueError(f"{field} outside {lower}..{upper} mmHg")
                    row[field] = value
                if row["units"] not in {"mmHg", ""}:
                    raise ValueError("units must be mmHg or blank")
                if row["documentation_status"] != "completed" and any(row[field] is not None for field in ("systolic", "diastolic", "observation_date")):
                    raise ValueError("Non-completed status conflicts with observation values")
                if row["systolic"] is not None and row["diastolic"] is not None and row["systolic"] <= row["diastolic"]:
                    raise ValueError("Systolic must exceed diastolic")
                if row["date_of_birth"] and row["encounter_date"] and row["date_of_birth"] > row["encounter_date"]:
                    raise ValueError("Birth date after encounter")
                row.update(source_row=line, source_fixture=filename)
                accepted.append(row)
            except (ValueError, TypeError) as error:
                errors.append({"row": line, "patient_id": identifier, "message": str(error)})
    except csv.Error as error:
        errors.append({"row": reader.line_num, "patient_id": None, "message": f"Malformed CSV: {error}"})
    return accepted, errors