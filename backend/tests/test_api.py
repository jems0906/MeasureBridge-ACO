import csv
import io

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.main import app
from app.models import Base, Patient, Snapshot, get_db
from app.services.population import seed
from app.services.validation import FIELDS, parse_csv


@pytest.fixture()
def client():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    with Session(engine) as db:
        seed(db)

        def override():
            yield db

        app.dependency_overrides[get_db] = override
        with TestClient(app) as http:
            yield http, db
    app.dependency_overrides.clear()
    engine.dispose()


def completion(role="Clinical Assistant", provenance="documentation_completion", **changes):
    return {"actor": "Jamie Chen", "role": role, "provenance": provenance, "evidence": "Simulated original chart reviewed; assessment fields located.", "documentation_status": "completed", "observation_date": "2026-10-01", "systolic": 125, "diastolic": 80, "units": "mmHg", "expected_event_id": 0} | changes


def test_fixed_demonstration_and_original_preserved(client):
    http, db = client
    baseline = http.get("/api/dashboard").json()
    assert baseline["current"]["rate"] == 60
    assert baseline["current"]["denominator"] == 100
    for number in range(61, 76):
        response = http.post(f"/api/workflows/SYN-{number:03}", json=completion())
        assert response.status_code == 200, response.text
    current = http.get("/api/dashboard").json()
    assert current["current"]["rate"] == 75
    assert current["baseline"]["rate"] == 60
    assert current["changes"] == {"documentation_completion": 15, "data_repair": 0, "simulated_care_event": 0}
    assert db.get(Patient, "SYN-061").original["documentation_status"] == "not_documented"
    assert http.post("/api/workflows/SYN-086", json=completion()).status_code == 409
    assert http.post("/api/workflows/SYN-076", json=completion()).status_code == 422


def test_provenance_roles_and_concurrency(client):
    http, _ = client
    assert http.post("/api/workflows/SYN-091", json=completion()).status_code == 422
    assert http.post("/api/workflows/SYN-091", json=completion(provenance="data_repair")).status_code == 403
    assert http.post("/api/workflows/SYN-091", json=completion("EHR/IT", "data_repair")).status_code == 200
    assert http.post("/api/workflows/SYN-091", json=completion("EHR/IT", "data_repair")).status_code == 409
    assert http.post("/api/workflows/SYN-062", json=completion(observation_date="2027-01-01")).status_code == 422
    assert http.post("/api/workflows/SYN-063", json=completion(documentation_status="patient_declined")).status_code == 422
    assert http.post("/api/workflows/SYN-076", json=completion("Provider", "simulated_care_event")).status_code == 200


def test_frozen_approval_and_exports(client):
    http, db = client
    first = http.post("/api/reports", json={"actor": "Sam Rivera", "role": "ACO Operations"}).json()
    review = {"actor": "Casey Lee", "role": "ACO Operations", "evidence": "Counts and evidence independently reviewed."}
    assert http.post(f"/api/reports/{first['id']}/signoff", json=review).status_code == 409
    for number in range(91, 101):
        assert http.post(f"/api/workflows/SYN-{number:03}", json=completion("EHR/IT", "data_repair")).status_code == 200
    second = http.post("/api/reports", json={"actor": "Sam Rivera", "role": "ACO Operations"}).json()
    assert second["counts"]["rate"] == 70
    assert second["blockers"] == []
    assert http.post(f"/api/reports/{second['id']}/signoff", json=review | {"actor": "Sam Rivera"}).status_code == 403
    signed = http.post(f"/api/reports/{second['id']}/signoff", json=review)
    assert signed.status_code == 200
    assert http.post(f"/api/reports/{second['id']}/signoff", json=review).status_code == 409
    assert db.get(Snapshot, first["id"]).payload["counts"]["rate"] == 60
    assert http.post("/api/workflows/SYN-061", json=completion()).status_code == 200
    package = http.get(f"/api/reports/{second['id']}/export").json()
    assert package["package"]["counts"]["rate"] == 70
    assert package["signoff"]["actor"] == "Casey Lee"
    exported = http.get(f"/api/reports/{second['id']}/export?format=csv")
    assert "INTERNAL" in exported.text and len(list(csv.DictReader(io.StringIO(exported.text)))) == 100


def test_equity_suppresses_small_and_complementary_cells(client):
    http, _ = client
    facility = http.get("/api/equity").json()
    assert sum(group["denominator"] for group in facility["groups"]) == 100
    barrier = http.get("/api/equity?dimension=access_barrier").json()
    assert barrier["complementary_suppression"]
    assert all(group["rate"] is None and group["population"] is None for group in barrier["groups"])


def test_import_rejects_duplicate_and_malformed_and_requires_disposition(client):
    http, _ = client
    content = ",".join(FIELDS) + "\nSYN-001,Fictional Duplicate,1980-01-01,2026-10-01,Community,none,true,false,completed,2026-10-01,120,80,mmHg\nSYN-999,Fictional Bad,not-a-date,2026-10-01,Community,none,true,false,not_documented,,,,\n"
    response = http.post("/api/imports", files={"file": ("bad.csv", content, "text/csv")})
    batch = response.json()
    assert response.status_code == 200 and batch["accepted"] == 0 and len(batch["errors"]) == 2
    assert http.get("/api/dashboard").json()["open_import_errors"] == 2
    review = {"actor": "Sam Rivera", "role": "ACO Operations", "evidence": "Rejected test rows reviewed; duplicates and invalid date intentionally excluded."}
    assert http.post(f"/api/imports/{batch['id']}/disposition", json=review).status_code == 200
    assert http.get("/api/dashboard").json()["open_import_errors"] == 0
    assert http.get("/api/dashboard").json()["current"]["denominator"] == 100


@pytest.mark.parametrize("value", ["nan", "inf", "49", "301", "-1"])
def test_invalid_observation_values_rejected(value):
    content = ",".join(FIELDS) + f"\nSYN-999,Fictional Boundary,1980-01-01,2026-10-01,Community,none,true,false,completed,2026-10-01,{value},80,mmHg\n"
    accepted, errors = parse_csv(content, set(), "boundary.csv")
    assert not accepted and errors