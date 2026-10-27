# MeasureBridge ACO

An educational quality-operations workspace for a fixed cohort of 100 entirely fictional records. It demonstrates how a versioned rule can move through CSV validation, explainable evaluation, role-owned follow-up, point-of-care documentation, equity review, and internal reporting approval.

**This is not a clinical decision-support system, validated measure, CMS submission system, payer contract, or reimbursement model.** The demonstration does not recommend treatment or medication changes. Patient preference, contraindications, and clinician judgment are not overridden.

## Run locally

Requirements: Python 3.11+, Node.js 20+, and npm. SQLite is the local default; Docker Compose uses PostgreSQL.

1. Start the API:

   ```powershell
   cd backend
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements-dev.txt
   python -m alembic upgrade head
   python scripts/seed_demo.py
   uvicorn app.main:app --reload
   ```

   The API is at `http://localhost:8000`; OpenAPI docs are at `http://localhost:8000/docs`.

2. In another terminal, start the UI:

   ```powershell
   cd frontend
   npm ci
   npm run dev
   ```

   Open `http://localhost:5173`. The UI uses `http://localhost:8000/api` by default; set `VITE_API_BASE` to override it.

The seed command is idempotent for a populated database. To regenerate the fixed fixture before initial seeding, run `python scripts/seed_demo.py --generate-fixture`; this rewrites `fixtures/synthetic_population.csv` to the documented 100-row construction.

## Docker Compose

From the repository root, copy `.env.example` to `.env`, change the local development password if desired, then run:

```powershell
docker compose up --build
```

Open `http://localhost:8080`; API health is at `http://localhost:8000/api/health`. PostgreSQL data persists in the `measurebridge-data` volume. Local demo credentials are not production secrets. This stack has no production authentication, authorization identity provider, PHI controls, backup policy, or deployment hardening.

## Demonstration path

1. Overview shows the constructed baseline of 60/100 (60%), the fixed denominator, unresolved items, provenance of changes, and reporting blockers.
2. Care-gap queue separates missing documentation, uncompleted assessment, patient preference, data defect, and eligibility questions. Assignments record owner, role, due date, and barrier.
3. Point of care captures a synthetic status and, when completed, a date and values with evidence and role. A workflow event appends to the record; the imported source is retained.
4. The fixture-backed educational documentation workflow can move the 15 `not_documented` records to completed, producing 75/100 (75%), a constructed +15 percentage-point change. This is not a measured clinical improvement. Data repair and simulated care events are tracked separately.
5. Equity view stratifies by facility setting or access barrier and suppresses small cells under 11, including complementary aggregate suppression.
6. Reporting review freezes a versioned digest-backed snapshot, reconciles it, requires a different ACO Operations reviewer, and exports internal CSV/JSON. Unresolved results or open import errors block sign-off.

## Project map

- `backend/app/services/measure_engine.py`: deterministic rule evaluation and denominator summary.
- `backend/app/services/validation.py`: strict CSV shape and row validation.
- `backend/app/services/reporting_snapshots.py`: frozen source/effective data, reconciliation, blockers, and digest.
- `backend/app/api/routes/`: import, registry/dashboard, care-gap, workflow, and reporting APIs.
- `frontend/src/`: operational React workspace and API client.
- `fixtures/educational_measure_v1.json`: executable versioned educational rule.
- `fixtures/synthetic_population.csv`: 100 fictional source records.
- `docs/`: measure specification and portfolio operating artifacts.

## Quality checks

```powershell
cd backend
pip install -r requirements-dev.txt
pytest -q
```

```powershell
cd frontend
npm ci
npm run build
```

GitHub Actions runs both checks on pushes and pull requests. The backend tests include exact rule boundaries, ingestion defects, role/provenance rules, fixed-denominator demonstration, immutable snapshots, and equity suppression.

## Scope and next steps

Read `docs/measure_specification.md` and `docs/limitations.md` before adapting this demonstration. CMS pages are context only. A real implementation would require exact performance-year and collection-type specifications, applicable value sets, validated eligibility/exclusion logic, governance, security/privacy controls, and independent clinical and reporting validation. A future fixture-based FHIR adapter would require conformance tests; local field mapping is not commercial EHR interoperability.