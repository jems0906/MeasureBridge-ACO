import json
from pathlib import Path

import pytest

from app.services.measure_engine import evaluate, summarize


SPEC = json.loads((Path(__file__).resolve().parents[2] / "fixtures/educational_measure_v1.json").read_text())
BASE = {"patient_id": "SYN-001", "date_of_birth": "1980-01-01", "encounter_date": "2026-10-01", "hypertension": True, "hospice": False, "documentation_status": "completed", "observation_date": "2026-10-01", "systolic": 120, "diastolic": 80, "units": "mmHg"}


@pytest.mark.parametrize("changes,status,eligible", [
    ({}, "met", True),
    ({"date_of_birth": "2008-12-31"}, "met", True),
    ({"date_of_birth": "2009-01-01"}, "excluded", False),
    ({"date_of_birth": "1941-01-01"}, "met", True),
    ({"date_of_birth": "1940-12-31"}, "excluded", False),
    ({"hospice": True}, "excluded", False),
    ({"hospice": None}, "unresolved", False),
    ({"hypertension": None}, "unresolved", False),
    ({"encounter_date": "2027-01-01"}, "excluded", False),
    ({"observation_date": "2026-10-02"}, "unresolved", True),
    ({"observation_date": "2026-01-01"}, "met", True),
    ({"observation_date": "2025-12-31"}, "unresolved", True),
    ({"systolic": None}, "unresolved", True),
    ({"systolic": 301}, "unresolved", True),
    ({"systolic": 50, "diastolic": 30}, "met", True),
    ({"systolic": 300, "diastolic": 200}, "met", True),
    ({"systolic": 80, "diastolic": 80}, "unresolved", True),
    ({"units": "kPa"}, "unresolved", True),
    ({"documentation_status": "not_documented"}, "not_met", True),
    ({"documentation_status": "not_completed"}, "not_met", True),
    ({"documentation_status": "patient_declined"}, "not_met", True),
])
def test_exact_rules(changes, status, eligible):
    outcome = evaluate(BASE | changes, SPEC)
    assert (outcome["status"], outcome["eligible"]) == (status, eligible)


def test_unresolved_eligible_stays_in_denominator():
    summary = summarize([evaluate(BASE, SPEC), evaluate(BASE | {"systolic": None}, SPEC)])
    assert summary["denominator"] == 2
    assert summary["rate"] == 50