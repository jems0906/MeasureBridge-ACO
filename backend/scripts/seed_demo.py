import argparse
import csv
import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.config import ROOT
from app.models import SessionLocal
from app.services.population import seed
from app.services.validation import FIELDS


def generate_fixture():
    path = ROOT / "fixtures/synthetic_population.csv"
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS)
        writer.writeheader()
        for number in range(1, 101):
            status = "completed" if number <= 60 or number > 90 else "not_documented" if number <= 75 else "not_completed" if number <= 85 else "patient_declined"
            has_values = number <= 60
            writer.writerow({
                "patient_id": f"SYN-{number:03}", "name": f"Fictional Patient {number:03}",
                "date_of_birth": f"{1945 + number % 50}-06-15", "encounter_date": "2026-10-01",
                "facility_type": "Community" if number % 10 < 4 else "Assisted living" if number % 10 < 8 else "Skilled nursing",
                "access_barrier": "language" if number <= 7 else "transport" if number % 3 == 0 else "none",
                "hypertension": "true", "hospice": "false", "documentation_status": status,
                "observation_date": "2026-10-01" if has_values else "", "systolic": 118 + number % 35 if has_values else "",
                "diastolic": 70 + number % 20 if has_values else "", "units": "mmHg",
            })


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--generate-fixture", action="store_true")
    arguments = parser.parse_args()
    if arguments.generate_fixture:
        generate_fixture()
        print("Generated exactly 100 entirely fictional source records")
    else:
        with SessionLocal() as session:
            seed(session)
        print("Educational specification and synthetic cohort are ready")